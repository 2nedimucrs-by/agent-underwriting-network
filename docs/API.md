# Underwriting API contract

## POST /can-hire

Purpose:

Given an exact agent identity, a task type and requested operational limits, return a fail-closed task-fitness decision backed by evidence.

### Request

```json
{
  "agent_id": "github:browser-use/browser-use",
  "task_type": "browser_read",
  "version_commit_sha": "0123456789abcdef0123456789abcdef01234567",
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

### Authentication and limits

The deployed `can-hire` function requires an authenticated Supabase user session. Its current request contract does not include a client-selected commit SHA: the function fetches the latest Trust Card for the repository. Therefore exact-version request/response binding is still an OPEN V1 acceptance gate, even though cards themselves carry a version field. Before technical readiness, require the exact 40-character commit SHA, compare it with the fetched card version, fail closed on mismatch/unresolved versions, and return that SHA with the decision. Anonymous and invalid-session requests must be denied. Authenticated per-user rate limits are implemented atomically at 30 requests per minute and 500 per day; external organization/API-key authentication is deferred until a specific pilot or post-pilot demand requires it.

Rate-limit implementation is not acceptance proof. Required tests cover concurrency/atomicity, malformed JSON and field types, missing agents, unknown tasks, invalid JWTs, cross-user isolation, and database/RPC failure. The limit must fail closed when the authority is unavailable. Client-provided counters are never trusted.

Request parsing must reject non-object bodies, unknown fields, missing or malformed agent/task identifiers, non-boolean `write_access`, and non-finite, negative, or wrongly typed `max_spend_usd` before evaluating a decision. Malformed requests return a client error and must not consume a successful decision path. Strict request parsing and malformed-input tests are implemented in the current draft PR; they are not yet in `main` or the deployed Edge Function. Production malformed-body acceptance remains OPEN until the change is reviewed, merged, and verified live.
