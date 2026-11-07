"""
simple_tokenizer.py
===================
Activity V - Part 1: Simple / Classical Word Tokenizer.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Implements standard classical word-level tokenization:
  - Splits text into lexical words using whitespace and punctuation rules.
  - Builds a fixed word vocabulary V.
  - Maps unseen out-of-vocabulary (OOV) words to a special <UNK> token.
  - Demonstrates the fundamental limitations of word-level tokenization.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Set

logger = logging.getLogger("activity_5.simple_tokenizer")


class SimpleWordTokenizer:
    """Classical word-level tokenizer with fixed vocabulary and OOV <UNK> handling."""

    # Regex matching word tokens, hyphenated terms, and special tokens like <NUM>, <DATE>
    WORD_REGEX: re.Pattern = re.compile(
        r"<[^>]+>|[\w\d]+(?:[-_°\'][\w\d]+)*",
        re.UNICODE,
    )

    UNK_TOKEN: str = "<UNK>"
    PAD_TOKEN: str = "<PAD>"

    def __init__(self, lowercase: bool = True) -> None:
        """Initialize tokenizer with casing preference."""
        self.lowercase: bool = lowercase
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.word_frequencies: Dict[str, int] = {}

    def tokenize(self, text: str) -> List[str]:
        """Split text into a sequence of word tokens."""
        if self.lowercase:
            text = text.lower()
        return self.WORD_REGEX.findall(text)

    def fit(self, corpus_text: str, max_vocab_size: Optional[int] = None) -> None:
        """Build fixed vocabulary from training corpus text."""
        tokens = self.tokenize(corpus_text)
        self.word_frequencies.clear()
        for tok in tokens:
            self.word_frequencies[tok] = self.word_frequencies.get(tok, 0) + 1

        # Sort words by frequency descending
        sorted_words = sorted(
            self.word_frequencies.keys(),
            key=lambda w: self.word_frequencies[w],
            reverse=True,
        )

        if max_vocab_size:
            sorted_words = sorted_words[: max_vocab_size - 2]

        self.vocab = {self.PAD_TOKEN: 0, self.UNK_TOKEN: 1}
        for idx, word in enumerate(sorted_words, start=2):
            self.vocab[word] = idx

        self.inverse_vocab = {v: k for k, v in self.vocab.items()}
        logger.info(
            "Simple Word Tokenizer fitted: %d unique vocabulary words registered.",
            len(self.vocab),
        )

    def encode(self, text: str) -> List[int]:
        """Convert text into token IDs, mapping unknown words to <UNK> (ID 1)."""
        tokens = self.tokenize(text)
        unk_id = self.vocab.get(self.UNK_TOKEN, 1)
        return [self.vocab.get(tok, unk_id) for tok in tokens]

    def decode(self, token_ids: List[int]) -> str:
        """Convert list of token IDs back into space-separated words."""
        return " ".join(self.inverse_vocab.get(tid, self.UNK_TOKEN) for tid in token_ids)

    def test_word(self, word: str) -> Dict[str, Any]:
        """Test encoding of a word and report whether it causes an Out-Of-Vocabulary (OOV) failure."""
        normalized = word.lower() if self.lowercase else word
        is_oov = normalized not in self.vocab
        token_id = self.vocab.get(normalized, self.vocab.get(self.UNK_TOKEN, 1))
        return {
            "input_word": word,
            "tokens": [normalized],
            "token_ids": [token_id],
            "is_oov": is_oov,
            "decoded": self.decode([token_id]),
            "limitation_note": (
                "OOV Failure: Word completely replaced by <UNK>, erasing all semantic information."
                if is_oov else
                "In Vocabulary: Word matched as monolithic atomic type."
            ),
        }

