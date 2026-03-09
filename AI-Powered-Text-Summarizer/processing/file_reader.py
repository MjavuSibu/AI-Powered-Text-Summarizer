"""
processing/file_reader.py
=========================
Provides a unified interface for reading text content from supported
file types (.txt and .pdf).

All reading operations return a plain string, and errors are surfaced
as descriptive exceptions so the GUI can display helpful messages.
"""

from pathlib import Path
import pdfplumber

from utils.constants import SUPPORTED_FILE_EXTENSIONS, MAX_FILE_SIZE_MB
from utils.helpers import clean_text, get_file_size_mb


class FileReadError(Exception):
    """Raised when a file cannot be read or its content cannot be extracted."""
    pass


class FileReader:
    """
    Reads the text content of .txt and .pdf files.

    Usage:
        reader = FileReader()
        text = reader.read("path/to/document.pdf")
    """

    def read(self, file_path: str) -> str:
        """
        Reads a file and returns its cleaned text content.

        Dispatches to the appropriate reader based on the file extension.

        Args:
            file_path: The absolute or relative path to the file.

        Returns:
            A cleaned string containing the full text content of the file.

        Raises:
            FileReadError: If the file is not found, is too large, has an
                           unsupported extension, or cannot be parsed.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileReadError(f"File not found: {path.name}")

        extension = path.suffix.lower()
        if extension not in SUPPORTED_FILE_EXTENSIONS:
            raise FileReadError(
                f"Unsupported file type '{extension}'. "
                f"Supported types are: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
            )

        size_mb = get_file_size_mb(path)
        if size_mb > MAX_FILE_SIZE_MB:
            raise FileReadError(
                f"File is too large ({size_mb:.1f} MB). "
                f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
            )

        if extension == ".txt":
            return self._read_txt(path)
        elif extension == ".pdf":
            return self._read_pdf(path)

        # This line should never be reached given the extension check above.
        raise FileReadError(f"Cannot process file: {path.name}")

    def _read_txt(self, path: Path) -> str:
        """
        Reads a plain text file with UTF-8 encoding.

        Args:
            path: A Path object pointing to the .txt file.

        Returns:
            The cleaned text content of the file.
        """
        try:
            raw_text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            raise FileReadError(f"Could not read file '{path.name}': {e}") from e

        cleaned = clean_text(raw_text)
        if not cleaned:
            raise FileReadError(f"The file '{path.name}' appears to be empty.")

        return cleaned

    def _read_pdf(self, path: Path) -> str:
        """
        Extracts text from a PDF file using pdfplumber.

        Iterates through all pages and concatenates their text content.

        Args:
            path: A Path object pointing to the .pdf file.

        Returns:
            The cleaned, concatenated text from all pages of the PDF.
        """
        try:
            with pdfplumber.open(path) as pdf:
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)

                if not pages_text:
                    raise FileReadError(
                        f"No readable text found in '{path.name}'. "
                        "The PDF may be image-based and require OCR."
                    )

                raw_text = "\n\n".join(pages_text)
        except FileReadError:
            raise
        except Exception as e:
            raise FileReadError(
                f"Failed to parse PDF '{path.name}': {e}"
            ) from e

        return clean_text(raw_text)
