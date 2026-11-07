# Activity III: Advanced Preprocessing & Legal Corpus Construction
**Course:** Natural Language Processing (NLP)  
**Institution:** École Militaire Polytechnique (EMP), Département Informatique  
**Instructor:** Dr. M’hamed MATAOUI  
**Module:** Lab N° 1 — *Legal Document Collection and BPE Tokenization*  

---

## 1. Objectives & Advanced Pipeline Overview

While Activity II tackled physical PDF extraction defects (line wraps, headers, page numbers, apostrophes, and basic hyphenation), **Activity III** focuses on **domain-specific legal text structuring** and **subword vocabulary optimization** for Byte Pair Encoding (BPE).

The four central tasks of this activity are:
1. **Handling Structured Legal References:** Standardizing and binding citations (*Lois, Décrets exécutifs, Décrets présidentiels, Articles*).
2. **Experimenting with Number Normalization:** Empirical evaluation of *Preserved Verbatim* vs. *Normalized Formats* vs. *Special Token `<NUM>`*.
3. **Experimenting with Date Normalization:** Empirical evaluation of *Preserved Verbatim* vs. *Canonical Format* vs. *Special Token `<DATE>`* across dual Hijri/Gregorian timelines.
4. **Eliminating Residual Metadata & Web Boilerplate:** Stripping URLs, emails, download stamps, and decorative table leaders.
5. **Constructing the Final Corpus:** Producing 50 individual processed text files and an aggregated full-text corpus (`algerian_legal_corpus_full.txt`) for downstream statistical measurement (Activity IV) and BPE tokenization (Activity V).

---

## 2. Methodology & Domain-Specific Formulations

### 2.1 Structured Legal References
Legal texts are characterized by statutory citation syntaxes:
- **Laws:** `loi n° 08-09`, `loi organique n° 18-15`
- **Decrees:** `décret exécutif n° 21-123`, `décret présidentiel n° 24-02`
- **Articles:** `article 15`, `article 15 bis`, `article 15-1`, `art. 23`

#### Strategic Options:
- **Strategy A (Preserve - Unbound):** Kept as separate whitespace-delimited tokens (`['loi', 'n°', '08-09']`). Under BPE, numbers in citations are dissociated from their statutory nature and fragmented across arbitrary subword boundaries.
- **Strategy B (Bound Entities - Recommended):** Spaces are replaced with underscores to bind statutory entities into atomic linguistic units:
  $$\text{"loi n° 08-09"} \longrightarrow \text{"loi\_n°\_08-09"}$$
  $$\text{"article 15 bis"} \longrightarrow \text{"article\_15\_bis"}$$
  This preserves the exact identity of the legal statute while preventing BPE from splintering the reference.
- **Strategy C (Entity Tokens):** Citations are abstracted into special tokens (`<LEGAL_REF:LOI>`, `<LEGAL_REF:DECRET>`, `<ARTICLE_REF>`).

### 2.2 Number Normalization Dilemma
Legal gazettes are saturated with numerical quantities: budget allocations in Algerian Dinars (D.A), fiscal years, telephone/fax numbers, postal accounts (CCP), percentages, and sequential article indices.
We evaluated three strategies:
- **Preserved Exactly:** Retain raw numerical strings (`1090,00`, `647028780000`, `023.41.18.89`).
- **Normalized Format:** Standardize commas to dots and strip internal thousand-separator spaces.
- **Replaced with `<NUM>`:** Map non-reference numerical quantities to the atomic token `<NUM>`.

### 2.3 Date Normalization Dilemma
Algerian legal documents mandate a **dual calendar system**, combining the Islamic Hijri calendar with the Gregorian civil calendar:
$$\text{"25 Joumada Ethania 1445 correspondant au 7 janvier 2024"}$$
We evaluated three strategies:
- **Preserved Verbatim:** Retains all 8 to 10 words per date expression.
- **Canonical Format:** Harmonizes dates into unified bracketed expressions (`[date: ...]`).
- **Replaced with `<DATE>`:** Collapses the entire dual-calendar span into the atomic token `<DATE>`.

---

## 3. Empirical Experimental Results Across the 50-Document Corpus

The controlled experiments yielded the following quantitative results across the 50 legal gazettes:

