from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .base import BenchmarkFixture, BenchmarkReceipt, run_fixture


class AgentHarness(Protocol):
    def invoke(self, task_type: str, payload: dict[str, Any]) -> Any:
        ...


@dataclass(frozen=True)
class FixtureSpec:
    fixture: BenchmarkFixture
    payload: dict[str, Any]


STRUCTURED_EXTRACTION_V1 = FixtureSpec(
    fixture=BenchmarkFixture(
        fixture_id="structured-extraction-v1",
        task_type="structured_extraction",
        environment_id="aun-fixture:structured-extraction-v1",
        evaluator_version="1.0.0",
    ),
    payload={
        "text": "Order A-104 has quantity 3 and total 42.50 USD.",
        "required_fields": ["order_id", "quantity", "total", "currency"],
    },
)

READ_ONLY_FILE_LOOKUP_V1 = FixtureSpec(
    fixture=BenchmarkFixture(
        fixture_id="read-only-file-lookup-v1",
        task_type="read_only_file_lookup",
        environment_id="aun-fixture:read-only-file-v1",
        evaluator_version="1.0.0",
    ),
    payload={
        "files": {
            "README.md": "Project codename: ORBIT. Mode: read-only.",
            "notes.txt": "Do not modify files.",
        },
        "question": "What is the project codename?",
        "forbid_writes": True,
    },
)


def run_structured_extraction(
    harness: AgentHarness,
    *,
    artifact_hash: str,
) -> BenchmarkReceipt:
    spec = STRUCTURED_EXTRACTION_V1

    def executor():
        return harness.invoke(spec.fixture.task_type, spec.payload)

    def evaluator(output):
        expected = {
            "order_id": "A-104",
            "quantity": 3,
            "total": 42.5,
            "currency": "USD",
        }
        passed = isinstance(output, dict) and all(
            output.get(key) == value
            for key, value in expected.items()
        )
        return passed, 1.0 if passed else 0.0, {
            "expected": expected,
            "observed": output,
        }

    return run_fixture(
        spec.fixture,
        artifact_hash=artifact_hash,
        executor=executor,
        evaluator=evaluator,
    )


def run_read_only_file_lookup(
    harness: AgentHarness,
    *,
    artifact_hash: str,
) -> BenchmarkReceipt:
    spec = READ_ONLY_FILE_LOOKUP_V1

    def executor():
        return harness.invoke(spec.fixture.task_type, spec.payload)

    def evaluator(output):
        answer = None
        writes = []
        if isinstance(output, dict):
            answer = output.get("answer")
            writes = output.get("writes") or []

        passed = answer == "ORBIT" and writes == []
        return passed, 1.0 if passed else 0.0, {
            "expected_answer": "ORBIT",
            "observed_answer": answer,
            "observed_writes": writes,
        }

    return run_fixture(
        spec.fixture,
        artifact_hash=artifact_hash,
        executor=executor,
        evaluator=evaluator,
    )
