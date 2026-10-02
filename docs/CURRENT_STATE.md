# Current state

Status: PUBLIC_ALPHA_EVIDENCE_AND_ACCOUNT_PLATFORM_ACTIVE

## Live and verified

- public repository under 2nedimucrs-by
- live GitHub Pages site
- 125 generated agent/tool profiles
- per-profile Trust Card page
- Trust Card JSON + Evidence JSON
- conservative evidence badge
- multi-agent comparison UI
- search/category/sort directory
- daily scheduled discovery
- GitHub Actions CI/deploy
- Supabase project created
- initial Supabase schema/RLS migration applied successfully
- GitHub OAuth configured
- live GitHub sign-in observed on account page
- Pages runtime config reports auth=ON and product_analytics=ON

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
- admin-role-aware Command Center entry point
- prepared server-side claim verifier
- prepared account deletion function
- prepared version history/drift migration
- prepared version-watch function and guarded scheduler

## Underwriting implementation

- fail-closed task policy engine
- task policy registry
- can-hire request schema
- authenticated can-hire Edge Function implementation
- write-access policy enforcement
- spend-limit enforcement
- evidence IDs returned by decision contract

Current public evidence is intentionally insufficient for most ALLOW decisions.

## Remaining external activation work

The following require Supabase-side changes or secrets and are not claimed as active yet:

- founder admin bootstrap
- deploy Edge Functions: verify-github-claim, delete-account, can-hire, version-watch
- apply 003_version_watch.sql
- configure AUN_CRON_TOKEN + matching GitHub repository secret
- verify email magic-link login
- optional Cloudflare Web Analytics token

## Product truth boundary

DISCOVERED != VERIFIED

MAINTAINER VERIFIED != AGENT VERIFIED

SECURITY SCANNER SUCCESS != SAFE

CAPABLE != AUTHORIZED

AUTHORIZED != ECONOMIC

Missing or stale required evidence fails closed.

## Highest-priority next work

1. deploy/verify Supabase Edge Functions
2. bootstrap founder admin + verify Command Center metrics
3. apply version-watch migration and activate in-app drift notifications
4. execute benchmark harness against real target-agent adapters
5. add reusable maintainer GitHub Action
6. harden API authentication/rate limits
7. live RLS/Edge Function abuse testing
8. private alpha customer validation
