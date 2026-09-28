# Dataset Provenance: UCI PhiUSIIL Phishing URL Dataset

## 1. Overview & Provenance

| Property | Value |
|---|---|
| **Dataset Name** | PhiUSIIL Phishing URL (Website) Dataset |
| **Repository** | UCI Machine Learning Repository |
| **UCI Dataset ID** | 967 |
| **Landing Page** | [UCI Repository Record](https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset) |
| **Direct Archive URL** | `https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip` |
| **DOI** | `10.24432/C56540` |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Donation Date** | 2024 |
| **Acquisition Date** | 2026-09-25 |
| **Raw File Path** | `data/raw/PhiUSIIL_Phishing_URL_Dataset.csv` |
| **Raw File Size** | 56,854,345 bytes (54.22 MB) |
| **SHA-256 Checksum** | `a236549cd369cd80bd478ff8e1779cbf44c58d5c3f79f7a51a1adbed7d06d1c6` |
| **MD5 Checksum** | `769ba530b3629c4c2f9896abf642aefa` |

---

## 2. Dataset Dimensions & Class Distribution

- **Total Instances (Rows)**: 235,795
- **Total Columns**: 56 (1 identifier, 1 raw URL string, 53 pre-extracted feature attributes, 1 binary target)
- **Missing / Null Values**: Exactly 0 across all 235,795 rows and 56 columns.
- **Target Column**: `label`

### Class Breakdown
| Class | Numerical Value | Instance Count | Percentage |
|---|---|---|---|
| **Legitimate** | `1` | 134,850 | 57.19% |
| **Phishing** | `0` | 100,945 | 42.81% |
| **Total** | — | **235,795** | **100.00%** |

---

## 3. Column Inventory & Data Dictionary

The 56 columns in the raw dataset are categorized by their nature:

### A. Non-Predictive Identifiers & Raw Text (To Be Excluded from Features)
1. `FILENAME`: Dataset internal file identifier (starts with UTF-8 BOM in source). **Leakage risk / Training identifier** — must not be used as a predictive feature.
2. `URL`: Raw, unparsed URL string. Serves as raw text for static feature extraction; not directly input to numeric ML models.

### B. URL Lexical & Syntactic Features (Derivable from URL string)
3. `URLLength`: Total character length of the URL.
4. `Domain`: Registered domain name / hostname.
5. `DomainLength`: Character count of the domain name.
6. `IsDomainIP`: Binary flag (1 if domain is a raw IPv4/IPv6 address, 0 otherwise).
7. `TLD`: Top-level domain string (e.g., `com`, `org`, `xyz`).
8. `URLSimilarityIndex`: Statistical similarity metric of URL tokens.
9. `CharContinuationRate`: Rate of consecutive characters belonging to the same character set.
10. `TLDLegitimateProb`: Historical probability of legitimate usage for the observed TLD.
11. `URLCharProb`: Character distribution probability across the URL.
12. `TLDLength`: Character length of the TLD.
13. `NoOfSubDomain`: Count of subdomains preceding the root domain.
14. `HasObfuscation`: Binary flag indicating presence of hexadecimal/URL encoding.
15. `NoOfObfuscatedChar`: Count of obfuscated characters.
16. `ObfuscationRatio`: Ratio of obfuscated characters to total URL length.
17. `NoOfLettersInURL`: Count of alphabetic characters `[a-zA-Z]`.
18. `LetterRatioInURL`: Ratio of alphabetic characters to URL length.
19. `NoOfDegitsInURL`: Count of numeric digits `[0-9]`.
20. `DegitRatioInURL`: Ratio of numeric digits to URL length.
21. `NoOfEqualsInURL`: Count of `=` characters.
22. `NoOfQMarkInURL`: Count of `?` characters.
23. `NoOfAmpersandInURL`: Count of `&` characters.
24. `NoOfOtherSpecialCharsInURL`: Count of non-alphanumeric, non-delimiter special characters.
25. `SpacialCharRatioInURL`: Ratio of special characters to URL length.
26. `IsHTTPS`: Binary flag (1 if scheme is `https`, 0 if `http`).

### C. Webpage & Content-Derived Attributes (Dataset-Provided; Offline Only)
*Note: Under PhishGuard's static analysis architecture, the production inference pipeline never visits web properties. These features exist in the raw training dataset but will be analyzed during Phase 2 (EDA) and Phase 3 (Leakage Controls).*

27. `LineOfCode`: Total lines of HTML code.
28. `LargestLineLength`: Length of the longest line in the HTML document.
29. `HasTitle`: Binary indicator if an HTML `<title>` tag exists.
30. `Title`: Text content of the page title.
31. `DomainTitleMatchScore`: Similarity score between domain name and title.
32. `URLTitleMatchScore`: Similarity score between full URL and title.
33. `HasFavicon`: Binary indicator for favicon presence.
34. `Robots`: Indicator for `robots.txt` configuration.
35. `IsResponsive`: Mobile responsiveness indicator.
36. `NoOfURLRedirect`: Count of HTTP redirection hops.
37. `NoOfSelfRedirect`: Count of redirections to the same domain.
38. `HasDescription`: Presence of `<meta name="description">`.
39. `NoOfPopup`: Count of Javascript popup calls (`window.open`).
40. `NoOfiFrame`: Count of `<iframe>` tags.
41. `HasExternalFormSubmit`: Binary indicator for forms submitting to third-party domains.
42. `HasSocialNet`: Links to social media networks.
43. `HasSubmitButton`: Presence of submit inputs/buttons.
44. `HasHiddenFields`: Presence of `<input type="hidden">`.
45. `HasPasswordField`: Presence of `<input type="password">`.
46. `Bank`: Frequency or presence of banking-related keywords.
47. `Pay`: Frequency or presence of payment-related keywords.
48. `Crypto`: Frequency or presence of cryptocurrency-related keywords.
49. `HasCopyrightInfo`: Presence of copyright notices in HTML.
50. `NoOfImage`: Count of `<img>` tags.
51. `NoOfCSS`: Count of external CSS stylesheets.
52. `NoOfJS`: Count of external/inline Javascript scripts.
53. `NoOfSelfRef`: Count of hyperlinks pointing to the source domain.
54. `NoOfEmptyRef`: Count of null/empty hyperlinks (`href="#"`).
55. `NoOfExternalRef`: Count of hyperlinks pointing to external domains.

### D. Ground Truth Target
56. `label`: Binary classification ground truth.
    - `1`: **Legitimate**
    - `0`: **Phishing**

---

## 4. Immutability & Safety Policy

1. **Strict Immutability**: The raw CSV file in `data/raw/` must never be altered, renamed, reformatted, or normalized in place.
2. **Deterministic Validation**: Any machine learning code using this dataset must run `src.data.validate.validate_raw_dataset()` to guarantee integrity before generating interim or processed data slices.
3. **No Target URL Traversal**: Neither the training pipeline, validator, nor inference service will ever crawl, ping, resolve, or visit any URL string from this dataset.
