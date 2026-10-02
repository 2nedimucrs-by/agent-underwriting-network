import unittest

from aun.benchmarks.fixtures import (
    run_read_only_file_lookup,
    run_structured_extraction,
)
from aun.scanners.github_advisory import _exact_version as gh_exact_version
from aun.scanners.manifests import DependencySignal
from aun.scanners.osv import _exact_version as osv_exact_version


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

    def test_structured_extraction_fixture(self):
        receipt = run_structured_extraction(
            FakeHarness(),
            artifact_hash="abc",
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.score, 1.0)

    def test_read_only_fixture_requires_no_writes(self):
        receipt = run_read_only_file_lookup(
            FakeHarness(),
            artifact_hash="abc",
        )
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.details["observed_writes"], [])


if __name__ == "__main__":
    unittest.main()
