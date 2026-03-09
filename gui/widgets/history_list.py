"""
gui/widgets/history_list.py
============================
Manages the summary history list displayed in the sidebar.

History entries are persisted to a local JSON file so they survive
application restarts. Each entry stores the summary text, method,
length, timestamp, and a truncated preview of the original text.
"""

import json
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt

from utils.constants import (
    SummarizationMethod, SummaryLength, MAX_HISTORY_ITEMS, HISTORY_FILE
)
from utils.helpers import truncate_text


class HistoryEntry:
    """Represents a single history item."""

    def __init__(
        self,
        summary: str,
        method: SummarizationMethod,
        length: SummaryLength,
        original_preview: str = "",
        timestamp: str = "",
    ):
        self.summary = summary
        self.method = method
        self.length = length
        self.original_preview = original_preview
        self.timestamp = timestamp or datetime.now().strftime("%b %d, %H:%M")

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "method": self.method.value,
            "length": self.length.value,
            "original_preview": self.original_preview,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            summary=data.get("summary", ""),
            method=SummarizationMethod(data.get("method", SummarizationMethod.ABSTRACTIVE.value)),
            length=SummaryLength(data.get("length", SummaryLength.MEDIUM.value)),
            original_preview=data.get("original_preview", ""),
            timestamp=data.get("timestamp", ""),
        )


class HistoryItemWidget(QFrame):
    """
    A single clickable history entry widget for the sidebar.

    Signals:
        clicked(HistoryEntry): Emitted when the item is clicked.
    """

    clicked = pyqtSignal(object)

    _METHOD_COLORS = {
        SummarizationMethod.EXTRACTIVE:  ("#e8f4e8", "#2d7a2d"),
        SummarizationMethod.ABSTRACTIVE: ("#e8eef8", "#2d4d8a"),
        SummarizationMethod.LLM_API:     ("#fff0e8", "#e8673a"),
    }

    def __init__(self, entry: HistoryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(3)

        title = truncate_text(self.entry.original_preview or self.entry.summary, 45)
        title_lbl = QLabel(title)
        font = title_lbl.font()
        font.setBold(True)
        font.setPointSize(11)
        title_lbl.setFont(font)
        layout.addWidget(title_lbl)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)

        bg, fg = self._METHOD_COLORS.get(
            self.entry.method, ("#f4f4f5", "#52525b")
        )
        method_badge = QLabel(self.entry.method.value.split(" ")[0])
        method_badge.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 10px;"
            "padding: 1px 7px; font-size: 9px; font-weight: 700;"
        )
        meta_row.addWidget(method_badge)

        time_lbl = QLabel(self.entry.timestamp)
        time_lbl.setObjectName("label_muted")
        time_font = time_lbl.font()
        time_font.setPointSize(9)
        time_lbl.setFont(time_font)
        meta_row.addWidget(time_lbl)
        meta_row.addStretch()

        layout.addLayout(meta_row)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.entry)


class HistoryManager(QWidget):
    """
    Manages the full history list: loading, saving, and rendering entries.

    Signals:
        entry_selected(HistoryEntry): Emitted when a history item is clicked.
    """

    entry_selected = pyqtSignal(object)

    def __init__(self, sidebar_layout: QVBoxLayout, parent=None):
        super().__init__(parent)
        self._layout = sidebar_layout
        self._entries: list[HistoryEntry] = []
        self._history_path = Path(HISTORY_FILE)
        self._load_from_disk()
        self._render_all()

    def add_entry(
        self,
        summary: str,
        method: SummarizationMethod,
        length: SummaryLength,
        original_text: str = "",
    ) -> None:
        """Adds a new entry to the top of the history list."""
        preview = truncate_text(original_text, 50)
        entry = HistoryEntry(
            summary=summary,
            method=method,
            length=length,
            original_preview=preview,
        )
        self._entries.insert(0, entry)
        if len(self._entries) > MAX_HISTORY_ITEMS:
            self._entries = self._entries[:MAX_HISTORY_ITEMS]
        self._save_to_disk()
        self._render_all()

    def _render_all(self) -> None:
        """Clears and re-renders all history item widgets."""
        # Remove existing widgets from layout
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for entry in self._entries[:8]:  # Show max 8 in sidebar
            widget = HistoryItemWidget(entry)
            widget.clicked.connect(self.entry_selected.emit)
            self._layout.addWidget(widget)

    def _save_to_disk(self) -> None:
        """Persists the history list to a JSON file."""
        try:
            data = [e.to_dict() for e in self._entries]
            self._history_path.write_text(
                json.dumps(data, indent=2), encoding="utf-8"
            )
        except OSError:
            pass  # Silently fail — history is non-critical

    def _load_from_disk(self) -> None:
        """Loads the history list from the JSON file if it exists."""
        if not self._history_path.exists():
            return
        try:
            data = json.loads(self._history_path.read_text(encoding="utf-8"))
            self._entries = [HistoryEntry.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError, ValueError):
            self._entries = []
