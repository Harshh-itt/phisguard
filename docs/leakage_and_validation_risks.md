# PhishGuard — Data Leakage and Validation Risk Investigation

## 1. Executive Summary & Purpose

A critical vulnerability in machine-learning-based phishing detection is **evaluation leakage**, where a model appears highly accurate during offline cross-validation but suffers catastrophic degradation when deployed against novel, real-world URLs.

In accordance with [AGENTS.md](file:///D:/PHISH/AGENTS.md), this document records an empirical investigation into data leakage risks, duplicate records, domain-level clustering, and evaluation methodologies within the raw UCI PhiUSIIL Phishing URL Dataset (`data/raw/PhiUSIIL_Phishing_URL_Dataset.csv`).

This investigation does not implement data transformations or lock the final split strategy (which is formally designated for Phase 5). Rather, it provides the evidence base required to design rigorous validation protocols.

---

## 2. Duplicate URL Leakage Analysis

### 2.1 Empirical Findings
Across the 235,795 records in the raw dataset:
- **Total Unique URLs**: 235,370.
- **Duplicate URL Rows**: Exactly 850 rows (representing 425 unique URLs that each appear exactly twice).
- **Class Distribution of Duplicates**:
  - **Phishing (`label == 0`)**: 850 rows (100.0%).
  - **Legitimate (`label == 1`)**: 0 rows (0.0%).
- **Label Consistency**: Exactly 0 conflicting labels among duplicate URLs (100% label consistency).

### 2.2 Leakage Mechanism Under Random Row Splitting
When an unstratified or standard random row split (e.g., 80% train / 20% test) is applied to raw rows:
1. Identical URL strings are randomly assigned across both the training set and the test set.
2. In our empirical simulation of a random 80/20 split, **134 duplicate URLs crossed the partition boundary**.
3. During evaluation, the model is tested on URLs that it already observed during gradient updates or tree branch construction.
4. Because all duplicate URLs are phishing, this introduces an artificial performance boost and direct label memorization on the minority class.

**Finding**: Exact duplicate URLs represent an unambiguous source of data leakage and must be resolved before final model evaluation.

---

## 3. Domain Duplication & Label Consistency Investigation

### 3.1 Domain Repetition Findings
- **Total Unique Domains**: 220,086.
- **Rows with Repeated Domains**: 21,235 rows.
- **Unique Domains Appearing More Than Once**: 5,526 domains.
- **Domain Label Consistency**:
  - Repeated domains with **100% consistent labels**: 5,472 domains (99.02%).
  - Repeated domains with **conflicting labels**: 54 domains (0.98%).

### 3.2 Conflicting-Label Domains (Shared & Compromised Infrastructure)
The 54 conflicting domains contain URLs that are labeled as legitimate in some records and phishing in others. Notable examples include:

| Domain | Phishing Rows (`0`) | Legitimate Rows (`1`) | Total Rows | Nature of Domain |
|---|---:|---:|---:|---|
| `www.indushealthplus.com` | 3 | 1 | 4 | Healthcare portal / compromised sub-paths |
| `www.kashmirhills.com` | 2 | 1 | 3 | Regional portal / compromised sub-paths |
| `www.poompuhar.com` | 2 | 1 | 3 | Commercial site / compromised sub-paths |
| `www.cutt.ly` | 1 | 1 | 2 | Public URL shortener |
| `www.drivehq.com` | 1 | 1 | 2 | Cloud storage / hosting service |
| `www.dynu.com` | 1 | 1 | 2 | Dynamic DNS provider |
| `www.ecrater.com` | 1 | 1 | 2 | Multi-tenant e-commerce platform |
| `www.coinmama.com` | 1 | 1 | 2 | Cryptocurrency exchange portal |

### 3.3 Key Architectural Takeaway
The existence of conflicting domains proves that **domain name alone is not a sufficient classification criterion**:
- Legitimate multi-tenant platforms (e.g., cloud storage, dynamic DNS, URL shorteners, blog hosts) are frequently abused by adversaries to host phishing pages alongside benign content.
- Compromised legitimate websites often have specific phishing paths or query parameters injected while the root domain remains legitimate.
- Therefore, a defensive model must evaluate **path, query, and lexical structure**, rather than relying solely on hostname memorization.

---

## 4. Limitations of Standard Random Row Splitting

To quantify how standard validation behaves on this dataset, we simulated an 80/20 stratified random row split:

| Metric | Measured Value | Percentage |
|---|---:|---:|
| Total Test Rows (20% sample) | 47,159 | 100.00% |
| Unique Domains in Test Set | 45,177 | — |
| Test Domains also present in Training Set | 2,189 | 4.85% |
| **Test Rows whose domain was seen during training** | **3,992** | **8.46%** |
| Exact Duplicate URLs crossing partition boundary | 134 | 0.28% |

### Core Limitations
1. **Domain Overlap**: Nearly 8.5% of all test predictions occur on domains that the model already encountered in the training partition. If a decision tree or neural network learns feature representations that correlate with known domains, it benefits from an unearned advantage on these test records.
2. **Optimistic In-Distribution Estimates**: Standard random splitting evaluates whether a model can recognize variations of previously seen domains. While relevant for tracking known campaigns, it systematically overestimates real-world efficacy against zero-day phishing campaigns.
3. **Imbalance in Duplicates**: Because all 850 duplicate rows are phishing instances, random splitting disproportionately deflates test false-negative rates.

---

## 5. Domain-Aware Evaluation as a Separate Generalization Question

### 5.1 What is Domain-Aware Evaluation?
Domain-aware evaluation (such as `GroupShuffleSplit` grouped by domain or FQDN) guarantees that **no domain appearing in the test partition has ever been seen in the training partition**.

### 5.2 Research & Evaluation Trade-offs
Evaluating phishing detectors across domain boundaries poses a distinct scientific question:

```
┌────────────────────────────────────────────────────────┐
│                   Evaluation Paradigms                 │
├───────────────────────────┬────────────────────────────┤
│ In-Distribution Evaluation│ Domain-Disjoint Evaluation │
│ (Standard Split)          │ (Group-Aware Split)        │
├───────────────────────────┼────────────────────────────┤
│ • Tests performance on    │ • Tests zero-day           │
│   observed ecosystem      │   generalization on        │
│ • ~8.5% domain overlap    │   completely novel domains │
│ • Evaluates known brand   │ • Evaluates pure syntactic │
│   and host patterns       │   and lexical rules        │
│ • Higher apparent accuracy│ • Tougher, more realistic  │
│   reported in literature  │   adversarial benchmark    │
└───────────────────────────┴────────────────────────────┘
```

### 5.3 Methodological Challenges of Domain-Disjoint Splitting
1. **Multi-Tenant Distortion**: For shared domains (e.g., `drivehq.com`, `cutt.ly`), placing all instances into either train or test prevents the model from learning how to differentiate legitimate from phishing paths on the same host.
2. **Class Ratio Skew**: Certain high-volume domains may heavily skew the target class balance if assigned entirely to one fold.
3. **Comparison with Benchmark Literature**: Published papers on the PhiUSIIL dataset generally report standard random k-fold cross-validation metrics. Presenting only domain-disjoint results would hinder direct comparison with baseline literature, while presenting only random splits obscures zero-day generalization.

**Recommendation for Phase 5**:
When the experiment protocol is locked in Phase 5, PhishGuard should report primary metrics on a clean, deduplicated in-distribution holdout set to enable baseline comparison, while investigating a domain-disjoint secondary benchmark to rigorously test zero-day generalization.

---

## 6. Target-Correlated Heuristic Leakage

### 6.1 The `URLSimilarityIndex` Anomaly
- Correlation with `label`: **+0.860358**.
- Median Value: **100.0** (both 50th and 75th percentiles are exactly 100.0).
- Nature of Feature: The UCI documentation defines this as a similarity index between the submitted URL tokens and precompiled lists of legitimate domain tokens.
- **Leakage Risk**: If the reference token dictionary was compiled with knowledge of the dataset's legitimate class or if phishing URLs systematically yield low similarity against a closed set, this feature acts as a proxy for the target label rather than an intrinsic URL property.
- **Inference Risk**: At serving time, PhishGuard cannot compute `URLSimilarityIndex` without embedding the exact, unversioned reference token corpus used by the dataset authors.

**Verdict**: Renders models brittle and introduces unverified distribution assumptions. Excluded from PhishGuard feature selection.

---

## 7. Actionable Directives for Upcoming Phases

1. **Phase 3 (Data Quality & Leakage Controls)**:
   - Deduplicate the 425 duplicate URLs (850 rows) to prevent identical URL cross-contamination.
   - Maintain the raw dataset in `data/raw/` strictly immutable; output deduplicated interim data to `data/interim/`.
2. **Phase 4 (Preprocessing & Feature Engineering)**:
   - Exclude `FILENAME`, all 27 webpage attributes, and unverified heuristics (`URLSimilarityIndex`, `TLDLegitimateProb`, `URLCharProb`).
   - Extract features strictly using `src.features.extract.extract_features()`.
3. **Phase 5 (Train/Validation/Test Protocol)**:
   - Seal the holdout test set before hyperparameter tuning.
   - Consider both standard stratified evaluation (for comparability with published benchmarks) and domain-aware evaluation (for zero-day robustness analysis).
   - Do not claim model superiority without empirical, controlled measurements.
