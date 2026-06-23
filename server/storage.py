"""Repository functions for feedback, knowledge cases, and audit records."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from server.db import connect, decode_json, encode_json
from server.models import AuditRecord, FeedbackRecord, KnowledgeCase

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KNOWLEDGE_SEED_FILE = DATA_DIR / "knowledge_cases.seed.json"


def list_feedback(alert_id: str | None = None) -> list[dict]:
    sql = "SELECT * FROM feedback_records"
    params: tuple = ()
    if alert_id:
        sql += " WHERE alert_id = ?"
        params = (alert_id,)
    sql += " ORDER BY created_at DESC"
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def save_feedback(record: FeedbackRecord) -> FeedbackRecord:
    if not record.feedback_id:
        record.feedback_id = f"FB-{uuid4().hex[:10].upper()}"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO feedback_records (
              feedback_id, alert_id, selected_cause_rank, final_root_cause,
              action_taken, recurrence_risk, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.feedback_id,
                record.alert_id,
                record.selected_cause_rank,
                record.final_root_cause,
                record.action_taken,
                record.recurrence_risk,
                record.notes,
                record.created_at,
            ),
        )
    return record


def _read_seed_cases() -> list[KnowledgeCase]:
    if not KNOWLEDGE_SEED_FILE.exists():
        return []
    rows = json.loads(KNOWLEDGE_SEED_FILE.read_text(encoding="utf-8"))
    return [KnowledgeCase(**row) for row in rows]


def _list_local_knowledge_cases() -> list[KnowledgeCase]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM knowledge_cases ORDER BY created_at DESC").fetchall()
    return [
        KnowledgeCase(
            case_id=row["case_id"],
            alarm_code=row["alarm_code"],
            equipment_family=row["equipment_family"],
            root_cause=row["root_cause"],
            action=row["action"],
            tags=decode_json(row["tags_json"]),
            source=row["source"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def list_knowledge_cases() -> list[KnowledgeCase]:
    return _read_seed_cases() + _list_local_knowledge_cases()


def find_knowledge_cases(alarm_code: str | None = None, equipment_family: str | None = None) -> list[KnowledgeCase]:
    cases = list_knowledge_cases()
    if alarm_code:
        cases = [case for case in cases if case.alarm_code == alarm_code]
    if equipment_family:
        cases = [case for case in cases if case.equipment_family == equipment_family]
    return cases


def create_knowledge_case(payload: dict) -> KnowledgeCase:
    required = ["alarm_code", "equipment_family", "root_cause", "action"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    if missing:
        raise ValueError(f"missing_required_fields:{','.join(missing)}")

    tags = payload.get("tags", [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

    record = KnowledgeCase(
        case_id=f"CASE-LOCAL-{uuid4().hex[:8].upper()}",
        alarm_code=str(payload["alarm_code"]).strip(),
        equipment_family=str(payload["equipment_family"]).strip().upper(),
        root_cause=str(payload["root_cause"]).strip(),
        action=str(payload["action"]).strip(),
        tags=list(tags),
        source=str(payload.get("source", "engineer")),
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO knowledge_cases (
              case_id, alarm_code, equipment_family, root_cause,
              action, tags_json, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.case_id,
                record.alarm_code,
                record.equipment_family,
                record.root_cause,
                record.action,
                encode_json(record.tags),
                record.source,
                record.created_at,
            ),
        )
    return record


def list_audit_records(alert_id: str | None = None) -> list[dict]:
    sql = "SELECT * FROM audit_records"
    params: tuple = ()
    if alert_id:
        sql += " WHERE alert_id = ?"
        params = (alert_id,)
    sql += " ORDER BY created_at DESC"
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [
        {
            "audit_id": row["audit_id"],
            "action": row["action"],
            "role": row["role"],
            "alert_id": row["alert_id"],
            "summary": row["summary"],
            "created_at": row["created_at"],
            "metadata": decode_json(row["metadata_json"]),
        }
        for row in rows
    ]


def save_audit_record(action: str, role: str, alert_id: str, summary: str, metadata: dict | None = None) -> AuditRecord:
    record = AuditRecord(
        audit_id=f"AUD-{uuid4().hex[:10].upper()}",
        action=action,
        role=role,
        alert_id=alert_id,
        summary=summary,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        metadata=metadata or {},
    )
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_records (
              audit_id, action, role, alert_id, summary, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.audit_id,
                record.action,
                record.role,
                record.alert_id,
                record.summary,
                record.created_at,
                encode_json(record.metadata),
            ),
        )
    return record

