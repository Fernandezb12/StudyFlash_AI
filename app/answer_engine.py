from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from app.llm_client import LLMClient, LLMClientError
from app.question_parser import ParsedQuestion
from app.utils import clamp, compact_multiline_text, ensure_sentence, normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AnswerResult:
    answer: str
    explanation: str
    confidence: float
    question_type: str
    source: str = "fallback"


class BaseAnswerEngine(ABC):
    @abstractmethod
    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        raise NotImplementedError


class LocalFallbackAnswerEngine(BaseAnswerEngine):
    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        question = parsed_question.question.lower()
        if parsed_question.question_type == "true_false":
            answer = "No concluyente"
            explanation = "El texto OCR no aporta suficiente certeza para decidir Verdadero o Falso."
            confidence = 0.28
        elif parsed_question.question_type == "multiple_choice":
            selected = self._pick_option(parsed_question.options)
            answer = selected or "No concluyente"
            explanation = (
                "Fallback local: se priorizó la opción más completa, pero la inferencia es limitada."
                if selected
                else "No se pudo inferir una opción fiable a partir del OCR."
            )
            confidence = 0.46 if selected else 0.18
        else:
            answer = self._summarize_open_answer(question)
            explanation = "Fallback local: respuesta muy breve basada solo en patrones del enunciado."
            confidence = 0.34 if answer != "No concluyente" else 0.18

        return self._normalize(
            AnswerResult(
                answer=answer,
                explanation=explanation,
                confidence=confidence,
                question_type=parsed_question.question_type,
                source="fallback",
            )
        )

    def _pick_option(self, options: Iterable[str]) -> str:
        ranked = sorted(options, key=lambda item: (len(item.split()), len(item)), reverse=True)
        return ranked[0] if ranked else ""

    def _summarize_open_answer(self, question: str) -> str:
        if not question:
            return "No concluyente"
        if any(token in question for token in ["define", "qué es", "que es"]):
            return "Definición breve requerida; conviene revisar el concepto central."
        if any(token in question for token in ["calcula", "resuelve", "hallar"]):
            return "No concluyente"
        if any(token in question for token in ["por qué", "porque"]):
            return "Explica la causa principal y su efecto inmediato."
        return "Resume la idea principal con una frase breve."

    def _normalize(self, result: AnswerResult) -> AnswerResult:
        result.answer = normalize_whitespace(result.answer) or "No concluyente"
        result.explanation = ensure_sentence(compact_multiline_text(result.explanation, max_lines=2))
        result.confidence = clamp(result.confidence)
        return result


class LLMAnswerEngine(BaseAnswerEngine):
    def __init__(self, client: LLMClient, min_confidence: float = 0.58, enabled: bool = True) -> None:
        self.client = client
        self.min_confidence = min_confidence
        self.enabled = enabled

    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        if not self.enabled:
            raise LLMClientError("LLM engine disabled by configuration.")

        if parsed_question.question_type == "multiple_choice":
            payload = self.client.answer_multiple_choice(parsed_question.question, parsed_question.options)
        elif parsed_question.question_type == "true_false":
            payload = self.client.answer_true_false(parsed_question.question)
        else:
            payload = self.client.answer_open(parsed_question.question)

        result = AnswerResult(
            answer=payload.answer,
            explanation=payload.explanation,
            confidence=payload.confidence,
            question_type=parsed_question.question_type,
            source=f"openai:{payload.model}",
        )
        return self._normalize_result(result, parsed_question.options)

    def _normalize_result(self, result: AnswerResult, options: list[str]) -> AnswerResult:
        result.answer = normalize_whitespace(result.answer) or "No concluyente"
        result.explanation = ensure_sentence(compact_multiline_text(result.explanation, max_lines=2))
        result.confidence = clamp(result.confidence)
        if options:
            matched = self._match_option(result.answer, options)
            if matched:
                result.answer = matched
        if result.confidence < self.min_confidence:
            result.answer = "No concluyente"
            result.explanation = "La confianza devuelta es baja; revisa el OCR o ajusta la región capturada."
        return result

    def _match_option(self, answer: str, options: list[str]) -> str:
        lowered = answer.lower()
        for option in options:
            if lowered == option.lower() or lowered in option.lower() or option.lower().startswith(lowered):
                return option
            label = option.split(maxsplit=1)[0].rstrip(').:-').lower()
            if lowered in {label, f"{label})", f"{label}."}:
                return option
        return answer


class StudyAnswerEngine(BaseAnswerEngine):
    def __init__(
        self,
        llm_engine: LLMAnswerEngine,
        fallback_engine: BaseAnswerEngine | None = None,
    ) -> None:
        self.llm_engine = llm_engine
        self.fallback_engine = fallback_engine or LocalFallbackAnswerEngine()

    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        try:
            result = self.llm_engine.answer(parsed_question, response_mode=response_mode)
            logger.info("Answer engine used source=%s confidence=%.2f", result.source, result.confidence)
            return result
        except Exception as exc:
            logger.warning("OpenAI answer failed; falling back locally: %s", exc)
            result = self.fallback_engine.answer(parsed_question, response_mode=response_mode)
            logger.info("Answer engine used source=%s confidence=%.2f", result.source, result.confidence)
            return result
