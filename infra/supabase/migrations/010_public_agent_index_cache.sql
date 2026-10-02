-- Public last-known-good discovery cache used only when GitHub discovery is temporarily unavailable.

create table if not exists public.public_agent_index_cache (
  cache_key text primary key,
  payload jsonb not null,
  source_url text not null,
  observed_at timestamptz not null default now()
);

alter table public.public_agent_index_cache enable row level security;

revoke all on table public.public_agent_index_cache from anon, authenticated;
grant select on table public.public_agent_index_cache to anon, authenticated;
grant select, insert, update on table public.public_agent_index_cache to service_role;

drop policy if exists "public agent index cache read"
  on public.public_agent_index_cache;
create policy "public agent index cache read"
on public.public_agent_index_cache for select
to anon, authenticated
using (true);
