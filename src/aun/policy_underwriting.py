from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICIES_PATH = ROOT / "config" / "task_policies.json"


@dataclass(frozen=True)
class TaskPolicy:
    task_type: str
    required_dimensions: tuple[str, ...]
    allows_write: bool
    max_spend_usd: float


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    enforced_limits: dict[str, Any]
    missing_dimensions: tuple[str, ...] = ()


def load_task_policies(
    path: Path = DEFAULT_POLICIES_PATH,
) -> dict[str, TaskPolicy]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, TaskPolicy] = {}

    for task_type, raw in (payload.get("policies") or {}).items():
        result[task_type] = TaskPolicy(
            task_type=task_type,
            required_dimensions=tuple(raw["required_dimensions"]),
            allows_write=bool(raw["allows_write"]),
            max_spend_usd=float(raw["max_spend_usd"]),
        )

    return result


def underwrite_task(
    *,
    agent_status: str,
    task_type: str,
    evidence_dimensions: dict[str, str],
    evidence_ids: list[str] | tuple[str, ...],
    requested_limits: dict[str, Any] | None = None,
    policies: dict[str, TaskPolicy] | None = None,
) -> PolicyDecision:
    policies = policies or load_task_policies()
    requested_limits = requested_limits or {}

    if agent_status == "BLOCKED":
        return PolicyDecision(
            decision="DENY",
            reasons=("agent status is BLOCKED",),
            evidence_ids=tuple(evidence_ids),
            enforced_limits={},
        )

    policy = policies.get(task_type)
    if policy is None:
        return PolicyDecision(
            decision="REVIEW_REQUIRED",
            reasons=(f"no underwriting policy exists for task {task_type!r}",),
            evidence_ids=tuple(evidence_ids),
            enforced_limits={},
        )

    requested_write = bool(requested_limits.get("write_access", False))
    requested_spend = float(requested_limits.get("max_spend_usd", 0) or 0)

    if requested_write and not policy.allows_write:
        return PolicyDecision(
            decision="DENY",
            reasons=(
                f"task policy {task_type!r} forbids write access",
            ),
            evidence_ids=tuple(evidence_ids),
            enforced_limits={
                "write_access": False,
                "max_spend_usd": policy.max_spend_usd,
            },
        )

    missing = tuple(
        dimension
        for dimension in policy.required_dimensions
        if evidence_dimensions.get(dimension) != "VERIFIED"
    )

    enforced_limits = {
        "write_access": requested_write and policy.allows_write,
        "max_spend_usd": min(
            requested_spend,
            policy.max_spend_usd,
        ),
    }

    if missing:
        return PolicyDecision(
            decision="INSUFFICIENT_EVIDENCE",
            reasons=(
                "required VERIFIED evidence is missing for: "
                + ", ".join(missing),
            ),
            evidence_ids=tuple(evidence_ids),
            enforced_limits=enforced_limits,
            missing_dimensions=missing,
        )

    if agent_status != "VERIFIED_FOR_TASK":
        return PolicyDecision(
            decision="REVIEW_REQUIRED",
            reasons=(
                "all policy dimensions are VERIFIED but the agent is not "
                "VERIFIED_FOR_TASK for this task",
            ),
            evidence_ids=tuple(evidence_ids),
            enforced_limits=enforced_limits,
        )

    if requested_spend > policy.max_spend_usd:
        return PolicyDecision(
            decision="ALLOW_WITH_LIMITS",
            reasons=(
                "task evidence is sufficient but requested spend exceeds "
                "the policy maximum",
            ),
            evidence_ids=tuple(evidence_ids),
            enforced_limits=enforced_limits,
        )

    return PolicyDecision(
        decision="ALLOW",
        reasons=("task-specific evidence and requested limits satisfy policy",),
        evidence_ids=tuple(evidence_ids),
        enforced_limits=enforced_limits,
    )
