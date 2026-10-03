# Supabase deployment

Supabase provides the optional authenticated product backend for the public GitHub Pages evidence network.

## Production migration source status

**Status: RECONCILIATION_INCOMPLETE (read-only capture, 2026-10-03).** The production ledger contains 16 rows. `migration-ledger-snapshot.json` archives their original statement arrays and SHA-256 hashes, including both rows named `version_watch_and_notifications`. This captures applied SQL, not proof of the current schema or an independently signed archive.

The duplicate entries `20261002223225` and `20261002223438` have the same SQL after removing only leading full-line comments and boundary whitespace; both match `003_version_watch.sql` under that comparison. Their names do not identify different schema changes. Preserve both ledger rows; do not collapse or rename history.

The four timestamped files are now exact original ledger statements (ignoring platform line endings and boundary whitespace). The earlier reconstructed extension SQL omitted the original cron schema/table grants and added a Vault installation absent from that ledger entry. The earlier schedule/policy sources added unschedule/drop operations absent from their original entries. Those historical files now preserve the applied statements. Vault is installed live, but its installation provenance is not established by this ledger.

`001_initial.sql` has no matching ledger row, so its exact applied identity remains unproven. `012_advisor_cleanup.sql` also has no separate named live row; its actor-index/admin-policy operations overlap the later timestamped sources and it must not be counted as an applied migration.

The live scheduler is active on `43 */6 * * *` and uses a Vault lookup for its token. Installed extensions and successful scheduler runs were verified read-only. No secret value, customer record, production DDL, or migration-ledger mutation was required for this capture.

**Do not replay production history.** The archive is reference data, not an executable deployment plan. Full reconciliation still requires authoritative initial-baseline/Vault installation provenance and independent current-object comparison. Table presence alone is not original migration proof. Keep `MIGRATION_SOURCE_RECONCILED=NO`.

### Captured ledger-to-source map

Every row's exact SQL is retained in the archive. The source column identifies the corresponding repository implementation; it does not claim byte equality for numbered files reformatted after application.

| Ledger version | Name | Repository source |
| --- | --- | --- |
| 20261002223225 | version_watch_and_notifications | 003_version_watch.sql (leading comments only) |
| 20261002223424 | security_definer_acl_hardening | 004_security_acl_hardening.sql (formatting/comments) |
| 20261002223438 | version_watch_and_notifications | 003_version_watch.sql (leading comments only; repeat application) |
| 20261002223739 | admin_rpc_security_invoker | 005_admin_rpc_security_invoker.sql |
| 20261002223915 | rls_initplan_and_fk_indexes | 006_rls_initplan_and_fk_indexes.sql |
| 20261002224150 | enable_version_watch_scheduler_extensions | 20261002224150_enable_version_watch_scheduler_extensions.sql (exact) |
| 20261002224159 | schedule_version_watch | 20261002224159_schedule_version_watch.sql (exact) |
| 20261002224806 | claim_challenge_and_audit | 007_claim_challenge_and_audit.sql |
| 20261002224856 | backend_service_role_grants | 008_backend_service_role_grants.sql (formatting/comments) |
| 20261002225025 | claim_status_audit_trigger | 009_claim_status_audit_trigger.sql |
| 20261002225524 | public_agent_index_cache | 010_public_agent_index_cache.sql |
| 20261002225742 | underwriting_rate_limits | 011_underwriting_rate_limits.sql |
| 20261002230020 | claim_audit_actor_index | 20261002230020_claim_audit_actor_index.sql (exact) |
| 20261002230030 | underwriting_rate_admin_visibility | 20261002230030_underwriting_rate_admin_visibility.sql (exact) |
| 20261002230329 | privacy_retention_cron | 013_privacy_retention_cron.sql |
| 20261003014714 | underwriting_rate_limit_atomic | 014_underwriting_rate_limit_atomic.sql |

Validate the archive hashes, restored files, and duplicate comparison locally:

```sh
python scripts/validate_supabase_migration_sources.py
```

A passing archive validation reports 16 captured rows and four exact restored sources. It deliberately retains `MIGRATION_SOURCE_RECONCILED=NO`; it does not connect to Supabase, prove recovery, or establish live acceptance. Hashes detect accidental changes; they are not an independent signature or external timestamp.

## Migration order

**Fresh-project bootstrap only:** the ordered SQL list below is for a new, dedicated Supabase project. Do not replay it against the existing production project. The timestamped files restore migrations already recorded as applied in production, and the numbered files are historical sources; do not rerun `001_initial.sql` or these restored migrations during source reconciliation. Any future production DDL requires a separately reviewed deployment plan and verification against the live migration ledger.

This bootstrap order has not been proven as a clean-project recovery path. Provision Vault and verify its secret, the Supabase automatic-RLS helper, and all external prerequisites before testing it on a dedicated disposable project. Apply these SQL files in the dependency order below. The time-prefixed filenames preserve their exact versions from the live Supabase migration ledger; the numbered files retain the repository's semantic sequence.

1. `migrations/001_initial.sql` — profiles, claims, saved agents, alerts, analytics, RLS, admin RPCs.
2. `migrations/003_version_watch.sql` — version history, drift events and in-app notification queue.
3. `migrations/004_security_acl_hardening.sql` — remove unintended Data API execution of privileged helpers.
4. `migrations/005_admin_rpc_security_invoker.sql` — run admin RPCs with caller/RLS privileges.
5. `migrations/006_rls_initplan_and_fk_indexes.sql` — optimize RLS auth lookups and foreign-key indexes.
6. `migrations/20261002224150_enable_version_watch_scheduler_extensions.sql` — original pg_net/pg_cron installation and postgres cron grants; Vault must already be provisioned.
7. `migrations/20261002224159_schedule_version_watch.sql` — original Vault-backed six-hour version-watch schedule (not a rerunnable replacement).
8. `migrations/007_claim_challenge_and_audit.sql` — add repository challenge state and claim audit storage.
9. `migrations/008_backend_service_role_grants.sql` — grant only the backend table access required by Edge Functions.
10. `migrations/009_claim_status_audit_trigger.sql` — audit claim creation and state transitions.
11. `migrations/010_public_agent_index_cache.sql` — persist a conservative last-known-good public discovery cache.
12. `migrations/011_underwriting_rate_limits.sql` — add authenticated underwriting rate-event storage and retention.
13. `migrations/20261002230020_claim_audit_actor_index.sql` — index claim-audit actors for admin review.
14. `migrations/20261002230030_underwriting_rate_admin_visibility.sql` — expose rate-event rows to authenticated admins only.
15. `migrations/012_advisor_cleanup.sql` — idempotent repository reconciliation for the actor index/admin read policy.
16. `migrations/013_privacy_retention_cron.sql` — enforce privacy-first operational data retention.
17. `migrations/014_underwriting_rate_limit_atomic.sql` — serialize per-user underwriting rate checks so concurrent requests cannot bypass limits.

`migrations/002_admin_bootstrap.example.sql` is a one-time founder admin bootstrap example, not a production migration. Replace its placeholder locally before running; never commit a real personal email to the public repository.

The four time-prefixed migration files restore source for existing production ledger entries. The schedule migration reads `aun_version_watch_token` from Vault; it never contains the token value. Deploy `version-watch` and provision that Vault secret before applying the schedule migration to a fresh project.

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
