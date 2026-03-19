from app.answer_engine import AnswerResult, LLMAnswerEngine, LocalFallbackAnswerEngine
from app.question_parser import ParsedQuestion


class FakeLLMClient:
    def __init__(self, answer: str, explanation: str, confidence: float) -> None:
        self.answer = answer
        self.explanation = explanation
        self.confidence = confidence

    def answer_multiple_choice(self, question: str, options: list[str]):
        return type("Payload", (), {
            "answer": self.answer,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "model": "fake-model",
        })()

    def answer_open(self, question: str):
        return self.answer_multiple_choice(question, [])

    def answer_true_false(self, question: str):
        return self.answer_multiple_choice(question, [])



def test_fallback_engine_returns_non_conclusive_for_ambiguous_true_false() -> None:
    engine = LocalFallbackAnswerEngine()
    parsed = ParsedQuestion(question="La afirmación es correcta.", options=["Verdadero", "Falso"], question_type="true_false", detected=True)
    result = engine.answer(parsed)
    assert result.answer == "No concluyente"
    assert result.source == "fallback"



def test_llm_engine_normalizes_to_exact_option_and_compact_explanation() -> None:
    engine = LLMAnswerEngine(FakeLLMClient("b", "Explicación larga\ncon salto\nextra", 0.91), min_confidence=0.5)
    parsed = ParsedQuestion(
        question="¿Cuál opción es correcta?",
        options=["A) Roma", "B) París"],
        question_type="multiple_choice",
        detected=True,
    )
    result = engine.answer(parsed)
    assert result.answer == "B) París"
    assert result.explanation.count("\n") <= 1



def test_llm_engine_marks_low_confidence_as_non_conclusive() -> None:
    engine = LLMAnswerEngine(FakeLLMClient("B) París", "Puede ser", 0.2), min_confidence=0.5)
    parsed = ParsedQuestion(question="¿Capital?", options=["A) Roma", "B) París"], question_type="multiple_choice", detected=True)
    result = engine.answer(parsed)
    assert isinstance(result, AnswerResult)
    assert result.answer == "No concluyente"
