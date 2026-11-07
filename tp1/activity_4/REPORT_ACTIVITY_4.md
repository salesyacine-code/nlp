# Activity IV: Measure the Effect of Cleaning
**Course:** Natural Language Processing (NLP)  
**Institution:** École Militaire Polytechnique (EMP), Département Informatique  
**Instructor:** Dr. M’hamed MATAOUI  
**Module:** Lab N° 1 — *Legal Document Collection and BPE Tokenization*  

---

## 1. Official Completed Evaluation Table

To measure the impact of basic and advanced preprocessing on our Algerian legal corpus, the 6 core corpus statistics were computed before preprocessing (Activity I raw extracted texts) and after preprocessing (Activity III final constructed corpus).

| Statistic | Before Preprocessing | After Preprocessing | Absolute Change | Relative Change (%) |
|---|---|---|---|---|
| **Documents** | **50** | **50** | 0 | **0.00%** |
| **Characters** | **5,324,347** | **4,181,829** | -1,142,518 | **-21.46%** |
| **Tokens** | **775,827** | **630,522** | -145,305 | **-18.73%** |
| **Unique tokens** | **21,172** | **18,243** | -2,929 | **-13.83%** |
| **Average word length** | **4.97** | **5.33** | +0.36 | **+7.24%** |
| **Vocabulary size** | **21,172** | **18,243** | -2,929 | **-13.83%** |

---

## 2. Progressive 3-Stage Pipeline Evolution

Analyzing the metrics across the intermediate stage (Activity II) reveals the distinct contributions of basic physical cleaning versus advanced semantic normalization:

| Metric | Stage 1: Raw Extracted (Act. I) | Stage 2: Basic Preprocessed (Act. II) | Stage 3: Final Legal Corpus (Act. III) | Net Change (Act. I $\to$ III) |
|---|---|---|---|---|
| **Documents** | 50 | 50 | 50 | 0.00% |
| **Characters** | 5,324,347 | 4,744,725 | 4,181,829 | **-21.46%** |
| **Tokens** | 775,827 | 679,221 | 630,522 | **-18.73%** |
| **Unique tokens** | 21,172 | 21,988 | 18,243 | **-13.83%** |
| **Avg Word Length** | 4.97 chars | 5.32 chars | 5.33 chars | **+7.24%** |
| **Vocabulary Size** | 21,172 | 21,988 | 18,243 | **-13.83%** |

---

## 3. Scientific Analysis & Linguistic Interpretation of Results

### 3.1 Total Characters (-21.46% Reduction)
- **Mechanism:** Over 1.14 million characters of non-lexical noise were purged from the corpus.
- **Root Drivers:**
  - Removal of repetitive running headers on all 1,472 pages (`JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE...`).
  - Elimination of page 1 masthead pricing tables, bank accounts, and postal CCP addresses.
  - Stripping of isolated margin page numbers and website URLs (`www.joradp.dz`).
  - Collapse of excessive tabular padding and non-breaking spaces (`\xa0`).

### 3.2 Total Tokens (-18.73% Reduction)
- **Mechanism:** The total token count decreased from 775,827 to 630,522 (-145,305 tokens).
- **Root Drivers:**
  - Dual date compression: 16,079 dual Hijri/Gregorian date expressions (each spanning 8 to 10 tokens) were collapsed into single `<DATE>` tokens, saving over 55,000 redundant tokens.
  - Elimination of isolated numerical tokens (page numbers, line identifiers).
  - Binding of statutory citations: `loi` + `n°` + `08-09` (3 tokens) was bound into `loi_n°_08-09` (1 token), condensing 8,966 statutory citations.

### 3.3 Unique Tokens & Vocabulary Size (-13.83% Compression)
- **Mechanism:** The vocabulary compressed from 21,172 to 18,243 unique word types (-2,929 types).
- **Root Drivers:**
  - In Stage 2 (Basic Preprocessing), case normalization and hyphen rejoining initially unified word variants, but revealed the underlying lexical spread (21,988 types).
  - In Stage 3 (Advanced Preprocessing), replacing thousands of sporadic, one-off numbers (budget dinar figures, telephone numbers, postal codes) with `<NUM>` collapsed vocabulary sparsity by 3,745 sparse entries.
  - The resulting vocabulary is linguistically dense, containing authentic French legal morphemes, roots, and bound statutory entities.

### 3.4 Average Word Length (+7.24% Increase)
- **Mechanism:** The average word length increased from **4.97 characters to 5.33 characters**.
- **Linguistic Explanation:** This is a hallmark indicator of effective text cleaning:
  1. **Purging of Short Noise:** Thousands of 1-digit and 2-digit page numbers (`6`, `7`, `15`) and short boilerplate abbreviations (`n°`, `d.a`, `p.`) that artificially pulled the mean word length downward were eliminated.
  2. **Recombination of Broken Word Stems:** Hyphenated fragments split across 2-column layout margins (e.g. `consti-` [6] and `tutionnel` [9]) were rejoined into complete legal terms (`constitutionnel` [14]).
  3. **Entity Binding:** Statutory references (e.g. `loi_n°_23-23`, `article_15_bis`) form longer, semantically cohesive multi-word expressions.

---

## 4. Significance for Downstream Byte Pair Encoding (BPE)

The quantitative enhancements directly address the primary failure modes of subword tokenization:
1. **Merge Budget Conservation:** With 21.46% of boilerplate noise and 17.1% of numerical sparsity eliminated, BPE's finite merge budget $K$ is dedicated entirely to learning meaningful morphological subwords (*pré-*, *in-*, *dé-*, *-tion*, *-ment*, *-alité*).
2. **Elimination of Spurious Bigrams:** Severed line-break hyphens (`admi- / nistratif`) no longer generate invalid subwords (`admi-`, `nistratif`).
3. **Context Length Optimization:** The 18.73% token reduction allows downstream Transformer models to encode nearly 20% more legal provisions within the same fixed context window (e.g., 512, 2048, or 8192 tokens).

---

## 5. Artifacts and Directory Layout
- **Evaluator Script:** [`tp1/activity_4/evaluator.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_4/evaluator.py)
- **Single Runner:** [`tp1/activity_4/main.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_4/main.py) (`activityFour()`)
- **Text Report:** [`tp1/activity_4/reports/corpus_cleaning_effect_report.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_4/reports/corpus_cleaning_effect_report.txt)
- **CSV Comparison Table:** [`tp1/activity_4/reports/corpus_statistics_comparison.csv`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_4/reports/corpus_statistics_comparison.csv)
- **JSON Structured Metrics:** [`tp1/activity_4/reports/corpus_cleaning_effect_report.json`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_4/reports/corpus_cleaning_effect_report.json)

