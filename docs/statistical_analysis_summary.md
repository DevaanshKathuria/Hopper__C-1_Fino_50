# Statistical Analysis Summary

## Methods Used

### 1. Correlation analysis

- Pearson correlation was used for the five requested pair checks:
  - `daily_return` vs `volume`
  - `daily_return` vs `turnover_cr`
  - `daily_return` vs `deliverable_percent`
  - `volatility_percent` vs `annualized_return_percent`
  - `liquidity_score` vs `risk_adjusted_return`
- Spearman correlation was also saved as a robustness check in `outputs/tables/statistical_test_results.csv`.

Why it fits the business problem:
Correlation helps the team distinguish activity variables that are merely noisy from variables that are meaningfully associated with short-horizon or stock-level outcomes. This is useful for deciding which fields deserve more dashboard attention.

### 2. Hypothesis testing

- High-delivery vs low-delivery stocks:
  - Stocks were split at the median `average_delivery_percent` of `50.94%`.
  - The comparison was performed at the stock level using `average_daily_return`, not row-level daily returns, so a few long histories did not dominate the test.
  - Assumption checks supported a two-sample t-test.
- Sector return comparison:
  - Equal-weighted daily sector returns were built from the cleaned stock data.
  - Because sector-return variances were not equal, the final comparison used a Kruskal-Wallis test, with one-way ANOVA saved as a reference check.

Why it fits the business problem:
These tests answer two practical questions directly:
- whether stronger delivery participation is actually linked with better returns
- whether sector selection matters enough to justify separate allocation or dashboard ranking logic

### 3. Risk analysis

The stock-level risk table adds multiple downside measures:

- `max_drawdown_percent`
- `downside_volatility_percent`
- `historical_var_95_percent`
- `historical_cvar_95_percent`
- a composite `risk_score`
- risk buckets: `Low`, `Medium`, `High`

Why it fits the business problem:
Investors do not experience risk through standard deviation alone. Drawdown, left-tail risk, and downside-only volatility are more decision-relevant when comparing names for portfolio use or watchlist filtering.

### 4. Segmentation

- A KMeans suitability check was run on scaled stock-level return, risk, and liquidity features.
- The five-cluster solution was not the strongest silhouette result, so the final output uses a transparent rule-based scoring method instead of forcing an unstable clustering structure.
- Stocks were classified into:
  - `Stable Compounders`
  - `High Growth High Risk`
  - `Liquid Trading Candidates`
  - `Weak Risk-Return Candidates`
  - `Defensive / Low Volatility`

Why it fits the business problem:
These segments are easier to explain in a capstone setting than opaque clusters, and they map directly to actionable stock-screening or dashboard-filter stories.

### 5. Trend analysis

- Equal-weighted market and sector indices were built from daily returns.
- 20-day and 60-day moving averages were used as a cautious regime check.

Why it fits the business problem:
The moving-average layer adds a simple trend signal without overclaiming forecasting accuracy. It is useful for timing or regime interpretation in the written report and Tableau annotations.

## Results and Interpretation

### Correlation results

- `daily_return` vs `volume`: `r = 0.0303`, statistically significant but economically very weak
- `daily_return` vs `turnover_cr`: `r = 0.0321`, statistically significant but economically very weak
- `daily_return` vs `deliverable_percent`: `r = -0.0358`, statistically significant but economically very weak
- `volatility_percent` vs `annualized_return_percent`: `r = -0.1601`, not statistically significant
- `liquidity_score` vs `risk_adjusted_return`: `r = -0.1498`, not statistically significant

Interpretation:
The large number of daily observations makes tiny effects look statistically significant, but their business value is limited. Liquidity and delivery strength should not be interpreted as direct return engines on their own.

### Hypothesis-testing results

- High-delivery vs low-delivery stocks:
  - test: independent two-sample t-test
  - p-value: `0.4856`
  - average daily return, high-delivery group: `0.0361%`
  - average daily return, low-delivery group: `0.0417%`
  - conclusion: do not reject the null hypothesis

