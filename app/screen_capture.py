from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mss import mss
from PIL import Image


@dataclass(slots=True)
class CaptureResult:
    image: Image.Image
    source: str


class ScreenCaptureService:
    def capture(self, mode: str = "full_screen", region: list[int] | None = None, monitor_index: int = 1) -> CaptureResult:
        with mss() as sct:
            if mode == "region" and region:
                left, top, width, height = region
                monitor = {"left": left, "top": top, "width": width, "height": height}
                source = f"region:{left},{top},{width},{height}"
            else:
                monitor = sct.monitors[min(monitor_index, len(sct.monitors) - 1)]
                source = f"monitor:{monitor_index}"
            raw = sct.grab(monitor)
            image = Image.frombytes("RGB", raw.size, raw.rgb)
            return CaptureResult(image=image, source=source)

    def load_debug_image(self, path: str) -> CaptureResult:
        image = Image.open(Path(path)).convert("RGB")
        return CaptureResult(image=image, source=f"debug:{path}")
