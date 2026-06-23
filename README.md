# Alarm-AgentForIC

半导体异常告警与根因分析 Agent MVP。当前版本聚焦设备告警响应，内置样例数据，支持告警工作台、事件时间线、Top 根因候选、证据链、处置建议和工程师反馈闭环。

## Tech Stack

- Backend: Python 3.13 standard library HTTP API
- Frontend: Vue 3 + Vite + TypeScript
- UI: Custom dense fab operations console

## Run Locally

Use the Python runtime requested for this project:

```powershell
& 'C:\Python313\python.exe' run.py --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd client
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Build Frontend

```powershell
cd client
npm run build
```

After build, the Python server can also serve the built frontend from `client/dist`:

```text
http://127.0.0.1:8000
```

## Test

```powershell
& 'C:\Python313\python.exe' -m unittest discover -s tests
```

```powershell
cd client
npm run build
```

## Current MVP Scope

- Sample alert ingestion model
- Connector boundary backed by local JSON fixtures
- Mock EAP equipment alarm feed normalization
- Configurable context collection policy by alarm code/equipment family
- Rule-backed context correlation
- Root cause candidates with evidence
- SOP/OCAP style handling recommendations
- Engineer feedback storage in `data/feedback.json`
- Knowledge case management through API and UI
- Role-aware advisory mode for EE/PE/QE/PIE/Shift Lead/Admin
- Audit trail for analysis, feedback, and knowledge-case creation

## API Highlights

- `GET /api/alerts`
- `POST /api/alerts/{alert_id}/analyze`
- `GET /api/alerts/{alert_id}/feedback`
- `POST /api/alerts/{alert_id}/feedback`
- `GET /api/knowledge-cases`
- `POST /api/knowledge-cases`
- `GET /api/alerts/{alert_id}/knowledge-cases`
- `GET /api/roles`
- `GET /api/alerts/{alert_id}/audit`
- `GET /api/audit`

## Connector Boundary

The current development connector is documented in `docs/architecture/connectors.md`. Production EAP, MES, FDC, SPC, APC, YMS, CMMS, and SOP/OCAP integrations should implement the same backend contract.

Mock data lives in:

- `data/mock_equipment_alarm_feed.json`
- `data/sample_alerts.json`
- `data/sample_events.json`
- `data/context_policies.json`
- `data/sop.json`
- `data/knowledge_cases.seed.json`
- `data/role_policies.json`

## Safety Boundary

The Agent is advisory-only. It can generate analysis, recommendations, feedback records, cases, and audit records. It must not automatically release lots, modify recipes, change equipment parameters, or close high-severity alerts.

The current role context is passed with `X-Agent-Role`. This is not authentication; it is an MVP role simulation for UI behavior, audit metadata, and safety messaging.

## Not Included Yet

- Real EAP/MES/FDC/SPC/YMS connectors
- LLM provider integration
- Authentication and role-based permissions
- Production database
- Automatic equipment control or lot release
