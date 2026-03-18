from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from app.question_parser import ParsedQuestion


@dataclass(slots=True)
class AnswerResult:
    answer: str
    explanation: str
    confidence: float
    question_type: str


class BaseAnswerEngine(ABC):
    @abstractmethod
    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        raise NotImplementedError


class DemoAnswerEngine(BaseAnswerEngine):
    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        question = parsed_question.question.lower()
        if parsed_question.question_type == "true_false":
            answer = "Verdadero" if "no" not in question else "Falso"
            explanation = "Respuesta heurística de demostración basada en negaciones detectadas."
            confidence = 0.52
        elif parsed_question.question_type == "multiple_choice":
            selected = self._pick_option(parsed_question.options)
            answer = selected or "No se pudo inferir una opción de forma fiable."
            explanation = "Modo demo: selecciona la opción más informativa por longitud y palabras clave."
            confidence = 0.46 if selected else 0.2
        else:
            answer = self._summarize_open_answer(parsed_question.question, response_mode)
            explanation = "Modo demo: genera una respuesta orientativa a partir de patrones del enunciado."
            confidence = 0.38

        return AnswerResult(
            answer=answer,
            explanation=self._expand_explanation(explanation, response_mode),
            confidence=confidence,
            question_type=parsed_question.question_type,
        )

    def _pick_option(self, options: Iterable[str]) -> str:
        ranked = sorted(options, key=lambda item: ("siempre" in item.lower(), len(item)), reverse=True)
        return ranked[0] if ranked else ""

    def _summarize_open_answer(self, question: str, response_mode: str) -> str:
        starters = {
            "breve": "Respuesta breve sugerida:",
            "normal": "Respuesta sugerida:",
            "explicativa": "Respuesta desarrollada sugerida:",
        }
        prefix = starters.get(response_mode, starters["normal"])
        if "define" in question.lower():
            body = "presenta una definición clara, una idea central y un ejemplo simple"
        elif "por qué" in question.lower():
            body = "explica la causa principal, su efecto y una consecuencia relevante"
        else:
            body = "resume el concepto principal y añade el dato más importante del enunciado"
        return f"{prefix} {body}."

    def _expand_explanation(self, explanation: str, response_mode: str) -> str:
        if response_mode == "breve":
            return explanation
        if response_mode == "explicativa":
            return f"{explanation} Revisa el texto OCR antes de usarla como apoyo de estudio."
        return f"{explanation} Conviene validar la captura y el contexto académico."


class LLMAnswerEngine(BaseAnswerEngine):
    def __init__(self, client: object | None = None) -> None:
        self.client = client

    def answer(self, parsed_question: ParsedQuestion, response_mode: str = "normal") -> AnswerResult:
        raise NotImplementedError(
            "Integra aquí tu proveedor LLM preferido manteniendo la interfaz AnswerResult."
        )
