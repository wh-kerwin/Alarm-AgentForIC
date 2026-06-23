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
- Rule-backed context correlation
- Root cause candidates with evidence
- SOP/OCAP style handling recommendations
- Engineer feedback storage in `data/feedback.json`

## Not Included Yet

- Real EAP/MES/FDC/SPC/YMS connectors
- LLM provider integration
- Authentication and role-based permissions
- Production database
- Automatic equipment control or lot release

