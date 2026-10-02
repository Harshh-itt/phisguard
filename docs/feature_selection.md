# PhishGuard — Feature Selection Specification

## 1. Executive Summary & Purpose

Feature selection is the critical bridge between data exploration and model training. In PhishGuard, feature selection is governed by two uncompromising architectural invariants:
1. **Defensive Static URL Analysis Only**: Every feature must be statically computable from an untrusted URL string without network calls, DNS queries, or webpage rendering.
2. **Deterministic Parity Between Training and Inference**: Training pipelines and serving APIs must execute the exact same extraction functions on raw URL strings.

This document records the evaluation of the existing **nine-feature schema (v1.0.0)**, catalogs proposed candidate additions based on our empirical provenance audit, formally records excluded categories, and establishes clear boundaries between the **currently approved production schema** and **future proposed enhancements**.

---

## 2. Evaluation of the Current Nine-Feature Schema (Version 1.0.0)

The current schema defined in [src/features/schema.py](file:///D:/PHISH/src/features/schema.py) and extracted via [src/features/extract.py](file:///D:/PHISH/src/features/extract.py) contains nine features in canonical order:

```
FEATURE_NAMES = (
    "url_length",
    "hostname_length",
    "is_https",
    "is_ip_address",
    "digit_count",
    "dot_count",
    "hyphen_count",
    "path_length",
    "query_length",
)
```

### 2.1 Individual Feature Assessment

| Feature Name | Static Extraction Formula | Data Type | Value Range | Empirical Signal in Dataset | Provenance Status |
|---|---|---|---|---|---|
| `url_length` | `len(url.strip())` | Integer | $[0, \infty)$ | Mean legitimate: 26.23 chars; Mean phishing: 45.72 chars. Phishing URLs tend to be longer. | **Retained**. Discrepancy with raw dataset (+1 char in 79% of rows) is documented; standard Python length retained. |
| `hostname_length` | `len(parsed.hostname)` | Integer | $[0, 253]$ | Mean legitimate: 19.23 chars; Mean phishing: 24.47 chars. | **Verified**. 99.98% agreement with dataset `DomainLength`. |
| `is_https` | `int(scheme == "https")` | Integer | $\{0, 1\}$ | In raw dataset, 100% of legitimate URLs were HTTPS vs. 49.2% of phishing URLs. | **Verified**. 99.79% agreement with dataset `IsHTTPS`. Essential transport security indicator. |
| `is_ip_address` | `int(is_ip(hostname))` | Integer | $\{0, 1\}$ | Raw IP hostnames are rarely used by legitimate public brands and often indicate compromised infrastructure. | **Verified**. 99.99% agreement with dataset `IsDomainIP`. |
| `digit_count` | `sum(c.isdigit() for c in url)` | Integer | $[0, \infty)$ | Phishing URLs frequently contain numeric tokens, hex strings, timestamps, or IP octets in path/query. | **Verified**. 99.49% agreement with dataset `NoOfDegitsInURL`. |
| `dot_count` | `hostname.count(".")` | Integer | $[0, \infty)$ | Measures domain segmentation and subdomain depth. Excessive dots often indicate subdomain abuse or spoofing. | **Verified**. Formally scoped to parsed hostname. |
| `hyphen_count` | `hostname.count("-")` | Integer | $[0, \infty)$ | Hyphens in hostnames are heavily employed in brand impersonation (e.g., `paypal-security-update.com`). | **Verified**. Formally scoped to parsed hostname. |
| `path_length` | `len(parsed.path)` | Integer | $[0, \infty)$ | Phishing URLs frequently exhibit deep nested directories mimicking legitimate authentication hierarchies. | **Verified**. Deterministic RFC 3986 component. |
| `query_length` | `len(parsed.query)` | Integer | $[0, \infty)$ | Phishing attacks commonly pass victim emails, session tokens, or redirection targets in query parameters. | **Verified**. Deterministic RFC 3986 component. |

### 2.2 Operational Strengths of Schema v1.0.0
1. **Zero External Dependencies**: Operates entirely with Python standard library modules (`urllib.parse`, `ipaddress`).
2. **Sub-Millisecond Latency**: Static string analysis executes in microseconds per URL, ideal for high-throughput API serving.
3. **Robust Input Validation**: Coupled with `validate_features()`, rejects negative values, invalid types, and malformed inputs with clean exceptions.
4. **Safety Compliance**: 100% compliant with Rules 1, 2, 3, and 4 in [AGENTS.md](file:///D:/PHISH/AGENTS.md).

---

## 3. Candidate Expansion Features (Empirical Audit Findings)

Based on the 56-column provenance audit ([docs/feature_provenance_audit.md](file:///D:/PHISH/docs/feature_provenance_audit.md)), four additional lexical features have verified formulas and high agreement with the raw dataset:

| Proposed Candidate | Static Formula | Match Rate vs Raw Dataset | Analytical Value |
|---|---|---:|---|
| `equal_sign_count` | `url.count("=")` | 99.89% | Measures query parameter count and key-value pair density. |
| `question_mark_count` | `url.count("?")` | 99.99% | Flags presence and repetition of query string delimiters. |
| `ampersand_count` | `url.count("&")` | 98.65% | Measures compound query parameters (often used in credential passing). |
| `tld_length` | `len(tld_str)` | 100.00% | Captures abnormal or long new generic TLDs (e.g., `.technology`, `.support`). |

### 3.1 Excluded Candidates (Failed Audit Criteria)
1. **`letter_count` (`NoOfLettersInURL`)**:
   - **Empirical Status**: 0.00% match rate with `sum(c.isalpha() for c in url)`.
   - **Reason**: The dataset authors inconsistently stripped protocol prefixes (`https`, `http`, `www`), producing arbitrary offsets of 4, 5, 8, or 9 characters. Introducing a naive `sum(c.isalpha())` would introduce a severe distribution mismatch against the raw dataset column.
2. **`subdomain_count` (`NoOfSubDomain`)**:
   - **Status**: Requires external public-suffix database (e.g. `tldextract`) to correctly identify multi-part TLDs (such as `.co.uk`, `.com.au`) before counting subdomain labels. Remains pending until public-suffix handling is approved.
3. **`special_character_count` (`NoOfOtherSpecialCharsInURL`)**:
   - **Status**: The exact delimiter exclusion set used by the dataset authors is undocumented and cannot be independently verified.

---

## 4. Categorically Excluded Features

The following categories from the 56-column dataset are permanently disqualified:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Categorically Excluded Columns                       │
├────────────────────────────────┬───────────────────────────────────────┤
│ Webpage / DOM Features         │ Reason: SSRF vulnerability, malware   │
│ (27 Columns)                   │ risks, total failure on offline sites,│
│ LineOfCode, HasTitle, Robots,  │ violation of Static Analysis Invariant│
│ HasFavicon, NoOfImage, etc.    │ (Rules 1, 2, 3 in AGENTS.md)          │
├────────────────────────────────┼───────────────────────────────────────┤
│ Proprietary / Corpus Heuristics│ Reason: Requires unversioned external │
│ URLSimilarityIndex,            │ lookup tables, severe distribution-   │
│ TLDLegitimateProb, URLCharProb │ shift risk, artificial target leakage │
├────────────────────────────────┼───────────────────────────────────────┤
│ Metadata Identifiers           │ Reason: Internal dataset file index;  │
│ FILENAME                       │ non-predictive artifact               │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 5. Comparison: Approved Schema vs. Proposed Candidate Schema

To prevent unapproved code churn, the current formal contract is kept separate from future proposals:

| Dimension | Tier 1: Formally Approved Schema (Active) | Tier 2: Proposed Future Enhancement (Candidate) |
|---|---|---|
| **Schema Version** | `1.0.0` | `1.1.0` (Proposed) |
| **Status** | **ACTIVE & LOCKED** | **PROPOSED FOR USER REVIEW** |
| **Feature Count** | **9 features** | **13 features** |
| **Feature List** | 1. `url_length`<br>2. `hostname_length`<br>3. `is_https`<br>4. `is_ip_address`<br>5. `digit_count`<br>6. `dot_count`<br>7. `hyphen_count`<br>8. `path_length`<br>9. `query_length` | 1. `url_length`<br>2. `hostname_length`<br>3. `is_https`<br>4. `is_ip_address`<br>5. `digit_count`<br>6. `dot_count`<br>7. `hyphen_count`<br>8. `path_length`<br>9. `query_length`<br>*10. `equal_sign_count`*<br>*11. `question_mark_count`*<br>*12. `ampersand_count`*<br>*13. `tld_length`* |
| **Implementation** | Implemented in `src/features/` & verified with 41 unit tests | Purely documented; zero source code changes |
| **Model Readiness** | Ready for Phase 4 preprocessing | Awaiting user decision before any code change |

---

## 6. Unresolved Decisions & Recommendations for User Approval

1. **Retain 9-Feature Schema for Phase 4 Baseline**:
   - *Recommendation*: Use the existing, fully-tested 9-feature schema for initial Phase 4 preprocessing and Phase 6 Decision Tree baseline. This preserves simplicity, prevents scope creep, and establishes an interpretable benchmark.
2. **Consider 13-Feature Schema for Future Iteration**:
   - *Recommendation*: If the 9-feature baseline leaves performance headroom, evaluate the 4 proposed candidate features (`equal_sign_count`, `question_mark_count`, `ampersand_count`, `tld_length`) under a formal version bump (`1.1.0`) with updated tests.
3. **Schema Immutability Confirmation**:
   - *Confirmation*: No code in `src/features/schema.py` or `src/features/extract.py` has been modified. The approved 9-feature contract remains active.
