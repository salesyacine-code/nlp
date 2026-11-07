"""
main.py
=======
Activity IV: Measure the Effect of Cleaning.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Single entrypoint executing:
  1. Computing corpus statistics Before preprocessing (Activity I raw).
  2. Computing corpus statistics After preprocessing (Activity III final).
  3. Generating the official required comparative table and detailed analysis.
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

from evaluator import CleaningEffectEvaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("activityFour")


def activityFour(
    before_dir: Optional[Path | str] = None,
    after_dir: Optional[Path | str] = None,
    intermediate_dir: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Execute Activity IV pipeline end-to-end.

    Naming conforms to the EMP NLP Lab 1 specification:
    'Developed functions must be named by the question number: activityOne, activityTwo, activityThree, activityFour...'

    Args:
        before_dir: Directory containing raw extracted texts (default: tp1/activity_1/extracted_texts).
        after_dir: Directory containing final clean corpus texts (default: tp1/activity_3/final_corpus/texts).
        intermediate_dir: Directory containing basic cleaned texts (default: tp1/activity_2/cleaned_texts).

    Returns:
        Dictionary containing statistical measurements, comparative rows, and report file paths.
    """
    b_path = Path(before_dir) if before_dir else TP1_DIR / "activity_1" / "extracted_texts"
    a_path = Path(after_dir) if after_dir else TP1_DIR / "activity_3" / "final_corpus" / "texts"
    i_path = Path(intermediate_dir) if intermediate_dir else TP1_DIR / "activity_2" / "cleaned_texts"

    reports_dir = CURRENT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_txt_file = reports_dir / "corpus_cleaning_effect_report.txt"
    report_csv_file = reports_dir / "corpus_statistics_comparison.csv"

    print("\n" + "=" * 80)
    print(" EMP NLP LAB 1 - ACTIVITY IV: MEASURE THE EFFECT OF CLEANING")
    print(f" Before Directory       : {b_path}")
    print(f" Intermediate Directory : {i_path}")
    print(f" After Directory        : {a_path}")
    print("=" * 80 + "\n")

    evaluator = CleaningEffectEvaluator(
        before_dir=b_path,
        after_dir=a_path,
        intermediate_dir=i_path if i_path.is_dir() else None,
    )

    results = evaluator.run_evaluation(
        report_txt_path=report_txt_file,
        report_csv_path=report_csv_file,
    )

    print(results["formatted_report"])
    print(f"\n✔ Activity IV Complete: Report written to {report_txt_file}")
    print(f"✔ CSV Table written to {report_csv_file}\n")

    return results


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Activity IV: Measure the Effect of Cleaning on Corpus Statistics"
    )
    parser.add_argument("--before", type=str, default=None, help="Path to raw extracted texts directory")
    parser.add_argument("--after", type=str, default=None, help="Path to final cleaned corpus texts directory")
    parser.add_argument("--intermediate", type=str, default=None, help="Path to basic cleaned texts directory")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    activityFour(
        before_dir=args.before,
        after_dir=args.after,
        intermediate_dir=args.intermediate,
    )

