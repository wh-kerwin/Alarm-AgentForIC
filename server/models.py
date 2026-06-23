"""Domain models for semiconductor alert analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["critical", "high", "medium", "low"]
AlertStatus = Literal["new", "analyzing", "recommended", "feedback_recorded"]
Confidence = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class Alert:
    alert_id: str
    source: str
    severity: Severity
    status: AlertStatus
    equipment_id: str
    chamber_id: str
    alarm_code: str
    alarm_message: str
    timestamp: str
    lot_id: str
    wafer_id: str
    recipe_id: str
    product_id: str
    current_state: str
    owner_role: str
    summary: str


@dataclass(frozen=True)
class Event:
    time: str
    event_type: str
    title: str
    description: str
    source: str
    severity: Severity = "medium"


@dataclass(frozen=True)
class CollectionPolicy:
    policy_id: str
    alarm_code: str
    equipment_family: str
    time_window_minutes: int
    required_sources: list[str]
    optional_sources: list[str]
    fallback_note: str


@dataclass(frozen=True)
class CollectionStatus:
    policy: CollectionPolicy
    collected_sources: list[str]
    missing_required_sources: list[str]
    missing_optional_sources: list[str]
    fallback_notes: list[str]


@dataclass(frozen=True)
class Evidence:
    label: str
    detail: str
    source: str
    strength: Confidence


@dataclass(frozen=True)
class RootCauseCandidate:
    rank: int
    cause: str
    confidence: Confidence
    category: str
    evidence: list[Evidence]
    counter_evidence: list[str]
    verification_steps: list[str]
    recommended_actions: list[str]


@dataclass(frozen=True)
class AnalysisResult:
    alert_id: str
    alert_summary: str
    generated_at: str
    impact_scope: dict[str, str]
    timeline: list[Event]
    root_cause_candidates: list[RootCauseCandidate]
    handling_recommendations: list[str]
    escalation: dict[str, str | bool]
    agent_limitations: list[str]
    data_sources: list[str]
    collection_status: CollectionStatus


@dataclass
class FeedbackRecord:
    feedback_id: str
    alert_id: str
    selected_cause_rank: int | None
    final_root_cause: str
    action_taken: str
    recurrence_risk: Literal["high", "medium", "low"]
    notes: str
    created_at: str


@dataclass(frozen=True)
class KnowledgeCase:
    case_id: str
    alarm_code: str
    equipment_family: str
    root_cause: str
    action: str
    tags: list[str] = field(default_factory=list)
    source: str = "seed"
    created_at: str = ""
