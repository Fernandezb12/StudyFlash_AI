from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.utils import chunk_lines, normalize_whitespace

OPTION_PATTERNS = [
    re.compile(r"^[A-D][\).:-]\s+(.+)$", re.IGNORECASE),
    re.compile(r"^\d+[\).:-]\s+(.+)$"),
    re.compile(r"^(verdadero|falso)\b", re.IGNORECASE),
]

QUESTION_HINTS = ["?", "cuál", "que", "qué", "como", "cómo", "por qué", "define", "selecciona"]


@dataclass(slots=True)
class ParsedQuestion:
    question: str
    options: list[str] = field(default_factory=list)
    question_type: str = "open_short"
    detected: bool = False
    source_text: str = ""


class QuestionParser:
    def parse(self, text: str) -> ParsedQuestion:
        normalized = normalize_whitespace(text)
        if not normalized:
            return ParsedQuestion(question="", source_text=text)

        lines = chunk_lines(text)
        options: list[str] = []
        question_lines: list[str] = []
        for line in lines:
            if any(pattern.match(line) for pattern in OPTION_PATTERNS):
                options.append(line)
            else:
                question_lines.append(line)

        question = normalize_whitespace(" ".join(question_lines)) or normalized
        detected = self._looks_like_question(question, options)
        question_type = self._classify(question, options)
        return ParsedQuestion(
            question=question,
            options=options,
            question_type=question_type,
            detected=detected,
            source_text=text,
        )

    def _looks_like_question(self, question: str, options: list[str]) -> bool:
        lowered = question.lower()
        return bool(options) or any(token in lowered for token in QUESTION_HINTS)

    def _classify(self, question: str, options: list[str]) -> str:
        lowered = question.lower()
        if options:
            if any(option.lower().startswith(("verdadero", "falso")) for option in options):
                return "true_false"
            return "multiple_choice"
        if len(question.split()) > 25:
            return "open_developed"
        return "open_short"
