# Sectoral Performance, Risk, and Trading Opportunity Analysis of NIFTY-50 Stocks Using Python and Tableau

## Team Members

- Aryan Verma
- Devaansh Kathuria
- Birajit Saikia
- Abhey Dua
- Atharv Paharia

## Sector

Finance / Stock Market Analytics

## Business Problem

Indian investors and portfolio analysts need a clear way to compare NIFTY-linked stocks and sectors on returns, volatility, liquidity, deliverable strength, and trading reliability. This project builds a reproducible Python-and-Tableau workflow to identify which stocks and sectors offer the best balance between opportunity and risk.

## Dataset Links

- Primary dataset: [Kaggle NIFTY-50 Stock Market Data (2000-2021) by Rohan Rao](https://www.kaggle.com/datasets/rohanrao/nifty50-stock-market-data/data)
- Backup dataset 1: [Kaggle S&P 500 Stocks by Andrew Mvd](https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks)
- Backup dataset 2: To be finalized if additional augmentation is required during ETL validation

## Project Workflow

1. Source and preserve raw row-level market data.
2. Build Python ETL pipelines for cleaning, standardization, and enrichment.
3. Perform exploratory data analysis for stock, sector, and time-based trends.
4. Conduct statistical analysis for volatility, risk, and comparative performance.
5. Prepare Tableau-ready extracts, charts, and supporting tables.
6. Compile the written report, screenshots, and final submission materials.

## Folder Structure

```text
.
|-- data
|   |-- external
|   |-- processed
|   `-- raw
|       `-- nifty-dataset
|-- docs
|-- notebooks
|-- outputs
|   |-- charts
|   `-- tables
|-- reports
|-- scripts
`-- tableau
    `-- screenshots
```

## Reproducibility Instructions

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install project dependencies from `requirements.txt`.
4. Confirm the raw Kaggle files are present in `data/raw/nifty-dataset/`.
5. Run ETL scripts from `scripts/` to generate cleaned outputs in `data/processed/`.
6. Run notebooks in `notebooks/` for EDA and statistical analysis.
7. Use processed extracts in Tableau and save screenshots in `tableau/screenshots/`.
8. Store report drafts and the final write-up in `reports/`.

Example setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Expected Final Deliverables

- Cleaned and documented Python ETL pipeline
- EDA notebooks and charts
- Statistical analysis outputs with interpretable methodology
- Tableau-ready datasets and dashboard assets
- Final written report
- Final presentation/deck
- Submission checklist and repository evidence for viva

## Repository Notes

- Raw source files are preserved under `data/raw/nifty-dataset/`.
- Documentation in `docs/` is intentionally written for academic review, handoff, and viva preparation.
- No analytical claims should be added unless they are backed by code, outputs, and versioned evidence in this repository.
