from app.question_parser import QuestionParser


def test_multiple_choice_detection() -> None:
    parser = QuestionParser()
    parsed = parser.parse(
        "¿Cuál es la capital de Francia?\nA) Madrid\nB) París\nC) Roma\nD) Berlín"
    )
    assert parsed.detected is True
    assert parsed.question_type == "multiple_choice"
    assert len(parsed.options) == 4


def test_open_question_detection() -> None:
    parser = QuestionParser()
    parsed = parser.parse("Define fotosíntesis y menciona su importancia biológica.")
    assert parsed.detected is True
    assert parsed.question_type == "open_short"
