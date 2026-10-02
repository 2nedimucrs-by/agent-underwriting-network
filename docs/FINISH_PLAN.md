# End-to-End Finish Plan

Status: ACTIVE_EXECUTION
Owner: 2nedimucrs-by
Principle: evidence before claims; deterministic workers before LLM workers; zero/low fixed cost until traction.

## Product finish definition

The first sellable release is complete only when a visitor can discover an agent, inspect version-pinned evidence, compare alternatives, create an account, save/claim an agent, receive version-change alerts, and when an organization can ask the underwriting API whether a specific agent is fit for a specific task under explicit policy.

A public profile, maintainer claim, badge, or GitHub popularity signal must never be converted into a VERIFIED security/capability claim without reproducible evidence.

## Phase A — Foundation and public discovery — DONE

Acceptance:
- public GitHub repository
- GitHub Pages deployment
- 100+ public profiles
- per-profile version pin
- Trust Card JSON
- Evidence JSON
- README badge
- comparison UI
- search/category/sort
- fail-closed underwriting primitive

Evidence at plan creation: 125 generated public profiles and successful Pages deployment.

## Phase B — Agent control plane — IN PROGRESS

Deliver:
- machine-readable Chief + worker contracts
- bounded capabilities
- explicit external-action policies
- retry/stop rules
- deterministic work routing
- evidence authority boundaries
- agent health/status contract

Acceptance:
- Chief cannot route a work item to a worker lacking the declared capability
- external sending/purchasing/high-risk writes require explicit approval
- no worker may upgrade an evidence state without evidence IDs
- agent contracts are CI validated

## Phase C — Evidence engine — IN PROGRESS

Deliver:
- version-drift detector
- evidence expiry/staleness propagation
- dependency inventory adapters
- declared permission/tool-surface extraction
- scanner adapter protocol
- security scanner aggregation
- reproducible benchmark contract
- controlled benchmark fixtures
- scanner/tool version provenance

Initial integrations to evaluate behind adapters:
- repository manifests and lockfiles
- OSV/dependency signals
- prompt/security scanners
- MCP-specific scanner outputs
- sandbox/runtime receipts

Acceptance:
- every finding has source, tool/version, time and artifact hash
- conflicting findings are retained, not averaged away
- scanner failure is explicit
- new agent version marks older evidence stale unless declared reusable
- VERIFIED capability requires a reproducible successful fixture

## Phase D — Accounts, identity and claims — BACKEND READY NEXT

Target stack: Supabase Free + GitHub OAuth + email magic link.

Deliver:
- account page
- GitHub sign-in
- email magic-link sign-in
- profile record
- saved agents
- claim requests
- claim identity state separate from Trust Card state
- server-side GitHub maintainer/collaborator verification
- admin approve/revoke path

Acceptance:
- anonymous browsing remains available
- GitHub password is never collected
- maintainer identity VERIFIED does not imply agent security VERIFIED
- users can delete their account/data
- all tables have RLS policies

External setup required:
- Supabase project
- GitHub OAuth App
- Supabase URL/publishable key in GitHub repository variables

## Phase E — Analytics and command center — FRONTEND/SCHEMA READY NEXT

Deliver:
- privacy-first aggregate traffic analytics
- consented first-party product events
- anonymous session ID
- Trust Card view/search/compare/claim/signup events
- admin-only dashboard
- live 5-minute active sessions
- daily page views/signups/claims/comparisons
- top agents/referrers
- event retention policy

Target:
- Cloudflare Web Analytics for aggregate site traffic
- Supabase event table + admin RPC for product analytics

Acceptance:
- no personal email scraping
- no raw IP storage in product event table
- product analytics obey consent state
- public users cannot read raw analytics events
- admin metrics require admin authorization

External setup required:
- optional Cloudflare Web Analytics token
- Supabase project from Phase D

## Phase F — Distribution and growth

Deliver:
- maintainer claim CTA on Trust Cards
- saved/followed agents
- release drift alerts
- GitHub Action for agent maintainers
- context-aware outreach queue
- suppression/opt-out list
- SEO profile pages and sitemap
- badge referral tracking

Acceptance:
- outreach drafts cite the exact public trigger
- no automated issue/comment advertising
- no mass messaging stargazers
- no autonomous bulk email
- external sending remains approval-gated until policy/legal controls are proven

## Phase G — Underwriting API and revenue

Deliver:
- POST /can-hire contract
- task policies
- organization policy overrides
- API authentication
- rate limits
- private agents/registries
- audit export
- usage metering
- plan gates

Decision set:
- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW_REQUIRED
- DENY
- INSUFFICIENT_EVIDENCE

Acceptance:
- decisions return evidence IDs
- stale/missing required evidence fails closed
- customers cannot pay for a better evidence verdict
- plan limits affect access/features, not truth

## Phase H — Launch hardening

Deliver:
- privacy policy
- terms
- data map
- security policy
- abuse/rate-limit controls
- dependency update policy
- backups/export
- monitoring
- recovery drill
- accessibility/mobile QA
- browser QA
- load test
- security review
- launch checklist

Release gates:
- CI green
- Pages deploy green
- auth smoke test
- RLS tests
- claim abuse tests
- analytics privacy test
- underwriting fail-closed tests
- no critical security findings
- recovery procedure tested

## Phase I — Verified Labor Exchange — GATED

Do not build marketplace cold-start infrastructure until there is evidence-network traction.

Unlock criteria:
- meaningful version-pinned corpus
- repeat verification usage
- active claim/badge usage
- external API demand
- real task-outcome history
- enough buyer/seller activity to justify two-sided liquidity

Then add:
- task routing
- verified work receipts
- buyer/seller reputation derived from evidence
- transaction rails
- escrow only if legally/operationally justified

## Execution order

1. Agent control plane contracts
2. Version drift + evidence lifecycle
3. Dependency/permission adapters
4. Security scanner adapters
5. Capability benchmark harness
6. Supabase schema + account frontend
7. GitHub/email auth setup
8. Claim verification backend
9. Analytics + admin command center
10. Saved agents + alerts
11. GitHub Action + outreach queue
12. Underwriting API
13. Privacy/security/recovery hardening
14. Private alpha customers
15. Paid plans
16. Labor exchange only after traction gate
