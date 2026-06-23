import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server.analyzer import analyze_alert
from server.roles import get_role_policy
from server.storage import list_audit_records, save_audit_record


class RoleSafetyTests(unittest.TestCase):
    def test_role_policy_loads_known_role(self):
        policy = get_role_policy("PE")

        self.assertEqual(policy.role, "PE")
        self.assertIn("modify_recipe_without_review", policy.blocked_actions)

    def test_analysis_includes_role_context_and_safety_gate(self):
        result = analyze_alert("ALM-20260623-001", role="EE")

        self.assertEqual(result.role_context["role"], "EE")
        self.assertTrue(result.role_context["is_owner_role"])
        self.assertEqual(result.safety_gate["mode"], "advisory_only")
        self.assertIn("release_lot", result.safety_gate["high_risk_actions"])

    def test_audit_records_can_be_filtered_by_alert(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_url = f"sqlite:///{Path(tmp) / 'test.db'}"
            with patch.dict("os.environ", {"DATABASE_URL": db_url}):
                save_audit_record("analysis_requested", "EE", "ALM-1", "Generated analysis")
                save_audit_record("analysis_requested", "PE", "ALM-2", "Generated analysis")

                rows = list_audit_records("ALM-1")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["role"], "EE")


if __name__ == "__main__":
    unittest.main()
