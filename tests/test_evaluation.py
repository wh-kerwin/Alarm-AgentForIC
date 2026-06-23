import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server.evaluation import build_evaluation_metrics
from server.models import FeedbackRecord
from server.storage import save_audit_record, save_feedback


class EvaluationMetricsTests(unittest.TestCase):
    def test_metrics_use_sqlite_feedback_and_audit_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_url = f"sqlite:///{Path(tmp) / 'eval.db'}"
            with patch.dict("os.environ", {"DATABASE_URL": db_url, "LLM_PROVIDER": "disabled"}):
                save_feedback(
                    FeedbackRecord(
                        feedback_id="",
                        alert_id="ALM-20260623-001",
                        selected_cause_rank=1,
                        final_root_cause="test cause",
                        action_taken="test action",
                        recurrence_risk="low",
                        notes="",
                        created_at="2026-06-23T00:00:00Z",
                    )
                )
                save_audit_record("analysis_requested", "EE", "ALM-20260623-001", "analysis")

                metrics = build_evaluation_metrics("EE")

        self.assertGreaterEqual(metrics["summary"]["total_alerts"], 1)
        self.assertEqual(metrics["summary"]["feedback_records"], 1)
        self.assertEqual(metrics["summary"]["analysis_requests"], 1)
        self.assertEqual(metrics["quality"]["top1_adoption_rate"], 1.0)
        self.assertEqual(metrics["quality"]["top3_adoption_rate"], 1.0)
        self.assertIn("recurrence_risk", metrics["risk"])


if __name__ == "__main__":
    unittest.main()

