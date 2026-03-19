from app.question_parser import QuestionParser



def test_multiple_choice_detection_with_noise_and_multiline_options() -> None:
    parser = QuestionParser()
    parsed = parser.parse(
        """
        Pregunta 4 de 20
        https://example.com/mock-test
        ¿Cuál es la capital de Francia?
        A) Madrid
        B) París, ciudad
        con mayor población
        C) Roma
        Siguiente
        D) Berlín
        """
    )
    assert parsed.detected is True
    assert parsed.question_type == "multiple_choice"
    assert parsed.question == "¿Cuál es la capital de Francia?"
    assert parsed.options[1] == "B) París, ciudad con mayor población"
    assert len(parsed.options) == 4



def test_true_false_detection() -> None:
    parser = QuestionParser()
    parsed = parser.parse("Indica si la afirmación es verdadera o falsa.\nVerdadero\nFalso")
    assert parsed.detected is True
    assert parsed.question_type == "true_false"
