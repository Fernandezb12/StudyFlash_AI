from app.answer_engine import DemoAnswerEngine
from app.question_parser import ParsedQuestion


def test_demo_engine_multiple_choice() -> None:
    engine = DemoAnswerEngine()
    parsed = ParsedQuestion(
        question="¿Cuál opción parece más completa?",
        options=["A) Breve", "B) Mucho más detallada y completa"],
        question_type="multiple_choice",
        detected=True,
    )
    result = engine.answer(parsed, response_mode="normal")
    assert "B)" in result.answer
    assert result.question_type == "multiple_choice"
