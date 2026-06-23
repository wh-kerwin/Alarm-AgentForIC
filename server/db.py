"""SQLite database initialization and connection helpers."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from server.config import get_database_config

SCHEMA_VERSION = 1


def get_database_path() -> Path:
    config = get_database_config()
    if config.engine != "sqlite" or config.path is None:
        raise NotImplementedError("PostgreSQL is reserved for production and is not implemented in this MVP.")
    return config.path


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        initialize(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version INTEGER PRIMARY KEY,
          applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback_records (
          feedback_id TEXT PRIMARY KEY,
          alert_id TEXT NOT NULL,
          selected_cause_rank INTEGER,
          final_root_cause TEXT NOT NULL,
          action_taken TEXT NOT NULL,
          recurrence_risk TEXT NOT NULL,
          notes TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge_cases (
          case_id TEXT PRIMARY KEY,
          alarm_code TEXT NOT NULL,
          equipment_family TEXT NOT NULL,
          root_cause TEXT NOT NULL,
          action TEXT NOT NULL,
          tags_json TEXT NOT NULL,
          source TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_records (
          audit_id TEXT PRIMARY KEY,
          action TEXT NOT NULL,
          role TEXT NOT NULL,
          alert_id TEXT NOT NULL,
          summary TEXT NOT NULL,
          created_at TEXT NOT NULL,
          metadata_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
        (SCHEMA_VERSION,),
    )


def encode_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def decode_json(value: str):
    return json.loads(value)

