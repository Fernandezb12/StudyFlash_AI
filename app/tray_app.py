from __future__ import annotations

import logging

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QStyle

from app.config import ConfigStore
from app.controller import StudyFlashController
from app.hotkeys import GlobalHotkeyManager
from app.popup_window import PopupWindow
from app.settings_window import SettingsWindow
from app.utils import resource_path

logger = logging.getLogger(__name__)


class StudyFlashTrayApp(QObject):
    def __init__(
        self,
        qt_app: QApplication,
        controller: StudyFlashController,
        config_store: ConfigStore,
        hotkeys: GlobalHotkeyManager,
        popup_window: PopupWindow,
    ) -> None:
        super().__init__()
        self.qt_app = qt_app
        self.controller = controller
        self.config_store = config_store
        self.hotkeys = hotkeys
        self.popup_window = popup_window
        self.tray_icon = QSystemTrayIcon(self._load_icon(), self)
        self.tray_icon.setToolTip("StudyFlash AI")
        self.menu = QMenu()
        self.settings_window: SettingsWindow | None = None
        self.toggle_hotkey_action: QAction | None = None
        self.startup_action: QAction | None = None
        self._build_menu()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._handle_activation)

    def start(self) -> None:
        self.tray_icon.show()
        self._sync_hotkey()
        self.controller.startup_manager.set_enabled(self.controller.config.start_with_windows)
        self.notify("StudyFlash AI", "Aplicación iniciada en segundo plano.")

    def notify(self, title: str, message: str) -> None:
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2500)

    def _load_icon(self) -> QIcon:
        icon = QIcon(resource_path("assets", "icon.png"))
        if icon.isNull():
            icon = self.qt_app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        return icon

    def _build_menu(self) -> None:
        open_settings = QAction("Abrir configuración", self)
        open_settings.triggered.connect(self.open_settings)

        self.toggle_hotkey_action = QAction("Desactivar hotkey", self)
        self.toggle_hotkey_action.triggered.connect(self.toggle_hotkey)

        test_ocr = QAction("Ejecutar prueba OCR", self)
        test_ocr.triggered.connect(self._safe_process_capture)

        show_history = QAction("Ver historial reciente", self)
        show_history.triggered.connect(self.show_history)

        self.startup_action = QAction("Iniciar con Windows", self)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.controller.config.start_with_windows)
        self.startup_action.triggered.connect(self.toggle_startup)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.exit_app)

        self.menu.addAction(open_settings)
        self.menu.addAction(self.toggle_hotkey_action)
        self.menu.addAction(test_ocr)
        self.menu.addAction(show_history)
        self.menu.addSeparator()
        self.menu.addAction(self.startup_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)

    def _handle_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_settings()

    def _safe_process_capture(self) -> None:
        try:
            self.controller.process_capture()
        except Exception as exc:
            logger.exception("Capture workflow failed")
            self.notify("StudyFlash AI", f"No se pudo procesar la captura: {exc}")

    def _sync_hotkey(self) -> None:
        config = self.controller.config
        if config.hotkey_enabled:
            self.hotkeys.register(config.hotkey, self._safe_process_capture)
            if self.toggle_hotkey_action:
                self.toggle_hotkey_action.setText("Desactivar hotkey")
        else:
            self.hotkeys.unregister()
            if self.toggle_hotkey_action:
                self.toggle_hotkey_action.setText("Activar hotkey")

    def open_settings(self) -> None:
        self.settings_window = SettingsWindow(self.controller.config)
        self.settings_window.settings_saved.connect(self._apply_settings)
        self.settings_window.exec()

    def _apply_settings(self, payload: dict) -> None:
        self.controller.save_settings(payload)
        if self.startup_action:
            self.startup_action.setChecked(self.controller.config.start_with_windows)
        self._sync_hotkey()

    def toggle_hotkey(self) -> None:
        new_state = not self.controller.config.hotkey_enabled
        self.config_store.update(hotkey_enabled=new_state)
        self.controller.reload_config()
        self._sync_hotkey()
        state_text = "activada" if new_state else "desactivada"
        self.notify("StudyFlash AI", f"Hotkey {state_text}.")

    def toggle_startup(self) -> None:
        new_state = bool(self.startup_action.isChecked()) if self.startup_action else False
        self.config_store.update(start_with_windows=new_state)
        self.controller.reload_config()
        self.controller.startup_manager.set_enabled(new_state)
        self.notify("StudyFlash AI", "Preferencia de inicio automático actualizada.")

    def show_history(self) -> None:
        QMessageBox.information(None, "Historial reciente", self.controller.recent_history_text())

    def exit_app(self) -> None:
        self.hotkeys.unregister()
        self.tray_icon.hide()
        self.qt_app.quit()