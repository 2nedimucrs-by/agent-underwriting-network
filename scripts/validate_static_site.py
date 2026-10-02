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

print(f"static site integrity: PASS ({len(agents)} generated profiles)")
