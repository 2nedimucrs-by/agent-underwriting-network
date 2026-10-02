-- Audit every claim creation and state transition.

create or replace function public.log_agent_claim_audit()
returns trigger
language plpgsql
security definer
set search_path = public
as $aun$
begin
  if tg_op = 'INSERT' then
    insert into public.claim_audit_events(
      claim_id,
      actor_user_id,
      event_type,
      metadata
    )
    values (
      new.id,
      auth.uid(),
      'CLAIM_CREATED',
      jsonb_build_object(
        'status', new.status,
        'verification_method', new.verification_method
      )
    );
    return new;
  end if;

  if
    new.status is distinct from old.status
    or new.verification_method is distinct from old.verification_method
  then
    insert into public.claim_audit_events(
      claim_id,
      actor_user_id,
      event_type,
      metadata
    )
    values (
      new.id,
      auth.uid(),
      'CLAIM_STATE_CHANGED',
      jsonb_build_object(
        'previous_status', old.status,
        'status', new.status,
        'previous_verification_method', old.verification_method,
        'verification_method', new.verification_method
      )
    );
  end if;

  return new;
end;
$aun$;

revoke execute on function public.log_agent_claim_audit()
  from public, anon, authenticated;

drop trigger if exists on_agent_claim_audit
  on public.agent_claims;

create trigger on_agent_claim_audit
after insert or update on public.agent_claims
for each row execute function public.log_agent_claim_audit();
