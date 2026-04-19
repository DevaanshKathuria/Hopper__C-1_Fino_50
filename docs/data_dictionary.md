# NIFTY-50 Dataset Data Dictionary

## Purpose

This draft data dictionary documents the raw fields currently available in the committed NIFTY dataset under `data/raw/nifty-dataset/`. Source spellings are preserved exactly to avoid confusion during ETL.

## Primary Trading File

Primary file: `data/raw/nifty-dataset/NIFTY50_all.csv`

Verified columns:

- `Date`
- `Symbol`
- `Series`
- `Prev Close`
- `Open`
- `High`
- `Low`
- `Last`
- `Close`
- `VWAP`
- `Volume`
- `Turnover`
- `Trades`
- `Deliverable Volume`
- `%Deliverble`

### Field Definitions

| Column | Description | Likely Type | Notes for Cleaning / Analysis |
| --- | --- | --- | --- |
| `Date` | Trading date for the row | date | Convert to datetime and validate range coverage |
| `Symbol` | Stock ticker / trading symbol | string | Historical constituent changes may create more than 50 symbols overall |
| `Series` | Market series classification | string | Check for dominant values such as `EQ` and assess rare categories |
| `Prev Close` | Previous trading session closing price | numeric | Useful for return calculations and gap analysis |
| `Open` | Opening price for the trading session | numeric | Compare with `Prev Close` to study opening gaps |
| `High` | Highest traded price during the session | numeric | Useful for daily range and volatility indicators |
| `Low` | Lowest traded price during the session | numeric | Useful for daily range and downside movement analysis |
| `Last` | Last traded price before close | numeric | Compare with `Close` when checking end-of-day consistency |
| `Close` | Official closing price for the session | numeric | Core field for returns, momentum, and sector performance analysis |
| `VWAP` | Volume weighted average price | numeric | Useful for trading quality and execution-related comparisons |
| `Volume` | Number of shares traded | numeric | Primary liquidity measure |
| `Turnover` | Total traded value | numeric | Check scale, units, and outliers during ETL |
| `Trades` | Number of trades executed | numeric | Missing values may exist and should be profiled before KPI use |
| `Deliverable Volume` | Quantity marked for delivery rather than intraday squaring off | numeric | Useful for delivery strength and trading reliability indicators |
| `%Deliverble` | Percentage of volume categorized as deliverable | numeric | Source field name is misspelled; preserve raw name and consider a standardized alias in processed data |

## Metadata File

Metadata file: `data/raw/nifty-dataset/stock_metadata.csv`

Verified columns:

- `Company Name`
- `Industry`
- `Symbol`
- `Series`
- `ISIN Code`

### Metadata Field Definitions

| Column | Description | Likely Type | Notes for Cleaning / Analysis |
| --- | --- | --- | --- |
| `Company Name` | Full company name | string | Useful for report labels and Tableau display names |
| `Industry` | Sector / industry grouping | string | Validate standardization before sector-level aggregation |
| `Symbol` | Stock ticker / trading symbol | string | Intended join key with the trading dataset |
| `Series` | Market series classification | string | Confirm consistency with the trading file |
| `ISIN Code` | International Securities Identification Number | string | Useful for entity validation and reference |

## Data Quality Notes

- Raw column names should remain unchanged in source-controlled raw files.
- Standardized aliases can be introduced later in `data/processed/` outputs if the team agrees on naming conventions.
- Missingness, duplicate date-symbol rows, and numeric scale checks should be documented during ETL.
- Historical symbol changes should be handled carefully before sector-level comparisons and dashboard filtering.

## Versioning Note

If new raw files are added or the source dataset is refreshed, update this document only after verifying the committed file headers.
