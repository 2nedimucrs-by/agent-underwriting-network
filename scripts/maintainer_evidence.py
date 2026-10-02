from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(os.environ.get("AUN_REPOSITORY_ROOT", ".")).resolve()
OUTPUT = ROOT / ".aun" / "evidence-submission.json"

MANIFESTS = (
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
)

MAX_BYTES = 256_000

TERMS = {
    "filesystem": ("pathlib", "readfile", "writefile", "fs."),
    "shell_process": ("subprocess", "child_process", "exec(", "spawn("),
    "browser": ("playwright", "selenium", "puppeteer", "browser"),
    "network": ("requests", "httpx", "fetch(", "urllib", "axios"),
    "git_github": ("github", "gitpython", "octokit"),
    "email": ("smtp", "sendgrid", "mailgun", "resend"),
    "payments": ("stripe", "paypal", "payment"),
    "database": ("postgres", "mysql", "sqlite", "mongodb", "supabase"),
    "containers": ("docker", "kubernetes", "podman"),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    files = []
    signals = []

    for relative in MANIFESTS:
        path = ROOT / relative
        if not path.is_file():
            continue

        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            files.append({
                "path": relative,
                "status": "SKIPPED_TOO_LARGE",
                "size": len(raw),
            })
            continue

        files.append({
            "path": relative,
            "status": "OBSERVED",
            "size": len(raw),
            "sha256": sha256_bytes(raw),
        })

        text = raw.decode("utf-8", errors="ignore").lower()
        for surface, terms in TERMS.items():
            matched = next((term for term in terms if term in text), None)
            if matched:
                signals.append({
                    "surface": surface,
                    "source_path": relative,
                    "matched_term": matched,
                    "state": "DECLARED_SIGNAL",
                })

    payload = {
        "schema_version": "1.0.0",
        "status": "SELF_COLLECTED_NOT_VERIFIED",
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "collector": "aun-maintainer-evidence-action-v1",
        "notice": (
            "This snapshot is maintainer-collected evidence. It is not an "
            "independent verification or safety certification."
        ),
        "manifests": files,
        "declared_permission_signals": signals,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"evidence_path={OUTPUT}\n")

    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as handle:
            handle.write("## Agent Underwriting evidence snapshot\n\n")
            handle.write(
                f"- observed manifests: {len(files)}\n"
                f"- declared permission signals: {len(signals)}\n"
                "- status: SELF_COLLECTED_NOT_VERIFIED\n"
            )

    print(str(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
