# PhishGuard — Exploratory Data Analysis (EDA)

## 1. Objective

This document records the exploratory analysis of the PhiUSIIL Phishing URL Dataset used in PhishGuard.

The objectives are to:

* Understand the dataset structure and target distribution.
* Examine missing values, duplicate records, and repeated URLs/domains.
* Understand numerical and categorical feature distributions.
* Identify unusual values and potentially important feature-target relationships.
* Record feature provenance concerns relevant to leakage prevention.
* Establish findings that will guide subsequent data-quality and feature-engineering phases.

This analysis does not modify the original raw dataset or make final feature-selection decisions.

## 2. Dataset Overview

| Property             | Observed Value                  |
| -------------------- | ------------------------------- |
| Dataset              | PhiUSIIL Phishing URL Dataset   |
| Source               | UCI Machine Learning Repository |
| Records              | 235,795                         |
| Total CSV columns    | 56                              |
| Target column        | `label`                         |
| Missing values       | 0                               |
| Exact duplicate rows | 0                               |
| Raw dataset status   | Checksum verified               |

The local CSV contains 56 columns. This count represents the complete CSV schema, including identifiers and the target, and should not be confused with UCI's documented count of 54 features.

## 3. Target Distribution

The target mapping is:

* `1` = Legitimate
* `0` = Phishing

| Class          | Records | Percentage |
| -------------- | ------: | ---------: |
| Legitimate (1) | 134,850 |     57.19% |
| Phishing (0)   | 100,945 |     42.81% |
| Total          | 235,795 |       100% |

### Observation

The dataset contains both classes in substantial quantities. The class distribution is not perfectly balanced.

Future model evaluation should therefore consider class-sensitive metrics in addition to accuracy.

## 4. Data Quality Findings

| Check                 | Result  |
| --------------------- | ------- |
| Missing values        | 0       |
| Exact duplicate rows  | 0       |
| Duplicate URL rows    | 425     |
| Unique URLs           | 235,370 |
| Duplicate domain rows | 15,709  |
| Unique domains        | 220,086 |

### Repeated URL label consistency

* Repeated URLs: 425
* Repeated URLs with one consistent label: 425
* Repeated URLs with conflicting labels: 0

### Repeated domain label consistency

* Repeated domains: 5,526
* Repeated domains with one label: 5,472
* Repeated domains with conflicting labels: 54

### Interpretation

Repeated URLs and domains require consideration during data splitting and leakage analysis.

The presence of conflicting labels for some domains indicates that a domain alone cannot be assumed to determine the label of every URL associated with it.

No records have been removed based on these observations.

## 5. Feature Source Inventory

The initial feature-source inventory identified:

| Category               | Count |
| ---------------------- | ----: |
| URL-related fields     |    24 |
| Webpage-related fields |    27 |
| Metadata               |     1 |
| Target                 |     1 |

### Metadata

`FILENAME` is treated as an identifier and is not intended to be a predictive feature.

### URL-related fields

The initial inventory includes fields such as:

* `URLLength`
* `Domain`
* `DomainLength`
* `IsDomainIP`
* `TLD`
* `TLDLength`
* `NoOfSubDomain`
* `IsHTTPS`
* `NoOfLettersInURL`
* `NoOfDegitsInURL`
* `NoOfEqualsInURL`
* `NoOfQMarkInURL`
* `NoOfAmpersandInURL`

Some derived URL-related fields require additional provenance investigation before being approved for production inference.

### Webpage-related fields

Examples include:

* `LineOfCode`
* `HasTitle`
* `HasFavicon`
* `Robots`
* `IsResponsive`
* `NoOfImage`
* `NoOfCSS`
* `NoOfJS`
* `NoOfSelfRef`
* `NoOfExternalRef`

These fields are not assumed to be available from a submitted URL alone.

## 6. Numerical Feature Analysis

Descriptive statistics were calculated for numerical columns.

Notable observations include:

* `URLLength` has a mean of approximately 34.57 and a maximum of 6,097.
* `DomainLength` has a mean of approximately 21.47 and a maximum of 110.
* `URLSimilarityIndex` has a mean of approximately 78.43.
* `LineOfCode` has a mean of approximately 1,141.90 and a maximum of 442,666.
* `LargestLineLength` has a maximum of 13,975,730.
* Several count-based features have highly dispersed distributions.

These observations indicate that some numerical features have long upper tails and substantially different scales.

No outliers have been removed or transformed during this EDA stage.

## 7. Feature Cardinality

The numerical cardinality analysis identified:

