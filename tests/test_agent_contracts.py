import unittest
from pathlib import Path

from aun.agent_contracts import load_registry, validate_required_capabilities
from aun.chief import WorkItem, route_work


ROOT = Path(__file__).resolve().parents[1]


class AgentContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry(ROOT / "config" / "agents.json")

    def test_required_capabilities_are_uniquely_routable(self):
        validate_required_capabilities(
            self.registry,
            (
                "discover.github",
                "version.compare",
                "permission.extract",
                "security.scan.normalize",
                "benchmark.run",
                "evidence.compile",
                "outreach.draft",
            ),
        )

    def test_forbidden_external_action_requires_human_approval(self):
        routed = route_work(
            self.registry,
            WorkItem(
                work_id="w1",
                capability="outreach.draft",
                payload={},
                external_action="bulk_email_send",
                human_approved=False,
            ),
        )
        self.assertEqual(
            routed.decision,
            "BLOCKED_PENDING_HUMAN_APPROVAL",
        )

    def test_read_only_worker_cannot_perform_external_write(self):
        routed = route_work(
            self.registry,
            WorkItem(
                work_id="w2",
                capability="discover.github",
                payload={},
                external_action="production_write",
            ),
        )
        self.assertEqual(routed.decision, "BLOCKED_BY_WORKER_POLICY")


if __name__ == "__main__":
    unittest.main()
