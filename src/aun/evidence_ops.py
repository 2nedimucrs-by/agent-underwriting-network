from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AgentCard
from .permissions import extract_permission_signals
from .repo_acquisition import acquire_manifest_files
from .scanners.github_advisory import scan_dependencies as scan_github_advisories
from .scanners.manifests import DependencySignal, extract_dependencies
from .scanners.osv import scan_dependencies as scan_osv


ROOT = Path(__file__).resolve().parents[2]
TARGETS_PATH = ROOT / "config" / "evidence_targets.json"


@dataclass(frozen=True)
class EvidenceTargets:
    manifest_targets: frozenset[str]
    security_targets: frozenset[str]
    max_security_dependencies: int


@dataclass(frozen=True)
class EnrichmentResult:
    card: AgentCard
    records: tuple[dict[str, Any], ...]


def load_targets(path: Path = TARGETS_PATH) -> EvidenceTargets:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return EvidenceTargets(
        manifest_targets=frozenset(
            item.lower() for item in payload.get("manifest_targets", [])
        ),
        security_targets=frozenset(
            item.lower() for item in payload.get("security_targets", [])
        ),
        max_security_dependencies=max(
            1,
            min(int(payload.get("max_security_dependencies", 25)), 50),
        ),
    )


def _evidence_id(card: AgentCard, suffix: str) -> str:
    basis = (
        f"{card.agent_id}:{card.version.get('identifier')}:{suffix}"
    ).encode("utf-8")
    return "ev-" + hashlib.sha256(basis).hexdigest()[:16]


def _manifest_record(
    card: AgentCard,
    acquired: dict,
    dependencies: list[DependencySignal],
) -> dict[str, Any]:
    observed = datetime.now(timezone.utc).isoformat()
    ecosystems: dict[str, int] = {}
    for dependency in dependencies:
        ecosystems[dependency.ecosystem] = (
            ecosystems.get(dependency.ecosystem, 0) + 1
        )

    return {
        "schema_version": "1.0.0",
        "evidence_id": _evidence_id(card, "manifest-inventory"),
        "agent_id": card.agent_id,
        "dimension": "provenance",
        "claim": (
            "A bounded dependency/manifest inventory was observed at the "
            "version-pinned repository head."
        ),
        "result": "EVIDENCE_PARTIAL",
        "source": {
            "kind": "github-version-pinned-manifests",
            "locator": card.source["url"],
        },
        "observed_at": observed,
        "expires_at": None,
        "artifact_hash": card.version.get("commit_sha"),
        "environment": {
            "collector": "aun-bounded-manifest-acquisition-v1",
            "manifest_count": len(acquired),
            "dependency_count": len(dependencies),
            "ecosystem_counts": ecosystems,
            "manifests": [
                {
                    "path": item.path,
                    "blob_sha": item.blob_sha,
                    "source_url": item.source_url,
                }
                for item in acquired.values()
            ],
            "dependencies": [
                {
                    "ecosystem": item.ecosystem,
                    "name": item.name,
                    "declared_version": item.declared_version,
                    "source_path": item.source_path,
                }
                for item in dependencies[:200]
            ],
        },
    }


def _permission_record(card: AgentCard, signals: list) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "evidence_id": _evidence_id(card, "declared-permission-signals"),
        "agent_id": card.agent_id,
        "dimension": "permissions",
        "claim": (
            "Declared permission/tool-surface signals were observed in bounded "
            "manifest files. These are lexical signals, not runtime permission verification."
        ),
        "result": "EVIDENCE_PARTIAL",
        "source": {
            "kind": "manifest-static-signal-extraction",
            "locator": card.source["url"],
        },
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None,
        "artifact_hash": card.version.get("commit_sha"),
        "environment": {
            "extractor": "aun-permission-signals-v1",
            "signals": [
                {
                    "surface": item.surface,
                    "source_path": item.source_path,
                    "matched_term": item.matched_term,
                    "state": item.evidence_state,
                }
                for item in signals
            ],
        },
    }