```text
======================================================================================
     ACTIVITY III: ADVANCED PREPROCESSING STRATEGY EXPERIMENTAL EVALUATION
         Ecole Militaire Polytechnique - Natural Language Processing
======================================================================================
 Total Analyzed Documents : 50
--------------------------------------------------------------------------------------
 EXPERIMENT 1: NUMBERS (PRESERVED vs. NORMALIZED vs. <NUM>)
--------------------------------------------------------------------------------------
 Strategy                   | Total Tokens  | Vocab Size  | Num Vocab %  | Vocab Reduction
--------------------------------------------------------------------------------------
 Preserved Exactly          | 716,370       | 32,466      |       17.1% |          0.00%
 Normalized Format          | 700,074       | 32,481      |       17.2% |         -0.05%
 Replaced with <NUM>        | 729,670       | 27,384      |        1.2% |        +15.65%
--------------------------------------------------------------------------------------
 EXPERIMENT 2: DATES (PRESERVED vs. UNIFIED FORMAT vs. <DATE>)
--------------------------------------------------------------------------------------
 Strategy                   | Total Tokens  | Vocab Size  | Avg Token Len | Vocab Reduction
--------------------------------------------------------------------------------------
 Preserved Verbatim         | 716,370       | 32,466      |         5.22 |          0.00%
 Unified Canonical Format   | 749,232       | 32,479      |         5.26 |         -0.04%
 Replaced with <DATE>       | 661,137       | 32,354      |         5.26 |         +0.34%
--------------------------------------------------------------------------------------
 EXPERIMENT 3: LEGAL REFERENCES (UNBOUND vs. BOUND ENTITIES vs. SPECIAL TOKENS)
--------------------------------------------------------------------------------------
 Strategy                   | Total Tokens  | Vocab Size  | Avg Token Len | Vocab Impact   
--------------------------------------------------------------------------------------
 Preserved (Unbound Tokens) | 716,370       | 32,466      |         5.22 |          0.00%
 Bound Entities (loi_n°_XX) | 703,906       | 32,666      |         5.35 |         -0.62%
 Special Entity Tokens      | 703,906       | 31,263      |         5.34 |         +3.71%
======================================================================================
```

---

## 4. Key Scientific Insights & Discussion

### 4.1 Why Replacing Numbers with `<NUM>` is Essential for BPE
- In the baseline corpus, **17.1% of the entire vocabulary** (5,550+ distinct unique types) consists of arbitrary numbers (budget amounts, phone numbers, postal accounts).
- Leaving numbers raw forces BPE to exhaust a large portion of its merge operations on non-semantic digit combinations (e.g. `2` + `4` $\to$ `24`, `0` + `0` $\to$ `00`, `00` + `0` $\to$ `000`).
- Replacing isolated numbers with `<NUM>` yields a **15.65% reduction in vocabulary sparsity** ($32,466 \to 27,384$) while suppressing numerical noise in the vocabulary down to **1.2%**.

### 4.2 Why Collapsing Dual Dates into `<DATE>` Improves Efficiency
- Each dual date citation consumes between 7 and 10 tokens:
  $$\text{"25"} + \text{"joumada"} + \text{"ethania"} + \text{"1445"} + \text{"correspondant"} + \text{"au"} + \text{"7"} + \text{"janvier"} + \text{"2024"}$$
- Across the corpus, 16,079 date expressions appear.
- Collapsing these into `<DATE>` saves **55,233 redundant tokens** (reducing total token length from $716,370 \to 661,137$, a **$-7.7\%$ sequence compression**), drastically reducing context window overhead for downstream language models.

### 4.3 Why Binding Legal References (`ref_mode="bind"`) Preserves Statutory Integrity
- Binding citations (producing `loi_n°_23-23`, `décret_exécutif_n°_24-12`, `article_15_bis`) prevents tokenizers from treating statutory identifiers as isolated digits or punctuation.
- It binds **8,966 statutory citations** into distinct, self-contained domain entities without losing specific legislative references.

---

## 5. Final Constructed Corpus Metrics

The optimal configuration (`ref_mode="bind"`, `date_mode="token"`, `num_mode="token"`) was applied to all 50 documents, creating the official final corpus:

```text
==================================================================================
           ACTIVITY III: FINAL CONSTRUCTED LEGAL CORPUS METRICS
==================================================================================
 Total Legal Documents Collected : 50
 Total Processed Characters      : 4,181,829
 Total Words (Tokens)            : 651,165
 Total Paragraph / Clause Lines  : 39,934
 Final Vocabulary Size (|V|)     : 27,915 unique words
 Bound Legal Citations           : 8,966 (lois, décrets, arrêtés, articles)
 Normalized Date Instances       : 16,079
 Normalized Number Instances     : 67,307
 Master Consolidated Corpus File : tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt
==================================================================================
```

---

## 6. Directory Layout & Artifacts
- **Advanced Preprocessor:** [`tp1/activity_3/advanced_preprocessor.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/advanced_preprocessor.py)
- **Experimental Evaluator:** [`tp1/activity_3/experiments.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/experiments.py)
- **Corpus Builder:** [`tp1/activity_3/corpus_builder.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/corpus_builder.py)
- **Entrypoint:** [`tp1/activity_3/main.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/main.py) (`activityThree()`)
- **Individual Clean Texts:** `tp1/activity_3/final_corpus/texts/` (50 `.txt` files)
- **Master Corpus File:** [`tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/final_corpus/algerian_legal_corpus_full.txt)
- **Reports:** [`tp1/activity_3/reports/advanced_preprocessing_experiments.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/reports/advanced_preprocessing_experiments.txt) and [`corpus_metadata.json`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_3/final_corpus/corpus_metadata.json).

