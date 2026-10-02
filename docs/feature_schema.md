# PhishGuard — Production Feature Schema

## 1. Purpose

This document defines the initial feature contract for PhishGuard's static phishing URL detection pipeline.

The system must extract features directly from a submitted URL without visiting, crawling, or downloading content from the target website.

## 2. Schema Version

* Schema ID: `phishguard_url_v1`
* Version: `1.0.0`
* Status: Initial design
* Extraction mode: Static URL analysis

## 3. Initial Feature Inventory

| Feature                   | Data Type | Definition                                                                                                | Status    |
| ------------------------- | --------- | --------------------------------------------------------------------------------------------------------- | --------- |
| `url_length`              | Integer   | Number of characters in the submitted URL                                                                 | Candidate |
| `hostname_length`         | Integer   | Number of characters in the parsed hostname                                                               | Candidate |
| `is_https`                | Integer   | 1 if the URL scheme is HTTPS, otherwise 0                                                                 | Candidate |
| `is_ip_address`           | Integer   | 1 if the hostname is an IP address, otherwise 0                                                           | Candidate |
| `dot_count`               | Integer   | Number of dots in the hostname                                                                            | Candidate |
| `hyphen_count`            | Integer   | Number of hyphens in the hostname                                                                         | Candidate |
| `at_symbol_count`         | Integer   | Number of `@` characters in the URL                                                                       | Candidate |
| `question_mark_count`     | Integer   | Number of `?` characters in the URL                                                                       | Candidate |
| `equal_sign_count`        | Integer   | Number of `=` characters in the URL                                                                       | Candidate |
| `ampersand_count`         | Integer   | Number of `&` characters in the URL                                                                       | Candidate |
| `digit_count`             | Integer   | Number of numeric characters in the URL                                                                   | Candidate |
| `special_character_count` | Integer   | Number of characters outside ASCII letters and digits                                                     | Candidate |
| `subdomain_count`         | Integer   | Number of hostname labels before the registrable domain, subject to a verified public-suffix parsing rule | Pending   |
| `path_length`             | Integer   | Number of characters in the URL path                                                                      | Candidate |
| `query_length`            | Integer   | Number of characters in the URL query component                                                           | Candidate |

## 4. Extraction Rules

1. Parse the submitted URL using a standard URL parser.
2. Do not make HTTP or HTTPS requests to the submitted URL.
3. Do not resolve the hostname through DNS.
4. Do not inspect page HTML, titles, scripts, forms, images, or redirects.
5. Preserve a documented distinction between the original input and its parsed components.
6. Use consistent handling of malformed URLs.
7. Maintain a fixed feature order for model input.
8. Ensure training and inference use the same feature definitions.

## 5. Excluded Feature Categories

The initial static inference schema excludes webpage-dependent features, including:

* Page title and title matching
* Favicon presence
* Robots information
* Page responsiveness
* Redirect behavior
* External forms and references
* Page images, CSS, and JavaScript counts
* Hidden fields and password fields

Provenance-sensitive dataset features remain excluded until their calculation methods can be independently reproduced.

## 6. Validation Requirements

* Feature names must be unique.
* Feature order must be deterministic.
* Feature values must follow the declared data types.
* The extractor must not access the network.
* Invalid input must produce a controlled validation error.
* The feature schema version must be recorded with trained model artifacts.

## 7. Current Status

This is an initial design contract, not a finalized model input schema.

The feature definitions, parsing behavior, edge cases, and production eligibility must be validated through implementation and tests before model training.

## 8. Initial Implementation Status

The initial nine-feature extraction implementation has been completed.

### Implemented Features

* `url_length`
* `hostname_length`
* `is_https`
* `is_ip_address`
* `digit_count`
* `dot_count`
* `hyphen_count`
* `path_length`
* `query_length`

### Implemented Components

* URL parsing and validation
* Static feature extraction
* Fixed feature ordering
* Schema version `1.0.0`
* Feature type and value validation
* Conversion to an ordered model input vector
* Unit tests for parsing, extraction, and schema validation

### Pending Work

* Additional URL feature calculations
* Public suffix and subdomain parsing rules
* Unicode and internationalized domain handling
* Expanded malformed URL test coverage
* Training and inference integration
* Final production feature approval

The current schema is an initial implementation and must not be treated as the final production model contract.
