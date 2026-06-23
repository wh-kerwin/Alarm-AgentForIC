import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.analyzer import analyze_alert, get_alert, list_alerts


class AnalyzerTests(unittest.TestCase):
    def test_lists_sample_alerts(self):
        alerts = list_alerts()
        self.assertGreaterEqual(len(alerts), 3)
        self.assertEqual(alerts[0].alert_id, "ALM-20260623-001")

    def test_get_alert_returns_none_for_unknown_id(self):
        self.assertIsNone(get_alert("missing"))

    def test_analysis_contains_ranked_candidates_and_evidence(self):
        result = analyze_alert("ALM-20260623-001")
        self.assertEqual(result.alert_id, "ALM-20260623-001")
        self.assertEqual(len(result.root_cause_candidates), 3)
        self.assertEqual(result.root_cause_candidates[0].rank, 1)
        self.assertGreaterEqual(len(result.root_cause_candidates[0].evidence), 1)
        self.assertTrue(result.escalation["required"])
        self.assertEqual(result.collection_status.policy.policy_id, "POLICY-ETCH-VAC")

    def test_mock_equipment_alarm_uses_generic_equipment_analysis(self):
        result = analyze_alert("ALM-MOCK-9002")

        self.assertEqual(result.alert_id, "ALM-MOCK-9002")
        self.assertEqual(result.collection_status.policy.policy_id, "POLICY-ETCH-RF")
        self.assertEqual(len(result.root_cause_candidates), 3)
        self.assertIn("CMMS", result.collection_status.missing_optional_sources)

    def test_unknown_alert_raises_key_error(self):
        with self.assertRaises(KeyError):
            analyze_alert("missing")


if __name__ == "__main__":
    unittest.main()
