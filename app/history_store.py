from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, UTC
from pathlib import Path

from app.utils import get_default_data_dir


@dataclass(slots=True)
class HistoryEntry:
    timestamp: str
    question: str
    answer: str
    explanation: str
    confidence: float
    question_type: str


class HistoryStore:
    def __init__(self, history_path: Path | None = None, limit: int = 20) -> None:
        self.base_dir = get_default_data_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = history_path or self.base_dir / "history.json"
        self.limit = limit

    def load(self) -> list[HistoryEntry]:
        if not self.history_path.exists():
            return []
        payload = json.loads(self.history_path.read_text(encoding="utf-8"))
        return [HistoryEntry(**item) for item in payload]

    def add_entry(
        self,
        question: str,
        answer: str,
        explanation: str,
        confidence: float,
        question_type: str,
    ) -> None:
        entries = self.load()
        entries.insert(
            0,
            HistoryEntry(
                timestamp=datetime.now(UTC).isoformat(),
                question=question,
                answer=answer,
                explanation=explanation,
                confidence=confidence,
                question_type=question_type,
            ),
        )
        entries = entries[: self.limit]
        self.history_path.write_text(
            json.dumps([asdict(entry) for entry in entries], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
