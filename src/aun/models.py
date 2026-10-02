from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceDimensions:
    identity: str = "NOT_EVALUATED"
    provenance: str = "NOT_EVALUATED"
    security: str = "NOT_EVALUATED"
    permissions: str = "NOT_EVALUATED"
    capability: str = "NOT_EVALUATED"
    reliability: str = "NOT_EVALUATED"
    economics: str = "NOT_EVALUATED"
    freshness: str = "NOT_EVALUATED"


@dataclass(frozen=True)
class AgentCard:
    agent_id: str
    source: dict[str, Any]
    version: dict[str, Any]
    status: str = "DISCOVERED_NOT_VERIFIED"
    evidence_dimensions: EvidenceDimensions = field(default_factory=EvidenceDimensions)
    schema_version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
