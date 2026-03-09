"""
processing/stats_calculator.py
================================
Computes descriptive statistics for a piece of text.

These statistics are displayed in the input and output panel footers,
giving users a clear picture of the text's length and the AI's
compression performance.
"""

from dataclasses import dataclass

from utils.helpers import (
    count_words,
    count_characters,
    estimate_reading_time,
    calculate_compression_ratio,
)
from utils.constants import CHUNK_SIZE_WORDS


@dataclass
class TextStats:
    """
    A data class holding all computed statistics for a piece of text.

    Attributes:
        word_count:     Total number of words.
        char_count:     Total number of characters (including spaces).
        reading_time:   Estimated reading time in minutes.
        chunk_count:    Number of chunks the text would be split into.
        sentence_count: Approximate number of sentences.
    """
    word_count: int = 0
    char_count: int = 0
    reading_time: int = 0
    chunk_count: int = 0
    sentence_count: int = 0


@dataclass
class SummaryStats:
    """
    A data class holding comparison statistics between original and summary.

    Attributes:
        original_words:    Word count of the original text.
        summary_words:     Word count of the generated summary.
        compression_ratio: Percentage reduction in length.
        reading_time:      Estimated reading time of the summary in minutes.
    """
    original_words: int = 0
    summary_words: int = 0
    compression_ratio: float = 0.0
    reading_time: int = 0


class StatsCalculator:
    """
    Computes statistics for input text and generated summaries.

    Usage:
        calc = StatsCalculator()
        stats = calc.compute_text_stats("Some long text here...")
    """

    def compute_text_stats(self, text: str) -> TextStats:
        """
        Computes all statistics for a given input text.

        Args:
            text: The input text string.

        Returns:
            A populated TextStats dataclass instance.
        """
        if not text or not text.strip():
            return TextStats()

        word_count = count_words(text)
        char_count = count_characters(text)
        reading_time = estimate_reading_time(word_count)
        chunk_count = max(1, -(-word_count // CHUNK_SIZE_WORDS))  # ceiling division
        sentence_count = self._estimate_sentence_count(text)

        return TextStats(
            word_count=word_count,
            char_count=char_count,
            reading_time=reading_time,
            chunk_count=chunk_count,
            sentence_count=sentence_count,
        )

    def compute_summary_stats(
        self, original_text: str, summary_text: str
    ) -> SummaryStats:
        """
        Computes comparison statistics between the original and summary text.

        Args:
            original_text: The original input text.
            summary_text:  The generated summary text.

        Returns:
            A populated SummaryStats dataclass instance.
        """
        original_words = count_words(original_text)
        summary_words = count_words(summary_text)
        compression = calculate_compression_ratio(original_words, summary_words)
        reading_time = estimate_reading_time(summary_words)

        return SummaryStats(
            original_words=original_words,
            summary_words=summary_words,
            compression_ratio=compression,
            reading_time=reading_time,
        )

    def _estimate_sentence_count(self, text: str) -> int:
        """
        Estimates the number of sentences using punctuation heuristics.

        Args:
            text: The input text.

        Returns:
            An estimated sentence count.
        """
        import re
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])
