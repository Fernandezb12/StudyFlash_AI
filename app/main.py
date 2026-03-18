from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.config import ConfigStore
from app.controller import StudyFlashController
from app.history_store import HistoryStore
from app.hotkeys import GlobalHotkeyManager
from app.popup_window import PopupWindow
from app.question_parser import QuestionParser
from app.screen_capture import ScreenCaptureService
from app.tray_app import StudyFlashTrayApp
from app.utils import ensure_windows_app_user_model_id, setup_logging


def build_application() -> tuple[QApplication, StudyFlashTrayApp]:
    ensure_windows_app_user_model_id()
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    config_store = ConfigStore()
    config = config_store.load()
    setup_logging(config.debug_mode)

    popup = PopupWindow(width=config.popup_width, height=config.popup_height, always_on_top=config.always_on_top)
    controller = StudyFlashController(
        config_store=config_store,
        history_store=HistoryStore(limit=config.history_limit),
        popup_window=popup,
        screen_capture=ScreenCaptureService(),
        parser=QuestionParser(),
    )
    tray_app = StudyFlashTrayApp(
        qt_app=qt_app,
        controller=controller,
        config_store=config_store,
        hotkeys=GlobalHotkeyManager(),
        popup_window=popup,
    )
    controller.notifier = tray_app.notify
    return qt_app, tray_app


def main() -> int:
    qt_app, tray_app = build_application()
    tray_app.start()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
