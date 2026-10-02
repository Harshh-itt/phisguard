# PhishGuard — Feature Provenance Audit

## 1. Executive Summary & Purpose

Under the core architectural constraints of **PhishGuard** ([AGENTS.md](file:///D:/PHISH/AGENTS.md)), the system must operate strictly as a **defensive, static URL classification system**. All URL features at inference time must be computed deterministically and statically from the submitted URL string without making network requests, crawling web properties, or inspecting webpage content.

This document records an exhaustive audit of all **56 columns** in the raw UCI PhiUSIIL Phishing URL Dataset (`data/raw/PhiUSIIL_Phishing_URL_Dataset.csv`). The objective is to establish:
1. Which features are verifiable, deterministically reproducible from a URL string alone.
2. Which features suffer from unresolved provenance, unexplained calculation discrepancies, or reliance on external corpus lookup tables.
3. Which features are derived from webpage content and must be formally disqualified to satisfy SSRF security and static analysis invariants.

---

## 2. Comprehensive 56-Column Classification Matrix

| # | Column Name | Raw Type | Category | Static Inference Eligibility | Provenance & Reproducibility Assessment |
|---|---|---|---|---|---|
| 1 | `FILENAME` | String | Metadata | **Excluded** | Non-predictive file index (contains UTF-8 BOM). Target leakage risk. |
| 2 | `URL` | String | Raw Input | **Source Input** | Raw untrusted URL string. Source for static feature extraction; not directly input to tabular models. |
| 3 | `URLLength` | Integer | URL Lexical | **Candidate (Discrepant)** | Mismatches `len(url.strip())` by 1 character in 79.37% of rows. Standard Python length retained. |
| 4 | `Domain` | String | URL Lexical | **Raw Input / Group** | Parsed hostname / FQDN. Used for group-level evaluation; not a numeric model feature. |
| 5 | `DomainLength` | Integer | URL Lexical | **Verified** | Character length of parsed hostname. Matches `len(hostname)` in 99.98% of rows. |
| 6 | `IsDomainIP` | Integer | URL Lexical | **Verified** | Binary flag for IPv4/IPv6 hostname. Matches `ipaddress.ip_address` in 99.99% of rows. |
| 7 | `TLD` | String | URL Lexical | **Categorical / Pending** | Top-level domain string (695 unique values). High cardinality; requires verified public-suffix parsing. |
| 8 | `URLSimilarityIndex` | Float | Derived Heuristic | **Excluded** | Token similarity metric (+0.860 correlation with label). Requires proprietary reference dictionary; cannot be computed offline without corpus. |
| 9 | `CharContinuationRate` | Float | Derived Heuristic | **Unresolved** | Rate of consecutive characters of same type. Exact tokenizer and boundary handling are unverified. |
| 10 | `TLDLegitimateProb` | Float | Derived Heuristic | **Excluded** | Historical legitimate probability for TLD. Requires external lookup table; unavailable statically. |
| 11 | `URLCharProb` | Float | Derived Heuristic | **Excluded** | Character distribution probability. Requires precomputed frequency dictionary; unavailable statically. |
| 12 | `TLDLength` | Integer | URL Lexical | **Verified** | Length of TLD string. 100.00% match with `len(TLD)`. |
| 13 | `NoOfSubDomain` | Integer | URL Lexical | **Pending** | Count of subdomains (0–10). Requires public suffix list (e.g., distinguishing `.co.uk` from subdomains). |
| 14 | `HasObfuscation` | Integer | URL Lexical | **Pending** | Binary indicator for hex/percent encoding. Very low positive rate (0.21%). Definition needs standardization. |
| 15 | `NoOfObfuscatedChar` | Integer | URL Lexical | **Pending** | Count of obfuscated characters. Dependent on `HasObfuscation` definition. |
| 16 | `ObfuscationRatio` | Float | URL Lexical | **Pending** | Ratio of obfuscated characters to URL length. |
| 17 | `NoOfLettersInURL` | Integer | URL Lexical | **Discrepant / Unresolved** | Count of letters in URL. **0.00% match** with `sum(c.isalpha())`. Dataset script systematically stripped components (off by 5 to 9 in >89% of rows). |
| 18 | `LetterRatioInURL` | Float | URL Lexical | **Discrepant / Unresolved** | Ratio of letters to URL length. Computed from discrepant `NoOfLettersInURL`. |
| 19 | `NoOfDegitsInURL` | Integer | URL Lexical | **Verified** | Count of numeric digits `[0-9]`. Matches `sum(c.isdigit())` in 99.49% of rows. |
| 20 | `DegitRatioInURL` | Float | URL Lexical | **Candidate** | Ratio of numeric digits to URL length. |
| 21 | `NoOfEqualsInURL` | Integer | URL Lexical | **Verified** | Count of `=` characters. Matches `url.count("=")` in 99.89% of rows. |
| 22 | `NoOfQMarkInURL` | Integer | URL Lexical | **Verified** | Count of `?` characters. Matches `url.count("?")` in 99.99% of rows. |
| 23 | `NoOfAmpersandInURL` | Integer | URL Lexical | **Verified** | Count of `&` characters. Matches `url.count("&")` in 98.65% of rows (discrepancies involve HTML entity `&amp;`). |
| 24 | `NoOfOtherSpecialCharsInURL` | Integer | URL Lexical | **Unresolved** | Count of non-alphanumeric, non-delimiter characters. Exact delimiter exclusion set is not documented. |
| 25 | `SpacialCharRatioInURL` | Float | URL Lexical | **Unresolved** | Ratio of special characters to URL length. Dependent on `NoOfOtherSpecialCharsInURL`. |
| 26 | `IsHTTPS` | Integer | URL Lexical | **Verified** | 1 if scheme is HTTPS, 0 if HTTP. Matches `parsed.scheme == "https"` in 99.79% of rows. |
| 27 | `LineOfCode` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Total HTML lines. Requires server-side HTTP request and page download. |
| 28 | `LargestLineLength` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Maximum length of single line in HTML. Requires page download. |
| 29 | `HasTitle` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Binary indicator for `<title>` tag. Requires page download. |
| 30 | `Title` | String | Webpage / DOM | **Excluded (SSRF Hazard)** | Text content of HTML title. Requires page download. |
| 31 | `DomainTitleMatchScore` | Float | Webpage / DOM | **Excluded (SSRF Hazard)** | Similarity score between domain and title. Requires page download. |
| 32 | `URLTitleMatchScore` | Float | Webpage / DOM | **Excluded (SSRF Hazard)** | Similarity score between full URL and title. Requires page download. |
| 33 | `HasFavicon` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Presence of `<link rel="icon">`. Requires page download. |
| 34 | `Robots` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Indicator for `robots.txt`. Requires outbound HTTP GET request. |
| 35 | `IsResponsive` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Viewport/responsiveness indicator. Requires page rendering / DOM evaluation. |
| 36 | `NoOfURLRedirect` | Integer | Webpage / Network | **Excluded (SSRF Hazard)** | HTTP redirect hop count. Requires following network redirects. |
| 37 | `NoOfSelfRedirect` | Integer | Webpage / Network | **Excluded (SSRF Hazard)** | Self-referential HTTP redirect count. Requires following network redirects. |
| 38 | `HasDescription` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Presence of `<meta name="description">`. Requires page download. |
| 39 | `NoOfPopup` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Count of JavaScript `window.open` calls. Requires JS parsing. |
| 40 | `NoOfiFrame` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Count of `<iframe>` tags. Requires HTML parsing. |
| 41 | `HasExternalFormSubmit` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Forms submitting to third-party domains. Requires HTML form parsing. |
| 42 | `HasSocialNet` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Links to social networks. Requires page download. |
| 43 | `HasSubmitButton` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Presence of submit input/button. Requires page download. |
| 44 | `HasHiddenFields` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Presence of `<input type="hidden">`. Requires page download. |
| 45 | `HasPasswordField` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Presence of `<input type="password">`. Requires page download. |
| 46 | `Bank` | Integer | Webpage / Content | **Excluded (SSRF Hazard)** | Frequency/presence of banking keywords in body. Requires page download. |
| 47 | `Pay` | Integer | Webpage / Content | **Excluded (SSRF Hazard)** | Frequency/presence of payment keywords in body. Requires page download. |
| 48 | `Crypto` | Integer | Webpage / Content | **Excluded (SSRF Hazard)** | Frequency/presence of cryptocurrency keywords in body. Requires page download. |
| 49 | `HasCopyrightInfo` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Copyright notice presence in HTML. Requires page download. |
| 50 | `NoOfImage` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Count of `<img>` tags. Requires HTML parsing. |
| 51 | `NoOfCSS` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Count of stylesheet references. Requires HTML parsing. |
| 52 | `NoOfJS` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Count of script tags. Requires HTML parsing. |
| 53 | `NoOfSelfRef` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Internal hyperlinks count. Requires page download. |
| 54 | `NoOfEmptyRef` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Hyperlinks with `href="#"`. Requires page download. |
| 55 | `NoOfExternalRef` | Integer | Webpage / DOM | **Excluded (SSRF Hazard)** | Hyperlinks pointing to external domains. Requires page download. |
| 56 | `label` | Integer | Ground Truth Target | **Supervised Target** | Ground truth label: `1` = Legitimate (134,850), `0` = Phishing (100,945). |

---

## 3. In-Depth Empirical Audit by Feature Group

### 3.1 Group A: Non-Predictive Metadata (`FILENAME`)
- **Verified Definition**: Internal dataset storage filename (e.g., `521848.txt`).
- **Inspection Findings**: In the raw CSV source, this field is prefixed with a UTF-8 Byte Order Mark (`\ufeffFILENAME`). All 235,795 rows have unique values.
- **Provenance Verdict**: Non-predictive tracking identifier. It must be purged before preprocessing to eliminate target leakage.

### 3.2 Group B: Raw Input String (`URL`)
- **Verified Definition**: The raw, unparsed URL string as collected by the dataset authors.
- **Inspection Findings**: Contains 235,370 unique URLs (425 duplicate URLs occurring exactly twice).
- **Provenance Verdict**: Untrusted user input string. In PhishGuard's architecture, this serves solely as raw input for the static URL feature extractor.

### 3.3 Group C: Lexical URL Features with Verified Empirical Agreement
The following features were empirically tested against the entire 235,795 rows:

1. **`DomainLength`**:
   - Extractor logic: `len(parsed.hostname)`
   - Full dataset match rate: **99.9847%** (235,759 / 235,795 rows match exactly).
   - Mismatches: 36 rows where authority strings contained embedded port or user credentials.
   - Status: **Verified**. Standards-based parsing retained.

2. **`IsDomainIP`**:
   - Extractor logic: `ipaddress.ip_address(parsed.hostname)`
   - Full dataset match rate: **99.9873%** (235,765 / 235,795 rows match exactly).
   - Mismatches: 30 rows where the dataset labeled hostnames with numeric subdomains as IP addresses.
   - Status: **Verified**. Strict IP parsing retained.

3. **`IsHTTPS`**:
   - Extractor logic: `int(parsed.scheme.lower() == "https")`
   - Full dataset match rate: **99.7910%** (235,302 / 235,795 rows match exactly).
   - Mismatches: 493 rows where the outer scheme was HTTP, but an embedded `https://` appeared in query parameters.
   - Status: **Verified**. Outer transport scheme retained.

4. **`NoOfDegitsInURL`**:
   - Extractor logic: `sum(char.isdigit() for char in url)`
   - Full dataset match rate: **99.4864%** (234,584 / 235,795 rows match exactly).
   - Mismatches: 1,211 rows where dataset count was off by 1, mostly involving port numbers or trailing characters.
   - Status: **Verified**.

5. **`NoOfEqualsInURL`**:
   - Extractor logic: `url.count("=")`
   - Full dataset match rate: **99.8944%** (235,546 / 235,795 rows match exactly).
   - Status: **Verified**.

6. **`NoOfQMarkInURL`**:
   - Extractor logic: `url.count("?")`
   - Full dataset match rate: **99.9949%** (235,783 / 235,795 rows match exactly; only 12 mismatches).
   - Status: **Verified**.

7. **`NoOfAmpersandInURL`**:
   - Extractor logic: `url.count("&")`
   - Full dataset match rate: **98.6548%** (232,623 / 235,795 rows match exactly).
   - Mismatches: 3,172 rows where HTML entities (`&amp;`) or URL query encoding caused count differences.
   - Status: **Verified**.

8. **`TLDLength`**:
   - Extractor logic: `len(row["TLD"])`
   - Full dataset match rate: **100.0000%** (235,795 / 235,795 rows match exactly).
   - Status: **Verified**.

### 3.4 Group D: Lexical Features with Systematic Anomalies

1. **`URLLength` Discrepancy**:
   - Comparison: `len(url.strip()) - URLLength`
   - Exact match (`diff == 0`): 48,644 rows (20.63%)
   - Off by 1 (`diff == 1`): 187,149 rows (79.37%)
   - Off by 4 or 35: 2 rows (involving non-ASCII characters).
   - Verdict: The dataset extraction script had an unexplained 1-character truncation (e.g. omitting trailing delimiter or newline). PhishGuard retains the standard, unambiguous Python definition: `len(url.strip())`.

2. **`NoOfLettersInURL` Anomaly**:
   - Comparison: `sum(char.isalpha() for char in url) - NoOfLettersInURL`
   - Exact match (`diff == 0`): **0 rows (0.00%)**.
   - Top differences:
     - `diff == 9`: 135,933 rows (57.65%)
     - `diff == 5`: 43,615 rows (18.50%)
     - `diff == 8`: 30,323 rows (12.86%)
     - `diff == 7`: 10,434 rows (4.43%)
     - `diff == 4`: 9,848 rows (4.18%)
     - `diff == 6`: 5,177 rows (2.20%)
   - Explanation: Differences of 9, 8, 5, and 4 correlate directly with the lengths of `https` (5), `http` (4), and `www` (3). The dataset authors stripped protocol schemes and `www` prefixes before counting letters, but did so inconsistently across different URL structures.
   - Verdict: `NoOfLettersInURL` cannot be classified as reproducible without an exact, verified specification of the dataset author's preprocessing logic. It must not be treated as a standard character count.

### 3.5 Group E: Derived / Proprietary Statistical Heuristics (Unresolved Provenance)

1. **`URLSimilarityIndex`**:
   - Description: Token similarity score (range 0.155 to 100.0, median 100.0).
   - Correlation with `label`: **+0.860358** (the strongest single correlation in the entire dataset).
   - Provenance Assessment: The UCI dataset paper describes this as a token-based similarity comparison between the URL and known legitimate domains. However, the reference domain dictionary and similarity scoring algorithm are not bundled with the dataset.
   - Verdict: **Excluded**. At inference time, PhishGuard cannot compute this feature on an unseen URL without embedding an unverified third-party lookup table. Furthermore, because it acts as a pseudo-target, relying on it introduces severe distribution-shift vulnerability.

2. **`CharContinuationRate`**:
   - Description: Consecutive character set continuation rate (range 0.0 to 1.0).
   - Correlation with `label`: +0.4677.
   - Provenance Assessment: The exact character classes (vowels vs consonants, ASCII vs non-ASCII, alphanumeric vs symbol) and boundary reset rules are not defined in the dataset documentation.
   - Verdict: **Unresolved**. Candidate for potential future investigation, but excluded from the current schema.

3. **`TLDLegitimateProb`**:
   - Description: Empirical probability of legitimate usage for the observed TLD (range 0.0 to 0.5229).
   - Provenance Assessment: This is a precomputed lookup table based on the author's historical training corpus. At inference time, previously unseen or newly registered TLDs would have undefined values.
   - Verdict: **Excluded**. Violates static self-contained feature extraction invariants.

4. **`URLCharProb`**:
   - Description: Character distribution probability across the URL (range 0.001 to 0.0908).
   - Provenance Assessment: Calculated from an external character n-gram or unigram probability distribution derived from the training corpus.
   - Verdict: **Excluded**. Cannot be computed deterministically without external probability tables.

### 3.6 Group F: Webpage / DOM Content Features (27 Features)

Columns 27 through 55 (`LineOfCode` through `NoOfExternalRef`) capture attributes of the rendered webpage DOM, HTML tags, scripts, redirection chains, and inline keywords (`Bank`, `Pay`, `Crypto`).

**Mandatory Architecture Invariant Check**:
1. **SSRF (Server-Side Request Forgery)**: Fetching arbitrary user-submitted URLs exposes internal cloud metadata services (`169.254.169.254`), private VPC microservices, and internal endpoints to network scanning and exploitation.
2. **Malware & Drive-By Downloads**: Automated HTTP clients fetching hostile URLs can trigger web exploitation, browser zero-days, or binary drops.
3. **Availability & Parity Breakdown**: Live phishing URLs have short lifespans (median < 24 hours). An inference system that relies on fetching page content will fail immediately when a target site is blocked, taken down, or geo-fenced, resulting in total prediction failure.

**Verdict**: **All 27 webpage-derived features are permanently excluded from PhishGuard's feature schema and model training pipelines.**

---

## 4. Current Nine-Feature Schema Alignment

PhishGuard's currently implemented nine-feature schema ([src/features/schema.py](file:///D:/PHISH/src/features/schema.py)) compares against the provenance findings as follows:

| Schema Feature | Derivation Rule | Provenance Status | Invariant Compliance |
|---|---|---|---|
| `url_length` | `len(url.strip())` | Discrepancy documented; standard rule locked | 100% Static |
| `hostname_length` | `len(parsed.hostname)` | 99.98% agreement with `DomainLength` | 100% Static |
| `is_https` | `int(scheme == "https")` | 99.79% agreement with `IsHTTPS` | 100% Static |
| `is_ip_address` | `int(is_ip(hostname))` | 99.99% agreement with `IsDomainIP` | 100% Static |
| `digit_count` | `sum(c.isdigit() for c in url)` | 99.49% agreement with `NoOfDegitsInURL` | 100% Static |
| `dot_count` | `hostname.count(".")` | Verified hostname dot count | 100% Static |
| `hyphen_count` | `hostname.count("-")` | Verified hostname hyphen count | 100% Static |
| `path_length` | `len(parsed.path)` | Deterministic URI component | 100% Static |
| `query_length` | `len(parsed.query)` | Deterministic URI component | 100% Static |

**Conclusion**: All 9 features in the current schema are **100% static, deterministic, and self-contained**. None depend on external lookups, corpus tables, or network calls.

---

## 5. Provenance Audit Summary

1. **Verified Static Features (Eligible for Modeling)**: `url_length`, `hostname_length`, `is_https`, `is_ip_address`, `digit_count`, `dot_count`, `hyphen_count`, `path_length`, `query_length`, `NoOfEqualsInURL`, `NoOfQMarkInURL`, `NoOfAmpersandInURL`, `TLDLength`.
2. **Unresolved / Inconsistent Lexical Features (Requires Explicit Formulation)**: `NoOfLettersInURL` (systematic stripping anomaly), `NoOfSubDomain` (requires public suffix boundary), `NoOfOtherSpecialCharsInURL` (undocumented character set).
3. **Proprietary Corpus Heuristics (Disqualified)**: `URLSimilarityIndex`, `TLDLegitimateProb`, `URLCharProb`.
4. **Webpage / Content Features (Disqualified by Safety Invariants)**: 27 columns from `LineOfCode` to `NoOfExternalRef`.
5. **Metadata (Disqualified)**: `FILENAME`.
