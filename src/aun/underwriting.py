from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class UnderwritingDecision:
    decision: str
    reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()


def decide_task_fitness(
    *,
    agent_status: str,
    task_type: str,
    required_dimensions: Iterable[str],
    evidence_dimensions: dict[str, str],
) -> UnderwritingDecision:
    """Fail closed unless task-relevant evidence is current and explicit."""

    if agent_status == "BLOCKED":
        return UnderwritingDecision("DENY", ("agent status is BLOCKED",))

    missing = [
        name
        for name in required_dimensions
        if evidence_dimensions.get(name) != "VERIFIED"
    ]
    if missing:
        joined = ", ".join(missing)
        return UnderwritingDecision(
            "INSUFFICIENT_EVIDENCE",
            (f"task {task_type!r} lacks VERIFIED evidence for: {joined}",),
        )

    if agent_status != "VERIFIED_FOR_TASK":
        return UnderwritingDecision(
            "REVIEW_REQUIRED",
            ("task-specific verification status is not VERIFIED_FOR_TASK",),
        )

    return UnderwritingDecision(
        "ALLOW",
        ("all required task dimensions are VERIFIED",),
    )
