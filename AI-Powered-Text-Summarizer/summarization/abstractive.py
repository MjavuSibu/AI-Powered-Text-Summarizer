"""
summarization/abstractive.py
==============================
Abstractive summarization engine using HuggingFace Transformer models.

Unlike extractive summarization, abstractive models generate entirely new
sentences that capture the meaning of the original text, much like a human
would when writing a summary. This engine supports BART and T5 models.

The model is loaded lazily on the first call to `summarize()` to avoid
slowing down application startup. A loaded model is cached on the instance
for subsequent calls.
"""

from transformers import pipeline, Pipeline

from summarization.base_summarizer import BaseSummarizer, SummarizationError
from utils.constants import (
    SummaryLength,
    ABSTRACTIVE_TOKEN_LIMITS,
    DEFAULT_ABSTRACTIVE_MODEL,
)


class AbstractiveSummarizer(BaseSummarizer):
    """
    Summarizes text by generating new sentences using a Transformer model.

    The underlying model is loaded from the HuggingFace Hub on first use.
    Subsequent calls reuse the cached pipeline for performance.

    Usage:
        summarizer = AbstractiveSummarizer(model_name="facebook/bart-large-cnn")
        summary = summarizer.summarize(text, SummaryLength.MEDIUM)
    """

    def __init__(self, model_name: str = DEFAULT_ABSTRACTIVE_MODEL):
        """
        Initializes the abstractive summarizer.

        Args:
            model_name: The HuggingFace model identifier string.
                        Defaults to 'facebook/bart-large-cnn'.
        """
        self.model_name = model_name
        self._pipeline: Pipeline | None = None

    def _load_pipeline(self) -> Pipeline:
        """
        Loads and caches the HuggingFace summarization pipeline.

        This is called lazily on the first summarization request.

        Returns:
            A loaded HuggingFace Pipeline object.

        Raises:
            SummarizationError: If the model cannot be loaded.
        """
        if self._pipeline is not None:
            return self._pipeline

        try:
            self._pipeline = pipeline(
                "summarization",
                model=self.model_name,
                tokenizer=self.model_name,
            )
            return self._pipeline
        except Exception as e:
            raise SummarizationError(
                f"Failed to load model '{self.model_name}'. "
                f"Ensure you have an internet connection for the first download. "
                f"Error: {e}"
            ) from e

    def summarize(self, text: str, length: SummaryLength) -> str:
        """
        Generates an abstractive summary using the loaded Transformer model.

        Args:
            text:   The input text to summarize.
            length: The desired summary length, which maps to min/max token limits.

        Returns:
            A string containing the generated abstractive summary.

        Raises:
            SummarizationError: If the model fails to generate a summary.
        """
        if not text or not text.strip():
            raise SummarizationError("Cannot summarize empty text.")

        token_limits = ABSTRACTIVE_TOKEN_LIMITS.get(
            length, ABSTRACTIVE_TOKEN_LIMITS[SummaryLength.MEDIUM]
        )
        min_tokens = token_limits["min"]
        max_tokens = token_limits["max"]

        try:
            nlp = self._load_pipeline()

            # Truncate input to the model's maximum token limit to prevent errors.
            # Most summarization models support up to 1024 tokens.
            result = nlp(
                text,
                min_length=min_tokens,
                max_length=max_tokens,
                do_sample=False,
                truncation=True,
            )

            if not result or not result[0].get("summary_text"):
                raise SummarizationError(
                    "The model returned an empty summary. "
                    "Try a different length setting or input text."
                )

            return result[0]["summary_text"].strip()

        except SummarizationError:
            raise
        except Exception as e:
            raise SummarizationError(
                f"Abstractive summarization failed: {e}"
            ) from e

    def reload_model(self, new_model_name: str) -> None:
        """
        Clears the cached pipeline and sets a new model for the next call.

        Args:
            new_model_name: The HuggingFace model identifier for the new model.
        """
        self._pipeline = None
        self.model_name = new_model_name
