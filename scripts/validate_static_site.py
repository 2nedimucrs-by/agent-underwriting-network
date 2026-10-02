import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

required = [
    SITE / "index.html",
    SITE / "styles.css",
    SITE / "app.js",
    SITE / "compare.html",
    SITE / "compare.js",
    SITE / "underwrite.html",
    SITE / "underwrite.js",
    SITE / "account.html",
    SITE / "account.js",
    SITE / "admin.html",
    SITE / "admin.js",
    SITE / "privacy.html",
    SITE / "terms.html",
    SITE / "runtime-config.js",
    SITE / "analytics.js",
    SITE / "data" / "agents.json",
]

missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:
    raise SystemExit("missing static-site files: " + ", ".join(missing))

payload = json.loads((SITE / "data" / "agents.json").read_text(encoding="utf-8"))
agents = payload.get("agents") or []

# CI validates the checked-in bootstrap shell. Pages validates the generated
# corpus after discovery has populated agents.json.
if agents:
    if len(agents) < 100:
        raise SystemExit(f"generated public index has only {len(agents)} profiles; expected >=100")

    profile_dirs = [path for path in (SITE / "agents").glob("*/index.html")]
    trust_cards = list((SITE / "trust-cards").glob("*.json"))
    evidence_files = list((SITE / "evidence").glob("*.json"))
    badges = list((SITE / "badges").glob("*.svg"))

    expected = len(agents)
    counts = {
        "profile_pages": len(profile_dirs),
        "trust_cards": len(trust_cards),
        "evidence_files": len(evidence_files),
        "badges": len(badges),
    }
    short = {name: value for name, value in counts.items() if value < expected}
    if short:
        raise SystemExit(f"generated evidence surfaces incomplete: expected {expected}, got {short}")

    for extra in ("sitemap.xml", "robots.txt"):
        if not (SITE / extra).exists():
            raise SystemExit(f"missing generated SEO surface: {extra}")

    degraded_mode = bool(payload.get("degraded_mode"))

    targets_path = ROOT / "config" / "evidence_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    manifest_targets = {
        value.lower()
        for value in targets.get("manifest_targets", [])
    }

    enriched = [
        agent
        for agent in agents
        if str(agent.get("metadata", {}).get("repository", "")).lower()
        in manifest_targets
        and agent.get("metadata", {}).get("evidence_enrichment")
    ]

    if degraded_mode:
        fallback_marked = [
            agent
            for agent in agents
            if agent.get("metadata", {}).get("discovery_fallback") is True
        ]
        if len(fallback_marked) < 100:
            raise SystemExit(
                "degraded discovery cache lacks required fallback markers"
            )
        print(
            "evidence surface: DEGRADED_FAIL_CLOSED "
            f"(profiles={len(fallback_marked)} fresh_enriched={len(enriched)})"
        )
    else:
        minimum_enriched = min(4, len(manifest_targets))
        if len(enriched) < minimum_enriched:
            raise SystemExit(
                "bounded evidence enrichment below minimum: "
                f"{len(enriched)} < {minimum_enriched}"
            )

        scanner_profiles = [
            agent
            for agent in enriched
            if (
                agent.get("metadata", {})
                .get("evidence_enrichment", {})
                .get("security_scanners")
            )
        ]
        if not scanner_profiles:
            raise SystemExit(
                "security scanner adapters produced no recorded run metadata"
            )

        print(
            "evidence surface: PASS "
            f"(enriched={len(enriched)} scanner_profiles={len(scanner_profiles)})"
        )

print(f"static site integrity: PASS ({len(agents)} generated profiles)")
