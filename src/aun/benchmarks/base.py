from __future__ import annotations

from dataclasses import dataclass
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
    artifact_hash: str | None
    passed: bool
    score: float
    details: dict[str, Any]


def run_fixture(
    fixture: BenchmarkFixture,
    *,
    artifact_hash: str | None,
    executor: Callable[[], Any],
    evaluator: Callable[[Any], tuple[bool, float, dict[str, Any]]],
) -> BenchmarkReceipt:
    """Run one bounded fixture and produce a reproducible receipt."""

    output = executor()
    passed, score, details = evaluator(output)
    score = max(0.0, min(1.0, float(score)))

    return BenchmarkReceipt(
        fixture_id=fixture.fixture_id,
        task_type=fixture.task_type,
        environment_id=fixture.environment_id,
        evaluator_version=fixture.evaluator_version,
        artifact_hash=artifact_hash,
        passed=bool(passed),
        score=score,
        details=details,
    )
