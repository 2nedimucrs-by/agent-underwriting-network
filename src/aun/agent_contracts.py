from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VALID_EXTERNAL_POLICIES = {
    "none",
    "read_only",
    "sandbox_only",
    "approval_required",
}


@dataclass(frozen=True)
class WorkerContract:
    worker_id: str
    capabilities: frozenset[str]
    writes: frozenset[str]
    mode: str
    external_action_policy: str

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class AgentRegistry:
    chief_id: str
    workers: tuple[WorkerContract, ...]
    forbidden_autonomous_actions: frozenset[str]

    def worker_for(self, capability: str) -> WorkerContract:
        matches = [worker for worker in self.workers if worker.supports(capability)]
        if len(matches) != 1:
            raise ValueError(
                f"capability {capability!r} must map to exactly one worker; "
                f"found {len(matches)}"
            )
        return matches[0]


def load_registry(path: Path) -> AgentRegistry:
    payload = json.loads(path.read_text(encoding="utf-8"))
    chief_id = payload["chief"]["id"]

    workers = tuple(
        WorkerContract(
            worker_id=item["id"],
            capabilities=frozenset(item["capabilities"]),
            writes=frozenset(item.get("writes", [])),
            mode=item["mode"],
            external_action_policy=item["external_action_policy"],
        )
        for item in payload["workers"]
    )

    ids = [worker.worker_id for worker in workers]
    if len(ids) != len(set(ids)):
        raise ValueError("worker IDs must be unique")

    all_capabilities: list[str] = []
    for worker in workers:
        if worker.external_action_policy not in VALID_EXTERNAL_POLICIES:
            raise ValueError(
                f"invalid external action policy for {worker.worker_id}: "
                f"{worker.external_action_policy}"
            )
        all_capabilities.extend(worker.capabilities)

    duplicates = {
        capability
        for capability in all_capabilities
        if all_capabilities.count(capability) > 1
    }
    if duplicates:
        raise ValueError(
            "capabilities must have one authority: " + ", ".join(sorted(duplicates))
        )

    return AgentRegistry(
        chief_id=chief_id,
        workers=workers,
        forbidden_autonomous_actions=frozenset(
            payload.get("forbidden_autonomous_actions", [])
        ),
    )


def validate_required_capabilities(
    registry: AgentRegistry,
    required: Iterable[str],
) -> None:
    missing = []
    for capability in required:
        try:
            registry.worker_for(capability)
        except ValueError:
            missing.append(capability)
    if missing:
        raise ValueError(
            "required capabilities are not uniquely routable: "
            + ", ".join(sorted(missing))
        )
