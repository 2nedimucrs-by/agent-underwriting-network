# Portable Trust Card v0.1

A Trust Card is a version-pinned projection of evidence. It is not a universal certification, warranty, endorsement, or deployment permission.

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

## Evidence linking

Every non-NOT_EVALUATED state must be traceable to one or more Evidence Records.

Each Evidence Record contains:

- evidence ID
- agent ID
- evidence dimension
- human-readable claim
- explicit result state
- source kind and locator
- observation time
- optional expiry time
- optional artifact/version hash
- test or collection environment

Public GitHub metadata can support EVIDENCE_PARTIAL identity, provenance and freshness observations. It cannot by itself produce VERIFIED security, permission, capability, reliability or economic claims.

## Badge semantics

The public README badge is a link to the current Trust Card.

A badge must never use the word VERIFIED unless the displayed claim is actually backed by evidence for the pinned version.

The V0 public badge therefore says **evidence partial**.

A maintainer adding a badge does not become the authority for the evidence and cannot remove unfavorable evidence simply by claiming a profile.

## Task-specific decision

Task underwriting returns one of:

- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW_REQUIRED
- DENY
- INSUFFICIENT_EVIDENCE

A decision must list the evidence IDs used. If required evidence is missing or stale, the system fails closed rather than guessing.
