from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "infra" / "supabase" / "migrations"


class VersionWatchMigrationContractTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
