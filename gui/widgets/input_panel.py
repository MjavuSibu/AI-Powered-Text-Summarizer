"""
gui/widgets/input_panel.py
===========================
The left-side input panel widget.

Provides a text area for pasting text, a file upload drop zone,
and a footer bar showing live text statistics.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QFileDialog, QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from processing.file_reader import FileReader, FileReadError
from processing.stats_calculator import StatsCalculator, TextStats
from utils.helpers import format_word_count
from utils.constants import SUPPORTED_FILE_EXTENSIONS


class DropZone(QFrame):
    """
    A drag-and-drop file upload zone.

    Signals:
        file_dropped(str): Emitted with the file path when a valid file is dropped.
    """

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(68)
        self.setObjectName("panel_frame")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        self.icon_label = QLabel("^")
        self.icon_label.setFixedSize(36, 36)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(
            "background-color: #fff0e8; border-radius: 6px;"
            "color: #e8673a; font-weight: 700; font-size: 16px;"
        )
        layout.addWidget(self.icon_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        self.title_label = QLabel("Drop a file here or click to upload")
        font = self.title_label.font()
        font.setBold(True)
        self.title_label.setFont(font)
        self.sub_label = QLabel("Supports .txt and .pdf files")
        self.sub_label.setObjectName("label_muted")
        text_col.addWidget(self.title_label)
        text_col.addWidget(self.sub_label)
        layout.addLayout(text_col)

        layout.addStretch()

        for ext in SUPPORTED_FILE_EXTENSIONS:
            tag = QLabel(ext.upper())
            tag.setStyleSheet(
                "background-color: #f4f4f5; border: 1px solid #e4e4e7;"
                "border-radius: 4px; padding: 2px 7px; font-size: 10px; font-weight: 600;"
            )
            layout.addWidget(tag)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        """Opens a file dialog when the drop zone is clicked."""
        self._open_file_dialog()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("border: 2px dashed #e8673a; border-radius: 8px; background: #fff0e8;")

    def dragLeaveEvent(self, event) -> None:
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent) -> None:
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)

    def _open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Supported Files (*.txt *.pdf);;Text Files (*.txt);;PDF Files (*.pdf)",
        )
        if path:
            self.file_dropped.emit(path)

    def set_loaded(self, filename: str, word_count: int) -> None:
        """Updates the drop zone labels to show a successfully loaded file."""
        self.title_label.setText(f"{filename} loaded successfully")
        self.sub_label.setText(f"{format_word_count(word_count)} words extracted")


class InputPanel(QWidget):
    """
    The left panel of the main workspace.

    Contains the file drop zone, the main text input area, and a stats footer.

    Signals:
        text_changed: Emitted whenever the text in the input area changes.
        file_load_error(str): Emitted with an error message if a file fails to load.
    """

    text_changed    = pyqtSignal()
    file_load_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_reader = FileReader()
        self._stats_calc = StatsCalculator()
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

        title = QLabel("INPUT TEXT")
        font = title.font()
        font.setBold(True)
        font.setPointSize(10)
        title.setFont(font)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.paste_btn = QPushButton("Paste")
        self.paste_btn.setFixedHeight(26)
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        header_layout.addWidget(self.paste_btn)

        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setFixedHeight(26)
        self.upload_btn.clicked.connect(self.drop_zone._open_file_dialog
                                        if hasattr(self, 'drop_zone') else lambda: None)
        header_layout.addWidget(self.upload_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(26)
        self.clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(self.clear_btn)

        layout.addWidget(header)
        layout.addWidget(self._make_h_line())

        # --- Drop Zone ---
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(14, 12, 14, 0)
        body_layout.setSpacing(10)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._load_file)
        body_layout.addWidget(self.drop_zone)

        # --- Text Area ---
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Paste or type your text here...\n\n"
            "You can also drag and drop a .txt or .pdf file above."
        )
        self.text_edit.textChanged.connect(self._on_text_changed)
        body_layout.addWidget(self.text_edit)

        layout.addWidget(body)

        # --- Footer Stats ---
        layout.addWidget(self._make_h_line())
        layout.addWidget(self._build_footer())

        # Fix upload button reference after drop_zone is created
        self.upload_btn.clicked.disconnect()
        self.upload_btn.clicked.connect(self.drop_zone._open_file_dialog)

    def _build_footer(self) -> QWidget:
        """Builds the stats footer bar."""
        footer = QWidget()
        footer.setFixedHeight(36)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        self.lbl_words    = self._stat_label("0 words")
        self.lbl_read     = self._stat_label("0 min read")
        self.lbl_chars    = self._stat_label("0 chars")
        self.lbl_chunks   = self._stat_label("0 chunks")

        layout.addWidget(self.lbl_words)
        layout.addWidget(self.lbl_read)
        layout.addWidget(self.lbl_chars)
        layout.addWidget(self.lbl_chunks)
        layout.addStretch()
        return footer

    def _stat_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("label_muted")
        font = lbl.font()
        font.setPointSize(10)
        lbl.setFont(font)
        return lbl

    def _make_h_line(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def _on_text_changed(self) -> None:
        """Updates stats labels whenever the text changes."""
        text = self.get_text()
        stats = self._stats_calc.compute_text_stats(text)
        self.lbl_words.setText(f"{format_word_count(stats.word_count)} words")
        self.lbl_read.setText(f"{stats.reading_time} min read")
        self.lbl_chars.setText(f"{format_word_count(stats.char_count)} chars")
        self.lbl_chunks.setText(f"{stats.chunk_count} chunk{'s' if stats.chunk_count != 1 else ''}")
        self.text_changed.emit()

    def _load_file(self, file_path: str) -> None:
        """Reads a file and populates the text area with its content."""
        try:
            text = self._file_reader.read(file_path)
            self.text_edit.setPlainText(text)
            filename = os.path.basename(file_path)
            word_count = len(text.split())
            self.drop_zone.set_loaded(filename, word_count)
        except FileReadError as e:
            self.file_load_error.emit(str(e))

    def _paste_from_clipboard(self) -> None:
        """Pastes clipboard text into the text area."""
        self.text_edit.paste()

    def get_text(self) -> str:
        """Returns the current text content of the input area."""
        return self.text_edit.toPlainText()

    def clear(self) -> None:
        """Clears the text area and resets the drop zone."""
        self.text_edit.clear()
        self.drop_zone.title_label.setText("Drop a file here or click to upload")
        self.drop_zone.sub_label.setText("Supports .txt and .pdf files")
