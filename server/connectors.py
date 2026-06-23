"""Connector boundary for manufacturing data sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from server.models import Alert, Event, KnowledgeCase
from server.storage import list_knowledge_cases

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


class ManufacturingConnector(Protocol):
    """Stable data access contract for EAP/MES/FDC/YMS style sources."""

    def list_alerts(self) -> list[Alert]:
        raise NotImplementedError

    def get_alert(self, alert_id: str) -> Alert | None:
        raise NotImplementedError

    def list_events(self, alert_id: str) -> list[Event]:
        raise NotImplementedError

    def list_sop_actions(self, alarm_code: str) -> list[str]:
        raise NotImplementedError

    def list_knowledge_cases(self) -> list[KnowledgeCase]:
        raise NotImplementedError


class JsonFixtureConnector:
    """Connector backed by local JSON fixtures.

    This is the current development connector. Real factory integrations should
    implement the same methods for EAP, MES, FDC, SPC, APC, YMS, CMMS, and
    SOP/OCAP repositories.
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir

    def list_alerts(self) -> list[Alert]:
        return [Alert(**row) for row in self._read_json("sample_alerts.json")]

    def get_alert(self, alert_id: str) -> Alert | None:
        return next((alert for alert in self.list_alerts() if alert.alert_id == alert_id), None)

    def list_events(self, alert_id: str) -> list[Event]:
        events_by_alert = self._read_json("sample_events.json")
        return [Event(**row) for row in events_by_alert.get(alert_id, [])]

    def list_sop_actions(self, alarm_code: str) -> list[str]:
        sop_by_alarm = self._read_json("sop.json")
        return sop_by_alarm.get(alarm_code, ["收集上下文数据后由值班工程师确认处置动作。"])

    def list_knowledge_cases(self) -> list[KnowledgeCase]:
        return list_knowledge_cases()

    def _read_json(self, filename: str):
        return json.loads((self.data_dir / filename).read_text(encoding="utf-8"))


_connector: ManufacturingConnector = JsonFixtureConnector()


def get_connector() -> ManufacturingConnector:
    return _connector


def set_connector(connector: ManufacturingConnector) -> None:
    global _connector
    _connector = connector

