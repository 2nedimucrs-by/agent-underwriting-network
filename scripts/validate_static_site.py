from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "site" / "index.html",
    ROOT / "site" / "styles.css",
    ROOT / "site" / "app.js",
    ROOT / "site" / "data" / "agents.json",
]

missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:
    raise SystemExit("missing static-site files: " + ", ".join(missing))

print("static site integrity: PASS")
