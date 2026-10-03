# Supabase deployment

Supabase provides the optional authenticated product backend for the public GitHub Pages evidence network.

## Migration order

Apply the production SQL files in version order:

1. `migrations/001_initial.sql` — profiles, claims, saved agents, alerts, analytics, RLS, admin RPCs.
2. `migrations/003_version_watch.sql` — version history, drift events and in-app notification queue.
3. `migrations/004_security_acl_hardening.sql` — remove unintended Data API execution of privileged helpers.
4. `migrations/005_admin_rpc_security_invoker.sql` — run admin RPCs with caller/RLS privileges.
5. `migrations/006_rls_initplan_and_fk_indexes.sql` — optimize RLS auth lookups and foreign-key indexes.
6. `migrations/007_claim_challenge_and_audit.sql` — add repository challenge state and claim audit storage.
7. `migrations/008_backend_service_role_grants.sql` — grant only the backend table access required by Edge Functions.
8. `migrations/009_claim_status_audit_trigger.sql` — audit claim creation and state transitions.
9. `migrations/010_public_agent_index_cache.sql` — persist a conservative last-known-good public discovery cache.
10. `migrations/011_underwriting_rate_limits.sql` — add authenticated underwriting rate-event storage and retention.
11. `migrations/012_advisor_cleanup.sql` — close remaining advisor findings introduced by later tables.
12. `migrations/013_privacy_retention_cron.sql` — enforce privacy-first operational data retention.
13. `migrations/014_underwriting_rate_limit_atomic.sql` — serialize per-user underwriting rate checks so concurrent requests cannot bypass limits.
14. `migrations/20261002224150_enable_version_watch_scheduler_extensions.sql` — enable pg_cron, pg_net and Supabase Vault in their production schemas.
15. `migrations/20261002224159_schedule_version_watch.sql` — idempotently configure the Vault-backed six-hour version-watch job.

`migrations/002_admin_bootstrap.example.sql` is a one-time founder admin bootstrap example, not a production migration. Replace its placeholder locally before running; never commit a real personal email to the public repository.

The two time-prefixed migrations restore source for existing production ledger entries. The schedule migration reads `aun_version_watch_token` from Vault; it never contains the token value. Deploy `version-watch` before applying the schedule migration to a fresh project.

## Edge Functions

Deploy:

- `verify-github-claim`
- `delete-account`
- `can-hire`
- `version-watch`
- `export-my-data`

### Runtime keys

Browser-safe site configuration uses the Supabase publishable key.

Edge Functions use Supabase-hosted runtime secrets. Current hosted projects may expose the newer publishable/secret key dictionaries; the functions keep a compatibility fallback for legacy `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` values.

Never expose:

- secret/service-role key
- database password
- GitHub OAuth client secret
- version-watch cron token

to GitHub Pages or public JavaScript.

## Claim verification scope

The first automatic proof intentionally supports only the safest simple case:

`GitHub OAuth login == personal repository owner`

Organization repositories and collaborator/maintainer roles remain PENDING until a stronger GitHub App/permission proof or explicit admin review is added.

Maintainer identity verification is separate from security, capability and reliability evidence.

## Underwriting API

`can-hire` requires an authenticated Supabase user session.

It fetches the current public Trust Card and applies fail-closed task policy. Public EVIDENCE_PARTIAL data normally yields `INSUFFICIENT_EVIDENCE` rather than an allow decision.

API-key authentication, organization policy overrides and metering are later hardening work.

## Version watch

`version-watch` is active in production and scheduled through Supabase Cron every six hours. The scheduler token is stored in Supabase Vault; only its SHA-256 digest exists in source control.

It creates in-app notifications only. No external email is sent automatically.

## Account export and deletion

`export-my-data` requires the authenticated user JWT and returns only account-owned product data that the current RLS policies allow the user to read.

`delete-account` requires the authenticated user JWT and deletes only that Auth identity. Database child records configured with `ON DELETE CASCADE` are removed with it.
