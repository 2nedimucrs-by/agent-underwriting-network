-- Privacy-first retention for operational user data.

select cron.schedule(
  'aun-data-retention',
  '37 4 * * *',
  $cron$
    delete from public.analytics_events
    where occurred_at < now() - interval '90 days';

    delete from public.user_notifications
    where
      (read_at is not null and read_at < now() - interval '90 days')
      or created_at < now() - interval '180 days';

    delete from public.account_deletion_requests
    where status = 'COMPLETED'
      and completed_at is not null
      and completed_at < now() - interval '365 days';
  $cron$
);
