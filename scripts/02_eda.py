from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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