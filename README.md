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
6. Run notebooks in `notebooks/` for EDA, statistical analysis, and final Tableau load preparation.
7. Use processed extracts in Tableau and save screenshots in `tableau/screenshots/`.
8. Store report drafts and the final write-up in `reports/`.

Example setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ETL Execution

Run the reproducible ETL pipeline from the repository root:

```bash
python scripts/etl_pipeline.py
```

Recommended workflow:

1. Confirm the Kaggle files are present in `data/raw/nifty-dataset/`.
2. Run `python scripts/etl_pipeline.py` to rebuild the extracted and cleaned datasets.
3. Open `notebooks/01_extraction.ipynb` to review file detection, extraction logic, and the raw combined dataset profile.
4. Open `notebooks/02_cleaning.ipynb` to review cleaning decisions, validation checks, engineered features, and saved outputs.

Graceful-failure behavior:

- If no raw stock CSVs are available under `data/raw/`, the ETL script exits with a clear instruction instead of fabricating processed outputs.
- When both per-stock files and `NIFTY50_all.csv` are present, the ETL prefers the per-stock files so the combined dataset is rebuilt without double-counting rows.

## ETL Outputs

The extraction and cleaning layer writes the following project artifacts:

| Output Path | Description |
| --- | --- |
| `data/processed/nifty50_combined_raw.csv` | Combined raw trading dataset rebuilt from the detected stock CSV files, with metadata attached where available |
| `data/processed/nifty50_cleaned.csv` | Cleaned and standardized dataset with quality flags and derived trading features |
| `outputs/tables/cleaning_summary.csv` | Machine-readable ETL summary containing row counts, missingness, duplicate counts, and flag totals |
| `docs/cleaning_log.md` | Human-readable cleaning log documenting detection logic, missing-value handling, validation checks, and turnover standardization |

## EDA and KPI Outputs

The analysis layer builds directly on `data/processed/nifty50_cleaned.csv` and is organized around Aryan Verma's EDA, KPI framework, and Tableau-ready tables.

- Notebook: `notebooks/03_eda.ipynb`
- Reusable analysis module: `scripts/eda_analysis.py`
- KPI framework documentation: `docs/kpi_framework.md`
- Business insight memo: `docs/eda_insights.md`

Generated tables:

| Output Path | Description |
| --- | --- |
| `outputs/tables/stock_kpis.csv` | Company-level KPI table covering return, volatility, drawdown, liquidity, delivery strength, and opportunity scoring |
| `outputs/tables/sector_kpis.csv` | Sector-level KPI table for comparative performance, risk, liquidity, and confidence analysis |
| `outputs/tables/yearly_market_summary.csv` | Year-by-year market summary for returns, volatility, turnover, and delivery behavior |
| `outputs/tables/covid_period_summary.csv` | Pre-COVID, crash, and recovery summary table for 2020 stress analysis |

Generated charts:

- `outputs/charts/yearly_market_trend.png`
- `outputs/charts/top_10_stocks_return.png`
- `outputs/charts/sector_return_comparison.png`
- `outputs/charts/sector_volatility_comparison.png`
- `outputs/charts/volume_turnover_trend.png`
- `outputs/charts/delivery_percent_trend.png`
- `outputs/charts/risk_return_scatter.png`
- `outputs/charts/covid_crash_recovery.png`

## Statistical Analysis Outputs

The statistical layer extends the project beyond counts, averages, and descriptive charts. It adds formal testing, downside-risk measurement, rule-based stock segmentation, and cautious moving-average trend analysis without overwriting the earlier EDA outputs.

- Notebook: `notebooks/04_statistical_analysis.ipynb`
- Reusable analysis module: `scripts/statistical_analysis.py`
- Summary memo: `docs/statistical_analysis_summary.md`
- Recommendation memo: `docs/recommendation_evidence.md`

Generated tables:

| Output Path | Description |
| --- | --- |
| `outputs/tables/statistical_test_results.csv` | Correlation checks, hypothesis-test results, p-values, and interpretation notes for the main statistical questions |
| `outputs/tables/risk_summary.csv` | Stock-level downside-risk table with drawdown, downside volatility, historical VaR/CVaR, composite risk score, and risk bucket |
| `outputs/tables/stock_segments.csv` | Rule-based stock segmentation output for compounders, high-growth/high-risk names, liquid trading candidates, weak candidates, and defensive names |
| `outputs/tables/recommendation_evidence.csv` | Five evidence-backed recommendation candidates linking insights to action, impact, and feasibility |

Generated charts:

- `outputs/charts/correlation_heatmap.png`
- `outputs/charts/risk_return_segments.png`
- `outputs/charts/max_drawdown_top10.png`
- `outputs/charts/sector_statistical_comparison.png`

Statistical design notes:

- Delivery, volume, and turnover relationships are treated as exploratory correlations, not causal claims.
- Sector comparison uses a non-parametric test when the data does not support equal-variance assumptions.
- A five-cluster KMeans solution was checked, but the final segmentation uses a transparent rule-based method because the required five-cluster structure was not strongly supported by the sample.
- Trend analysis uses 20-day and 60-day moving averages as regime indicators only and does not claim forecasting accuracy.

## Final Tableau Load And Submission Assets

The final integration layer packages the cleaned data, KPI outputs, and statistical outputs into Tableau-ready files plus submission-facing documentation.

- Notebook: `notebooks/05_final_load_prep.ipynb`
- Validation output: `outputs/tables/final_load_validation.csv`
- Dashboard blueprint: `tableau/dashboard_blueprint.md`
- Dashboard links placeholder: `tableau/dashboard_links.md`
- Final report draft: `reports/project_report.md`
- Presentation outline: `reports/presentation_outline.md`
- Final checklist: `docs/final_submission_checklist.md`
- Viva preparation: `docs/viva_questions.md`

Generated Tableau-ready CSV files:

| Output Path | Description |
| --- | --- |
| `data/processed/tableau_stock_level.csv` | Stock-level KPI pack with opportunity, risk, segment, and recommendation fields |
| `data/processed/tableau_sector_level.csv` | Sector-level KPI pack with COVID crash and recovery comparison fields |
| `data/processed/tableau_yearly_trends.csv` | Date-grain market and sector trend file for timeline views, filters, and regime overlays |
| `data/processed/tableau_risk_segments.csv` | Stock-level risk and segmentation file for scatter plots, risk filters, and downside comparisons |
| `data/processed/tableau_recommendation_view.csv` | Dashboard-ready recommendation file mapping stocks to `Buy`, `Watch`, `Trade Candidate`, and `Avoid` |

Validation notes:

- Duplicate key rows are `0` across all five Tableau exports.
- Four of the five Tableau exports have full KPI availability.
- `tableau_yearly_trends.csv` retains expected early-history gaps in rolling averages and some delivery coverage gaps, producing `99.5%` KPI availability without fabricating values.

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
- Tableau submission requires a packaged workbook in `.twbx` format only; the public URL placeholder is stored in `tableau/dashboard_links.md` until publication.
- No analytical claims should be added unless they are backed by code, outputs, and versioned evidence in this repository.
