"""Evaluation metrics for the alert Agent MVP."""

from __future__ import annotations

from collections import Counter

from server.analyzer import analyze_alert, list_alerts
from server.storage import list_audit_records, list_feedback, list_knowledge_cases


def build_evaluation_metrics(role: str | None = None) -> dict:
    alerts = list_alerts()
    feedback = list_feedback()
    audit = list_audit_records()
    cases = list_knowledge_cases()

    alert_ids = {alert.alert_id for alert in alerts}
    feedback_by_alert = _group_by(feedback, "alert_id")
    audit_by_action = Counter(row["action"] for row in audit)
    severity_counts = Counter(alert.severity for alert in alerts)
    status_counts = Counter(alert.status for alert in alerts)
    recurrence_counts = Counter(row["recurrence_risk"] for row in feedback)

    analyses = []
    for alert in alerts:
        try:
            analyses.append(analyze_alert(alert.alert_id, role))
        except KeyError:
            continue

    missing_required_total = sum(len(result.collection_status.missing_required_sources) for result in analyses)
    missing_optional_total = sum(len(result.collection_status.missing_optional_sources) for result in analyses)

    selected_ranks = [
        int(row["selected_cause_rank"])
        for row in feedback
        if row.get("selected_cause_rank") is not None
    ]
    top1_hits = sum(1 for rank in selected_ranks if rank == 1)
    top3_hits = sum(1 for rank in selected_ranks if 1 <= rank <= 3)

    feedback_alert_ids = set(feedback_by_alert)
    unresolved_alerts = [
        alert.alert_id
        for alert in alerts
        if alert.severity in {"critical", "high"} and alert.alert_id not in feedback_alert_ids
    ]

    return {
        "summary": {
            "total_alerts": len(alerts),
            "critical_alerts": severity_counts["critical"],
            "high_alerts": severity_counts["high"],
            "feedback_records": len(feedback),
            "alerts_with_feedback": len(feedback_alert_ids & alert_ids),
            "knowledge_cases": len(cases),
            "analysis_requests": audit_by_action["analysis_requested"],
            "unresolved_high_priority": len(unresolved_alerts),
        },
        "quality": {
            "top1_adoption_rate": _rate(top1_hits, len(selected_ranks)),
            "top3_adoption_rate": _rate(top3_hits, len(selected_ranks)),
            "feedback_coverage_rate": _rate(len(feedback_alert_ids & alert_ids), len(alerts)),
            "recommendation_feedback_count": len(selected_ranks),
        },
        "risk": {
            "recurrence_risk": dict(recurrence_counts),
            "unresolved_alert_ids": unresolved_alerts,
            "missing_required_sources_total": missing_required_total,
            "missing_optional_sources_total": missing_optional_total,
        },
        "distribution": {
            "severity": dict(severity_counts),
            "status": dict(status_counts),
            "audit_actions": dict(audit_by_action),
        },
        "notes": [
            "Metrics are calculated from mock alerts plus SQLite feedback/audit/local case data.",
            "Top 1/Top 3 adoption rates use engineer-selected root-cause ranks from feedback records.",
            "Response-time metrics are not available until external alert receipt and acknowledgement timestamps are captured.",
        ],
    }


def _group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)

