"""
comparator.py
=============
Activity V - Part 4: Three-Way Tokenization Approach Comparative Evaluator.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Contrasts:
  1. Classical Word-Level Tokenization
  2. Simple / Demonstrative BPE
  3. Complete Trained BPE Tokenizer
Across vocabulary efficiency, OOV resilience, morphological alignment, and sequence length.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from simple_tokenizer import SimpleWordTokenizer
from simple_bpe import SimpleBPE
from complete_bpe import CompleteBPETokenizer

logger = logging.getLogger("activity_5.comparator")


@dataclass
class WordComparisonResult:
    """Comparison result for a single test word across all three methods."""
    word: str
    classical_output: str
    classical_is_oov: bool
    simple_bpe_output: str
    complete_bpe_subwords: List[str]
    complete_bpe_output: str
    morphological_interpretation: str


class TokenizationComparator:
    """Orchestrates comprehensive side-by-side comparison across all three tokenization methods."""

    def __init__(
        self,
        classical: SimpleWordTokenizer,
        simple_bpe: SimpleBPE,
        complete_bpe: CompleteBPETokenizer,
    ) -> None:
        """Initialize with instances of all three tokenizer implementations."""
        self.classical = classical
        self.simple_bpe = simple_bpe
        self.complete_bpe = complete_bpe

    def evaluate_test_words(self, test_words: List[str]) -> List[WordComparisonResult]:
        """Evaluate a battery of target legal words across all three systems."""
        results: List[WordComparisonResult] = []

        for word in test_words:
            # 1. Classical
            class_res = self.classical.test_word(word)
            class_str = f"[{class_res['tokens'][0]}]" if not class_res["is_oov"] else "<UNK>"

            # 2. Simple BPE
            # Segment word using simple BPE's learned merges
            simple_pieces = list(word.lower()[:-1]) + [word.lower()[-1] + "</w>"]
            for pair, _ in self.simple_bpe.learned_merges:
                new_p = []
                i = 0
                while i < len(simple_pieces):
                    if i < len(simple_pieces) - 1 and (simple_pieces[i], simple_pieces[i + 1]) == pair:
                        new_p.append(pair[0] + pair[1])
                        i += 2
                    else:
                        new_p.append(simple_pieces[i])
                        i += 1
                simple_pieces = new_p
            simple_str = " + ".join(simple_pieces)

            # 3. Complete BPE
            bpe_res = self.complete_bpe.test_legal_word(word)
            bpe_subwords = bpe_res["subwords"]
            bpe_str = " + ".join(bpe_subwords)

            # Morphological analysis note
            if class_res["is_oov"]:
                morph_note = "Classical fails (<UNK>). Complete BPE recovers root and affixes without data loss."
            else:
                morph_note = "Classical matches single fixed word. Complete BPE exposes underlying subword morphemes."

            results.append(
                WordComparisonResult(
                    word=word,
                    classical_output=class_str,
                    classical_is_oov=class_res["is_oov"],
                    simple_bpe_output=simple_str,
                    complete_bpe_subwords=bpe_subwords,
                    complete_bpe_output=bpe_str,
                    morphological_interpretation=morph_note,
                )
            )

        return results

    def format_comparison_table(self, results: List[WordComparisonResult]) -> str:
        """Format the comparative results into a clean markdown and terminal table."""
        lines: List[str] = [
            "=" * 92,
            " ACTIVITY V: THREE-WAY TOKENIZATION COMPARISON ON ALGERIAN LEGAL VOCABULARY",
            "=" * 92,
            f" {'Test Word':<22} | {'Classical (Word)':<18} | {'Simple BPE (Toy)':<22} | {'Complete BPE (Corpus)':<24}",
            "-" * 92,
        ]

        for r in results:
            lines.append(
                f" {r.word:<22} | {r.classical_output:<18} | {r.simple_bpe_output:<22} | {r.complete_bpe_output:<24}"
            )

        lines.extend([
            "-" * 92,
            "",
            " PARADIGMATIC COMPARISON MATRIX:",
            "-" * 92,
            f" {'Dimension':<25} | {'Classical Tokenization':<20} | {'Complete BPE Subword':<35}",
            "-" * 92,
            f" {'Vocabulary Size':<25} | {'Explosive (> 20,000)':<20} | {'Fixed, bounded (~400-1000)':<35}",
            f" {'Out-Of-Vocabulary (OOV)':<25} | {'Fatal (<UNK> error)':<20} | {'Zero OOV (falls back to chars)':<35}",
            f" {'Morphological Awareness':<25} | {'None (monolithic)':<20} | {'High (identifies affixes/roots)':<35}",
            f" {'Sequence Length':<25} | {'1 token per word':<20} | {'1.2 - 2.5 tokens per word':<35}",
            f" {'Downstream Transformer Fit':<25} | {'Poor (sparse embeddings)':<20} | {'Optimal (dense embeddings)':<35}",
            "=" * 92,
        ])

        return "\n".join(lines)

