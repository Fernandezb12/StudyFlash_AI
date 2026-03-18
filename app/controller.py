from __future__ import annotations

import logging
from typing import Callable

from app.answer_engine import BaseAnswerEngine, DemoAnswerEngine
from app.config import ConfigStore
from app.history_store import HistoryStore
from app.ocr_engine import OCREngine
from app.popup_window import PopupWindow
from app.question_parser import ParsedQuestion, QuestionParser
from app.screen_capture import ScreenCaptureService
from app.startup_manager import StartupManager

logger = logging.getLogger(__name__)


class StudyFlashController:
    def __init__(
        self,
        config_store: ConfigStore,
        history_store: HistoryStore,
        popup_window: PopupWindow,
        screen_capture: ScreenCaptureService,
        parser: QuestionParser,
        answer_engine: BaseAnswerEngine | None = None,
        startup_manager: StartupManager | None = None,
        notifier: Callable[[str, str], None] | None = None,
    ) -> None:
        self.config_store = config_store
        self.config = config_store.load()
        self.history_store = history_store
        self.popup_window = popup_window
        self.screen_capture = screen_capture
        self.parser = parser
        self.answer_engine = answer_engine or DemoAnswerEngine()
        self.startup_manager = startup_manager or StartupManager()
        self.notifier = notifier or (lambda title, message: None)
        self.ocr_engine = OCREngine(self.config.ocr_language, self.config.tesseract_cmd)

    def reload_config(self) -> None:
        self.config = self.config_store.load()
        self.history_store.limit = self.config.history_limit
        self.ocr_engine = OCREngine(self.config.ocr_language, self.config.tesseract_cmd)

    def save_settings(self, payload: dict) -> None:
        self.config_store.update(**payload)
        self.reload_config()
        self.startup_manager.set_enabled(self.config.start_with_windows)
        self.notifier("StudyFlash AI", "Configuración guardada correctamente.")

    def process_capture(self) -> tuple[ParsedQuestion, object]:
        logger.info("Starting capture workflow")
        if self.config.debug_mode and self.config.debug_image_path:
            capture = self.screen_capture.load_debug_image(self.config.debug_image_path)
        else:
            capture = self.screen_capture.capture(
                mode=self.config.capture.mode,
                region=self.config.capture.region,
                monitor_index=self.config.capture.monitor_index,
            )
        ocr_result = self.ocr_engine.extract_text(capture.image)
        parsed = self.parser.parse(ocr_result.raw_text)
        if not parsed.detected:
            parsed = ParsedQuestion(
                question=ocr_result.text or "No se detectó texto utilizable en la captura.",
                options=[],
                question_type="unknown",
                detected=False,
                source_text=ocr_result.raw_text,
            )
        answer = self.answer_engine.answer(parsed, self.config.response_mode)
        self.history_store.add_entry(
            question=parsed.question,
            answer=answer.answer,
            explanation=answer.explanation,
            confidence=answer.confidence,
            question_type=answer.question_type,
        )
        self.popup_window.show_result(parsed, answer)
        return parsed, answer

    def run_ocr_test(self) -> tuple[ParsedQuestion, object]:
        return self.process_capture()

    def recent_history_text(self) -> str:
        entries = self.history_store.load()
        if not entries:
            return "No hay historial reciente."
        rows = []
        for entry in entries[:10]:
            rows.append(f"• {entry.timestamp} | {entry.question[:80]} -> {entry.answer[:60]}")
        return "\n".join(rows)
