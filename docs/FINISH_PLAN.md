# End-to-End Finish Plan

Status: ACTIVE_EXECUTION
Owner: 2nedimucrs-by
Principle: evidence before claims; deterministic workers before LLM workers; zero/low fixed cost until traction.

## Product finish definition

The first sellable release is complete only when a visitor can discover an agent, inspect version-pinned evidence, compare alternatives, create an account, save/claim an agent, receive version-change alerts, and when an organization can ask the underwriting API whether a specific agent is fit for a specific task under explicit policy.

A public profile, maintainer claim, badge, or GitHub popularity signal must never be converted into a VERIFIED security/capability claim without reproducible evidence.

## First commercial milestone — one paid B2B pilot

The first revenue target is a manually delivered, human-reviewed pilot for one real workflow. Do not wait for a self-serve billing system, and do not add one before buyer demand is proven.

Pilot scope:
- one named business workflow and at most five exact, version-pinned agents;
- time-boxed review with public or explicitly authorized evidence only;
- source-linked evidence register, task-fit matrix, explicit unknowns, and review session;
- reproducible receipts only for fixtures and adapters actually executed;
- no certification, universal safety claim, production permission, pay-to-rank, or paid influence over evidence.

The proposed pilot report format is [PILOT_REPORT_TEMPLATE.md](./PILOT_REPORT_TEMPLATE.md). It is a blank delivery template; it is not evidence that any agent has passed. Prepare the customer-specific proposal with [PAID_PILOT_SCOPE_TEMPLATE.md](./PAID_PILOT_SCOPE_TEMPLATE.md); completed copies and customer agreements must stay outside this public repository.

Payment readiness requires, at minimum:
- buyer/problem interviews and written agreement on workflow, scope, fee, deliverables, and acceptance;
- privacy, terms, data handling, and security review for the actual pilot scope;
- seller entity and tax review with qualified help, and confirmation that the chosen route is enabled for commercial B2B collection;
- signed scope and an agreed due date before work starts;
- delivery accepted by the buyer and payment confirmed before recording the first paid-pilot success.

Use Payoneer only if the account enables the relevant business-to-business collection feature and the transaction meets its current terms. The first manual pilot does not grant software entitlements. Stripe remains excluded.



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

## Phase D — Accounts, identity and claims — LIVE FEATURES; END-TO-END VALIDATION OPEN

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

## Phase E — Analytics and command center — LIVE; RETENTION/RECOVERY OPEN

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

## Phase G — Underwriting API and revenue — API CORE LIVE; COMMERCIAL ACCESS OPEN

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

## Execution order toward first paid pilot

1. Keep the commercial plan and pilot report template aligned with actual product evidence.
2. Execute capability fixtures against explicitly approved third-party agents in a bounded test environment; do not substitute mock harnesses for external evidence.
3. Verify the live magic-link, maintainer-claim, saved-agent, version-drift, and notification paths with controlled test accounts and one real upstream version change.
4. Close launch gate #16: abuse/rate-limit tests, backup/export/recovery drill, accessibility/browser QA, privacy/terms review, and monitoring/failure visibility.
5. Conduct buyer/problem interviews; record willingness to pay separately from interest and secure written scope acceptance for one pilot.
6. Confirm seller standing, tax responsibilities with qualified help, and that the chosen non-Stripe B2B payment method is enabled and suitable.
7. Deliver and obtain acceptance for the scoped pilot; confirm collection before calling the product commercially ready.
8. Only after pilot proof, add recurring checkout, provider webhooks, API keys, metering, and plan gates behind server-side authorization and truth-preserving tests.
9. Keep the labor exchange gated until evidence-network traction is demonstrated.
