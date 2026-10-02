import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SupabaseContractTests(unittest.TestCase):
    def test_initial_sensitive_tables_enable_rls(self):
        sql = (
            ROOT / "infra" / "supabase" / "migrations" / "001_initial.sql"
        ).read_text(encoding="utf-8").lower()

        for table in (
            "profiles",
            "admin_users",
            "agent_claims",
            "saved_agents",
            "agent_alerts",
            "analytics_events",
            "account_deletion_requests",
            "outreach_suppression",
        ):
            self.assertIn(
                f"alter table public.{table} enable row level security",
                sql,
            )

    def test_raw_analytics_are_not_publicly_selectable(self):
        sql = (
            ROOT / "infra" / "supabase" / "migrations" / "001_initial.sql"
        ).read_text(encoding="utf-8").lower()

        self.assertIn(
            "grant insert on table public.analytics_events to anon",
            sql,
        )
        self.assertNotIn(
            "grant select on table public.analytics_events to anon",
            sql,
        )
        self.assertIn("analytics admin select", sql)

    def test_admin_rpc_is_not_granted_to_anon(self):
        sql = (
            ROOT / "infra" / "supabase" / "migrations" / "001_initial.sql"
        ).read_text(encoding="utf-8").lower()

        self.assertIn(
            "revoke all on function public.admin_dashboard_metrics() from public",
            sql,
        )
        self.assertIn(
            "grant execute on function public.admin_dashboard_metrics() to authenticated",
            sql,
        )

    def test_version_watch_notifications_are_user_scoped(self):
        sql = (
            ROOT / "infra" / "supabase" / "migrations" / "003_version_watch.sql"
        ).read_text(encoding="utf-8").lower()

        self.assertIn(
            "alter table public.user_notifications enable row level security",
            sql,
        )
        self.assertIn(
            "using (user_id = auth.uid())",
            sql,
        )
        self.assertNotIn(
            "grant select on table public.user_notifications to anon",
            sql,
        )

    def test_admin_bootstrap_example_contains_no_real_email(self):
        sql = (
            ROOT
            / "infra"
            / "supabase"
            / "migrations"
            / "002_admin_bootstrap.example.sql"
        ).read_text(encoding="utf-8")

        self.assertIn("REPLACE_WITH_AUTH_EMAIL", sql)
        self.assertNotIn("@gmail.com", sql.lower())
        self.assertNotIn("@outlook.com", sql.lower())


if __name__ == "__main__":
    unittest.main()
