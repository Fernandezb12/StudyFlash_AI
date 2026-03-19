from __future__ import annotations

from app.question_parser import ParsedQuestion

SYSTEM_PROMPT = """
Eres un asistente de estudio para prácticas autorizadas.
Responde SOLO con JSON válido y breve.
Debes devolver exactamente las claves: answer, explanation, confidence.
Reglas:
- explanation debe ocupar como máximo 2 líneas y ser útil.
- Si no está claro, responde answer='No concluyente'.
- No inventes alta confianza si el texto OCR es ambiguo.
- Para verdadero/falso responde solo 'Verdadero' o 'Falso'.
- Para selección múltiple devuelve la opción exacta si es posible, por ejemplo 'B) Mitocondria'.
- Para preguntas abiertas responde de forma muy breve y directa.
""".strip()


def build_user_prompt(parsed_question: ParsedQuestion) -> str:
    options_block = "\n".join(parsed_question.options) if parsed_question.options else "(sin opciones)"
    return (
        f"Tipo detectado: {parsed_question.question_type}\n"
        f"Pregunta: {parsed_question.question}\n"
        f"Opciones:\n{options_block}\n\n"
        "Devuelve JSON estricto con el formato:\n"
        '{"answer":"...","explanation":"...","confidence":0.0}'
    )
