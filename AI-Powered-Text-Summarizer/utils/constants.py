"""
utils/constants.py
==================
Application-wide constants and enumeration values.
These values are referenced throughout the application and are
defined here to avoid magic strings and numbers scattered in the code.
"""

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Application Metadata
# ---------------------------------------------------------------------------

APP_NAME = "AI-Powered Text Summarizer"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "SummarAI"
HISTORY_FILE = "summary_history.json"
MAX_HISTORY_ITEMS = 50


# ---------------------------------------------------------------------------
# Summarization Methods
# ---------------------------------------------------------------------------

class SummarizationMethod(Enum):
    """Enumeration of all available summarization methods."""
    EXTRACTIVE = "Extractive (NLP)"
    ABSTRACTIVE = "Abstractive (BART/T5)"
    LLM_API = "LLM API (OpenAI)"


# ---------------------------------------------------------------------------
# Summary Length Options
# ---------------------------------------------------------------------------

class SummaryLength(Enum):
    """Enumeration of available summary length options."""
    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"


# Ratio of the summary length relative to the original text word count.
# These values are used by the summarization engines to calibrate output.
SUMMARY_LENGTH_RATIOS = {
    SummaryLength.SHORT: 0.10,   # ~10% of original
    SummaryLength.MEDIUM: 0.25,  # ~25% of original
    SummaryLength.LONG: 0.40,    # ~40% of original
}

# Sentence count targets for extractive summarization.
EXTRACTIVE_SENTENCE_COUNTS = {
    SummaryLength.SHORT: 3,
    SummaryLength.MEDIUM: 6,
    SummaryLength.LONG: 10,
}

# Token limits for abstractive (transformer) summarization.
ABSTRACTIVE_TOKEN_LIMITS = {
    SummaryLength.SHORT:  {"min": 40,  "max": 100},
    SummaryLength.MEDIUM: {"min": 100, "max": 250},
    SummaryLength.LONG:   {"min": 200, "max": 450},
}


# ---------------------------------------------------------------------------
# Text Processing
# ---------------------------------------------------------------------------

# Maximum number of words per chunk when splitting long documents.
# This keeps inputs within model context window limits.
CHUNK_SIZE_WORDS = 500

# Average reading speed in words per minute (used for reading time estimate).
AVERAGE_READING_SPEED_WPM = 200


# ---------------------------------------------------------------------------
# File Handling
# ---------------------------------------------------------------------------

SUPPORTED_FILE_EXTENSIONS = [".txt", ".pdf"]
MAX_FILE_SIZE_MB = 50


# ---------------------------------------------------------------------------
# UI / Theme
# ---------------------------------------------------------------------------

class Theme(Enum):
    """Enumeration of available UI themes."""
    LIGHT = "light"
    DARK = "dark"


# ---------------------------------------------------------------------------
# Supported HuggingFace Models
# ---------------------------------------------------------------------------

ABSTRACTIVE_MODELS = {
    "BART (facebook/bart-large-cnn)": "facebook/bart-large-cnn",
    "T5 (t5-small)": "t5-small",
    "T5 (t5-base)": "t5-base",
}

DEFAULT_ABSTRACTIVE_MODEL = "facebook/bart-large-cnn"


# ---------------------------------------------------------------------------
# Extractive Summarization Algorithms (Sumy)
# ---------------------------------------------------------------------------

EXTRACTIVE_ALGORITHMS = {
    "LSA (Latent Semantic Analysis)": "lsa",
    "LexRank": "lexrank",
    "Luhn": "luhn",
    "TF-IDF": "text_rank",
}

DEFAULT_EXTRACTIVE_ALGORITHM = "lsa"
