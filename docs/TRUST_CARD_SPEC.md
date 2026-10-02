# Portable Trust Card v0

A Trust Card is a version-pinned projection of evidence. It is not a universal certification.

## Independent dimensions

- Identity
- Provenance
- Security
- Permissions
- Capability
- Reliability
- Economics
- Freshness

Each dimension is one of:

- NOT_EVALUATED
- EVIDENCE_PARTIAL
- VERIFIED
- FAILED
- STALE

## Task-specific decision

Task underwriting returns one of:

- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW_REQUIRED
- DENY
- INSUFFICIENT_EVIDENCE

A decision must list the evidence IDs used. If required evidence is missing or stale, the system fails closed rather than guessing.
