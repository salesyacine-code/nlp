# Activity V: Classical Tokenization vs. Byte Pair Encoding (BPE)
**Course:** Natural Language Processing (NLP)  
**Institution:** École Militaire Polytechnique (EMP), Département Informatique  
**Instructor:** Dr. M’hamed MATAOUI  
**Module:** Lab N° 1 — *Legal Document Collection and BPE Tokenization*  

---

## 1. Objectives & Theoretical Progression

Tokenization is the foundational entry point of all modern Natural Language Processing pipelines. This activity examines the evolution from **Classical Word-Level Splitting** to **Subword Tokenization (Byte Pair Encoding - BPE)** using our preprocessed Algerian legal corpus.

We implemented and contrasted three progressive approaches:
1. **Classical / Simple Word Tokenizer:** Whitespace and regex splitting with a fixed dictionary and Out-of-Vocabulary (`<UNK>`) fallback.
2. **Simple BPE (Pedagogical):** A compact demonstrator illustrating the step-by-step discovery and greedy merging of adjacent character pairs.
3. **Complete BPE Tokenizer:** A full subword tokenizer that learns 300 ranked merge operations from the master legal corpus, serializes the model to JSON, and segments unseen words (specifically testing **`"constitutionnalité"`**).

---

## 2. Simple BPE: Pedagogical Step-by-Step Merge Progression

BPE begins by treating all words as whitespace-separated sequences of base characters terminated by an end-of-word marker (`</w>`). At each iteration $k$, it selects the pair $(c_i, c_j)$ that maximizes corpus frequency:
$$(c_i^*, c_j^*) = \arg\max_{(c_i, c_j)} \text{freq}(c_i, c_j)$$

Below is the empirical progression of the **Top 15 Merges** learned from the legal corpus:

| Step | Merged Pair $(c_1, c_2)$ | Co-occurrence Frequency | Resulting Subword | Linguistic Significance in French Legal Text |
|---|---|---|---|---|
| **1** | `('e', '</w>')` | 1,072 | `e</w>` | Feminine and mute endings (e.g., *loi*, *république*) |
| **2** | `('s', '</w>')` | 955 | `s</w>` | Plural grammatical suffix (*lois*, *décrets*, *articles*) |
| **3** | `('t', '</w>')` | 771 | `t</w>` | Verb agreement & noun endings (*décret*, *état*) |
| **4** | `('t', 'i')` | 672 | `ti` | Common syllable for abstract suffix derivation |
| **5** | `('o', 'n')` | 517 | `on` | Nasal vowel bigram |
| **6** | `('e', 'n')` | 511 | `en` | Preposition *en* and participial/adverbial morpheme |
| **7** | `('e', 's</w>')` | 460 | `es</w>` | Plural inflection (*dépenses*, *finances*) |
| **8** | `('d', 'e</w>')` | 423 | `de</w>` | Highest-frequency legal preposition (*de la république*) |
| **9** | `('u', '</w>')` | 407 | `u</w>` | Past participle ending (*vu*, *conclu*) |
| **10** | `('l', 'a')` | 351 | `la` | Definite feminine article (*la loi*, *la cour*) |
| **11** | `('ti', 'on')` | 343 | `tion` | **Nominal action/result suffix** (*constitution*, *juridiction*) |
| **12** | `('la', '</w>')` | 307 | `la</w>` | Complete grammatical word *la* |
| **13** | `('a', 'n')` | 299 | `an` | Common French syllable |
| **14** | `('en', 't</w>')` | 297 | `ent</w>` | 3rd person plural verb inflection (*portent*, *stipulent*) |
| **15** | `('n', 'u')` | 277 | `nu` | Common stem syllable |

> **Key Observation:** Notice that at **Step 4** `('t', 'i')` is formed, at **Step 5** `('o', 'n')` is formed, and at **Step 11** they combine into `('ti', 'on') \to tion`. BPE automatically rediscovers French morphological derivation without any hand-crafted grammatical rules!

---

## 3. Evaluation on the Mandatory Legal Test Word: *"constitutionnalité"*

The laboratory assignment explicitly requires testing the trained Complete BPE Tokenizer on the complex legal term **`"constitutionnalité"`**.

### 3.1 Empirical BPE Segmentation Trace
```text
Input Word       : constitutionnalité
Initial Pieces   : c + o + n + s + t + i + t + u + t + i + o + n + n + a + l + i + t + é</w>
Learned Subwords : con + stitu + tion + na + li + t + é</w>
Subword Count    : 7 subword pieces
Subword Token IDs: [94, 293, 313, 214, 197, 297, 367]
Reconstruction   : "constitutionnalité" (100% lossless match)
```

