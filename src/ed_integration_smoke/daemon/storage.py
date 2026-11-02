"""Embedded SQLite storage engine with WAL mode for the telemetry audit daemon."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ed_integration_smoke.daemon.models import (
    CoverageRecord,
    DomainMismatchRecord,
    TargetDefinition,
)


class TelemetryStorageEngine:
    """Thread-safe SQLite storage engine for raw telemetry, coverage, and mismatches."""

    def __init__(
        self,
        db_path: Path | str,
        mismatches_path: Path | str | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.mismatches_path = (
            Path(mismatches_path)
            if mismatches_path is not None
            else self.db_path.parent / "domain_mismatches.jsonl"
        )
        self.mismatches_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS raw_journal_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    received_at TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_raw_events_name ON raw_journal_events(event_name);

                CREATE TABLE IF NOT EXISTS target_coverage (
                    target_id TEXT PRIMARY KEY,
                    target_type TEXT NOT NULL,
                    chapter TEXT NOT NULL,
                    description TEXT,
                    hit_count INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TEXT,
                    last_seen_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_coverage_chapter ON target_coverage(chapter);

                CREATE TABLE IF NOT EXISTS domain_mismatches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    error_class TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    traceback TEXT NOT NULL,
                    raw_payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_mismatches_target ON domain_mismatches(target_id);
                """
            )

    def seed_targets(self, targets: Sequence[TargetDefinition]) -> None:
        """Seed target registry without overriding existing hit counts."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO target_coverage (
                    target_id, target_type, chapter, description, hit_count
                )
                VALUES (?, ?, ?, ?, 0)
                ON CONFLICT(target_id) DO UPDATE SET
                    target_type = excluded.target_type,
                    chapter = excluded.chapter,
                    description = excluded.description;
                """,
                [(t.target_id, t.target_type.value, t.chapter, t.description) for t in targets],
            )

    def record_raw_event(self, event_name: str, payload: dict[str, Any]) -> int:
        """Persist raw event payload."""
        now = datetime.now(UTC).isoformat()
        payload_str = json.dumps(payload, default=str)
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO raw_journal_events (received_at, event_name, payload_json)
                VALUES (?, ?, ?)
                """,
                (now, event_name, payload_str),
            )
            return int(cursor.lastrowid or 0)

    def record_target_hit(self, target_id: str) -> None:
        """Increment hit count and update timestamps for target."""
        now = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE target_coverage
                SET hit_count = hit_count + 1,
                    first_seen_at = COALESCE(first_seen_at, ?),
                    last_seen_at = ?
                WHERE target_id = ?;
                """,
                (now, now, target_id),
            )

    def record_mismatch(self, mismatch: DomainMismatchRecord) -> int:
        """Record domain hydration failure or unhandled event to SQLite and JSONL."""
        now = mismatch.occurred_at or datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO domain_mismatches (
                    occurred_at, target_id, error_class, error_message, traceback, raw_payload
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    now,
                    mismatch.target_id,
                    mismatch.error_class,
                    mismatch.error_message,
                    mismatch.traceback,
                    mismatch.raw_payload,
                ),
            )
            row_id = int(cursor.lastrowid or 0)

        # Append to human-readable JSONL ledger
        try:
            try:
                parsed_payload = json.loads(mismatch.raw_payload)
            except json.JSONDecodeError:
                parsed_payload = mismatch.raw_payload

            jsonl_entry = {
                "id": row_id,
                "occurred_at": now,
                "target_id": mismatch.target_id,
                "error_class": mismatch.error_class,
                "error_message": mismatch.error_message,
                "payload": parsed_payload,
                "traceback": mismatch.traceback,
            }
            with open(self.mismatches_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(jsonl_entry, default=str) + "\n")
        except OSError:
            pass

        return row_id

    def get_coverage_summary(self) -> dict[str, Any]:
        """Calculate overall and per-chapter target coverage metrics."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    chapter,
                    COUNT(*) as total_targets,
                    SUM(CASE WHEN hit_count > 0 THEN 1 ELSE 0 END) as achieved_targets
                FROM target_coverage
                GROUP BY chapter;
                """
            )
            by_chapter = {
                row["chapter"]: {
                    "total": row["total_targets"],
                    "achieved": row["achieved_targets"],
                    "percentage": round((row["achieved_targets"] / row["total_targets"]) * 100, 2)
                    if row["total_targets"] > 0
                    else 0.0,
                }
                for row in cursor.fetchall()
            }

            cursor_total = conn.execute(
                """
                SELECT
                    COUNT(*) as total_targets,
                    SUM(CASE WHEN hit_count > 0 THEN 1 ELSE 0 END) as achieved_targets,
                    SUM(hit_count) as total_hits
                FROM target_coverage;
                """
            )
            row_total = cursor_total.fetchone()
            total = row_total["total_targets"] or 0
            achieved = row_total["achieved_targets"] or 0
            hits = row_total["total_hits"] or 0

            return {
                "total_targets": total,
                "achieved_targets": achieved,
                "total_hits": hits,
                "percentage": round((achieved / total) * 100, 2) if total > 0 else 0.0,
                "by_chapter": by_chapter,
            }

    def list_unachieved_targets(self, chapter: str | None = None) -> list[CoverageRecord]:
        """Return list of targets not yet encountered."""
        query = """
            SELECT
                target_id, target_type, chapter, description,
                hit_count, first_seen_at, last_seen_at
            FROM target_coverage
            WHERE hit_count = 0
        """
        params: list[Any] = []
        if chapter:
            query += " AND chapter = ?"
            params.append(chapter)
        query += " ORDER BY chapter, target_id"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [
                CoverageRecord(
                    target_id=row["target_id"],
                    target_type=row["target_type"],
                    chapter=row["chapter"],
                    description=row["description"],
                    hit_count=row["hit_count"],
                    first_seen_at=row["first_seen_at"],
                    last_seen_at=row["last_seen_at"],
                )
                for row in cursor.fetchall()
            ]

    def list_mismatches(self, limit: int = 50) -> list[DomainMismatchRecord]:
        """Fetch recent domain mismatches."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    id, occurred_at, target_id, error_class,
                    error_message, traceback, raw_payload
                FROM domain_mismatches
                ORDER BY id DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [
                DomainMismatchRecord(
                    mismatch_id=row["id"],
                    occurred_at=row["occurred_at"],
                    target_id=row["target_id"],
                    error_class=row["error_class"],
                    error_message=row["error_message"],
                    traceback=row["traceback"],
                    raw_payload=row["raw_payload"],
                )
                for row in cursor.fetchall()
            ]
