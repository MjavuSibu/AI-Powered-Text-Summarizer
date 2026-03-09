"""
export/clipboard_handler.py
============================
Provides a simple interface for copying text to the system clipboard
using PyQt6's QApplication clipboard integration.
"""

from PyQt6.QtWidgets import QApplication


class ClipboardHandler:
    """
    Copies text to the system clipboard.

    This class wraps PyQt6's clipboard API to provide a clean, testable
    interface that is decoupled from the GUI widgets.

    Usage:
        handler = ClipboardHandler()
        handler.copy("Text to copy")
    """

    def copy(self, text: str) -> bool:
        """
        Copies the provided text to the system clipboard.

        Args:
            text: The string to place on the clipboard.

        Returns:
            True if the operation succeeded, False otherwise.
        """
        if not text:
            return False

        clipboard = QApplication.clipboard()
        if clipboard is None:
            return False

        clipboard.setText(text)
        return True

    def get(self) -> str:
        """
        Retrieves the current text content from the system clipboard.

        Returns:
            The clipboard text as a string, or an empty string if unavailable.
        """
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return ""
        return clipboard.text() or ""
