-- Persistent version history + in-app notification queue.
-- Apply after 001_initial.sql.

create table if not exists public.agent_version_snapshots (
  id uuid primary key default gen_random_uuid(),
  agent_id text not null,
  version_hash text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  unique (agent_id, version_hash)
);

create index if not exists agent_version_snapshots_agent_time_idx
  on public.agent_version_snapshots (agent_id, observed_at desc);

create table if not exists public.version_drift_events (
  id uuid primary key default gen_random_uuid(),
  agent_id text not null,
  previous_hash text,
  current_hash text not null,
  detected_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  unique (agent_id, current_hash)
);

create index if not exists version_drift_events_time_idx
  on public.version_drift_events (detected_at desc);

create table if not exists public.user_notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null
    check (event_type in (
      'VERSION_DRIFT',
      'EVIDENCE_CHANGED',
      'SECURITY_FINDING',
      'TRUST_CARD_CHANGED'
    )),
  agent_id text not null,
  title text not null,
  body text not null,
  metadata jsonb not null default '{}'::jsonb,
  dedup_key text not null,
  read_at timestamptz,
  created_at timestamptz not null default now(),
  unique (user_id, dedup_key)
);

create index if not exists user_notifications_user_time_idx
  on public.user_notifications (user_id, created_at desc);

alter table public.agent_version_snapshots enable row level security;
alter table public.version_drift_events enable row level security;
alter table public.user_notifications enable row level security;

revoke all on table public.agent_version_snapshots from anon, authenticated;
grant select on table public.agent_version_snapshots to authenticated;

revoke all on table public.version_drift_events from anon, authenticated;
grant select on table public.version_drift_events to authenticated;

revoke all on table public.user_notifications from anon, authenticated;
grant select, update, delete on table public.user_notifications to authenticated;

drop policy if exists "version snapshots admin select"
  on public.agent_version_snapshots;
create policy "version snapshots admin select"
on public.agent_version_snapshots for select
to authenticated
using (public.is_aun_admin());

drop policy if exists "drift events admin select"
  on public.version_drift_events;
create policy "drift events admin select"
on public.version_drift_events for select
to authenticated
using (public.is_aun_admin());

drop policy if exists "notifications own select"
  on public.user_notifications;
create policy "notifications own select"
on public.user_notifications for select
to authenticated
using (user_id = auth.uid());

drop policy if exists "notifications own update"
  on public.user_notifications;
create policy "notifications own update"
on public.user_notifications for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "notifications own delete"
  on public.user_notifications;
create policy "notifications own delete"
on public.user_notifications for delete
to authenticated
using (user_id = auth.uid());
