from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

patterns = {
    "private key": re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"),
    "GitHub classic token": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "OpenAI project key": re.compile(r"sk-proj-[A-Za-z0-9_-]{16,}"),
    "Supabase service role marker": re.compile(r"SUPABASE_SERVICE_ROLE_KEY\s*[:=]\s*['\"][^'\"]+"),
}

violations = []

for path in SITE.rglob("*"):
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for name, pattern in patterns.items():
        if pattern.search(text):
            violations.append(f"{path.relative_to(ROOT)}: {name}")

if violations:
    raise SystemExit(
        "secret-like material found in public site output:\n"
        + "\n".join(violations)
    )

print("public-site secret scan: PASS")
