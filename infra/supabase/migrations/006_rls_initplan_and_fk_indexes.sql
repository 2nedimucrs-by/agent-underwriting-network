-- Optimize RLS auth lookups and add covering indexes for foreign keys.

create index if not exists account_deletion_requests_user_idx
  on public.account_deletion_requests(user_id);

create index if not exists agent_alerts_user_idx
  on public.agent_alerts(user_id);

create index if not exists analytics_events_user_idx
  on public.analytics_events(user_id);

drop policy if exists "profile own select" on public.profiles;
create policy "profile own select"
on public.profiles for select to authenticated
using (
  user_id = (select auth.uid())
  or (select public.is_aun_admin())
);

drop policy if exists "profile own update" on public.profiles;
create policy "profile own update"
on public.profiles for update to authenticated
using (user_id = (select auth.uid()))
with check (user_id = (select auth.uid()));

drop policy if exists "admin user self inspect" on public.admin_users;
create policy "admin user self inspect"
on public.admin_users for select to authenticated
using (user_id = (select auth.uid()));

drop policy if exists "claim own select" on public.agent_claims;
create policy "claim own select"
on public.agent_claims for select to authenticated
using (
  user_id = (select auth.uid())
  or (select public.is_aun_admin())
);

drop policy if exists "claim own insert" on public.agent_claims;
create policy "claim own insert"
on public.agent_claims for insert to authenticated
with check (
  user_id = (select auth.uid())
  and status = 'PENDING_GITHUB_VERIFICATION'
);

drop policy if exists "claim admin update" on public.agent_claims;
create policy "claim admin update"
on public.agent_claims for update to authenticated
using ((select public.is_aun_admin()))
with check ((select public.is_aun_admin()));

drop policy if exists "saved own all" on public.saved_agents;
create policy "saved own all"
on public.saved_agents for all to authenticated
using (user_id = (select auth.uid()))
with check (user_id = (select auth.uid()));

drop policy if exists "alerts own all" on public.agent_alerts;
create policy "alerts own all"
on public.agent_alerts for all to authenticated
using (user_id = (select auth.uid()))
with check (user_id = (select auth.uid()));

drop policy if exists "analytics anonymous insert" on public.analytics_events;
create policy "analytics anonymous insert"
on public.analytics_events for insert to anon, authenticated
with check (
  user_id is null
  or user_id = (select auth.uid())
);

drop policy if exists "analytics admin select" on public.analytics_events;
create policy "analytics admin select"
on public.analytics_events for select to authenticated
using ((select public.is_aun_admin()));

drop policy if exists "deletion own insert" on public.account_deletion_requests;
create policy "deletion own insert"
on public.account_deletion_requests for insert to authenticated
with check (
  user_id = (select auth.uid())
  and status = 'PENDING'
);

drop policy if exists "deletion own select" on public.account_deletion_requests;
create policy "deletion own select"
on public.account_deletion_requests for select to authenticated
using (
  user_id = (select auth.uid())
  or (select public.is_aun_admin())
);

drop policy if exists "suppression admin all" on public.outreach_suppression;
create policy "suppression admin all"
on public.outreach_suppression for all to authenticated
using ((select public.is_aun_admin()))
with check ((select public.is_aun_admin()));

drop policy if exists "version snapshots admin select"
  on public.agent_version_snapshots;
create policy "version snapshots admin select"
on public.agent_version_snapshots for select to authenticated
using ((select public.is_aun_admin()));

drop policy if exists "drift events admin select"
  on public.version_drift_events;
create policy "drift events admin select"
on public.version_drift_events for select to authenticated
using ((select public.is_aun_admin()));

drop policy if exists "notifications own select"
  on public.user_notifications;
create policy "notifications own select"
on public.user_notifications for select to authenticated
using (user_id = (select auth.uid()));

drop policy if exists "notifications own update"
  on public.user_notifications;
create policy "notifications own update"
on public.user_notifications for update to authenticated
using (user_id = (select auth.uid()))
with check (user_id = (select auth.uid()));

drop policy if exists "notifications own delete"
  on public.user_notifications;
create policy "notifications own delete"
on public.user_notifications for delete to authenticated
using (user_id = (select auth.uid()));
