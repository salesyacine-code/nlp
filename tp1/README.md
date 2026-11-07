# NLP Lab N° 1: Legal Document Collection and BPE Tokenization
**Institution:** École Militaire Polytechnique (EMP), Département Informatique  
**Course:** Natural Language Processing (NLP)  
**Instructor:** Dr. M’hamed MATAOUI  
**Student:** Master / Engineering Student  
**Academic Year:** 2026–2027  

---

## 📌 Executive Summary & Architecture

This repository contains the complete implementation of **NLP Lab N° 1**, covering the full text processing lifecycle from raw PDF scraping to modern subword tokenization:
$$\text{JORADP Portal} \longrightarrow \text{Automated Crawler} \longrightarrow \text{PDF Extraction} \longrightarrow \text{Basic Cleaning} \longrightarrow \text{Advanced Normalization} \longrightarrow \text{Corpus Construction} \longrightarrow \text{Statistical Evaluation} \longrightarrow \text{BPE Subword Tokenization}$$

```text
tp1/
├── main.py                               # Master unified runner orchestrating all 5 activities
├── README.md                             # Global project documentation
│
├── activity_1/                           # Activity I: JORADP Crawler & PDF Extraction
│   ├── raw_pdfs/                         # 50 downloaded French gazette PDFs (F2024001.pdf - F2024050.pdf)
│   ├── extracted_texts/                  # 50 extracted UTF-8 text files with page markers
│   ├── reports/                          # Diagnostic reports (quantifying 6 anomaly classes)
│   ├── downloader.py                     # Throttled, idempotent HTTP downloader
│   ├── extractor.py                      # pypdf stream text extractor
│   ├── diagnostics.py                    # Programmatic extraction anomaly detector
│   ├── main.py                           # Entrypoint exposing activityOne()
│   └── REPORT_ACTIVITY_1.md              # Academic report for Activity I
│
├── activity_2/                           # Activity II: Basic Preprocessing of the Corpus
│   ├── cleaned_texts/                    # 50 preprocessed, fluent text files
│   ├── reports/                          # Side-by-side visual inspection report & stats
│   ├── preprocessor.py                   # Core cleaning engine & French compound disambiguation
│   ├── cleaner.py                        # Batch corpus preprocessor
│   ├── inspector.py                      # Before vs. After visual evidence generator
│   ├── main.py                           # Entrypoint exposing activityTwo()
│   └── REPORT_ACTIVITY_2.md              # Academic report for Activity II
│
├── activity_3/                           # Activity III: Advanced Preprocessing & Corpus Construction
│   ├── final_corpus/
│   │   ├── texts/                        # 50 final normalized legal document texts
│   │   ├── algerian_legal_corpus_full.txt # Master consolidated corpus file (4.42 MB)
│   │   └── corpus_metadata.json          # Serialized corpus metadata
│   ├── reports/                          # Experiments comparing Numbers, Dates, and Citations
│   ├── advanced_preprocessor.py          # Entity binding, <DATE> and <NUM> normalizer
│   ├── experiments.py                    # Controlled empirical strategy evaluator
│   ├── corpus_builder.py                 # Assembler of final individual and master corpus
│   ├── main.py                           # Entrypoint exposing activityThree()
│   └── REPORT_ACTIVITY_3.md              # Academic report for Activity III
│
├── activity_4/                           # Activity IV: Measure the Effect of Cleaning
│   ├── reports/
│   │   ├── corpus_cleaning_effect_report.txt  # Human-readable completion report
│   │   └── corpus_statistics_comparison.csv   # Official CSV evaluation table
│   ├── evaluator.py                      # 6-metric corpus statistics engine
│   ├── main.py                           # Entrypoint exposing activityFour()
│   └── REPORT_ACTIVITY_4.md              # Academic report for Activity IV
│
└── activity_5/                           # Activity V: Classical Tokenization vs. BPE
    ├── models/
    │   └── bpe_model.json                # Serialized trained BPE model (merges + vocabulary)
    ├── reports/
    │   └── activity_5_bpe_tokenization_report.txt # Three-way comparative evaluation report
    ├── simple_tokenizer.py               # Classical word tokenizer (OOV & vocabulary analysis)
    ├── simple_bpe.py                     # Didactic BPE demonstrator (15 step-by-step merges)
    ├── complete_bpe.py                   # Complete BPE tokenizer (training, storage, inference)
    ├── comparator.py                     # Side-by-side evaluation harness
    ├── main.py                           # Entrypoint exposing activityFive()
    └── REPORT_ACTIVITY_5.md              # Academic report for Activity V
```

---

## 🚀 Quickstart & Execution

