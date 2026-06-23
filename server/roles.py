"""Role policy and advisory-only safety gates."""

from __future__ import annotations

import json
from pathlib import Path

from server.models import Alert, RolePolicy

ROOT = Path(__file__).resolve().parent.parent
ROLE_POLICY_FILE = ROOT / "data" / "role_policies.json"
DEFAULT_ROLE = "EE"


def list_role_policies() -> list[RolePolicy]:
    rows = json.loads(ROLE_POLICY_FILE.read_text(encoding="utf-8"))
    return [RolePolicy(**row) for row in rows]


def get_role_policy(role: str | None) -> RolePolicy:
    normalized = (role or DEFAULT_ROLE).upper()
    policies = list_role_policies()
    return next((policy for policy in policies if policy.role == normalized), policies[0])


def build_role_context(role: str | None, alert: Alert) -> dict[str, object]:
    policy = get_role_policy(role)
    return {
        "role": policy.role,
        "label": policy.label,
        "focus": policy.focus,
        "allowed_records": policy.allowed_records,
        "escalation_targets": policy.escalation_targets,
        "alert_owner_role": alert.owner_role,
        "is_owner_role": policy.role == alert.owner_role,
    }


def build_safety_gate(role: str | None, alert: Alert) -> dict[str, object]:
    policy = get_role_policy(role)
    high_risk_actions = [
        "release_lot",
        "modify_recipe",
        "change_equipment_parameter",
        "close_high_severity_alert",
    ]
    return {
        "mode": "advisory_only",
        "requires_human_confirmation": True,
        "blocked_actions": policy.blocked_actions,
        "high_risk_actions": high_risk_actions,
        "message": "Agent 只提供分析、验证建议和处置建议；放行 lot、修改 recipe、修改设备参数、关闭高等级告警都必须由授权工程师在外部系统确认。",
        "alert_severity": alert.severity,
    }
