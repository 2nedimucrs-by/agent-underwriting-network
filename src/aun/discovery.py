from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AgentCard, EvidenceDimensions


ROOT = Path(__file__).resolve().parents[2]
SEEDS_PATH = ROOT / "data" / "seeds.json"
OUTPUT_PATH = ROOT / "site" / "data" / "agents.json"


def _github_get(path: str, token: str | None) -> dict[str, Any]:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "agent-underwriting-network/0.1",
        },
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def discover_repository(full_name: str, token: str | None = None) -> AgentCard:
    repo = _github_get(f"/repos/{full_name}", token)
    default_branch = repo.get("default_branch") or "main"
    commit_sha = None
    try:
        commit = _github_get(f"/repos/{full_name}/commits/{default_branch}", token)
        commit_sha = commit.get("sha")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        pass

    observed = datetime.now(timezone.utc).isoformat()
    return AgentCard(
        agent_id=f"github:{full_name.lower()}",
        source={"kind": "github", "url": repo["html_url"]},
        version={
            "identifier": commit_sha or default_branch,
            "commit_sha": commit_sha,
            "observed_at": observed,
        },
        status="DISCOVERED_NOT_VERIFIED",
        evidence_dimensions=EvidenceDimensions(
            identity="EVIDENCE_PARTIAL",
            provenance="EVIDENCE_PARTIAL",
            freshness="EVIDENCE_PARTIAL",
        ),
        metadata={
            "repository": full_name,
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "archived": bool(repo.get("archived")),
            "license": (repo.get("license") or {}).get("spdx_id"),
            "pushed_at": repo.get("pushed_at"),
            "default_branch": default_branch,
        },
    )


def build_index(
    seeds_path: Path = SEEDS_PATH,
    output_path: Path = OUTPUT_PATH,
) -> list[dict[str, Any]]:
    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))["repositories"]
    token = os.environ.get("GITHUB_TOKEN")
    cards: list[AgentCard] = []
    failures: list[dict[str, str]] = []

    for full_name in seeds:
        try:
            cards.append(discover_repository(full_name, token))
        except Exception as exc:
            failures.append(
                {"repository": full_name, "error": type(exc).__name__}
            )

    payload = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Discovery metadata only. DISCOVERED does not mean VERIFIED.",
        "agents": [card.to_dict() for card in cards],
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload["agents"]


def main() -> int:
    agents = build_index()
    print(f"published {len(agents)} discovered agent/tool profiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
