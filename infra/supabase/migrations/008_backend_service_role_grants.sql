-- Explicit backend grants used by Supabase Edge Functions.

grant select on table public.profiles to service_role;
grant select, update on table public.agent_claims to service_role;
grant select, insert on table public.claim_audit_events to service_role;
grant select, insert, update on table public.agent_version_snapshots to service_role;
grant select, insert, update on table public.version_drift_events to service_role;
grant select on table public.agent_alerts to service_role;
grant select, insert, update on table public.user_notifications to service_role;
