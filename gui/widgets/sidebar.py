"""
gui/widgets/sidebar.py
=======================
The left-side navigation sidebar widget.

Displays the application logo, navigation links, the summary history
list, and footer utility links (settings, keyboard shortcuts).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class SidebarNavButton(QPushButton):
    """A styled navigation button for the sidebar."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFlat(True)
        self.setFixedHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class Sidebar(QWidget):
    """
    The left navigation sidebar of the main application window.

    Signals:
        new_summary_requested:   User clicked "New Summary".
        history_requested:       User clicked "History".
        settings_requested:      User clicked "Settings".
        shortcuts_requested:     User clicked "Keyboard Shortcuts".
    """

    new_summary_requested = pyqtSignal()
    history_requested     = pyqtSignal()
    settings_requested    = pyqtSignal()
    shortcuts_requested   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(210)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Logo / Brand Header ---
        layout.addWidget(self._build_logo_section())
        layout.addWidget(self._make_h_line())

        # --- Navigation ---
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(10, 12, 10, 8)
        nav_layout.setSpacing(2)

        nav_label = QLabel("WORKSPACE")
        nav_label.setObjectName("label_muted")
        font = nav_label.font()
        font.setPointSize(9)
        font.setBold(True)
        nav_label.setFont(font)
        nav_layout.addWidget(nav_label)

        self.btn_new = SidebarNavButton("  New Summary")
        self.btn_new.setChecked(True)
        self.btn_new.clicked.connect(self.new_summary_requested.emit)
        nav_layout.addWidget(self.btn_new)

        self.btn_history = SidebarNavButton("  History")
        self.btn_history.clicked.connect(self.history_requested.emit)
        nav_layout.addWidget(self.btn_history)

        layout.addWidget(nav_container)
        layout.addWidget(self._make_h_line())

        # --- History section label ---
        hist_label_container = QWidget()
        hist_label_layout = QVBoxLayout(hist_label_container)
        hist_label_layout.setContentsMargins(16, 10, 10, 4)
        hist_section_label = QLabel("RECENT SUMMARIES")
        hist_section_label.setObjectName("label_muted")
        font2 = hist_section_label.font()
        font2.setPointSize(9)
        font2.setBold(True)
        hist_section_label.setFont(font2)
        hist_label_layout.addWidget(hist_section_label)
        layout.addWidget(hist_label_container)

        # --- History list (injected from outside) ---
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(8, 0, 8, 0)
        self.history_layout.setSpacing(2)
        layout.addWidget(self.history_container)

        layout.addStretch()
        layout.addWidget(self._make_h_line())

        # --- Footer ---
        layout.addWidget(self._build_footer())

    def _build_logo_section(self) -> QWidget:
        """Builds the branded logo header at the top of the sidebar."""
        container = QWidget()
        container.setFixedHeight(60)
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(14, 12, 14, 12)
        h_layout.setSpacing(10)

        icon_label = QLabel("AI")
        icon_label.setFixedSize(34, 34)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #e8673a, stop:1 #ffb08a);"
            "border-radius: 8px;"
            "color: white;"
            "font-weight: 700;"
            "font-size: 13px;"
        )
        h_layout.addWidget(icon_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)

        app_name = QLabel("SummarAI")
        font = app_name.font()
        font.setBold(True)
        font.setPointSize(12)
        app_name.setFont(font)

        sub_name = QLabel("AI Text Summarizer")
        sub_name.setObjectName("label_muted")
        sub_font = sub_name.font()
        sub_font.setPointSize(9)
        sub_name.setFont(sub_font)

        text_col.addWidget(app_name)
        text_col.addWidget(sub_name)
        h_layout.addLayout(text_col)
        h_layout.addStretch()

        return container

    def _build_footer(self) -> QWidget:
        """Builds the footer section with utility navigation links."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 8, 10, 12)
        layout.setSpacing(2)

        self.btn_shortcuts = SidebarNavButton("  Keyboard Shortcuts")
        self.btn_shortcuts.clicked.connect(self.shortcuts_requested.emit)
        layout.addWidget(self.btn_shortcuts)

        self.btn_settings = SidebarNavButton("  Settings")
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        return container

    def _make_h_line(self) -> QFrame:
        """Creates a horizontal separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def set_active_nav(self, button_name: str) -> None:
        """Sets the active (checked) state for a navigation button by name."""
        mapping = {
            "new": self.btn_new,
            "history": self.btn_history,
        }
        for name, btn in mapping.items():
            btn.setChecked(name == button_name)

    def add_history_widget(self, widget: QWidget) -> None:
        """Adds a widget to the history list section of the sidebar."""
        self.history_layout.addWidget(widget)

    def clear_history_widgets(self) -> None:
        """Removes all widgets from the history list section."""
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
