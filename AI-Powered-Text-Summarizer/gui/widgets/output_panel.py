"""
gui/widgets/output_panel.py
============================
The right-side summary output panel widget.

Displays the generated summary, statistics, a loading overlay during
processing, and action buttons for copying and exporting the result.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QProgressBar, QStackedWidget, QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont

from processing.stats_calculator import StatsCalculator, SummaryStats
from utils.helpers import format_word_count
from utils.constants import SummarizationMethod, SummaryLength


class LoadingWidget(QWidget):
    """A centered loading indicator shown while summarization is in progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # Spinner label (animated via a timer)
        self.spinner_label = QLabel("...")
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setStyleSheet(
            "font-size: 28px; color: #e8673a; font-weight: 700;"
        )
        layout.addWidget(self.spinner_label)

        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.status_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)

        self.sub_label = QLabel("Please wait while the AI processes your text.")
        self.sub_label.setObjectName("label_muted")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setFixedWidth(220)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spinner animation
        self._frames = ["   ", ".  ", ".. ", "..."]
        self._frame_index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self, message: str = "Processing...") -> None:
        self.status_label.setText(message)
        self._timer.start(400)

    def stop(self) -> None:
        self._timer.stop()

    def update_message(self, message: str) -> None:
        self.status_label.setText(message)

    def _tick(self) -> None:
        self._frame_index = (self._frame_index + 1) % len(self._frames)
        self.spinner_label.setText(self._frames[self._frame_index])


