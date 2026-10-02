-- Production ACL hardening for SECURITY DEFINER functions.
-- Safe to re-run after 001_initial.sql.

revoke execute on function public.admin_dashboard_metrics() from anon;
revoke execute on function public.admin_top_agents(integer) from anon;
revoke execute on function public.is_aun_admin() from anon;

revoke execute on function public.handle_new_aun_user()
  from anon, authenticated;

-- Created by Supabase automatic-RLS project setup.
-- Event-trigger infrastructure must not be callable through Data API roles.
revoke execute on function public.rls_auto_enable()
  from public, anon, authenticated;

grant execute on function public.admin_dashboard_metrics()
  to authenticated;
grant execute on function public.admin_top_agents(integer)
  to authenticated;
grant execute on function public.is_aun_admin()
  to authenticated;
