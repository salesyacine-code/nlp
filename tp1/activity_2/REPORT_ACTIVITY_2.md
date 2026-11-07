# Activity II: Basic Preprocessing of the Corpus
**Course:** Natural Language Processing (NLP)  
**Institution:** École Militaire Polytechnique (EMP), Département Informatique  
**Instructor:** Dr. M’hamed MATAOUI  
**Module:** Lab N° 1 — *Legal Document Collection and BPE Tokenization*  

---

## 1. Objectives & Theoretical Justification

In modern NLP pipelines, text extracted from digital PDF documents is fundamentally corrupted by visual formatting artifacts. Before applying tokenization (and particularly subword algorithms like **Byte Pair Encoding (BPE)**), a corpus must undergo systematic basic preprocessing.

The objective of **Activity II** is to eliminate physical layout noise while preserving semantic, lexical, and morphological integrity.

---

## 2. Preprocessing Transformations & Linguistic Rules

### 2.1 Removal of Headers, Footers & Administrative Mastheads
- **Problem:** JORADP gazettes repeat the running header (`JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE...`) and printer imprint (`Imprimerie Officielle - Les Vergers...`) on every page canvas. Additionally, page 1 contains pricing tables and postal checking accounts (CCP/BADR).
- **Impact if uncleaned:** Spurious frequency amplification of administrative vocabulary (`république`, `officiel`, `algérienne`, `dinar`, `abonnement`), which distorts BPE merge candidate rankings.
- **Rule:** Regex filters strip all instances of running headers, synthetic bold titles (`JJOOUURRNNAALL`), publication fee tables, and running printer seals.

### 2.2 Removal of Isolated Page Numbers
- **Problem:** Standalone digits (`6`, `7`, `15`) rendered at the bottom margin of pages.
- **Rule:** Remove lines matching `^\s*(?:page\s+)?\d{1,4}\s*$`. Prevents numerical digits from falsely merging with surrounding words.

### 2.3 The PDF Hyphenation Disambiguation Dilemma
A major contribution of this activity is handling hyphens with linguistic precision, as emphasized in the lab instructions:
> *"Handle PDF Hyphenation (be careful, hyphen does not always indicate a broken word, for instance: ci-dessus, non-respect, sous-jacent)"*

In French typography, a hyphen at the end of a line can represent two mutually exclusive phenomena:
1. **Layout-induced line breaking:** An arbitrary split of a single morphological unit across column boundaries (e.g., `consti-` $\parallel$ `tutionnel` $\to$ `constitutionnel`, `admi-` $\parallel$ `nistratif` $\to$ `administratif`).
2. **Intrinsic lexical hyphenation:** A genuine French compound word, numerical expression, or affixed term that **requires** a hyphen (e.g., `sous-programmes`, `non-respect`, `ci-dessus`, `quarante-quatre`, `procès-verbal`, `garde-côtes`).

#### Algorithmic Disambiguation Strategy
Our preprocessor evaluates candidates matching `\b([a-zA-Zà-ÿÀ-Ÿ]{2,})[-—]\s*\n\s*([a-zA-Zà-ÿÀ-Ÿ]{2,})\b` against four linguistic rules:
- **Rule 1 (Compound Prefixes):** If prefix $\in \{\text{sous}, \text{non}, \text{ci}, \text{ayants}, \text{procès}, \text{garde}, \text{auto}, \text{pré}, \text{post}, \text{médico}, \text{socio}, \text{gastro}, \dots\}$, preserve hyphen (`w1-w2`).
- **Rule 2 (French Numerals):** If either word is a French number ($\{\text{dix}, \text{vingt}, \text{quarante}, \dots\}$), preserve hyphen (`quarante-quatre`).
- **Rule 3 (Deictics & Pronouns):** If either word $\in \{\text{celui}, \text{ceux}, \text{ci}, \text{là}, \text{même}\}$, preserve hyphen (`celui-ci`).
- **Rule 4 (Compound Proper Nouns):** Capitalized pairs (e.g., `Boumediène-Fret`) retain hyphen.
- **Fallback (Word Recombination):** Otherwise, merge into a unified lexical unit without a hyphen (`w1 + w2`).

### 2.4 Apostrophe & Quotation Mark Standardization
- Typographical variants (`’`, `‘`, `\``, `´`) are mapped to ASCII `'` (`\x27`).
- Extraneous spacing around apostrophes (e.g., `l ' article`, `d ' un`, `qu ' il`) is contracted into standard French elision (`l'article`, `d'un`, `qu'il`).
- Guillemets (`«`, `»`) and curly quotes (`“`, `”`) are converted to standard ASCII double quotes (`"`).

