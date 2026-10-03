import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SupabaseFunctionContractTests(unittest.TestCase):
    def test_claim_verifier_preserves_identity_boundary(self):
        source = (
            ROOT
            / "infra"
            / "supabase"
            / "functions"
            / "verify-github-claim"
            / "index.ts"
        ).read_text(encoding="utf-8")

        self.assertIn("github_oauth_login_equals_repository_owner", source)
        self.assertIn("public_repository_challenge_file", source)
        self.assertIn("CHALLENGE_ISSUED", source)
        self.assertIn("CHALLENGE_VERIFIED", source)
        self.assertIn('status: "VERIFIED_MAINTAINER"', source)
        self.assertNotIn('status: "VERIFIED_FOR_TASK"', source)

    def test_claim_challenge_is_expiring_and_repository_bound(self):
        source = (
            ROOT
            / "infra"
            / "supabase"
            / "functions"
            / "verify-github-claim"
            / "index.ts"
        ).read_text(encoding="utf-8")

        self.assertIn("CHALLENGE_TTL_MS", source)
        self.assertIn(".github/agent-underwriting-claim.json", source)
        self.assertIn("proof.claim_id === claim.id", source)
        self.assertIn("proof.challenge === challengeToken", source)


if __name__ == "__main__":
    unittest.main()
