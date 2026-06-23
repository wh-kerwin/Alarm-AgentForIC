"""Small JSON-file storage for engineer feedback."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from server.models import FeedbackRecord, KnowledgeCase

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
KNOWLEDGE_SEED_FILE = DATA_DIR / "knowledge_cases.seed.json"
KNOWLEDGE_LOCAL_FILE = DATA_DIR / "knowledge_cases.local.json"


def _read_all() -> list[dict]:
    if not FEEDBACK_FILE.exists():
        return []
    return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))


def list_feedback(alert_id: str | None = None) -> list[dict]:
    rows = _read_all()
    if alert_id:
        return [row for row in rows if row["alert_id"] == alert_id]
    return rows


def save_feedback(record: FeedbackRecord) -> FeedbackRecord:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = _read_all()
    if not record.feedback_id:
        record.feedback_id = f"FB-{uuid4().hex[:10].upper()}"
    rows.append(asdict(record))
    FEEDBACK_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def list_knowledge_cases() -> list[KnowledgeCase]:
    rows = _read_json_list(KNOWLEDGE_SEED_FILE) + _read_json_list(KNOWLEDGE_LOCAL_FILE)
    return [KnowledgeCase(**row) for row in rows]


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

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = _read_json_list(KNOWLEDGE_LOCAL_FILE)
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
    rows.append(asdict(record))
    KNOWLEDGE_LOCAL_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return record
