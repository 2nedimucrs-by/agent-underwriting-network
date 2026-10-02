# Roadmap

The detailed execution contract is in [FINISH_PLAN.md](./FINISH_PLAN.md).

## Phase 0 — Public foundation — DONE

- [x] public repository
- [x] core schemas
- [x] GitHub discovery index
- [x] GitHub Pages pipeline
- [x] fail-closed underwriting primitive
- [x] live Pages deployment
- [x] 100+ discovery profiles (125 generated)
- [x] public Trust Card pages
- [x] README evidence badges
- [x] comparison UI

## Phase 1 — Control plane + evidence lifecycle — ACTIVE

- [x] Chief + 10 bounded worker contracts
- [x] external-action policy gates
- [x] version-drift stale-evidence primitive
- [x] bounded version-pinned manifest acquisition
- [x] dependency inventory extraction
- [x] declared permission/tool-surface extraction
- [x] scanner adapter protocol
- [x] OSV dependency advisory adapter
- [x] GitHub Global Advisory adapter
- [x] selected-profile evidence enrichment
- [x] reproducible benchmark receipt protocol
- [x] structured-extraction benchmark fixture
- [x] read-only file benchmark fixture
- [ ] execute capability fixtures against real third-party agent adapters
- [ ] persist full historical evidence receipts across builds
- [ ] sandbox adapters for higher-risk runtime tests

## Phase 2 — Identity, claims and user workspace — ACTIVE

- [x] Supabase project created
- [x] initial database/RLS migration applied
- [x] GitHub OAuth configured and live sign-in observed
- [x] account UI
- [x] email magic-link client
- [x] maintainer claim UI
- [x] server-side claim verifier implementation
- [x] saved-agent UI
- [x] version-drift alert preferences
- [x] claim status workspace
- [x] admin-role-aware Command Center link
- [x] version history + in-app notification schema prepared
- [x] version-watch Edge Function prepared
- [ ] deploy claim/delete/can-hire/version-watch Edge Functions
- [ ] apply admin bootstrap
- [ ] apply version-watch migration
- [ ] verify email magic-link flow
- [ ] organization/collaborator maintainer proof path
- [ ] activate in-app notification UI after migration

## Phase 3 — Analytics and operations — ACTIVE

- [x] optional Cloudflare beacon integration
- [x] consented first-party event client
- [x] analytics database schema + RLS applied
- [x] admin metrics RPC
- [x] admin Command Center UI
- [x] privacy/data map
- [x] runtime config reports Supabase auth/product analytics enabled
- [ ] bootstrap founder admin role
- [ ] verify live analytics inserts and admin metrics
- [ ] activate Cloudflare Web Analytics
- [ ] retention/recovery automation

## Phase 4 — Distribution

- [x] SEO profile pages + sitemap
- [x] badge surface
- [x] save/watch CTA on Trust Cards
- [ ] maintainer verification Edge Function deployed
- [ ] reusable GitHub Action for maintainers
- [ ] contextual outreach queue
- [ ] suppression/opt-out enforcement in sending layer
- [ ] version/evidence notification delivery

## Phase 5 — Underwriting API + revenue — CORE READY

- [x] fail-closed decision primitive
- [x] task-policy registry
- [x] POST /can-hire request schema
- [x] authenticated Supabase Edge Function implementation
- [x] write-access and spend-limit policy enforcement
- [ ] deploy can-hire Edge Function
- [ ] API keys/rate limits
- [ ] organization policy overrides
- [ ] private agent registry
- [ ] audit export
- [ ] usage metering
- [ ] pricing/plan gates that never alter evidence truth

## Phase 6 — Launch hardening

- [x] draft privacy policy
- [x] draft public-alpha terms
- [x] security policy
- [x] public Pages secret-like-material scan
- [ ] live RLS abuse tests
- [ ] Edge Function authorization tests
- [ ] abuse/rate-limit tests
- [ ] backup/export/recovery drill
- [ ] accessibility/mobile/browser acceptance
- [ ] private alpha customer evidence
- [ ] jurisdiction-specific legal review

## Phase 7 — Verified Labor Exchange — GATED

Do not build wallet, escrow or two-sided marketplace infrastructure until evidence-network usage justifies it.

Unlock only after:
- meaningful historical evidence corpus
- repeat verification usage
- active claims/badges
- external API demand
- real task-outcome history
- buyer/seller liquidity evidence
