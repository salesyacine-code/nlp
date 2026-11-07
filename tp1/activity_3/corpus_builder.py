"""
corpus_builder.py
=================
Activity III - Part 3: Final Legal Corpus Construction.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Applies advanced preprocessing to construct the final clean Algerian legal corpus:
  1. Processes all 50 gazette documents with optimal advanced settings:
     - Legal references: bound atomic entities (e.g., 'loi_n°_08-09', 'article_15_bis')
     - Dates: unified <DATE> tokens
     - Generic Numbers: <NUM> tokens
     - Metadata & URLs: completely stripped
  2. Saves individual processed documents to 'tp1/activity_3/final_corpus/texts/'.
  3. Builds an aggregated full-text corpus file: 'tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt'.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from advanced_preprocessor import AdvancedLegalPreprocessor

logger = logging.getLogger("activity_3.corpus_builder")


@dataclass
class FinalCorpusSummary:
    """Summary metrics of the fully constructed legal corpus."""
    total_documents: int = 0
    total_characters: int = 0
    total_words: int = 0
    total_lines: int = 0
    vocabulary_size: int = 0
    legal_references_bound_count: int = 0
    dates_normalized_count: int = 0
    numbers_normalized_count: int = 0
    aggregated_corpus_path: str = ""


class CorpusBuilder:
    """Constructs individual and aggregated final clean corpus files."""

    def __init__(
        self,
        input_dir: Path | str = Path("tp1/activity_2/cleaned_texts"),
        output_dir: Path | str = Path("tp1/activity_3/final_corpus"),
        ref_mode: str = "bind",
        date_mode: str = "token",
        num_mode: str = "token",
    ) -> None:
        """Initialize builder with paths and normalization modes."""
        self.input_dir: Path = Path(input_dir)
        self.output_dir: Path = Path(output_dir)
        self.texts_dir: Path = self.output_dir / "texts"
        self.texts_dir.mkdir(parents=True, exist_ok=True)

        self.ref_mode: str = ref_mode
        self.date_mode: str = date_mode
        self.num_mode: str = num_mode
        self.preprocessor: AdvancedLegalPreprocessor = AdvancedLegalPreprocessor()

    def build_corpus(self, limit: Optional[int] = None) -> FinalCorpusSummary:
        """Process all documents, persist individual texts and consolidated corpus."""
        txt_files = sorted(self.input_dir.glob("*.txt"))
        if limit:
            txt_files = txt_files[:limit]

        if not txt_files:
            logger.warning("No files found in %s to construct corpus.", self.input_dir)
            return FinalCorpusSummary()

        logger.info(
            "Building final corpus from %d documents in %s (ref=%s, date=%s, num=%s)...",
            len(txt_files),
            self.input_dir,
            self.ref_mode,
            self.date_mode,
            self.num_mode,
        )

        all_doc_texts: List[str] = []
        summary = FinalCorpusSummary(total_documents=len(txt_files))
        all_vocab: set[str] = set()

        for file_path in txt_files:
            try:
                raw_text = file_path.read_text(encoding="utf-8", errors="replace")

                # Count domain items prior to transformation for reporting
                summary.legal_references_bound_count += len(self.preprocessor._re_laws.findall(raw_text))
                summary.legal_references_bound_count += len(self.preprocessor._re_decrees.findall(raw_text))
                summary.legal_references_bound_count += len(self.preprocessor._re_articles.findall(raw_text))
                summary.dates_normalized_count += len(self.preprocessor._re_dual_date.findall(raw_text))
                summary.dates_normalized_count += len(self.preprocessor._re_gregorian_date.findall(raw_text))
                summary.numbers_normalized_count += len(self.preprocessor._re_generic_numbers.findall(raw_text))

                # Apply advanced processing
                clean_text = self.preprocessor.process_document(
                    text=raw_text,
                    ref_mode=self.ref_mode,
                    date_mode=self.date_mode,
                    num_mode=self.num_mode,
                )

                # Save individual file
                target_file = self.texts_dir / file_path.name
                target_file.write_text(clean_text, encoding="utf-8")

                all_doc_texts.append(clean_text)
                summary.total_characters += len(clean_text)
                summary.total_lines += clean_text.count("\n") + 1

                words = clean_text.split()
                summary.total_words += len(words)
                all_vocab.update(words)

            except Exception as exc:
                logger.error("Error constructing document %s: %s", file_path.name, exc)

        summary.vocabulary_size = len(all_vocab)

        # Build aggregated master corpus file
        agg_file = self.output_dir / "algerian_legal_corpus_full.txt"
        aggregated_text = "\n\n".join(all_doc_texts)
        agg_file.write_text(aggregated_text, encoding="utf-8")
        summary.aggregated_corpus_path = str(agg_file.resolve())

        # Save metadata summary
        meta_file = self.output_dir / "corpus_metadata.json"
        meta_file.write_text(json.dumps(asdict(summary), indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info(
            "Corpus construction complete:\n"
            "  • Total Documents : %d\n"
            "  • Total Words     : %s\n"
            "  • Vocabulary Size : %s\n"
            "  • Consolidated File: %s",
            summary.total_documents,
            f"{summary.total_words:,}",
            f"{summary.vocabulary_size:,}",
            agg_file.name,
        )
        return summary


def build_final_corpus(
    input_dir: Path | str = Path("tp1/activity_2/cleaned_texts"),
    output_dir: Path | str = Path("tp1/activity_3/final_corpus"),
    ref_mode: str = "bind",
    date_mode: str = "token",
    num_mode: str = "token",
) -> FinalCorpusSummary:
    """Convenience functional wrapper for corpus construction."""
    builder = CorpusBuilder(
        input_dir=input_dir,
        output_dir=output_dir,
        ref_mode=ref_mode,
        date_mode=date_mode,
        num_mode=num_mode,
    )
    return builder.build_corpus()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    build_final_corpus()

