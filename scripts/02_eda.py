import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "PhiUSIIL_Phishing_URL_Dataset.csv"

print("Python:", sys.version)
print("Dataset:", DATA_PATH)
print("Exists:", DATA_PATH.exists())

df = pd.read_csv(DATA_PATH)

print("\n========== BASIC DATASET INFO ==========")
print("Shape:", df.shape)

print("\n========== COLUMNS ==========")
print(df.columns.tolist())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== TARGET DISTRIBUTION ==========")
print(df["label"].value_counts())
print("\nTarget percentages:")
print(df["label"].value_counts(normalize=True) * 100)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print("Exact duplicate rows:", df.duplicated().sum())

print("\n========== UNIQUE VALUES ==========")

for col in ["FILENAME", "URL", "Domain", "TLD", "Title", "label"]:
    print(f"{col}: {df[col].nunique(dropna=False)} unique values")


print("\n========== DUPLICATE URLS ==========")
print("Duplicate URL rows:", df["URL"].duplicated().sum())
print("Unique URLs:", df["URL"].nunique())


print("\n========== DUPLICATE DOMAINS ==========")
print("Duplicate Domain rows:", df["Domain"].duplicated().sum())
print("Unique Domains:", df["Domain"].nunique())


print("\n========== TARGET BY URL DUPLICATION ==========")
url_counts = df["URL"].value_counts()
print("URLs occurring more than once:", (url_counts > 1).sum())


print("\n========== TARGET VALUES ==========")
print(df["label"].unique())

print("\n========== REPEATED URL LABEL CONSISTENCY ==========")

repeated_urls = (
    df.groupby("URL")["label"]
      .agg(["count", "nunique"])
)

repeated_urls = repeated_urls[repeated_urls["count"] > 1]

print("Repeated URLs:", len(repeated_urls))
print("Repeated URLs with one label:", (repeated_urls["nunique"] == 1).sum())
print("Repeated URLs with conflicting labels:", (repeated_urls["nunique"] > 1).sum())


print("\n========== EXAMPLE REPEATED URLs ==========")

example_urls = repeated_urls.head(10).index

print(
    df[df["URL"].isin(example_urls)]
    [["URL", "Domain", "label"]]
    .sort_values("URL")
    .to_string(index=False)
)

print("\n========== DOMAIN LABEL CONSISTENCY ==========")

domain_labels = (
    df.groupby("Domain")["label"]
      .agg(["count", "nunique"])
)

repeated_domains = domain_labels[domain_labels["count"] > 1]

print("Repeated domains:", len(repeated_domains))
print(
    "Repeated domains with one label:",
    (repeated_domains["nunique"] == 1).sum()
)
print(
    "Repeated domains with conflicting labels:",
    (repeated_domains["nunique"] > 1).sum()
)


print("\n========== EXAMPLE CONFLICTING DOMAINS ==========")

conflicting_domains = repeated_domains[
    repeated_domains["nunique"] > 1
].index

print("Conflicting domain count:", len(conflicting_domains))

if len(conflicting_domains) > 0:
    print(
        df[df["Domain"].isin(conflicting_domains)]
        [["URL", "Domain", "label"]]
        .sort_values("Domain")
        .head(30)
        .to_string(index=False)
    )

print("\n========== NUMERIC FEATURE SUMMARY ==========")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

print("Number of numeric columns:", len(numeric_cols))
print("\nNumeric columns:")
print(numeric_cols)

print("\nDescriptive statistics:")
print(
    df[numeric_cols]
    .describe()
    .T
    .to_string()
)

print("\n========== NUMERIC FEATURE CARDINALITY ==========")

feature_cardinality = (
    df[numeric_cols]
    .nunique()
    .sort_values()
)

print(feature_cardinality.to_string())

print("\n========== CLASS-WISE NUMERIC SUMMARY ==========")

class_summary = (
    df.groupby("label")[numeric_cols]
    .mean()
    .T
)

print(class_summary.to_string())

print("\n========== EXTREME VALUE ANALYSIS ==========")

continuous_cols = [
    col
    for col in numeric_cols
    if df[col].nunique() > 10 and col != "label"
]

for col in continuous_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr

    extreme_count = (df[col] > upper_bound).sum()

    print(
        f"{col}: "
        f"Q1={q1:.4f}, "
        f"Q3={q3:.4f}, "
        f"upper_bound={upper_bound:.4f}, "
        f"extreme_values={extreme_count}"
    )


print("\n========== CATEGORICAL FEATURE SUMMARY ==========")

categorical_cols = df.select_dtypes(
    include=["object", "string"]
).columns.tolist()

for col in categorical_cols:
    print(f"\n{col}:")
    print("  Unique values:", df[col].nunique(dropna=False))
    print("  Missing values:", df[col].isna().sum())
    print("  Top 10 values:")
    print(df[col].value_counts(dropna=False).head(10).to_string())

print("\n========== FEATURE SOURCE INVENTORY ==========")

url_derived_features = [
    "URLLength",
    "Domain",
    "DomainLength",
    "IsDomainIP",
    "TLD",
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
]

webpage_derived_features = [
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "Title",
    "HasFavicon",
    "Robots",
    "IsResponsive",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasDescription",
    "NoOfPopup",
    "NoOfiFrame",
    "HasExternalFormSubmit",
    "HasSocialNet",
    "HasSubmitButton",
    "HasHiddenFields",
    "HasPasswordField",
    "Bank",
    "Pay",
    "Crypto",
    "HasCopyrightInfo",
    "NoOfImage",
    "NoOfCSS",
    "NoOfJS",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef",
]

metadata_features = [
    "FILENAME",
]

target_feature = "label"

print("URL-derived features:", len(url_derived_features))
print("Webpage-derived features:", len(webpage_derived_features))
print("Metadata features:", len(metadata_features))
print("Target:", target_feature)

print("\nURL-derived:")
print(url_derived_features)

print("\nWebpage-derived:")
print(webpage_derived_features)

print("\nMetadata:")
print(metadata_features)

print("\n========== FEATURE-TARGET CORRELATION ==========")

correlations = (
    df[numeric_cols]
    .corr()["label"]
    .drop("label")
    .sort_values(key=abs, ascending=False)
)

print(correlations.to_string())
