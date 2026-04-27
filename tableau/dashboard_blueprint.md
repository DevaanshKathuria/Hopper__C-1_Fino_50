# Tableau Dashboard Blueprint

## Dashboard Title

NIFTY-50 Sectoral Performance & Risk Intelligence Dashboard

## Build Objective

This dashboard should help an investor or analyst make faster stock-screening and sector-comparison decisions. It should prioritize decision support, comparability, and evidence-backed interpretation instead of decorative visuals.

## Data Files To Use

- `data/processed/tableau_stock_level.csv`
- `data/processed/tableau_sector_level.csv`
- `data/processed/tableau_yearly_trends.csv`
- `data/processed/tableau_risk_segments.csv`
- `data/processed/tableau_recommendation_view.csv`

## Build Principles

- Use the Tableau-ready CSVs as the only dashboard sources for the final version.
- Keep labels business-friendly and consistent with the report.
- Prefer sort order, annotations, and conditional color to show meaning.
- Use tooltips to surface evidence rather than adding clutter to the canvas.
- Keep default views investor-oriented: strongest opportunities, clearest risks, and regime context first.
- Use color to distinguish decision states such as `Buy`, `Watch`, `Trade Candidate`, and `Avoid`.

## Recommended Layout

### 1. Executive KPI Cards

Place these across the top of the dashboard:

- Total stocks analyzed
Source: `tableau_stock_level.csv`
Field logic: `COUNTD([Stock Symbol])`

- Date range
Source: `tableau_yearly_trends.csv`
Field logic: `MIN([Date])` to `MAX([Date])`

- Best performing stock
Source: `tableau_stock_level.csv`
Recommended rule: top `Annualized Return (%)`

- Best performing sector
Source: `tableau_sector_level.csv`
Recommended rule: top `Annualized Return (%)`

- Highest risk stock
Source: `tableau_risk_segments.csv`
Recommended rule: top `Risk Score`

- Average delivery percent
Source: `tableau_stock_level.csv`
Recommended rule: average `Average Delivery (%)`

- Average turnover
Source: `tableau_stock_level.csv`
Recommended rule: average `Average Turnover (Cr)`

Design note:
Keep the cards plain and readable. The value and the definition matter more than decorative icons.

### 2. Market Trend View

Purpose:
Show regime shifts before asking the user to compare stocks.

Required sheets:

- Yearly close or return trend
Recommended source: `tableau_yearly_trends.csv`
Recommended chart: line chart using `Equal Weighted Index` or yearly aggregated `Daily Return`

- Volume and turnover trend
Recommended source: `tableau_yearly_trends.csv`
Recommended chart: dual-axis or aligned small multiples for `Volume` and `Turnover (Cr)`

Suggested fields:

- `Date`
- `Year`
- `View Level`
- `Sector / Industry`
- `Equal Weighted Index`
- `Daily Return`
- `Volume`
- `Turnover (Cr)`
- `Average Delivery (%)`
- `Trend Signal`

### 3. Sector Comparison View

Purpose:
Compare opportunity and risk at the sector level.

Required sheets:

- Sector return
Recommended chart: sorted horizontal bar chart using `Annualized Return (%)`

- Sector volatility
Recommended chart: horizontal bar chart using `Volatility (%)`

- Sector delivery percentage
Recommended chart: lollipop or bar chart using `Average Delivery (%)`

Recommended source:
`tableau_sector_level.csv`

Suggested tooltip fields:

- `Opportunity Score`
- `Liquidity Score`
- `Investor Confidence Score`
- `COVID Crash Return (%)`
- `COVID Recovery Return (%)`
- `Best Stock by Opportunity`

### 4. Stock Opportunity View

Purpose:
Help the user shortlist names rather than just browse them.

Required sheets:

- Risk-return scatter
Recommended source: `tableau_risk_segments.csv`
X-axis: `Volatility (%)`
Y-axis: `Annualized Return (%)`
Color: `Risk Bucket` or `Segment`
Size: `Opportunity Score`

- Opportunity score ranking
Recommended source: `tableau_stock_level.csv`
Recommended chart: sorted bar chart by `Opportunity Score`

- Liquidity score ranking
Recommended source: `tableau_stock_level.csv`
Recommended chart: sorted bar chart by `Liquidity Score`

Suggested tooltip fields:

- `Stock Symbol`
- `Company Name`
- `Sector / Industry`
- `Recommendation Action`
- `Max Drawdown (%)`
- `Average Delivery (%)`

### 5. COVID Crash Recovery View

Purpose:
Show resilience, not just pain.

Required sheets:

- 2020 drawdown
Recommended source: `tableau_sector_level.csv`
Recommended chart: bar chart using `COVID Crash Return (%)`

- Recovery comparison
Recommended source: `tableau_sector_level.csv`
Recommended chart: side-by-side bars or slope chart comparing `COVID Crash Return (%)` vs `COVID Recovery Return (%)`

Suggested supporting callout:

- `Recovery Minus Crash (pp)`

### 6. Recommendation View

Purpose:
Translate the project into action-oriented screening output.

Required sheet:

- Segment-wise action: `Buy`, `Watch`, `Avoid`, `Trade Candidate`

Recommended source:
`tableau_recommendation_view.csv`

Recommended chart options:

- highlight table by `Recommendation Action`
- grouped bars by action bucket
- ranked stock table filtered by action

Suggested display fields:

- `Recommendation Label`
- `Stock Symbol`
- `Sector / Industry`
- `Opportunity Score`
- `Risk Bucket`
- `Annualized Return (%)`
- `Volatility (%)`
- `Why This Action`

## Required Filters

Add these filters to the final dashboard:

- Year
- Sector / Industry
- Stock Symbol
- Risk Bucket
- Segment
- Date range

Implementation note:
Use `tableau_yearly_trends.csv` for date and year filters, then apply dashboard actions or related filters to the stock and sector views where sensible.

## Suggested Color Logic

- `Buy`: dark green
- `Watch`: amber
- `Trade Candidate`: blue
- `Avoid`: red

- Low risk bucket: muted green
- Medium risk bucket: orange
- High risk bucket: red

Use one logic for action and one for risk. Do not mix them inside the same legend unless the sheet demands it.

## Recommended Build Order

1. Connect all five CSV files.
2. Build the executive KPI cards.
3. Build the market trend section from `tableau_yearly_trends.csv`.
4. Build sector comparison from `tableau_sector_level.csv`.
5. Build stock scatter and rankings from `tableau_stock_level.csv` and `tableau_risk_segments.csv`.
6. Build the recommendation section from `tableau_recommendation_view.csv`.
7. Add filters and dashboard actions.
8. Add short evidence tooltips and source notes.
9. Export the packaged workbook as `.twbx`.

## Final Reminder

The dashboard is part of the analytical story, not a poster. If a visual does not help an investor compare return, risk, liquidity, recovery, or recommendation quality, remove it.
