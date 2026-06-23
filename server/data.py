"""In-memory sample data for the MVP.

The production version should replace this module with connectors for EAP,
MES, FDC, SPC, APC, YMS, maintenance systems, SOP/OCAP repositories, and the
case knowledge base.
"""

from __future__ import annotations

from server.models import Alert, Event, KnowledgeCase


ALERTS: list[Alert] = [
    Alert(
        alert_id="ALM-20260623-001",
        source="EAP",
        severity="critical",
        status="new",
        equipment_id="ETCH-07",
        chamber_id="CH-B",
        alarm_code="VAC-LOW-302",
        alarm_message="Chamber vacuum level below process threshold",
        timestamp="2026-06-23 09:42:18",
        lot_id="L26A0619",
        wafer_id="W17",
        recipe_id="OX-ETCH-45N-A3",
        product_id="P-7NAND-128L",
        current_state="DOWN",
        owner_role="EE",
        summary="ETCH-07 CH-B 在加工 L26A0619 W17 时触发真空不足报警，设备进入 DOWN。",
    ),
    Alert(
        alert_id="ALM-20260623-002",
        source="FDC",
        severity="high",
        status="recommended",
        equipment_id="CVD-12",
        chamber_id="CH-A",
        alarm_code="TEMP-DRIFT-118",
        alarm_message="Process temperature drift exceeded FDC guard band",
        timestamp="2026-06-23 10:18:44",
        lot_id="L26A0621",
        wafer_id="W04",
        recipe_id="SIN-CVD-210C-B2",
        product_id="P-Logic-28",
        current_state="PROCESS",
        owner_role="PE",
        summary="CVD-12 CH-A 温度 FDC 趋势越过 guard band，尚未触发设备硬停。",
    ),
    Alert(
        alert_id="ALM-20260623-003",
        source="YMS",
        severity="medium",
        status="analyzing",
        equipment_id="LITHO-03",
        chamber_id="TRACK-1",
        alarm_code="DEFECT-PATTERN-044",
        alarm_message="Wafer map edge-ring defect pattern excursion",
        timestamp="2026-06-23 11:06:03",
        lot_id="L26A0588",
        wafer_id="W02-W25",
        recipe_id="PR-COAT-90N-C1",
        product_id="P-7NAND-128L",
        current_state="MONITOR",
        owner_role="QE",
        summary="L26A0588 多片 wafer 出现 edge-ring 缺陷图形，疑似 track 或前序工艺相关。",
    ),
]


EVENTS_BY_ALERT: dict[str, list[Event]] = {
    "ALM-20260623-001": [
        Event("2026-06-23 08:15:00", "MaintenanceEvent", "PM close", "CH-B 完成 dry pump filter 清洁，设备恢复生产。", "CMMS"),
        Event("2026-06-23 09:21:36", "RecipeChangeEvent", "Recipe loaded", "recipe 从 OX-ETCH-45N-A2 切换到 OX-ETCH-45N-A3。", "MES"),
        Event("2026-06-23 09:34:08", "SensorAnomalyEvent", "Pressure variance rising", "foreline pressure 方差连续 6 分钟高于同 recipe P95。", "FDC", "high"),
        Event("2026-06-23 09:40:51", "StateChangeEvent", "Throttle valve oscillation", "throttle valve position 在 42%-78% 之间快速摆动。", "EAP", "high"),
        Event("2026-06-23 09:42:18", "AlarmEvent", "VAC-LOW-302", "真空不足报警触发，设备进入 DOWN。", "EAP", "critical"),
        Event("2026-06-23 09:45:07", "HumanActionEvent", "Lot held", "值班工程师 hold L26A0619，等待设备确认。", "MES"),
    ],
    "ALM-20260623-002": [
        Event("2026-06-23 07:58:22", "APCAdjustmentEvent", "APC offset changed", "APC 对 heater zone 2 增加 +1.8C offset。", "APC"),
        Event("2026-06-23 09:55:30", "ProcessRunEvent", "Lot started", "L26A0621 开始在 CVD-12 CH-A 加工。", "MES"),
        Event("2026-06-23 10:12:10", "SensorAnomalyEvent", "Temperature drift", "zone 2 temperature 连续 9 个采样点上升。", "FDC", "high"),
        Event("2026-06-23 10:18:44", "SPCFDCViolationEvent", "TEMP-DRIFT-118", "FDC guard band 被突破。", "FDC", "high"),
    ],
    "ALM-20260623-003": [
        Event("2026-06-22 21:33:18", "MaintenanceEvent", "Nozzle replaced", "TRACK-1 edge rinse nozzle 更换。", "CMMS"),
        Event("2026-06-23 02:17:40", "ProcessRunEvent", "Lot processed", "L26A0588 完成 PR coat。", "MES"),
        Event("2026-06-23 10:42:12", "YieldDefectEvent", "Edge-ring pattern", "W02-W25 多片 wafer 出现 edge-ring defect pattern。", "YMS", "medium"),
        Event("2026-06-23 11:06:03", "AlarmEvent", "DEFECT-PATTERN-044", "YMS 触发 pattern excursion。", "YMS", "medium"),
    ],
}


KNOWLEDGE_CASES: list[KnowledgeCase] = [
    KnowledgeCase(
        case_id="CASE-ETCH-VAC-009",
        alarm_code="VAC-LOW-302",
        equipment_family="ETCH",
        root_cause="PM 后 foreline sealing 不稳定导致抽气效率下降。",
        action="检查 dry pump/filter sealing、foreline leak rate、throttle valve response，再执行 chamber qualification。",
        tags=["vacuum", "pm", "foreline", "etch"],
    ),
    KnowledgeCase(
        case_id="CASE-CVD-TEMP-014",
        alarm_code="TEMP-DRIFT-118",
        equipment_family="CVD",
        root_cause="APC offset 与 heater zone sensor calibration 偏差叠加造成温度漂移。",
        action="冻结 APC offset，复核 zone sensor calibration，比较 golden lot trace。",
        tags=["temperature", "apc", "fdc", "cvd"],
    ),
    KnowledgeCase(
        case_id="CASE-LITHO-DEF-006",
        alarm_code="DEFECT-PATTERN-044",
        equipment_family="LITHO",
        root_cause="edge rinse nozzle 更换后角度偏移造成边缘残胶。",
        action="检查 nozzle angle、spin profile、edge bead removal trend，必要时重做 qualification。",
        tags=["defect", "edge-ring", "track", "maintenance"],
    ),
]


SOP_BY_ALARM_CODE: dict[str, list[str]] = {
    "VAC-LOW-302": [
        "保持设备 DOWN 状态，确认 chamber 内无 wafer 安全风险。",
        "检查 dry pump、foreline、throttle valve 与 chamber door seal。",
        "比较告警前后 pressure、valve position、pump current trace。",
        "完成 leak check 与 qualification 后再申请恢复生产。",
    ],
    "TEMP-DRIFT-118": [
        "暂停自动 APC offset 更新，保留当前 trace。",
        "对比同 recipe golden lot 的 zone temperature profile。",
        "检查 heater zone sensor calibration 与 recent maintenance。",
        "若 drift 持续扩大，hold 当前 lot 并升级 PE/EE 联合确认。",
    ],
    "DEFECT-PATTERN-044": [
        "hold 受影响 lot，确认 defect review image 与 wafer map pattern。",
        "关联 track maintenance、nozzle replacement 与 edge rinse trend。",
        "抽查前后 lot 是否出现相同 edge-ring pattern。",
        "必要时执行 monitor wafer 验证后恢复。",
    ],
}

