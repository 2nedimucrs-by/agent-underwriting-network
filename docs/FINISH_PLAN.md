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
- authenticated per-user limits (live, 30/minute and 500/day)
- external API-key authentication and rate limits
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
- abuse controls and concurrent-load/outage validation of the live rate limiter
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
- underwriting fail-closed and rate-limit concurrency/outage tests
- no critical security findings
- recovery procedure tested
- live Supabase migration ledger reconciled to tracked source; explain the initial-baseline and duplicate-history entries, add tracked source for the live version-watch extension/schedule migrations, and verify schema/permissions before claiming source sync

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
4. Close launch gate #16: concurrent rate-limit/abuse tests, backup/export/recovery drill, accessibility/browser QA, privacy/terms review, and monitoring/failure visibility.
5. Conduct buyer/problem interviews; record willingness to pay separately from interest and secure written scope acceptance for one pilot.
6. Confirm seller standing, tax responsibilities with qualified help, and that the chosen non-Stripe B2B payment method is enabled and suitable.
7. Deliver and obtain acceptance for the scoped pilot; confirm collection before calling the product commercially ready.
8. Only after pilot proof, add recurring checkout, provider webhooks, API keys, metering, and plan gates behind server-side authorization and truth-preserving tests.
9. Keep the labor exchange gated until evidence-network traction is demonstrated.


## Private-alpha acceptance matrix

The following criteria define closure evidence for the current private-alpha milestone. Existing source code, a green fixture, or a successful deploy alone does not close an acceptance gate.

### Identity and claims

- GitHub OAuth: anonymous → sign-in → session/profile → refresh → sign-out; verify account state visibility at each step.
- Email magic link: request, callback, session state; if the real link click requires the user, record only `BLOCKED_USER_MAGIC_LINK_CLICK`.
- Verify anonymous, own-user, admin, and cross-user RLS behavior. No user may read another user's private records.
- Personal-repository claim proves the signed-in GitHub user is the repository owner. Organization/collaborator claims use a 24-hour public challenge at `.github/agent-underwriting-claim.json`, bound to the exact claim ID, random token, and expiry.
- Test pending, verified, rejected, and revoked states; wrong user/token/claim, expired challenge, replay, admin actions, and audit events.
- Maintainer verification proves identity/control only and never changes security, capability, reliability, or task fitness.

### Saved agents and version monitoring

- Prove save → opt-in `VERSION_DRIFT` → real upstream version change → version snapshot → drift event → unread in-app notification → mark read.
- Use controlled records where possible; preserve/restore real preferences and remove synthetic rows after the test.
- External delivery remains opt-in; no automatic email or SMS.

### Underwriting

- Bind each request to the exact selected agent commit SHA; reject missing/unresolved or mismatched versions and include the bound SHA in the decision. This is not implemented in the current live function.
- Test authenticated success and anonymous/invalid-session denial.
- Cover missing evidence → `INSUFFICIENT_EVIDENCE`, blocked agent → `DENY`, prohibited writes → `DENY`, spend caps, stale evidence, unknown task → `REVIEW_REQUIRED`, missing agent, malformed JSON/types, cross-user isolation, returned evidence IDs, and backend failure.
- Rate limits are 30 requests/minute/user and 500 requests/day/user. Prove concurrency and atomicity, and prove database/RPC failure fails closed. Client counters are not trusted.
- Strict request parsing and malformed-input unit/contract tests are implemented in draft PR #30. They are not yet in `main` or production; the live negative test remains open until reviewed merge and deployment. The parser rejects unknown keys and incorrect types (including string booleans and non-finite/negative spend values) before decision evaluation.

### Security, recovery, operations, and privacy

- Run RLS and Edge Function abuse tests; verify anonymous/authenticated/admin boundaries and public secret scanning.
- Test account export and deletion, including cascades. Complete a database backup/restore drill and document RPO/RTO assumptions.
- Verify operational failure visibility for Edge Functions, version-watch, discovery, Pages, and CI.
- Complete browser/accessibility acceptance for home, Trust Card, compare, underwriting, account, and admin on supported desktop browsers and desktop (1440), laptop (1024), tablet (~768), and mobile (~390) viewports. Check overflow, navigation, hidden state, forms, keyboard/focus, labels, contrast, and responsive layouts.
- Confirm product analytics consent, no public raw-event access, no raw IP in product events, admin-only metrics, retention, export/deletion, and that internal test sessions are not reported as organic users.
- Cloudflare traffic analytics remains additive and ON; Supabase product analytics remains ON.

### Evidence receipts and growth boundaries

- Execute task-specific third-party fixtures in bounded environments and retain exact artifact/version, SHA-256, fixture/environment IDs, evaluator version, timestamp, latency/cost, result, prohibited side effects, receipt hash, workflow provenance, and limitations.
- Label procedural framework/TestModel execution as framework plumbing; never present it as model-backed capability.
- Contextual outreach may be drafted with an exact public trigger, opt-out/suppression, audit trail, and human approval. No autonomous bulk email, stargazer campaigns, unsolicited mass DM, or automated GitHub advertising.

### Readiness and human gates

Set `TECHNICAL_PRIVATE_ALPHA_READY=YES` only after all feasible engineering acceptance criteria pass, with only named human/external actions remaining. Real buyer interviews, workflow/fee agreement, signed scope, qualified legal/tax review, seller/payment-route eligibility, customer acceptance, and actual payment are human/external gates. Do not mark the paid pilot complete until buyer acceptance and payment are evidenced.

Keep issue #8 OPEN/GATED. Do not build wallets, escrow, a labor exchange, complex payment architecture, or self-serve recurring billing before first-pilot evidence. External API keys, organization overrides, metering, and plan gates should be introduced only when a concrete pilot or proven demand requires them.
