from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from time import perf_counter
from typing import Any, Callable


@dataclass(frozen=True)
class BenchmarkFixture:
    fixture_id: str
    task_type: str
    environment_id: str
    evaluator_version: str


@dataclass(frozen=True)
class BenchmarkReceipt:
    fixture_id: str
    task_type: str
    environment_id: str
    evaluator_version: str
    artifact_hash: str
    passed: bool
    score: float
    latency_ms: float
    cost_usd: float | None
    recorded_at_utc: str
    details: dict[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible snapshot of this receipt."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize the receipt canonically for storage or export."""
        return _canonical_json(self.to_dict())

    def verify_integrity(self) -> bool:
        """Check that the payload still matches its recorded digest."""
        payload = self.to_dict()
        recorded_digest = payload.pop("receipt_sha256")
        return recorded_digest == _receipt_digest(payload)


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _receipt_digest(payload: dict[str, Any]) -> str:
    encoded = _canonical_json(payload).encode("utf-8")
    return sha256(encoded).hexdigest()


def run_fixture(
    fixture: BenchmarkFixture,
    *,
    artifact_hash: str,
    executor: Callable[[], Any],
    evaluator: Callable[[Any], tuple[bool, float, dict[str, Any]]],
    cost_usd: float | None = None,
) -> BenchmarkReceipt:
    """Run one bounded fixture and produce a timestamped, verifiable receipt."""

    for field_name in ("fixture_id", "task_type", "environment_id", "evaluator_version"):
        value = getattr(fixture, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")

    if not isinstance(artifact_hash, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", artifact_hash.strip()
    ):
        raise ValueError("artifact_hash must be a 64-character SHA-256 hex digest")

    if cost_usd is not None:
        if isinstance(cost_usd, bool) or not isinstance(cost_usd, (int, float)):
            raise TypeError("cost_usd must be a non-negative finite number or None")
        if not math.isfinite(float(cost_usd)) or cost_usd < 0:
            raise ValueError("cost_usd must be a non-negative finite number or None")

    started = perf_counter()
    output = executor()
    latency_ms = (perf_counter() - started) * 1000.0
    passed, score, details = evaluator(output)

    if not isinstance(passed, bool):
        raise TypeError("evaluator passed result must be a bool")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise TypeError("evaluator score must be a finite number")
    score = float(score)
    if not math.isfinite(score):
        raise ValueError("evaluator score must be a finite number")
    if not isinstance(details, dict):
        raise TypeError("evaluator details must be a JSON object")

    # Snapshot JSON data so later mutation cannot silently change an exported receipt.
    details_snapshot = json.loads(
        json.dumps(details, ensure_ascii=False, allow_nan=False)
    )
    normalized_score = max(0.0, min(1.0, score))
    recorded_at_utc = datetime.now(timezone.utc).isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")

    payload = {
        "fixture_id": fixture.fixture_id,
        "task_type": fixture.task_type,
        "environment_id": fixture.environment_id,
        "evaluator_version": fixture.evaluator_version,
        "artifact_hash": artifact_hash.strip().lower(),
        "passed": passed,
        "score": normalized_score,
        "latency_ms": latency_ms,
        "cost_usd": float(cost_usd) if cost_usd is not None else None,
        "recorded_at_utc": recorded_at_utc,
        "details": details_snapshot,
    }
    digest = _receipt_digest(payload)
    return BenchmarkReceipt(**payload, receipt_sha256=digest)
