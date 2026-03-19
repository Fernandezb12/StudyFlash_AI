from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.utils import chunk_lines, normalize_whitespace, unique_preserve_order

OPTION_START_RE = re.compile(r"^(?P<label>(?:[A-H]|\d+))[\).:-]\s*(?P<body>.+)$", re.IGNORECASE)
TRUE_FALSE_RE = re.compile(r"^(verdadero|falso)\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
QUESTION_HINTS = [
    "?",
    "cuál",
    "que",
    "qué",
    "como",
    "cómo",
    "por qué",
    "selecciona",
    "marca",
    "elige",
    "indica",
    "define",
    "resuelve",
    "calcula",
]
NOISE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"^(siguiente|anterior|continuar|finalizar|mostrar solución|mostrar respuesta)$",
        r"^(inicio|menú|menu|preguntas?|simulacro|banco de preguntas|tiempo restante|progreso)$",
        r"^(volver|confirmar|revisar|resolver más tarde|saltar)$",
        r"^(www\.|http)",
        r"^(pregunta\s+\d+\s+de\s+\d+)$",
        r"^(copyright|política de privacidad|términos y condiciones)",
    ]
]


@dataclass(slots=True)
class ParsedQuestion:
    question: str
    options: list[str] = field(default_factory=list)
    question_type: str = "open_short"
    detected: bool = False
    source_text: str = ""
    cleaned_text: str = ""


class QuestionParser:
    def clean_exam_text(self, text: str) -> str:
        cleaned_lines: list[str] = []
        for raw_line in chunk_lines(text):
            line = self._normalize_line(raw_line)
            if not line:
                continue
            if self._is_noise(line):
                continue
            cleaned_lines.append(line)
        return "\n".join(unique_preserve_order(cleaned_lines))

    def parse(self, text: str) -> ParsedQuestion:
        cleaned_text = self.clean_exam_text(text)
        if not cleaned_text:
            return ParsedQuestion(question="", source_text=text, cleaned_text="")

        lines = chunk_lines(cleaned_text)
        question_lines: list[str] = []
        option_lines: list[str] = []
        in_options = False

        for line in lines:
            if self._is_option_start(line) or (in_options and self._looks_like_option_continuation(line)):
                option_lines.append(line)
                in_options = True
                continue
            if not in_options:
                question_lines.append(line)

        options = self._merge_option_lines(option_lines)
        if not question_lines and options:
            question_lines.append(lines[0])

        question = normalize_whitespace(" ".join(question_lines))
        if not question and lines:
            question = normalize_whitespace(lines[0])
        detected = self._looks_like_question(question, options)
        question_type = self._classify(question, options)
        return ParsedQuestion(
            question=question,
            options=options,
            question_type=question_type,
            detected=detected,
            source_text=text,
            cleaned_text=cleaned_text,
        )

    def _normalize_line(self, line: str) -> str:
        line = URL_RE.sub("", line)
        line = re.sub(r"[\u200b\ufeff]", "", line)
        line = re.sub(r"\s+", " ", line).strip(" -–•\t")
        return line.strip()

    def _is_noise(self, line: str) -> bool:
        lowered = line.lower()
        if len(lowered) <= 1:
            return True
        if any(pattern.match(lowered) for pattern in NOISE_PATTERNS):
            return True
        if lowered in {"a", "b", "c", "d"}:
            return True
        if re.fullmatch(r"\d{1,2}:\d{2}", lowered):
            return True
        return False

    def _is_option_start(self, line: str) -> bool:
        return bool(OPTION_START_RE.match(line) or TRUE_FALSE_RE.match(line))

    def _looks_like_option_continuation(self, line: str) -> bool:
        lowered = line.lower()
        if self._is_option_start(line):
            return False
        if any(token in lowered for token in QUESTION_HINTS):
            return False
        return len(line.split()) >= 2

    def _merge_option_lines(self, lines: list[str]) -> list[str]:
        merged: list[str] = []
        current = ""
        for line in lines:
            if self._is_option_start(line):
                if current:
                    merged.append(normalize_whitespace(current))
                current = line
            elif current:
                current = f"{current} {line}"
        if current:
            merged.append(normalize_whitespace(current))
        return merged

    def _looks_like_question(self, question: str, options: list[str]) -> bool:
        lowered = question.lower()
        if bool(options):
            return True
        return any(token in lowered for token in QUESTION_HINTS)

    def _classify(self, question: str, options: list[str]) -> str:
        lowered = question.lower()
        lowered_options = [option.lower() for option in options]
        if len(options) >= 2:
            if any(option.startswith("verdadero") or option.startswith("falso") for option in lowered_options):
                return "true_false"
            return "multiple_choice"
        if "verdadero o falso" in lowered or "verdadero/falso" in lowered:
            return "true_false"
        if len(question.split()) > 28:
            return "open_developed"
        return "open_short"
