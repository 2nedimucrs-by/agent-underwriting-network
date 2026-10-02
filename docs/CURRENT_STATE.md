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
- structured extraction + read-only file benchmark fixtures

Public GitHub metadata and static signals remain EVIDENCE_PARTIAL. Scanner success does not create a global SAFE verdict.

## User/account implementation

- GitHub OAuth + email magic-link frontend
- maintainer claim flow
- saved agents
- version-drift alert preferences
- claim status list
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
- evidence IDs returned by decision contract
- signed-in users use server-side underwriting API from the public underwriting page
- anonymous users receive local fail-closed preview only

Current public evidence is intentionally insufficient for most ALLOW decisions.

## Version-watch operations

- Supabase Vault holds the scheduler token
- only the scheduler-token SHA-256 digest is committed in source
- Supabase Cron runs every six hours
- manual smoke run succeeded
- 125 initial version snapshots persisted
- zero drift events on baseline
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

- verify email magic-link flow interactively
- test claim verification end-to-end from a Trust Card
- test saved-agent + version-drift notification end-to-end on a real upstream version change
- execute capability fixtures against real third-party agent adapters in a controlled sandbox
- add API-key authentication/rate limits for external underwriting API customers
- backup/export/recovery drill
- accessibility/mobile/browser acceptance
- private alpha customer validation
- jurisdiction-specific legal review

## Product truth boundary

DISCOVERED != VERIFIED

MAINTAINER VERIFIED != AGENT VERIFIED

SECURITY SCANNER SUCCESS != SAFE

CAPABLE != AUTHORIZED

AUTHORIZED != ECONOMIC

Missing or stale required evidence fails closed.
