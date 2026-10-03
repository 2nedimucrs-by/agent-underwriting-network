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


### Response

Decision responses use `schema_version: "2.0.0"` and include the exact `version_commit_sha` used for the decision.

```json
{
  "schema_version": "2.0.0",
  "decision": "INSUFFICIENT_EVIDENCE",
  "agent_id": "github:browser-use/browser-use",
  "task_type": "browser_read",
  "version_commit_sha": "0123456789abcdef0123456789abcdef01234567",
  "reasons": ["required VERIFIED evidence is missing for: capability"],
  "limits": { "write_access": false, "max_spend_usd": 0 },
  "evidence_ids": [],
  "missing_dimensions": ["capability"]
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

The live `main` deployment requires an authenticated Supabase user session and still uses the pre-#30 request contract. PR #30 changes the contract to require a 40-character commit SHA, compare it with the fetched Trust Card version, fail closed on mismatch or unresolved versions, and return the pinned SHA with each decision under response schema version `2.0.0`. Production exact-version acceptance remains open until the change is reviewed, merged, deployed, and checked with live negative-input and version-mismatch tests. Anonymous and invalid-session requests must be denied. Authenticated per-user rate limits are implemented atomically at 30 requests per minute and 500 per day; external organization/API-key authentication is deferred until a specific pilot or post-pilot demand requires it.

Rate-limit implementation is not acceptance proof. Required tests cover concurrency/atomicity, malformed JSON and field types, missing agents, unknown tasks, invalid JWTs, cross-user isolation, and database/RPC failure. The limit must fail closed when the authority is unavailable. Client-provided counters are never trusted.

Request parsing must reject non-object bodies, unknown fields, missing or malformed agent/task identifiers, non-boolean `write_access`, and non-finite, negative, or wrongly typed `max_spend_usd` before evaluating a decision. Malformed requests return a client error and must not consume a successful decision path. Strict request parsing and malformed-input tests are implemented in the current draft PR; they are not yet in `main` or the deployed Edge Function. Production malformed-body acceptance remains OPEN until the change is reviewed, merged, and verified live.
