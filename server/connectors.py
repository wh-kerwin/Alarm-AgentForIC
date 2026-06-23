"""Connector boundary for manufacturing data sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from server.models import Alert, CollectionPolicy, Event, KnowledgeCase
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

    def get_collection_policy(self, alarm_code: str, equipment_family: str) -> CollectionPolicy:
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
        fixture_alerts = [Alert(**row) for row in self._read_json("sample_alerts.json")]
        raw_alerts = [self._normalize_eap_alarm(row) for row in self._read_json("mock_equipment_alarm_feed.json")]
        by_id = {alert.alert_id: alert for alert in fixture_alerts + raw_alerts}
        return list(by_id.values())

    def get_alert(self, alert_id: str) -> Alert | None:
        return next((alert for alert in self.list_alerts() if alert.alert_id == alert_id), None)

    def list_events(self, alert_id: str) -> list[Event]:
        events_by_alert = self._read_json("sample_events.json")
        return [Event(**row) for row in events_by_alert.get(alert_id, [])]

    def list_sop_actions(self, alarm_code: str) -> list[str]:
        sop_by_alarm = self._read_json("sop.json")
        return sop_by_alarm.get(alarm_code, ["收集上下文数据后由值班工程师确认处置动作。"])

    def get_collection_policy(self, alarm_code: str, equipment_family: str) -> CollectionPolicy:
        policies = [CollectionPolicy(**row) for row in self._read_json("context_policies.json")]
        return (
            next(
                (
                    policy
                    for policy in policies
                    if policy.alarm_code == alarm_code and policy.equipment_family == equipment_family
                ),
                None,
            )
            or next((policy for policy in policies if policy.alarm_code == alarm_code and policy.equipment_family == "*"), None)
            or next((policy for policy in policies if policy.alarm_code == "*" and policy.equipment_family == equipment_family), None)
            or next(policy for policy in policies if policy.alarm_code == "*" and policy.equipment_family == "*")
        )

    def list_knowledge_cases(self) -> list[KnowledgeCase]:
        return list_knowledge_cases()

    def _read_json(self, filename: str):
        return json.loads((self.data_dir / filename).read_text(encoding="utf-8"))

    def _normalize_eap_alarm(self, row: dict) -> Alert:
        severity_map = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low",
        }
        status = "new" if row.get("tool_state") == "DOWN" else "analyzing"
        owner_role = "EE" if str(row.get("source_system", "")).upper() == "EAP" else "PE"
        return Alert(
            alert_id=f"ALM-MOCK-{row['eap_event_id'].split('-')[-1]}",
            source=row.get("source_system", "EAP"),
            severity=severity_map.get(str(row.get("priority", "MEDIUM")).upper(), "medium"),
            status=status,
            equipment_id=row["tool"],
            chamber_id=row.get("module", ""),
            alarm_code=row["code"],
            alarm_message=row.get("message", ""),
            timestamp=row.get("event_time", ""),
            lot_id=row.get("lot", ""),
            wafer_id=row.get("wafer", ""),
            recipe_id=row.get("recipe", ""),
            product_id=row.get("product", ""),
            current_state=row.get("tool_state", ""),
            owner_role=owner_role,
            summary=f"{row['tool']} {row.get('module', '')} 触发 {row['code']}，状态 {row.get('tool_state', 'UNKNOWN')}。{row.get('operator_note', '')}",
        )


_connector: ManufacturingConnector = JsonFixtureConnector()


def get_connector() -> ManufacturingConnector:
    return _connector


def set_connector(connector: ManufacturingConnector) -> None:
    global _connector
    _connector = connector
