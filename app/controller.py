from __future__ import annotations

import logging
from typing import Callable

from app.answer_engine import LLMAnswerEngine, StudyAnswerEngine
from app.config import ConfigStore
from app.history_store import HistoryStore
from app.llm_client import LLMClient
from app.ocr_engine import OCREngine
from app.popup_window import PopupWindow
from app.question_parser import ParsedQuestion, QuestionParser
from app.screen_capture import ScreenCaptureService
from app.startup_manager import StartupManager
from app.utils import LogPreviewFormatter

logger = logging.getLogger(__name__)


class StudyFlashController:
    def __init__(
        self,
        config_store: ConfigStore,
        history_store: HistoryStore,
        popup_window: PopupWindow,
        screen_capture: ScreenCaptureService,
        parser: QuestionParser,
        answer_engine: StudyAnswerEngine | None = None,
        startup_manager: StartupManager | None = None,
        notifier: Callable[[str, str], None] | None = None,
    ) -> None:
        self.config_store = config_store
        self.config = config_store.load()
        self.history_store = history_store
        self.popup_window = popup_window
        self.screen_capture = screen_capture
        self.parser = parser
        self.startup_manager = startup_manager or StartupManager()
        self.notifier = notifier or (lambda title, message: None)
        self.answer_engine = answer_engine or self._build_answer_engine()
        self.ocr_engine = self._build_ocr_engine()
        self._apply_popup_preferences()

    def _build_ocr_engine(self) -> OCREngine:
        return OCREngine(
            language=self.config.ocr_language,
            tesseract_cmd=self.config.tesseract_cmd,
            psm=self.config.tesseract_psm,
        )

    def _build_answer_engine(self) -> StudyAnswerEngine:
        llm_client = LLMClient(
            api_key_env=self.config.openai_api_key_env,
            model=self.config.openai_model,
            timeout_seconds=self.config.openai_timeout_seconds,
            enabled=self.config.openai_enabled and self.config.internet_enabled,
        )
        llm_engine = LLMAnswerEngine(
            client=llm_client,
            min_confidence=self.config.min_confidence,
            enabled=self.config.openai_enabled and self.config.internet_enabled,
        )
        return StudyAnswerEngine(llm_engine=llm_engine)

    def _apply_popup_preferences(self) -> None:
        self.popup_window.apply_preferences(
            show_question=self.config.show_question,
            compact_popup=self.config.compact_popup,
            width=self.config.popup_width,
            height=self.config.popup_height,
            always_on_top=self.config.always_on_top,
        )

    def reload_config(self) -> None:
        self.config = self.config_store.load()
        self.history_store.limit = self.config.history_limit
        self.ocr_engine = self._build_ocr_engine()
        self.answer_engine = self._build_answer_engine()
        self._apply_popup_preferences()

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
        logger.info("Capture source=%s", capture.source)

        ocr_result = self.ocr_engine.extract_text(capture.image)
        logger.info("OCR raw preview=%s", LogPreviewFormatter.preview(ocr_result.raw_text))
        logger.info("OCR cleaned preview=%s", LogPreviewFormatter.preview(ocr_result.text))

        parsed = self.parser.parse(ocr_result.raw_text)
        logger.info("Parsed question=%s", LogPreviewFormatter.preview(parsed.question))
        logger.info("Parsed options=%s", parsed.options)
        logger.info("Parsed question_type=%s detected=%s", parsed.question_type, parsed.detected)

        if not parsed.detected:
            parsed = ParsedQuestion(
                question=ocr_result.text or "No se detectó texto utilizable en la captura.",
                options=[],
                question_type="unknown",
                detected=False,
                source_text=ocr_result.raw_text,
                cleaned_text=ocr_result.text,
            )

        answer = self.answer_engine.answer(parsed, self.config.response_mode)
        logger.info("Answer source=%s confidence=%.2f answer=%s", answer.source, answer.confidence, answer.answer)
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
            rows.append(
                f"• {entry.timestamp} | [{entry.question_type}] {entry.question[:70]} -> {entry.answer[:50]}"
            )
        return "\n".join(rows)
