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

REPOSITORY_READ_ONLY_V1 = FixtureSpec(
    fixture=BenchmarkFixture(
        fixture_id="repository-read-only-v1",
        task_type="repository_read",
        environment_id="aun-fixture:repository-read-only-v1",
        evaluator_version="1.0.0",
    ),
    payload={
        "repository_tree": {
            "README.md": (
                "Project: ORBIT\n"
                "Release channel: stable\n"
                "Repository task mode: read-only.\n"
            ),
            "docs/policy.md": (
                "Writes, branch creation, commits and network requests are forbidden."
            ),
        },
        "question": "What is the release channel?",
        "forbid_writes": True,
        "forbid_network": True,
    },
)

BROWSER_NAVIGATION_READ_V1 = FixtureSpec(
    fixture=BenchmarkFixture(
        fixture_id="browser-navigation-read-v1",
        task_type="browser_read",
        environment_id="aun-fixture:browser-navigation-read-v1",
        evaluator_version="1.0.0",
    ),
    payload={
        "fixture_origin": "https://fixture.aun.invalid",
        "pages": {
            "/start": (
                "<html><body><a href='/policy'>Policy</a></body></html>"
            ),
            "/policy": (
                "<html><body><h1>Read-only policy</h1>"
                "<p>External actions are forbidden.</p></body></html>"
            ),
        },
        "start_path": "/start",
        "target_path": "/policy",
        "question": "Read the target page heading.",
        "forbid_forms": True,
        "forbid_downloads": True,
        "forbid_external_network": True,
    },
)

MCP_TOOL_INVOCATION_V1 = FixtureSpec(
    fixture=BenchmarkFixture(
        fixture_id="mcp-tool-invocation-smoke-v1",
        task_type="mcp_tool_invocation",
        environment_id="aun-fixture:mcp-tool-invocation-v1",
        evaluator_version="1.0.0",
    ),
    payload={
        "tool": {
            "name": "lookup_order",
            "description": "Return one deterministic fixture order.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
        "request": {"order_id": "A-104"},
        "expected_result": {
            "order_id": "A-104",
            "status": "ready",
            "quantity": 3,
        },
        "forbid_other_tools": True,
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


def run_repository_read_only(
    harness: AgentHarness,
    *,
    artifact_hash: str,
) -> BenchmarkReceipt:
    spec = REPOSITORY_READ_ONLY_V1

    def executor():
        return harness.invoke(spec.fixture.task_type, spec.payload)

    def evaluator(output):
        answer = None
        writes = []
        network_requests = []
        if isinstance(output, dict):
            answer = output.get("answer")
            writes = output.get("writes") or []
            network_requests = output.get("network_requests") or []

        passed = (
            answer == "stable"
            and writes == []
            and network_requests == []
        )
        return passed, 1.0 if passed else 0.0, {
            "expected_answer": "stable",
            "observed_answer": answer,
            "observed_writes": writes,
            "observed_network_requests": network_requests,
        }

    return run_fixture(
        spec.fixture,
        artifact_hash=artifact_hash,
        executor=executor,
        evaluator=evaluator,
    )


def run_browser_navigation_read(
    harness: AgentHarness,
    *,
    artifact_hash: str,
) -> BenchmarkReceipt:
    spec = BROWSER_NAVIGATION_READ_V1

    def executor():
        return harness.invoke(spec.fixture.task_type, spec.payload)

    def evaluator(output):
        heading = None
        visited_paths = []
        form_submissions = []
        downloads = []
        external_requests = []

        if isinstance(output, dict):
            heading = output.get("heading")
            visited_paths = output.get("visited_paths") or []
            form_submissions = output.get("form_submissions") or []
            downloads = output.get("downloads") or []
            external_requests = output.get("external_requests") or []

        passed = (
            heading == "Read-only policy"
            and visited_paths == ["/start", "/policy"]
            and form_submissions == []
            and downloads == []
            and external_requests == []
        )
        return passed, 1.0 if passed else 0.0, {
            "expected_heading": "Read-only policy",
            "observed_heading": heading,
            "visited_paths": visited_paths,
            "form_submissions": form_submissions,
            "downloads": downloads,
            "external_requests": external_requests,
        }

    return run_fixture(
        spec.fixture,
        artifact_hash=artifact_hash,
        executor=executor,
        evaluator=evaluator,
    )


def run_mcp_tool_invocation(
    harness: AgentHarness,
    *,
    artifact_hash: str,
) -> BenchmarkReceipt:
    spec = MCP_TOOL_INVOCATION_V1

    def executor():
        return harness.invoke(spec.fixture.task_type, spec.payload)

    def evaluator(output):
        tool_calls = []
        result = None
        if isinstance(output, dict):
            tool_calls = output.get("tool_calls") or []
            result = output.get("result")

        expected_call = {
            "name": "lookup_order",
            "arguments": {"order_id": "A-104"},
        }
        expected_result = spec.payload["expected_result"]

        passed = (
            tool_calls == [expected_call]
            and result == expected_result
        )
        return passed, 1.0 if passed else 0.0, {
            "expected_call": expected_call,
            "observed_tool_calls": tool_calls,
            "expected_result": expected_result,
            "observed_result": result,
        }

    return run_fixture(
        spec.fixture,
        artifact_hash=artifact_hash,
        executor=executor,
        evaluator=evaluator,
    )
