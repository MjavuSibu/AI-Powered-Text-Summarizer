"""
summarization/extractive.py
============================
Extractive summarization engine powered by the Sumy library.

Extractive summarization works by scoring each sentence in the original
text and selecting the highest-scoring ones to form the summary. No new
text is generated; the output is always a subset of the original sentences.

Supported algorithms (configurable via AppConfig):
    - LSA  (Latent Semantic Analysis) — default, best for general text
    - LexRank — graph-based, good for news articles
    - Luhn — frequency-based, fast and lightweight
    - TextRank — similar to Google's PageRank applied to sentences
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from summarization.base_summarizer import BaseSummarizer, SummarizationError
from utils.constants import SummaryLength, EXTRACTIVE_SENTENCE_COUNTS


# Mapping of algorithm keys (from constants) to their Sumy summarizer classes.
_ALGORITHM_MAP = {
    "lsa":        LsaSummarizer,
    "lexrank":    LexRankSummarizer,
    "luhn":       LuhnSummarizer,
    "text_rank":  TextRankSummarizer,
}

LANGUAGE = "english"


class ExtractiveSummarizer(BaseSummarizer):
    """
    Summarizes text by extracting the most important sentences.

    Uses the Sumy library under the hood. The algorithm and language
    are configurable at instantiation time.

    Usage:
        summarizer = ExtractiveSummarizer(algorithm="lsa")
        summary = summarizer.summarize(text, SummaryLength.MEDIUM)
    """

    def __init__(self, algorithm: str = "lsa"):
        """
        Initializes the extractive summarizer.

        Args:
            algorithm: The Sumy algorithm key to use. Must be one of the
                       keys defined in EXTRACTIVE_ALGORITHMS in constants.py.
        """
        if algorithm not in _ALGORITHM_MAP:
            raise ValueError(
                f"Unknown extractive algorithm '{algorithm}'. "
                f"Choose from: {list(_ALGORITHM_MAP.keys())}"
            )
        self.algorithm = algorithm
        self._stemmer = Stemmer(LANGUAGE)
        self._stop_words = get_stop_words(LANGUAGE)

    def summarize(self, text: str, length: SummaryLength) -> str:
        """
        Generates an extractive summary of the provided text.

        Args:
            text:   The input text to summarize.
            length: The desired summary length.

        Returns:
            A string of the selected sentences joined by spaces.

        Raises:
            SummarizationError: If parsing or summarization fails.
        """
        if not text or not text.strip():
            raise SummarizationError("Cannot summarize empty text.")

        sentence_count = EXTRACTIVE_SENTENCE_COUNTS.get(length, 6)

        try:
            parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
            summarizer_class = _ALGORITHM_MAP[self.algorithm]
            summarizer = summarizer_class(self._stemmer)
            summarizer.stop_words = self._stop_words

            sentences = summarizer(parser.document, sentence_count)

            if not sentences:
                raise SummarizationError(
                    "The extractive algorithm could not identify key sentences. "
                    "Try a different algorithm or a longer input text."
                )

            return " ".join(str(sentence) for sentence in sentences)

        except SummarizationError:
            raise
        except Exception as e:
            raise SummarizationError(
                f"Extractive summarization failed: {e}"
            ) from e
