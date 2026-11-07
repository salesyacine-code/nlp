"""
diagnostics.py
==============
Activity I - Part 3: Corpus Extraction Diagnostics Analyzer.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.

Scans the raw extracted text corpus to programmatically detect, quantify,
and sample 6 critical categories of PDF text extraction artifacts:
  a) Broken line breaks inside sentences.
  b) End-of-line word hyphenation splits.
  c) Repetitive running headers and footers.
  d) Isolated pagination numbers.
  e) Multiple consecutive and non-breaking spaces (\xa0).
  f) Two-column layout interleaving and horizontal reading-order artifacts.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("activity_1.diagnostics")


@dataclass
class AnomalyCategoryResult:
    """Diagnostic metrics and concrete snippets for a single anomaly category."""
    category_id: str
    description: str
    total_occurrences: int = 0
    affected_documents_count: int = 0
    concrete_snippets: List[str] = field(default_factory=list)


@dataclass
class CorpusDiagnosticReport:
    """Comprehensive diagnostic evaluation across the entire extracted corpus."""
    total_documents: int = 0
    total_characters: int = 0
    total_lines: int = 0
    categories: Dict[str, AnomalyCategoryResult] = field(default_factory=dict)


class CorpusDiagnosticsAnalyzer:
    """Analyzes raw extracted legal text files for layout and extraction anomalies."""

    def __init__(self, text_dir: Path | str = Path("activity_1/extracted_texts")) -> None:
        """Initialize analyzer with the path to the extracted texts directory."""
        self.text_dir: Path = Path(text_dir)

        # Regex patterns designed for French administrative/legal texts
        self.patterns = {
            # a) Broken line breaks: lowercase/comma/quote at EOL followed by newline and lowercase start
            "broken_line_breaks": re.compile(
                r"(?<=[a-zà-ÿ,\(\[\'\"])[\t ]*\n[\t ]*(?=[a-zà-ÿ])",
                re.UNICODE,
            ),
            # b) Hyphenation splits: word stem ending with '-' at EOL followed by remainder on next line
            "hyphenation_splits": re.compile(
                r"\b([a-zA-Zà-ÿÀ-Ÿ]{2,})[-—]\s*\n\s*([a-zA-Zà-ÿÀ-Ÿ]{2,})\b",
                re.UNICODE,
            ),
            # c) Repetitive headers & footers
            "running_headers_footers": re.compile(
                r"(?i)(?:journal\s+officiel\s+de\s+la\s+r[ée]publique\s+alg[ée]rienne|"
                r"jjoouurrnnaall\s+ooffffiicciieell|"
                r"imprimerie\s+officielle|"
                r"secr[ée]tariat\s+g[ée]n[ée]ral\s+du\s+gouvernement|"
                r"\d+.*joumada.*correspondant|"
                r"edition\s+originale,\s+le\s+num[ée]ro)",
                re.UNICODE,
            ),
            # d) Isolated pagination numbers: line consisting only of digits or 'Page X'
            "isolated_pagination": re.compile(
                r"(?m)^\s*(?:page\s+)?(\d{1,4})\s*$",
                re.UNICODE | re.IGNORECASE,
            ),
            # e1) Multiple consecutive spaces (>= 2 spaces)
            "multiple_spaces": re.compile(r"[ ]{2,}", re.UNICODE),
            # e2) Non-breaking and typographic spaces (\xa0, narrow no-break, etc.)
            "non_breaking_spaces": re.compile(r"[\xa0\u202f\u2009\u200a\u3000]", re.UNICODE),
            # f) Two-column layout interleaving: horizontal column bridge or wide gap between clauses
            "two_column_interleaving": re.compile(
                r"(?m)^([^\n]{15,45})\s{4,}([A-ZÀ-Ÿ][^\n]{15,45})$",
                re.UNICODE,
            ),
        }

    def analyze_document(self, text: str, doc_name: str) -> Dict[str, Dict[str, Any]]:
        """Extract occurrences and snippets for each anomaly category in a single document."""
        results: Dict[str, Dict[str, Any]] = {}

        # a) Broken line breaks
        matches_a = list(self.patterns["broken_line_breaks"].finditer(text))
        snippets_a: List[str] = []
        for m in matches_a[:3]:
            start = max(0, m.start() - 35)
            end = min(len(text), m.end() + 35)
            snippet = text[start:end].replace("\n", " ⏎ ")
            snippets_a.append(f"[{doc_name}] ...{snippet}...")
        results["broken_line_breaks"] = {"count": len(matches_a), "snippets": snippets_a}

        # b) Hyphenation splits
        matches_b = list(self.patterns["hyphenation_splits"].finditer(text))
        snippets_b: List[str] = []
        for m in matches_b[:3]:
            full_span = m.group(0).replace("\n", " ")
            reconstructed = f"{m.group(1)}{m.group(2)}"
            snippets_b.append(f"[{doc_name}] '{full_span}' -> [Reconstructed: {reconstructed}]")
        results["hyphenation_splits"] = {"count": len(matches_b), "snippets": snippets_b}

        # c) Running headers and footers
        matches_c = list(self.patterns["running_headers_footers"].finditer(text))
        snippets_c: List[str] = []
        for m in matches_c[:3]:
            line_start = text.rfind("\n", 0, m.start())
            line_end = text.find("\n", m.end())
            line_str = text[max(0, line_start + 1): line_end if line_end != -1 else len(text)].strip()
            snippets_c.append(f"[{doc_name}] {line_str[:90]}")
        results["running_headers_footers"] = {"count": len(matches_c), "snippets": snippets_c}

        # d) Isolated pagination
        matches_d = list(self.patterns["isolated_pagination"].finditer(text))
        snippets_d: List[str] = []
        for m in matches_d[:3]:
            val = m.group(0).strip()
            snippets_d.append(f"[{doc_name}] Isolated page marker line: '{val}'")
        results["isolated_pagination"] = {"count": len(matches_d), "snippets": snippets_d}

        # e) Multiple spaces and non-breaking spaces
        matches_e_mult = list(self.patterns["multiple_spaces"].finditer(text))
        matches_e_nbsp = list(self.patterns["non_breaking_spaces"].finditer(text))
        total_e = len(matches_e_mult) + len(matches_e_nbsp)
        snippets_e: List[str] = []
        for m in matches_e_mult[:2]:
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            clean_snip = text[start:end].replace(" ", "␣")
            snippets_e.append(f"[{doc_name}] Multi-space: ...{clean_snip}...")
        for m in matches_e_nbsp[:1]:
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            clean_snip = text[start:end].replace("\xa0", "[\\xa0_NBSP]")
            snippets_e.append(f"[{doc_name}] Non-breaking space: ...{clean_snip}...")
        results["spaces_and_non_breaking"] = {"count": total_e, "snippets": snippets_e}

        # f) Two-column layout interleaving
        matches_f = list(self.patterns["two_column_interleaving"].finditer(text))
        snippets_f: List[str] = []
        for m in matches_f[:3]:
            col1 = m.group(1).strip()
            col2 = m.group(2).strip()
            snippets_f.append(f"[{doc_name}] [Col1: '{col1}'] <==GAP==> [Col2: '{col2}']")
        results["two_column_interleaving"] = {"count": len(matches_f), "snippets": snippets_f}

        return results

    def analyze_corpus(self, sample_limit: Optional[int] = None) -> CorpusDiagnosticReport:
        """Scan all text files in the corpus directory and aggregate diagnostic measurements."""
        txt_files = sorted(self.text_dir.glob("*.txt"))
        if sample_limit:
            txt_files = txt_files[:sample_limit]

        report = CorpusDiagnosticReport(total_documents=len(txt_files))

        categories_meta = {
            "broken_line_breaks": "Broken Line Breaks Inside Sentences (hard newlines breaking syntactic flow)",
            "hyphenation_splits": "End-of-line Word Hyphenation Splits (e.g. 'admi- / nistration')",
            "running_headers_footers": "Repetitive Running Headers & Footers (official gazette stamps, banners)",
            "isolated_pagination": "Isolated Pagination Numbers (standalone digits / 'Page X' lines)",
            "spaces_and_non_breaking": "Multiple Consecutive Spaces and Non-Breaking Spaces (\\xa0, \\u202f)",
            "two_column_interleaving": "Two-Column Layout Interleaving & Reading Order Artifacts",
        }

        for cat_id, desc in categories_meta.items():
            report.categories[cat_id] = AnomalyCategoryResult(category_id=cat_id, description=desc)

        logger.info("Analyzing %d extracted text documents in %s...", len(txt_files), self.text_dir)

        for txt_path in txt_files:
            try:
                content = txt_path.read_text(encoding="utf-8", errors="replace")
                report.total_characters += len(content)
                report.total_lines += content.count("\n") + 1

                doc_res = self.analyze_document(content, txt_path.stem)

                for cat_id, data in doc_res.items():
                    cat_report = report.categories[cat_id]
                    count = data["count"]
                    if count > 0:
                        cat_report.total_occurrences += count
                        cat_report.affected_documents_count += 1
                        # Retain up to 3 diverse snippets per category across the corpus
                        if len(cat_report.concrete_snippets) < 3 and data["snippets"]:
                            for snip in data["snippets"]:
                                if len(cat_report.concrete_snippets) < 3:
                                    cat_report.concrete_snippets.append(snip)

            except Exception as exc:
                logger.error("Error analyzing %s: %s", txt_path.name, exc)

        return report

    def format_text_report(self, report: CorpusDiagnosticReport) -> str:
        """Render a clean, human-readable terminal and text report."""
        lines: List[str] = [
            "=" * 82,
            "           ACTIVITY I: JORADP TEXT EXTRACTION DIAGNOSTIC REPORT",
            "         Ecole Militaire Polytechnique - Natural Language Processing",
            "=" * 82,
            f" Total Analyzed Documents : {report.total_documents}",
            f" Total Corpus Characters   : {report.total_characters:,}",
            f" Total Lines Scanned       : {report.total_lines:,}",
            "-" * 82,
            " PROGRAMMATIC ANOMALY AUDIT (QUANTITATIVE & SAMPLES):",
            "-" * 82,
        ]

        letters = ["a", "b", "c", "d", "e", "f"]
        for idx, (cat_id, cat_data) in enumerate(report.categories.items()):
            letter = letters[idx] if idx < len(letters) else str(idx + 1)
            pct_docs = (
                (cat_data.affected_documents_count / report.total_documents * 100)
                if report.total_documents > 0
                else 0.0
            )
            lines.append(f"\n[{letter}] {cat_data.description}")
            lines.append(f"    • Total Occurrences Detected : {cat_data.total_occurrences:,}")
            lines.append(
                f"    • Affected Documents Count   : {cat_data.affected_documents_count}/{report.total_documents} ({pct_docs:.1f}%)"
            )
            lines.append("    • Concrete Extraction Snippets (Sample Evidence):")
            if cat_data.concrete_snippets:
                for s_idx, snippet in enumerate(cat_data.concrete_snippets, start=1):
                    lines.append(f"      [{s_idx}] {snippet}")
            else:
                lines.append("      (No occurrences detected)")

        lines.append("\n" + "=" * 82)
        lines.append(" END OF EXTRACTION DIAGNOSTICS REPORT")
        lines.append("=" * 82)
        return "\n".join(lines)

    def run_and_save_report(
        self, report_path: Path | str = Path("activity_1/reports/extraction_diagnostics_report.txt")
    ) -> CorpusDiagnosticReport:
        """Execute full corpus analysis and write formatted report to disk."""
        target_path = Path(report_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.analyze_corpus()
        formatted_text = self.format_text_report(report)
        target_path.write_text(formatted_text, encoding="utf-8")
        logger.info("Diagnostic report successfully generated and saved to: %s", target_path.resolve())

        # Also save JSON metadata summary
        json_path = target_path.with_suffix(".json")
        json_dict = {
            "total_documents": report.total_documents,
            "total_characters": report.total_characters,
            "total_lines": report.total_lines,
            "categories": {
                k: asdict(v) for k, v in report.categories.items()
            },
        }
        json_path.write_text(json.dumps(json_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        return report


def run_diagnostics(
    text_dir: Path | str = Path("activity_1/extracted_texts"),
    report_path: Path | str = Path("activity_1/reports/extraction_diagnostics_report.txt"),
) -> CorpusDiagnosticReport:
    """Convenience functional wrapper for diagnostics analyzer component."""
    analyzer = CorpusDiagnosticsAnalyzer(text_dir=text_dir)
    return analyzer.run_and_save_report(report_path=report_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_diagnostics()