def _scanner_record(card: AgentCard, run) -> dict[str, Any]:
    result = (
        "EVIDENCE_PARTIAL"
        if run.status == "SUCCESS"
        else "NOT_EVALUATED"
    )
    return {
        "schema_version": "1.0.0",
        "evidence_id": _evidence_id(
            card,
            f"scanner-{run.scanner_id}-{run.scanner_version}",
        ),
        "agent_id": card.agent_id,
        "dimension": "security",
        "claim": (
            f"{run.scanner_id} dependency advisory scan completed."
            if run.status == "SUCCESS"
            else f"{run.scanner_id} scan did not complete: {run.status}."
        ),
        "result": result,
        "source": {
            "kind": "security-scanner",
            "locator": run.scanner_id,
        },
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None,
        "artifact_hash": card.version.get("commit_sha"),
        "environment": {
            "scanner_id": run.scanner_id,
            "scanner_version": run.scanner_version,
            "status": run.status,
            "scanned_dependencies": run.scanned_dependencies,
            "skipped_dependencies": run.skipped_dependencies,
            "error": run.error,
            "finding_count": len(run.findings),
            "findings": [
                {
                    "check_id": finding.check_id,
                    "severity": finding.severity,
                    "title": finding.title,
                    "source_locator": finding.source_locator,
                    "observed_at": finding.observed_at,
                    "raw_result": finding.raw_result,
                }
                for finding in run.findings[:100]
            ],
        },
    }


def enrich_card(
    card: AgentCard,
    *,
    token: str | None,
    targets: EvidenceTargets,
) -> EnrichmentResult:
    repository = str(card.metadata.get("repository") or "")
    repository_key = repository.lower()

    if repository_key not in targets.manifest_targets:
        return EnrichmentResult(card=card, records=())

    commit_sha = card.version.get("commit_sha")
    if not commit_sha:
        return EnrichmentResult(card=card, records=())

    try:
        acquired = acquire_manifest_files(
            repository,
            commit_sha,
            token=token,
        )
    except Exception as exc:
        error_record = {
            "schema_version": "1.0.0",
            "evidence_id": _evidence_id(card, "manifest-acquisition-error"),
            "agent_id": card.agent_id,
            "dimension": "provenance",
            "claim": "Bounded manifest acquisition did not complete.",
            "result": "NOT_EVALUATED",
            "source": {
                "kind": "github-version-pinned-manifests",
                "locator": card.source["url"],
            },
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
            "artifact_hash": commit_sha,
            "environment": {
                "collector": "aun-bounded-manifest-acquisition-v1",
                "status": "ERROR",
                "error": type(exc).__name__,
            },
        }
        return EnrichmentResult(card=card, records=(error_record,))

    if not acquired:
        return EnrichmentResult(card=card, records=())

    contents = {
        path: item.content
        for path, item in acquired.items()
    }
    dependencies = extract_dependencies(contents)
    permission_signals = extract_permission_signals(contents)

    records: list[dict[str, Any]] = [
        _manifest_record(card, acquired, dependencies)
    ]

    dimensions = card.evidence_dimensions
    permissions_state = dimensions.permissions
    security_state = dimensions.security

    if permission_signals:
        records.append(
            _permission_record(card, permission_signals)
        )
        permissions_state = "EVIDENCE_PARTIAL"

    scanner_summary: list[dict[str, Any]] = []
    if repository_key in targets.security_targets and dependencies:
        scanner_runs = [
            scan_osv(
                dependencies,
                artifact_hash=commit_sha,
                max_dependencies=targets.max_security_dependencies,
            ),
            scan_github_advisories(
                dependencies,
                artifact_hash=commit_sha,
                token=token,
                max_dependencies=min(
                    targets.max_security_dependencies,
                    15,
                ),
            ),
        ]

        successful = False
        for run in scanner_runs:
            records.append(_scanner_record(card, run))
            scanner_summary.append(
                {
                    "scanner_id": run.scanner_id,
                    "scanner_version": run.scanner_version,
                    "status": run.status,
                    "finding_count": len(run.findings),
                }
            )
            if run.status == "SUCCESS":
                successful = True

        if successful:
            security_state = "EVIDENCE_PARTIAL"

    enriched_dimensions = replace(
        dimensions,
        provenance="EVIDENCE_PARTIAL",
        permissions=permissions_state,
        security=security_state,
    )

    metadata = dict(card.metadata)
    metadata["evidence_enrichment"] = {
        "manifest_count": len(acquired),
        "dependency_count": len(dependencies),
        "permission_signal_count": len(permission_signals),
        "security_scanners": scanner_summary,
    }

    return EnrichmentResult(
        card=replace(
            card,
            evidence_dimensions=enriched_dimensions,
            metadata=metadata,
        ),
        records=tuple(records),
    )
