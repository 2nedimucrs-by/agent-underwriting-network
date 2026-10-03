# Current state

Status: PUBLIC_ALPHA_BACKEND_AND_EVIDENCE_PLATFORM_ACTIVE

## Live and verified

- public repository under 2nedimucrs-by
- live GitHub Pages site
- 125 generated agent/tool profiles
- per-profile Trust Card page
- Trust Card JSON + Evidence JSON
- conservative evidence badge
- multi-agent comparison UI
- task underwriting page
- search/category/sort directory
- daily scheduled discovery
- GitHub Actions CI/deploy
- Supabase project ACTIVE_HEALTHY in Frankfurt
- GitHub OAuth configured and live sign-in observed
- founder account bootstrapped as admin
- product analytics receiving live page-view events
- Cloudflare Web Analytics deployed; latest Pages runtime reports `cloudflare=ON`, and the live page contains the Cloudflare beacon script
- Main Pages deployment #196 succeeded on `6c0736e056378420941802b342807ced84e14804`; the main CI run on that exact commit also succeeded
- admin metrics RPC verified under authenticated RLS context

## Evidence/control-plane implementation

- machine-readable Underwriting Chief + 10 worker contracts
- external-action policy gates
- version-drift stale-evidence primitive
- bounded repository manifest acquisition
- dependency inventory extraction
- declared permission/tool-surface signal extraction
- selected-profile enrichment allowlist
- OSV dependency advisory scanner adapter
- GitHub Global Advisory scanner adapter
- scanner/tool version provenance
- scanner failures represented explicitly rather than silently ignored
- reproducible benchmark receipt protocol
- canonical SHA-256 receipt self-check + timestamped receipt serialization
- complete initial fixture contracts: structured extraction, read-only file, repository read-only, browser read/navigation and MCP tool invocation

Public GitHub metadata and static signals remain EVIDENCE_PARTIAL. Scanner success does not create a global SAFE verdict.

## User/account implementation

- GitHub OAuth + email magic-link frontend
- maintainer claim flow
- saved agents
- version-drift alert preferences
- claim status list
- account data export
- account deletion request
- admin Command Center
- server-side claim verifier deployed
- account deletion Edge Function deployed
- version history/drift schema active
- in-app notification schema active
- version-watch Edge Function active

## Underwriting implementation

- fail-closed task policy engine
- task policy registry
- can-hire request schema
- can-hire Edge Function deployed
- write-access policy enforcement
- spend-limit enforcement
- atomic authenticated per-user underwriting rate limiter implemented (30/minute, 500/day); concurrency, malformed-body, and backend-outage acceptance tests are still open
- evidence IDs returned by decision contract
- signed-in users use server-side underwriting API from the public underwriting page
- anonymous users receive local fail-closed preview only

Current public evidence is intentionally insufficient for most ALLOW decisions.

## Acceptance status

`TECHNICAL_PRIVATE_ALPHA_READY=NO` while the engineering gates above remain open. `FIRST_PAID_PILOT_COMMERCIALLY_COMPLETE=NO`; no buyer acceptance or payment is evidenced. The live system is a public alpha, not a production certification service.

## Supabase migration/source reconciliation

Read-only production audit on 2026-10-03: the Supabase project is ACTIVE_HEALTHY in eu-central-1. Five active Edge Functions were retrieved from production and each deployed index.ts matched the corresponding main-branch source byte-for-byte. The live migration ledger contains 16 rows; the repository has 13 executable migration SQL files plus the example-only admin bootstrap file. The live ledger has no row named for 001_initial.sql, and version_watch_and_notifications appears twice. The ledger also records `enable_version_watch_scheduler_extensions` and `schedule_version_watch`, but no tracked migration SQL contains the version-watch extension/schedule setup. Production metadata confirms pg_cron, pg_net, and Supabase Vault are enabled and the `aun-version-watch` job is active every six hours with Vault-backed authorization; only sanitized job metadata was inspected. The exact source-to-ledger mapping, the origin of the initial schema, and reproducible source for the active scheduler still require reconciliation. No production schema or migration history was changed. Do not claim full production/source migration sync until this mapping and schema comparison are complete.

## Version-watch operations

- Supabase Vault holds the scheduler token
- only the scheduler-token SHA-256 digest is committed in source
- Supabase Cron runs every six hours
- manual smoke run succeeded
- version snapshots continue to accumulate after upstream changes
- version-drift events are being detected
- user notification delivery remains empty until a user actively watches a changed agent
- GitHub Actions duplicate schedule disabled

## Security/performance posture

- all public application tables have RLS enabled
- non-admin authenticated RLS test sees zero admin/analytics rows
- SECURITY DEFINER exposure warnings cleared
- admin RPCs switched to SECURITY INVOKER
- RLS init-plan warnings cleared
- missing foreign-key indexes added
- only current security advisor warning is leaked-password protection, while the product currently uses GitHub OAuth and passwordless magic links
- remaining performance notices are unused-index informational notices on the new low-traffic database

## Remaining activation / validation work

- run complete GitHub OAuth and email magic-link acceptance: session creation/refresh/sign-out and anonymous, self, admin, and cross-user RLS boundaries; only the real email-link click may remain a user action
- test personal-owner and organization/collaborator claim paths, challenge binding/expiry/replay, admin approve/reject/revoke, audit events, and prove maintainer verification never upgrades agent evidence
- complete save → opt-in version-drift alert → real upstream change → snapshot/event/notification → unread/read acceptance with controlled data and cleanup
- strict `/can-hire` body parsing and malformed-input tests are implemented in open draft PR #30 only; current `main` and production have not received this fix
- add exact-version underwriting request/response binding: the live API currently fetches the latest Trust Card without a client-selected commit SHA; require a commit pin, reject mismatches/unresolved versions, and return the bound version in the decision
- run underwriting negative and positive acceptance: anonymous/invalid JWT denial, missing evidence, blocked agent, prohibited writes, spend cap, stale evidence, unknown task, evidence IDs, malformed JSON/types, missing agent, cross-user behavior, and backend failure
- prove 30/minute and 500/day per-user rate limits under concurrent load and verify limiter/database failures fail closed; do not trust client counters
- execute additional task-specific external benchmark fixtures in bounded environments; distinguish framework plumbing from model-backed capability receipts
- complete RLS/function abuse tests, account export/deletion cascade checks, backup/recovery drill with documented RPO/RTO assumptions, and Edge Function/version-watch/discovery/Pages/CI failure visibility
- complete browser and accessibility acceptance for home, Trust Card, compare, underwriting, account, and admin across desktop/tablet/mobile viewports and supported browsers
- verify consent, non-public analytics/raw-IP boundary, admin-only analytics access, retention, export/deletion, and that own test sessions are not counted as organic traffic
- finish private-alpha buyer validation; legal/tax/payment-route review and real customer/pilot acceptance remain human/external gates
- external API-key authentication, organization overrides, recurring billing, usage metering, and self-serve checkout remain post-pilot unless a concrete pilot requires them

## Product truth boundary

DISCOVERED != VERIFIED

MAINTAINER VERIFIED != AGENT VERIFIED

SECURITY SCANNER SUCCESS != SAFE

CAPABLE != AUTHORIZED

AUTHORIZED != ECONOMIC

Missing or stale required evidence fails closed.
