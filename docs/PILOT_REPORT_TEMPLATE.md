# AUN First-Pilot Evidence Report

> Template only. A blank template is not evidence, a certification, a warranty, or a production authorization. Complete one copy per agreed pilot; do not commit customer-specific completed reports to this public repository.

## Report control

- Report ID:
- Prepared on (UTC):
- Prepared by:
- Customer-approved recipient:
- Scope / statement of work reference:
- Review version:

## Decision requested

- Business workflow:
- Decision owner:
- What decision is the customer trying to make?
- Consequence of an incorrect decision:
- Customer policy and constraints:

## Scope boundary

- Included agents (exact identity and version):
- Explicitly excluded agents or tasks:
- Permitted evidence sources:
- Test environment, if any:
- Allowed actions:
- Prohibited actions:
- Data handling and retention agreed for this review:
- Human approval points:

Do not include credentials, secrets, personal data not needed for the review, or private source material without explicit authorization and an agreed secure handling process.

## Executive outcome

Choose one task-specific outcome:

- [ ] ALLOW
- [ ] ALLOW_WITH_LIMITS
- [ ] REVIEW_REQUIRED
- [ ] DENY
- [ ] INSUFFICIENT_EVIDENCE

- Task / policy evaluated:
- Decision date:
- Expiry or re-review trigger:
- Plain-language rationale:
- Human reviewer:

This is a scoped evidence-based recommendation. It is not a universal agent score, security certification, legal opinion, warranty, or authorization to deploy.

## Agent identity and version pins

| Agent | Maintainer/source | Exact version or commit | Artifact hash | Observed on |
|---|---|---|---|---|
| | | | | |

If exact identity or version cannot be established, mark the affected evidence INSUFFICIENT or STALE.

## Evidence register

Use one stable evidence ID per item. Link the original source or attached receipt. Retain conflicting results as separate entries.

| Evidence ID | Claim / dimension | State (OBSERVED, PASSED, FAILED, UNKNOWN, STALE, NOT_RUN) | Source or receipt | Tool/version and method | Artifact/version pin | Observed (UTC) | Limitations |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Task-specific capability receipts

Include only fixtures that were actually executed against the identified agent in the stated environment.

| Receipt ID | Fixture and evaluator version | Agent artifact hash | Environment | Result | Latency | Cost | Receipt link/hash |
|---|---|---|---|---|---:|---:|---|
| | | | | | | | |

For every unexecuted fixture, write NOT_RUN and explain why. A mock harness or local fixture-contract test is not a third-party capability result.

## Permissions and operating limits

| Permission / resource | Required by task? | Agent declared it? | Independently observed? | Allowed limit | Evidence ID |
|---|---|---|---|---|---|
| Filesystem | | | | | |
| Network | | | | | |
| Tools / MCP | | | | | |
| Credentials | | | | | |
| Spend / rate | | | | | |
| Human approval | | | | | |

A declaration is not proof of enforcement. Mark enforcement UNKNOWN unless it was tested in the exact environment.

## Dependencies and security signals

- Manifest and lockfile sources:
- Dependency scanner and version:
- Advisories observed:
- Scanner coverage and exclusions:
- Conflicts between sources:
- Scanner errors or unavailable sources:

Scanner success does not mean SAFE. Do not average conflicting findings into a single score.

## Unknowns, risks, and required follow-up

| Item | Why it matters | Evidence needed | Owner | Re-review trigger |
|---|---|---|---|---|
| | | | | |

## Recommendation and limits

- Recommendation:
- Conditions or limits:
- Evidence IDs supporting the recommendation:
- Required human checks:
- Conditions that invalidate this report:
- Next review date or trigger:

## Customer review and acceptance

- Delivered on:
- Review session held on:
- Customer acceptance of agreed deliverables:
- Open questions:
- Accepted by (name/title or customer-controlled reference):
- Acceptance date:

Acceptance confirms receipt of the scoped deliverables only; it does not convert unknown evidence into verified evidence.