Interpretation:
Within this sample, delivery intensity does not provide strong evidence of a stock-level return advantage by itself.

- Sector return comparison:
  - test: Kruskal-Wallis
  - p-value: `0.0379`
  - reference ANOVA p-value: `0.8162`
  - conclusion: reject the null hypothesis for equal sector return distributions

Interpretation:
Sector behavior differs in distributional terms, even though pure mean differences are not strong enough under classical ANOVA. This supports sector-aware analysis, but with caution about volatility and dispersion differences.

### Risk results

- The highest composite-risk names include `VEDL`, `ZEEL`, `HINDALCO`, `TATAMOTORS`, and `TATASTEEL`.
- The deepest max drawdowns came from `TITAN (-95.19%)`, `EICHERMOT (-94.10%)`, and `VEDL (-92.42%)`.
- Risk buckets were reasonably balanced:
  - `High`: 17 stocks
  - `Medium`: 16 stocks
  - `Low`: 16 stocks

Interpretation:
Several liquid or well-known stocks still experienced severe capital erosion over the full sample. The capstone should therefore treat liquidity as an execution feature, not as a safety feature.

### Segmentation results

Segment counts:

- `Weak Risk-Return Candidates`: 12
- `Defensive / Low Volatility`: 11
- `High Growth High Risk`: 9
- `Liquid Trading Candidates`: 9
- `Stable Compounders`: 8

Examples:

- Stable compounders: `TCS`, `BAJAJ-AUTO`, `DRREDDY`, `HDFC`, `MARUTI`
- High growth high risk: `JSWSTEEL`, `HCLTECH`, `HINDALCO`
- Defensive / low volatility: `NESTLEIND`, `ASIANPAINT`, `HDFCBANK`, `SUNPHARMA`
- Weak risk-return: `ADANIPORTS`, `EICHERMOT`, `ZEEL`, `BHARTIARTL`, `COALINDIA`

Interpretation:
The segmentation makes it easier to convert raw metrics into a stock-selection narrative. It also reveals that some low-volatility names are not automatically strong return candidates, and some liquid names are not automatically attractive investments.

### Trend results

- The equal-weighted market closed the sample on `2021-04-30` with a `Downtrend` signal because the 20-day moving average (`366.95`) sat below the 60-day moving average (`368.84`).
- The strongest positive sector trend gaps at the sample end came from:
  - `METALS`
  - `CEMENT & CEMENT PRODUCTS`
  - `PHARMA`
  - `IT`

Interpretation:
Trend signals are best used as regime context, not as stand-alone forecasts.

## Limitations

- The dataset reflects the committed NIFTY-50 stock universe and may still carry survivorship effects.
- Daily observations are time-series data, so statistical significance should not be interpreted as causal proof.
- Some sectors have only one stock in the cleaned dataset, which limits sector-level generalization.
- Historical VaR and drawdown are backward-looking and do not guarantee future downside.
- Moving averages are descriptive regime tools, not predictive models.
- Risk-adjusted return is computed without an explicit risk-free rate because the project KPI framework already uses that simpler definition.

## How To Use These Results In Tableau and the Report

- Use `statistical_test_results.csv` for:
  - hypothesis-test summary cards
  - correlation callouts
  - evidence footnotes in the report
- Use `risk_summary.csv` for:
  - stock risk filters
  - risk-bucket color encoding
  - drawdown and VaR comparison tables
- Use `stock_segments.csv` for:
  - dashboard segment filters
  - scatter-plot color groups
  - shortlist views such as compounders vs tactical growth vs weak candidates
- Use `recommendation_evidence.csv` for:
  - the report's recommendation section
  - dashboard narrative text boxes
  - viva-ready evidence summaries
- Use the chart PNGs for:
  - supporting visuals in the report
  - quick image embeds in the deck or documentation

Recommended report stance:

- treat sector selection and downside-risk control as meaningful
- treat delivery participation, raw volume, and raw turnover as weak stand-alone signals
- present segmentation as a decision-support layer, not as a guarantee of performance
