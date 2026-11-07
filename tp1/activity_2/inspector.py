"""
inspector.py
============
Activity II - Part 3: Preprocessing Visual Inspector & Evidence Auditor.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Inspects raw vs. cleaned corpus text and extracts side-by-side evidence
for each required transformation:
  1. Header & Footer Removal
  2. Page Number Removal
  3. Hyphenation Disambiguation (Compound preservation vs. word recombination)
  4. Apostrophe Normalization
  5. Quotation Mark Normalization
  6. Line Break Normalization
  7. Case Normalization
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from preprocessor import CorpusPreprocessor

logger = logging.getLogger("activity_2.inspector")


@dataclass
class InspectionExample:
    """Pair of raw snippet vs cleaned snippet demonstrating a specific rule."""
    category: str
    doc_id: str
    raw_snippet: str
    cleaned_snippet: str
    explanation: str


class CorpusInspector:
    """Extracts qualitative inspection samples comparing raw text with preprocessed output."""

    def __init__(self, preprocessor: Optional[CorpusPreprocessor] = None) -> None:
        """Initialize inspector with a preprocessor instance."""
        self.preprocessor = preprocessor or CorpusPreprocessor(lowercase_by_default=True)

    def generate_inspection_examples(self, raw_text: str, doc_id: str = "Sample") -> List[InspectionExample]:
        """Extract illustrative Before vs. After snippets from a document text."""
        examples: List[InspectionExample] = []

        # 1. Header & Footer removal
        header_match = self.preprocessor._re_running_headers.search(raw_text)
        if header_match:
            raw_h = header_match.group(0).strip()
            clean_h = self.preprocessor.remove_headers_footers(raw_h).strip()
            examples.append(InspectionExample(
                category="1. Header and Footer Removal",
                doc_id=doc_id,
                raw_snippet=raw_h,
                cleaned_snippet=clean_h or "[COMPLETELY STRIPPED]",
                explanation="Running gazette masthead banner and date stamp eliminated to avoid skewed frequency counts."
            ))

        # 2. Page Number removal
        page_match = self.preprocessor._re_isolated_pagination.search(raw_text)
        if page_match:
            raw_p = page_match.group(0).strip()
            clean_p = self.preprocessor.remove_page_numbers(raw_p).strip()
            examples.append(InspectionExample(
                category="2. Page Number Removal",
                doc_id=doc_id,
                raw_snippet=f"Line: '{raw_p}'",
                cleaned_snippet=clean_p or "[COMPLETELY STRIPPED]",
                explanation="Isolated page digit removed so it does not pollute vocabulary or token frequency."
            ))

        # 3. PDF Hyphenation - Preserved compound vs merged split
        hyph_matches = list(self.preprocessor._re_hyphen_split.finditer(raw_text))
        for hm in hyph_matches[:2]:
            raw_hyph = hm.group(0)
            clean_hyph = self.preprocessor.handle_hyphenation(raw_hyph)
            is_compound = "-" in clean_hyph
            rule_type = "PRESERVED COMPOUND" if is_compound else "MERGED BROKEN WORD"
            examples.append(InspectionExample(
                category=f"3. PDF Hyphenation Disambiguation ({rule_type})",
                doc_id=doc_id,
                raw_snippet=raw_hyph.replace("\n", " ⏎ "),
                cleaned_snippet=clean_hyph,
                explanation=(
                    f"'{clean_hyph}' recognized as legitimate French compound word; hyphen kept intact."
                    if is_compound else
                    f"'{clean_hyph}' recognized as a split single word broken by column layout; recombined."
                )
            ))

        # 4. Apostrophe Normalization
        apo_matches = list(self.preprocessor._re_apostrophe_chars.finditer(raw_text))
        if apo_matches:
            m = apo_matches[0]
            start = max(0, m.start() - 25)
            end = min(len(raw_text), m.end() + 25)
            raw_apo = raw_text[start:end].replace("\n", " ")
            clean_apo = self.preprocessor.normalize_apostrophes(raw_apo)
            examples.append(InspectionExample(
                category="4. Apostrophe Normalization",
                doc_id=doc_id,
                raw_snippet=raw_apo,
                cleaned_snippet=clean_apo,
                explanation="Typographic/curly apostrophe ('’') normalized to standard ASCII apostrophe (''')."
            ))

        # 5. Quotation Marks Normalization
        quote_matches = list(self.preprocessor._re_quotes.finditer(raw_text))
        if quote_matches:
            m = quote_matches[0]
            start = max(0, m.start() - 30)
            end = min(len(raw_text), m.end() + 30)
            raw_q = raw_text[start:end].replace("\n", " ")
            clean_q = self.preprocessor.normalize_quotation_marks(raw_q)
            examples.append(InspectionExample(
                category="5. Quotation Marks Normalization",
                doc_id=doc_id,
                raw_snippet=raw_q,
                cleaned_snippet=clean_q,
                explanation="French guillemets (« ») and curly quotes converted to uniform ASCII double quote (\")."
            ))

        # 6. Line Breaks Normalization
        # Find 3 consecutive lines that should be joined
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip() and not ln.startswith("---")]
        for i in range(len(lines) - 2):
            l1, l2, l3 = lines[i], lines[i + 1], lines[i + 2]
            if (
                not l1.endswith((".", ":", ";"))
                and not self.preprocessor._re_structural_start.match(l2)
                and len(l1) > 20
                and len(l2) > 20
            ):
                raw_chunk = f"{l1}\n{l2}\n{l3}"
                clean_chunk = self.preprocessor.normalize_line_breaks(raw_chunk)
                examples.append(InspectionExample(
                    category="6. Line Breaks Normalization (Paragraph Flow)",
                    doc_id=doc_id,
                    raw_snippet=raw_chunk.replace("\n", " ⏎ \n  "),
                    cleaned_snippet=clean_chunk,
                    explanation="PDF column-wrap line breaks joined into a fluent continuous sentence."
                ))
                break

        # 7. Case Normalization
        upper_snippet = ""
        for line in lines:
            if any(ch in line for ch in "ÉÈÀÇÊÎÔÛ") and len(line) > 25:
                upper_snippet = line
                break
        if upper_snippet:
            clean_case = self.preprocessor.normalize_case(upper_snippet)
            examples.append(InspectionExample(
                category="7. Case Normalization (Unicode Lowercasing)",
                doc_id=doc_id,
                raw_snippet=upper_snippet,
                cleaned_snippet=clean_case,
                explanation="Uppercase accented French characters (É, È, À, Ç) lowercased with full Unicode fidelity."
            ))

        return examples

    def create_inspection_report(
        self,
        raw_dir: Path | str = Path("tp1/activity_1/extracted_texts"),
        target_report_path: Path | str = Path("tp1/activity_2/reports/preprocessing_inspection_report.txt"),
    ) -> str:
        """Scan sample files, collect comprehensive examples, and write formatted report."""
        raw_path = Path(raw_dir)
        report_file = Path(target_report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)

        sample_files = sorted(raw_path.glob("*.txt"))[:5]
        all_examples: List[InspectionExample] = []

        for s_file in sample_files:
            content = s_file.read_text(encoding="utf-8", errors="replace")
            examples = self.generate_inspection_examples(content, doc_id=s_file.stem)
            for ex in examples:
                # Add one example per category
                if not any(existing.category == ex.category for existing in all_examples):
                    all_examples.append(ex)

        # Format output
        report_lines: List[str] = [
            "=" * 82,
            "        ACTIVITY II: CORPUS PREPROCESSING VISUAL INSPECTION REPORT",
            "       Ecole Militaire Polytechnique - Natural Language Processing",
            "=" * 82,
            " Below is concrete empirical evidence of raw PDF extraction problems and their",
            " exact resolution through our basic preprocessing pipeline:\n",
        ]

        for idx, ex in enumerate(all_examples, start=1):
            report_lines.append(f"[{idx}] {ex.category.upper()}")
            report_lines.append(f"    • Source Document: {ex.doc_id}")
            report_lines.append("    • [BEFORE - Raw Extracted]:")
            report_lines.append(f"      {ex.raw_snippet}")
            report_lines.append("    • [AFTER - Preprocessed]:")
            report_lines.append(f"      {ex.cleaned_snippet}")
            report_lines.append(f"    • Linguistic/Algorithmic Note: {ex.explanation}")
            report_lines.append("-" * 82)

        report_lines.append("=" * 82)
        report_lines.append(" END OF PREPROCESSING INSPECTION REPORT")
        report_lines.append("=" * 82)

        formatted_report = "\n".join(report_lines)
        report_file.write_text(formatted_report, encoding="utf-8")
        logger.info("Saved visual inspection report to: %s", report_file.resolve())
        return formatted_report


def inspect_corpus(
    raw_dir: Path | str = Path("tp1/activity_1/extracted_texts"),
    report_path: Path | str = Path("tp1/activity_2/reports/preprocessing_inspection_report.txt"),
) -> str:
    """Convenience functional wrapper for corpus inspection."""
    inspector = CorpusInspector()
    return inspector.create_inspection_report(raw_dir=raw_dir, target_report_path=report_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print(inspect_corpus())

