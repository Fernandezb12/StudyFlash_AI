from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.answer_engine import AnswerResult
from app.question_parser import ParsedQuestion


class PopupWindow(QDialog):
    def __init__(self, width: int = 350, height: int = 170, always_on_top: bool = True) -> None:
        super().__init__()
        self._show_question = False
        self._compact_popup = True
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
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("StudyFlash AI")
        self.title_label.setObjectName("titleLabel")

        self.question_label = QLabel("")
        self.question_label.setObjectName("questionLabel")
        self.question_label.setWordWrap(True)
        self.question_label.hide()

        self.answer_title = QLabel("Respuesta")
        self.answer_title.setObjectName("sectionLabel")
        self.answer_label = QLabel("—")
        self.answer_label.setObjectName("answerLabel")
        self.answer_label.setWordWrap(True)
        self.answer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.explanation_title = QLabel("Explicación")
        self.explanation_title.setObjectName("sectionLabel")
        self.explanation_label = QLabel("—")
        self.explanation_label.setObjectName("explanationLabel")
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.accept)
        button_row.addWidget(self.accept_button)

        layout.addWidget(self.title_label)
        layout.addWidget(self.question_label)
        layout.addWidget(self.answer_title)
        layout.addWidget(self.answer_label)
        layout.addWidget(self.explanation_title)
        layout.addWidget(self.explanation_label)
        layout.addLayout(button_row)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: #ffffff;
                color: #0f172a;
                border: 1px solid #dbe3ef;
                border-radius: 12px;
            }
            #titleLabel {
                font-size: 14px;
                font-weight: 700;
                color: #111827;
                padding-bottom: 2px;
            }
            #sectionLabel {
                font-size: 11px;
                font-weight: 700;
                color: #475569;
                margin-top: 2px;
            }
            #questionLabel {
                font-size: 11px;
                color: #334155;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 8px;
            }
            #answerLabel {
                font-size: 15px;
                font-weight: 700;
                color: #0f172a;
            }
            #explanationLabel {
                font-size: 12px;
                color: #334155;
            }
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                min-width: 92px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            """
        )

    def apply_preferences(
        self,
        *,
        show_question: bool,
        compact_popup: bool,
        width: int,
        height: int,
        always_on_top: bool,
    ) -> None:
        self._show_question = show_question
        self._compact_popup = compact_popup
        self.question_label.setVisible(show_question)
        self.resize(width, height)
        flags = Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setFixedSize(width, height)
        self._apply_spacing_profile()

    def _apply_spacing_profile(self) -> None:
        layout = self.layout()
        if self._compact_popup:
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(6)
        else:
            layout.setContentsMargins(18, 16, 18, 16)
            layout.setSpacing(10)

    def show_result(self, parsed_question: ParsedQuestion, answer_result: AnswerResult) -> None:
        self.question_label.setText(parsed_question.question or "No se detectó una pregunta clara.")
        self.answer_label.setText(answer_result.answer or "No concluyente")
        self.explanation_label.setText(answer_result.explanation or "Información insuficiente.")
        self.question_label.setVisible(self._show_question)
        self.show()
        self.raise_()
        self.activateWindow()
