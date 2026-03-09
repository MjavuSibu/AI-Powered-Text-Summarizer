"""
main.py
=======
Application entry point for the AI-Powered Text Summarizer.

This script initializes the QApplication, sets application metadata,
applies the saved theme, launches the main window, and starts the
Qt event loop.

Run this file to start the application:
    python main.py
"""

import sys
import os
from pathlib import Path

# Ensure the project root is on the Python path so all modules resolve
# correctly regardless of the working directory when the app is launched.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def main() -> None:
    """
    Initializes and launches the AI-Powered Text Summarizer application.

    This function:
    1. Creates the QApplication instance.
    2. Sets application-level metadata (name, version, organization).
    3. Enables high-DPI display support.
    4. Instantiates and shows the MainWindow.
    5. Enters the Qt event loop.
    """
    # Enable high-DPI scaling before creating the QApplication instance.
    # This must be set before QApplication is constructed.
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("AI-Powered Text Summarizer")
    app.setOrganizationName("SummarAI")
    app.setApplicationVersion("1.0.0")

    # Import MainWindow here (after path setup) to avoid circular imports.
    from gui.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
