# Dataset Provenance: UCI PhiUSIIL Phishing URL Dataset

## Dataset Metadata
- **Dataset Name**: PhiUSIIL Phishing URL (Website) Dataset
- **Repository**: UCI Machine Learning Repository
- **URL**: `https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset`
- **DOI**: `10.24432/C56540`
- **Donation Date**: 2024
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)

## Verified Dimensions & Characteristics
- **Total Instances**: 235,795
- **Total Features**: 54 features
- **Class Breakdown**:
  - Legitimate URLs: 134,850 instances
  - Phishing URLs: 100,945 instances
- **Target Column**: `label`
  - `1`: Legitimate
  - `0`: Phishing
- **Missing Values**: 0 (UCI records state no missing values)

## Immutability Protocol
The raw dataset downloaded in Phase 1 is stored in `data/raw/` and is strictly read-only. No normalization, header rewriting, row deletion, or in-place transformations are permitted on the raw file.
