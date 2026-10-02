from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PermissionSignal:
    surface: str
    source_path: str
    matched_term: str
    evidence_state: str = "DECLARED_SIGNAL"


TERMS: dict[str, tuple[str, ...]] = {
    "filesystem": ("filesystem", "readfile", "writefile", "pathlib", "fs."),
    "shell_process": ("subprocess", "child_process", "exec(", "spawn(", "shell"),
    "browser": ("playwright", "selenium", "puppeteer", "browser"),
    "network": ("requests", "httpx", "fetch(", "urllib", "axios", "websocket"),
    "git_github": ("github", "gitpython", "octokit"),
    "email": ("smtp", "sendgrid", "mailgun", "resend"),
    "payments": ("stripe", "paypal", "payment"),
    "database": ("postgres", "mysql", "sqlite", "mongodb", "supabase"),
    "containers": ("docker", "kubernetes", "podman"),
}


def extract_permission_signals(
    files: Mapping[str, str],
) -> list[PermissionSignal]:
    signals: list[PermissionSignal] = []

    for path, content in files.items():
        haystack = content.lower()
        for surface, terms in TERMS.items():
            for term in terms:
                if term in haystack:
                    signals.append(
                        PermissionSignal(
                            surface=surface,
                            source_path=path,
                            matched_term=term,
                        )
                    )
                    break

    unique: dict[tuple[str, str], PermissionSignal] = {}
    for signal in signals:
        unique[(signal.surface, signal.source_path)] = signal
    return sorted(
        unique.values(),
        key=lambda item: (item.surface, item.source_path),
    )
