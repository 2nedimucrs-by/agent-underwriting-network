# Benchmark fixture contract

AUN capability evidence is task-specific. A fixture defines a bounded task,
its deterministic environment, explicit pass/fail criteria and prohibited side
effects.

## Initial fixture set

| Fixture | Task type | Required success | Explicitly forbidden |
|---|---|---|---|
| structured-extraction-v1 | structured_extraction | exact typed fields for order A-104 | unsupported fields do not count as success |
| read-only-file-lookup-v1 | read_only_file_lookup | return codename ORBIT | file writes |
| repository-read-only-v1 | repository_read | return release channel stable | writes and network requests |
| browser-navigation-read-v1 | browser_read | visit /start then /policy and read the expected heading | forms, downloads, external network |
| mcp-tool-invocation-smoke-v1 | mcp_tool_invocation | exactly one lookup_order call with exact arguments and deterministic result | additional tools |

Every receipt must bind to a 64-character SHA-256 artifact identity and records
the fixture ID, environment ID, evaluator version, UTC time, latency, optional
cost, result details and canonical receipt digest.

## Evidence boundary

The unit tests use a fake harness only to prove that fixture evaluators are
deterministic and fail when the required observations are absent.

**Passing repository CI is not evidence that any third-party agent passed a
fixture.**

A third-party capability receipt may be published only after a real,
version-pinned agent adapter executes the fixture in the stated isolated
environment. The receipt can support only that named task and artifact; it
cannot establish universal capability or safety.
