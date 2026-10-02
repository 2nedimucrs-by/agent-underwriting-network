-- Authenticated underwriting API abuse guard.

create table if not exists public.underwriting_rate_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  agent_id text,
  task_type text,
  occurred_at timestamptz not null default now()
);

create index if not exists underwriting_rate_events_user_time_idx
  on public.underwriting_rate_events(user_id, occurred_at desc);

alter table public.underwriting_rate_events enable row level security;

revoke all on table public.underwriting_rate_events from anon, authenticated;
grant select, insert, delete on table public.underwriting_rate_events to service_role;

select cron.schedule(
  'aun-underwriting-rate-retention',
  '19 4 * * *',
  $cron$
    delete from public.underwriting_rate_events
    where occurred_at < now() - interval '30 days';
  $cron$
);
