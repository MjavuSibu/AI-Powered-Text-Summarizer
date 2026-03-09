"""
processing/text_chunker.py
==========================
Splits long documents into smaller, overlapping chunks so they can be
processed by AI models that have a limited context window.

The chunker splits on paragraph and sentence boundaries to preserve
semantic coherence, rather than cutting arbitrarily mid-sentence.
"""

import re
from utils.constants import CHUNK_SIZE_WORDS


class TextChunker:
    """
    Splits a long text into a list of smaller text chunks.

    Each chunk stays within a configurable word limit. The chunker
    respects paragraph and sentence boundaries to maintain readability
    and coherence in each chunk.

    Usage:
        chunker = TextChunker(chunk_size=500)
        chunks = chunker.chunk("Very long text here...")
    """

    def __init__(self, chunk_size: int = CHUNK_SIZE_WORDS):
        """
        Initializes the TextChunker.

        Args:
            chunk_size: The maximum number of words per chunk.
        """
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        """
        Splits the input text into a list of chunks.

        If the text is short enough to fit in a single chunk, a list
        containing only the original text is returned. Otherwise, the
        text is split by paragraphs first, then by sentences if a
        single paragraph exceeds the chunk size.

        Args:
            text: The full input text to be chunked.

        Returns:
            A list of text chunk strings.
        """
        if not text or not text.strip():
            return []

        word_count = len(text.split())
        if word_count <= self.chunk_size:
            return [text.strip()]

        paragraphs = self._split_into_paragraphs(text)
        chunks = self._build_chunks(paragraphs)
        return chunks

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """
        Splits text into a list of non-empty paragraphs.

        Args:
            text: The full input text.

        Returns:
            A list of paragraph strings.
        """
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_into_sentences(self, paragraph: str) -> list[str]:
        """
        Splits a paragraph into individual sentences.

        Uses a simple regex pattern that handles common sentence-ending
        punctuation (., !, ?) followed by whitespace.

        Args:
            paragraph: A single paragraph string.

        Returns:
            A list of sentence strings.
        """
        sentence_endings = re.compile(r"(?<=[.!?])\s+")
        sentences = sentence_endings.split(paragraph)
        return [s.strip() for s in sentences if s.strip()]

    def _build_chunks(self, paragraphs: list[str]) -> list[str]:
        """
        Assembles paragraphs into chunks that do not exceed the word limit.

        If a single paragraph is larger than the chunk size, it is further
        split into sentences and those sentences are grouped into chunks.

        Args:
            paragraphs: A list of paragraph strings.

        Returns:
            A list of assembled text chunks.
        """
        chunks: list[str] = []
        current_chunk_parts: list[str] = []
        current_word_count = 0

        for paragraph in paragraphs:
            para_word_count = len(paragraph.split())

            # If a single paragraph is too large, split it by sentences.
            if para_word_count > self.chunk_size:
                # First, flush the current chunk buffer.
                if current_chunk_parts:
                    chunks.append("\n\n".join(current_chunk_parts))
                    current_chunk_parts = []
                    current_word_count = 0

                sentences = self._split_into_sentences(paragraph)
                sentence_buffer: list[str] = []
                sentence_word_count = 0

                for sentence in sentences:
                    s_words = len(sentence.split())
                    if sentence_word_count + s_words > self.chunk_size and sentence_buffer:
                        chunks.append(" ".join(sentence_buffer))
                        sentence_buffer = []
                        sentence_word_count = 0
                    sentence_buffer.append(sentence)
                    sentence_word_count += s_words

                if sentence_buffer:
                    chunks.append(" ".join(sentence_buffer))

            # Otherwise, add the paragraph to the current chunk if it fits.
            elif current_word_count + para_word_count > self.chunk_size:
                if current_chunk_parts:
                    chunks.append("\n\n".join(current_chunk_parts))
                current_chunk_parts = [paragraph]
                current_word_count = para_word_count
            else:
                current_chunk_parts.append(paragraph)
                current_word_count += para_word_count

        # Flush any remaining content in the buffer.
        if current_chunk_parts:
            chunks.append("\n\n".join(current_chunk_parts))

        return [c for c in chunks if c.strip()]
