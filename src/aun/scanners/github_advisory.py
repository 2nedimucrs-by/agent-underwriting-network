from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from .base import ScannerFinding
from .manifests import DependencySignal


GITHUB_ADVISORIES_URL = "https://api.github.com/advisories"


@dataclass(frozen=True)
class ScannerRun:
    scanner_id: str
    scanner_version: str
    status: str
    findings: tuple[ScannerFinding, ...]
    scanned_dependencies: int
    skipped_dependencies: int
    error: str | None = None


def _exact_version(signal: DependencySignal) -> str | None:
    raw = (signal.declared_version or "").strip()
    if signal.ecosystem == "python" and raw.startswith("=="):
        return raw[2:].strip() or None
    if signal.ecosystem == "npm" and re.fullmatch(
        r"[0-9][0-9A-Za-z.+_-]*",
        raw,
    ):
        return raw
    return None


def _github_ecosystem(signal: DependencySignal) -> str | None:
    return {"python": "pip", "npm": "npm"}.get(signal.ecosystem)


def scan_dependencies(
    dependencies: list[DependencySignal],
    *,
    artifact_hash: str | None,
    token: str | None,
    max_dependencies: int = 15,
) -> ScannerRun:
    scanner_id = "github-global-advisories"
    scanner_version = "rest-2022-11-28"

    findings: list[ScannerFinding] = []
    scanned = 0
    skipped = 0
    observed = datetime.now(timezone.utc).isoformat()

    for signal in dependencies:
        ecosystem = _github_ecosystem(signal)
        version = _exact_version(signal)

        if not ecosystem or not version:
            skipped += 1
            continue

        if scanned >= max_dependencies:
            break

        scanned += 1
        query = urllib.parse.urlencode(
            {
                "ecosystem": ecosystem,
                "affects": f"{signal.name}@{version}",
                "per_page": "100",
            }
        )
        request = urllib.request.Request(
            GITHUB_ADVISORIES_URL + "?" + query,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "agent-underwriting-network/0.4",
                "X-GitHub-Api-Version": "2022-11-28",
                **({"Authorization": "Bearer " + token} if token else {}),
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                advisories = json.load(response)
        except Exception as exc:
            return ScannerRun(
                scanner_id=scanner_id,
                scanner_version=scanner_version,
                status="ERROR",
                findings=tuple(findings),
                scanned_dependencies=scanned,
                skipped_dependencies=skipped,
                error=type(exc).__name__,
            )

        for advisory in advisories or []:
            ghsa_id = str(advisory.get("ghsa_id") or "UNKNOWN")
            findings.append(
                ScannerFinding(
                    scanner_id=scanner_id,
                    scanner_version=scanner_version,
                    check_id=ghsa_id,
                    severity=str(advisory.get("severity") or "unknown").lower(),
                    title=(
                        advisory.get("summary")
                        or f"{signal.name} {version}: {ghsa_id}"
                    ),
                    source_locator=(
                        advisory.get("html_url")
                        or f"https://github.com/advisories/{ghsa_id}"
                    ),
                    artifact_hash=artifact_hash,
                    observed_at=observed,
                    raw_result=json.dumps(
                        {
                            "package": signal.name,
                            "version": version,
                            "cve_id": advisory.get("cve_id"),
                            "ghsa_id": ghsa_id,
                        },
                        sort_keys=True,
                    ),
                )
            )

    status = "SUCCESS" if scanned else "NOT_APPLICABLE"
    return ScannerRun(
        scanner_id=scanner_id,
        scanner_version=scanner_version,
        status=status,
        findings=tuple(findings),
        scanned_dependencies=scanned,
        skipped_dependencies=skipped,
    )
