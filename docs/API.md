# Underwriting API contract

## POST /can-hire

Purpose:

Given an exact agent identity, a task type and requested operational limits, return a fail-closed task-fitness decision backed by evidence.

### Request

```json
{
  "agent_id": "github:browser-use/browser-use",
  "task_type": "browser_read",
  "limits": {
    "write_access": false,
    "max_spend_usd": 0
  }
}
```

### Decision set

- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW_REQUIRED
- DENY
- INSUFFICIENT_EVIDENCE

### Public-alpha behavior

Current public Trust Cards are mostly EVIDENCE_PARTIAL or NOT_EVALUATED. Therefore the API should normally return INSUFFICIENT_EVIDENCE rather than convert popularity, maintainer identity or scanner absence into trust.

### Evidence rule

A decision returns the evidence IDs used by the current Trust Card. Missing or stale required evidence fails closed.

### Policy rule

Task policies are stored in `config/task_policies.json`.

A policy determines:

- required VERIFIED dimensions
- whether write access can be granted
- maximum spend limit

Customers may configure stricter future organization policies. A paid plan must never purchase a better evidence verdict.

### Authentication

The first deployable Edge Function version requires a valid Supabase user session. Organization/API-key authentication and rate limits are a later production-hardening step.
