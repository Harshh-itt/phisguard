# PhishGuard — Train/Test Split Protocol & Stratification Specification

## 1. Executive Summary & Purpose

A fundamental failure mode in machine learning for cybersecurity is **evaluation leakage**, where a model appears highly accurate during training/validation but degrades significantly when confronted with zero-day attacks or novel infrastructure. 

In accordance with [AGENTS.md](file:///D:/PHISH/AGENTS.md) and findings in [docs/leakage_and_validation_risks.md](file:///D:/PHISH/docs/leakage_and_validation_risks.md), Phase 5 implements a **reproducible, 80/20, domain-grouped and class-stratified train/test split** on the cleaned interim dataset (`data/interim/cleaned_phiusiil.csv`).

This document records the mathematical design, empirical validation results, domain isolation proofs, and operational rules governing the partitioned datasets.

---

## 2. Leakage Vulnerability of Standard Random Splitting

Prior to locking this protocol, empirical analysis established the failure mechanisms of standard unstratified or random row splitting:

1. **Domain Memorization Leakage**: In a standard random 80/20 split, **3,992 test rows (8.46% of the test partition)** shared domains with URLs in the training set. A model evaluated under this regime benefits from an artificial advantage by memorizing domain characteristics rather than generalizing static lexical patterns.
2. **Duplicate Contamination**: In the raw dataset, all 850 duplicate rows (425 distinct URLs) belong to the phishing class (`label == 0`). In unstratified random splits, identical phishing URLs cross partition boundaries, artificially inflating recall and deflating false-negative rates.
3. **Optimistic Benchmark Distortions**: While random row splits reflect performance against previously seen ecosystem infrastructure, they do not simulate realistic zero-day deployment against novel, unencountered domains.

---

## 3. The Domain-Grouped Stratified Protocol

To eliminate evaluation leakage while preserving class proportions, PhishGuard applies **`StratifiedGroupKFold`** from `scikit-learn` with 5 folds and a fixed random seed.

### 3.1 Mathematical Formulation
Let the dataset $\mathcal{D} = \{(\mathbf{x}_i, y_i, g_i)\}_{i=1}^N$ comprise:
- Input URL record $\mathbf{x}_i$
- Target label $y_i \in \{0, 1\}$ (where $0 = \text{phishing}$, $1 = \text{legitimate}$)
- Group identifier $g_i = \text{lower}(\text{Domain}_i)$

The partitioning maps groups to partitions $\mathcal{D}_{\text{train}}$ and $\mathcal{D}_{\text{test}}$ subject to:
1. **Strict Domain Isolation**:
   $$\mathcal{G}_{\text{train}} \cap \mathcal{G}_{\text{test}} = \emptyset, \quad \text{where } \mathcal{G} = \{g_i\}$$
2. **Class Balance Preservation**:
   $$\frac{\sum_{i \in \text{train}} \mathbb{I}(y_i = 1)}{|\mathcal{D}_{\text{train}}|} \approx \frac{\sum_{j \in \text{test}} \mathbb{I}(y_j = 1)}{|\mathcal{D}_{\text{test}}|} \approx \frac{\sum_{k=1}^N \mathbb{I}(y_k = 1)}{N}$$
3. **Approximate 80/20 Ratio**:
   $$\frac{|\mathcal{D}_{\text{test}}|}{N} \approx 0.20, \quad \frac{|\mathcal{D}_{\text{train}}|}{N} \approx 0.80$$

Fold 0 of a 5-fold `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` is designated as the holdout test partition ($\sim 20\%$), while folds 1 through 4 are combined into the training partition ($\sim 80\%$).

---

## 4. Empirical Split Validation Results

The partition was executed on the 235,370 clean rows of `data/interim/cleaned_phiusiil.csv`. The measured results are recorded below:

| Metric | Interim Dataset (Total) | Training Partition (`train.csv`) | Test Partition (`test.csv`) | Target / Tolerance |
|---|---:|---:|---:|---|
| **Total Rows** | `235,370` (100.0%) | `188,296` (**80.00%**) | `47,074` (**20.00%**) | Exact 80.00% / 20.00% |
| **Unique Domains** | `220,086` | `176,072` | `44,014` | Complete domain coverage |
| **Domain Overlap** | — | **0** | **0** | **0 (Zero domain leakage)** |
| **Phishing Rows (`label == 0`)** | `100,520` (42.71%) | `80,416` (42.71%) | `20,104` (42.71%) | Preserved to 4 decimal places |
| **Legitimate Rows (`label == 1`)** | `134,850` (57.29%) | `107,880` (57.29%) | `26,970` (57.29%) | Preserved to 4 decimal places |
| **Legitimate Ratio** | `0.5729` | **`0.5729`** | **`0.5729`** | Exact match |
| **Phishing Ratio** | `0.4271` | **`0.4271`** | **`0.4271`** | Exact match |
| **Random Seed** | `42` | `42` | `42` | Deterministic reproducibility |

---

## 5. Handling Multi-Tenant & Conflicting Domains

Our provenance audit identified **54 unique domains** in the dataset that contain both legitimate and phishing URLs (e.g., shared cloud hosts, URL shorteners, dynamic DNS providers like `drivehq.com`, `cutt.ly`, and compromised web portals).

### Operational Invariant
Under `StratifiedGroupKFold`:
- Multi-tenant domains are **assigned as atomic units** to either the train partition or the test partition.
- They are **never split across partitions**.
- Verified in unit test `test_conflicting_label_domain_stays_in_single_partition`: all records associated with a given domain remain in exactly one partition.

---

## 6. Role and Boundaries of the `Domain` Field

1. **Retained for Lineage and Grouping**:
   - `Domain` is retained in `data/processed/train.csv` and `data/processed/test.csv`.
   - Its presence enables group-aware cross-validation (e.g., inner CV folds on training data) and post-hoc error categorization.
2. **Strictly Excluded from Feature Vectors**:
   - As mandated by [AGENTS.md](file:///D:/PHISH/AGENTS.md) and [docs/feature_schema.md](file:///D:/PHISH/docs/feature_schema.md), `Domain` is **never passed as an input feature** to the Decision Tree or ANN.
   - Predictive models consume only the 9 numeric URL features extracted by `src.features.extract.extract_features()`.

---

## 7. Artifact Specifications & Quality Controls

### 7.1 Generated Files
- `data/processed/train.csv` (22.2 MB, 188,296 rows, gitignored)
- `data/processed/test.csv` (5.57 MB, 47,074 rows, gitignored)

### 7.2 Atomic File Generation
The `split_dataset()` function in [src/data/split.py](file:///D:/PHISH/src/data/split.py) stages writes in hidden temporary files (`.train.csv.<uuid>.tmp`) before executing atomic replacement (`os.replace`). In the event of a disk error or process termination, existing files are never left in a corrupted or partial state.

### 7.3 Holdout Test Set Sealing Protocol
- The test partition (`data/processed/test.csv`) is **formally sealed**.
- Hyperparameter tuning, tree depth selection, learning rate optimization, and scaler fitting across Phases 6 through 9 must utilize **only the training partition** (`data/processed/train.csv`) via inner cross-validation or validation splits.
- The sealed test set is evaluated strictly in **Phase 10 (Rigorous Model Comparison)** for headline performance reporting.
