# Version Drift Watch

The version watcher converts public repository head changes into persistent version history and opt-in in-app notifications.

## Components

- `003_version_watch.sql`
- Supabase Edge Function: `version-watch`
- GitHub Actions workflow: `Version Drift Watch`

## Safety model

The watcher does not claim that a new version is better, worse or unsafe.

It only records:

- previous version hash
- current version hash
- detection time

The user-facing notification says that version-bound evidence may need re-evaluation.

## Activation

1. Apply `003_version_watch.sql`.
2. Deploy the `version-watch` Edge Function.
3. Set an Edge Function secret named `AUN_CRON_TOKEN`.
4. Add the same value to the GitHub repository secret `AUN_VERSION_WATCH_TOKEN`.

Until the secret exists, the scheduled GitHub workflow exits successfully without making an external call.

## Delivery boundary

Current implementation creates in-app `user_notifications` rows only.

No email, SMS or external notification is sent automatically.
