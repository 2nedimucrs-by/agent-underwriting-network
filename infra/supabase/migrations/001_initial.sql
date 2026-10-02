-- Agent Underwriting Network: initial identity, claim and analytics schema.
-- Run inside a dedicated Supabase project.
-- Public evidence remains on GitHub Pages; this database stores user-owned state.

create extension if not exists pgcrypto;

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  github_login text,
  avatar_url text,
  marketing_opt_in boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.admin_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create or replace function public.is_aun_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $aun$
  select exists (
    select 1 from public.admin_users where user_id = auth.uid()
  );
$aun$;

revoke all on function public.is_aun_admin() from public;
grant execute on function public.is_aun_admin() to authenticated;

create table if not exists public.agent_claims (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  agent_id text not null,
  repository text,
  github_login text,
  status text not null default 'PENDING_GITHUB_VERIFICATION'
    check (status in (
      'PENDING_GITHUB_VERIFICATION',
      'VERIFIED_MAINTAINER',
      'REJECTED',
      'REVOKED'
    )),
  verification_method text not null default 'github_oauth'
    check (verification_method in ('github_oauth', 'manual_review')),
  verification_notes jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  verified_at timestamptz,
  unique (user_id, agent_id)
);

create table if not exists public.saved_agents (
  user_id uuid not null references auth.users(id) on delete cascade,
  agent_id text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, agent_id)
);

create table if not exists public.agent_alerts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  agent_id text not null,
  alert_type text not null
    check (alert_type in (
      'VERSION_DRIFT',
      'EVIDENCE_CHANGED',
      'SECURITY_FINDING',
      'TRUST_CARD_CHANGED'
    )),
  enabled boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.analytics_events (
  id uuid primary key default gen_random_uuid(),
  session_id text not null check (length(session_id) between 8 and 128),
  user_id uuid references auth.users(id) on delete set null,
  event_type text not null check (event_type in (
    'PAGE_VIEW',
    'SEARCH',
    'TRUST_CARD_VIEW',
    'COMPARE_ADD',
    'COMPARE_RUN',
    'BADGE_VIEW',
    'BADGE_COPY',
    'CLAIM_START',
    'CLAIM_COMPLETE',
    'SIGN_UP',
    'LOGIN',
    'SAVE_AGENT',
    'ALERT_CREATE'
  )),
  agent_id text,
  page_path text not null default '/',
  referrer text,
  metadata jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now()
);

create index if not exists analytics_events_occurred_at_idx
  on public.analytics_events (occurred_at desc);

create index if not exists analytics_events_agent_idx
  on public.analytics_events (agent_id, occurred_at desc);

create index if not exists analytics_events_session_idx
  on public.analytics_events (session_id, occurred_at desc);