* Multiple binary features with two unique values.
* Count-based features with relatively low or moderate cardinality.
* Continuous or high-cardinality features such as `URLCharProb`, `URLSimilarityIndex`, and `LargestLineLength`.

Cardinality alone is not being used to determine whether a feature should be retained.

## 8. Class-Wise Observations

The class-wise mean analysis shows differences between legitimate and phishing records.

Examples:

| Feature         | Phishing (0) Mean | Legitimate (1) Mean |
| --------------- | ----------------: | ------------------: |
| URLLength       |             45.72 |               26.23 |
| DomainLength    |             24.47 |               19.23 |
| IsHTTPS         |             0.492 |               1.000 |
| HasTitle        |             0.678 |               0.999 |
| HasDescription  |             0.044 |               0.737 |
| NoOfImage       |             0.866 |              44.947 |
| NoOfExternalRef |             1.128 |              85.295 |

These are descriptive differences, not causal explanations or guarantees of predictive performance.

## 9. Extreme Value Analysis

An IQR-based upper-bound analysis was performed for numerical features with more than ten unique values.

Examples of observed extreme-value counts:

| Feature           | Extreme Values |
| ----------------- | -------------: |
| URLLength         |         22,493 |
| DomainLength      |         13,474 |
| NoOfDegitsInURL   |         51,461 |
| LineOfCode        |         19,280 |
| LargestLineLength |         17,503 |
| NoOfiFrame        |         34,441 |
| NoOfEmptyRef      |         38,885 |
| NoOfExternalRef   |         22,780 |

The IQR method identifies statistical extremes; it does not establish that a record is invalid.

No automatic outlier removal is authorized by these findings.

## 10. Categorical Feature Observations

Observed unique-value counts include:

| Field    | Unique Values |
| -------- | ------------: |
| FILENAME |       235,795 |
| URL      |       235,370 |
| Domain   |       220,086 |
| TLD      |           695 |
| Title    |       197,874 |

The `Title` field includes values such as `0` and `#NAME?`.

These values require interpretation during data-quality analysis rather than automatic replacement.

## 11. Feature-Target Correlation

The numerical correlation analysis produced the following strongest relationships with `label`:

| Feature               | Correlation |
| --------------------- | ----------: |
| URLSimilarityIndex    |   +0.860358 |
| HasSocialNet          |   +0.784255 |
| HasCopyrightInfo      |   +0.743358 |
| HasDescription        |   +0.690232 |
| IsHTTPS               |   +0.609132 |
| DomainTitleMatchScore |   +0.584905 |
| HasSubmitButton       |   +0.578561 |
| IsResponsive          |   +0.548608 |
| URLTitleMatchScore    |   +0.539419 |

### Interpretation

High correlation indicates a strong statistical relationship with the target.

It does not independently establish:

* Data leakage.
* Causal relevance.
* Production availability.
* Generalization to unseen domains.
* Whether a feature can be reproduced from a URL alone.

These questions require separate investigation.

## 12. Feature Provenance and Leakage Concerns

The UCI documentation states that dataset features are extracted from URLs and webpage source code.

It also identifies the following as derived features:

* `CharContinuationRate`
* `URLTitleMatchScore`
* `URLCharProb`
* `TLDLegitimateProb`

The exact construction of these features has not yet been independently reproduced.

`URLSimilarityIndex` also requires further investigation because its construction and production-time availability have not been established by the current analysis.

### Current decision

These fields are classified as **provenance-sensitive**, not automatically rejected.

The raw dataset remains unchanged.

The production feature schema will only include features whose generation can be justified under the project's static URL-analysis requirement.

## 13. EDA Limitations

This analysis is based on the available dataset and observed statistical properties.

It does not yet establish:

* Whether all features are safe for production inference.
* Whether domain-level leakage affects random splitting.
* Whether duplicate URLs should be grouped during splitting.
* Whether extreme values are erroneous.
* Which features should be selected for final model training.

These matters remain for subsequent phases.

## 14. Conclusion

The initial EDA confirms that the dataset is structurally complete, contains no missing values or exact duplicate rows, and has a moderately imbalanced target distribution.

Repeated URLs and domains, conflicting domain labels, extreme numerical values, and strong feature-target correlations have been identified as areas requiring further analysis.

Feature provenance is a central architectural consideration because PhishGuard is intended to perform static URL analysis without visiting submitted URLs.

The findings will guide the next phase: data quality assessment and leakage control.

---

**Status:** EDA findings recorded; final feature selection and model training have not yet begun.
