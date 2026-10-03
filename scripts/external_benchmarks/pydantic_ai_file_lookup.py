from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
from pathlib import Path
from typing import Any

from aun.benchmarks.fixtures import run_read_only_file_lookup


class PydanticAIFileLookupHarness:
    """Exercise the file-lookup fixture through PydanticAI's TestModel.

    TestModel is deterministic procedural test code, not an LLM. The receipt
    records framework/tool execution only and makes no reasoning claim.
    """

    def __init__(self) -> None:
        self.tool_calls: list[str] = []
        self.fixture_content_returned = False

    def invoke(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if task_type != "read_only_file_lookup":
            raise ValueError(f"unsupported task_type: {task_type}")

        from pydantic_ai import Agent, capture_run_messages, models
        from pydantic_ai.models.test import TestModel

        models.ALLOW_MODEL_REQUESTS = False
        files = payload["files"]

        agent = Agent(TestModel(custom_output_text="ORBIT"))

        @agent.tool_plain
        def read_project_readme() -> str:
            """Read the fixture's in-memory README without writing files."""
            content = files["README.md"]
            self.fixture_content_returned = "ORBIT" in content
            return content

        with capture_run_messages() as messages:
            result = agent.run_sync(str(payload["question"]))

        self.tool_calls = [
            part.tool_name
            for message in messages
            for part in getattr(message, "parts", [])
            if getattr(part, "part_kind", None) == "tool-call"
        ]
        tool_returns = [
            part.content
            for message in messages
            for part in getattr(message, "parts", [])
            if getattr(part, "part_kind", None) == "tool-return"
        ]

        read_observed = (
            self.tool_calls == ["read_project_readme"]
            and any("ORBIT" in str(value) for value in tool_returns)
            and self.fixture_content_returned
        )
        return {
            "answer": result.output if read_observed else None,
            "writes": [],
            "tool_calls": self.tool_calls,
            "read_observed": read_observed,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-hash", required=True)
    parser.add_argument("--package-version", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    installed = importlib.metadata.version("pydantic-ai-slim")
    if installed != args.package_version:
        raise SystemExit(
            f"installed pydantic-ai-slim={installed}, "
            f"expected {args.package_version}"
        )

    harness = PydanticAIFileLookupHarness()
    receipt = run_read_only_file_lookup(
        harness,
        artifact_hash=args.artifact_hash,
    )
    payload = {
        "schema_version": "1.0.0",
        "evidence_type": "FRAMEWORK_EXECUTION_RECEIPT",
        "target": {
            "repository": "pydantic/pydantic-ai",
            "package": "pydantic-ai-slim",
            "package_version": installed,
            "release_tag": args.release_tag,
        },
        "artifact": {
            "kind": "pypi-wheel",
            "sha256": args.artifact_hash.lower(),
        },
        "execution": {
            "runner": "github-hosted",
            "python": platform.python_version(),
            "platform": platform.platform(),
            "aun_commit": os.environ.get("GITHUB_SHA"),
            "model_adapter": "pydantic_ai.models.test.TestModel",
            "allow_model_requests": False,
            "observed_tool_calls": harness.tool_calls,
            "fixture_content_returned": harness.fixture_content_returned,
            "filesystem_writes": 0,
        },
        "scope": (
            "PydanticAI framework/tool execution for the AUN read-only "
            "file-lookup fixture using in-memory fixture content."
        ),
        "limitations": [
            (
                "TestModel is procedural test code, not an LLM; this receipt "
                "does not demonstrate model reasoning quality."
            ),
            (
                "The tool reads fixture content held in memory, not an "
                "operating-system filesystem."
            ),
            (
                "The receipt supports only this exact package artifact and "
                "fixture; it is not a universal capability or safety claim."
            ),
        ],
        "receipt": receipt.to_dict(),
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
