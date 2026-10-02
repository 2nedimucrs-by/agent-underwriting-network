import unittest

from aun.underwriting import decide_task_fitness


class UnderwritingTests(unittest.TestCase):
    def test_missing_evidence_fails_closed(self):
        decision = decide_task_fitness(
            agent_status="DISCOVERED_NOT_VERIFIED",
            task_type="crm_write",
            required_dimensions=("security", "permissions", "capability"),
            evidence_dimensions={
                "security": "VERIFIED",
                "permissions": "NOT_EVALUATED",
                "capability": "VERIFIED",
            },
        )
        self.assertEqual(decision.decision, "INSUFFICIENT_EVIDENCE")

    def test_blocked_agent_is_denied(self):
        decision = decide_task_fitness(
            agent_status="BLOCKED",
            task_type="browser_read",
            required_dimensions=("security",),
            evidence_dimensions={"security": "VERIFIED"},
        )
        self.assertEqual(decision.decision, "DENY")

    def test_verified_task_can_allow(self):
        decision = decide_task_fitness(
            agent_status="VERIFIED_FOR_TASK",
            task_type="browser_read",
            required_dimensions=("security", "permissions", "capability"),
            evidence_dimensions={
                "security": "VERIFIED",
                "permissions": "VERIFIED",
                "capability": "VERIFIED",
            },
        )
        self.assertEqual(decision.decision, "ALLOW")


if __name__ == "__main__":
    unittest.main()
