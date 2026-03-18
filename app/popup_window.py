from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.answer_engine import AnswerResult
from app.question_parser import ParsedQuestion


class InfoCard(QFrame):
    def __init__(self, title: str, body: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("infoCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        body_label = QLabel(body or "—")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(title_label)
        layout.addWidget(body_label)


class PopupWindow(QDialog):
    def __init__(self, width: int = 430, height: int = 360, always_on_top: bool = True) -> None:
        super().__init__()
        self.setWindowTitle("StudyFlash AI")
        flags = Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setModal(False)
        self.resize(width, height)
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.question_card = InfoCard("Pregunta detectada", "")
        self.answer_card = InfoCard("Respuesta", "")
        self.explanation_card = InfoCard("Explicación", "")
        self.confidence_label = QLabel("Confianza: —")
        self.confidence_label.setObjectName("confidenceLabel")

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.accept)
        button_row.addWidget(self.accept_button)

        layout.addWidget(self.question_card)
        layout.addWidget(self.answer_card)
        layout.addWidget(self.explanation_card)
        layout.addWidget(self.confidence_label)
        layout.addLayout(button_row)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: #121826;
                color: #f3f4f6;
            }
            #infoCard {
                background: #1f2937;
                border: 1px solid #374151;
                border-radius: 12px;
            }
            #cardTitle {
                font-size: 13px;
                font-weight: 700;
                color: #93c5fd;
            }
            #confidenceLabel {
                color: #d1d5db;
                padding-left: 4px;
            }
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 110px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            """
        )

    def show_result(self, parsed_question: ParsedQuestion, answer_result: AnswerResult) -> None:
        self._set_card_text(self.question_card, parsed_question.question or "No se detectó una pregunta clara.")
        self._set_card_text(self.answer_card, answer_result.answer)
        self._set_card_text(self.explanation_card, answer_result.explanation)
        self.confidence_label.setText(
            f"Confianza: {answer_result.confidence:.0%} · Tipo: {answer_result.question_type}"
        )
        self.show()
        self.raise_()
        self.activateWindow()

    def _set_card_text(self, card: InfoCard, value: str) -> None:
        label = card.layout().itemAt(1).widget()
        label.setText(value)