### 2.5 Line Break Normalization (Paragraph Continuity)
- Standard 2-column PDF extraction creates hard line breaks every 30 to 50 characters.
- Sentences broken mid-clause are concatenated with a single whitespace into continuous grammatical sentences.
- True structural legal breaks are strictly protected: articles (`Article 1er`, `Art. 2.`), enacting clauses (`Décrète :`, `Décide :`, `Vu `), and itemized lists (`- `, `• `, `1° `).

### 2.6 Case Normalization
- Converts all text to lowercase while maintaining full Unicode compliance for accented French characters (`É` $\to$ `é`, `È` $\to$ `è`, `À` $\to$ `à`, `Ç` $\to$ `ç`, `Ê` $\to$ `ê`).

---

## 3. Visual Inspection Evidence (Before vs. After)

The following empirical samples are extracted directly from the corpus during automated inspection:

| Transformation Category | [BEFORE] Raw Extracted Sample | [AFTER] Cleaned Sample | Algorithmic Justification |
|---|---|---|---|
| **1. Header & Footer Removal** | `JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE N° 01 25 Joumada Ethania 1445 7 janvier 20242` | *[COMPLETELY STRIPPED]* | Eliminates 2,962 redundant administrative mastheads across the corpus. |
| **2. Page Number Removal** | `\n 6 \n` (isolated line) | *[COMPLETELY STRIPPED]* | Removes 11,430 isolated digits from interfering with word embeddings. |
| **3. Hyphenation (Compound)** | `sous- \n programmes` | `sous-programmes` | Recognized prefix `sous-`; hyphen preserved to maintain compound lexical meaning. |
| **3. Hyphenation (Broken Word)** | `vice- \n recteurs` | `vicerecteurs` | Arbitrary layout line break; recombined into unified morpheme sequence. |
| **4. Apostrophe Normalization** | `autorisations d’engagement` | `autorisations d'engagement` | Curly Unicode apostrophe `’` replaced by ASCII `'`. |
| **5. Quotation Normalization** | `ainsi rédigé : « Art. 23. — Les crédits... »` | `ainsi rédigé : "Art. 23. — Les crédits..."` | French guillemets `« »` normalized to standard `"`. |
| **6. Line Break Normalization** | `relative à la conformité de la loi \n organique modifiant et complétant \n la loi organique...` | `relative à la conformité de la loi organique modifiant et complétant la loi organique...` | PDF column line breaks merged into a fluent, continuous grammatical sentence. |
| **7. Case Normalization** | `DÉCISION N° 05/D.C.C/CCC/23` | `décision n° 05/d.c.c/ccc/23` | Unicode uppercase accented characters converted cleanly to lowercase (`é`). |

---

## 4. Quantitative Corpus Reduction Metrics

Batch execution across all **50 legal gazette documents** yielded the following measurements:

```text
==================================================================================
           ACTIVITY II: EMPIRICAL BATCH PREPROCESSING RESULTS
==================================================================================
 Total Documents Processed : 50
 Total Raw Characters      : 5,324,347
 Total Cleaned Characters  : 4,744,725
 Net Noise Removed         : 579,622 characters (-10.89%)
 Total Raw Lines           : 192,205
 Total Consolidated Lines  : 62,997
 Structural Line Reduction : -129,208 lines (-67.22%)
==================================================================================
```

### Analysis of Reduction
- **$-10.89\%$ Character Reduction:** Corresponds strictly to eliminated noise: recurring masthead headers, footers, duplicate synthetic titles (`JJOOUURRNNAALL`), isolated pagination digits, and excessive whitespace padding.
- **$-67.22\%$ Line Count Consolidation:** Reflects the successful merging of fragmented 2-column visual lines into proper, continuous legal sentences and articles, establishing an ideal foundation for subword vocabulary learning.

---

## 5. Artifacts and Directory Layout
- **Preprocessor:** [`tp1/activity_2/preprocessor.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/preprocessor.py)
- **Batch Cleaner:** [`tp1/activity_2/cleaner.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/cleaner.py)
- **Visual Inspector:** [`tp1/activity_2/inspector.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/inspector.py)
- **Entrypoint:** [`tp1/activity_2/main.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/main.py) (`activityTwo()`)
- **Cleaned Corpus:** `tp1/activity_2/cleaned_texts/` (50 preprocessed `.txt` files)
- **Reports:** [`tp1/activity_2/reports/preprocessing_inspection_report.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/reports/preprocessing_inspection_report.txt) and [`cleaning_summary.json`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_2/reports/cleaning_summary.json).

