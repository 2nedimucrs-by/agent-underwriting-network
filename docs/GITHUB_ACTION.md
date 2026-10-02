# Maintainer GitHub Action

Maintainers can generate a bounded, version-pinned evidence snapshot inside their own CI without granting Agent Underwriting Network repository write access.

Example:

```yaml
name: Agent evidence snapshot

on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - id: aun
        uses: 2nedimucrs-by/agent-underwriting-network@main
      - uses: actions/upload-artifact@v4
        with:
          name: aun-evidence
          path: ${{ steps.aun.outputs.evidence-path }}
```

The action observes only a bounded set of root manifest files and emits hashes plus declared permission/tool-surface signals.

Its output status is:

`SELF_COLLECTED_NOT_VERIFIED`

Maintainer-generated evidence can later be ingested as one source, but it cannot independently upgrade security or capability to VERIFIED.
