from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from .base import ScannerFinding
from .manifests import DependencySignal


OSV_QUERYBATCH_URL = "https://api.osv.dev/v1/querybatch"


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
    if signal.ecosystem == "python":
        if raw.startswith("=="):
            value = raw[2:].strip()
            return value or None
        return None

    if signal.ecosystem == "npm":
        if re.fullmatch(r"[0-9][0-9A-Za-z.+_-]*", raw):
            return raw
        return None

    return None


def _osv_ecosystem(signal: DependencySignal) -> str | None:
    return {"python": "PyPI", "npm": "npm"}.get(signal.ecosystem)


def _severity(vuln: dict) -> str:
    database_specific = vuln.get("database_specific") or {}
    severity = database_specific.get("severity")
    if severity:
        return str(severity).lower()

    severities = vuln.get("severity") or []
    if severities:
        return str(severities[0].get("score") or "unknown").lower()

    return "unknown"


def scan_dependencies(
    dependencies: list[DependencySignal],
    *,
    artifact_hash: str | None,
    max_dependencies: int = 25,
) -> ScannerRun:
    scanner_id = "osv-api"
    scanner_version = "v1-querybatch"

    eligible: list[tuple[DependencySignal, str, str]] = []
    skipped = 0

    for signal in dependencies:
        ecosystem = _osv_ecosystem(signal)
        version = _exact_version(signal)
        if not ecosystem or not version:
            skipped += 1
            continue
        eligible.append((signal, ecosystem, version))
        if len(eligible) >= max_dependencies:
            break

    if not eligible:
        return ScannerRun(
            scanner_id=scanner_id,
            scanner_version=scanner_version,
            status="NOT_APPLICABLE",
            findings=(),
            scanned_dependencies=0,
            skipped_dependencies=skipped,
        )

    payload = {
        "queries": [
            {
                "package": {"name": signal.name, "ecosystem": ecosystem},
                "version": version,
            }
            for signal, ecosystem, version in eligible
        ]
    }

    request = urllib.request.Request(
        OSV_QUERYBATCH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "agent-underwriting-network/0.4",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except Exception as exc:
        return ScannerRun(
            scanner_id=scanner_id,
            scanner_version=scanner_version,
            status="ERROR",
            findings=(),
            scanned_dependencies=len(eligible),
            skipped_dependencies=skipped,
            error=type(exc).__name__,
        )

    observed = datetime.now(timezone.utc).isoformat()
    findings: list[ScannerFinding] = []
    rows = result.get("results") or []

    for index, row in enumerate(rows):
        if index >= len(eligible):
            break
        signal, _ecosystem, version = eligible[index]
        for vuln in row.get("vulns") or []:
            vuln_id = str(vuln.get("id") or "UNKNOWN")
            findings.append(
                ScannerFinding(
                    scanner_id=scanner_id,
                    scanner_version=scanner_version,
                    check_id=vuln_id,
                    severity=_severity(vuln),
                    title=f"{signal.name} {version}: {vuln_id}",
                    source_locator=f"https://osv.dev/vulnerability/{vuln_id}",
                    artifact_hash=artifact_hash,
                    observed_at=observed,
                    raw_result=json.dumps(
                        {
                            "package": signal.name,
                            "version": version,
                            "aliases": vuln.get("aliases") or [],
                            "summary": vuln.get("summary"),
                        },
                        sort_keys=True,
                    ),
                )
            )

    return ScannerRun(
        scanner_id=scanner_id,
        scanner_version=scanner_version,
        status="SUCCESS",
        findings=tuple(findings),
        scanned_dependencies=len(eligible),
        skipped_dependencies=skipped,
    )
