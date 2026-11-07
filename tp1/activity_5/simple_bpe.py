"""
simple_bpe.py
=============
Activity V - Part 2: Simplified / Demonstrative Byte Pair Encoding (BPE).
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Demonstrates the core mechanics of Byte Pair Encoding (BPE):
  1. Represents words as whitespace-separated character sequences with '</w>' end marker.
  2. Iteratively computes frequencies of all adjacent symbol pairs across vocabulary.
  3. Greedily merges the most frequent adjacent symbol pair in-place.
  4. Traces and displays the step-by-step subword merge evolution.
"""

from __future__ import annotations

import collections
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("activity_5.simple_bpe")


class SimpleBPE:
    """Compact pedagogical implementation of Byte Pair Encoding."""

    END_OF_WORD: str = "</w>"

    def __init__(self, num_merges: int = 15) -> None:
        """Initialize with target number of merge iterations."""
        self.num_merges: int = num_merges
        self.learned_merges: List[Tuple[Tuple[str, str], int]] = []
        self.merge_history: List[Dict[str, Any]] = []

    def build_initial_vocab(self, corpus_words: List[str]) -> Dict[str, int]:
        """Convert a list of raw words into character-separated dictionary with '</w>'."""
        word_counts = collections.Counter(corpus_words)
        vocab: Dict[str, int] = {}
        for word, count in word_counts.items():
            if not word:
                continue
            # Format word: 'c o n s t i t u t i o n </w>'
            spaced = " ".join(list(word)) + f" {self.END_OF_WORD}"
            vocab[spaced] = count
        return vocab

    @staticmethod
    def get_stats(vocab: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        """Count co-occurrence frequencies of all adjacent symbol pairs across vocabulary."""
        pairs: Dict[Tuple[str, str], int] = collections.defaultdict(int)
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pair = (symbols[i], symbols[i + 1])
                pairs[pair] += freq
        return pairs

    @staticmethod
    def merge_vocab(pair: Tuple[str, str], vocab: Dict[str, int]) -> Dict[str, int]:
        """Replace all occurrences of pair in vocabulary with merged symbol."""
        v_out: Dict[str, int] = {}
        bigram = re.escape(" ".join(pair))
        replacement = "".join(pair)
        # Use negative lookbehind and lookahead to avoid partial substring matching
        pattern = re.compile(r"(?<!\S)" + bigram + r"(?!\S)")

        for word, freq in vocab.items():
            w_out = pattern.sub(replacement, word)
            v_out[w_out] = freq
        return v_out

    def train_simple(
        self, corpus_text: str, max_words: Optional[int] = 5000
    ) -> List[Tuple[Tuple[str, str], int]]:
        """Train simple BPE merges on sample text and log the merge progression."""
        # Simple extraction of legal words
        words = re.findall(r"\b[a-zA-Zà-ÿÀ-Ÿ_°]+(?:-[a-zA-Zà-ÿÀ-Ÿ]+)*\b", corpus_text.lower())
        if max_words:
            words = words[:max_words]

        vocab = self.build_initial_vocab(words)
        logger.info("Initial Simple BPE vocabulary built with %d distinct words.", len(vocab))

        self.learned_merges.clear()
        self.merge_history.clear()

        for iteration in range(1, self.num_merges + 1):
            pairs = self.get_stats(vocab)
            if not pairs:
                logger.info("No further symbol pairs to merge. Stopping early at iteration %d.", iteration)
                break

            # Find the most frequent adjacent pair: argmax freq(p1, p2)
            best_pair = max(pairs, key=pairs.get)
            best_freq = pairs[best_pair]

            if best_freq < 2:
                logger.info("Best pair frequency < 2. Stopping at iteration %d.", iteration)
                break

            vocab = self.merge_vocab(best_pair, vocab)
            self.learned_merges.append((best_pair, best_freq))

            merged_symbol = "".join(best_pair)
            self.merge_history.append({
                "iteration": iteration,
                "pair": best_pair,
                "frequency": best_freq,
                "resulting_symbol": merged_symbol,
            })

            logger.debug(
                "Iteration %02d: Merged %s -> '%s' (frequency: %d)",
                iteration, best_pair, merged_symbol, best_freq
            )

        return self.learned_merges

    def format_merge_trace(self) -> str:
        """Render a clean text table tracing the pedagogical merge progression."""
        lines: List[str] = [
            "-" * 68,
            f" {'Iter':<5} | {'Pair (c1, c2)':<24} | {'Frequency':<11} | {'Merged Subword':<16}",
            "-" * 68,
        ]
        for m in self.merge_history:
            pair_str = f"('{m['pair'][0]}', '{m['pair'][1]}')"
            lines.append(
                f" {m['iteration']:<5} | {pair_str:<24} | {m['frequency']:<11,} | {m['resulting_symbol']:<16}"
            )
        lines.append("-" * 68)
        return "\n".join(lines)

