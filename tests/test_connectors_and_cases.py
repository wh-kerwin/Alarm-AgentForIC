import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server.connectors import JsonFixtureConnector
from server.storage import create_knowledge_case, find_knowledge_cases


class ConnectorTests(unittest.TestCase):
    def test_json_fixture_connector_loads_alerts_events_and_sop(self):
        connector = JsonFixtureConnector()

        alerts = connector.list_alerts()
        self.assertEqual(alerts[0].alert_id, "ALM-20260623-001")
        self.assertEqual(connector.get_alert("ALM-20260623-001").equipment_id, "ETCH-07")
        self.assertGreaterEqual(len(connector.list_events("ALM-20260623-001")), 1)
        self.assertGreaterEqual(len(connector.list_sop_actions("VAC-LOW-302")), 1)

    def test_json_fixture_connector_normalizes_mock_eap_feed(self):
        connector = JsonFixtureConnector()

        alert = connector.get_alert("ALM-MOCK-9002")

        self.assertIsNotNone(alert)
        self.assertEqual(alert.source, "EAP")
        self.assertEqual(alert.severity, "high")
        self.assertEqual(alert.alarm_code, "RF-MATCH-221")
        self.assertEqual(alert.equipment_id, "ETCH-07")

    def test_context_policy_matches_alarm_and_equipment_family(self):
        connector = JsonFixtureConnector()

        policy = connector.get_collection_policy("RF-MATCH-221", "ETCH")
        fallback = connector.get_collection_policy("UNKNOWN", "UNKNOWN")

        self.assertEqual(policy.policy_id, "POLICY-ETCH-RF")
        self.assertEqual(policy.time_window_minutes, 90)
        self.assertEqual(fallback.policy_id, "POLICY-DEFAULT")


class KnowledgeCaseTests(unittest.TestCase):
    def test_create_and_find_local_knowledge_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed = Path(tmp) / "seed.json"
            local = Path(tmp) / "local.json"
            seed.write_text("[]", encoding="utf-8")

            with patch("server.storage.KNOWLEDGE_SEED_FILE", seed), patch("server.storage.KNOWLEDGE_LOCAL_FILE", local):
                created = create_knowledge_case(
                    {
                        "alarm_code": "VAC-LOW-302",
                        "equipment_family": "ETCH",
                        "root_cause": "验证用本地案例",
                        "action": "执行验证动作",
                        "tags": "vacuum,test",
                    }
                )
                matches = find_knowledge_cases("VAC-LOW-302", "ETCH")

        self.assertTrue(created.case_id.startswith("CASE-LOCAL-"))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].root_cause, "验证用本地案例")
        self.assertEqual(matches[0].tags, ["vacuum", "test"])


if __name__ == "__main__":
    unittest.main()
