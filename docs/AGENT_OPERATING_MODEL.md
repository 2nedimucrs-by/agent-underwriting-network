# Runtime operating model

The system starts with one Chief and ten bounded specialist workers. A worker is a role, not necessarily an LLM. Deterministic code is preferred whenever reasoning is unnecessary.

## Chief

**Underwriting Chief** owns the work graph, evidence freshness, retries, stop conditions and publication gates. The Chief cannot convert missing evidence into a positive claim.

## Specialists

1. GitHub Scout — discovers public agent repositories and metadata.
2. MCP/A2A Scout — discovers registries, servers and agent cards.
3. Release Watcher — detects new versions and evidence staleness.
4. Provenance Auditor — binds claims to source, version and hash.
5. Permission Auditor — extracts declared and observed permission surfaces.
6. Security Aggregator — normalizes scanner findings; does not claim absolute safety.
7. Capability Benchmark Worker — runs task-specific reproducible fixtures.
8. Evidence Compiler — produces portable evidence records and public profile projections.
9. Lead Intelligence Worker — finds public/professional maintainer and buyer-intent signals.
10. Outreach/SEO Worker — prepares contextual outreach and public index pages.

## External-action rule

No autonomous bulk email, GitHub-comment spam, credential use, purchasing, or high-risk write action.

Outreach starts as a reviewable queue. Human authorization can later be delegated only through explicit policy.
