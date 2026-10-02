# Agent Underwriting Network

Independent, evidence-linked task-fitness infrastructure for AI agents, MCP tools and agent ecosystems.

**Live public index:** https://2nedimucrs-by.github.io/agent-underwriting-network/

## Core question

Do not ask only whether an agent is "safe."

Ask whether a specific, version-pinned agent is fit for a specific task, under a specific permission and budget envelope, with evidence.

The network separates:

- identity and source provenance
- security and permission evidence
- capability evidence
- reliability evidence
- economics and latency evidence
- version freshness
- task-specific underwriting decisions

No single universal trust score is treated as authority.

## Public alpha

The public site is built and deployed with GitHub Actions + GitHub Pages. The discovery pipeline refreshes a curated 125-project agent ecosystem corpus and generates:

- public agent/tool profiles
- exact default-branch head pins where GitHub exposes them
- evidence-linked Trust Card JSON
- raw Evidence Record JSON
- README evidence badges
- side-by-side comparison
- search/category/sort directory
- sitemap and robots metadata

The V0 evidence layer is deliberately conservative. Public repository metadata can support partial identity, provenance and freshness evidence. It does **not** automatically prove security, permissions, capability, reliability or economics.

## Long-term sequence

**Index -> Evidence Network -> Underwriting API -> Agent Router -> Verified Labor Exchange**

Marketplace, wallet, escrow and automated purchasing are intentionally out of scope until the evidence network has meaningful real-world history.

## Operating principles

DISCOVERED != VERIFIED

SECURE != CAPABLE

CAPABLE != AUTHORIZED

AUTHORIZED != ECONOMIC

MISSING REQUIRED EVIDENCE = FAIL CLOSED

## Development

Python 3.11+.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/discover.py
python scripts/validate_static_site.py
```

## License

Apache-2.0. See LICENSE.
