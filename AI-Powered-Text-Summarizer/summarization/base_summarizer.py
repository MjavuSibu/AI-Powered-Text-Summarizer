"""
summarization/base_summarizer.py
=================================
Defines the abstract base class that all summarization engines must implement.

Using an abstract base class enforces a consistent interface, making it
straightforward to add new summarization methods in the future without
changing any of the calling code.
"""

from abc import ABC, abstractmethod
from utils.constants import SummaryLength


class BaseSummarizer(ABC):
    """
    Abstract base class for all summarization engines.

    Every concrete summarizer (extractive, abstractive, LLM API) must
    inherit from this class and implement the `summarize` method.
    """

    @abstractmethod
    def summarize(self, text: str, length: SummaryLength) -> str:
        """
        Generates a summary of the provided text.

        Args:
            text:   The full input text to be summarized. For long documents,
                    this may already be a single chunk from the TextChunker.
            length: The desired summary length (SHORT, MEDIUM, or LONG).

        Returns:
            A string containing the generated summary.

        Raises:
            SummarizationError: If the summarization process fails for any reason.
        """
        raise NotImplementedError

    def summarize_chunks(self, chunks: list[str], length: SummaryLength) -> str:
        """
        Summarizes a list of text chunks and merges the results.

        For documents that were split by the TextChunker, this method
        summarizes each chunk individually and then performs a final
        summarization pass on the combined intermediate summaries.

        Args:
            chunks: A list of text chunk strings.
            length: The desired summary length.

        Returns:
            A single merged summary string.
        """
        if not chunks:
            return ""

        if len(chunks) == 1:
            return self.summarize(chunks[0], length)

        # Summarize each chunk individually.
        intermediate_summaries = []
        for chunk in chunks:
            chunk_summary = self.summarize(chunk, SummaryLength.SHORT)
            intermediate_summaries.append(chunk_summary)

        # Merge and perform a final summarization pass.
        merged = " ".join(intermediate_summaries)
        return self.summarize(merged, length)


class SummarizationError(Exception):
    """
    Raised when a summarization engine encounters an unrecoverable error.

    The message should be descriptive enough for the GUI to display
    a helpful error dialog to the user.
    """
    pass
