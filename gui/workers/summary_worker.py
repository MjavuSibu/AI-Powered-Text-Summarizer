"""
gui/workers/summary_worker.py
==============================
A QThread-based background worker that runs the summarization pipeline
without blocking the main GUI thread.

By running the AI model inference in a separate thread, the application
remains responsive and can display a loading indicator while processing.

Signals emitted:
    - progress(str): A status message string for the loading overlay.
    - finished(str): The completed summary text on success.
    - error(str):    A user-friendly error message on failure.
"""

from PyQt6.QtCore import QThread, pyqtSignal

from summarization.extractive import ExtractiveSummarizer
from summarization.abstractive import AbstractiveSummarizer
from summarization.llm_api import LLMApiSummarizer
from summarization.base_summarizer import SummarizationError
from processing.text_chunker import TextChunker
from utils.constants import SummarizationMethod, SummaryLength
from utils.config import config


class SummaryWorker(QThread):
    """
    Background worker thread for running the summarization pipeline.

    This worker:
    1. Splits the input text into chunks (if necessary).
    2. Instantiates the correct summarization engine.
    3. Runs summarization on each chunk.
    4. Merges chunk summaries into a final result.
    5. Emits signals to update the GUI.

    Usage:
        worker = SummaryWorker(text, method, length)
        worker.finished.connect(on_summary_done)
        worker.error.connect(on_summary_error)
        worker.progress.connect(on_progress_update)
        worker.start()
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(
        self,
        text: str,
        method: SummarizationMethod,
        length: SummaryLength,
        parent=None,
    ):
        """
        Initializes the worker with the summarization parameters.

        Args:
            text:   The full input text to summarize.
            method: The summarization method to use.
            length: The desired summary length.
            parent: Optional Qt parent object.
        """
        super().__init__(parent)
        self.text = text
        self.method = method
        self.length = length

    def run(self) -> None:
        """
        Executes the summarization pipeline in the background thread.

        This method is called automatically by QThread.start().
        It emits `progress`, `finished`, or `error` signals as appropriate.
        """
        try:
            # Step 1: Chunk the text.
            self.progress.emit("Splitting document into chunks...")
            chunker = TextChunker()
            chunks = chunker.chunk(self.text)

            if not chunks:
                self.error.emit("The input text is empty or could not be processed.")
                return

            # Step 2: Select and initialize the summarizer.
            summarizer = self._build_summarizer()

            # Step 3: Summarize.
            if len(chunks) == 1:
                self.progress.emit(self._get_progress_message())
                summary = summarizer.summarize(chunks[0], self.length)
            else:
                self.progress.emit(
                    f"Processing {len(chunks)} chunks — this may take a moment..."
                )
                summary = summarizer.summarize_chunks(chunks, self.length)

            if not summary or not summary.strip():
                self.error.emit(
                    "The summarization engine returned an empty result. "
                    "Please try a different method or adjust the input text."
                )
                return

            self.finished.emit(summary.strip())

        except SummarizationError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(
                f"An unexpected error occurred during summarization: {e}"
            )

    def _build_summarizer(self):
        """
        Instantiates and returns the correct summarizer for the selected method.

        Returns:
            A BaseSummarizer subclass instance.
        """
        if self.method == SummarizationMethod.EXTRACTIVE:
            return ExtractiveSummarizer(algorithm=config.extractive_algorithm)
        elif self.method == SummarizationMethod.ABSTRACTIVE:
            return AbstractiveSummarizer(model_name=config.abstractive_model)
        elif self.method == SummarizationMethod.LLM_API:
            return LLMApiSummarizer()
        else:
            raise SummarizationError(f"Unknown summarization method: {self.method}")

    def _get_progress_message(self) -> str:
        """Returns a descriptive progress message for the current method."""
        messages = {
            SummarizationMethod.EXTRACTIVE: "Running NLP algorithm — scoring sentences...",
            SummarizationMethod.ABSTRACTIVE: "Running Transformer model — generating summary...",
            SummarizationMethod.LLM_API: "Calling LLM API — waiting for response...",
        }
        return messages.get(self.method, "Processing...")
