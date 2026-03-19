from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from app.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.question_parser import ParsedQuestion
from app.utils import clamp, compact_multiline_text, ensure_sentence, normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LLMClientResult:
    answer: str
    explanation: str
    confidence: float
    model: str


class LLMClientError(RuntimeError):
    pass


class LLMClient:
    def __init__(
        self,
        api_key_env: str = "OPENAI_API_KEY",
        model: str = "gpt-4o-mini",
        timeout_seconds: float = 20.0,
        enabled: bool = True,
    ) -> None:
        self.api_key_env = api_key_env
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled
        self._client: Any | None = None

    def is_available(self) -> bool:
        return self.enabled and bool(os.getenv(self.api_key_env))

    def answer_multiple_choice(self, question: str, options: list[str]) -> LLMClientResult:
        parsed = ParsedQuestion(question=question, options=options, question_type="multiple_choice", detected=True)
        return self._request(parsed)

    def answer_open(self, question: str) -> LLMClientResult:
        parsed = ParsedQuestion(question=question, options=[], question_type="open_short", detected=True)
        return self._request(parsed)

    def answer_true_false(self, question: str) -> LLMClientResult:
        parsed = ParsedQuestion(question=question, options=["Verdadero", "Falso"], question_type="true_false", detected=True)
        return self._request(parsed)

    def _build_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = os.getenv(self.api_key_env)
        if not self.enabled:
            raise LLMClientError("OpenAI integration disabled by configuration.")
        if not api_key:
            raise LLMClientError(f"Environment variable {self.api_key_env} is not set.")

        openai_module = import_module("openai")
        openai_client = getattr(openai_module, "OpenAI")
        self._client = openai_client(api_key=api_key, timeout=float(self.timeout_seconds), max_retries=1)
        return self._client

    def _request(self, parsed_question: ParsedQuestion) -> LLMClientResult:
        client = self._build_client()
        prompt = build_user_prompt(parsed_question)
        logger.debug("Sending question to OpenAI model=%s type=%s", self.model, parsed_question.question_type)

        try:
            response = client.responses.create(
                model=self.model,
                store=False,
                instructions=SYSTEM_PROMPT,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "studyflash_answer",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "answer": {"type": "string"},
                                "explanation": {"type": "string"},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["answer", "explanation", "confidence"],
                            "additionalProperties": False,
                        },
                    }
                },
            )
            if not getattr(response, "output_text", ""):
                raise LLMClientError("OpenAI returned an empty structured response.")
            payload = json.loads(response.output_text)
            return self._normalize_payload(payload)
        except Exception as exc:
            raise LLMClientError(f"OpenAI request failed: {exc}") from exc

    def _normalize_payload(self, payload: dict[str, Any]) -> LLMClientResult:
        answer = normalize_whitespace(str(payload.get("answer", "No concluyente"))) or "No concluyente"
        explanation = compact_multiline_text(str(payload.get("explanation", "Información insuficiente.")), max_lines=2)
        explanation = ensure_sentence(explanation) if explanation else "Información insuficiente."
        confidence = clamp(float(payload.get("confidence", 0.0)))
        return LLMClientResult(
            answer=answer,
            explanation=explanation,
            confidence=confidence,
            model=self.model,
        )
