from __future__ import annotations

from dataclasses import dataclass

import pytesseract
from PIL import Image, ImageFilter, ImageOps

from app.utils import normalize_whitespace


@dataclass(slots=True)
class OCRResult:
    text: str
    raw_text: str


class OCREngine:
    def __init__(self, language: str = "spa+eng", tesseract_cmd: str = "") -> None:
        self.language = language
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess(self, image: Image.Image) -> Image.Image:
        gray = ImageOps.grayscale(image)
        enhanced = ImageOps.autocontrast(gray)
        return enhanced.filter(ImageFilter.SHARPEN)

    def extract_text(self, image: Image.Image) -> OCRResult:
        processed = self.preprocess(image)
        raw_text = pytesseract.image_to_string(processed, lang=self.language)
        clean_text = normalize_whitespace(raw_text)
        return OCRResult(text=clean_text, raw_text=raw_text)
