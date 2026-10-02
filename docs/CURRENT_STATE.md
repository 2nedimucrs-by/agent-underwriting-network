# Current state

Status: PUBLIC_ALPHA_PLATFORM_BUILD_IN_PROGRESS

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
- fail-closed underwriting primitive
- GitHub Actions CI/deploy

## Newly implemented in the finish-plan pass

- machine-readable Underwriting Chief + 10 worker contracts
- capability ownership and external-action policy gates
- version-drift stale-evidence primitive
- dependency manifest extractor
- declared permission-surface extractor
- scanner adapter protocol preserving conflicting findings
- reproducible benchmark receipt protocol
- Supabase identity/claims/saved-agents/alerts/analytics schema with RLS
- GitHub OAuth + email magic-link account frontend
- pending maintainer claim flow
- optional Cloudflare Web Analytics injection
- consented first-party product-event client
- admin-only Command Center frontend + metrics RPC
- account deletion request contract
- privacy/data map + draft privacy/terms
- end-to-end finish plan

## External setup still required

The repository cannot create third-party accounts or secrets by itself.

Required to activate account/analytics features:
- dedicated Supabase project
- apply infra/supabase/migrations/001_initial.sql
- GitHub OAuth App configured in Supabase
- repository variables AUN_SUPABASE_URL and AUN_SUPABASE_ANON_KEY
- optional AUN_CLOUDFLARE_WEB_ANALYTICS_TOKEN
- founder auth UUID inserted into admin_users

Until those values exist, the public evidence directory continues working and account/analytics features remain safely disabled.

## Product truth boundary

Public GitHub metadata may support EVIDENCE_PARTIAL identity/provenance/freshness.

It does not prove security, permission safety, capability, reliability or economics.

Maintainer identity verification is also separate from agent verification.

## Highest-priority remaining engineering

1. wire dependency/permission evidence to bounded repo acquisition
2. real scanner adapters
3. first capability benchmark fixtures
4. activate Supabase auth and admin analytics
5. server-side GitHub maintainer verification
6. saved agents + drift alerts
7. production underwriting API
8. launch security/recovery/private-alpha gate
