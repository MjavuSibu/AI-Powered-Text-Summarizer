"""
export/pdf_exporter.py
=======================
Exports a generated summary to a professionally formatted PDF document
using the ReportLab library.

The exported PDF includes:
    - A branded header with the application name and generation timestamp.
    - Metadata: summarization method, length setting, and word counts.
    - The full summary body text.
    - A footer with the page number and source application.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from utils.constants import APP_NAME, APP_VERSION


# Brand colors (matching the deep peach palette).
PEACH_COLOR = colors.HexColor("#E8673A")
PEACH_LIGHT = colors.HexColor("#FFF0E8")
TEXT_DARK   = colors.HexColor("#1A0F0A")
TEXT_MUTED  = colors.HexColor("#9C7060")
WHITE       = colors.white


class PdfExporter:
    """
    Generates a formatted PDF document from a summary result.

    Usage:
        exporter = PdfExporter()
        exporter.export(
            output_path="summary.pdf",
            summary_text="...",
            method="Abstractive (BART)",
            length="Medium",
            original_word_count=1200,
            summary_word_count=180,
        )
    """

    def export(
        self,
        output_path: str,
        summary_text: str,
        method: str,
        length: str,
        original_word_count: int,
        summary_word_count: int,
        original_title: str = "Untitled Document",
    ) -> None:
        """
        Generates and saves a PDF file at the specified path.

        Args:
            output_path:         Full path where the PDF will be saved.
            summary_text:        The generated summary body text.
            method:              The summarization method used (display name).
            length:              The summary length setting used (display name).
            original_word_count: Word count of the original input text.
            summary_word_count:  Word count of the generated summary.
            original_title:      Optional title for the source document.

        Raises:
            OSError: If the file cannot be written to the specified path.
        """
        output_path = str(Path(output_path))

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = self._build_styles()
        story = self._build_story(
            styles=styles,
            summary_text=summary_text,
            method=method,
            length=length,
            original_word_count=original_word_count,
            summary_word_count=summary_word_count,
            original_title=original_title,
        )

        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

    def _build_styles(self) -> dict:
        """Builds and returns a dictionary of custom paragraph styles."""
        base = getSampleStyleSheet()

        styles = {
            "app_name": ParagraphStyle(
                "AppName",
                fontSize=9,
                textColor=PEACH_COLOR,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                spaceAfter=2,
            ),
            "title": ParagraphStyle(
                "Title",
                fontSize=20,
                textColor=TEXT_DARK,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                spaceAfter=4,
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                fontSize=11,
                textColor=TEXT_MUTED,
                fontName="Helvetica",
                alignment=TA_LEFT,
                spaceAfter=8,
            ),
            "section_heading": ParagraphStyle(
                "SectionHeading",
                fontSize=10,
                textColor=TEXT_MUTED,
                fontName="Helvetica-Bold",
                alignment=TA_LEFT,
                spaceBefore=8,
                spaceAfter=4,
                textTransform="uppercase",
            ),
            "body": ParagraphStyle(
                "Body",
                fontSize=11,
                textColor=TEXT_DARK,
                fontName="Helvetica",
                alignment=TA_LEFT,
                leading=18,
                spaceAfter=6,
            ),
        }
        return styles

    def _build_story(
        self,
        styles: dict,
        summary_text: str,
        method: str,
        length: str,
        original_word_count: int,
        summary_word_count: int,
        original_title: str,
    ) -> list:
        """Assembles the list of ReportLab flowables that make up the document."""
        story = []
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        compression = 0
        if original_word_count > 0:
            compression = round((1 - summary_word_count / original_word_count) * 100)

        # --- Header ---
        story.append(Paragraph(APP_NAME.upper(), styles["app_name"]))
        story.append(Paragraph("AI-Generated Summary", styles["title"]))
        story.append(Paragraph(f"Generated on {timestamp}", styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=PEACH_COLOR, spaceAfter=12))

        # --- Metadata Table ---
        story.append(Paragraph("Summary Details", styles["section_heading"]))
        meta_data = [
            ["Source Document", original_title],
            ["Summarization Method", method],
            ["Summary Length", length],
            ["Original Word Count", f"{original_word_count:,} words"],
            ["Summary Word Count", f"{summary_word_count:,} words"],
            ["Compression Ratio", f"{compression}% reduction"],
        ]
        meta_table = Table(meta_data, colWidths=[55 * mm, 110 * mm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("FONTNAME",    (0, 0), (0, -1),  "Helvetica-Bold"),
            ("TEXTCOLOR",   (0, 0), (0, -1),  TEXT_MUTED),
            ("TEXTCOLOR",   (1, 0), (1, -1),  TEXT_DARK),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PEACH_LIGHT, WHITE]),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#F0E0D6")),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 12))

        # --- Summary Body ---
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#F0E0D6"), spaceAfter=8))
        story.append(Paragraph("Summary", styles["section_heading"]))

        for paragraph in summary_text.split("\n\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), styles["body"]))

        return story

    @staticmethod
    def _add_footer(canvas, doc):
        """Draws the page footer on each page of the document."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(TEXT_MUTED)
        footer_text = f"{APP_NAME} v{APP_VERSION}  |  Page {doc.page}"
        canvas.drawString(20 * mm, 12 * mm, footer_text)
        canvas.restoreState()
