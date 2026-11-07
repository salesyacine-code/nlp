"""
main.py
=======
Activity II: Preprocessing of the Corpus.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Single entrypoint executing:
  1. Inspecting examples of extracted text with extraction anomalies.
  2. Batch basic preprocessing across all 50 documents:
     - Header and Footer removal
     - Page numbers removal
     - Line breaks normalization
     - Disambiguated PDF hyphenation
     - Apostrophes & Quotation marks normalization
     - Case normalization
  3. Generating side-by-side inspection report and quantitative reduction summary.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

CURRENT_DIR = Path(__file__).resolve().parent
TP1_DIR = CURRENT_DIR.parent
PROJECT_ROOT = TP1_DIR.parent

for path in [CURRENT_DIR, TP1_DIR, PROJECT_ROOT]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from preprocessor import CorpusPreprocessor
from cleaner import BatchCorpusCleaner, BatchCleaningReport
from inspector import CorpusInspector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("activityTwo")


def activityTwo(
    input_dir: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    lowercase: bool = True,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute Activity II pipeline end-to-end.

    Naming conforms to the EMP NLP Lab 1 specification:
    'Developed functions must be named by the question number: activityOne, activityTwo...'

    Args:
        input_dir: Directory containing raw extracted texts (default: tp1/activity_1/extracted_texts).
        output_dir: Destination directory for cleaned texts (default: tp1/activity_2/cleaned_texts).
        lowercase: Whether to apply Unicode case normalization (default: True).
        limit: Optional limit on number of documents to clean (default: all).

    Returns:
        Dictionary containing cleaning report, inspection report, and summary statistics.
    """
    in_path = Path(input_dir) if input_dir else TP1_DIR / "activity_1" / "extracted_texts"
    out_path = Path(output_dir) if output_dir else CURRENT_DIR / "cleaned_texts"
    reports_dir = CURRENT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    inspection_report_path = reports_dir / "preprocessing_inspection_report.txt"
    summary_report_path = reports_dir / "cleaning_summary.json"

    print("\n" + "=" * 80)
    print(" EMP NLP LAB 1 - ACTIVITY II: BASIC CORPUS PREPROCESSING")
    print(f" Input Directory  : {in_path}")
    print(f" Output Directory : {out_path}")
    print(f" Case Lowercasing : {lowercase}")
    print("=" * 80 + "\n")

    # ---------------------------------------------------------
    # STEP 1: Qualitative Visual Inspection (Before vs After)
    # ---------------------------------------------------------
    print(">>> [STEP 1/2] Inspecting extraction anomalies & generating visual evidence report...")
    inspector = CorpusInspector(preprocessor=CorpusPreprocessor(lowercase_by_default=lowercase))
    inspection_text = inspector.create_inspection_report(
        raw_dir=in_path, target_report_path=inspection_report_path
    )
    print(inspection_text)
    print(f"✔ Step 1 Complete: Inspection evidence written to {inspection_report_path}\n")

    # ---------------------------------------------------------
    # STEP 2: Batch Corpus Cleaning Across All Documents
    # ---------------------------------------------------------
    print(">>> [STEP 2/2] Applying full preprocessing pipeline to corpus documents...")
    cleaner = BatchCorpusCleaner(
        input_dir=in_path,
        output_dir=out_path,
        lowercase=lowercase,
    )
    cleaning_report = cleaner.clean_all(limit=limit)
    cleaner.save_report(cleaning_report, target_path=summary_report_path)

    print("\n" + "-" * 80)
    print(" BASIC PREPROCESSING SUMMARY METRICS:")
    print("-" * 80)
    print(f"  • Total Documents Processed : {cleaning_report.total_documents}")
    print(
        f"  • Total Raw Characters      : {cleaning_report.total_raw_characters:,} -> "
        f"{cleaning_report.total_clean_characters:,} ({cleaning_report.overall_char_reduction_pct:+.2f}% net noise removed)"
    )
    print(
        f"  • Total Lines               : {cleaning_report.total_raw_lines:,} -> "
        f"{cleaning_report.total_clean_lines:,} ({cleaning_report.overall_line_reduction_pct:+.2f}% lines consolidated into cohesive sentences)"
    )
    print(f"✔ Step 2 Complete: Cleaned texts written to {out_path}")
    print(f"✔ Summary JSON written to {summary_report_path}")
    print("=" * 80 + "\n")

    return {
        "cleaning_report": cleaning_report,
        "inspection_report_path": inspection_report_path,
        "summary_report_path": summary_report_path,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Activity II: Basic Corpus Preprocessing")
    parser.add_argument("--input", type=str, default=None, help="Input directory of extracted texts")
    parser.add_argument("--output", type=str, default=None, help="Output directory for cleaned texts")
    parser.add_argument("--no-lower", action="store_true", help="Do not lowercase text")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    activityTwo(
        input_dir=args.input,
        output_dir=args.output,
        lowercase=not args.no_lower,
        limit=args.limit,
    )

