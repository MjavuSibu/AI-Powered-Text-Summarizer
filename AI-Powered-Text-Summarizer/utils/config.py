"""
utils/config.py
===============
Manages application configuration and user preferences.

Settings are persisted using PyQt6's QSettings, which stores data in the
Windows Registry (on Windows) or a platform-appropriate location on other
operating systems. An optional .env file is also read to load API keys
securely without hard-coding them in the source.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtCore import QSettings

from utils.constants import (
    APP_NAME,
    APP_ORGANIZATION,
    Theme,
    SummarizationMethod,
    SummaryLength,
    DEFAULT_ABSTRACTIVE_MODEL,
    DEFAULT_EXTRACTIVE_ALGORITHM,
)


# Load environment variables from a .env file if it exists in the project root.
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class AppConfig:
    """
    Centralized configuration manager for the application.

    This class wraps PyQt6's QSettings to provide a clean, typed interface
    for reading and writing user preferences. It also exposes API keys
    loaded from the environment.
    """

    def __init__(self):
        self._settings = QSettings(APP_ORGANIZATION, APP_NAME)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    @property
    def theme(self) -> Theme:
        """Returns the currently saved UI theme."""
        raw = self._settings.value("appearance/theme", Theme.LIGHT.value)
        return Theme(raw)

    @theme.setter
    def theme(self, value: Theme) -> None:
        """Persists the selected UI theme."""
        self._settings.setValue("appearance/theme", value.value)

    # ------------------------------------------------------------------
    # Summarization Preferences
    # ------------------------------------------------------------------

    @property
    def last_method(self) -> SummarizationMethod:
        """Returns the last-used summarization method."""
        raw = self._settings.value(
            "summarization/method", SummarizationMethod.ABSTRACTIVE.value
        )
        return SummarizationMethod(raw)

    @last_method.setter
    def last_method(self, value: SummarizationMethod) -> None:
        self._settings.setValue("summarization/method", value.value)

    @property
    def last_length(self) -> SummaryLength:
        """Returns the last-used summary length."""
        raw = self._settings.value(
            "summarization/length", SummaryLength.MEDIUM.value
        )
        return SummaryLength(raw)

    @last_length.setter
    def last_length(self, value: SummaryLength) -> None:
        self._settings.setValue("summarization/length", value.value)

    @property
    def abstractive_model(self) -> str:
        """Returns the selected HuggingFace model identifier."""
        return self._settings.value(
            "summarization/abstractive_model", DEFAULT_ABSTRACTIVE_MODEL
        )

    @abstractive_model.setter
    def abstractive_model(self, value: str) -> None:
        self._settings.setValue("summarization/abstractive_model", value)

    @property
    def extractive_algorithm(self) -> str:
        """Returns the selected Sumy algorithm key."""
        return self._settings.value(
            "summarization/extractive_algorithm", DEFAULT_EXTRACTIVE_ALGORITHM
        )

    @extractive_algorithm.setter
    def extractive_algorithm(self, value: str) -> None:
        self._settings.setValue("summarization/extractive_algorithm", value)

    # ------------------------------------------------------------------
    # API Keys (read-only, sourced from environment)
    # ------------------------------------------------------------------

    @property
    def openai_api_key(self) -> str | None:
        """
        Returns the OpenAI API key from the environment.
        Returns None if the key is not set.
        """
        return os.getenv("OPENAI_API_KEY")

    # ------------------------------------------------------------------
    # Export Preferences
    # ------------------------------------------------------------------

    @property
    def last_export_dir(self) -> str:
        """Returns the last directory used for PDF export."""
        return self._settings.value("export/last_dir", str(Path.home()))

    @last_export_dir.setter
    def last_export_dir(self, value: str) -> None:
        self._settings.setValue("export/last_dir", value)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def sync(self) -> None:
        """Force-writes any pending changes to the persistent store."""
        self._settings.sync()


# A single shared instance for use across the application.
config = AppConfig()
