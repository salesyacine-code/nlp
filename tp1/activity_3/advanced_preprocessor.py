"""
advanced_preprocessor.py
========================
Activity III - Part 1: Advanced Preprocessor for Legal Corpus Construction.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Applies advanced domain-specific legal preprocessing to the French legal corpus:
  1. Handle structured legal references:
     - Loi n° 08-09
     - Décret exécutif n° 21-123 / Décret présidentiel n° ...
     - Article 15 / Article 15 bis / Article 15-1
     (Supports modes: 'bind', 'token', 'standardize', 'preserve')
  2. Normalize numbers:
     (Supports modes: 'preserve', 'normalize', 'token' -> <NUM>)
  3. Normalize dates (dual Hijri/Gregorian, Gregorian, Hijri, numeric):
     (Supports modes: 'preserve', 'normalize', 'token' -> <DATE>)
  4. Remove irrelevant metadata, URLs, generator stamps, and table artifacts.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("activity_3.advanced_preprocessor")


class AdvancedLegalPreprocessor:
    """Domain-specific legal preprocessor with configurable normalization strategies."""

    # Algerian Hijri months written in French
    HIJRI_MONTHS: str = (
        r"(?:moharram|safar|rabie\s+el\s+aouel|rabie\s+ethani|"
        r"djoumada\s+el\s+oula|joumada\s+el\s+oula|joumada\s+ethania|djoumada\s+ethania|"
        r"radjab|cha[aâ]bane|ramadhan|chawwal|dhou\s+el\s+ka[aâ]da|dhou\s+el\s+hidja)"
    )

    # Gregorian months in French
    GREGORIAN_MONTHS: str = (
        r"(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)"
    )

    def __init__(self) -> None:
        """Compile optimized regex patterns for legal references, dates, numbers, and metadata."""
        # 1. Legal References Patterns
        self._re_laws = re.compile(
            r"\b(loi\s+organique|loi)\s+n°?\s*(\d+[-/]\d+)\b",
            re.IGNORECASE | re.UNICODE,
        )
        self._re_decrees = re.compile(
            r"\b(d[ée]cret\s+pr[ée]sidentiel|d[ée]cret\s+ex[ée]cutif|d[ée]cret|ordonnance|"
            r"arr[êe]t[ée](?:\s+interminist[ée]riel|\s+minist[ée]riel)?|d[ée]cision)\s+n°?\s*([\w\d]+(?:[-/][\w\d]+)*)\b",
            re.IGNORECASE | re.UNICODE,
        )
        self._re_articles = re.compile(
            r"\b(article|art\.)\s+(\d+(?:\s*(?:bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies)|-\d+)?)\b",
            re.IGNORECASE | re.UNICODE,
        )

        # 2. Date Patterns
        # Dual Dates: e.g. "25 Joumada Ethania 1445 correspondant au 7 janvier 2024"
        self._re_dual_date = re.compile(
            rf"\b\d{{1,2}}\s+{self.HIJRI_MONTHS}\s+\d{{4}}\s+correspondant\s+au\s+\d{{1,2}}(?:er)?\s+{self.GREGORIAN_MONTHS}\s+\d{{4}}\b",
            re.IGNORECASE | re.UNICODE,
        )
        # Standalone Gregorian Dates: e.g. "20 décembre 2023", "1er mai 2024"
        self._re_gregorian_date = re.compile(
            rf"\b\d{{1,2}}(?:er)?\s+{self.GREGORIAN_MONTHS}\s+\d{{4}}\b",
            re.IGNORECASE | re.UNICODE,
        )
        # Standalone Hijri Dates: e.g. "7 Joumada Ethania 1445"
        self._re_hijri_date = re.compile(
            rf"\b\d{{1,2}}(?:er)?\s+{self.HIJRI_MONTHS}\s+\d{{4}}\b",
            re.IGNORECASE | re.UNICODE,
        )
        # Numeric Dates: e.g. "20/12/2023", "07-01-2024"
        self._re_numeric_date = re.compile(
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            re.UNICODE,
        )

        # 3. Numbers & Currency Patterns
        # Currency: e.g. "14,00 dinars", "1090,00 D.A", "5350,00 da"
        self._re_currency = re.compile(
            r"\b\d+(?:[\s.,]\d+)?\s*(?:dinars?|d\.?a\.?|centimes?)\b",
            re.IGNORECASE | re.UNICODE,
        )
        # Percentages: e.g. "15 %", "2.5%"
        self._re_percentage = re.compile(
            r"\b\d+(?:[\.,]\d+)?\s*%\b",
            re.UNICODE,
        )
        # Ordinal law numbers: e.g. "1°", "2°", "1er", "2ème"
        self._re_ordinals = re.compile(
            r"\b\d+(?:°|er|ère|ème|eme)\b",
            re.IGNORECASE | re.UNICODE,
        )
        # Standard decimal and integer numbers (not already part of words or tokens)
        self._re_generic_numbers = re.compile(
            r"(?<![a-zA-Zà-ÿÀ-Ÿ_<>])\b\d+(?:[\s.,]\d+)*\b(?![a-zA-Zà-ÿÀ-Ÿ_<>])",
            re.UNICODE,
        )

        # 4. Metadata & Boilerplate Removal Patterns
        self._re_urls = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE | re.UNICODE)
        self._re_emails = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", re.IGNORECASE | re.UNICODE)
        self._re_download_stamps = re.compile(
            r"(?i)\b(?:downloaded\s+on|t[ée]l[ée]charg[ée]\s+le|document\s+g[ée]n[ée]r[ée]\s+(?:le|par)|imprim[ée]\s+le)\b.*$",
            re.MULTILINE | re.UNICODE,
        )
        self._re_contact_info = re.compile(
            r"(?i)\b(?:t[ée]l\s*:|fax\s*:|c\.?c\.?p\.?|badr\s*:).*$",
            re.MULTILINE | re.UNICODE,
        )
        self._re_table_leaders = re.compile(r"\.{3,}|_{3,}|-{4,}", re.UNICODE)

    def handle_legal_references(self, text: str, mode: str = "bind") -> str:
        """Process structured legal references according to chosen strategy.

        Args:
            text: Input text string.
            mode: Strategy mode:
              - 'bind': Join citation tokens with underscores (e.g. 'loi_n°_08-09', 'article_15_bis')
              - 'token': Replace citations with typed entity tokens (<LEGAL_REF:LOI>, <LEGAL_REF:DECRET>, <ARTICLE_REF>)
              - 'standardize': Harmonize syntax to canonical 'loi n° XX-YY' and 'article XX'
              - 'preserve': Keep raw text.

        Returns:
            Transformed text with legal references processed.
        """
        if mode == "preserve":
            return text

        if mode == "token":
            # Replace with structured entity tokens
            text = self._re_laws.sub(" <LEGAL_REF:LOI> ", text)
            text = self._re_decrees.sub(" <LEGAL_REF:DECRET> ", text)
            text = self._re_articles.sub(" <ARTICLE_REF> ", text)
            return text

        if mode == "bind":
            # Bind tokens into single atomic units to prevent tokenization splits
            def bind_law(m: re.Match) -> str:
                ref_type = re.sub(r"\s+", "_", m.group(1).lower())
                num = m.group(2).strip()
                return f" {ref_type}_n°_{num} "

            def bind_decree(m: re.Match) -> str:
                ref_type = re.sub(r"\s+", "_", m.group(1).lower())
                num = m.group(2).strip()
                return f" {ref_type}_n°_{num} "

            def bind_article(m: re.Match) -> str:
                art_tag = "article"
                art_num = re.sub(r"\s+", "_", m.group(2).lower().strip())
                return f" {art_tag}_{art_num} "

            text = self._re_laws.sub(bind_law, text)
            text = self._re_decrees.sub(bind_decree, text)
            text = self._re_articles.sub(bind_article, text)
            return text

        if mode == "standardize":
            # Standardize spacing and punctuation
            text = self._re_laws.sub(r"\1 n° \2", text)
            text = self._re_decrees.sub(r"\1 n° \2", text)
            text = self._re_articles.sub(lambda m: f"article {m.group(2)}", text)
            return text

        return text

    def normalize_dates(self, text: str, mode: str = "token") -> str:
        """Process date expressions in the corpus.

        Args:
            text: Input text string.
            mode: Strategy mode:
              - 'token': Replace dates with '<DATE>' special token
              - 'normalize': Harmonize dates into standardized format
              - 'preserve': Keep verbatim dates.

        Returns:
            Transformed text with dates normalized.
        """
        if mode == "preserve":
            return text

        if mode == "token":
            # Note: order matters (dual dates first before standalone dates!)
            text = self._re_dual_date.sub(" <DATE> ", text)
            text = self._re_gregorian_date.sub(" <DATE> ", text)
            text = self._re_hijri_date.sub(" <DATE> ", text)
            text = self._re_numeric_date.sub(" <DATE> ", text)
            return text

        if mode == "normalize":
            # Normalize to standardized representation: [DATE: ...]
            def norm_dual(m: re.Match) -> str:
                clean_str = re.sub(r"\s+", " ", m.group(0).strip())
                return f" [date: {clean_str}] "

            text = self._re_dual_date.sub(norm_dual, text)
            text = self._re_gregorian_date.sub(lambda m: f" [date: {m.group(0).strip()}] ", text)
            text = self._re_hijri_date.sub(lambda m: f" [date_hijri: {m.group(0).strip()}] ", text)
            text = self._re_numeric_date.sub(lambda m: f" [date: {m.group(0).strip()}] ", text)
            return text

        return text

    def normalize_numbers(self, text: str, mode: str = "token") -> str:
        """Process numbers, currencies, and amounts in the corpus.

        Args:
            text: Input text string.
            mode: Strategy mode:
              - 'token': Replace remaining numbers with '<NUM>' special token
              - 'normalize': Clean thousands separators and convert decimals
              - 'preserve': Keep verbatim numbers.

        Returns:
            Transformed text with numbers normalized.
        """
        if mode == "preserve":
            return text

        if mode == "token":
            # Replace currencies, percentages, and remaining digits with <NUM>
            text = self._re_currency.sub(" <NUM> dinars ", text)
            text = self._re_percentage.sub(" <NUM>% ", text)
            text = self._re_ordinals.sub(" <NUM> ", text)
            text = self._re_generic_numbers.sub(" <NUM> ", text)
            return text

        if mode == "normalize":
            # Standardize numeric formats: remove spaces in thousands, replace commas with dots
            def norm_num(m: re.Match) -> str:
                s = m.group(0).replace(" ", "")
                return s.replace(",", ".")

            text = self._re_generic_numbers.sub(norm_num, text)
            return text

        return text

    def remove_metadata(self, text: str) -> str:
        """Strip URLs, emails, download stamps, contact numbers, and table leaders."""
        text = self._re_urls.sub("", text)
        text = self._re_emails.sub("", text)
        text = self._re_download_stamps.sub("", text)
        text = self._re_contact_info.sub("", text)
        text = self._re_table_leaders.sub(" ", text)
        return text

    def process_document(
        self,
        text: str,
        ref_mode: str = "bind",
        date_mode: str = "token",
        num_mode: str = "token",
    ) -> str:
        """Execute complete Advanced Preprocessing pipeline.

        Execution sequence:
          1. Strip metadata, URLs, and table artifacts.
          2. Normalize dates (protects numbers embedded inside dates).
          3. Handle legal references (protects law & article numbers).
          4. Normalize remaining numerical quantities into <NUM>.
          5. Final whitespace cleanup.

        Args:
            text: Document text after Activity II basic preprocessing.
            ref_mode: 'bind', 'token', 'standardize', or 'preserve'.
            date_mode: 'token', 'normalize', or 'preserve'.
            num_mode: 'token', 'normalize', or 'preserve'.

        Returns:
            Final cleaned legal text ready for corpus construction and BPE training.
        """
        # Step 1: Remove metadata and table leaders
        text = self.remove_metadata(text)

        # Step 2: Normalize dates (crucial to run before generic numbers!)
        text = self.normalize_dates(text, mode=date_mode)

        # Step 3: Handle legal references (protects law and article identifiers)
        text = self.handle_legal_references(text, mode=ref_mode)

        # Step 4: Normalize remaining numbers
        text = self.normalize_numbers(text, mode=num_mode)

        # Step 5: Final whitespace tidy
        text = re.sub(r"[ \t]{2,}", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
