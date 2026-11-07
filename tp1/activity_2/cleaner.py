"""
cleaner.py
==========
Activity II - Part 2: Batch Corpus Cleaner.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Applies CorpusPreprocessor to all extracted gazette text files in batch,
persisting the cleaned corpus to disk and quantifying the reduction in size/noise.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from preprocessor import CorpusPreprocessor

logger = logging.getLogger("activity_2.cleaner")


@dataclass
class DocumentCleaningStats:
    """Pre- and post-cleaning metrics for a single legal document."""
    doc_id: str
    raw_chars: int = 0
    clean_chars: int = 0
    char_reduction_pct: float = 0.0
    raw_lines: int = 0
    clean_lines: int = 0
    line_reduction_pct: float = 0.0


@dataclass
class BatchCleaningReport:
    """Aggregate statistics for batch preprocessing across the corpus."""
    total_documents: int = 0
    total_raw_characters: int = 0
    total_clean_characters: int = 0
    overall_char_reduction_pct: float = 0.0
    total_raw_lines: int = 0
    total_clean_lines: int = 0
    overall_line_reduction_pct: float = 0.0
    document_stats: List[DocumentCleaningStats] = field(default_factory=list)


class BatchCorpusCleaner:
    """Orchestrates batch preprocessing over extracted legal text files."""

    def __init__(
        self,
        input_dir: Path | str = Path("tp1/activity_1/extracted_texts"),
        output_dir: Path | str = Path("tp1/activity_2/cleaned_texts"),
        lowercase: bool = True,
    ) -> None:
        """Initialize cleaner with input/output directories and case normalization flag."""
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.preprocessor: CorpusPreprocessor = CorpusPreprocessor(lowercase_by_default=lowercase)

    def clean_document_file(self, txt_path: Path) -> DocumentCleaningStats:
        """Read a single extracted text file, preprocess it, and save the result."""
        doc_id = txt_path.stem
        target_path = self.output_dir / txt_path.name

        raw_text = txt_path.read_text(encoding="utf-8", errors="replace")
        raw_chars = len(raw_text)
        raw_lines = raw_text.count("\n") + 1

        clean_text = self.preprocessor.preprocess_text(raw_text)
        clean_chars = len(clean_text)
        clean_lines = clean_text.count("\n") + 1

        target_path.write_text(clean_text, encoding="utf-8")

        char_red = ((raw_chars - clean_chars) / raw_chars * 100) if raw_chars > 0 else 0.0
        line_red = ((raw_lines - clean_lines) / raw_lines * 100) if raw_lines > 0 else 0.0

        stats = DocumentCleaningStats(
            doc_id=doc_id,
            raw_chars=raw_chars,
            clean_chars=clean_chars,
            char_reduction_pct=round(char_red, 2),
            raw_lines=raw_lines,
            clean_lines=clean_lines,
            line_reduction_pct=round(line_red, 2),
        )

        logger.debug(
            "Cleaned %s: %d -> %d chars (-%.1f%%), %d -> %d lines (-%.1f%%)",
            doc_id, raw_chars, clean_chars, char_red, raw_lines, clean_lines, line_red
        )
        return stats

    def clean_all(self, limit: Optional[int] = None) -> BatchCleaningReport:
        """Clean all text documents found in input_dir and generate aggregate summary report."""
        txt_files = sorted(self.input_dir.glob("*.txt"))
        if limit:
            txt_files = txt_files[:limit]

        if not txt_files:
            logger.warning("No .txt files found to clean in %s", self.input_dir)
            return BatchCleaningReport()

        logger.info("Found %d extracted text files in %s. Commencing basic preprocessing...", len(txt_files), self.input_dir)

        report = BatchCleaningReport(total_documents=len(txt_files))

        for file_path in txt_files:
            try:
                stats = self.clean_document_file(file_path)
                report.document_stats.append(stats)
                report.total_raw_characters += stats.raw_chars
                report.total_clean_characters += stats.clean_chars
                report.total_raw_lines += stats.raw_lines
                report.total_clean_lines += stats.clean_lines
            except Exception as exc:
                logger.error("Failed to clean %s: %s", file_path.name, exc)

        if report.total_raw_characters > 0:
            report.overall_char_reduction_pct = round(
                (report.total_raw_characters - report.total_clean_characters)
                / report.total_raw_characters * 100,
                2,
            )
        if report.total_raw_lines > 0:
            report.overall_line_reduction_pct = round(
                (report.total_raw_lines - report.total_clean_lines)
                / report.total_raw_lines * 100,
                2,
            )

        logger.info(
            "Batch preprocessing completed for %d documents:\n"
            "  • Characters : %s -> %s (-%.2f%%)\n"
            "  • Lines      : %s -> %s (-%.2f%%)",
            report.total_documents,
            f"{report.total_raw_characters:,}",
            f"{report.total_clean_characters:,}",
            report.overall_char_reduction_pct,
            f"{report.total_raw_lines:,}",
            f"{report.total_clean_lines:,}",
            report.overall_line_reduction_pct,
        )
        return report

    def save_report(
        self,
        report: BatchCleaningReport,
        target_path: Path | str = Path("tp1/activity_2/reports/cleaning_summary.json"),
    ) -> None:
        """Serialize cleaning report to JSON on disk."""
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Cleaning report saved to: %s", path.resolve())


def clean_corpus(
    input_dir: Path | str = Path("tp1/activity_1/extracted_texts"),
    output_dir: Path | str = Path("tp1/activity_2/cleaned_texts"),
    lowercase: bool = True,
) -> BatchCleaningReport:
    """Convenience functional wrapper for batch cleaning."""
    cleaner = BatchCorpusCleaner(input_dir=input_dir, output_dir=output_dir, lowercase=lowercase)
    report = cleaner.clean_all()
    cleaner.save_report(report)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    clean_corpus()

