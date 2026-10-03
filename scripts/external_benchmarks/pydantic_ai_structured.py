from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
from pathlib import Path

from aun.benchmarks.fixtures import run_structured_extraction


class PydanticAIHarness:
    """Execute the AUN fixture through a real PydanticAI Agent runtime.

    The model is PydanticAI's documented procedural TestModel. This verifies
    framework execution and output plumbing only; it does not measure LLM
    reasoning quality.
    """

    def invoke(self, task_type: str, payload: dict) -> dict:
        if task_type != "structured_extraction":
            raise ValueError(f"unsupported task_type: {task_type}")

        from pydantic_ai import Agent, models
        from pydantic_ai.models.test import TestModel

        models.ALLOW_MODEL_REQUESTS = False

        canned = json.dumps(
            {
                "order_id": "A-104",
                "quantity": 3,
                "total": 42.5,
                "currency": "USD",
            },
            separators=(",", ":"),
            sort_keys=True,
        )

        agent = Agent(TestModel(custom_output_text=canned))
        result = agent.run_sync(
            "Extract the required fields from: " + str(payload["text"])
        )

        output = result.output
        if not isinstance(output, str):
            raise TypeError("PydanticAI TestModel returned non-text output")

        parsed = json.loads(output)
        if not isinstance(parsed, dict):
            raise TypeError("PydanticAI output did not decode to an object")
        return parsed


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

    receipt = run_structured_extraction(
        PydanticAIHarness(),
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
        },
        "scope": (
            "PydanticAI framework execution and deterministic output plumbing "
            "for the AUN structured-extraction fixture."
        ),
        "limitations": [
            (
                "PydanticAI TestModel is procedural test code, not an LLM; "
                "this receipt does not demonstrate model reasoning quality."
            ),
            (
                "The receipt supports only this exact package artifact and "
                "fixture; it is not a universal capability or safety claim."
            ),
            (
                "PyPI wheel identity is recorded by SHA-256; source-release "
                "equivalence is referenced by release tag, not independently proven."
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
