import unittest

from aun.policy_underwriting import underwrite_task


VERIFIED = {
    "identity": "VERIFIED",
    "provenance": "VERIFIED",
    "security": "VERIFIED",
    "permissions": "VERIFIED",
    "capability": "VERIFIED",
    "reliability": "VERIFIED",
    "economics": "VERIFIED",
    "freshness": "VERIFIED",
}


class PolicyUnderwritingTests(unittest.TestCase):
    def test_public_partial_evidence_fails_closed(self):
        decision = underwrite_task(
            agent_status="DISCOVERED_NOT_VERIFIED",
            task_type="browser_read",
            evidence_dimensions={
                "identity": "EVIDENCE_PARTIAL",
                "provenance": "EVIDENCE_PARTIAL",
                "security": "EVIDENCE_PARTIAL",
                "permissions": "EVIDENCE_PARTIAL",
                "capability": "NOT_EVALUATED",
                "reliability": "NOT_EVALUATED",
                "freshness": "EVIDENCE_PARTIAL",
            },
            evidence_ids=["ev-1"],
        )
        self.assertEqual(decision.decision, "INSUFFICIENT_EVIDENCE")
        self.assertIn("capability", decision.missing_dimensions)

    def test_read_task_denies_write_access(self):
        decision = underwrite_task(
            agent_status="VERIFIED_FOR_TASK",
            task_type="repository_read",
            evidence_dimensions=VERIFIED,
            evidence_ids=["ev-1"],
            requested_limits={"write_access": True},
        )
        self.assertEqual(decision.decision, "DENY")

    def test_verified_task_allows_with_policy_limits(self):
        decision = underwrite_task(
            agent_status="VERIFIED_FOR_TASK",
            task_type="code_change",
            evidence_dimensions=VERIFIED,
            evidence_ids=["ev-a", "ev-b"],
            requested_limits={
                "write_access": True,
                "max_spend_usd": 3,
            },
        )
        self.assertEqual(decision.decision, "ALLOW")
        self.assertEqual(decision.enforced_limits["max_spend_usd"], 3)

    def test_spend_above_policy_is_limited(self):
        decision = underwrite_task(
            agent_status="VERIFIED_FOR_TASK",
            task_type="code_change",
            evidence_dimensions=VERIFIED,
            evidence_ids=["ev-a"],
            requested_limits={
                "write_access": True,
                "max_spend_usd": 20,
            },
        )
        self.assertEqual(decision.decision, "ALLOW_WITH_LIMITS")
        self.assertEqual(decision.enforced_limits["max_spend_usd"], 5)


if __name__ == "__main__":
    unittest.main()
