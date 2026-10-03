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

    def test_underwriting_rate_limit_is_serialized_and_backend_only(self):
        sql = (
            ROOT
            / "infra"
            / "supabase"
            / "migrations"
            / "012_underwriting_rate_limit_atomic.sql"
        ).read_text(encoding="utf-8").lower()

        self.assertIn("set search_path = ''", sql)
        self.assertIn("pg_catalog.pg_advisory_xact_lock", sql)
        self.assertLess(
            sql.index("pg_catalog.pg_advisory_xact_lock"),
            sql.index("from public.underwriting_rate_events"),
        )
        self.assertLess(
            sql.index("from public.underwriting_rate_events"),
            sql.index("insert into public.underwriting_rate_events"),
        )
        self.assertIn(
            "revoke all on function public.consume_underwriting_rate_limit(uuid, text, text)",
            sql,
        )
        self.assertIn(
            "from public, anon, authenticated",
            sql,
        )
        self.assertIn(
            "grant execute on function public.consume_underwriting_rate_limit(uuid, text, text)",
            sql,
        )
        self.assertIn("to service_role", sql)

    def test_can_hire_fails_closed_through_atomic_rate_limit_rpc(self):
        source = (
            ROOT
            / "infra"
            / "supabase"
            / "functions"
            / "can-hire"
            / "index.ts"
        ).read_text(encoding="utf-8")

        self.assertIn(
            '"consume_underwriting_rate_limit"',
            source,
        )
        self.assertIn("if (rateLimitError)", source)
        self.assertIn(
            'typeof rateLimit.allowed !== "boolean"',
            source,
        )
        self.assertIn("if (rateLimit.allowed === false)", source)
        self.assertNotIn(
            '.from("underwriting_rate_events")',
            source,
        )


if __name__ == "__main__":
    unittest.main()
