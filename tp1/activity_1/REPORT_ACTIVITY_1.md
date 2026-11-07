# Activity I: Legal Texts Extraction from JORADP & Diagnostic Audit
**Course:** Natural Language Processing (NLP)  

**Instructor:** Dr. M’hamed MATAOUI  
**Module:** Lab N° 1 — *Legal Document Collection and BPE Tokenization*  

---

## 1. JORADP Data Source & Structural Architecture Analysis

### 1.1 Source Repository & Governance
The primary authoritative legal repository of the People's Democratic Republic of Algeria is the **Secrétariat Général du Gouvernement (SGG)**, hosted at the official portal [www.joradp.dz](https://www.joradp.dz). The portal archives all official legal gazettes (*Journal Officiel de la République Algérienne Démocratique et Populaire* — JORADP) published since independence (1962).

### 1.2 Web Repository Topology & Directory Schema
The JORADP backend exposes a predictable static hierarchical file repository via HTTP/FTP:
```text
https://www.joradp.dz/FTP/
│
├── jo-francais/                 <-- French-translated legal gazettes
│   ├── {YEAR}/                  <-- Four-digit publication year (e.g., 2024, 2023, ...)
│   │   ├── F{YEAR}001.pdf       <-- Gazette issue N° 01 (e.g., F2024001.pdf)
│   │   ├── F{YEAR}002.pdf       <-- Gazette issue N° 02
│   │   └── ...
│   └── ...
│
└── jo-arabe/                    <-- Original Arabic-language legal gazettes
    ├── {YEAR}/
    │   ├── A{YEAR}001.pdf       <-- Gazette issue N° 01 (e.g., A2024001.pdf)
    │   └── ...
```

- **Prefix Conventions:** `F` denotes the French edition (*Traduction française*), while `A` designates the authentic Arabic edition.
- **Naming Pattern:** `F{YEAR}{ISSUE:03d}.pdf` (3-digit zero-padded sequence).
- **Temporal Cadence:** Gazettes are published weekly or bi-weekly, yielding between 60 to 90 issues per calendar year.

### 1.3 Physical and Typographical Gazette Layout
An official Algerian legal gazette exhibits a rigorous physical composition:
1. **Front Masthead (Page 1):**
   - Official national motto, Hijri calendar date, Gregorian publication date, and sequential issue number.
   - Dual-printed synthetic bold title: `JJOOUURRNNAALL OOFFFFIICCIIEELL` (caused by double-strike PDF rendering for visual bolding).
   - Legal text typology index (*Sommaire*): International Conventions, Laws (*Lois*), Presidential Decrees (*Décrets présidentiels*), Executive Decrees (*Décrets exécutifs*), Ministerial Orders (*Arrêtés*), Decisions, and Notices.
2. **Dual-Column Body Typography:**
   - Body pages feature a strict **two-column layout** divided by a thin vertical line separator.
   - Legal articles (`Article 1er`, `Art. 2.`, `Art. 15 bis`) are structured hierarchically under preamble citations (*"Vu la Constitution...", "Vu le décret..."*).
3. **Running Banners & Margins:**
   - **Running Header:** Issue number and date repeated at the top of every subsequent page.
   - **Running Footer:** Page number and official printer seal (*Imprimerie Officielle - Les Fusillés, Alger*).

---

## 2. Systematic Text Extraction Diagnostic Audit

Because PDF is a visual layout specification (based on absolute 2D Cartesian coordinate positioning `(x, y)` and glyph drawing operators) rather than a semantic markup language (like XML or HTML), programmatic text extraction using stream readers (such as `pypdf`) introduces severe morphological and syntactic anomalies.

### 2.1 Empirical Corpus Measurements (50 Consecutive Issues - 2024)
- **Total Valid Documents Collected:** 50 (`F2024001.pdf` through `F2024050.pdf`)
- **Total Pages Extracted:** 1,472 pages
- **Total Corpus Characters:** 5,324,347 characters
- **Total Lines Scanned:** 192,205 lines

### 2.2 Formal Analysis Table of Extraction Problems & Impact on BPE