### 3.2 Morphological Analysis of the Subword Split
The Complete BPE tokenizer decomposes `"constitutionnalité"` into structurally meaningful morphological components:
1. `con-` : Common French Latinate prefix indicating union or assembly.
2. `stitu` : Root verb stem (*constituer*, *institution*, *statut*).
3. `tion` : Nominal suffix denoting the action or resulting state.
4. `na` + `li` + `t` + `é</w>` : Morphemes constructing the abstract property suffix *-alité* (forming an abstract noun of quality).

---

## 4. Three-Way Comparative Evaluation Across Legal Vocabulary

We tested a battery of legal words spanning unseen terms, derivatives, and frequent vocabulary across Classical Word Tokenization, Simple BPE, and Complete BPE:

| Test Word | Classical (Word-Level) | Simple BPE (15 Merges) | Complete BPE (300 Merges) | Morphological Interpretation |
|---|---|---|---|---|
| **constitutionnalité** | `[constitutionnalité]` | `c + on + s + ti + t + u + tion + n + a + l + i + t + é</w>` | **`con + stitu + tion + na + li + t + é</w>`** | BPE isolates stem and suffix *-tion* and quality morphemes. |
| **inconstitutionnalité** | **`<UNK>` (FATAL OOV)** | `i + n + c + on + s + ti + t + u + tion + n + a + l + i + t + é</w>` | **`in + con + stitu + tion + na + li + t + é</w>`** | **BPE isolates negative prefix `in-`**; classical fails completely. |
| **décret** | `[décret]` | `d + é + c + r + e + t</w>` | **`décret</w>`** | Frequent legal word merged into a single atomic token. |
| **anticonstitutionnel** | **`<UNK>` (FATAL OOV)** | `an + ti + c + on + s + ti + t + u + tion + n + e + l</w>` | **`an + ti + con + stitu + tion + n + el</w>`** | BPE isolates `anti-` prefix and `-el` adjective ending. |
| **jurisprudence** | `[jurisprudence]` | `j + u + r + i + s + p + r + u + d + en + c + e</w>` | **`j + ur + is + pr + u + d + en + ce</w>`** | Decomposed into common phonological clusters. |
| **loi_organique** | **`<UNK>`** (if unbound) | `l + o + i + _ + o + r + g + an + i + q + u + e</w>` | **`loi + _ + organ + i + que</w>`** | Reconstructs statutory compound from constituent roots. |
| **superficie** | `[superficie]` | `s + u + p + e + r + f + i + c + i + e</w>` | **`su + per + fi + ci + e</w>`** | Segmented into frequent Latinate syllables. |

---

## 5. Paradigmatic Comparison Matrix

| Architectural Dimension | Classical Word-Level Tokenization | Byte Pair Encoding (BPE) Subword Tokenization |
|---|---|---|
| **Vocabulary Size ($|V|$)** | **Explosive & Open-Ended:** Typically $> 20,000$ to $100,000$ words. Every inflection requires its own entry. | **Compact & Fixed:** Bounded by design (e.g., $525$ tokens in our 300-merge model; typically 32k in LLaMA/Mistral). |
| **Out-of-Vocabulary (OOV) Resilience** | **Catastrophic:** Any unseen word is replaced by `<UNK>`, destroying all semantic information. | **Zero OOV:** 100% vocabulary coverage. Unseen words fall back gracefully to character combinations. |
| **Morphological Generalization** | **None:** Treats *constitution*, *constitutionnel*, and *inconstitutionnalité* as completely unrelated integers. | **High:** Shares subword embeddings (`constitut`, `tion`), allowing transfer of syntactic/semantic knowledge. |
| **Sequence Length** | 1 token per word (shortest sequence). | 1.2 to 2.5 tokens per word (slight expansion for rare words). |
| **Embedding Matrix Size** | Enormous memory footprint: $|V| \times d_{\text{model}}$ requires gigabytes of parameters. | Highly parameter-efficient: dense embedding representations. |
| **Modern LLM Alignment** | Obsolete for generative language modeling. | **Standard Foundation:** Underpins GPT-4, LLaMA-3, Mistral, Gemma, and BERT. |

---

## 6. Directory Layout & Artifacts
- **Classical Tokenizer:** [`tp1/activity_5/simple_tokenizer.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/simple_tokenizer.py)
- **Simple BPE Demonstrator:** [`tp1/activity_5/simple_bpe.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/simple_bpe.py)
- **Complete BPE Tokenizer:** [`tp1/activity_5/complete_bpe.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/complete_bpe.py)
- **Comparator Harness:** [`tp1/activity_5/comparator.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/comparator.py)
- **Single Runner:** [`tp1/activity_5/main.py`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/main.py) (`activityFive()`)
- **Serialized Model:** [`tp1/activity_5/models/bpe_model.json`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/models/bpe_model.json)
- **Report:** [`tp1/activity_5/reports/activity_5_bpe_tokenization_report.txt`](file:///c:/Users/nitro/Desktop/NLP-tps/tp1/activity_5/reports/activity_5_bpe_tokenization_report.txt).

