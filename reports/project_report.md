# Sectoral Performance, Risk, and Trading Opportunity Analysis of NIFTY-50 Stocks Using Python and Tableau

## Cover Page

Group Name: Fino_50 (C-1)

Team Members:

- Aryan Verma - Exploratory Data Analysis, KPI framework, chart outputs
- Devaansh Kathuria - Extraction, ETL, cleaning pipeline, processed data
- Birajit Saikia - Final Tableau asset pack, report, presentation, QA
- Abhey Dua - Statistical analysis, risk scoring, segmentation
- Atharv Paharia - Dataset sourcing, repository setup, problem framing

Project Sector:
Finance / Stock Market Analytics

Institute:
Newton School of Technology

GitHub Repository:
[Hopper__C-1_Fino_50](https://github.com/DevaanshKathuria/Hopper__C-1_Fino_50)

Tableau Public Dashboard URL:
Pending publication. This must be replaced with the final Tableau Public URL before final submission.

Submission Date:
April 28, 2026

Submission Note:
Unless explicitly stated otherwise, all numeric values in this report are computed from the versioned project outputs in `outputs/tables/` and the final Tableau extracts in `data/processed/tableau_stock_level.csv`, `data/processed/tableau_sector_level.csv`, `data/processed/tableau_yearly_trends.csv`, `data/processed/tableau_risk_segments.csv`, and `data/processed/tableau_recommendation_view.csv`.

## Executive Summary

This project converts raw daily market data for NIFTY-linked stocks into a reproducible analytics workflow for sector comparison, risk evaluation, liquidity screening, and dashboard-ready decision support. The committed dataset covers `2000-01-03` to `2021-04-30`, contains `235,192` cleaned daily rows, tracks `49` stable company-file stock keys, and spans `13` mapped sectors.

The final output combines Python ETL, KPI construction, EDA, statistical testing, and a Tableau-ready asset pack. The strongest broad-based market expansion in the sample occurred in `2003` with `50.54%` equal-weighted cumulative return, while `2008` was the deepest yearly drawdown at `-41.59%`. At the stock level, `TCS` leads both annualized return (`21.15%`) and opportunity score (`91.73`). At the sector level, `CEMENT & CEMENT PRODUCTS` leads annualized return (`16.69%`) and opportunity score (`82.69`), while `VEDL` has the highest composite risk score (`98.98`).

The final recommendation layer separates names into `Buy`, `Watch`, `Trade Candidate`, and `Avoid` groups using transparent rule-based segments instead of opaque black-box labels. This keeps the project academically defensible and more practical for viva discussion.

## Sector And Business Context

Indian equity markets generate a large volume of historical stock-level trading data, but portfolio decisions still require structure. Investors need to compare not only raw returns, but also volatility, drawdown, liquidity, delivery participation, and sector resilience. A clean dashboard and report are useful only if the underlying calculations are reproducible and the filters reflect real business questions.

In this project, the business context is investor decision support rather than algorithmic trading. The intended user is a portfolio analyst, research student, or retail-investor-focused reviewer who wants to narrow the opportunity set quickly while keeping risk visible.

## Problem Statement And Objectives

### Problem Statement

Raw NIFTY historical data is not directly decision-ready. Without structured cleaning and derived metrics, it is difficult to determine which sectors and stocks combine return quality, manageable downside, liquidity, and investor conviction.

### Objectives

- preserve raw data and build a reproducible ETL pipeline
- create a cleaned and standardized analytical dataset
- define stock-level and sector-level KPIs
- perform EDA for regime, sector, and liquidity insights
- apply statistical methods for risk and comparison questions
- export Tableau-ready files that support an investor-oriented dashboard
- assemble final report, presentation, and submission QA assets

## Data Description

### Source

- Primary dataset: [Kaggle NIFTY-50 Stock Market Data (2000-2021) by Rohan Rao](https://www.kaggle.com/datasets/rohanrao/nifty50-stock-market-data/data)
- Local raw path: `data/raw/nifty-dataset/`
- Metadata path: `data/raw/nifty-dataset/stock_metadata.csv`

### Coverage

- Raw combined file rows: `235,192`
- Cleaned rows: `235,192`
- Raw columns in `NIFTY50_all.csv`: `15`
- Cleaned analytical columns: `35`
- Stable file-level stock keys used for KPI aggregation: `49`
- Historical row-level symbols observed: `65`
- Sector count: `13`

### Core Variables

- price variables: previous close, open, high, low, last, close, VWAP
- activity variables: volume, turnover, trades
- participation variables: deliverable volume, deliverable percent
- metadata variables: company name, industry, ISIN
- derived analytical fields: returns, spreads, VWAP gap, turnover in crore, delivery ratio, flags, and date components

### Data Limitations And Biases

- The dataset is historical and cannot prove future market behavior.
- Historical NIFTY membership changes create more row-level symbols than the current NIFTY-50 count.
- Missing `trades` and delivery fields affect the certainty of participation-related conclusions.
- Sector counts are uneven, so sector-level comparisons should be read as decision-support evidence rather than universal sector laws.

## Data Cleaning And ETL Methodology

The ETL workflow is implemented in `scripts/etl_pipeline.py` and documented in `docs/cleaning_log.md`. The pipeline detects stock files, attaches metadata, standardizes column names to `snake_case`, converts numeric fields safely, validates OHLC consistency, and engineers derived features.

Key cleaning decisions:

- per-stock files are preferred over `NIFTY50_all.csv` to avoid double counting
- no exact duplicate rows were removed because none were found
- price fields required no final manual imputation after symbol-wise fill checks
- `turnover` was rescaled by `100000` because the committed raw field was consistently inflated relative to `VWAP * Volume`
- missing trading-activity fields were kept visible through flags instead of hidden
- outlier returns were flagged, not deleted, so downstream analysis could exclude them transparently through `analysis_return`

Important ETL evidence from versioned outputs:

- missing `trades` rows: `114,848`
- missing `deliverable_percent` rows: `16,077`
- missing `deliverable_volume` rows: `16,077`
- invalid OHLC rows: `0`
- outlier return rows flagged: `12,680`

## KPI And Metric Framework

The KPI layer is documented in `docs/kpi_framework.md` and exported through `outputs/tables/stock_kpis.csv`, `sector_kpis.csv`, `yearly_market_summary.csv`, and `covid_period_summary.csv`.

The most important KPIs are:

- cumulative return
- annualized return
- volatility
- average daily return
- max drawdown
- risk-adjusted return
- average volume
- average turnover in crore
- average delivery percent
- liquidity score
- investor confidence score
- opportunity score

Why the framework matters:

- return alone can over-reward speculative names
- volatility alone can misclassify slow wealth destroyers
- liquidity matters for execution but not as a direct quality signal
- delivery participation adds context for conviction
- the opportunity score provides a single investor-screening field without hiding the component logic

## EDA

EDA was performed through `notebooks/03_eda.ipynb` and `scripts/eda_analysis.py`. The work focused on market regimes, sector comparisons, liquidity behavior, delivery participation, and COVID-era stress and recovery.

Key EDA outputs:

- `outputs/charts/yearly_market_trend.png`
- `outputs/charts/top_10_stocks_return.png`
- `outputs/charts/sector_return_comparison.png`
- `outputs/charts/sector_volatility_comparison.png`
- `outputs/charts/volume_turnover_trend.png`
- `outputs/charts/delivery_percent_trend.png`
- `outputs/charts/risk_return_scatter.png`
- `outputs/charts/covid_crash_recovery.png`

The EDA stage established the core narrative that the market behaves differently across regimes, sectors, and participation styles. It also showed that turnover and liquidity need to be interpreted together with delivery strength and risk, not in isolation.

## Statistical Analysis

Statistical analysis was completed in `notebooks/04_statistical_analysis.ipynb` and `scripts/statistical_analysis.py`. The analysis added correlation checks, hypothesis testing, downside-risk metrics, transparent stock segmentation, and moving-average trend context.

### Methods Used

- Pearson and Spearman correlation analysis
- independent two-sample t-test for high-delivery vs low-delivery stock returns
- Kruskal-Wallis test for sector return distribution differences
- downside-volatility, historical VaR, and historical CVaR calculation
- rule-based segmentation into five stock groups
- 20-day and 60-day moving-average regime checks

### Core Statistical Results

- `daily_return` vs `volume`: weak positive correlation, statistically significant, economically weak
- `daily_return` vs `turnover_cr`: weak positive correlation, statistically significant, economically weak
- `daily_return` vs `deliverable_percent`: weak negative correlation, statistically significant, economically weak
- `volatility_percent` vs `annualized_return_percent`: weak negative relationship, not statistically significant
- `liquidity_score` vs `risk_adjusted_return`: weak negative relationship, not statistically significant
- high-delivery vs low-delivery stock return test: `p = 0.4856`, so no strong evidence of a return advantage
- sector return difference test: `p = 0.0379`, so sector dispersion is statistically detectable

This supports a cautious interpretation: sector selection matters, downside risk matters, but delivery intensity and raw activity variables are weak stand-alone return signals.

## Tableau Dashboard Design

The final dashboard is specified in `tableau/dashboard_blueprint.md` and uses these exported files:

- `data/processed/tableau_stock_level.csv`
- `data/processed/tableau_sector_level.csv`
- `data/processed/tableau_yearly_trends.csv`
- `data/processed/tableau_risk_segments.csv`
- `data/processed/tableau_recommendation_view.csv`

The Tableau layer is built to answer six investor questions:

1. What is the market regime and how has it changed over time?
2. Which sectors offered the strongest performance-risk trade-off?
3. Which stocks combine return quality, liquidity, and conviction?
4. Which names are risky enough to require caution or tactical positioning?
5. Which sectors recovered best from the COVID crash?
6. Which stocks should be tagged as `Buy`, `Watch`, `Trade Candidate`, or `Avoid`?

The final-load validation output in `outputs/tables/final_load_validation.csv` confirms:

- all five Tableau exports were generated
- duplicate key rows are `0` across all exported datasets
- no unusable index columns were written
- KPI availability is `100%` for four of the five files
- the trend file has expected early-history gaps in rolling averages and some delivery coverage gaps, leaving KPI availability at `99.5%`

Dashboard status at report draft time:
The Tableau-ready data pack and dashboard blueprint are complete, but the final Tableau workbook, screenshots, `.twbx` export, and Tableau Public URL must still be completed in Tableau before submission. The final PDF should be regenerated after those assets are added.

Required interactive filters:
Year, sector or industry, stock symbol, risk bucket, segment, and date range.

Screenshot plan:
Screenshots should be stored in `tableau/screenshots/` and inserted into this section after the workbook is built. Minimum screenshots should include the executive KPI view, market trend view, sector comparison view, stock opportunity view, COVID crash/recovery view, and recommendation view.

## Key Insights

1. The equal-weighted market had its best yearly expansion in `2003` with `50.54%` cumulative return and its weakest in `2008` with `-41.59%`.
2. The dataset covers `49` stable stock keys and `13` sectors, which is enough to compare opportunity, risk, and liquidity without relying on fabricated entities.
3. `TCS` is the strongest all-around stock in the current KPI framework with `21.15%` annualized return and `91.73` opportunity score.
4. `CEMENT & CEMENT PRODUCTS` is the strongest sector on both annualized return (`16.69%`) and opportunity score (`82.69`).
5. `VEDL` is the highest-risk stock in the universe with a `98.98` risk score and a `-92.42%` max drawdown.
6. The `2020` COVID crash phase delivered `-17.25%` cumulative return, but the recovery phase rebounded `37.42%`, showing a short, severe drawdown followed by strong reversal.
7. Recovery behavior was uneven across sectors; cement, pharma, and IT show stronger recovery narratives than weaker opportunity sectors such as services, telecom, and media.
8. Liquidity is necessary for execution but insufficient for investment quality. Highly liquid names do not automatically rank well on opportunity score or long-run return.
9. Delivery intensity alone does not explain stock-level return differences in this sample because the high-delivery vs low-delivery test was not significant.
10. Sector differences are meaningful enough to justify sector-aware dashboard views because the Kruskal-Wallis test rejected equal return distributions at the `5%` level.
11. The sample ended on `2021-04-30` with a market `Downtrend` signal because the 20-day moving average (`366.95`) was below the 60-day moving average (`368.84`).
12. The recommendation layer narrows the universe to `8` `Buy` names, `11` `Watch` names, `18` `Trade Candidate` names, and `12` `Avoid` names, which creates an actionable final story for Tableau.

## Recommendations

1. Use the `Buy` bucket as the core long-horizon shortlist because it is anchored in the `Stable Compounders` segment and supported by stronger opportunity scores.
2. Use `Trade Candidate` names for tactical monitoring only, especially when they come from `High Growth High Risk` or liquidity-led segments.
3. Keep `Watch` names visible for lower-volatility positioning, especially under weaker market trend signals.
4. Deprioritize `Avoid` names in the default dashboard ranking because their return quality and risk profile do not support strong allocation arguments.
5. Lead the sector story with cement, IT, pharma, automobile, and financial services rather than weaker opportunity sectors such as services, telecom, and media.

## Impact Estimation

This capstone does not claim realized portfolio returns, but it can estimate decision-support impact.

- The recommendation layer reduces the active review set from `49` stocks to `8` core `Buy` names for a first-pass shortlist. That is an `83.7%` reduction in screening load.
- The sector layer reduces the attention set from `13` sectors to the top `3` or `5` sectors depending on the view, which lowers dashboard complexity while keeping the strongest comparative stories visible.
- The final Tableau pack consolidates the project into `5` versioned CSV files, making dashboard construction faster and more reproducible than rebuilding metrics inside Tableau.
- The validation file surfaces data quality openly, reducing the risk of silent spreadsheet mistakes during final dashboard assembly.

## Limitations

- The dataset is historical and backward-looking.
- The stock universe may still contain survivorship and constituent-change effects.
- Some missing `trades` and `deliverable` fields remain in the source data and are intentionally not fabricated.
- Statistical significance in long time-series data should not be confused with causality.
- Sector counts are uneven, so some sector comparisons are more stable than others.
- The recommendation layer is rule-based decision support, not live investment advice.

## Future Scope

- add benchmark comparison against NIFTY index or macro indicators
- test rolling-window robustness for opportunity and risk scores
- enrich the recommendation layer with valuation or earnings data
- publish the final Tableau dashboard with narrative annotations and parameter actions
- extend the project to include scenario analysis and portfolio simulation

## Conclusion

The project now reaches the final integration stage with reproducible ETL, documented KPIs, EDA evidence, statistical analysis, and a Tableau-ready asset pack. The strongest project story is not simply that some stocks went up more than others, but that risk, liquidity, delivery strength, sector behavior, and crash recovery can be combined into a clearer investor-screening framework. The final deliverables are positioned for submission as long as the team completes the final manual packaging steps for Tableau `.twbx`, screenshots, and PDF exports.

## Appendix

### Appendix A: Key Output Artifacts

- cleaned dataset: `data/processed/nifty50_cleaned.csv`
- stock KPIs: `outputs/tables/stock_kpis.csv`
- sector KPIs: `outputs/tables/sector_kpis.csv`
- yearly summary: `outputs/tables/yearly_market_summary.csv`
- risk summary: `outputs/tables/risk_summary.csv`
- stock segments: `outputs/tables/stock_segments.csv`
- recommendation evidence: `outputs/tables/recommendation_evidence.csv`
- final Tableau pack:
`data/processed/tableau_stock_level.csv`, `data/processed/tableau_sector_level.csv`, `data/processed/tableau_yearly_trends.csv`, `data/processed/tableau_risk_segments.csv`, and `data/processed/tableau_recommendation_view.csv`
- final load validation: `outputs/tables/final_load_validation.csv`

### Appendix B: Data Dictionary Summary

| Field Group | Representative Columns | Business Use |
| --- | --- | --- |
| Price fields | `prev_close`, `open`, `high`, `low`, `close`, `vwap` | return, volatility, spread, and trade-quality analysis |
| Activity fields | `volume`, `turnover`, `trades`, `turnover_cr` | liquidity and market-depth analysis |
| Delivery fields | `deliverable_volume`, `deliverable_percent`, `delivery_ratio` | participation and holding-conviction proxy |
| Metadata fields | `source_symbol`, `company_name`, `industry`, `isin_code` | stock and sector grouping |
| Quality flags | `missing_price_flag`, `missing_volume_flag`, `invalid_ohlc_flag`, `outlier_return_flag` | transparent ETL validation and analysis filtering |
| KPI fields | `annualized_return_percent`, `volatility_percent`, `max_drawdown_percent`, `opportunity_score` | stock and sector decision support |

Full field definitions are maintained in `docs/data_dictionary.md`.

### Appendix C: Cleaning Log Summary

- Raw stock files used: `50`
- Combined raw file detected but not stacked: `1`
- Cleaned rows: `235,192`
- Date range: `2000-01-03` to `2021-04-30`
- Missing `trades` rows: `114,848`
- Missing `deliverable_percent` rows: `16,077`
- Invalid OHLC rows: `0`
- Outlier return rows flagged: `12,680`
- Turnover scale factor applied: `100000`

The full cleaning log is maintained in `docs/cleaning_log.md`.

### Appendix D: Notebook And Script References

| Project Stage | Notebook | Supporting Script |
| --- | --- | --- |
| Extraction | `notebooks/01_extraction.ipynb` | `scripts/etl_pipeline.py` |
| Cleaning | `notebooks/02_cleaning.ipynb` | `scripts/etl_pipeline.py` |
| EDA and KPIs | `notebooks/03_eda.ipynb` | `scripts/eda_analysis.py` |
| Statistical analysis | `notebooks/04_statistical_analysis.ipynb` | `scripts/statistical_analysis.py` |
| Final Tableau load | `notebooks/05_final_load_prep.ipynb` | final-load notebook code |

### Appendix E: Chart And Table Outputs

Core chart outputs are stored in `outputs/charts/`, including yearly trend, sector return, sector volatility, delivery trend, risk-return scatter, COVID crash/recovery, correlation heatmap, and segmentation visuals.

Core table outputs are stored in `outputs/tables/`, including cleaning summary, stock KPIs, sector KPIs, yearly market summary, COVID period summary, statistical test results, risk summary, stock segments, recommendation evidence, and final load validation.

### Appendix F: Tableau Submission Note

The dashboard must be exported and submitted in `.twbx` format only. The Tableau Public link should be stored in `tableau/dashboard_links.md` after publication and should match the same final packaged workbook.

### Appendix G: Contribution Matrix

| Team Member | Dataset & Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT & Viva |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Aryan Verma | Support | Review | Lead: KPIs, EDA charts, insight memo | Support | Chart support | Support | Support |
| Devaansh Kathuria | Support | Lead: ETL pipeline, cleaning notebook, processed data | Support | Support | Data support | Support | Support |
| Birajit Saikia | Review | Final integration QA | Final integration QA | Final integration QA | Lead: Tableau CSV pack, blueprint, dashboard links | Lead: final report assembly | Lead: presentation outline and viva prep |
| Abhey Dua | Support | Review | Support | Lead: tests, risk scoring, segmentation, recommendations | Statistical evidence support | Support | Support |
| Atharv Paharia | Lead: sourcing, repository setup, initial framing | Support | Support | Support | Support | Early documentation | Support |

Contribution evidence:

- Git history shows visible commits from all five members.
- `git shortlog -sne --all` shows 6 commits each for Aryan Verma, Devaansh Kathuria, Birajit Saikia, Abhey Dua, and Atharv Paharia in the audited local repository history.
- The matrix above should still be checked against GitHub Insights and any pull request evidence before final form submission.

Final note:
This matrix should be cross-checked one last time against the final commit history before form submission.
