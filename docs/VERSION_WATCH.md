# Version Drift Watch

The version watcher converts public repository head changes into persistent version history and opt-in in-app notifications.

## Production state

Production scheduling runs inside Supabase using:

- `pg_cron`
- `pg_net`
- Supabase Vault
- the deployed `version-watch` Edge Function

The active production schedule is every six hours.

The initial smoke run initialized 125 version snapshots. The live table snapshot later showed 159 snapshots and 34 drift events; notification rows were 0 at the last check, consistent with no completed saved-agent watch → changed-version → user notification chain. Counts are point-in-time, not acceptance evidence.

## Safety model

The watcher does not claim that a new version is better, worse or unsafe.

It records:

- previous version hash
- current version hash
- detection time

When a watched agent changes version, the user-facing notification says only that version-bound evidence may need re-evaluation.

## Authentication

The scheduler token is generated randomly and stored encrypted in Supabase Vault.

Only its SHA-256 digest is present in the Edge Function source. The raw token is not committed to GitHub and is not exposed to GitHub Pages.

## Delivery boundary

Current implementation creates in-app `user_notifications` rows only.

No email, SMS or external notification is sent automatically. End-to-end acceptance is still open: save an agent, opt in to version-drift alerts, observe a real upstream version change, verify snapshot and drift rows, verify the user's unread notification, mark it read, and clean up controlled test data without changing real user preferences.

## GitHub Actions

The former six-hour GitHub Actions scheduler has been disabled to avoid duplicate execution. The remaining workflow is a manual operational fallback marker.
