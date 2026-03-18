from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.config import AppConfig


class SettingsWindow(QDialog):
    settings_saved = Signal(dict)

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.setWindowTitle("Configuración · StudyFlash AI")
        self.resize(460, 360)
        self._build_ui(config)

    def _build_ui(self, config: AppConfig) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.hotkey_input = QLineEdit(config.hotkey)
        self.hotkey_enabled = QCheckBox("Hotkey activa")
        self.hotkey_enabled.setChecked(config.hotkey_enabled)

        self.response_mode = QComboBox()
        self.response_mode.addItems(["breve", "normal", "explicativa"])
        self.response_mode.setCurrentText(config.response_mode)

        self.capture_mode = QComboBox()
        self.capture_mode.addItems(["full_screen", "region"])
        self.capture_mode.setCurrentText(config.capture.mode)

        self.region_input = QLineEdit(",".join(str(value) for value in config.capture.region))
        self.monitor_input = QSpinBox()
        self.monitor_input.setMinimum(1)
        self.monitor_input.setValue(config.capture.monitor_index)

        self.ocr_language_input = QLineEdit(config.ocr_language)
        self.tesseract_path_input = QLineEdit(config.tesseract_cmd)
        browse_button = QPushButton("Buscar…")
        browse_button.clicked.connect(self._choose_tesseract_path)
        tesseract_row = QHBoxLayout()
        tesseract_row.addWidget(self.tesseract_path_input)
        tesseract_row.addWidget(browse_button)

        self.start_with_windows = QCheckBox("Iniciar con Windows")
        self.start_with_windows.setChecked(config.start_with_windows)

        self.debug_mode = QCheckBox("Usar imagen de prueba")
        self.debug_mode.setChecked(config.debug_mode)
        self.debug_image_path = QLineEdit(config.debug_image_path)

        form.addRow("Hotkey global", self.hotkey_input)
        form.addRow("Estado de hotkey", self.hotkey_enabled)
        form.addRow("Modo de respuesta", self.response_mode)
        form.addRow("Modo de captura", self.capture_mode)
        form.addRow("Región (x,y,w,h)", self.region_input)
        form.addRow("Monitor", self.monitor_input)
        form.addRow("Idioma OCR", self.ocr_language_input)
        form.addRow("Ruta de Tesseract", tesseract_row)
        form.addRow("Inicio automático", self.start_with_windows)
        form.addRow("Depuración OCR", self.debug_mode)
        form.addRow("Imagen de prueba", self.debug_image_path)

        info = QLabel("Usa formatos como ctrl+x o alt+shift+s para la hotkey global.")
        info.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancelar")
        save_button = QPushButton("Guardar")
        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self._emit_settings)
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addStretch(1)
        layout.addLayout(button_row)

    def _choose_tesseract_path(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Selecciona tesseract.exe")
        if selected:
            self.tesseract_path_input.setText(selected)

    def _emit_settings(self) -> None:
        region_values = [segment.strip() for segment in self.region_input.text().split(",") if segment.strip()]
        region = [int(value) for value in region_values] if len(region_values) == 4 else [0, 0, 1280, 720]
        payload = {
            "hotkey": self.hotkey_input.text().strip() or "ctrl+x",
            "hotkey_enabled": self.hotkey_enabled.isChecked(),
            "response_mode": self.response_mode.currentText(),
            "capture": {
                "mode": self.capture_mode.currentText(),
                "region": region,
                "monitor_index": self.monitor_input.value(),
            },
            "ocr_language": self.ocr_language_input.text().strip() or "spa+eng",
            "tesseract_cmd": self.tesseract_path_input.text().strip(),
            "start_with_windows": self.start_with_windows.isChecked(),
            "debug_mode": self.debug_mode.isChecked(),
            "debug_image_path": self.debug_image_path.text().strip(),
        }
        self.settings_saved.emit(payload)
        self.accept()
