"""
complete_bpe.py
===============
Activity V - Part 3: Complete Byte Pair Encoding (BPE) Tokenizer.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Production-grade Byte Pair Encoding (BPE) subword tokenizer:
  1. Trains BPE merges from a full legal text corpus.
  2. Stores/serializes the learned merges and subword vocabulary to disk.
  3. Encodes unseen words into subwords using ranked merge priority rules.
  4. Tests encoding on target legal test words (e.g., 'constitutionnalité').
  5. Decodes subwords back into reconstructed surface text.
"""

from __future__ import annotations

import collections
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("activity_5.complete_bpe")


class CompleteBPETokenizer:
    """Full Byte Pair Encoding tokenizer with training, persistence, and inference."""

    END_OF_WORD: str = "</w>"
    UNK_TOKEN: str = "<UNK>"
    PAD_TOKEN: str = "<PAD>"

    def __init__(self, num_merges: int = 300) -> None:
        """Initialize tokenizer with target number of merges."""
        self.num_merges: int = num_merges
        # Maps (p1, p2) -> rank index (lower rank = learned earlier, higher priority)
        self.merges: Dict[Tuple[str, str], int] = {}
        # Complete subword vocabulary {subword: token_id}
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.special_tokens: List[str] = [
            self.PAD_TOKEN, self.UNK_TOKEN, "<NUM>", "<DATE>",
            "<LEGAL_REF:LOI>", "<LEGAL_REF:DECRET>", "<ARTICLE_REF>"
        ]

    # -------------------------------------------------------------------------
    # 1. Training Phase
    # -------------------------------------------------------------------------
    def train(
        self,
        corpus_text: str,
        num_merges: Optional[int] = None,
        min_frequency: int = 2,
        log_interval: int = 50,
    ) -> Dict[str, Any]:
        """Learn ranked BPE merges from corpus text."""
        target_merges = num_merges if num_merges is not None else self.num_merges

        # Extract words (keeping special tokens and bound legal entities)
        word_tokens = re.findall(
            r"<[^>]+>|[\w\d]+(?:[-_°\'][\w\d]+)*",
            corpus_text.lower(),
            re.UNICODE,
        )

        word_counts = collections.Counter(word_tokens)
        logger.info("Building initial BPE character vocabulary from %d unique words...", len(word_counts))

        # Initial vocabulary: space-separated characters + '</w>'
        vocab: Dict[str, int] = {}
        initial_chars: Set[str] = set()

        for word, count in word_counts.items():
            if not word:
                continue
            # Treat special tokens as atomic single symbols
            if word.startswith("<") and word.endswith(">"):
                vocab[f"{word} {self.END_OF_WORD}"] = count
                initial_chars.add(word)
            else:
                chars = list(word)
                initial_chars.update(chars)
                spaced = " ".join(chars) + f" {self.END_OF_WORD}"
                vocab[spaced] = count

        self.merges.clear()
        merge_records: List[Dict[str, Any]] = []

        logger.info("Commencing BPE merge training for %d iterations...", target_merges)

        for step in range(target_merges):
            # Compute pair frequencies
            pairs: Dict[Tuple[str, str], int] = collections.defaultdict(int)
            for word, freq in vocab.items():
                symbols = word.split()
                for i in range(len(symbols) - 1):
                    pairs[(symbols[i], symbols[i + 1])] += freq

            if not pairs:
                logger.info("No further symbol pairs available. Terminating at step %d.", step)
                break

            best_pair = max(pairs, key=pairs.get)
            best_freq = pairs[best_pair]

            if best_freq < min_frequency:
                logger.info("Best pair frequency (%d) below threshold (%d). Terminating at step %d.", best_freq, min_frequency, step)
                break

            # Assign rank to this merge
            self.merges[best_pair] = step
            merged_symbol = "".join(best_pair)

            merge_records.append({
                "rank": step,
                "pair": best_pair,
                "frequency": best_freq,
                "merged": merged_symbol,
            })

            # Fast regex in-place replacement across vocabulary
            bigram = re.escape(" ".join(best_pair))
            pattern = re.compile(r"(?<!\S)" + bigram + r"(?!\S)")
            vocab = {pattern.sub(merged_symbol, w): c for w, c in vocab.items()}

            if (step + 1) % log_interval == 0 or (step + 1) == target_merges:
                logger.info("BPE Training Step %03d/%d: Merged %s -> '%s' (freq: %d)", step + 1, target_merges, best_pair, merged_symbol, best_freq)

        # Build final subword vocabulary
        final_subwords: Set[str] = set(self.special_tokens)
        final_subwords.update(initial_chars)
        final_subwords.add(self.END_OF_WORD)

        for best_pair in self.merges:
            final_subwords.add("".join(best_pair))

        self.vocab = {tok: idx for idx, tok in enumerate(sorted(final_subwords))}
        self.inverse_vocab = {idx: tok for tok, idx in self.vocab.items()}

        logger.info(
            "BPE Training complete: %d merges learned. Subword vocabulary size: %d.",
            len(self.merges),
            len(self.vocab),
        )

        return {
            "num_merges_learned": len(self.merges),
            "vocab_size": len(self.vocab),
            "top_10_merges": merge_records[:10],
            "last_5_merges": merge_records[-5:] if len(merge_records) >= 5 else merge_records,
        }

    # -------------------------------------------------------------------------
    # 2. Persistence Phase (Save / Load)
    # -------------------------------------------------------------------------
    def save_model(self, file_path: Path | str) -> None:
        """Serialize learned merges and vocabulary to JSON on disk."""
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        serializable_merges = [
            {"pair": list(pair), "rank": rank}
            for pair, rank in sorted(self.merges.items(), key=lambda x: x[1])
        ]

        model_payload = {
            "num_merges": len(self.merges),
            "vocab_size": len(self.vocab),
            "special_tokens": self.special_tokens,
            "merges": serializable_merges,
            "vocab": self.vocab,
        }

        target.write_text(json.dumps(model_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("BPE Model successfully saved to: %s", target.resolve())

    def load_model(self, file_path: Path | str) -> None:
        """Load trained BPE model from JSON file."""
        target = Path(file_path)
        data = json.loads(target.read_text(encoding="utf-8"))

        self.special_tokens = data.get("special_tokens", self.special_tokens)
        self.vocab = data["vocab"]
        self.inverse_vocab = {int(idx): tok for tok, idx in self.vocab.items()}

        self.merges = {
            tuple(item["pair"]): item["rank"]
            for item in data["merges"]
        }
        self.num_merges = len(self.merges)
        logger.info("BPE Model loaded from %s: %d merges, %d vocab.", target, len(self.merges), len(self.vocab))

    # -------------------------------------------------------------------------
    # 3. Inference / Encoding Phase
    # -------------------------------------------------------------------------
    def encode_word(self, word: str) -> List[str]:
        """Segment an individual word into learned subword units.

        Applies learned merges in strict order of training rank (earliest first).
        """
        clean_word = word.lower().strip()
        if not clean_word:
            return []

        # If special token, return as atomic unit
        if clean_word.startswith("<") and clean_word.endswith(">"):
            return [clean_word]

        # Initial segmentation into characters with </w> attached to final character
        word_pieces = list(clean_word[:-1]) + [clean_word[-1] + self.END_OF_WORD]

        while len(word_pieces) > 1:
            # Find all adjacent pairs in current word segmentation
            pairs = [
                (word_pieces[i], word_pieces[i + 1])
                for i in range(len(word_pieces) - 1)
            ]

            # Find pairs that exist in our learned merge rules
            valid_candidates = [p for p in pairs if p in self.merges]
            if not valid_candidates:
                break

            # Pick candidate with the lowest rank (learned earliest)
            best_pair = min(valid_candidates, key=lambda p: self.merges[p])

            # Apply merge across word_pieces
            new_pieces: List[str] = []
            i = 0
            while i < len(word_pieces):
                if i < len(word_pieces) - 1 and (word_pieces[i], word_pieces[i + 1]) == best_pair:
                    new_pieces.append(best_pair[0] + best_pair[1])
                    i += 2
                else:
                    new_pieces.append(word_pieces[i])
                    i += 1

            word_pieces = new_pieces

        return word_pieces

    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize arbitrary running text into subwords."""
        words = re.findall(r"<[^>]+>|[\w\d]+(?:[-_°\'][\w\d]+)*", text, re.UNICODE)
        subwords: List[str] = []
        for w in words:
            subwords.extend(self.encode_word(w))
        return subwords

    def decode(self, subwords: List[str]) -> str:
        """Reconstruct original text from a sequence of subwords."""
        joined = "".join(subwords)
        reconstructed = joined.replace(self.END_OF_WORD, " ").strip()
        return reconstructed

    # -------------------------------------------------------------------------
    # 4. Mandatory Lab Test Case
    # -------------------------------------------------------------------------
    def test_legal_word(self, test_word: str = "constitutionnalité") -> Dict[str, Any]:
        """Execute the required lab test on a target legal word.

        Demonstrates how BPE breaks down complex unseen legal terms into learned morphemes.
        """
        subwords = self.encode_word(test_word)
        token_ids = [self.vocab.get(sw, self.vocab.get(self.UNK_TOKEN, 1)) for sw in subwords]
        reconstructed = self.decode(subwords)

        return {
            "input_word": test_word,
            "subwords": subwords,
            "subword_count": len(subwords),
            "token_ids": token_ids,
            "reconstructed": reconstructed,
            "is_perfect_reconstruction": reconstructed == test_word.lower(),
        }

