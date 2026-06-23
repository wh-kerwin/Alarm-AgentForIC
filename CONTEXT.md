# Alarm-AgentForIC Context

## Product

Alarm-AgentForIC is a semiconductor manufacturing anomaly alert Agent. It starts with equipment alarm response, then expands to yield and defect anomaly analysis, process parameter anomaly analysis, and finally a general alert Agent platform.

## Problem Space

Semiconductor engineers currently handle alarms by manually collecting data from equipment logs, EAP, MES, FDC, SPC, APC, YMS, maintenance records, SOPs, OCAP documents, and historical cases. This creates slow response, inconsistent diagnosis, repeated work, and weak knowledge reuse.

The product turns an alert into a structured analysis task:

1. Normalize the alert.
2. Collect relevant context.
3. Correlate events.
4. Generate possible root causes.
5. Recommend verification and handling actions.
6. Capture engineer feedback.
7. Improve the knowledge base.

## Core Domain Terms

- Alert: A raw or normalized abnormal signal from equipment, MES, FDC, SPC, YMS, or another manufacturing system.
- Alarm: An equipment-originated alert, usually tied to a tool, chamber, module, alarm code, and timestamp.
- Alert Event: The normalized event model used by the Agent across all alert sources.
- Equipment: A manufacturing tool or machine on the fab floor.
- Chamber: A process chamber or module within equipment.
- Lot: A manufacturing batch containing wafers.
- Wafer: A semiconductor wafer processed through the fab.
- Recipe: A process configuration or program used by equipment.
- Sensor Trace: Time-series equipment or process sensor data.
- FDC: Fault Detection and Classification data and rules.
- SPC: Statistical Process Control data and rules.
- APC: Advanced Process Control adjustments and records.
- YMS: Yield Management System data, including yield, defect, and wafer map information.
- PM: Preventive Maintenance.
- SOP: Standard Operating Procedure.
- OCAP: Out of Control Action Plan.
- Root Cause Candidate: A ranked possible explanation for an alert, with evidence and uncertainty.
- Evidence Chain: The structured support behind a root cause candidate.
- Handling Recommendation: Suggested verification, recovery, escalation, or containment action.
- Human Feedback: Engineer confirmation, correction, or supplement to the Agent's analysis.
- Alert Workbench: The UI where engineers review alerts, timelines, root causes, recommendations, and feedback.

## Product Phases

### Phase 1: Equipment Alarm Response Agent

Focus on equipment alarms. The Agent collects alarm logs, equipment state, sensor/FDC traces, recipe changes, PM records, lot context, and historical similar alarms. It outputs a timeline, Top 3 root cause candidates, evidence, and handling recommendations.

### Phase 2: Yield and Defect Anomaly Agent

Extend to yield drop, defect excursion, wafer map anomaly, metrology trend, and lot-to-lot comparison.

### Phase 3: Process Parameter Anomaly Agent

Extend to SPC/FDC/APC alerts, process drift, parameter excursions, and process window analysis.

### Final Platform: General Alert Agent

Abstract common capabilities into a configurable alert Agent platform with normalized alert models, context collection strategies, event correlation, root cause generation, recommendation templates, feedback loops, and evaluation metrics.

## Safety Boundaries

The MVP is advisory only.

- The Agent can read authorized data.
- The Agent can generate analysis and recommendations.
- The Agent can draft handling records.
- The Agent must not automatically release lots.
- The Agent must not automatically modify recipes.
- The Agent must not automatically modify equipment parameters.
- The Agent must not automatically close high-severity alerts.
- High-risk actions require authorized engineer confirmation.

## Success Metrics

- Reduce mean first response time.
- Reduce manual cross-system lookup count.
- Improve Top 3 root cause hit rate.
- Improve recommendation adoption rate.
- Increase structured case reuse.
- Track recurrence and unresolved alerts.

## Current PRD

The initial PRD is stored at `docs/plans/2026-06-23-semiconductor-alert-agent-prd.md`.

