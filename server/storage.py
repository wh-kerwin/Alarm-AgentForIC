"""Small JSON-file storage for engineer feedback."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from server.models import FeedbackRecord

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.json"


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

