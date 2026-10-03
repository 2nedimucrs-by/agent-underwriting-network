import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExternalReceiptTests(unittest.TestCase):
    def test_pydantic_ai_receipt_integrity_and_scope(self):
        path = (
            ROOT
            / "evidence"
            / "external"
            / "pydantic-ai"
            / "structured-extraction-v1.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["evidence_type"],
            "FRAMEWORK_EXECUTION_RECEIPT",
        )
        self.assertEqual(
            payload["target"]["package_version"],
            "2.53.0",
        )
        self.assertFalse(payload["execution"]["allow_model_requests"])
        self.assertTrue(payload["receipt"]["passed"])

        receipt = dict(payload["receipt"])
        recorded = receipt.pop("receipt_sha256")
        canonical = json.dumps(
            receipt,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), recorded)

        limitations = " ".join(payload["limitations"]).lower()
        self.assertIn("not an llm", limitations)
        self.assertIn("not a universal capability", limitations)


if __name__ == "__main__":
    unittest.main()
