from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone


@dataclass(frozen=True)
class EvidenceReceipt:
    evidence_id: str
    dimension: str
    state: str
    artifact_hash: str | None
    observed_at: str
    reusable_across_versions: bool = False
    stale_reason: str | None = None


def apply_version_drift(
    receipts: list[EvidenceReceipt],
    *,
    previous_hash: str | None,
    current_hash: str | None,
) -> list[EvidenceReceipt]:
    """Mark version-bound evidence stale when the artifact changes."""

    if not previous_hash or not current_hash or previous_hash == current_hash:
        return receipts

    updated: list[EvidenceReceipt] = []
    for receipt in receipts:
        if receipt.reusable_across_versions:
            updated.append(receipt)
            continue

        if receipt.artifact_hash and receipt.artifact_hash != current_hash:
            updated.append(
                replace(
                    receipt,
                    state="STALE",
                    stale_reason=(
                        f"artifact changed from {previous_hash[:12]} "
                        f"to {current_hash[:12]}"
                    ),
                )
            )
        else:
            updated.append(receipt)

    return updated


def observed_now() -> str:
    return datetime.now(timezone.utc).isoformat()
