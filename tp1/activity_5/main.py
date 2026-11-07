"""
main.py
=======
Activity V: Classical Tokenization vs Byte Pair Encoding (BPE).
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Single entrypoint executing:
  1. Simple Word Tokenizer (Classical word-level splitting and OOV analysis).
  2. Simple BPE (Step-by-step pedagogical merge trace).
  3. Complete BPE:
     - Trains BPE merges from the constructed legal corpus.
     - Saves learned merges and subword vocabulary to disk.
     - Encodes unseen legal words (mandatory target: 'constitutionnalité').
  4. Three-way comparative evaluation matrix and formal report.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

CURRENT_DIR = Path(__file__).resolve().parent
TP1_DIR = CURRENT_DIR.parent
PROJECT_ROOT = TP1_DIR.parent

for path in [CURRENT_DIR, TP1_DIR, PROJECT_ROOT]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from simple_tokenizer import SimpleWordTokenizer
from simple_bpe import SimpleBPE
from complete_bpe import CompleteBPETokenizer
from comparator import TokenizationComparator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("activityFive")


def activityFive(
    corpus_path: Optional[Path | str] = None,
    model_save_path: Optional[Path | str] = None,
    num_merges: int = 350,
    test_word: str = "constitutionnalité",
) -> Dict[str, Any]:
    """Execute Activity V pipeline end-to-end.

    Naming conforms to the EMP NLP Lab 1 specification:
    'Developed functions must be named by the question number: activityOne, activityTwo, ..., activityFive'

    Args:
        corpus_path: Path to final preprocessed master corpus (default: tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt).
        model_save_path: Destination path for serialized BPE model (default: tp1/activity_5/models/bpe_model.json).
        num_merges: Number of BPE merges to learn (default: 350).
        test_word: Target legal word to test (default: 'constitutionnalité').

    Returns:
        Dictionary containing trained tokenizers, test word evaluations, and report paths.
    """
    c_path = Path(corpus_path) if corpus_path else TP1_DIR / "activity_3" / "final_corpus" / "algerian_legal_corpus_full.txt"
    m_path = Path(model_save_path) if model_save_path else CURRENT_DIR / "models" / "bpe_model.json"
    reports_dir = CURRENT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_txt_file = reports_dir / "activity_5_bpe_tokenization_report.txt"

    print("\n" + "=" * 85)
    print(" EMP NLP LAB 1 - ACTIVITY V: CLASSICAL TOKENIZATION vs. BYTE PAIR ENCODING")
    print(f" Master Corpus Source : {c_path}")
    print(f" Target Merge Steps   : {num_merges}")
    print(f" Target Test Word     : '{test_word}'")
    print("=" * 85 + "\n")

    if not c_path.is_file():
        raise FileNotFoundError(f"Corpus file not found at {c_path}. Please run Activity III first.")

    corpus_text = c_path.read_text(encoding="utf-8", errors="replace")

    # ---------------------------------------------------------
    # STEP 1: Simple Classical Word Tokenizer
    # ---------------------------------------------------------
    print(">>> [STEP 1/3] Training and fitting Classical Word Tokenizer...")
    classical_tokenizer = SimpleWordTokenizer(lowercase=True)
    # Fit with max vocab size to intentionally create a realistic finite dictionary
    classical_tokenizer.fit(corpus_text, max_vocab_size=15000)
    print(f"✔ Classical Tokenizer fitted (Vocab Size: {len(classical_tokenizer.vocab):,})\n")

    # ---------------------------------------------------------
    # STEP 2: Simple BPE (Pedagogical Trace)
    # ---------------------------------------------------------
    print(">>> [STEP 2/3] Demonstrating Simple BPE fundamental merge loop...")
    simple_bpe = SimpleBPE(num_merges=15)
    simple_bpe.train_simple(corpus_text, max_words=5000)
    trace_table = simple_bpe.format_merge_trace()
    print(" Pedagogical Step-by-Step Merge Progression (Top 15 Merges):")
    print(trace_table)
    print("✔ Simple BPE demonstration complete.\n")

    # ---------------------------------------------------------
    # STEP 3: Complete BPE Tokenizer (Training & Persistence)
    # ---------------------------------------------------------
    print(f">>> [STEP 3/3] Training Complete BPE Tokenizer ({num_merges} merges) on full legal corpus...")
    complete_bpe = CompleteBPETokenizer(num_merges=num_merges)
    train_summary = complete_bpe.train(corpus_text=corpus_text, num_merges=num_merges)
    complete_bpe.save_model(m_path)
    print(f"✔ Complete BPE model serialized and saved to: {m_path}\n")

    # ---------------------------------------------------------
    # STEP 4: Mandatory Evaluation on 'constitutionnalité' & Battery
    # ---------------------------------------------------------
    print("=" * 85)
    print(f" EVALUATING TARGET LEGAL TEST WORD: '{test_word}'")
    print("=" * 85)
    target_eval = complete_bpe.test_legal_word(test_word)
    print(f"  • Input Word      : {target_eval['input_word']}")
    print(f"  • BPE Subwords    : {' + '.join(target_eval['subwords'])}")
    print(f"  • Subword Count   : {target_eval['subword_count']}")
    print(f"  • Subword Token IDs: {target_eval['token_ids']}")
    print(f"  • Reconstructed   : '{target_eval['reconstructed']}'")
    print(f"  • Perfect Match   : {target_eval['is_perfect_reconstruction']}\n")

    # Test battery of morphological variations
    test_battery = [
        test_word,
        "inconstitutionnalité",
        "décret",
        "anticonstitutionnel",
        "jurisprudence",
        "loi_organique",
        "superficie",
    ]

    comparator = TokenizationComparator(
        classical=classical_tokenizer,
        simple_bpe=simple_bpe,
        complete_bpe=complete_bpe,
    )
    comp_results = comparator.evaluate_test_words(test_battery)
    comp_table = comparator.format_comparison_table(comp_results)
    print(comp_table)

    # ---------------------------------------------------------
    # Generate and save full report
    # ---------------------------------------------------------
    report_lines = [
        "=" * 85,
        " ACTIVITY V: CLASSICAL TOKENIZATION vs. BYTE PAIR ENCODING (BPE) REPORT",
        "       Ecole Militaire Polytechnique - Natural Language Processing",
        "=" * 85,
        f" Target Test Word : {test_word}",
        f" BPE Merges Learned: {train_summary['num_merges_learned']}",
        f" Final BPE Vocabulary Size: {train_summary['vocab_size']}",
        "",
        " [1] SIMPLE BPE PEDAGOGICAL MERGE TRACE:",
        trace_table,
        "",
        " [2] TARGET WORD EVALUATION ('constitutionnalité'):",
        f"  • Input Word       : {target_eval['input_word']}",
        f"  • Subwords         : {' + '.join(target_eval['subwords'])}",
        f"  • Subword Token IDs: {target_eval['token_ids']}",
        f"  • Reconstructed    : '{target_eval['reconstructed']}'",
        "",
        " [3] THREE-WAY COMPARATIVE EVALUATION:",
        comp_table,
        "=" * 85,
    ]
    report_text = "\n".join(report_lines)
    report_txt_file.write_text(report_text, encoding="utf-8")
    print(f"✔ Full Activity V report written to: {report_txt_file}\n")

    return {
        "classical_tokenizer": classical_tokenizer,
        "simple_bpe": simple_bpe,
        "complete_bpe": complete_bpe,
        "target_eval": target_eval,
        "comp_results": comp_results,
        "report_txt_file": report_txt_file,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Activity V: Classical Tokenization vs Byte Pair Encoding (BPE)"
    )
    parser.add_argument("--corpus", type=str, default=None, help="Path to aggregated corpus file")
    parser.add_argument("--model", type=str, default=None, help="Path to save BPE model JSON")
    parser.add_argument("--merges", type=int, default=350, help="Number of BPE merges to train (default: 350)")
    parser.add_argument(
        "--word", type=str, default="constitutionnalité", help="Test legal word (default: constitutionnalité)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    activityFive(
        corpus_path=args.corpus,
        model_save_path=args.model,
        num_merges=args.merges,
        test_word=args.word,
    )

