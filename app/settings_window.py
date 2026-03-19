from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
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
        self.resize(560, 540)
        self._build_ui(config)

    def _build_ui(self, config: AppConfig) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        hotkey_group = QGroupBox("Hotkey y captura")
        hotkey_form = QFormLayout(hotkey_group)
        hotkey_form.setSpacing(10)

        self.hotkey_input = QLineEdit(config.hotkey)
        self.hotkey_enabled = QCheckBox("Hotkey activa")
        self.hotkey_enabled.setChecked(config.hotkey_enabled)
        self.capture_mode = QComboBox()
        self.capture_mode.addItems(["region", "full_screen"])
        self.capture_mode.setCurrentText(config.capture.mode)
        self.region_input = QLineEdit(",".join(str(value) for value in config.capture.region))
        self.monitor_input = QSpinBox()
        self.monitor_input.setMinimum(1)
        self.monitor_input.setValue(config.capture.monitor_index)

        hotkey_form.addRow("Hotkey global", self.hotkey_input)
        hotkey_form.addRow("Estado", self.hotkey_enabled)
        hotkey_form.addRow("Modo de captura", self.capture_mode)
        hotkey_form.addRow("Región (x,y,w,h)", self.region_input)
        hotkey_form.addRow("Monitor", self.monitor_input)

        ocr_group = QGroupBox("OCR")
        ocr_form = QFormLayout(ocr_group)
        self.ocr_language_input = QLineEdit(config.ocr_language)
        self.tesseract_path_input = QLineEdit(config.tesseract_cmd)
        self.tesseract_psm_input = QSpinBox()
        self.tesseract_psm_input.setRange(3, 13)
        self.tesseract_psm_input.setValue(config.tesseract_psm)
        browse_button = QPushButton("Buscar…")
        browse_button.clicked.connect(self._choose_tesseract_path)
        tesseract_row = QHBoxLayout()
        tesseract_row.addWidget(self.tesseract_path_input)
        tesseract_row.addWidget(browse_button)
        self.debug_mode = QCheckBox("Usar imagen de prueba")
        self.debug_mode.setChecked(config.debug_mode)
        self.debug_image_path = QLineEdit(config.debug_image_path)
        ocr_form.addRow("Idioma OCR", self.ocr_language_input)
        ocr_form.addRow("Ruta de Tesseract", tesseract_row)
        ocr_form.addRow("Tesseract PSM", self.tesseract_psm_input)
        ocr_form.addRow("Depuración OCR", self.debug_mode)
        ocr_form.addRow("Imagen de prueba", self.debug_image_path)

        api_group = QGroupBox("OpenAI / motor de respuesta")
        api_form = QFormLayout(api_group)
        self.openai_enabled = QCheckBox("Usar OpenAI como motor principal")
        self.openai_enabled.setChecked(config.openai_enabled)
        self.internet_enabled = QCheckBox("Permitir peticiones API")
        self.internet_enabled.setChecked(config.internet_enabled)
        self.openai_model_input = QLineEdit(config.openai_model)
        self.openai_env_input = QLineEdit(config.openai_api_key_env)
        self.min_confidence_input = QDoubleSpinBox()
        self.min_confidence_input.setRange(0.0, 1.0)
        self.min_confidence_input.setSingleStep(0.05)
        self.min_confidence_input.setDecimals(2)
        self.min_confidence_input.setValue(config.min_confidence)
        self.response_mode = QComboBox()
        self.response_mode.addItems(["breve", "normal", "explicativa"])
        self.response_mode.setCurrentText(config.response_mode)
        api_form.addRow("OpenAI", self.openai_enabled)
        api_form.addRow("Internet/API", self.internet_enabled)
        api_form.addRow("Modelo", self.openai_model_input)
        api_form.addRow("Variable API key", self.openai_env_input)
        api_form.addRow("Confianza mínima", self.min_confidence_input)
        api_form.addRow("Modo de respuesta", self.response_mode)

        popup_group = QGroupBox("Popup")
        popup_form = QFormLayout(popup_group)
        self.show_question = QCheckBox("Mostrar pregunta en el popup")
        self.show_question.setChecked(config.show_question)
        self.compact_popup = QCheckBox("Popup compacto")
        self.compact_popup.setChecked(config.compact_popup)
        self.popup_width = QSpinBox()
        self.popup_width.setRange(320, 500)
        self.popup_width.setValue(config.popup_width)
        self.popup_height = QSpinBox()
        self.popup_height.setRange(140, 280)
        self.popup_height.setValue(config.popup_height)
        self.start_with_windows = QCheckBox("Iniciar con Windows")
        self.start_with_windows.setChecked(config.start_with_windows)
        popup_form.addRow("Mostrar pregunta", self.show_question)
        popup_form.addRow("Compacto", self.compact_popup)
        popup_form.addRow("Ancho", self.popup_width)
        popup_form.addRow("Alto", self.popup_height)
        popup_form.addRow("Autoarranque", self.start_with_windows)

        info = QLabel(
            "La API key no se guarda en config.json. Define la variable de entorno indicada, por ejemplo OPENAI_API_KEY."
        )
        info.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancelar")
        save_button = QPushButton("Guardar")
        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self._emit_settings)
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        layout.addWidget(hotkey_group)
        layout.addWidget(ocr_group)
        layout.addWidget(api_group)
        layout.addWidget(popup_group)
        layout.addWidget(info)
        layout.addStretch(1)
        layout.addLayout(button_row)

    def _choose_tesseract_path(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Selecciona tesseract.exe")
        if selected:
            self.tesseract_path_input.setText(selected)

    def _emit_settings(self) -> None:
        region_values = [segment.strip() for segment in self.region_input.text().split(",") if segment.strip()]
        region = [int(value) for value in region_values] if len(region_values) == 4 else [140, 140, 1280, 760]
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
            "tesseract_psm": self.tesseract_psm_input.value(),
            "start_with_windows": self.start_with_windows.isChecked(),
            "debug_mode": self.debug_mode.isChecked(),
            "debug_image_path": self.debug_image_path.text().strip(),
            "openai_enabled": self.openai_enabled.isChecked(),
            "internet_enabled": self.internet_enabled.isChecked(),
            "openai_model": self.openai_model_input.text().strip() or "gpt-4o-mini",
            "openai_api_key_env": self.openai_env_input.text().strip() or "OPENAI_API_KEY",
            "min_confidence": self.min_confidence_input.value(),
            "show_question": self.show_question.isChecked(),
            "compact_popup": self.compact_popup.isChecked(),
            "popup_width": self.popup_width.value(),
            "popup_height": self.popup_height.value(),
        }
        self.settings_saved.emit(payload)
        self.accept()
