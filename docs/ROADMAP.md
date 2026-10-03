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
- [x] task underwriting UI

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
- [ ] persist full historical benchmark receipts
- [ ] sandbox adapters for higher-risk runtime tests

## Phase 2 — Identity, claims and user workspace — ACTIVE

- [x] Supabase project created
- [x] initial database/RLS migration applied
- [x] GitHub OAuth configured and live sign-in observed
- [x] founder admin bootstrap
- [x] account UI
- [x] email magic-link client
- [x] maintainer claim UI
- [x] server-side claim verifier deployed
- [x] saved-agent UI
- [x] version-drift alert preferences
- [x] claim status workspace
- [x] Command Center admin entry point
- [x] version history + in-app notification schema active
- [x] version-watch Edge Function deployed
- [x] six-hour Supabase Cron scheduler active
- [x] 125 initial version snapshots persisted
- [ ] verify email magic-link flow
- [ ] verify maintainer claim end-to-end
- [ ] organization/collaborator maintainer proof path
- [ ] verify real drift notification after an upstream version change

## Phase 3 — Analytics and operations — ACTIVE

- [x] consented first-party event client
- [x] analytics database schema + RLS
- [x] admin metrics RPC
- [x] admin Command Center UI
- [x] privacy/data map
- [x] runtime config reports Supabase auth/product analytics enabled
- [x] founder admin role active
- [x] live analytics inserts observed
- [x] admin metrics verified under authenticated RLS
- [x] Cloudflare Web Analytics token configured; deployed runtime previously verified beacon ON
- [ ] retention/recovery automation
- [ ] backup/export/recovery drill

## Phase 4 — Distribution

- [x] SEO profile pages + sitemap
- [x] badge surface
- [x] save/watch CTA on Trust Cards
- [x] maintainer verification Edge Function deployed
- [x] reusable GitHub Action for maintainers
- [ ] contextual outreach queue
- [ ] suppression/opt-out enforcement in sending layer
- [x] in-app version/evidence notification infrastructure
- [ ] external notification delivery (opt-in only)

## Phase 5 — Underwriting API + revenue — ACTIVE

- [x] fail-closed decision primitive
- [x] task-policy registry
- [x] POST /can-hire request schema
- [x] authenticated Supabase Edge Function deployed
- [x] write-access and spend-limit policy enforcement
- [x] signed-in UI invokes deployed can-hire API
- [ ] external API keys/rate limits
- [ ] organization policy overrides
- [ ] private agent registry
- [ ] audit export
- [ ] usage metering
- [ ] pricing/plan gates that never alter evidence truth
- [ ] first paid B2B pilot delivered and accepted; seller and payment-route gates verified (see [FINISH_PLAN.md](./FINISH_PLAN.md))

## Phase 6 — Launch hardening

- [x] draft privacy policy
- [x] draft public-alpha terms
- [x] security policy
- [x] public Pages secret-like-material scan
- [x] live non-admin RLS visibility test
- [x] Supabase security advisor critical privilege findings cleared
- [x] RLS init-plan performance findings cleared
- [ ] live user-session Edge Function smoke tests
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
