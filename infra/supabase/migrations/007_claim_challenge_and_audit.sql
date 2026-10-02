-- Organization/collaborator claim challenge state and immutable audit trail.

alter table public.agent_claims
  add column if not exists challenge_token text,
  add column if not exists challenge_issued_at timestamptz,
  add column if not exists challenge_expires_at timestamptz;

create table if not exists public.claim_audit_events (
  id uuid primary key default gen_random_uuid(),
  claim_id uuid not null references public.agent_claims(id) on delete cascade,
  actor_user_id uuid references auth.users(id) on delete set null,
  event_type text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists claim_audit_events_claim_time_idx
  on public.claim_audit_events(claim_id, created_at desc);

alter table public.claim_audit_events enable row level security;

revoke all on table public.claim_audit_events from anon, authenticated;
grant select on table public.claim_audit_events to authenticated;

drop policy if exists "claim audit owner or admin select"
  on public.claim_audit_events;
create policy "claim audit owner or admin select"
on public.claim_audit_events for select to authenticated
using (
  exists (
    select 1
    from public.agent_claims c
    where c.id = claim_audit_events.claim_id
      and (
        c.user_id = (select auth.uid())
        or (select public.is_aun_admin())
      )
  )
);
