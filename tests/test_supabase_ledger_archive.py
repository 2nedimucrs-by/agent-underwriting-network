from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "migration_sources", ROOT / "scripts" / "validate_supabase_migration_sources.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SupabaseLedgerArchiveTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(AUDIT.SNAPSHOT.read_text(encoding="utf-8"))

    def test_archive_and_restored_sources_match_but_baseline_remains_unproven(self):
        result = AUDIT.validate_snapshot(self.snapshot)
        self.assertEqual(result["CAPTURED_LEDGER_ROWS"], 16)
        self.assertEqual(result["RESTORED_EXACT_SQL_SOURCES"], 4)
        self.assertEqual(result["MIGRATION_SOURCE_RECONCILED"], "NO")

    def test_missing_history_is_rejected(self):
        self.snapshot["rows"].pop()
        with self.assertRaisesRegex(ValueError, "16 distinct"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_duplicate_versions_are_rejected(self):
        self.snapshot["rows"][1]["version"] = self.snapshot["rows"][0]["version"]
        with self.assertRaisesRegex(ValueError, "16 distinct"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_changed_archived_sql_is_rejected(self):
        self.snapshot["rows"][0]["statements"][0] += "\nselect 1;"
        with self.assertRaisesRegex(ValueError, "statements changed"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_duplicate_sql_difference_is_not_hidden_by_updated_hash(self):
        row = self.snapshot["rows"][2]
        row["statements"][0] = row["statements"][0].replace("user_id = auth.uid()", "true")
        row["statements_sha256"] = AUDIT.statements_hash(row["statements"])
        with self.assertRaisesRegex(ValueError, "beyond leading comments"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_source_mismatch_is_rejected(self):
        row = next(row for row in self.snapshot["rows"] if "exact_source" in row)
        row["statements"][0] += "\nselect 1;"
        row["statements_sha256"] = AUDIT.statements_hash(row["statements"])
        with self.assertRaisesRegex(ValueError, "source differs"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_source_cannot_escape_migrations(self):
        row = next(row for row in self.snapshot["rows"] if "exact_source" in row)
        row["exact_source"] = "../../README.md"
        with self.assertRaisesRegex(ValueError, "stay in migrations"):
            AUDIT.validate_snapshot(self.snapshot)

    def test_comparison_preserves_sql_literal_content(self):
        self.assertNotEqual(
            AUDIT.without_leading_comments("select '--a  b';"),
            AUDIT.without_leading_comments("select '--a b';"),
        )

    def test_hash_preserves_statement_boundaries(self):
        self.assertNotEqual(AUDIT.statements_hash(["a", "b"]), AUDIT.statements_hash(["a\nb"]))


if __name__ == "__main__":
    unittest.main()
