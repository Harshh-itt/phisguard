# Feature Compatibility Investigation

## 1. Purpose

This document records the investigation of compatibility between PhishGuard's custom static URL feature extractor and the corresponding fields in the PhiUSIIL phishing URL dataset.

The objective is to understand which features can be independently reproduced from a submitted URL, identify discrepancies, and document unresolved compatibility issues before model training.

This investigation does not establish final feature selection or model performance.

## 2. Dataset Reference

| Property | Value |
|---|---|
| Dataset | PhiUSIIL Phishing URL Dataset |
| Source | UCI Machine Learning Repository |
| Dataset rows | 235,795 |
| Dataset columns | 56 |
| Target column | `label` |
| Legitimate label | 1 |
| Phishing label | 0 |
| Custom feature schema version | 1.0.0 |

## 3. Current Custom Feature Schema

PhishGuard currently extracts nine static URL features.

| Feature | Description |
|---|---|
| `url_length` | Length of the trimmed submitted URL |
| `hostname_length` | Length of the parsed hostname |
| `is_https` | 1 when the parsed scheme is HTTPS, otherwise 0 |
| `is_ip_address` | 1 when the parsed hostname is recognized as an IP address |
| `digit_count` | Number of digit characters in the URL |
| `dot_count` | Number of dots in the parsed hostname |
| `hyphen_count` | Number of hyphens in the parsed hostname |
| `path_length` | Length of the parsed URL path |
| `query_length` | Length of the parsed URL query |

The feature order is defined centrally by the versioned feature schema. Training and inference must use the same order and extraction implementation.

## 4. Dataset Compatibility Investigation

### 4.1 URL Length

The dataset's `URLLength` field does not consistently equal Python's `len(URL)`.

Full-dataset comparison:

| Difference: `len(URL) - URLLength` | Rows |
|---|---:|
| 0 | 48,644 |
| 1 | 187,149 |
| 4 | 1 |
| 35 | 1 |
| Total | 235,795 |

Two URLs contain non-ASCII characters and account for the exceptional differences of 4 and 35.

The precise dataset-side URL length calculation has not been established.

**Decision:** PhishGuard retains its documented definition, `len(url.strip())`, rather than introducing an unexplained adjustment such as subtracting one character.

Compatibility remains unresolved and must be considered during model development.

### 4.2 Hostname Length

The custom `hostname_length` is derived from the parsed hostname.

Full-dataset comparison against `DomainLength`:

| Result | Count |
|---|---:|
| Matching rows | 235,759 |
| Mismatching rows | 36 |
| Total | 235,795 |
| Match rate | 99.9847% |

Some differences involve authority strings containing user information or port information.

The custom extractor uses the hostname parsed from the URL authority rather than treating the entire authority string as the hostname.

**Decision:** Retain standards-based hostname parsing. Do not alter the extractor solely to reproduce unexplained dataset values.

### 4.3 HTTPS Detection

The custom `is_https` feature is determined from the parsed URL scheme.

Comparison against the dataset's `IsHTTPS` field:

| Result | Count |
|---|---:|
| Matching rows | 235,302 |
| Mismatching rows | 493 |
| Total | 235,795 |
| Match rate | 99.7910% |

The inspected mismatches include URLs whose outer scheme is HTTP but whose query parameters contain an embedded `https://` string.

**Decision:** Use the actual parsed scheme for custom inference. Do not infer HTTPS from arbitrary text elsewhere in the URL.

### 4.4 IP Address Detection

The custom `is_ip_address` feature identifies whether the parsed hostname is a valid IP address.

Comparison against `IsDomainIP`:

| Result | Count |
|---|---:|
| Matching rows | 235,765 |
| Mismatching rows | 30 |
| Total | 235,795 |
| Match rate | 99.9873% |

Inspected mismatches include hostnames with IP-like numeric components in their subdomains.

The dataset's exact IP detection rule has not been established.

**Decision:** Retain explicit IP parsing rather than classifying a hostname as an IP address merely because it contains numeric components.

## 5. Important Interpretation

The compatibility measurements describe agreement with dataset fields. They do not prove that either implementation is universally correct.

The custom extractor is intended to operate on a URL supplied at inference time. It must not depend on the original dataset row, hidden webpage content, or unavailable metadata.

The following principles apply:

- Use the same feature extraction code during training and inference.
- Preserve a fixed feature order and schema version.
- Do not silently introduce dataset-specific corrections.
- Investigate discrepancies before making compatibility claims.
- Keep URL processing static; do not visit submitted URLs.
- Document unresolved assumptions rather than presenting them as verified facts.

## 6. Current Status

| Area | Status |
|---|---|
| Custom nine-feature schema | Implemented |
| Feature schema validation | Implemented |
| Static URL parsing | Implemented |
| URL length compatibility | Unresolved |
| Hostname length compatibility | High agreement; discrepancies documented |
| HTTPS compatibility | High agreement; discrepancies documented |
| IP detection compatibility | High agreement; discrepancies documented |
| Final model feature selection | Pending |
| Training/inference parity verification | Pending |
| Model training | Not started |

## 7. Next Investigation Steps

Before model training:

1. Review the provenance and definitions of candidate dataset features.
2. Identify features that can be reproduced from a submitted URL alone.
3. Investigate potential target leakage and dataset-specific dependencies.
4. Establish a documented final feature set.
5. Verify that the training and inference pipelines produce identical feature vectors for the same URL.
6. Record the final decisions and update this document as evidence becomes available.

---

**Document status:** Initial compatibility investigation  
**Feature schema version:** 1.0.0  
**Model training status:** Pending
