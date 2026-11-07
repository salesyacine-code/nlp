"""
preprocessor.py
===============
Activity II - Part 1: Corpus Preprocessor for French Legal Texts.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Applies basic preprocessing to extracted JORADP legal gazettes:
  1. Remove page delimiters (--- PAGE_BREAK: X ---).
  2. Remove repetitive running headers and footers (masthead, gazette stamps).
  3. Remove isolated pagination numbers.
  4. Handle PDF hyphenation with French compound word disambiguation.
  5. Normalize apostrophes and eliminate artificial spacing.
  6. Normalize quotation marks (guillemets, curly quotes to standard \").
  7. Normalize broken line breaks into fluent paragraphs.
  8. Normalize non-breaking and consecutive spaces.
  9. Normalize character case (with Unicode French accent preservation).
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger("activity_2.preprocessor")


class CorpusPreprocessor:
    """Production-grade preprocessor for Algerian legal French texts extracted from PDF."""

    # Whitelist of standard French compound prefixes, stems, and particles that
    # legitimately require a hyphen (e.g., sous-programme, non-respect, ci-dessus).
    COMPOUND_PREFIXES: Set[str] = {
        "sous", "non", "ci", "ayants", "procès", "garde", "auto", "pré", "post",
        "médico", "socio", "gastro", "électro", "extra", "infra", "ultra", "vis",
        "porte", "arrière", "avant", "court", "long", "haut", "bas", "mi", "quasi",
        "semi", "tout", "tous", "grand", "petit", "chef", "contre", "entre",
        "multi", "inter", "intra", "co", "sur", "sans", "plus", "moins", "béni",
        "nouveau", "nouvelle", "saint", "sainte"
    }

    # French cardinal numbers used in hyphenated compounds (e.g., quarante-quatre, soixante-dix).
    FRENCH_NUMBERS: Set[str] = {
        "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
        "onze", "douze", "treize", "quatorze", "quinze", "seize", "vingt", "trente",
        "quarante", "cinquante", "soixante", "cent", "mille"
    }

    # Deictics and emphatic pronouns connected via hyphen (e.g., celui-ci, eux-mêmes).
    DEICTICS: Set[str] = {
        "celui", "celle", "ceux", "celles", "eux", "lui", "elle", "moi", "toi",
        "nous", "vous", "ci", "là", "même", "mêmes"
    }

    def __init__(self, lowercase_by_default: bool = True) -> None:
        """Initialize compiled regular expressions for the cleaning pipeline."""
        self.lowercase_by_default: bool = lowercase_by_default

        # 1. Page delimiter markers from Activity I
        self._re_page_markers = re.compile(r"--- PAGE_BREAK:\s*\d+\s*---\n?", re.UNICODE)

        # 2. Running headers:
        # e.g., 'JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE N° 01 25 Joumada Ethania 1445 7 janvier 20246'
        self._re_running_headers = re.compile(
            r"(?m)^.*JOURNAL\s+OFFICIEL\s+DE\s+LA\s+R[ÉE]PUBLIQUE\s+ALG[ÉE]RIENNE.*$\n?",
            re.IGNORECASE | re.UNICODE,
        )

        # Synthetic bold drop-shadow headers: 'JJOOUURRNNAALL  OOFFFFIICCIIEELL'
        self._re_synthetic_bold = re.compile(
            r"(?m)^.*(?:JJOOUURRNNAALL\s+OOFFFFIICCIIEELL|DDEE\s+LLAA\s+RREEPPUUBBLLIIQQUUEE).*$\n?",
            re.IGNORECASE | re.UNICODE,
        )

        # Masthead administrative boilerplate (pricing, address, CCP, BADR)
        self._re_masthead_blocks = re.compile(
            r"(?is)Edition\s+originale,\s+le\s+num[ée]ro\s*:.*?ABONNEMENT\s+ANNUEL.*?(?=\n\n|\Z)",
            re.UNICODE,
        )
        self._re_admin_contacts = re.compile(
            r"(?m)^(?:DIRECTION\s+ET\s+REDACTION|SECRETARIAT\s+GENERAL\s+DU\s+GOUVERNEMENT|"
            r"WWW\.JORADP\.DZ|IMPRIMERIE\s+OFFICIELLE|ALGER-GARE|"
            r"T[ée]l\s*:|Fax\s*:|C\.C\.P\.|BADR\s*:).*$\n?",
            re.IGNORECASE | re.UNICODE,
        )

        # Footers: Imprimerie Officielle imprint at the bottom of pages
        self._re_running_footers = re.compile(
            r"(?m)^.*(?:Imprimerie\s+Officielle\s*-\s*Les\s+Vergers|Imprimerie\s+Officielle\s*-\s*Les\s+Fusill[ée]s|"
            r"SECRETARIAT\s+GENERAL\s+DU\s+GOUVERNEMENT).*$\n?",
            re.IGNORECASE | re.UNICODE,
        )

        # 3. Isolated pagination numbers
        self._re_isolated_pagination = re.compile(
            r"(?m)^\s*(?:page\s+)?\d{1,4}\s*$\n?",
            re.IGNORECASE | re.UNICODE,
        )

        # 4. End-of-line hyphenation splits
        self._re_hyphen_split = re.compile(
            r"\b([a-zA-Zà-ÿÀ-Ÿ]{2,})[-—]\s*\n\s*([a-zA-Zà-ÿÀ-Ÿ]{2,})\b",
            re.UNICODE,
        )

        # 5. Apostrophe variants
        self._re_apostrophe_chars = re.compile(r"[’‘`´′]", re.UNICODE)
        # Spaces around apostrophes (e.g. "l ' article" -> "l'article")
        self._re_apostrophe_spacing = re.compile(
            r"\b([a-zA-Zà-ÿÀ-Ÿ]{1,8})\s*'\s*([a-zA-Zà-ÿÀ-Ÿ])",
            re.UNICODE,
        )

        # 6. Quotation marks: French guillemets and curly quotes
        self._re_quotes = re.compile(r"[«»“”„‟]", re.UNICODE)
        self._re_quote_spacing_open = re.compile(r'"\s+', re.UNICODE)
        self._re_quote_spacing_close = re.compile(r'\s+"', re.UNICODE)

        # 7. Non-breaking and typographic spaces
        self._re_nbsp = re.compile(r"[\xa0\u202f\u2009\u200a\u3000]", re.UNICODE)

        # 8. Multiple consecutive horizontal spaces
        self._re_multi_spaces = re.compile(r"[ \t]{2,}", re.UNICODE)

        # 9. Structural legal markers starting an independent sentence/clause
        self._re_structural_start = re.compile(
            r"^(?:article\s+\d+|art\.\s*\d+|vu\s+|consid[ée]rant|d[ée]cr[èe]te\s*:|d[ée]cide\s*:|"
            r"arr[êe]te\s*:|titre\s+[ivxlcdm\d]+|chapitre\s+[ivxlcdm\d]+|section\s+[ivxlcdm\d]+|"
            r"sous-section\s+[ivxlcdm\d]+|[•\-—]\s+|\d+[\)°]\s+|[a-z]\)\s+)",
            re.IGNORECASE | re.UNICODE,
        )

    def remove_page_markers(self, text: str) -> str:
        """Strip custom physical page delimiters inserted during text extraction."""
        return self._re_page_markers.sub("", text)

    def remove_headers_footers(self, text: str) -> str:
        """Strip running headers, synthetic bold titles, administrative pricing blocks, and footers."""
        text = self._re_running_headers.sub("", text)
        text = self._re_synthetic_bold.sub("", text)
        text = self._re_masthead_blocks.sub("", text)
        text = self._re_admin_contacts.sub("", text)
        text = self._re_running_footers.sub("", text)
        return text

    def remove_page_numbers(self, text: str) -> str:
        """Remove isolated lines containing only page numbers."""
        return self._re_isolated_pagination.sub("", text)

    def _resolve_hyphen_match(self, match: re.Match) -> str:
        """Intelligently disambiguate between true French compound words and broken layout words."""
        w1: str = match.group(1)
        w2: str = match.group(2)
        w1_lower = w1.lower()
        w2_lower = w2.lower()

        # Rule 1: Prefixes that genuinely require a hyphen (e.g. sous-programmes, non-respect)
        if w1_lower in self.COMPOUND_PREFIXES:
            return f"{w1}-{w2}"

        # Rule 2: French compound numbers (e.g. quarante-quatre, soixante-dix)
        if w1_lower in self.FRENCH_NUMBERS or w2_lower in self.FRENCH_NUMBERS:
            return f"{w1}-{w2}"

        # Rule 3: Pronouns and deictics (e.g. celui-ci, eux-mêmes)
        if w1_lower in self.DEICTICS or w2_lower in self.DEICTICS:
            return f"{w1}-{w2}"

        # Rule 4: Capitalized compound proper names or acronyms (e.g. Boumediène-Fret)
        if (w1[0].isupper() and w2[0].isupper()) or (w1.isupper() and w2.isupper()):
            return f"{w1}-{w2}"

        # Rule 5: Arbitrary layout line-break word splits (e.g. consti- \n tutionnel -> constitutionnel)
        return f"{w1}{w2}"

    def handle_hyphenation(self, text: str) -> str:
        """Recombine line-wrapped words while preserving genuine French compound words."""
        return self._re_hyphen_split.sub(self._resolve_hyphen_match, text)

    def normalize_apostrophes(self, text: str) -> str:
        """Replace typographic/curly apostrophes with standard ASCII ' and remove artificial whitespace."""
        text = self._re_apostrophe_chars.sub("'", text)
        text = self._re_apostrophe_spacing.sub(r"\1'\2", text)
        return text

    def normalize_quotation_marks(self, text: str) -> str:
        """Standardize French guillemets and curly quotes to ASCII double quotes and clean spaces."""
        text = self._re_quotes.sub('"', text)
        text = self._re_quote_spacing_open.sub('"', text)
        text = self._re_quote_spacing_close.sub('"', text)
        return text

    def normalize_whitespace(self, text: str) -> str:
        """Normalize non-breaking spaces, collapse redundant spaces, and trim line boundaries."""
        text = self._re_nbsp.sub(" ", text)
        text = self._re_multi_spaces.sub(" ", text)

        # Normalize trailing spaces on lines
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(lines)

        # Collapse 3 or more consecutive empty lines into standard paragraph break (\n\n)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def normalize_line_breaks(self, text: str) -> str:
        """Join lines broken mid-sentence by 2-column PDF layout while keeping legal structure."""
        paragraphs = re.split(r"\n\s*\n", text)
        cleaned_paragraphs: List[str] = []

        for para in paragraphs:
            lines = [line.strip() for line in para.split("\n") if line.strip()]
            if not lines:
                continue

            merged_lines: List[str] = []
            current_line = lines[0]

            for next_line in lines[1:]:
                # If next_line explicitly starts a distinct legal article, clause, or bullet
                if self._re_structural_start.match(next_line):
                    merged_lines.append(current_line)
                    current_line = next_line
                # If current_line ends with a colon (e.g., "Décrète :")
                elif current_line.endswith(":"):
                    merged_lines.append(current_line)
                    current_line = next_line
                # If current_line ends with sentence terminator and next_line starts with uppercase
                elif current_line[-1] in ".!?" and (next_line[0].isupper() or next_line[0] in '"«'):
                    merged_lines.append(current_line)
                    current_line = next_line
                else:
                    # Merge lines within the same sentence
                    current_line = f"{current_line} {next_line}"

            merged_lines.append(current_line)
            cleaned_paragraphs.append("\n".join(merged_lines))

        return "\n\n".join(cleaned_paragraphs)

    def normalize_case(self, text: str) -> str:
        """Uniformly lowercase text while ensuring full Unicode preservation of French accents."""
        return text.lower()

    def preprocess_text(self, text: str, lowercase: Optional[bool] = None) -> str:
        """Execute the full Activity II preprocessing pipeline in optimal sequence.

        Args:
            text: Raw extracted document text.
            lowercase: Whether to apply case normalization (defaults to instance setting).

        Returns:
            Preprocessed clean text ready for corpus construction and tokenization.
        """
        do_lower = self.lowercase_by_default if lowercase is None else lowercase

        # Step 1: Strip page boundary markers
        text = self.remove_page_markers(text)

        # Step 2: Remove repetitive running headers, masthead blocks, and footers
        text = self.remove_headers_footers(text)

        # Step 3: Remove standalone page number lines
        text = self.remove_page_numbers(text)

        # Step 4: Disambiguate hyphenation (before line-break merging!)
        text = self.handle_hyphenation(text)

        # Step 5: Normalize apostrophes and spaces around them
        text = self.normalize_apostrophes(text)

        # Step 6: Normalize quotation marks
        text = self.normalize_quotation_marks(text)

        # Step 7: Normalize line breaks into cohesive paragraphs
        text = self.normalize_line_breaks(text)

        # Step 8: Normalize non-breaking and consecutive spaces
        text = self.normalize_whitespace(text)

        # Step 9: Normalize case
        if do_lower:
            text = self.normalize_case(text)

        return text

