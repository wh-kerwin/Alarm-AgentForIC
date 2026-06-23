"""Evidence-only LLM explanation providers.

The analyzer remains deterministic. LLM providers only rewrite already-collected
evidence into a clearer explanation and must not invent new root causes.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from typing import Protocol

from server.models import Alert, Event, LLMExplanation, RootCauseCandidate

DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


class ExplanationProvider(Protocol):
    provider_name: str

    def explain(self, alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> LLMExplanation:
        raise NotImplementedError


class DisabledExplanationProvider:
    provider_name = "disabled"

    def explain(self, alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> LLMExplanation:
        return LLMExplanation(
            status="disabled",
            provider=self.provider_name,
            model="none",
            summary="LLM 解释层未启用。当前结果来自规则、事件关联和知识案例。",
            evidence_notes=[],
            uncertainty=[],
            suggested_next_questions=[],
            safety_note=_safety_note(),
        )


class PlaceholderProvider:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def explain(self, alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> LLMExplanation:
        return LLMExplanation(
            status="unavailable",
            provider=self.provider_name,
            model="reserved",
            summary=f"{self.provider_name} provider interface is reserved but not implemented yet.",
            evidence_notes=[],
            uncertainty=["该 provider 尚未接入，不影响确定性 RCA 输出。"],
            suggested_next_questions=[],
            safety_note=_safety_note(),
        )


class OpenAIResponsesProvider:
    provider_name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout_seconds: int = 30):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.timeout_seconds = timeout_seconds

    def explain(self, alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> LLMExplanation:
        if not self.api_key:
            return LLMExplanation(
                status="unavailable",
                provider=self.provider_name,
                model=self.model,
                summary="OpenAI provider is configured but OPENAI_API_KEY is not set.",
                evidence_notes=[],
                uncertainty=["缺少 API key，已降级为确定性 RCA 输出。"],
                suggested_next_questions=[],
                safety_note=_safety_note(),
            )

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You explain semiconductor alert RCA results. Use only the evidence provided. "
                                "Do not invent root causes, data sources, measurements, SOPs, or actions. "
                                "If evidence is missing, state uncertainty. Return JSON only."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": json.dumps(_evidence_payload(alert, events, candidates), ensure_ascii=False)}],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "semiconductor_rca_explanation",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "summary": {"type": "string"},
                            "evidence_notes": {"type": "array", "items": {"type": "string"}},
                            "uncertainty": {"type": "array", "items": {"type": "string"}},
                            "suggested_next_questions": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["summary", "evidence_notes", "uncertainty", "suggested_next_questions"],
                    },
                    "strict": True,
                }
            },
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            parsed = _extract_json(body)
            return LLMExplanation(
                status="generated",
                provider=self.provider_name,
                model=self.model,
                summary=str(parsed["summary"]),
                evidence_notes=list(parsed["evidence_notes"]),
                uncertainty=list(parsed["uncertainty"]),
                suggested_next_questions=list(parsed["suggested_next_questions"]),
                safety_note=_safety_note(),
            )
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as error:
            return LLMExplanation(
                status="error",
                provider=self.provider_name,
                model=self.model,
                summary=f"OpenAI explanation failed: {error}",
                evidence_notes=[],
                uncertainty=["LLM 解释失败，已保留确定性 RCA 输出。"],
                suggested_next_questions=[],
                safety_note=_safety_note(),
            )


def get_explanation_provider() -> ExplanationProvider:
    provider = os.getenv("LLM_PROVIDER", "disabled").lower()
    if provider == "openai":
        return OpenAIResponsesProvider()
    if provider in {"deepseek", "qwen"}:
        return PlaceholderProvider(provider)
    return DisabledExplanationProvider()


def build_explanation(alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> LLMExplanation:
    return get_explanation_provider().explain(alert, events, candidates)


def _evidence_payload(alert: Alert, events: list[Event], candidates: list[RootCauseCandidate]) -> dict:
    return {
        "alert": asdict(alert),
        "events": [asdict(event) for event in events],
        "root_cause_candidates": [asdict(candidate) for candidate in candidates],
        "constraints": [
            "Only explain supplied evidence.",
            "Do not add root causes beyond candidates.",
            "Do not recommend high-risk automated actions.",
            "State missing evidence as uncertainty.",
        ],
    }


def _extract_json(body: dict) -> dict:
    if "output_text" in body:
        return json.loads(body["output_text"])
    for item in body.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return json.loads(content["text"])
    raise ValueError("No JSON text found in OpenAI response.")


def _safety_note() -> str:
    return "LLM 仅解释已收集证据，不新增根因；所有处置仍需授权工程师确认。"
