"""Rule-backed root cause analyzer for the MVP Agent."""

from __future__ import annotations

from datetime import UTC, datetime

from server.connectors import get_connector
from server.models import Alert, AnalysisResult, Evidence, RootCauseCandidate
from server.storage import find_knowledge_cases


def list_alerts() -> list[Alert]:
    return get_connector().list_alerts()


def get_alert(alert_id: str) -> Alert | None:
    return get_connector().get_alert(alert_id)


def _equipment_family(equipment_id: str) -> str:
    return equipment_id.split("-", maxsplit=1)[0]


def _matching_case(alert: Alert):
    family = _equipment_family(alert.equipment_id)
    return next(iter(find_knowledge_cases(alert.alarm_code, family)), None)


def _has_event(alert_id: str, event_type: str, text: str | None = None) -> bool:
    events = get_connector().list_events(alert_id)
    for event in events:
        haystack = f"{event.title} {event.description}".lower()
        if event.event_type == event_type and (text is None or text.lower() in haystack):
            return True
    return False


def analyze_alert(alert_id: str) -> AnalysisResult:
    alert = get_alert(alert_id)
    if alert is None:
        raise KeyError(alert_id)

    events = get_connector().list_events(alert_id)
    candidates = _build_candidates(alert)
    handling = get_connector().list_sop_actions(alert.alarm_code)
    data_sources = sorted({event.source for event in events} | {alert.source, "KnowledgeBase", "SOP/OCAP"})
    escalation_required = alert.severity in {"critical", "high"}
    target_role = "Shift Lead + EE/PE" if alert.severity == "critical" else "Owner Engineer"

    return AnalysisResult(
        alert_id=alert.alert_id,
        alert_summary=alert.summary,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        impact_scope={
            "equipment": alert.equipment_id,
            "chamber": alert.chamber_id,
            "lot": alert.lot_id,
            "wafer": alert.wafer_id,
            "recipe": alert.recipe_id,
            "product": alert.product_id,
            "time_window": "告警前后 120 分钟",
        },
        timeline=events,
        root_cause_candidates=candidates,
        handling_recommendations=handling,
        escalation={
            "required": escalation_required,
            "target_role": target_role,
            "reason": "高等级告警需要跨角色确认" if escalation_required else "当前可由 owner 跟进",
        },
        agent_limitations=[
            "当前 MVP 使用内置样例数据，尚未接入真实 EAP/MES/FDC/YMS。",
            "根因置信度来自规则、历史案例和事件证据，不代表最终工程判定。",
            "Agent 只提供建议，不执行放行、改 recipe 或设备控制动作。",
        ],
        data_sources=data_sources,
    )


