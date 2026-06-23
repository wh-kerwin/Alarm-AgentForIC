# Connector Boundary

The MVP uses `JsonFixtureConnector` as the development connector. Production integrations should implement the same `ManufacturingConnector` contract in `server/connectors.py`.

## Contract

Connectors provide normalized manufacturing context:

- `list_alerts()` returns normalized Alert Events.
- `get_alert(alert_id)` returns one Alert Event.
- `list_events(alert_id)` returns correlated context events for the alert.
- `list_sop_actions(alarm_code)` returns SOP/OCAP-style handling actions.
- `list_knowledge_cases()` returns reusable historical cases.

## Current Fixture Sources

- `data/sample_alerts.json`
- `data/sample_events.json`
- `data/sop.json`
- `data/knowledge_cases.seed.json`

Engineer-created cases are written to `data/knowledge_cases.local.json`, which is intentionally ignored by git.

## Real Integration Notes

Future EAP, MES, FDC, SPC, APC, YMS, and CMMS connectors should map source-specific payloads into the same domain models. Missing data should be explicit: return empty optional collections and allow the analyzer to report limitations instead of inventing context.