All developed entrypoints follow the official lab requirement:
`activityOne`, `activityTwo`, `activityThree`, `activityFour`, `activityFive`.

### Run All 5 Activities Sequentially:
```powershell
python tp1/main.py
```

### Run Any Specific Activity Individually:
```powershell
# Activity I: Collect & Extract 50 gazettes from JORADP
python tp1/main.py --activity 1

# Activity II: Basic Preprocessing & Hyphenation Disambiguation
python tp1/main.py --activity 2

# Activity III: Advanced Normalization & Corpus Construction
python tp1/main.py --activity 3

# Activity IV: Official Before vs. After Statistical Table
python tp1/main.py --activity 4

# Activity V: Train BPE and evaluate on "constitutionnalité"
python tp1/main.py --activity 5
```

---

## 📊 Summary of Laboratory Results

### Activity I: JORADP Collection & Anomaly Diagnostics
- Collected **50 consecutive gazette issues** from year 2024 (`F2024001.pdf` through `F2024050.pdf`).
- Extracted **1,472 pages** and **5,324,347 characters**.
- Programmatically identified:
  - 45,328 broken line breaks inside sentences.
  - 195 hyphenated line splits.
  - 2,962 running gazette headers.
  - 11,430 isolated pagination digits.
  - 22,559 consecutive / non-breaking spaces (`\xa0`).
  - 1,953 two-column reading order interleavings.

### Activity II: Basic Preprocessing
- Purged running headers, footers, and isolated page numbers.
- Implemented linguistic hyphenation disambiguation: preserved true French compound words (`sous-programmes`, `non-respect`, `quarante-quatre`) while rejoining broken layout words (`consti-` + `tutionnel` $\to$ `constitutionnel`).
- Standardized apostrophes (`’` $\to$ `'`), quotes (`« »` $\to$ `"`), and lowercased text with Unicode accent fidelity.
- **Impact:** $-10.89\%$ character reduction (noise removed), $-67.22\%$ line reduction (sentences consolidated).

### Activity III: Advanced Preprocessing & Corpus Construction
- Controlled experiments on **Numbers**: Replacing numbers with `<NUM>` collapsed vocabulary sparsity by **15.65%**, reducing numerical noise in vocabulary from 17.1% to 1.2%.
- Controlled experiments on **Dates**: Collapsing 16,079 dual Hijri/Gregorian date citations into `<DATE>` saved **55,233 redundant tokens** (-7.7% sequence compression).
- Bound **8,966 statutory citations** (`loi_n°_23-23`, `article_15_bis`) into atomic semantic units.
- Built master corpus file: [`tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt) (4.42 MB, 651,165 words).

### Activity IV: Measure the Effect of Cleaning (Official Table)

| Statistic | Before Preprocessing | After Preprocessing | Delta (%) | Scientific Meaning |
|---|---|---|---|---|
| **Documents** | **50** | **50** | **0.00%** | Complete corpus integrity preserved |
| **Characters** | **5,324,347** | **4,181,829** | **-21.46%** | Non-lexical visual noise purged |
| **Tokens** | **757,903** | **591,724** | **-21.93%** | Sequence compression via `<DATE>` and entity binding |
| **Unique tokens** | **22,440** | **19,771** | **-11.89%** | Dense lexical vocabulary without sporadic numbers |
| **Average word length** | **5.11** | **5.75** | **+12.52%** | Elimination of 1-digit noise & word rejoining |
| **Vocabulary size** | **22,440** | **19,771** | **-11.89%** | Cleaned vocabulary for optimal BPE training |

### Activity V: Classical Tokenization vs. Byte Pair Encoding (BPE)
- **Pedagogical BPE:** Demonstrated the discovery of French suffixes (`e</w>`, `s</w>`, `ti`, `on`, `tion`, `ent</w>`).
- **Complete BPE:** Trained 300 merges on the 50-document legal corpus; serialized model to `tp1/activity_5/models/bpe_model.json`.
- **Target Test Word (`"constitutionnalité"`):**
  - Segmented as: **`con + stitu + tion + na + li + t + é</w>`** (7 subwords).
  - Perfectly captures French morphology: prefix `con-`, root stem `stitu-`, nominal action suffix `tion`, and abstract noun quality suffix `na-li-t-é`.
- **Out-of-Vocabulary Resilience:**
  - Words unseen in training (e.g., `"inconstitutionnalité"`, `"anticonstitutionnel"`) cause a fatal `<UNK>` failure under Classical Tokenization.
  - Complete BPE segments them into known morphemes (`in + con + stitu + tion + ...`, `an + ti + con + stitu + ...`) with **zero Out-of-Vocabulary errors** and 100% semantic preservation!