create table if not exists public.account_deletion_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'PENDING'
    check (status in ('PENDING', 'COMPLETED', 'REJECTED')),
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists public.outreach_suppression (
  contact_key text primary key,
  reason text not null,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.admin_users enable row level security;
alter table public.agent_claims enable row level security;
alter table public.saved_agents enable row level security;
alter table public.agent_alerts enable row level security;
alter table public.analytics_events enable row level security;
alter table public.account_deletion_requests enable row level security;
alter table public.outreach_suppression enable row level security;

-- Explicit Data API grants.
-- New Supabase projects no longer necessarily expose public tables automatically.
-- Grants answer "may this role attempt the operation?"; RLS policies below answer
-- "which rows may that role actually touch?".
grant usage on schema public to anon, authenticated;

revoke all on table public.profiles from anon, authenticated;
grant select, update on table public.profiles to authenticated;

revoke all on table public.admin_users from anon, authenticated;
grant select on table public.admin_users to authenticated;

revoke all on table public.agent_claims from anon, authenticated;
grant select, insert, update on table public.agent_claims to authenticated;

revoke all on table public.saved_agents from anon, authenticated;
grant select, insert, update, delete on table public.saved_agents to authenticated;

revoke all on table public.agent_alerts from anon, authenticated;
grant select, insert, update, delete on table public.agent_alerts to authenticated;

revoke all on table public.analytics_events from anon, authenticated;
grant insert on table public.analytics_events to anon;
grant select, insert on table public.analytics_events to authenticated;

revoke all on table public.account_deletion_requests from anon, authenticated;
grant select, insert on table public.account_deletion_requests to authenticated;

revoke all on table public.outreach_suppression from anon, authenticated;
grant select, insert, update, delete on table public.outreach_suppression to authenticated;

drop policy if exists "profile own select" on public.profiles;
create policy "profile own select"
on public.profiles for select
to authenticated
using (user_id = auth.uid() or public.is_aun_admin());

drop policy if exists "profile own update" on public.profiles;
create policy "profile own update"
on public.profiles for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "admin user self inspect" on public.admin_users;
create policy "admin user self inspect"
on public.admin_users for select
to authenticated
using (user_id = auth.uid());

drop policy if exists "claim own select" on public.agent_claims;
create policy "claim own select"
on public.agent_claims for select
to authenticated
using (user_id = auth.uid() or public.is_aun_admin());

drop policy if exists "claim own insert" on public.agent_claims;
create policy "claim own insert"
on public.agent_claims for insert
to authenticated
with check (
  user_id = auth.uid()
  and status = 'PENDING_GITHUB_VERIFICATION'
);

drop policy if exists "claim admin update" on public.agent_claims;
create policy "claim admin update"
on public.agent_claims for update
to authenticated
using (public.is_aun_admin())
with check (public.is_aun_admin());

drop policy if exists "saved own all" on public.saved_agents;
create policy "saved own all"
on public.saved_agents for all
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "alerts own all" on public.agent_alerts;
create policy "alerts own all"
on public.agent_alerts for all
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "analytics anonymous insert" on public.analytics_events;
create policy "analytics anonymous insert"
on public.analytics_events for insert
to anon, authenticated
with check (
  user_id is null or user_id = auth.uid()
);

drop policy if exists "analytics admin select" on public.analytics_events;
create policy "analytics admin select"
on public.analytics_events for select
to authenticated
using (public.is_aun_admin());

drop policy if exists "deletion own insert" on public.account_deletion_requests;
create policy "deletion own insert"
on public.account_deletion_requests for insert
to authenticated
with check (user_id = auth.uid() and status = 'PENDING');

drop policy if exists "deletion own select" on public.account_deletion_requests;
create policy "deletion own select"
on public.account_deletion_requests for select
to authenticated
using (user_id = auth.uid() or public.is_aun_admin());

drop policy if exists "suppression admin all" on public.outreach_suppression;
create policy "suppression admin all"
on public.outreach_suppression for all
to authenticated
using (public.is_aun_admin())
with check (public.is_aun_admin());

create or replace function public.handle_new_aun_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $aun$
begin
  insert into public.profiles (
    user_id,
    email,
    github_login,
    avatar_url
  )
  values (
    new.id,
    new.email,
    coalesce(
      new.raw_user_meta_data ->> 'user_name',
      new.raw_user_meta_data ->> 'preferred_username'
    ),
    new.raw_user_meta_data ->> 'avatar_url'
  )
  on conflict (user_id) do update set
    email = excluded.email,
    github_login = coalesce(excluded.github_login, public.profiles.github_login),
    avatar_url = coalesce(excluded.avatar_url, public.profiles.avatar_url),
    updated_at = now();

  return new;
end;
$aun$;

drop trigger if exists on_auth_user_created_aun on auth.users;
create trigger on_auth_user_created_aun
after insert or update on auth.users
for each row execute function public.handle_new_aun_user();

revoke all on function public.handle_new_aun_user() from public;

create or replace function public.admin_dashboard_metrics()
returns jsonb
language plpgsql
security definer
set search_path = public
as $aun$
declare
  result jsonb;
begin
  if not public.is_aun_admin() then
    raise exception 'not authorized';
  end if;

  select jsonb_build_object(
    'live_sessions', (
      select count(distinct session_id)
      from public.analytics_events
      where occurred_at >= now() - interval '5 minutes'
    ),
    'today_events', (
      select count(*)
      from public.analytics_events
      where occurred_at >= date_trunc('day', now())
    ),
    'today_page_views', (
      select count(*)
      from public.analytics_events
      where event_type = 'PAGE_VIEW'
        and occurred_at >= date_trunc('day', now())
    ),
    'today_signups', (
      select count(*)
      from public.analytics_events
      where event_type = 'SIGN_UP'
        and occurred_at >= date_trunc('day', now())
    ),
    'today_claim_starts', (
      select count(*)
      from public.analytics_events
      where event_type = 'CLAIM_START'
        and occurred_at >= date_trunc('day', now())
    ),
    'today_claim_completes', (
      select count(*)
      from public.analytics_events
      where event_type = 'CLAIM_COMPLETE'
        and occurred_at >= date_trunc('day', now())
    ),
    'today_comparisons', (
      select count(*)
      from public.analytics_events
      where event_type = 'COMPARE_RUN'
        and occurred_at >= date_trunc('day', now())
    ),
    'registered_users', (
      select count(*) from public.profiles
    ),
    'verified_maintainer_claims', (
      select count(*) from public.agent_claims
      where status = 'VERIFIED_MAINTAINER'
    )
  )
  into result;

  return result;
end;
$aun$;

create or replace function public.admin_top_agents(hours_back integer default 24)
returns table (agent_id text, event_count bigint)
language plpgsql
security definer
set search_path = public
as $aun$
begin
  if not public.is_aun_admin() then
    raise exception 'not authorized';
  end if;

  return query
  select e.agent_id, count(*)::bigint
  from public.analytics_events e
  where e.agent_id is not null
    and e.occurred_at >= now() - make_interval(hours => greatest(1, least(hours_back, 720)))
  group by e.agent_id
  order by count(*) desc
  limit 20;
end;
$aun$;

revoke all on function public.admin_dashboard_metrics() from public;
revoke all on function public.admin_top_agents(integer) from public;
grant execute on function public.admin_dashboard_metrics() to authenticated;
grant execute on function public.admin_top_agents(integer) to authenticated;
