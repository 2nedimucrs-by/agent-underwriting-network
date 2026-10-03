import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PydanticAIFileLookupReceiptTests(unittest.TestCase):
    def test_receipt_is_persisted_with_bounded_framework_scope(self):
        path = ROOT / "evidence" / "external" / "pydantic-ai" / "read-only-file-lookup-v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        receipt = payload["receipt"]
        execution = payload["execution"]

        self.assertEqual(payload["schema_version"], "1.0.0")
        self.assertEqual(payload["evidence_type"], "FRAMEWORK_EXECUTION_RECEIPT")
        self.assertEqual(payload["target"]["package_version"], "2.53.0")
        self.assertEqual(
            payload["artifact"]["sha256"],
            "979fb5553cc32baf9f3aaeff7a83c19d6ce6d19c0284f5cd54087bc9870b2522",
        )
        self.assertEqual(execution["aun_commit"], "b1ea6db12a1f1a42398f4b34f76aadc3fb5e88d9")
        self.assertEqual(execution["observed_tool_calls"], ["read_project_readme"])
        self.assertTrue(execution["fixture_content_returned"])
        self.assertEqual(execution["filesystem_writes"], 0)
        self.assertIs(execution["allow_model_requests"], False)
        self.assertEqual(execution["model_adapter"], "pydantic_ai.models.test.TestModel")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["details"]["expected_answer"], "ORBIT")
        self.assertEqual(receipt["details"]["observed_answer"], "ORBIT")
        self.assertEqual(receipt["details"]["observed_writes"], [])
        self.assertEqual(len(receipt["receipt_sha256"]), 64)
        self.assertTrue(any("not an LLM" in item for item in payload["limitations"]))
        self.assertTrue(any("in memory" in item for item in payload["limitations"]))


if __name__ == "__main__":
    unittest.main()
