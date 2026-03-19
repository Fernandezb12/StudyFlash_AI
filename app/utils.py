from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import Iterable

APP_NAME = "StudyFlash AI"
APP_AUTHOR = "OpenAI"
APP_ID = "studyflash_ai"


class LogPreviewFormatter:
    @staticmethod
    def preview(text: str, limit: int = 240) -> str:
        compact = normalize_whitespace(text)
        if len(compact) <= limit:
            return compact
        return f"{compact[:limit - 1]}…"


def ensure_windows_app_user_model_id() -> None:
    """Set an explicit app id on Windows so tray/popups behave better."""
    if sys.platform != "win32":
        return

    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        logging.getLogger(__name__).debug("Unable to set AppUserModelID", exc_info=True)


def resource_path(*parts: str) -> str:
    """Return a path that works both from source and PyInstaller builds."""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return str(base_dir.joinpath(*parts))


def get_default_data_dir() -> Path:
    """Return the per-user configuration directory."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_ID}"


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def normalize_whitespace(text: str) -> str:
    compact = re.sub(r"\s+", " ", text or "")
    return compact.strip()


def chunk_lines(text: str) -> list[str]:
    return [line.strip() for line in re.split(r"\r?\n", text or "") if line.strip()]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def compact_multiline_text(text: str, max_lines: int = 2) -> str:
    lines = [normalize_whitespace(line) for line in re.split(r"\r?\n", text or "") if normalize_whitespace(line)]
    if not lines:
        return ""
    return "\n".join(lines[:max_lines])


def ensure_sentence(text: str) -> str:
    clean = normalize_whitespace(text)
    if not clean:
        return clean
    if clean[-1] in ".!?":
        return clean
    return f"{clean}."


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = normalize_whitespace(value).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(normalize_whitespace(value))
    return result
