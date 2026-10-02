-- Admin RPCs rely on RLS and auth.uid(); they do not require definer rights.
-- Switching to SECURITY INVOKER removes unnecessary privilege elevation.

alter function public.is_aun_admin() security invoker;
alter function public.admin_dashboard_metrics() security invoker;
alter function public.admin_top_agents(integer) security invoker;