| Anomaly Class | Quantitative Prevalence (Corpus 2024) | Empirical Example / Detection Pattern | PDF Rendering Root Cause | Detrimental Impact on BPE Subword Tokenization |
|---|---|---|---|---|
| **[a] Broken Line Breaks Inside Sentences** | **45,328** occurrences (50/50 docs - 100%) | `"...relative à la conformité de la loi \n organique modifiant..."` | PDF engines emit hard newline delimiters (`\n` or `0x0A`) at the end of every visual bounding box line (`T*` / `Td` operators), regardless of grammatical continuity. | Destroys sentence boundaries; creates artificial word-terminal tokens. When BPE learns merge rules across whitespace boundaries, words preceding a hard break are treated as line-terminal, preventing bigram merging with subsequent words. |
| **[b] End-of-Line Word Hyphenation Splits** | **195** occurrences (39/50 docs - 78%) | `'sous- programmes'` $\to$ `[sous-, programmes]`, `'admi-\nnistration'` $\to$ `'admi-'` + `'nistration'` | Justified column typesetting splits words across line boundaries with trailing hyphens (`-`). Stream extractors extract both halves as independent lexical units. | **Catastrophic vocabulary fragmentation:** The true subword bigram (e.g., $i + s \to is$) is severed by the hyphen and newline. BPE learns spurious merge rules containing hyphens (e.g., `mi-`, `con-`) and generates orphaned suffix tokens (`nistration`, `tutionnel`), inflating the vocabulary size budget $V$ and crippling embedding semantics. |
| **[c] Repetitive Running Headers & Footers** | **2,962** occurrences (50/50 docs - 100%) | `JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE N° 01`, `JJOOUURRNNAALL OOFFFFIICCIIEELL` | Headers and footers are physically redrawn on every single page canvas with identical glyph streams. Synthetic bold headers repeat letters twice to simulate heavy weight. | **Frequency distribution skewing:** BPE iteratively merges symbol pairs by global corpus frequency: $\text{argmax}_{(u, v)} \text{freq}(u, v)$. Highly repetitive administrative headers artificially inflate frequencies of boilerplate tokens (`RÉPUBLIQUE`, `OFFICIEL`, `ALGÉRIENNE`), causing early merge iterations to be monopolized by administrative boilerplate instead of core legal and judicial lexicon. |
| **[d] Isolated Pagination Numbers** | **11,430** occurrences (50/50 docs - 100%) | Standalone lines: `\n 6 \n`, `\n 7 \n` adjacent to page splits. | Footer numbers rendered in isolated text frames centered at the bottom margin of each page canvas. | Injects isolated numerical noise into the token sequence. If not normalized or stripped, digit sequences pollute subword merge candidates (e.g., merging `1` and `5` into `15` as a frequent subword rather than learning semantic linguistic morphemes). |
| **[e] Multiple Spaces & Non-Breaking Spaces** | **22,559** occurrences (50/50 docs - 100%) | Consecutive spaces `[  ]`, narrow spaces, and Latin-1 non-breaking spaces (`\xa0`, `\u202f`). | Variable-width justification in dual-column typesetting adjusts inter-word spacing via PDF horizontal translation vectors (`TJ` operator with negative kerning offsets). French typography also mandates non-breaking spaces before colons and inside legal numbers (`14 000 D.A`). | Character encoding fragmentation. If `\xa0` (U+00A0) is distinct from ASCII `\x20` (U+0020), BPE treats `'loi\xa0n°'` and `'loi n°'` as completely distinct character byte streams, creating redundant subword branches for identical lexical concepts. |
| **[f] Two-Column Layout Interleaving** | **1,953** occurrences (43/50 docs - 86%) | `[Col1: 'Fatiha BENABBOU, membre ;'] <==GAP==> [Col2: 'Abdelouahab KHERIEF, membre ;']` | Coordinate-blind PDF parsers sort text chunks solely by descending vertical coordinate $Y$. When two columns share the same vertical height, the parser reads horizontally across columns ($Y_1^{\text{col1}} \to Y_1^{\text{col2}} \to Y_2^{\text{col1}} \to Y_2^{\text{col2}}$) instead of reading Column 1 sequentially before Column 2. | **Severe syntactic corruption:** Concatenates unrelated legal articles and provisions, producing nonsense n-grams. While BPE operates at the subword level, column interleaving introduces false adjacencies between unrelated words, resulting in aberrant cross-clause merge pairs that never exist in natural French syntax. |

---

## 3. Mathematical & Algorithmic Formulation of BPE Distortion

Byte Pair Encoding constructs a subword vocabulary $V = V_{\text{base}} \cup V_{\text{merges}}$ by greedily optimizing the objective:
$$\text{pair}^* = \arg\max_{(c_i, c_j) \in V \times V} \sum_{w \in \mathcal{C}} \text{count}(w) \cdot \mathbb{I}\{(c_i, c_j) \subseteq w\}$$

Where $\mathcal{C}$ is the training corpus vocabulary with associated word frequencies.

### 3.1 The Hyphenation Defect
Consider a legal keyword $w = \text{"constitutionnalité"}$ occurring $M$ times in the corpus:
- If uncleaned, $k$ occurrences are split as $\text{"consti-"} \parallel \text{"tutionnalité"}$.
- The frequency of the true internal bigram $(i, t)$ is reduced from $M$ to $M - k$.
- Concurrently, spurious bigrams $(i, \text{"-"})$ and $(\text{"-"}, \text{"\n"})$ receive $+k$ frequency.
- Consequently, BPE may prioritize merging spurious boundary pairs before capturing the legitimate French morpheme $\text{"tion"}$ or $\text{"alité"}$.

### 3.2 The Administrative Header Bias
Because each gazette in our 50-issue corpus contains between 20 and 100 pages, the header string `"JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE"` is repeated several thousand times. Without basic preprocessing (Activity II), the initial iterations of BPE allocate valuable merge slots to reconstruct boilerplates:
1. $(O, U) \to OU$
2. $(R, N) \to RN$
3. $(J, OU) \to JOU$
4. $(JOU, RN) \to JOURN$
5. $(JOURN, AL) \to JOURNAL$

This exhausts the finite merge budget $K$ on structural noise rather than domain-specific legal terminology (e.g., *jurisprudence*, *ordonnance*, *stipulation*, *abrogation*).

---

## 4. Pipeline Structure & Execution Artifacts
- **Downloader:** [`activity_1/downloader.py`](file:///c:/Users/nitro/Desktop/NLP-tps/activity_1/downloader.py)
- **Extractor:** [`activity_1/extractor.py`](file:///c:/Users/nitro/Desktop/NLP-tps/activity_1/extractor.py)
- **Diagnostics:** [`activity_1/diagnostics.py`](file:///c:/Users/nitro/Desktop/NLP-tps/activity_1/diagnostics.py)
- **Single Runner:** [`activity_1/main.py`](file:///c:/Users/nitro/Desktop/NLP-tps/activity_1/main.py) (`activityOne()`)
- **Raw PDFs:** `activity_1/raw_pdfs/` (50 PDF issues, ~15.2 MB)
- **Extracted Text:** `activity_1/extracted_texts/` (50 UTF-8 `.txt` files)
- **Diagnostic Reports:** [`activity_1/reports/extraction_diagnostics_report.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/activity_1/reports/extraction_diagnostics_report.txt) and `.json`.
