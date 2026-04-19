# Dataset Sources and Suitability

## Primary Dataset

- Name: NIFTY-50 Stock Market Data (2000-2021)
- Source: Kaggle
- Publisher: Rohan Rao
- Link: [https://www.kaggle.com/datasets/rohanrao/nifty50-stock-market-data/data](https://www.kaggle.com/datasets/rohanrao/nifty50-stock-market-data/data)
- Local raw path: `data/raw/nifty-dataset/`

## Local Repository Evidence

The following raw files are already present in this repository:

- `data/raw/nifty-dataset/NIFTY50_all.csv`
- `data/raw/nifty-dataset/stock_metadata.csv`
- 50 additional per-stock CSV files inside `data/raw/nifty-dataset/`

Verified local file characteristics:

- `NIFTY50_all.csv`: 235,192 data rows, 15 columns, 65 distinct symbols
- `stock_metadata.csv`: 50 data rows, 5 columns
- Total CSV files in the raw dataset folder: 52

Note: although the dataset is branded around NIFTY-50, the combined historical file currently contains 65 distinct symbols. This is consistent with historical constituent changes and should be documented during ETL and analysis.

## Backup Dataset 1

- Name: S&P 500 Stocks
- Source: Kaggle
- Publisher: Andrew Mvd
- Link: [https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks](https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks)
- Intended use: fallback benchmark or backup stock-market dataset if primary ingestion or schema issues affect the planned workflow

## Backup Dataset 2

- Status: Placeholder
- Note: a second Kaggle backup can be added later if the team decides to supplement sector benchmarking, index comparison, or macro context. No second backup dataset is referenced in the current repository contents yet.

## Suitability Against Capstone Requirements

| Requirement | Assessment | Evidence |
| --- | --- | --- |
| Minimum rows | Suitable | `NIFTY50_all.csv` contains 235,192 data rows |
| 8+ columns | Suitable | Primary file contains 15 columns |
| Raw row-level records | Suitable | Daily stock-trading rows are preserved in raw CSV form |
| Cleaning potential | Suitable | Field naming inconsistencies, missing values, historical constituent changes, and metadata joins create meaningful ETL scope |
| Tableau usability | Suitable | Time series, stock-level, and sector-level summaries can be exported from processed outputs for Tableau |

## Capstone Relevance

This dataset is well aligned with the project title and business problem because it supports:

- stock-level return and volatility analysis
- liquidity and turnover exploration
- deliverable-volume-based trading strength analysis
- sector mapping using metadata
- creation of Tableau-ready summary tables and dashboard inputs

## Documentation Guidance

- Do not state fixed sector-level conclusions until ETL and analysis are complete.
- Keep row-count and schema references synchronized with the committed raw files.
- Record any future backup dataset adoption in this document before use in analysis.
