-- Resolve remaining actionable advisor findings introduced by later tables.

create index if not exists claim_audit_events_actor_user_idx
  on public.claim_audit_events(actor_user_id);

grant select on table public.underwriting_rate_events to authenticated;

drop policy if exists "underwriting rate admin select"
  on public.underwriting_rate_events;
create policy "underwriting rate admin select"
on public.underwriting_rate_events
for select
to authenticated
using ((select public.is_aun_admin()));
