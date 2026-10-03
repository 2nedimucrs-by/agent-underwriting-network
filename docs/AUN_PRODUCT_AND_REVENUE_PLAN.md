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

1. **Google discovery:** A live browser check on 2026-10-03 loaded the public homepage directory with 125 profiles and 12 categories. The initial URL Inspection result said “URL is unknown to Google” and showed no referring sitemap. A later live URL test (04:27 Turkey time) reported “URL is available to Google” and “Page can be indexed”; the subsequent indexing request was accepted and Google confirmed it was added to the priority crawl queue. This confirms fetchability for the homepage at test time, not that it has been indexed. The submitted `/sitemap.xml` still reports “Couldn't fetch,” zero discovered pages, and “Sitemap could not be read.” The Pages workflow (#185) succeeded on main `b8a8cd5378372b77a24dec543b6ab930f52ca2e0` and produced a `github-pages` artifact. The sitemap and `robots.txt` are generated during the Pages build by `src/aun/discovery.py`, but the validator checks file presence rather than the published HTTP response or parsed XML. Direct retrieval from this environment is blocked, so the sitemap status/body and root cause remain unverified. Next: verify both deployed endpoints and XML/URL contents from an external fetch; diagnose the sitemap before resubmitting it.
2. **Launch gate (#16):** Live desktop browser smoke on 2026-10-03 confirmed the loaded homepage shows 125 profiles across 12 categories; the Underwrite page labels itself a simulator, fails closed when required VERIFIED evidence is missing, and requires sign-in for the deployed API; the account page offers GitHub OAuth and email magic link without asking for the GitHub password. The live Privacy and Terms pages are still marked as drafts and explicitly require qualified legal review before commercial launch. An additional limited desktop accessibility smoke found labeled search/category/sort controls and compare checkboxes, a working search for “n8n,” keyboard focus movement from Search to Category with a visible focus ring, and primary buttons/filters sized at least 44/48 CSS pixels. This is not a full WCAG audit: mobile, screen-reader, 200% zoom, and automated accessibility checks remain open. The authenticated per-user rate-limit migration and `can-hire` v3 RPC are now present in the live Supabase project; catalog checks confirm `SECURITY INVOKER`, an empty `search_path`, and execution granted only to `service_role`. Concurrent-load and database-outage/fail-closed tests remain open, along with auth/RLS abuse tests, recovery/export, monitoring, private-alpha buyer validation, and the invariant that paid plans cannot change evidence truth.
3. **Capability receipts (#15):** deterministic fixture contracts now cover structured extraction, read-only file/repository tasks, browser navigation, and MCP invocation. CI's fake harness proves evaluator behavior only; it is not evidence that a third-party agent passed. Next: execute pinned third-party adapters in an isolated environment and capture artifact/version, environment, criteria, latency, and cost.
4. **Workspace value (#12):** finish saved agents, drift alerts, and user-visible notification behavior with opt-in email.
5. **Analytics (#11):** complete privacy-first product analytics and admin metrics; keep Cloudflare traffic analytics distinct from product analytics.

## Recommended revenue sequence

### Phase 0 — Validate the buyer and the job

Interview AI platform/security/procurement teams and agent-platform maintainers. Use the [buyer discovery interview guide](./PILOT_BUYER_INTERVIEW_GUIDE.md) to keep questions neutral. Focus on a recurring decision they already make: selecting or approving an agent for a real workflow. Ask for a concrete recent decision, evidence they used, the cost of a wrong choice, the review owner, and what would make an independent report useful. Record willingness-to-pay separately from general interest.

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

1. **First B2B design-partner pilot:** for a signed business-to-business pilot scope, use a Payoneer Payment Request, invoice, or payment link only after the seller account confirms eligibility for that feature. Payoneer supports requests to business clients without an AUN integration, while payment methods, currencies, and reusable links depend on account eligibility. Its current U.S. terms limit Billing Solutions to commercial transactions and prohibit consumer payments; requests may cover only an undisputed amount that is owed and due, not debt collection. Send requests or links only to the correct, consenting business payer through a secure direct channel; do not publish them on a public website, post them to mass media, or distribute them in bulk. Do not reuse a single-payment request for the same amount. Payoneer may require identity, line-of-business, invoice, or service-delivery evidence before or after a request. Treat collection as manual, separate from AUN checkout, and never as automatic product entitlement.
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
- Underwriting limits: authenticated per-user atomic rate checks are live and database permissions were verified; concurrent-load and database-outage/fail-closed tests remain pending.
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
