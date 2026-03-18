from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.utils import APP_NAME, get_default_data_dir


@dataclass(slots=True)
class CaptureSettings:
    mode: str = "full_screen"
    region: list[int] = field(default_factory=lambda: [0, 0, 1280, 720])
    monitor_index: int = 1


@dataclass(slots=True)
class AppConfig:
    app_name: str = APP_NAME
    hotkey: str = "ctrl+x"
    hotkey_enabled: bool = True
    start_with_windows: bool = False
    response_mode: str = "normal"
    capture: CaptureSettings = field(default_factory=CaptureSettings)
    ocr_language: str = "spa+eng"
    tesseract_cmd: str = ""
    popup_width: int = 430
    popup_height: int = 360
    always_on_top: bool = True
    history_limit: int = 20
    debug_mode: bool = False
    debug_image_path: str = ""
    theme: str = "system"


class ConfigStore:
    def __init__(self, config_path: Path | None = None) -> None:
        self.base_dir = get_default_data_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = config_path or self.base_dir / "config.json"
        self._config = AppConfig()

    @property
    def config(self) -> AppConfig:
        return self._config

    def load(self) -> AppConfig:
        if not self.config_path.exists():
            self.save()
            return self._config

        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        capture = CaptureSettings(**payload.get("capture", {}))
        merged = {**asdict(AppConfig()), **payload, "capture": capture}
        self._config = AppConfig(**merged)
        return self._config

    def update(self, **changes: Any) -> AppConfig:
        data = asdict(self._config)
        for key, value in changes.items():
            if key == "capture" and isinstance(value, dict):
                data[key] = CaptureSettings(**value)
            else:
                data[key] = value
        self._config = AppConfig(**data)
        self.save()
        return self._config

    def save(self) -> None:
        data = asdict(self._config)
        self.config_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
