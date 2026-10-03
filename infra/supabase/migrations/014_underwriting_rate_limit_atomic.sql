-- Serialize underwriting rate checks per authenticated user.
-- SECURITY INVOKER is intentional: the Edge Function calls this with service_role,
-- which already owns the narrowly scoped table privileges from migration 011.

create function public.consume_underwriting_rate_limit(
  p_user_id uuid,
  p_agent_id text,
  p_task_type text
)
returns jsonb
language plpgsql
set search_path = ''
as $function$
declare
  v_now timestamptz;
  v_minute_count bigint;
  v_day_count bigint;
begin
  if p_user_id is null then
    raise exception 'p_user_id is required'
      using errcode = '22004';
  end if;

  -- The lock is transaction-scoped. A waiter checks the counts only after the
  -- previous request commits its event, so parallel requests cannot all pass.
  perform pg_catalog.pg_advisory_xact_lock(
    pg_catalog.hashtextextended(
      'aun-underwriting-rate-limit:' || p_user_id::text,
      0::bigint
    )
  );

  -- clock_timestamp() is evaluated after any lock wait; now() would be stale
  -- because it is fixed at transaction start.
  v_now := pg_catalog.clock_timestamp();

  select
    pg_catalog.count(*) filter (
      where occurred_at >= v_now - interval '1 minute'
    ),
    pg_catalog.count(*) filter (
      where occurred_at >= v_now - interval '1 day'
    )
  into v_minute_count, v_day_count
  from public.underwriting_rate_events
  where user_id = p_user_id
    and occurred_at >= v_now - interval '1 day';

  if v_minute_count >= 30 or v_day_count >= 500 then
    return pg_catalog.jsonb_build_object(
      'allowed', false,
      'retry_after_seconds',
      case when v_minute_count >= 30 then 60 else 3600 end
    );
  end if;

  insert into public.underwriting_rate_events (
    user_id,
    agent_id,
    task_type
  )
  values (
    p_user_id,
    pg_catalog.left(p_agent_id, 256),
    pg_catalog.left(p_task_type, 80)
  );

  return pg_catalog.jsonb_build_object(
    'allowed', true,
    'retry_after_seconds', 0
  );
end;
$function$;

-- The function is in the exposed public schema for RPC routing, so explicitly
-- remove the default PUBLIC execute grant and allow only the backend role.
revoke all on function public.consume_underwriting_rate_limit(uuid, text, text)
  from public, anon, authenticated;
grant execute on function public.consume_underwriting_rate_limit(uuid, text, text)
  to service_role;
