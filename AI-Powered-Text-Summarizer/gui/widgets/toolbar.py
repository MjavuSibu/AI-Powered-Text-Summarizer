"""
gui/widgets/toolbar.py
=======================
The main application toolbar widget.

Contains controls for selecting the summarization method, adjusting
summary length, and triggering the primary Summarize action.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from utils.constants import SummarizationMethod, SummaryLength


class Toolbar(QWidget):
    """
    The top toolbar of the main application window.

    Signals:
        summarize_requested: Emitted when the user clicks the Summarize button.
        method_changed(SummarizationMethod): Emitted when the method dropdown changes.
        length_changed(SummaryLength): Emitted when a length button is toggled.
        clear_requested: Emitted when the Clear button is clicked.
    """

    summarize_requested = pyqtSignal()
    method_changed      = pyqtSignal(SummarizationMethod)
    length_changed      = pyqtSignal(SummaryLength)
    clear_requested     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_length = SummaryLength.MEDIUM
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        # --- Method label + dropdown ---
        method_label = QLabel("Method")
        method_label.setObjectName("label_muted")
        layout.addWidget(method_label)

        self.method_combo = QComboBox()
        for method in SummarizationMethod:
            self.method_combo.addItem(method.value, userData=method)
        self.method_combo.setCurrentIndex(1)  # Default: Abstractive
        self.method_combo.currentIndexChanged.connect(self._on_method_changed)
        layout.addWidget(self.method_combo)

        layout.addWidget(self._make_separator())

        # --- Length label + toggle buttons ---
        length_label = QLabel("Length")
        length_label.setObjectName("label_muted")
        layout.addWidget(length_label)

        self.length_buttons: dict[SummaryLength, QPushButton] = {}
        for length in SummaryLength:
            btn = QPushButton(length.value)
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda checked, l=length: self._on_length_clicked(l))
            self.length_buttons[length] = btn
            layout.addWidget(btn)

        # Set default active length button
        self.length_buttons[SummaryLength.MEDIUM].setChecked(True)
        self.length_buttons[SummaryLength.MEDIUM].setObjectName("btn_primary")

        layout.addStretch()

        # --- Clear button ---
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.clear_btn)

        # --- Summarize button ---
        self.summarize_btn = QPushButton("  Summarize")
        self.summarize_btn.setObjectName("btn_primary")
        self.summarize_btn.setFixedHeight(32)
        self.summarize_btn.setShortcut("Ctrl+Return")
        self.summarize_btn.clicked.connect(self.summarize_requested.emit)
        layout.addWidget(self.summarize_btn)

    def _make_separator(self) -> QFrame:
        """Creates a vertical separator line."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setFixedHeight(24)
        return sep

    def _on_method_changed(self, index: int) -> None:
        method = self.method_combo.itemData(index)
        if method:
            self.method_changed.emit(method)

    def _on_length_clicked(self, length: SummaryLength) -> None:
        # Uncheck all buttons and style the selected one.
        for l, btn in self.length_buttons.items():
            btn.setChecked(l == length)
            btn.setObjectName("btn_primary" if l == length else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._current_length = length
        self.length_changed.emit(length)

    def set_loading(self, loading: bool) -> None:
        """Disables or re-enables the toolbar controls during processing."""
        self.summarize_btn.setEnabled(not loading)
        self.summarize_btn.setText("  Processing..." if loading else "  Summarize")
        self.method_combo.setEnabled(not loading)
        for btn in self.length_buttons.values():
            btn.setEnabled(not loading)

    def get_method(self) -> SummarizationMethod:
        """Returns the currently selected summarization method."""
        return self.method_combo.currentData()

    def get_length(self) -> SummaryLength:
        """Returns the currently selected summary length."""
        return self._current_length
