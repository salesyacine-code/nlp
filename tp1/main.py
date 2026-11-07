"""
tp1/main.py
===========
Unified Master Pipeline Runner for NLP Lab N° 1.
"Legal Document Collection and BPE Tokenization"
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Orchestrates all 5 laboratory activities in strict sequence:
  - Activity I   : Legal texts extraction from JORADP (activityOne)
  - Activity II  : Basic preprocessing of the corpus (activityTwo)
  - Activity III : Advanced preprocessing and corpus construction (activityThree)
  - Activity IV  : Measure the effect of cleaning (activityFour)
  - Activity V   : Classical tokenization vs. Byte Pair Encoding (activityFive)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure all activity submodules can be imported
TP1_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TP1_ROOT.parent

for p in [TP1_ROOT, TP1_ROOT / "activity_1", TP1_ROOT / "activity_2",
         TP1_ROOT / "activity_3", TP1_ROOT / "activity_4", TP1_ROOT / "activity_5"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from activity_1.main import activityOne
from activity_2.main import activityTwo
from activity_3.main import activityThree
from activity_4.main import activityFour
from activity_5.main import activityFive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Lab1_MasterRunner")


def run_all_activities(year: int = 2024, count: int = 50, num_merges: int = 300) -> Dict[str, Any]:
    """Execute all five activities of the NLP Lab sequentially."""
    print("\n" + "=" * 90)
    print(" ECOLE MILITAIRE POLYTECHNIQUE - NLP LAB N° 1")
    print(" LEGAL DOCUMENT COLLECTION AND BYTE PAIR ENCODING (BPE) TOKENIZATION")
    print(" Instructor: Dr. M'hamed MATAOUI")
    print("=" * 90 + "\n")

    results: Dict[str, Any] = {}

    # Activity I
    print("\n>>> STARTING ACTIVITY I: JORADP EXTRACTION & DIAGNOSTICS")
    results["activity_1"] = activityOne(year=year, count=count, base_dir=TP1_ROOT / "activity_1")

    # Activity II
    print("\n>>> STARTING ACTIVITY II: BASIC PREPROCESSING")
    results["activity_2"] = activityTwo(
        input_dir=TP1_ROOT / "activity_1" / "extracted_texts",
        output_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
        lowercase=True,
    )

    # Activity III
    print("\n>>> STARTING ACTIVITY III: ADVANCED PREPROCESSING & CORPUS CONSTRUCTION")
    results["activity_3"] = activityThree(
        input_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
        output_dir=TP1_ROOT / "activity_3" / "final_corpus",
        ref_mode="bind",
        date_mode="token",
        num_mode="token",
    )

    # Activity IV
    print("\n>>> STARTING ACTIVITY IV: MEASURE THE EFFECT OF CLEANING")
    results["activity_4"] = activityFour(
        before_dir=TP1_ROOT / "activity_1" / "extracted_texts",
        after_dir=TP1_ROOT / "activity_3" / "final_corpus" / "texts",
        intermediate_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
    )

    # Activity V
    print("\n>>> STARTING ACTIVITY V: CLASSICAL TOKENIZATION vs. BYTE PAIR ENCODING")
    results["activity_5"] = activityFive(
        corpus_path=TP1_ROOT / "activity_3" / "final_corpus" / "algerian_legal_corpus_full.txt",
        model_save_path=TP1_ROOT / "activity_5" / "models" / "bpe_model.json",
        num_merges=num_merges,
        test_word="constitutionnalité",
    )

    print("\n" + "=" * 90)
    print(" ✔ ALL FIVE ACTIVITIES COMPLETED SUCCESSFULLY!")
    print("=" * 90 + "\n")
    return results


def parse_args() -> argparse.Namespace:
    """Parse CLI options for the master runner."""
    parser = argparse.ArgumentParser(description="EMP NLP Lab 1 Master Pipeline Runner")
    parser.add_argument("--activity", type=int, choices=[1, 2, 3, 4, 5], default=None,
                        help="Run a specific activity (1 to 5). Omit to run all.")
    parser.add_argument("--year", type=int, default=2024, help="JORADP gazette publication year (default: 2024)")
    parser.add_argument("--count", type=int, default=50, help="Number of gazette issues (default: 50)")
    parser.add_argument("--merges", type=int, default=300, help="Number of BPE merges (default: 300)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.activity == 1:
        activityOne(year=args.year, count=args.count, base_dir=TP1_ROOT / "activity_1")
    elif args.activity == 2:
        activityTwo(
            input_dir=TP1_ROOT / "activity_1" / "extracted_texts",
            output_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
        )
    elif args.activity == 3:
        activityThree(
            input_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
            output_dir=TP1_ROOT / "activity_3" / "final_corpus",
        )
    elif args.activity == 4:
        activityFour(
            before_dir=TP1_ROOT / "activity_1" / "extracted_texts",
            after_dir=TP1_ROOT / "activity_3" / "final_corpus" / "texts",
            intermediate_dir=TP1_ROOT / "activity_2" / "cleaned_texts",
        )
    elif args.activity == 5:
        activityFive(
            corpus_path=TP1_ROOT / "activity_3" / "final_corpus" / "algerian_legal_corpus_full.txt",
            model_save_path=TP1_ROOT / "activity_5" / "models" / "bpe_model.json",
            num_merges=args.merges,
            test_word="constitutionnalité",
        )
    else:
        run_all_activities(year=args.year, count=args.count, num_merges=args.merges)

