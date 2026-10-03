# AUN Product Context and Revenue Plan

_Last reviewed: 2026-10-03_

## Compressed product context

Agent Underwriting Network (AUN) is an evidence-first index and task-fitness product for AI agents, MCP tools, and agent infrastructure. Its promise is to help a buyer decide whether an exact, version-pinned agent is fit for a particular task under explicit permissions, risk limits, and budget constraints.

The live public alpha currently provides a curated discovery index, version-pinned public-source Trust Cards, comparison, account/workspace scaffolding, and a fail-closed task-underwriting simulator. Public repository metadata is only partial identity/provenance/freshness evidence; it does not prove security, capability, reliability, permission enforcement, or economics. The task-underwriting page explicitly says it is a simulator and does not grant production permission.

Product principles:
- DISCOVERED != VERIFIED; evidence is version-specific and source-linked.
- No universal trust score, pay-to-rank slots, or paid influence over evidence/verdicts.
- Missing required evidence fails closed.
- Marketplace, wallet, escrow, and automated purchasing wait until the evidence network has a meaningful track record.

## Current launch gaps and order

1. **Google discovery:** Search Console currently reports the homepage as unknown/not indexed and the submitted sitemap as “Couldn't fetch” with zero discovered pages. The sitemap is generated during the Pages build by `src/aun/discovery.py`; the validator currently checks that generated sitemap and robots files exist. Next: verify the deployed sitemap response and XML/URL contents from a browser or Google URL inspection, then strengthen build validation and resubmit only after the fetch problem is identified.
2. **Launch gate (#16):** complete privacy/terms review, auth/RLS abuse tests, recovery/export test, monitoring and rate limits, accessibility/browser QA, private-alpha buyer validation, and evidence that paid plans cannot change evidence truth.
3. **Capability receipts (#15):** run reproducible, task-specific fixtures with pinned artifacts, environment, pass/fail criteria, latency, and cost.
4. **Workspace value (#12):** finish saved agents, drift alerts, and user-visible notification behavior with opt-in email.
5. **Analytics (#11):** complete privacy-first product analytics and admin metrics; keep Cloudflare traffic analytics distinct from product analytics.

## Recommended revenue sequence

### Phase 0 — Validate the buyer and the job

Interview AI platform/security/procurement teams and agent-platform maintainers. Focus on a recurring decision they already make: selecting or approving an agent for a real workflow. Ask for a concrete recent decision, evidence they used, the cost of a wrong choice, the review owner, and what would make an independent report useful. Record willingness-to-pay separately from general interest.

Do not charge for a security/capability verdict that the current evidence system cannot substantiate.

### Phase 1 — Paid design-partner pilot (manual delivery)

Offer a time-bounded pilot for one narrowly scoped workflow and a small, agreed set of agents. Deliver an evidence register, version/provenance snapshot, explicit unknowns, reproducible task-specific test receipts where available, and a decision workshop. Clearly label any untested dimension as unknown; do not claim a guarantee or blanket safety certification. Use the public [pilot evidence report template](./PILOT_REPORT_TEMPLATE.md) so the buyer can trace each conclusion to its source or executed receipt; never present a mock fixture as a real third-party result. Prepare a customer-specific scope using the [paid pilot scope sheet](./PAID_PILOT_SCOPE_TEMPLATE.md), then move the final agreement off this public repository for legal review and signature.

Pricing hypothesis to test, not a published price: **$500–$1,500 per pilot**, adjusted after the first buyer interviews based on scope and review effort. A lower-cost or no-charge design-partner slot is acceptable only when it buys specific access to a real workflow, reviewer feedback, and permission to use anonymized learnings. Define deliverables and acceptance in writing before accepting payment.

This validates value before building billing or an automated underwriting API.

#### Minimum sellable first pilot

- **Buyer:** an AI platform, security, or procurement team that already makes agent approval decisions for a real workflow.
- **Scope:** one named workflow and up to five exact, version-pinned agents, delivered in a time-boxed two-week review. Start with public or explicitly authorized evidence. Do not require production credentials or claim that AUN has safely executed an agent in a customer environment.
- **Deliverables:** a source-linked evidence register with observation time and artifact/version identity; a task-fit matrix covering capability, permission, dependency, freshness, and material unknowns; reproducible receipts only for fixtures and adapters actually run; and a review session with a decision record. Every conclusion must point to evidence. Unknown or untested dimensions stay unknown; the report is not a certification or deployment authorization.
- **Acceptance:** the buyer receives the agreed evidence pack and review session; each material claim has a source or receipt; unresolved gaps and stale evidence are visible; no secrets are included in the report.
- **Commercial setup:** agree the workflow, agent limit, deliverables, exclusions, schedule, fee, and payment date in a signed business-to-business scope before work begins. Select a pilot fee within the existing hypothesis range based on review effort. Request payment only after the seller entity, tax obligations, and enabled payment route have been checked; use Payoneer only if the account supports the relevant commercial B2B request. Payment does not unlock or change evidence, verdicts, ranking, or production permissions.
- **Evidence to proceed:** record at least three buyer/problem interviews and one pilot buyer's written acceptance of scope and price. Do not claim commercial readiness until a real pilot is delivered and accepted and the agreed payment is confirmed.



### Phase 2 — Self-serve team subscription

Only after the account workspace and monitoring deliver recurring value, test a per-workspace subscription. Candidate paid value: saved-agent portfolio, version/evidence drift alerts, evidence history/export, team review notes, and policy templates. Keep the public index free. Charge for workflow, monitoring, collaboration, and service capacity—not for better scores, faster verdicts, badges, or ranking.

Initial price hypotheses to test with buyers: **$99–$299/month per team workspace**. These are experiments, not final prices. Set usage caps around costly benchmark/scanner runs, show cost before execution, and sell additional runs transparently.

### Phase 3 — Enterprise/API

Offer custom annual agreements only after there is a production underwriting API, documented evidence freshness, audit/recovery behavior, access controls, support expectations, and measured customer value. Price by monitored portfolio/workflow volume and support/SLA scope. Marketplace take-rate, escrow, and automated agent purchasing remain deferred.

## Payment collection recommendation

Payment-provider preference: Stripe is excluded at the founder's request. This public plan records the provider strategy only; it does not publish private company or payment-account details.

1. **First B2B design-partner pilot:** for a signed business-to-business pilot scope, use a Payoneer Payment Request, invoice, or payment link only if the seller account has that feature enabled. Payoneer supports business-client payment links without a technical integration, while reusable/recurring links are eligibility-dependent. Its Billing Solutions terms limit these tools to commercial business transactions and prohibit consumer sales. Bill only an agreed, due amount. This is manual collection, not AUN checkout, and does not automatically activate product entitlements.
2. **Self-serve SaaS checkout:** Stripe is excluded at the founder's request. Evaluate Paddle Billing as the first hosted-checkout candidate after seller, business, identity, and domain review. Paddle acts as Merchant of Record and documents handling global indirect taxes, refunds, and chargebacks. Its published price is currently 5% + $0.50 per transaction. Paddle documents Payoneer as a payout option, with monthly payouts subject to a minimum threshold and Payoneer fees. Confirm the seller is approved, the payout route works, and the full terms are acceptable before integrating.
3. **Payoneer Checkout is separate from Payment Links.** Its current web checkout page describes additional entity and high-volume eligibility requirements, so it is not the initial AUN route. Revisit it only if the product reaches the stated eligibility threshold and Payoneer confirms access.
4. **Fallback if Paddle does not approve the seller:** pause self-serve billing and compare other non-Stripe providers, including PayPal Business, for customer coverage, recurring billing, tax responsibilities, payout route, and fees. Do not silently reintroduce Stripe.
5. **iyzico remains an optional local-market alternative** only if an eligible Türkiye-based seller is selected and approved.
6. **Provider-independent entitlement boundary:** all plans, purchases, refunds, cancellations, and entitlements must be recorded and verified server-side. The browser may open hosted checkout and show current entitlement, but must never grant access based on a query parameter or client-side success screen. Validate signed provider webhooks, make processing idempotent, retain a minimal audit trail, and apply access changes from verified server state. Keep secrets out of static Pages assets, logs, and client code.

### Go-live gates

- Confirm the seller entity's current standing, required filings, and tax obligations with official records and a qualified tax professional before accepting payments.
- Confirm Payoneer account KYC, enabled B2B billing features, fees, settlement path, and applicable terms in the seller account.
- Complete Paddle's business, identity, and domain review; confirm Payoneer payout configuration and settlement timing before launch.
- Do not accept consumer subscriptions through Payoneer Billing Solutions; use an approved consumer/SaaS checkout for that phase.
- Validate one successful test transaction, duplicate webhook, failed payment, cancellation, refund, and entitlement removal in sandbox before launch.
- Run buyer interviews and at least one paid pilot before committing to self-serve plan names or public prices.
- Keep evidence/verdict computation independent of payment status; never sell a stronger verdict.

## Current status snapshot

- Google indexing: **BLOCKED/UNRESOLVED** — Search Console sitemap fetch and discovery still need a live response diagnosis.
- Cloudflare Web Analytics: **ON** in the latest verified Pages runtime; existing Supabase product analytics remains **ON**.
- Billing implementation: **NOT STARTED** — provider preference excludes Stripe; Payoneer B2B billing and Paddle seller/payout eligibility must be verified before implementation.
- Commercial readiness: **NOT PROVEN** — the public alpha does not yet provide verified task-specific underwriting at production quality.

## Primary references

- [Payoneer Payment Links](https://www.payoneer.com/payment-links/)
- [Payoneer Payment Requests](https://www.payoneer.com/payment-request/)
- [Payoneer Billing Solutions terms](https://pubs.payoneer.com/legal/PayoneerTermsAndConditionsINC_Apr2026.htm)
- [Payoneer Checkout eligibility](https://www.payoneer.com/checkout/)
- [Paddle merchant-of-record model](https://developer.paddle.com/get-started/how-paddle-works/)
- [Paddle account verification](https://www.paddle.com/help/start/account-verification/what-is-account-verification)
- [Paddle payout methods and timing](https://www.paddle.com/help/manage/get-paid/when-and-how-do-i-get-paid)
- [Paddle payout fees](https://www.paddle.com/help/manage/get-paid/is-there-a-fee-taken-for-payouts)
- [Paddle current pricing](https://www.paddle.com/pricing)
- [IRS guidance on closing an inactive business](https://www.irs.gov/newsroom/what-if-i-close-my-own-business)
- [Google Search Console sitemap report](https://support.google.com/webmasters/answer/7451001?hl=en-GB)
