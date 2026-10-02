from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .evidence_ops import enrich_card, load_targets
from .models import AgentCard, EvidenceDimensions


ROOT = Path(__file__).resolve().parents[2]
SEEDS_PATH = ROOT / "data" / "seeds.json"
SITE_ROOT = ROOT / "site"
OUTPUT_PATH = SITE_ROOT / "data" / "agents.json"
PUBLIC_BASE = "https://2nedimucrs-by.github.io/agent-underwriting-network"


def _github_get(path: str, token: str | None, retries: int = 2) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-underwriting-network/0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                f"https://api.github.com{path}",
                headers=headers,
            )
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.0 + attempt)
    assert last_error is not None
    raise last_error


def _slug(full_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", full_name.lower()).strip("-")


def _category(full_name: str, description: str | None) -> str:
    haystack = f"{full_name} {description or ''}".lower()
    rules = [
        ("MCP / Tooling", ("mcp", "model context protocol")),
        ("Security / Evaluation", ("security", "scanner", "red team", "promptfoo", "garak", "pyrit", "giskard", "threat")),
        ("Observability", ("langfuse", "openlit", "helicone", "observability", "telemetry")),
        ("Memory", ("mem0", "graphiti", "letta", "memory")),
        ("Voice / Realtime", ("livekit", "pipecat", "voice", "realtime")),
        ("Browser / Computer Use", ("browser", "playwright", "ui-tars", "autoglm", "computer use", "agent-s")),
        ("Coding", ("cline", "openhands", "continue", "trae", "coding", "developer agent")),
        ("Workflow / Orchestration", ("n8n", "dify", "activepieces", "langgraph", "crewai", "autogen", "workflow", "orchestrat")),
        ("Model / Inference", ("ollama", "vllm", "sglang", "litellm", "inference")),
        ("Robotics", ("lerobot", "openpi", "robot")),
        ("Document / Knowledge", ("docling", "markitdown", "graphrag", "llama_index", "haystack")),
    ]
    for label, needles in rules:
        if any(needle in haystack for needle in needles):
            return label
    return "Agent / Framework"


def discover_repository(full_name: str, token: str | None = None) -> AgentCard:
    repo = _github_get(f"/repos/{full_name}", token)
    canonical_name = repo.get("full_name") or full_name
    default_branch = repo.get("default_branch") or "main"
    commit_sha = None

    try:
        commit = _github_get(
            f"/repos/{canonical_name}/commits/{default_branch}",
            token,
        )
        commit_sha = commit.get("sha")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        pass

    observed = datetime.now(timezone.utc).isoformat()
    slug = _slug(canonical_name)
    description = repo.get("description")

    return AgentCard(
        agent_id=f"github:{canonical_name.lower()}",
        source={"kind": "github", "url": repo["html_url"]},
        version={
            "identifier": commit_sha or default_branch,
            "commit_sha": commit_sha,
            "observed_at": observed,
        },
        status="DISCOVERED_NOT_VERIFIED",
        evidence_dimensions=EvidenceDimensions(
            identity="EVIDENCE_PARTIAL",
            provenance="EVIDENCE_PARTIAL" if commit_sha else "NOT_EVALUATED",
            freshness="EVIDENCE_PARTIAL",
        ),
        metadata={
            "repository": canonical_name,
            "owner": (repo.get("owner") or {}).get("login"),
            "name": repo.get("name"),
            "description": description,
            "homepage": repo.get("homepage"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "watchers": repo.get("subscribers_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "archived": bool(repo.get("archived")),
            "fork": bool(repo.get("fork")),
            "license": (repo.get("license") or {}).get("spdx_id"),
            "language": repo.get("language"),
            "topics": repo.get("topics") or [],
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "default_branch": default_branch,
            "category": _category(canonical_name, description),
            "slug": slug,
            "profile_path": f"agents/{slug}/",
            "trust_card_path": f"trust-cards/{slug}.json",
            "evidence_path": f"evidence/{slug}.json",
            "badge_path": f"badges/{slug}.svg",
        },
    )


def _evidence_for(card: AgentCard) -> list[dict[str, Any]]:
    metadata = card.metadata
    observed = card.version.get("observed_at")
    commit_sha = card.version.get("commit_sha")
    repository = metadata.get("repository")
    prefix = hashlib.sha256(
        f"{card.agent_id}:{card.version.get('identifier')}".encode("utf-8")
    ).hexdigest()[:12]

    evidence = [
        {
            "schema_version": "1.0.0",
            "evidence_id": f"ev-{prefix}-identity",
            "agent_id": card.agent_id,
            "dimension": "identity",
            "claim": "A public GitHub repository and publisher identity were observed.",
            "result": "EVIDENCE_PARTIAL",
            "source": {
                "kind": "github-repository-metadata",
                "locator": card.source["url"],
            },
            "observed_at": observed,
            "expires_at": None,
            "artifact_hash": None,
            "environment": {"collector": "github-rest-v2022-11-28"},
        },
        {
            "schema_version": "1.0.0",
            "evidence_id": f"ev-{prefix}-freshness",
            "agent_id": card.agent_id,
            "dimension": "freshness",
            "claim": "Repository update and push timestamps were observed from GitHub.",
            "result": "EVIDENCE_PARTIAL",
            "source": {
                "kind": "github-repository-metadata",
                "locator": card.source["url"],
            },
            "observed_at": observed,
            "expires_at": None,
            "artifact_hash": None,
            "environment": {
                "pushed_at": metadata.get("pushed_at"),
                "updated_at": metadata.get("updated_at"),
            },
        },
    ]

    if commit_sha:
        evidence.append(
            {
                "schema_version": "1.0.0",
                "evidence_id": f"ev-{prefix}-provenance",
                "agent_id": card.agent_id,
                "dimension": "provenance",
                "claim": "The default branch head commit was resolved and version-pinned.",
                "result": "EVIDENCE_PARTIAL",
                "source": {
                    "kind": "github-commit",
                    "locator": f"https://github.com/{repository}/commit/{commit_sha}",
                },
                "observed_at": observed,
                "expires_at": None,
                "artifact_hash": commit_sha,
                "environment": {
                    "default_branch": metadata.get("default_branch"),
                },
            }
        )

    return evidence


def _badge_svg(card: AgentCard) -> str:
    label = "evidence partial"
    left = "AUN"
    left_width = 42
    right_width = 104
    total = left_width + right_width
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{left}: {label}">
  <title>{left}: {label}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".08"/>
    <stop offset="1" stop-opacity=".08"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total}" height="20" rx="3"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{left_width}" height="20" fill="#252823"/>
    <rect x="{left_width}" width="{right_width}" height="20" fill="#8a6720"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">
    <text x="{left_width / 2}" y="14">{left}</text>
    <text x="{left_width + right_width / 2}" y="14">{label}</text>
  </g>
</svg>
"""


def _profile_html(card: AgentCard, evidence: list[dict[str, Any]]) -> str:
    m = card.metadata
    dims = card.evidence_dimensions.__dict__
    repo_name = html.escape(str(m.get("repository") or card.agent_id))
    desc = html.escape(str(m.get("description") or "No repository description."))
    category = html.escape(str(m.get("category") or "Agent / Framework"))
    commit = html.escape(str(card.version.get("commit_sha") or "unresolved"))
    observed = html.escape(str(card.version.get("observed_at") or "unknown"))
    source = html.escape(str(card.source.get("url") or ""))
    slug = str(m.get("slug"))
    license_name = html.escape(str(m.get("license") or "unknown"))
    language = html.escape(str(m.get("language") or "unknown"))
    claim_param = quote(card.agent_id, safe="")

    dimension_rows = "".join(
        f'<div class="dimension"><span>{html.escape(name.title())}</span><strong class="dim-state">{html.escape(state)}</strong></div>'
        for name, state in dims.items()
    )
    evidence_rows = "".join(
        f'<li><strong>{html.escape(ev["dimension"].title())}</strong><span>{html.escape(ev["claim"])}</span><code>{html.escape(ev["evidence_id"])}</code></li>'
        for ev in evidence
    )
    badge_url = f"{PUBLIC_BASE}/badges/{slug}.svg"
    profile_url = f"{PUBLIC_BASE}/agents/{slug}/"
    badge_md = f"[![Agent evidence]({badge_url})]({profile_url})"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{repo_name} · Trust Card · Agent Underwriting Network</title>
  <meta name="description" content="Version-pinned evidence card for {repo_name}.">
  <link rel="stylesheet" href="../../styles.css">
  <script src="../../runtime-config.js"></script>
</head>
<body>
  <header class="shell header">
    <a class="brand" href="../../">AUN <span>Agent Underwriting Network</span></a>
    <nav class="nav"><a href="../../#index">Index</a><a href="../../compare.html">Compare</a><a href="../../account.html">Account</a></nav>
    <span class="phase">TRUST CARD</span>
  </header>
  <main class="shell profile-main">
    <nav class="breadcrumbs"><a href="../../">Index</a><span>/</span><span>{repo_name}</span></nav>
    <section class="profile-hero">
      <div>
        <p class="eyebrow">{category}</p>
        <h1 class="profile-title">{repo_name}</h1>
        <p class="lede">{desc}</p>
      </div>
      <div class="profile-status">
        <img src="../../badges/{slug}.svg" alt="AUN evidence partial badge">
        <strong>DISCOVERED · NOT VERIFIED</strong>
        <span>Public metadata evidence only</span>
      </div>
    </section>

    <section class="trust-grid">
      <article class="panel">
        <p class="panel-label">VERSION PIN</p>
        <code class="commit">{commit}</code>
        <span>Observed {observed}</span>
      </article>
      <article class="panel">
        <p class="panel-label">SOURCE</p>
        <a href="{source}" target="_blank" rel="noreferrer">{repo_name}</a>
        <span>GitHub public repository</span>
      </article>
      <article class="panel">
        <p class="panel-label">PROJECT SIGNALS</p>
        <strong>★ {m.get("stars", 0)} · forks {m.get("forks", 0)}</strong>
        <span>{language} · license {license_name}</span>
      </article>
    </section>

    <section class="section-block">
      <div class="section-title">
        <div><p class="eyebrow">MULTIDIMENSIONAL</p><h2>Evidence dimensions</h2></div>
        <span>No universal trust score</span>
      </div>
      <div class="dimension-grid">{dimension_rows}</div>
      <p class="notice">EVIDENCE_PARTIAL means a public source was observed. It does not mean the security, capability or permission surface has been verified.</p>
    </section>

    <section class="section-block">
      <div class="section-title">
        <div><p class="eyebrow">TRACEABLE</p><h2>Evidence records</h2></div>
        <a href="../../evidence/{slug}.json">Raw JSON</a>
      </div>
      <ol class="evidence-list">{evidence_rows}</ol>
    </section>

    <section class="section-block split">
      <article class="panel">
        <p class="panel-label">README BADGE</p>
        <img src="../../badges/{slug}.svg" alt="AUN evidence partial badge">
        <pre class="snippet">{html.escape(badge_md)}</pre>
      </article>
      <article class="panel">
        <p class="panel-label">PORTABLE TRUST CARD</p>
        <p>Machine-readable card for registries, CI and future underwriting APIs.</p>
        <a class="button secondary" href="../../trust-cards/{slug}.json">Open Trust Card JSON</a>
      </article>
    </section>

    <section class="profile-actions">
      <a class="button" href="../../compare.html?agents={slug}">Compare this project</a>
      <a class="button secondary" href="../../account.html?watch={claim_param}">Save & watch</a>
      <a class="button secondary" href="../../account.html?claim={claim_param}">Claim this profile</a>
      <a class="button secondary" href="{source}" target="_blank" rel="noreferrer">Open source repository</a>
    </section>
  </main>
  <footer class="shell footer">Evidence is version-specific · No warranty · No pay-to-rank placement.</footer>
  <script src="../../analytics.js"></script>
  <script>if (window.AUNAnalytics) window.AUNAnalytics.track("TRUST_CARD_VIEW", {{agent_id: {json.dumps(card.agent_id)}}});</script>
</body>
</html>
"""


def _write_profile(card: AgentCard, evidence: list[dict[str, Any]]) -> None:
    slug = str(card.metadata["slug"])
    profile_dir = SITE_ROOT / "agents" / slug
    profile_dir.mkdir(parents=True, exist_ok=True)

    card_dict = card.to_dict()
    card_dict["evidence_ids"] = [item["evidence_id"] for item in evidence]
    card_dict["public_url"] = f"{PUBLIC_BASE}/agents/{slug}/"

    (profile_dir / "index.html").write_text(
        _profile_html(card, evidence),
        encoding="utf-8",
    )

    trust_dir = SITE_ROOT / "trust-cards"
    trust_dir.mkdir(parents=True, exist_ok=True)
    (trust_dir / f"{slug}.json").write_text(
        json.dumps(card_dict, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    evidence_dir = SITE_ROOT / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / f"{slug}.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "agent_id": card.agent_id,
                "version": card.version,
                "records": evidence,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    badge_dir = SITE_ROOT / "badges"
    badge_dir.mkdir(parents=True, exist_ok=True)
    (badge_dir / f"{slug}.svg").write_text(
        _badge_svg(card),
        encoding="utf-8",
    )


def _write_sitemap(cards: list[AgentCard]) -> None:
    urls = [
        f"{PUBLIC_BASE}/",
        f"{PUBLIC_BASE}/compare.html",
        f"{PUBLIC_BASE}/account.html",
        f"{PUBLIC_BASE}/privacy.html",
        f"{PUBLIC_BASE}/terms.html",
    ]
    urls.extend(
        f"{PUBLIC_BASE}/agents/{card.metadata['slug']}/"
        for card in cards
    )
    body = "".join(
        f"  <url><loc>{html.escape(url)}</loc></url>\n"
        for url in urls
    )
    (SITE_ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}</urlset>\n",
        encoding="utf-8",
    )
    (SITE_ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_BASE}/sitemap.xml\n",
        encoding="utf-8",
    )


def build_index(
    seeds_path: Path = SEEDS_PATH,
    output_path: Path = OUTPUT_PATH,
) -> list[dict[str, Any]]:
    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))["repositories"]
    token = os.environ.get("GITHUB_TOKEN")
    targets = load_targets()
    cards: list[AgentCard] = []
    failures: list[dict[str, str]] = []

    max_workers = min(10, max(1, len(seeds)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {
            pool.submit(discover_repository, full_name, token): full_name
            for full_name in seeds
        }
        for future in as_completed(future_map):
            full_name = future_map[future]
            try:
                cards.append(future.result())
            except Exception as exc:
                failures.append(
                    {
                        "repository": full_name,
                        "error": type(exc).__name__,
                    }
                )

    cards.sort(
        key=lambda card: (
            int(card.metadata.get("stars") or 0),
            str(card.metadata.get("repository") or "").lower(),
        ),
        reverse=True,
    )

    enriched_cards: list[AgentCard] = []
    for card in cards:
        enrichment = enrich_card(
            card,
            token=token,
            targets=targets,
        )
        enriched_card = enrichment.card
        evidence = _evidence_for(enriched_card) + list(enrichment.records)
        _write_profile(enriched_card, evidence)
        enriched_cards.append(enriched_card)

    cards = enriched_cards

    enriched_count = 0
    scanner_runs = 0
    scanner_successes = 0
    scanner_findings = 0
    for card in cards:
        summary = card.metadata.get("evidence_enrichment") or {}
        if summary:
            enriched_count += 1
        for scanner in summary.get("security_scanners") or []:
            scanner_runs += 1
            if scanner.get("status") == "SUCCESS":
                scanner_successes += 1
            scanner_findings += int(scanner.get("finding_count") or 0)

    print(
        "evidence enrichment: "
        f"profiles={enriched_count} "
        f"scanner_runs={scanner_runs} "
        f"scanner_successes={scanner_successes} "
        f"scanner_findings={scanner_findings}"
    )

    _write_sitemap(cards)

    categories: dict[str, int] = {}
    for card in cards:
        category = str(card.metadata.get("category") or "Other")
        categories[category] = categories.get(category, 0) + 1

    payload = {
        "schema_version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Discovery metadata and public-source evidence only. DISCOVERED does not mean VERIFIED.",
        "profile_count": len(cards),
        "seed_count": len(seeds),
        "categories": dict(sorted(categories.items())),
        "agents": [card.to_dict() for card in cards],
        "failures": sorted(failures, key=lambda item: item["repository"].lower()),
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
    return 0 if len(agents) >= 100 else 2


if __name__ == "__main__":
    sys.exit(main())
