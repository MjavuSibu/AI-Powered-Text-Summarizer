"""
utils/helpers.py
================
General-purpose helper functions used across the application.

These functions are stateless and have no dependencies on other
application modules, making them easy to test and reuse.
"""

import re
from pathlib import Path


def count_words(text: str) -> int:
    """
    Counts the number of words in a given string.

    Args:
        text: The input string.

    Returns:
        The integer word count. Returns 0 for empty or whitespace-only strings.
    """
    if not text or not text.strip():
        return 0
    return len(text.split())


def count_characters(text: str) -> int:
    """
    Counts the total number of characters in a string, including spaces.

    Args:
        text: The input string.

    Returns:
        The integer character count.
    """
    return len(text)


def estimate_reading_time(word_count: int, wpm: int = 200) -> int:
    """
    Estimates the reading time in minutes for a given word count.

    Args:
        word_count: The number of words in the text.
        wpm: The average reading speed in words per minute. Defaults to 200.

    Returns:
        The estimated reading time in minutes, with a minimum of 1.
    """
    if word_count <= 0:
        return 0
    minutes = word_count / wpm
    return max(1, round(minutes))


def calculate_compression_ratio(original_words: int, summary_words: int) -> float:
    """
    Calculates the compression ratio as a percentage.

    A ratio of 75.0 means the summary is 75% shorter than the original.

    Args:
        original_words: Word count of the original text.
        summary_words: Word count of the generated summary.

    Returns:
        The compression percentage as a float, or 0.0 if inputs are invalid.
    """
    if original_words <= 0 or summary_words <= 0:
        return 0.0
    if summary_words >= original_words:
        return 0.0
    return round((1 - summary_words / original_words) * 100, 1)


def clean_text(text: str) -> str:
    """
    Cleans raw text by normalizing whitespace and removing control characters.

    This is applied to text extracted from files before processing.

    Args:
        text: The raw input string.

    Returns:
        A cleaned string with normalized whitespace.
    """
    # Remove null bytes and other control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Normalize multiple consecutive blank lines to a maximum of two
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize multiple spaces to a single space within lines
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 100) -> str:
    """
    Truncates a string to a maximum character length, appending an ellipsis.

    Useful for displaying preview text in the history panel.

    Args:
        text: The input string.
        max_chars: The maximum number of characters before truncation.

    Returns:
        The original string if short enough, or a truncated version with '...'.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def get_file_size_mb(file_path: str | Path) -> float:
    """
    Returns the size of a file in megabytes.

    Args:
        file_path: The path to the file.

    Returns:
        The file size in MB as a float.
    """
    path = Path(file_path)
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def format_word_count(count: int) -> str:
    """
    Formats a word count integer into a human-readable string with commas.

    Args:
        count: The word count.

    Returns:
        A formatted string, e.g., '1,482'.
    """
    return f"{count:,}"
