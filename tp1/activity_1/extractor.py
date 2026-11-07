"""
extractor.py
============
Activity I - Part 2: Robust PDF Text Extraction via pypdf.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.

Extracts text content page-by-page from downloaded JORADP PDF gazettes,
inserting structured page boundary markers to retain physical layout traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pypdf

logger = logging.getLogger("activity_1.extractor")


@dataclass
class ExtractionSummary:
    """Statistical summary of text extraction across a single PDF document."""
    issue_name: str
    pdf_path: Path
    text_path: Path
    total_pages: int = 0
    extracted_pages: int = 0
    empty_pages: int = 0
    total_characters: int = 0
    errors: List[str] = field(default_factory=list)


class PDFTextExtractor:
    """Extracts raw text from legal PDF issues using pypdf.

    Attributes:
        input_dir (Path): Directory containing raw downloaded PDFs.
        output_dir (Path): Destination directory for extracted plain text files.
        page_delimiter_template (str): Formattable marker separating distinct PDF pages.
    """

    PAGE_DELIMITER_TEMPLATE: str = "\n\n--- PAGE_BREAK: {page_num} ---\n\n"

    def __init__(
        self,
        input_dir: Path | str = Path("activity_1/raw_pdfs"),
        output_dir: Path | str = Path("activity_1/extracted_texts"),
    ) -> None:
        """Initialize extractor with input and output directory paths."""
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_single_pdf(
        self, pdf_path: Path, force_reextract: bool = False
    ) -> ExtractionSummary:
        """Extract text from all pages of a single PDF file and persist as UTF-8 .txt.

        Args:
            pdf_path: Path to the target PDF file.
            force_reextract: If False, skips extraction when target .txt already exists.

        Returns:
            ExtractionSummary containing page counts, character totals, and error details.
        """
        issue_name = pdf_path.stem
        target_txt = self.output_dir / f"{issue_name}.txt"

        summary = ExtractionSummary(
            issue_name=issue_name,
            pdf_path=pdf_path,
            text_path=target_txt,
        )

        # Idempotency check: if already extracted and non-empty
        if not force_reextract and target_txt.is_file() and target_txt.stat().st_size > 0:
            logger.info("[Cached] Text for %s already extracted (%d bytes).", issue_name, target_txt.stat().st_size)
            # Read existing file to populate summary statistics
            try:
                content = target_txt.read_text(encoding="utf-8", errors="replace")
                summary.total_characters = len(content)
                summary.total_pages = content.count("--- PAGE_BREAK:")
                summary.extracted_pages = summary.total_pages
                return summary
            except OSError as err:
                logger.warning("Could not read cached %s: %s. Re-extracting.", target_txt, err)

        page_texts: List[str] = []

        try:
            reader = pypdf.PdfReader(str(pdf_path))
            summary.total_pages = len(reader.pages)

            # Handle password-protected or restricted PDFs with empty password
            if reader.is_encrypted:
                try:
                    decrypt_result = reader.decrypt("")
                    logger.debug("PDF %s is encrypted; decrypt result code: %s", issue_name, decrypt_result)
                except Exception as dec_err:
                    msg = f"Failed to decrypt {issue_name}: {dec_err}"
                    summary.errors.append(msg)
                    logger.warning(msg)

            for page_idx, page in enumerate(reader.pages, start=1):
                try:
                    raw_text = page.extract_text() or ""
                    clean_page_text = raw_text.strip()

                    if clean_page_text:
                        summary.extracted_pages += 1
                        delimiter = self.PAGE_DELIMITER_TEMPLATE.format(page_num=page_idx)
                        page_texts.append(f"{delimiter}{raw_text}")
                    else:
                        summary.empty_pages += 1
                        logger.debug("Page %d of %s is empty or scanned image only.", page_idx, issue_name)

                except Exception as page_err:
                    err_msg = f"Error extracting page {page_idx} of {issue_name}: {page_err}"
                    summary.errors.append(err_msg)
                    logger.warning(err_msg)

            full_text = "".join(page_texts).strip()
            summary.total_characters = len(full_text)

            # Save extracted text to disk with UTF-8 encoding
            target_txt.write_text(full_text, encoding="utf-8", errors="replace")
            logger.info(
                "Extracted %s: %d/%d pages (%d chars, %d empty) -> %s",
                issue_name,
                summary.extracted_pages,
                summary.total_pages,
                summary.total_characters,
                summary.empty_pages,
                target_txt.name,
            )

        except Exception as exc:
            err_msg = f"Fatal extraction failure for {issue_name}: {exc}"
            summary.errors.append(err_msg)
            logger.error(err_msg, exc_info=True)

        return summary

    def extract_all(self, force_reextract: bool = False) -> List[ExtractionSummary]:
        """Scan input directory, extract all .pdf documents, and return aggregate summaries.

        Args:
            force_reextract: Whether to re-extract documents that already have extracted .txt files.

        Returns:
            List of ExtractionSummary objects for all processed documents.
        """
        pdf_files = sorted(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF documents found in %s to extract.", self.input_dir.resolve())
            return []

        logger.info("Found %d PDF documents in %s. Commencing extraction...", len(pdf_files), self.input_dir)

        summaries: List[ExtractionSummary] = []
        for pdf_path in pdf_files:
            summary = self.extract_single_pdf(pdf_path, force_reextract=force_reextract)
            summaries.append(summary)

        total_extracted = sum(s.extracted_pages for s in summaries)
        total_chars = sum(s.total_characters for s in summaries)
        logger.info(
            "Batch extraction completed: %d files processed, %d total pages, %d total characters.",
            len(summaries),
            total_extracted,
            total_chars,
        )
        return summaries


def extract_texts(
    input_dir: Path | str = Path("activity_1/raw_pdfs"),
    output_dir: Path | str = Path("activity_1/extracted_texts"),
    force_reextract: bool = False,
) -> List[ExtractionSummary]:
    """Convenience functional wrapper for text extraction component."""
    extractor = PDFTextExtractor(input_dir=input_dir, output_dir=output_dir)
    return extractor.extract_all(force_reextract=force_reextract)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    extract_texts()

