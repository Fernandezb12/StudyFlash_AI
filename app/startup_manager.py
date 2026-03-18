from __future__ import annotations

import os
import sys
from pathlib import Path

APP_RUN_VALUE = "StudyFlashAI"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


class StartupManager:
    def __init__(self, app_name: str = APP_RUN_VALUE) -> None:
        self.app_name = app_name

    def is_supported(self) -> bool:
        return sys.platform == "win32"

    def get_command(self) -> str:
        executable = Path(sys.executable).resolve()
        if executable.name.lower().endswith("python.exe") or executable.name.lower().endswith("pythonw.exe"):
            run_target = Path(__file__).resolve().parents[1] / "run.py"
            return f'"{executable}" "{run_target}"'
        return f'"{executable}"'

    def is_enabled(self) -> bool:
        if not self.is_supported():
            return False
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return value == self.get_command()
        except FileNotFoundError:
            return False
        except OSError:
            return False

    def set_enabled(self, enabled: bool) -> None:
        if not self.is_supported():
            return
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH) as key:
            if enabled:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.get_command())
            else:
                try:
                    winreg.DeleteValue(key, self.app_name)
                except FileNotFoundError:
                    pass

    def startup_folder(self) -> Path:
        return Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs\Startup"
