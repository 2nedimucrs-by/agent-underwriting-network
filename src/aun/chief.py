from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_contracts import AgentRegistry, WorkerContract


@dataclass(frozen=True)
class WorkItem:
    work_id: str
    capability: str
    payload: dict[str, Any]
    external_action: str | None = None
    human_approved: bool = False


@dataclass(frozen=True)
class RoutedWork:
    work: WorkItem
    worker: WorkerContract
    decision: str
    reason: str


def route_work(registry: AgentRegistry, work: WorkItem) -> RoutedWork:
    worker = registry.worker_for(work.capability)

    if work.external_action in registry.forbidden_autonomous_actions:
        if not work.human_approved:
            return RoutedWork(
                work=work,
                worker=worker,
                decision="BLOCKED_PENDING_HUMAN_APPROVAL",
                reason=f"external action {work.external_action!r} is forbidden autonomously",
            )

    if worker.external_action_policy == "approval_required":
        if work.external_action and not work.human_approved:
            return RoutedWork(
                work=work,
                worker=worker,
                decision="BLOCKED_PENDING_HUMAN_APPROVAL",
                reason="worker contract requires approval for external action",
            )

    if worker.external_action_policy == "read_only" and work.external_action:
        return RoutedWork(
            work=work,
            worker=worker,
            decision="BLOCKED_BY_WORKER_POLICY",
            reason="worker is read-only",
        )

    return RoutedWork(
        work=work,
        worker=worker,
        decision="ROUTED",
        reason="capability authority and action policy satisfied",
    )
