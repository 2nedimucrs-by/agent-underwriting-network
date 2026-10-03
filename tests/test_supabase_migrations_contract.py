from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "infra" / "supabase" / "migrations"


class SupabaseMigrationContractTests(unittest.TestCase):
    def test_scheduler_extensions_are_enabled_idempotently_in_live_schemas(self):
        source = (
            MIGRATIONS
            / "20261002224150_enable_version_watch_scheduler_extensions.sql"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "create extension if not exists pg_cron with schema pg_catalog;",
            source.lower(),
        )
        self.assertIn(
            "create extension if not exists pg_net with schema extensions;",
            source.lower(),
        )
        self.assertIn(
            "create extension if not exists supabase_vault with schema vault;",
            source.lower(),
        )

    def test_version_watch_schedule_is_vault_backed_and_reproducible(self):
        source = (
            MIGRATIONS
            / "20261002224159_schedule_version_watch.sql"
        ).read_text(encoding="utf-8")

        self.assertLess(
            source.index("cron.unschedule"),
            source.index("cron.schedule("),
        )
        self.assertIn("'aun-version-watch'", source)
        self.assertIn("'43 */6 * * *'", source)
        self.assertIn(
            "https://sfplbbnratiznbipniez.supabase.co/functions/v1/version-watch",
            source,
        )
        self.assertRegex(
            source,
            re.compile(
                r"'x-aun-cron-token'\s*,\s*\(\s*select decrypted_secret"
                r"\s+from vault\.decrypted_secrets\s+where name = "
                r"'aun_version_watch_token'",
                re.IGNORECASE | re.DOTALL,
            ),
        )
        self.assertNotIn("Authorization", source)
        self.assertNotRegex(source, r"(?i)sb_secret_[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]{10,}")
        self.assertNotRegex(source, r"'x-aun-cron-token'\s*,\s*'[^']{24,}'")

    def test_claim_audit_actor_index_matches_live_object(self):
        source = (
            MIGRATIONS
            / "20261002230020_claim_audit_actor_index.sql"
        ).read_text(encoding="utf-8")

        self.assertIn("create index if not exists claim_audit_events_actor_user_idx", source.lower())
        self.assertIn("on public.claim_audit_events(actor_user_id)", source.lower())

    def test_rate_event_visibility_is_admin_only(self):
        source = (
            MIGRATIONS
            / "20261002230030_underwriting_rate_admin_visibility.sql"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "grant select on table public.underwriting_rate_events to authenticated;",
            source.lower(),
        )
        self.assertIn('drop policy if exists "underwriting rate admin select"', source.lower())
        self.assertIn("for select", source.lower())
        self.assertIn("to authenticated", source.lower())
        self.assertIn("using ((select public.is_aun_admin()))", source.lower())

    def test_readme_preserves_live_ledger_dependency_order(self):
        readme = (ROOT / "infra" / "supabase" / "README.md").read_text(
            encoding="utf-8"
        )
        ordered_paths = [
            "migrations/006_rls_initplan_and_fk_indexes.sql",
            "migrations/20261002224150_enable_version_watch_scheduler_extensions.sql",
            "migrations/20261002224159_schedule_version_watch.sql",
            "migrations/007_claim_challenge_and_audit.sql",
            "migrations/011_underwriting_rate_limits.sql",
            "migrations/20261002230020_claim_audit_actor_index.sql",
            "migrations/20261002230030_underwriting_rate_admin_visibility.sql",
            "migrations/012_advisor_cleanup.sql",
            "migrations/013_privacy_retention_cron.sql",
            "migrations/014_underwriting_rate_limit_atomic.sql",
        ]

        positions = [readme.index(path) for path in ordered_paths]
        self.assertEqual(positions, sorted(positions))


    def test_readme_keeps_unresolved_live_migration_history_explicit(self):
        readme = (ROOT / "infra" / "supabase" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("RECONCILIATION_INCOMPLETE", readme)
        self.assertIn("20261002223225", readme)
        self.assertIn("Two rows are named version_watch_and_notifications", readme)
        self.assertIn("must not be counted as an applied migration", readme)
        self.assertIn("Do not replay production history.", readme)

    def test_readme_warns_against_replaying_historical_sources_on_live_project(self):
        readme = (ROOT / "infra" / "supabase" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Fresh-project bootstrap only", readme)
        self.assertIn(
            "Do not replay it against the existing production project.", readme
        )
        self.assertIn(
            "Any future production DDL requires a separately reviewed deployment plan",
            readme,
        )


if __name__ == "__main__":
    unittest.main()
