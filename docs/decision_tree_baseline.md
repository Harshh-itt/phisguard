# PhishGuard — Decision Tree Baseline Model Specification & Empirical Report

## 1. Executive Summary & Purpose

Phase 6 implements the **Decision Tree Baseline Model** (`sklearn.tree.DecisionTreeClassifier`), the first of PhishGuard's exactly two headline predictive algorithms mandated by [AGENTS.md](file:///D:/PHISH/AGENTS.md). 

This baseline establishes the benchmark against which subsequent tuned decision trees (Phase 7) and artificial neural networks (Phases 8 & 9) are evaluated.

### Core Operating Invariants Adhered To
1. **Defensive Static Analysis Only**: Features are extracted strictly using [`src.features.extract.extract_features()`](file:///D:/PHISH/src/features/extract.py) without network, DNS, or DOM dependencies.
2. **Approved Feature Schema**: Relies solely on the 9 canonical features defined in schema v1.0.0 ([`src/features/schema.py`](file:///D:/PHISH/src/features/schema.py)).
3. **Data Boundary Enforcement**: Trained **strictly on `data/processed/train.csv`** (188,296 records).
4. **Sealed Holdout Partition**: The test partition (`data/processed/test.csv`) remains completely untouched and sealed until Phase 10 model comparison.
5. **No Invented Metrics**: All reported metrics are empirically measured from 5-fold domain-grouped cross-validation on the training set and persisted in machine-readable metadata.

---

## 2. Model Architecture & Hyperparameters

The baseline classifier uses scikit-learn's default parameters without pruning or tree depth constraints:

```python
DecisionTreeClassifier(
    criterion="gini",
    splitter="best",
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
)
```

### Empirical Model Complexity
- **Fitted Max Depth**: `22`
- **Total Tree Nodes**: `805`
- **Training Records**: `188,296`
- **Distinct Domains in Training Set**: `176,072`
- **Training & CV Execution Time**: `34.59s`

---

## 3. Gini Feature Importances

The Gini feature importances measured on the fitted baseline model:

| Feature Name | Gini Importance | Share of Importance | Role in Decision Tree |
|---|---:|---:|---|
| `is_https` | **`0.5111`** | **`51.1%`** | Primary root discriminator (benign URLs predominantly HTTPS) |
| `path_length` | **`0.4647`** | **`46.5%`** | Secondary discriminator (phishing URLs exhibit long, nested paths) |
| `url_length` | `0.0114` | `1.1%` | Tertiary branch refinement |
| `dot_count` | `0.0072` | `0.7%` | Subdomain depth segmentation |
| `digit_count` | `0.0033` | `0.3%` | Numeric tokens in URL |
| `hyphen_count` | `0.0012` | `0.1%` | Brand spoofing punctuation |
| `hostname_length` | `0.0011` | `0.1%` | FQDN length checks |
| `is_ip_address` | `0.0000` | `0.0%` | Low frequency in training subset |
| `query_length` | `0.0000` | `0.0%` | Subsumed by path length / url length |

**Key Insight**: Two features (`is_https` and `path_length`) drive **97.6%** of the decision tree's splitting decisions. This highlights both the efficiency of static URL analysis and the potential vulnerability of over-relying on transport security (e.g., adversary adopting free TLS certificates).

---

## 4. Empirical Evaluation Results

### 4.1 Out-of-Fold Domain-Grouped Cross-Validation (5-Fold StratifiedGroupKFold)
This evaluation partitions the 188,296 training records into 5 folds grouped strictly by domain (`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`). In each fold, the model is tested on domains it has never seen, evaluating zero-day generalization:

| Metric | Overall | Phishing (`label == 0`) | Legitimate (`label == 1`) |
|---|---:|---:|---:|
| **Precision** | `0.9953` (Macro) | `0.9985` | `0.9930` |
| **Recall** | `0.9953` (Macro) | `0.9905` | `0.9989` |
| **F1-Score** | **`0.9952`** (Macro) | **`0.9945`** | **`0.9959`** |
| **Support** | `188,296` | `80,416` | `107,880` |
| **Overall Accuracy** | **`0.9953`** | — | — |
| **Weighted F1** | **`0.9953`** | — | — |

#### Domain-Grouped Confusion Matrix (Out-of-Fold)
$$\begin{pmatrix} 
\text{True Phishing: } 79,652 & \text{False Legitimate (FP): } 764 \\ 
\text{False Phishing (FN): } 121 & \text{True Legitimate: } 107,759 
\end{pmatrix}$$

- **False Negative Rate on Phishing**: $\frac{764}{80,416} \approx 0.95\%$ (phishing URLs passing undetected).
- **False Positive Rate on Legitimate**: $\frac{121}{107,880} \approx 0.11\%$ (benign URLs falsely flagged as phishing).

---

### 4.2 Training Fit & Overfitting Analysis

Evaluating the unpruned tree on its own training set:

| Metric | Training Fit | Out-of-Fold Cross-Validation | Generalization Gap ($\Delta$) |
|---|---:|---:|---:|
| **Accuracy** | `0.9960` | `0.9953` | **`+0.0007`** (0.07%) |
| **Macro F1** | `0.9959` | `0.9952` | **`+0.0007`** (0.07%) |
| **Phishing F1** | `0.9953` | `0.9945` | **`+0.0008`** (0.08%) |
| **Legitimate F1** | `0.9965` | `0.9959` | **`+0.0006`** (0.06%) |

#### Overfitting Diagnosis
1. **Minimal Overfitting Gap**: The generalization gap between full training fit and domain-disjoint cross-validation is exceptionally small ($< 0.1\%$). This indicates that the 9 static features generalize robustly across unencountered domains.
2. **Imperfection at Depth 22**: Even with an unpruned tree depth of 22 and 805 nodes, the model achieves 99.60% (not 100.0%) training accuracy. This occurs because certain distinct URLs from differing classes share identical 9-feature representations (feature collisions).
3. **Pruning Opportunity for Phase 7**: The depth of 22 and 805 nodes suggests redundant splits on tiny sample subsets. In Phase 7 (Decision Tree Tuning), hyperparameter tuning (`max_depth`, `min_samples_split`, `ccp_alpha`) will target tree simplification and interpretability without sacrificing recall.

---

## 5. Artifacts and Lineage

The trained model and accompanying audit metadata are persisted under version control exclusion:

- **Model Binary**: `artifacts/models/decision_tree_baseline.joblib` (116 KB)
- **Metadata**: `artifacts/metadata/decision_tree_baseline_metadata.json` (contains training timestamp, schema version, hyperparameters, feature importances, train metrics, and CV metrics).
- **Reload Verification**: Verified with automated unit test `test_save_and_load_decision_tree_artifacts` confirming prediction parity.