class EmptyStateWidget(QWidget):
    """Shown when no summary has been generated yet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon = QLabel("AI")
        icon.setFixedSize(64, 64)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "background: #fff0e8; border-radius: 16px;"
            "color: #e8673a; font-weight: 700; font-size: 18px;"
        )
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Ready to Summarize")
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Paste or upload your text on the left,\n"
            "then click Summarize to generate an AI-powered summary."
        )
        sub.setObjectName("label_muted")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)


class SummaryResultWidget(QWidget):
    """Displays the generated summary with statistics and action buttons."""

    copy_requested   = pyqtSignal()
    export_requested = pyqtSignal()
    save_requested   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # --- Method & Length Badges ---
        badges_row = QHBoxLayout()
        self.method_badge = self._make_badge("Abstractive (BART)", accent=True)
        self.length_badge = self._make_badge("Medium", accent=False)
        badges_row.addWidget(self.method_badge)
        badges_row.addWidget(self.length_badge)
        badges_row.addStretch()
        layout.addLayout(badges_row)

        # --- Stats Row ---
        stats_row = QHBoxLayout()
        self.stat_words    = self._make_stat_card("0", "Words")
        self.stat_read     = self._make_stat_card("<1", "Min Read")
        self.stat_compress = self._make_stat_card("0%", "Compressed")
        stats_row.addWidget(self.stat_words)
        stats_row.addWidget(self.stat_read)
        stats_row.addWidget(self.stat_compress)
        layout.addLayout(stats_row)

        # --- Summary Text ---
        self.summary_edit = QTextEdit()
        self.summary_edit.setReadOnly(True)
        self.summary_edit.setObjectName("panel_frame")
        layout.addWidget(self.summary_edit)

        # --- Action Buttons ---
        btn_row = QHBoxLayout()
        self.copy_btn   = QPushButton("Copy Summary")
        self.export_btn = QPushButton("Export PDF")
        self.export_btn.setObjectName("btn_primary")
        self.copy_btn.clicked.connect(self.copy_requested.emit)
        self.export_btn.clicked.connect(self.export_requested.emit)
        btn_row.addWidget(self.copy_btn)
        btn_row.addWidget(self.export_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _make_badge(self, text: str, accent: bool) -> QLabel:
        lbl = QLabel(text)
        style = (
            "background: #fff0e8; color: #e8673a; border: 1px solid #e8c8b8;"
            if accent else
            "background: #f4f4f5; color: #52525b; border: 1px solid #e4e4e7;"
        )
        lbl.setStyleSheet(
            f"{style} border-radius: 20px; padding: 3px 10px;"
            "font-size: 11px; font-weight: 600;"
        )
        return lbl

    def _make_stat_card(self, value: str, label: str) -> QFrame:
        card = QFrame()
        card.setObjectName("panel_frame")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(2)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("label_accent")
        val_font = val_lbl.font()
        val_font.setPointSize(18)
        val_font.setBold(True)
        val_lbl.setFont(val_font)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_lbl = QLabel(label.upper())
        lbl_lbl.setObjectName("label_muted")
        lbl_font = lbl_lbl.font()
        lbl_font.setPointSize(9)
        lbl_font.setBold(True)
        lbl_lbl.setFont(lbl_font)
        lbl_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(val_lbl)
        card_layout.addWidget(lbl_lbl)

        # Store reference to value label for updates
        card._value_label = val_lbl
        return card

    def populate(
        self,
        summary: str,
        stats: SummaryStats,
        method: SummarizationMethod,
        length: SummaryLength,
    ) -> None:
        """Populates all fields with the summary result data."""
        self.method_badge.setText(method.value)
        self.length_badge.setText(length.value)
        self.summary_edit.setPlainText(summary)

        self.stat_words._value_label.setText(str(stats.summary_words))
        read_str = "<1" if stats.reading_time < 1 else str(stats.reading_time)
        self.stat_read._value_label.setText(read_str)
        self.stat_compress._value_label.setText(f"{stats.compression_ratio:.0f}%")

    def get_summary_text(self) -> str:
        """Returns the current summary text."""
        return self.summary_edit.toPlainText()


class OutputPanel(QWidget):
    """
    The right panel of the main workspace.

    Uses a QStackedWidget to switch between the empty state,
    the loading overlay, and the summary result view.

    Signals:
        copy_requested:   User clicked Copy.
        export_requested: User clicked Export PDF.
    """

    copy_requested   = pyqtSignal()
    export_requested = pyqtSignal()

    EMPTY   = 0
    LOADING = 1
    RESULT  = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stats_calc = StatsCalculator()
        self._current_method = None
        self._current_length = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Panel Header ---
        header = QWidget()
        header.setFixedHeight(42)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 12, 0)

        title = QLabel("SUMMARY OUTPUT")
        font = title.font()
        font.setBold(True)
        font.setPointSize(10)
        title.setFont(font)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.copy_btn_header   = QPushButton("Copy")
        self.export_btn_header = QPushButton("Export PDF")
        self.copy_btn_header.setFixedHeight(26)
        self.export_btn_header.setFixedHeight(26)
        self.copy_btn_header.setEnabled(False)
        self.export_btn_header.setEnabled(False)
        self.copy_btn_header.clicked.connect(self.copy_requested.emit)
        self.export_btn_header.clicked.connect(self.export_requested.emit)
        header_layout.addWidget(self.copy_btn_header)
        header_layout.addWidget(self.export_btn_header)

        layout.addWidget(header)
        layout.addWidget(self._make_h_line())

        # --- Stacked Widget ---
        self.stack = QStackedWidget()

        self.empty_widget   = EmptyStateWidget()
        self.loading_widget = LoadingWidget()
        self.result_widget  = SummaryResultWidget()
        self.result_widget.copy_requested.connect(self.copy_requested.emit)
        self.result_widget.export_requested.connect(self.export_requested.emit)

        self.stack.addWidget(self.empty_widget)    # index 0
        self.stack.addWidget(self.loading_widget)  # index 1
        self.stack.addWidget(self.result_widget)   # index 2

        layout.addWidget(self.stack)

    def _make_h_line(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def show_loading(self, message: str = "Processing...") -> None:
        """Switches to the loading view."""
        self.stack.setCurrentIndex(self.LOADING)
        self.loading_widget.start(message)
        self.copy_btn_header.setEnabled(False)
        self.export_btn_header.setEnabled(False)

    def update_loading_message(self, message: str) -> None:
        """Updates the loading status message."""
        self.loading_widget.update_message(message)

    def show_result(
        self,
        summary: str,
        original_text: str,
        method: SummarizationMethod,
        length: SummaryLength,
    ) -> None:
        """Switches to the result view and populates it with summary data."""
        self.loading_widget.stop()
        stats = self._stats_calc.compute_summary_stats(original_text, summary)
        self.result_widget.populate(summary, stats, method, length)
        self.stack.setCurrentIndex(self.RESULT)
        self.copy_btn_header.setEnabled(True)
        self.export_btn_header.setEnabled(True)
        self._current_method = method
        self._current_length = length

    def show_empty(self) -> None:
        """Switches back to the empty state."""
        self.loading_widget.stop()
        self.stack.setCurrentIndex(self.EMPTY)
        self.copy_btn_header.setEnabled(False)
        self.export_btn_header.setEnabled(False)

    def get_summary_text(self) -> str:
        """Returns the current summary text, or empty string if none."""
        return self.result_widget.get_summary_text()
