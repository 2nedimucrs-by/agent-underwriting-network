"""Validate the captured ledger archive without connecting to or changing a database."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPABASE = ROOT / "infra" / "supabase"
SNAPSHOT = SUPABASE / "migration-ledger-snapshot.json"


def statements_hash(statements: list[str]) -> str:
    return hashlib.sha256(
        json.dumps(statements, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def without_leading_comments(sql: str) -> str:
    # Remove only initial full-line comments. Preserve literals, bodies, and all
    # interior whitespace; this is deliberately not a SQL equivalence parser.
    return re.sub(r"\A(?:\s*--[^\n]*(?:\n|$))*", "", sql.replace("\r\n", "\n")).strip()


def validate_snapshot(snapshot: dict, source_root: Path = SUPABASE) -> dict:
    rows = snapshot["rows"]
    if len(rows) != 16 or len({row["version"] for row in rows}) != len(rows):
        raise ValueError("Expected all 16 distinct captured ledger versions")
    exact_sources = 0
    for row in rows:
        statements = row["statements"]
        if not statements or any(not isinstance(s, str) or not s.strip() for s in statements):
            raise ValueError("Missing SQL statements")
        if statements_hash(statements) != row["statements_sha256"]:
            raise ValueError("Captured ledger statements changed: " + row["version"])
        if "exact_source" in row:
            path = (source_root / row["exact_source"]).resolve()
            if not path.is_relative_to((source_root / "migrations").resolve()):
                raise ValueError("Source path must stay in migrations")
            # Ignore only platform line endings and boundary whitespace.
            if path.read_text(encoding="utf-8").strip() != "\n".join(statements).strip():
                raise ValueError("Historical SQL source differs from ledger: " + row["version"])
            exact_sources += 1
    if exact_sources != 4:
        raise ValueError("Expected four restored exact historical sources")
    by_version = {row["version"]: row for row in rows}
    first = by_version["20261002223225"]
    second = by_version["20261002223438"]
    if first["name"] != second["name"] or first["name"] != "version_watch_and_notifications":
        raise ValueError("Unexpected duplicate migration identity")
    if without_leading_comments("\n".join(first["statements"])) != without_leading_comments("\n".join(second["statements"])):
        raise ValueError("Duplicate ledger SQL differs beyond leading comments")
    if any(row["name"] == "initial" for row in rows):
        raise ValueError("Baseline evidence changed; re-audit reconciliation status")
    return {
        "CAPTURED_LEDGER_ROWS": len(rows),
        "RESTORED_EXACT_SQL_SOURCES": exact_sources,
        "DUPLICATE_VERSION_WATCH": "SAME_SQL_EXCEPT_LEADING_COMMENTS",
        "INITIAL_BASELINE_PROVENANCE": "UNPROVEN",
        "MIGRATION_SOURCE_RECONCILED": "NO",
    }


if __name__ == "__main__":
    result = validate_snapshot(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    for name, value in result.items():
        print(f"{name}={value}")
