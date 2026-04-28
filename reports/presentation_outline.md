# Presentation Outline

## Slide 1. Title And Team

- Project title: Sectoral Performance, Risk, and Trading Opportunity Analysis of NIFTY-50 Stocks Using Python and Tableau
- Group name: NST DVA Capstone 2 Team
- Team members: Aryan Verma, Devaansh Kathuria, Birajit Saikia, Abhey Dua, Atharv Paharia
- One-line objective: build a reproducible investor decision-support workflow from raw stock-market data

## Slide 2. Problem Statement

- Raw market data is not decision-ready on its own
- Investors need return, risk, liquidity, and conviction in one framework
- Project goal: identify which stocks and sectors offer the strongest balance between opportunity and risk

## Slide 3. Dataset Overview

- Primary source: Kaggle NIFTY-50 Stock Market Data (2000-2021)
- Cleaned coverage: `235,192` rows
- Stable stock keys: `49`
- Historical row-level symbols: `65`
- Sector count: `13`
- Date range: `2000-01-03` to `2021-04-30`

## Slide 4. ETL And Cleaning

- automatic file detection and metadata merge
- column standardization to `snake_case`
- turnover rescaling by `100000`
- quality flags for missing prices, missing volume fields, invalid OHLC, and outlier returns
- important remaining gaps: `114,848` missing `trades` rows and `16,077` missing delivery fields

## Slide 5. KPI Framework

- return: cumulative return, annualized return, average daily return
- risk: volatility, max drawdown, risk-adjusted return
- liquidity: average volume, average turnover, liquidity score
- conviction: average delivery percent, close above VWAP ratio, investor confidence score
- screening metric: opportunity score

## Slide 6. EDA Insights

- best yearly expansion: `2003` at `50.54%`
- worst yearly drawdown: `2008` at `-41.59%`
- COVID crash: `-17.25%`
- COVID recovery: `37.42%`
- cement, IT, and pharma emerge as strong sector stories

## Slide 7. Statistical Analysis

- weak but statistically significant daily-return links with volume and turnover
- delivery intensity did not significantly change stock-level return averages
- sector-return differences were statistically detectable: `p = 0.0379`
- risk layer adds drawdown, downside volatility, VaR, and CVaR
- segmentation produces five explainable action groups

## Slide 8. Tableau Dashboard Walkthrough

- executive KPI cards
- market trend section
- sector comparison section
- stock opportunity scatter and ranking
- COVID crash vs recovery comparison
- recommendation action board

## Slide 9. Key Recommendations

- use `Buy` names as the core shortlist
- monitor `Watch` names for defensive positioning
- use `Trade Candidate` names tactically, not blindly
- keep `Avoid` names below the fold in default ranking
- lead sector discussion with cement, IT, pharma, automobile, and financial services

## Slide 10. Impact, Limitations, And Future Scope

- decision-support impact: first-pass stock shortlist reduced from `49` names to `8` `Buy` names
- limitations: historical sample, missing delivery/trades fields, non-causal statistics
- future scope: benchmark comparison, rolling-window tests, valuation overlays, published Tableau story

## Slide 11. Contribution Matrix

- Atharv: setup, sourcing, problem framing
- Devaansh: ETL and cleaned dataset
- Aryan: EDA, KPIs, chart outputs
- Abhey: statistics, risk, segmentation
- Birajit: final Tableau pack, report, presentation, QA, submission readiness

## Slide 12. Viva Preparation

- be ready to justify dataset choice
- explain why turnover was rescaled
- explain why rule-based segmentation was preferred over forced clustering
- explain why significant p-values can still be economically weak
- explain why the dashboard is designed for decision support instead of decoration

## Export Note

If PDF export is required, convert this final outline after slide design is completed. Do not export a PDF from this outline until the actual slide deck content has been finalized.
