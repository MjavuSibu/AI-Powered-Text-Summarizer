"""
summarization/llm_api.py
=========================
LLM API summarization engine using the OpenAI API (or any compatible endpoint).

This engine sends the input text to an external LLM API and returns the
generated summary. It requires a valid API key, which is read from the
application configuration (sourced from the .env file).

The prompt is carefully engineered to instruct the model to produce
a clean, well-structured summary without unnecessary preamble.
"""

from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

from summarization.base_summarizer import BaseSummarizer, SummarizationError
from utils.constants import SummaryLength
from utils.config import config


# Prompt templates for each summary length.
_SYSTEM_PROMPT = (
    "You are an expert text summarizer. Your task is to produce a clear, "
    "accurate, and well-structured summary of the provided text. "
    "Write in complete sentences. Do not include any preamble, "
    "introductory phrases like 'This text discusses...', or meta-commentary. "
    "Output only the summary itself."
)

_LENGTH_INSTRUCTIONS = {
    SummaryLength.SHORT: (
        "Write a concise summary in 2-3 sentences capturing only the most "
        "essential information."
    ),
    SummaryLength.MEDIUM: (
        "Write a comprehensive summary in one paragraph (4-6 sentences) "
        "covering the main points and key details."
    ),
    SummaryLength.LONG: (
        "Write a detailed summary in 2-3 paragraphs covering the main points, "
        "supporting details, and any significant conclusions or implications."
    ),
}

DEFAULT_MODEL = "gpt-4o-mini"


class LLMApiSummarizer(BaseSummarizer):
    """
    Summarizes text by calling an external LLM API (OpenAI-compatible).

    Requires a valid OPENAI_API_KEY to be set in the .env file.

    Usage:
        summarizer = LLMApiSummarizer()
        summary = summarizer.summarize(text, SummaryLength.MEDIUM)
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initializes the LLM API summarizer.

        Args:
            model: The OpenAI model identifier to use. Defaults to 'gpt-4o-mini'.
        """
        self.model = model
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """
        Lazily initializes and returns the OpenAI client.

        Returns:
            An initialized OpenAI client instance.

        Raises:
            SummarizationError: If the API key is not configured.
        """
        if self._client is not None:
            return self._client

        api_key = config.openai_api_key
        if not api_key:
            raise SummarizationError(
                "OpenAI API key is not configured. "
                "Please add OPENAI_API_KEY to your .env file in the project root."
            )

        self._client = OpenAI(api_key=api_key)
        return self._client

    def summarize(self, text: str, length: SummaryLength) -> str:
        """
        Generates a summary by calling the OpenAI Chat Completions API.

        Args:
            text:   The input text to summarize.
            length: The desired summary length.

        Returns:
            A string containing the LLM-generated summary.

        Raises:
            SummarizationError: For API errors, authentication failures,
                                rate limits, or connection issues.
        """
        if not text or not text.strip():
            raise SummarizationError("Cannot summarize empty text.")

        length_instruction = _LENGTH_INSTRUCTIONS.get(
            length, _LENGTH_INSTRUCTIONS[SummaryLength.MEDIUM]
        )
        user_prompt = f"{length_instruction}\n\nText to summarize:\n\n{text}"

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )

            summary = response.choices[0].message.content
            if not summary or not summary.strip():
                raise SummarizationError(
                    "The API returned an empty response. Please try again."
                )

            return summary.strip()

        except SummarizationError:
            raise
        except AuthenticationError:
            raise SummarizationError(
                "Invalid OpenAI API key. Please check your .env file and "
                "ensure the key is correct and active."
            )
        except RateLimitError:
            raise SummarizationError(
                "OpenAI API rate limit exceeded. Please wait a moment and try again, "
                "or check your usage quota at platform.openai.com."
            )
        except APIConnectionError:
            raise SummarizationError(
                "Could not connect to the OpenAI API. "
                "Please check your internet connection and try again."
            )
        except Exception as e:
            raise SummarizationError(
                f"LLM API summarization failed: {e}"
            ) from e
