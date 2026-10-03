-- Restore the production migration for admin-only rate-event visibility.
grant select on table public.underwriting_rate_events to authenticated;

drop policy if exists "underwriting rate admin select"
  on public.underwriting_rate_events;
create policy "underwriting rate admin select"
on public.underwriting_rate_events
for select
to authenticated
using ((select public.is_aun_admin()));
