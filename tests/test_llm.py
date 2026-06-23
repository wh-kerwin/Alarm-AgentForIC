import os
import unittest
from unittest.mock import patch

from server.analyzer import analyze_alert
from server.llm import OpenAIResponsesProvider, get_explanation_provider


class LLMProviderTests(unittest.TestCase):
    def test_default_provider_is_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = get_explanation_provider()
            result = provider.explain(None, [], [])  # type: ignore[arg-type]

        self.assertEqual(result.status, "disabled")
        self.assertEqual(result.provider, "disabled")

    def test_reserved_provider_returns_unavailable(self):
        with patch.dict(os.environ, {"LLM_PROVIDER": "deepseek"}, clear=True):
            provider = get_explanation_provider()
            result = provider.explain(None, [], [])  # type: ignore[arg-type]

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.provider, "deepseek")

    def test_openai_without_key_degrades(self):
        provider = OpenAIResponsesProvider(api_key=None, model="test-model")
        with patch.dict(os.environ, {}, clear=True):
            result = provider.explain(None, [], [])  # type: ignore[arg-type]

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.provider, "openai")

    def test_analysis_includes_disabled_llm_explanation_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            result = analyze_alert("ALM-20260623-001", role="EE")

        self.assertEqual(result.llm_explanation.status, "disabled")
        self.assertIn("LLM", result.llm_explanation.summary)


if __name__ == "__main__":
    unittest.main()

