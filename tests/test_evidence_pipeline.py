import unittest

from aun.benchmarks.base import BenchmarkFixture, run_fixture
from aun.evidence_lifecycle import EvidenceReceipt, apply_version_drift
from aun.permissions import extract_permission_signals
from aun.scanners.base import ScannerFinding, aggregate_findings
from aun.scanners.manifests import extract_dependencies


class EvidencePipelineTests(unittest.TestCase):
    def test_version_change_marks_bound_evidence_stale(self):
        receipt = EvidenceReceipt(
            evidence_id="ev1",
            dimension="capability",
            state="VERIFIED",
            artifact_hash="a" * 40,
            observed_at="2026-10-02T00:00:00+00:00",
        )
        updated = apply_version_drift(
            [receipt],
            previous_hash="a" * 40,
            current_hash="b" * 40,
        )
        self.assertEqual(updated[0].state, "STALE")

    def test_dependency_extraction_preserves_ecosystem(self):
        signals = extract_dependencies(
            {
                "requirements.txt": "httpx==0.28.0\npytest>=8\n",
                "package.json": '{"dependencies":{"playwright":"^1.55.0"}}',
            }
        )
        names = {(item.ecosystem, item.name) for item in signals}
        self.assertIn(("python", "httpx"), names)
        self.assertIn(("npm", "playwright"), names)

    def test_permission_extraction_is_only_declared_signal(self):
        signals = extract_permission_signals(
            {"agent.py": "import subprocess\nimport httpx\n"}
        )
        self.assertTrue(signals)
        self.assertTrue(
            all(item.evidence_state == "DECLARED_SIGNAL" for item in signals)
        )

    def test_conflicting_scanner_findings_are_retained(self):
        findings = [
            ScannerFinding(
                "scanner-a", "1", "prompt-injection", "high", "A",
                "x", "abc", "now"
            ),
            ScannerFinding(
                "scanner-b", "2", "prompt-injection", "low", "B",
                "y", "abc", "now"
            ),
        ]
        grouped = aggregate_findings(findings)
        self.assertEqual(len(grouped["prompt-injection"]), 2)

    def test_benchmark_receipt_is_bounded(self):
        fixture = BenchmarkFixture(
            fixture_id="json-001",
            task_type="structured_extraction",
            environment_id="fixture:v1",
            evaluator_version="1.0.0",
        )
        receipt = run_fixture(
            fixture,
            artifact_hash="a" * 64,
            executor=lambda: {"ok": True},
            evaluator=lambda output: (
                output == {"ok": True},
                1.2,
                {"observed": output},
            ),
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.score, 1.0)


if __name__ == "__main__":
    unittest.main()
