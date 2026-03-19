from __future__ import annotations

import logging
from dataclasses import dataclass

import pytesseract
from PIL import Image, ImageFilter, ImageOps

from app.utils import LogPreviewFormatter, normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OCRResult:
    text: str
    raw_text: str
    preprocessing_summary: str


class OCREngine:
    def __init__(self, language: str = "spa+eng", tesseract_cmd: str = "", psm: int = 6) -> None:
        self.language = language
        self.psm = psm
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess(self, image: Image.Image) -> Image.Image:
        logger.debug("OCR preprocess started: size=%s mode=%s", image.size, image.mode)
        processed = ImageOps.exif_transpose(image).convert("RGB")
        processed = ImageOps.grayscale(processed)
        processed = ImageOps.autocontrast(processed)
        processed = processed.resize((processed.width * 2, processed.height * 2), Image.Resampling.LANCZOS)
        processed = processed.filter(ImageFilter.SHARPEN)
        processed = self._apply_threshold(processed)
        processed = self._optional_opencv_cleanup(processed)
        logger.debug("OCR preprocess finished: size=%s mode=%s", processed.size, processed.mode)
        return processed

    def _apply_threshold(self, image: Image.Image) -> Image.Image:
        return image.point(lambda px: 255 if px > 168 else 0, mode="1").convert("L")

    def _optional_opencv_cleanup(self, image: Image.Image) -> Image.Image:
        from importlib import import_module, util

        if util.find_spec("cv2") is None or util.find_spec("numpy") is None:
            logger.debug("OpenCV cleanup unavailable; continuing with Pillow-only OCR preprocessing.")
            return image

        cv2 = import_module("cv2")
        np = import_module("numpy")
        array = np.array(image)
        denoised = cv2.medianBlur(array, 3)
        _, thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return Image.fromarray(thresholded)

    def extract_text(self, image: Image.Image) -> OCRResult:
        processed = self.preprocess(image)
        config_candidates = [
            f"--oem 3 --psm {self.psm} -c preserve_interword_spaces=1",
            "--oem 3 --psm 4 -c preserve_interword_spaces=1",
        ]
        attempts: list[tuple[str, str]] = []
        for config in config_candidates:
            raw_text = pytesseract.image_to_string(processed, lang=self.language, config=config)
            attempts.append((config, raw_text))
            logger.debug("OCR attempt config=%s preview=%s", config, LogPreviewFormatter.preview(raw_text))

        best_config, best_raw = max(attempts, key=lambda item: self._score_text(item[1]))
        clean_text = normalize_whitespace(best_raw)
        logger.info("OCR selected config=%s preview=%s", best_config, LogPreviewFormatter.preview(clean_text))
        return OCRResult(text=clean_text, raw_text=best_raw, preprocessing_summary=best_config)

    def _score_text(self, text: str) -> tuple[int, int, int]:
        compact = normalize_whitespace(text)
        alnum = sum(char.isalnum() for char in compact)
        question_bias = sum(token in compact.lower() for token in ["?", "qué", "cuál", "verdadero", "falso"])
        option_bias = sum(token in compact for token in ["A)", "B)", "C)", "D)", "A.", "B."])
        return (question_bias + option_bias, alnum, len(compact))
