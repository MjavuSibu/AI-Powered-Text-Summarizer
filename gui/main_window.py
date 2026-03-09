"""
gui/main_window.py
===================
The main application window.

This is the top-level QMainWindow that assembles all widgets, connects
all signals and slots, manages the theme, and coordinates the
summarization workflow from user input to displayed result.
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFileDialog,
    QDialog, QLabel, QVBoxLayout as QVBox, QKeySequenceEdit,
    QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon

from gui.widgets.sidebar import Sidebar
from gui.widgets.toolbar import Toolbar
from gui.widgets.input_panel import InputPanel
from gui.widgets.output_panel import OutputPanel
from gui.widgets.history_list import HistoryManager, HistoryEntry
from gui.workers.summary_worker import SummaryWorker
from export.pdf_exporter import PdfExporter
from export.clipboard_handler import ClipboardHandler
from utils.constants import (
    APP_NAME, APP_VERSION, SummarizationMethod, SummaryLength, Theme
)
from utils.config import config


class MainWindow(QMainWindow):
    """
    The main application window for the AI-Powered Text Summarizer.

    Responsibilities:
    - Assembles the sidebar, toolbar, input panel, and output panel.
    - Manages the summarization workflow via SummaryWorker.
    - Handles theme switching between light and dark mode.
    - Coordinates export (PDF) and clipboard operations.
    - Maintains keyboard shortcuts.
    - Persists user preferences on close.
    """

    def __init__(self):
        super().__init__()
        self._worker: SummaryWorker | None = None
        self._current_method = config.last_method
        self._current_length = config.last_length
        self._current_theme  = config.theme

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._apply_theme(self._current_theme)
        self._update_status("Ready")

    # ------------------------------------------------------------------
    # Window Setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(QSize(1000, 650))
        self.resize(1280, 800)

        # Load window icon if available
        icon_path = Path("assets/icons/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    # ------------------------------------------------------------------
    # UI Assembly
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Toolbar ---
        self.toolbar = Toolbar()
        self.toolbar.summarize_requested.connect(self._on_summarize)
        self.toolbar.method_changed.connect(self._on_method_changed)
        self.toolbar.length_changed.connect(self._on_length_changed)
        self.toolbar.clear_requested.connect(self._on_clear)
        root_layout.addWidget(self.toolbar)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        root_layout.addWidget(sep)

        # --- Body (sidebar + workspace) ---
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.new_summary_requested.connect(self._on_new_summary)
        self.sidebar.history_requested.connect(self._on_show_history)
        self.sidebar.settings_requested.connect(self._on_show_settings)
        self.sidebar.shortcuts_requested.connect(self._on_show_shortcuts)
        body_layout.addWidget(self.sidebar)

        # Vertical separator
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.Shape.VLine)
        v_sep.setFixedWidth(1)
        body_layout.addWidget(v_sep)

        # Workspace splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)

        self.input_panel = InputPanel()
        self.input_panel.file_load_error.connect(self._show_error)

        self.output_panel = OutputPanel()
        self.output_panel.copy_requested.connect(self._on_copy)
        self.output_panel.export_requested.connect(self._on_export_pdf)

        self.splitter.addWidget(self.input_panel)
        self.splitter.addWidget(self.output_panel)
        self.splitter.setSizes([600, 600])

        body_layout.addWidget(self.splitter)
        root_layout.addWidget(body)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._status_method_lbl = QLabel()
        self._status_version_lbl = QLabel(f"v{APP_VERSION}")
        self.status_bar.addPermanentWidget(self._status_method_lbl)
        self.status_bar.addPermanentWidget(self._status_version_lbl)

        # --- History Manager ---
        self.history_manager = HistoryManager(
            sidebar_layout=self.sidebar.history_layout
        )
        self.history_manager.entry_selected.connect(self._on_history_entry_selected)

        # --- Theme toggle in menu bar ---
        self._build_menu_bar()

        # Sync toolbar to saved preferences
        method_index = list(SummarizationMethod).index(self._current_method)
        self.toolbar.method_combo.setCurrentIndex(method_index)
        self.toolbar._on_length_clicked(self._current_length)

    def _build_menu_bar(self) -> None:
        """Builds the application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Summary\tCtrl+N", self._on_new_summary)
        file_menu.addAction("Open File...\tCtrl+O", self._open_file_dialog)
        file_menu.addSeparator()
        file_menu.addAction("Export PDF...\tCtrl+Shift+E", self._on_export_pdf)
        file_menu.addSeparator()
        file_menu.addAction("Exit\tAlt+F4", self.close)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Copy Summary\tCtrl+Shift+C", self._on_copy)
        edit_menu.addAction("Clear Input\tCtrl+Shift+X", self._on_clear)

        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Toggle Theme\tCtrl+Shift+T", self._on_toggle_theme)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("Keyboard Shortcuts\tCtrl+?", self._on_show_shortcuts)
        help_menu.addAction(f"About {APP_NAME}", self._on_show_about)

    # ------------------------------------------------------------------
    # Keyboard Shortcuts
    # ------------------------------------------------------------------

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Return"),    self, self._on_summarize)
        QShortcut(QKeySequence("Ctrl+Shift+C"),   self, self._on_copy)
        QShortcut(QKeySequence("Ctrl+Shift+E"),   self, self._on_export_pdf)
        QShortcut(QKeySequence("Ctrl+Shift+X"),   self, self._on_clear)
        QShortcut(QKeySequence("Ctrl+Shift+T"),   self, self._on_toggle_theme)
        QShortcut(QKeySequence("Ctrl+N"),         self, self._on_new_summary)
        QShortcut(QKeySequence("Ctrl+O"),         self, self._open_file_dialog)
        QShortcut(QKeySequence("Ctrl+?"),         self, self._on_show_shortcuts)

    # ------------------------------------------------------------------
    # Theme Management
    # ------------------------------------------------------------------

    def _apply_theme(self, theme: Theme) -> None:
        """Loads and applies the QSS stylesheet for the given theme."""
        qss_path = Path(f"assets/theme/{theme.value}.qss")
        if qss_path.exists():
            stylesheet = qss_path.read_text(encoding="utf-8")
            self.setStyleSheet(stylesheet)
        self._current_theme = theme

    def _on_toggle_theme(self) -> None:
        new_theme = (
            Theme.DARK if self._current_theme == Theme.LIGHT else Theme.LIGHT
        )
        self._apply_theme(new_theme)
        config.theme = new_theme

    # ------------------------------------------------------------------
    # Summarization Workflow
    # ------------------------------------------------------------------

    def _on_summarize(self) -> None:
        """Validates input and starts the summarization worker thread."""
        text = self.input_panel.get_text().strip()
        if not text:
            self._show_error(
                "No text to summarize.\n\n"
                "Please paste text into the input area or upload a file."
            )
            return

        if self._worker and self._worker.isRunning():
            return  # Already processing

        self.toolbar.set_loading(True)
        self.output_panel.show_loading(
            f"Starting {self._current_method.value}..."
        )
        self._update_status(f"Summarizing with {self._current_method.value}...")

        self._worker = SummaryWorker(
            text=text,
            method=self._current_method,
            length=self._current_length,
        )
        self._worker.progress.connect(self.output_panel.update_loading_message)
        self._worker.finished.connect(self._on_summary_finished)
        self._worker.error.connect(self._on_summary_error)
        self._worker.start()

    def _on_summary_finished(self, summary: str) -> None:
        """Handles a successful summary result from the worker."""
        self.toolbar.set_loading(False)
        original_text = self.input_panel.get_text()
        self.output_panel.show_result(
            summary=summary,
            original_text=original_text,
            method=self._current_method,
            length=self._current_length,
        )
        self.history_manager.add_entry(
            summary=summary,
            method=self._current_method,
            length=self._current_length,
            original_text=original_text,
        )
        self._update_status("Summary generated successfully.")

    def _on_summary_error(self, message: str) -> None:
        """Handles an error from the summarization worker."""
        self.toolbar.set_loading(False)
        self.output_panel.show_empty()
        self._show_error(message)
        self._update_status("Summarization failed.")

    # ------------------------------------------------------------------
    # Toolbar Signal Handlers
    # ------------------------------------------------------------------

    def _on_method_changed(self, method: SummarizationMethod) -> None:
        self._current_method = method
        self._status_method_lbl.setText(f"  {method.value}  ")

    def _on_length_changed(self, length: SummaryLength) -> None:
        self._current_length = length

    def _on_clear(self) -> None:
        self.input_panel.clear()
        self.output_panel.show_empty()
        self._update_status("Cleared.")

    # ------------------------------------------------------------------
    # Sidebar Signal Handlers
    # ------------------------------------------------------------------

    def _on_new_summary(self) -> None:
        self._on_clear()
        self.sidebar.set_active_nav("new")

    def _on_show_history(self) -> None:
        self.sidebar.set_active_nav("history")

    def _on_history_entry_selected(self, entry: HistoryEntry) -> None:
        """Restores a history entry into the output panel."""
        self.output_panel.show_result(
            summary=entry.summary,
            original_text=entry.summary,  # Use summary as proxy for stats
            method=entry.method,
            length=entry.length,
        )

    # ------------------------------------------------------------------
    # Export & Clipboard
    # ------------------------------------------------------------------

    def _on_copy(self) -> None:
        summary = self.output_panel.get_summary_text()
        if not summary:
            self._show_error("No summary to copy. Please generate a summary first.")
            return
        handler = ClipboardHandler()
        if handler.copy(summary):
            self._update_status("Summary copied to clipboard.")
        else:
            self._show_error("Failed to copy to clipboard.")

    def _on_export_pdf(self) -> None:
        summary = self.output_panel.get_summary_text()
        if not summary:
            self._show_error("No summary to export. Please generate a summary first.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Summary as PDF",
            str(Path(config.last_export_dir) / "summary.pdf"),
            "PDF Files (*.pdf)",
        )
        if not save_path:
            return

        try:
            exporter = PdfExporter()
            original_text = self.input_panel.get_text()
            exporter.export(
                output_path=save_path,
                summary_text=summary,
                method=self._current_method.value,
                length=self._current_length.value,
                original_word_count=len(original_text.split()),
                summary_word_count=len(summary.split()),
            )
            config.last_export_dir = str(Path(save_path).parent)
            self._update_status(f"Exported to {Path(save_path).name}")
            QMessageBox.information(
                self, "Export Successful",
                f"Summary exported successfully to:\n{save_path}"
            )
        except Exception as e:
            self._show_error(f"Failed to export PDF:\n{e}")

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------

    def _on_show_shortcuts(self) -> None:
        """Displays the keyboard shortcuts dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setFixedWidth(420)
        layout = QVBox(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        shortcuts = [
            ("Summarize",         "Ctrl + Enter"),
            ("Copy Summary",      "Ctrl + Shift + C"),
            ("Export to PDF",     "Ctrl + Shift + E"),
            ("Open File",         "Ctrl + O"),
            ("New Summary",       "Ctrl + N"),
            ("Clear Input",       "Ctrl + Shift + X"),
            ("Toggle Theme",      "Ctrl + Shift + T"),
            ("Show Shortcuts",    "Ctrl + ?"),
        ]

        for action, keys in shortcuts:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            action_lbl = QLabel(action)
            keys_lbl = QLabel(keys)
            keys_lbl.setStyleSheet(
                "background: #f4f4f5; border: 1px solid #e4e4e7;"
                "border-radius: 4px; padding: 2px 8px; font-weight: 600;"
                "font-family: 'Consolas', monospace; font-size: 11px;"
            )
            row_layout.addWidget(action_lbl)
            row_layout.addStretch()
            row_layout.addWidget(keys_lbl)
            layout.addWidget(row)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("btn_primary")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def _on_show_settings(self) -> None:
        QMessageBox.information(
            self, "Settings",
            "Settings panel coming in a future update.\n\n"
            "You can configure your API key by creating a .env file\n"
            "in the project root with: OPENAI_API_KEY=your_key_here"
        )

    def _on_show_about(self) -> None:
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b><br>"
            f"Version {APP_VERSION}<br><br>"
            "A production-quality AI text summarization tool<br>"
            "built with Python and PyQt6.<br><br>"
            "Supports Extractive (NLP), Abstractive (BART/T5),<br>"
            "and LLM API summarization methods."
        )

    def _open_file_dialog(self) -> None:
        """Opens a file dialog and loads the selected file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Supported Files (*.txt *.pdf);;Text Files (*.txt);;PDF Files (*.pdf)",
        )
        if path:
            self.input_panel._load_file(path)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _update_status(self, message: str) -> None:
        self.status_bar.showMessage(f"  {message}", 5000)
        self._status_method_lbl.setText(f"  {self._current_method.value}  ")

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        """Saves user preferences before the window closes."""
        config.last_method = self._current_method
        config.last_length = self._current_length
        config.theme = self._current_theme
        config.sync()
        event.accept()
