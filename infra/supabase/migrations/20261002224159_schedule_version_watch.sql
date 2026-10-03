
select cron.schedule(
  'aun-version-watch',
  '43 */6 * * *',
  $cron$
  select net.http_post(
    url := 'https://sfplbbnratiznbipniez.supabase.co/functions/v1/version-watch',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-aun-cron-token',
      (select decrypted_secret
       from vault.decrypted_secrets
       where name = 'aun_version_watch_token')
    ),
    body := jsonb_build_object(
      'source', 'supabase-cron',
      'scheduled_at', now()
    ),
    timeout_milliseconds := 15000
  );
  $cron$
);
