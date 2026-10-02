-- Run only after the founder has successfully signed in at least once.
-- Replace the placeholder with the exact Auth email visible in Supabase Auth.
-- Do not commit a real personal email address to this public repository.

do $aun$
declare
  target_email text := 'REPLACE_WITH_AUTH_EMAIL';
  target_user_id uuid;
begin
  if target_email = 'REPLACE_WITH_AUTH_EMAIL' then
    raise exception 'replace REPLACE_WITH_AUTH_EMAIL before running';
  end if;

  select id
  into target_user_id
  from auth.users
  where lower(email) = lower(target_email)
  order by created_at asc
  limit 1;

  if target_user_id is null then
    raise exception 'no auth user found for the supplied email';
  end if;

  insert into public.admin_users(user_id)
  values (target_user_id)
  on conflict (user_id) do nothing;
end
$aun$;
