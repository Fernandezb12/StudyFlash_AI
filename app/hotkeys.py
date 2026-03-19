from __future__ import annotations

import logging
from typing import Callable

import keyboard

logger = logging.getLogger(__name__)


class GlobalHotkeyManager:
    def __init__(self) -> None:
        self._hotkey_ref: int | None = None
        self._hotkey: str | None = None
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        self.unregister()
        self._hotkey_ref = keyboard.add_hotkey(hotkey, callback, suppress=False, trigger_on_release=False)
        self._hotkey = hotkey
        self._enabled = True
        logger.info("Registered global hotkey: %s", hotkey)

    def unregister(self) -> None:
        if self._hotkey_ref is not None:
            keyboard.remove_hotkey(self._hotkey_ref)
            logger.info("Unregistered global hotkey: %s", self._hotkey)
        self._hotkey_ref = None
        self._enabled = False

    def set_enabled(self, enabled: bool, callback: Callable[[], None] | None = None) -> None:
        if enabled and self._hotkey and callback:
            self.register(self._hotkey, callback)
        elif not enabled:
            self.unregister()
