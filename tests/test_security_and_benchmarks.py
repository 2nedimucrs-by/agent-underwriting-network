import unittest

from aun.benchmarks.fixtures import (
    run_browser_navigation_read,
    run_mcp_tool_invocation,
    run_read_only_file_lookup,
    run_repository_read_only,
    run_structured_extraction,
)
from aun.benchmarks.base import BenchmarkFixture, run_fixture
from aun.scanners.github_advisory import (
    GitHubAdvisoryDependencyScanner,
    _exact_version as gh_exact_version,
)
from aun.scanners.manifests import DependencySignal
from aun.scanners.osv import (
    OSVDependencyScanner,
    _exact_version as osv_exact_version,
)


class FakeHarness:
    def invoke(self, task_type, payload):
        if task_type == "structured_extraction":
            return {
                "order_id": "A-104",
                "quantity": 3,
                "total": 42.5,
                "currency": "USD",
            }

        if task_type == "read_only_file_lookup":
            return {"answer": "ORBIT", "writes": []}

        if task_type == "repository_read":
            return {
                "answer": "stable",
                "writes": [],
                "network_requests": [],
            }

        if task_type == "browser_read":
            return {
                "heading": "Read-only policy",
                "visited_paths": ["/start", "/policy"],
                "form_submissions": [],
                "downloads": [],
                "external_requests": [],
            }

        if task_type == "mcp_tool_invocation":
            return {
                "tool_calls": [
                    {
                        "name": "lookup_order",
                        "arguments": {"order_id": "A-104"},
                    }
                ],
                "result": {
                    "order_id": "A-104",
                    "status": "ready",
                    "quantity": 3,
                },
            }

        raise AssertionError("unexpected task")


class SecurityAndBenchmarkTests(unittest.TestCase):
    def test_scanners_only_use_exact_python_versions(self):
        exact = DependencySignal(
            "python",
            "httpx",
            "==0.28.0",
            "requirements.txt",
        )
        ranged = DependencySignal(
            "python",
            "httpx",
            ">=0.28",
            "requirements.txt",
        )
        self.assertEqual(osv_exact_version(exact), "0.28.0")
        self.assertIsNone(osv_exact_version(ranged))
        self.assertEqual(gh_exact_version(exact), "0.28.0")
        self.assertIsNone(gh_exact_version(ranged))

    def test_dependency_scanners_expose_common_identity(self):
        osv = OSVDependencyScanner(max_dependencies=5)
        github = GitHubAdvisoryDependencyScanner(
            token=None,
            max_dependencies=5,
        )
        self.assertEqual(osv.scanner_id, "osv-api")
        self.assertEqual(github.scanner_id, "github-global-advisories")
        self.assertTrue(callable(osv.scan))
        self.assertTrue(callable(github.scan))

    def test_structured_extraction_fixture(self):
        receipt = run_structured_extraction(
            FakeHarness(),
            artifact_hash="a" * 64,
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.score, 1.0)
        self.assertGreaterEqual(receipt.latency_ms, 0)
        self.assertIsNone(receipt.cost_usd)

    def test_read_only_fixture_requires_no_writes(self):
        receipt = run_read_only_file_lookup(
            FakeHarness(),
            artifact_hash="a" * 64,
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.details["observed_writes"], [])
        self.assertTrue(receipt.verify_integrity())


    def test_repository_read_only_fixture_forbids_side_effects(self):
        receipt = run_repository_read_only(
            FakeHarness(),
            artifact_hash="b" * 64,
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.details["observed_writes"], [])
        self.assertEqual(receipt.details["observed_network_requests"], [])

    def test_browser_read_fixture_is_navigation_only(self):
        receipt = run_browser_navigation_read(
            FakeHarness(),
            artifact_hash="c" * 64,
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(
            receipt.details["visited_paths"],
            ["/start", "/policy"],
        )
        self.assertEqual(receipt.details["form_submissions"], [])
        self.assertEqual(receipt.details["downloads"], [])
        self.assertEqual(receipt.details["external_requests"], [])

    def test_mcp_fixture_requires_exact_single_tool_call(self):
        receipt = run_mcp_tool_invocation(
            FakeHarness(),
            artifact_hash="d" * 64,
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(
            receipt.details["observed_tool_calls"],
            [
                {
                    "name": "lookup_order",
                    "arguments": {"order_id": "A-104"},
                }
            ],
        )

    def test_receipt_timestamp_digest_and_serialization(self):
        import json

        receipt = run_structured_extraction(
            FakeHarness(),
            artifact_hash="a" * 64,
        )
        self.assertTrue(receipt.recorded_at_utc.endswith("Z"))
        self.assertEqual(len(receipt.receipt_sha256), 64)
        self.assertTrue(receipt.verify_integrity())
        self.assertEqual(
            json.loads(receipt.to_json())["receipt_sha256"],
            receipt.receipt_sha256,
        )

    def test_receipt_detects_mutated_details(self):
        receipt = run_read_only_file_lookup(
            FakeHarness(),
            artifact_hash="a" * 64,
        )
        receipt.details["observed_writes"].append("unexpected")
        self.assertFalse(receipt.verify_integrity())

    def test_receipt_requires_sha256_artifact_identity(self):
        for invalid_hash in ("", "abc", "g" * 64, "a" * 63):
            with self.subTest(artifact_hash=invalid_hash):
                with self.assertRaises(ValueError):
                    run_structured_extraction(
                        FakeHarness(), artifact_hash=invalid_hash
                    )

    def test_receipt_rejects_non_boolean_pass_results(self):
        with self.assertRaises(TypeError):
            run_fixture(
                BenchmarkFixture("fixture", "task", "env", "1"),
                artifact_hash="a" * 64,
                executor=lambda: "output",
                evaluator=lambda output: ("yes", 1.0, {}),
            )

    def test_receipt_rejects_non_finite_metrics(self):
        fixture = BenchmarkFixture("fixture", "task", "env", "1")
        with self.assertRaises(ValueError):
            run_fixture(
                fixture,
                artifact_hash="a" * 64,
                executor=lambda: "output",
                evaluator=lambda output: (True, float("nan"), {}),
            )
        with self.assertRaises(ValueError):
            run_fixture(
                fixture,
                artifact_hash="a" * 64,
                executor=lambda: "output",
                evaluator=lambda output: (True, 1.0, {}),
                cost_usd=-1.0,
            )

if __name__ == "__main__":
    unittest.main()
