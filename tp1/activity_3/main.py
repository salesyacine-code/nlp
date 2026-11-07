"""
main.py
=======
Activity III: Advanced Preprocessing and Corpus Construction.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Single entrypoint executing:
  1. Controlled quantitative experiments comparing:
     - Numbers: Preserved vs Normalized vs Replaced with <NUM>
     - Dates: Preserved vs Normalized vs Replaced with <DATE>
     - Legal References: Unbound vs Bound (loi_n°_XX-YY) vs Special Tokens
  2. Construction of the final clean Algerian legal corpus:
     - Individual processed documents in tp1/activity_3/final_corpus/texts/
     - Single consolidated corpus file: tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt
  3. Generating full experimental and metadata reports.
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

from advanced_preprocessor import AdvancedLegalPreprocessor
from experiments import AdvancedPreprocessingExperiments, AdvancedExperimentReport
from corpus_builder import CorpusBuilder, FinalCorpusSummary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("activityThree")


def activityThree(
    input_dir: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    ref_mode: str = "bind",
    date_mode: str = "token",
    num_mode: str = "token",
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute Activity III pipeline end-to-end.

    Naming conforms to the EMP NLP Lab 1 specification:
    'Developed functions must be named by the question number: activityOne, activityTwo, activityThree...'

    Args:
        input_dir: Directory containing Activity II cleaned texts (default: tp1/activity_2/cleaned_texts).
        output_dir: Destination directory for final corpus (default: tp1/activity_3/final_corpus).
        ref_mode: Legal reference handling mode ('bind', 'token', 'standardize', 'preserve').
        date_mode: Date normalization mode ('token', 'normalize', 'preserve').
        num_mode: Number normalization mode ('token', 'normalize', 'preserve').
        limit: Optional document limit for testing.

    Returns:
        Dictionary containing experiment report, corpus summary, and generated file paths.
    """
    in_path = Path(input_dir) if input_dir else TP1_DIR / "activity_2" / "cleaned_texts"
    out_path = Path(output_dir) if output_dir else CURRENT_DIR / "final_corpus"
    reports_dir = CURRENT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    exp_report_path = reports_dir / "advanced_preprocessing_experiments.txt"

    print("\n" + "=" * 80)
    print(" EMP NLP LAB 1 - ACTIVITY III: ADVANCED PREPROCESSING & CORPUS CONSTRUCTION")
    print(f" Input Directory       : {in_path}")
    print(f" Output Directory      : {out_path}")
    print(f" Legal References Mode : {ref_mode}")
    print(f" Dates Mode            : {date_mode}")
    print(f" Numbers Mode          : {num_mode}")
    print("=" * 80 + "\n")

    # ---------------------------------------------------------
    # STEP 1: Controlled Strategy Experiments
    # ---------------------------------------------------------
    print(">>> [STEP 1/2] Running comparative strategy experiments across corpus...")
    exp_runner = AdvancedPreprocessingExperiments(input_dir=in_path)
    experiment_report = exp_runner.run_and_save_report(report_path=exp_report_path)
    print(exp_runner.format_text_report(experiment_report))
    print(f"\n✔ Step 1 Complete: Experimental results written to {exp_report_path}\n")

    # ---------------------------------------------------------
    # STEP 2: Final Legal Corpus Construction
    # ---------------------------------------------------------
    print(">>> [STEP 2/2] Constructing final preprocessed corpus with optimal configuration...")
    builder = CorpusBuilder(
        input_dir=in_path,
        output_dir=out_path,
        ref_mode=ref_mode,
        date_mode=date_mode,
        num_mode=num_mode,
    )
    corpus_summary = builder.build_corpus(limit=limit)

    print("\n" + "-" * 80)
    print(" FINAL CONSTRUCTED CORPUS METRICS:")
    print("-" * 80)
    print(f"  • Total Legal Documents        : {corpus_summary.total_documents}")
    print(f"  • Total Characters             : {corpus_summary.total_characters:,}")
    print(f"  • Total Words                  : {corpus_summary.total_words:,}")
    print(f"  • Total Lines                  : {corpus_summary.total_lines:,}")
    print(f"  • Vocabulary Size (|V|)        : {corpus_summary.vocabulary_size:,}")
    print(f"  • Bound Legal References       : {corpus_summary.legal_references_bound_count:,}")
    print(f"  • Normalized Dates             : {corpus_summary.dates_normalized_count:,}")
    print(f"  • Normalized Numbers           : {corpus_summary.numbers_normalized_count:,}")
    print(f"  • Aggregated Full Corpus File  : {corpus_summary.aggregated_corpus_path}")
    print(f"✔ Step 2 Complete: Final corpus built in {out_path}")
    print("=" * 80 + "\n")

    return {
        "experiment_report": experiment_report,
        "corpus_summary": corpus_summary,
        "experiment_report_path": exp_report_path,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Activity III: Advanced Preprocessing and Legal Corpus Construction"
    )
    parser.add_argument("--input", type=str, default=None, help="Input directory of cleaned texts")
    parser.add_argument("--output", type=str, default=None, help="Output directory for final corpus")
    parser.add_argument(
        "--ref-mode",
        type=str,
        default="bind",
        choices=["bind", "token", "standardize", "preserve"],
        help="Legal references mode (default: bind)",
    )
    parser.add_argument(
        "--date-mode",
        type=str,
        default="token",
        choices=["token", "normalize", "preserve"],
        help="Date normalization mode (default: token)",
    )
    parser.add_argument(
        "--num-mode",
        type=str,
        default="token",
        choices=["token", "normalize", "preserve"],
        help="Number normalization mode (default: token)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    activityThree(
        input_dir=args.input,
        output_dir=args.output,
        ref_mode=args.ref_mode,
        date_mode=args.date_mode,
        num_mode=args.num_mode,
        limit=args.limit,
    )

