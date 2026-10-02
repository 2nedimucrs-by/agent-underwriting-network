from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ScannerFinding:
    scanner_id: str
    scanner_version: str
    check_id: str
    severity: str
    title: str
    source_locator: str
    artifact_hash: str | None
    observed_at: str
    raw_result: str | None = None


class ScannerAdapter(Protocol):
    scanner_id: str
    scanner_version: str

    def scan(self, target: str, artifact_hash: str | None) -> list[ScannerFinding]:
        ...


def aggregate_findings(
    findings: list[ScannerFinding],
) -> dict[str, list[ScannerFinding]]:
    """Preserve conflicting scanner evidence instead of averaging it away."""

    grouped: dict[str, list[ScannerFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.check_id, []).append(finding)
    return grouped