def _build_candidates(alert: Alert) -> list[RootCauseCandidate]:
    case = _matching_case(alert)
    candidates: list[RootCauseCandidate] = []

    if alert.alarm_code == "VAC-LOW-302":
        candidates.extend(
            [
                RootCauseCandidate(
                    rank=1,
                    cause="PM 后 foreline 或 chamber sealing 不稳定，导致抽气效率下降。",
                    confidence="high",
                    category="equipment",
                    evidence=[
                        Evidence("近期维护", "告警前约 87 分钟 CH-B 完成 dry pump filter 清洁。", "CMMS", "high"),
                        Evidence("压力波动", "foreline pressure 方差连续高于同 recipe P95。", "FDC", "high"),
                        Evidence("历史案例", case.root_cause if case else "同 alarm code 存在 PM 后 sealing 异常案例。", "KnowledgeBase", "medium"),
                    ],
                    counter_evidence=["尚未看到 leak check 实测结果。"],
                    verification_steps=[
                        "执行 foreline leak check 并记录 leak rate。",
                        "检查 dry pump filter seating 与 chamber door seal。",
                        "比对 PM 前后 pump current 与 pressure trace。",
                    ],
                    recommended_actions=[
                        "维持设备 DOWN，hold 当前 lot。",
                        "完成 sealing 检查和 qualification 后再恢复生产。",
                    ],
                ),
                RootCauseCandidate(
                    rank=2,
                    cause="Throttle valve response 异常造成 chamber pressure 控制失稳。",
                    confidence="medium",
                    category="equipment",
                    evidence=[
                        Evidence("阀位震荡", "throttle valve position 在 42%-78% 之间快速摆动。", "EAP", "high"),
                        Evidence("报警时序", "阀位震荡发生在 VAC-LOW-302 前 2 分钟。", "Timeline", "medium"),
                    ],
                    counter_evidence=["尚未确认阀门 command 与 actual position 偏差。"],
                    verification_steps=["拉取 valve command/actual trace。", "执行 throttle valve response test。"],
                    recommended_actions=["若 response test 失败，安排阀门维护并重新跑 monitor wafer。"],
                ),
                RootCauseCandidate(
                    rank=3,
                    cause="新 recipe OX-ETCH-45N-A3 的 vacuum window 与当前 chamber 状态不匹配。",
                    confidence="low",
                    category="process",
                    evidence=[
                        Evidence("Recipe 切换", "告警前 21 分钟 recipe 从 A2 切换到 A3。", "MES", "medium"),
                    ],
                    counter_evidence=["没有看到 setpoint 变更细节，也没有同 recipe 其他 chamber 对比。"],
                    verification_steps=["比较 A2/A3 pressure setpoint 与 pumpdown step。", "查看其他 chamber 跑 A3 的 trace。"],
                    recommended_actions=["在确认设备硬件前，不建议直接修改 recipe。"],
                ),
            ]
        )
    elif alert.alarm_code == "TEMP-DRIFT-118":
        candidates.extend(
            [
                RootCauseCandidate(
                    rank=1,
                    cause="APC offset 调整叠加 heater zone sensor calibration 偏差，造成温度 drift。",
                    confidence="high",
                    category="process-control",
                    evidence=[
                        Evidence("APC 调整", "告警前 APC 对 heater zone 2 增加 +1.8C offset。", "APC", "high"),
                        Evidence("FDC 趋势", "zone 2 temperature 连续 9 个采样点上升。", "FDC", "high"),
                        Evidence("历史案例", case.root_cause if case else "同类 temperature drift 案例指向 APC 与 sensor calibration。", "KnowledgeBase", "medium"),
                    ],
                    counter_evidence=["尚未完成 sensor calibration 复核。"],
                    verification_steps=["冻结 APC offset。", "比较 golden lot temperature profile。", "复核 zone 2 sensor calibration。"],
                    recommended_actions=["暂停自动调参，PE/EE 联合确认后再恢复 APC。"],
                ),
                RootCauseCandidate(
                    rank=2,
                    cause="Heater zone 2 控制回路响应变慢。",
                    confidence="medium",
                    category="equipment",
                    evidence=[
                        Evidence("趋势异常", "温度持续上升并越过 guard band。", "FDC", "medium"),
                    ],
                    counter_evidence=["没有 heater power/current trace。"],
                    verification_steps=["拉取 heater power、current、PID output。"],
                    recommended_actions=["如响应异常，安排 heater loop check。"],
                ),
                RootCauseCandidate(
                    rank=3,
                    cause="当前 lot 或产品族对温度窗口更敏感。",
                    confidence="low",
                    category="product-process",
                    evidence=[
                        Evidence("产品上下文", f"告警发生在产品 {alert.product_id}、recipe {alert.recipe_id}。", "MES", "low"),
                    ],
                    counter_evidence=["缺少正常批次对比数据。"],
                    verification_steps=["对比同产品近 20 个 lot 的 FDC 分布。"],
                    recommended_actions=["若仅特定产品异常，升级 PIE 做产品族敏感性分析。"],
                ),
            ]
        )
    else:
        candidates.extend(
            [
                RootCauseCandidate(
                    rank=1,
                    cause="Edge rinse nozzle 更换后角度或流量偏移，造成 edge-ring defect pattern。",
                    confidence="high" if _has_event(alert.alert_id, "MaintenanceEvent", "nozzle") else "medium",
                    category="yield-defect",
                    evidence=[
                        Evidence("近期维护", "TRACK-1 edge rinse nozzle 在异常前一晚更换。", "CMMS", "high"),
                        Evidence("缺陷图形", "多片 wafer 出现 edge-ring defect pattern。", "YMS", "high"),
                        Evidence("历史案例", case.root_cause if case else "类似案例与 nozzle angle 相关。", "KnowledgeBase", "medium"),
                    ],
                    counter_evidence=["尚未完成 review image 抽查和前后 lot 对比。"],
                    verification_steps=["抽查 defect review image。", "检查 nozzle angle 和 edge bead removal trend。", "比较前后 lot wafer map。"],
                    recommended_actions=["hold 受影响 lot，执行 monitor wafer 验证后恢复。"],
                ),
                RootCauseCandidate(
                    rank=2,
                    cause="Track spin profile 或 edge bead removal 参数漂移。",
                    confidence="medium",
                    category="process",
                    evidence=[
                        Evidence("空间分布", "缺陷集中在 wafer edge-ring 区域。", "YMS", "medium"),
                    ],
                    counter_evidence=["缺少 spin speed、dispense、EBR 流量 trace。"],
                    verification_steps=["拉取 track process trace。", "比对正常 lot 的 edge trend。"],
                    recommended_actions=["确认 trace 后再决定是否调整 track 参数。"],
                ),
                RootCauseCandidate(
                    rank=3,
                    cause="前序工艺或来料导致边缘缺陷在 litho 后显现。",
                    confidence="low",
                    category="upstream",
                    evidence=[
                        Evidence("批次影响", "同 lot 多片 wafer 异常，可能存在批次级因素。", "YMS", "low"),
                    ],
                    counter_evidence=["目前最强证据仍指向 TRACK-1 近期维护。"],
                    verification_steps=["追溯前序站点设备、recipe 与 metrology。"],
                    recommended_actions=["若 track 检查无异常，转 PIE 做前序路径分析。"],
                ),
            ]
        )

    return candidates
