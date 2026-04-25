# KPI Framework

## Scope and Computation Notes

- Stock-level KPIs are computed at the stable company-file level using `source_symbol`, not the historical row-level `symbol`, because several companies changed ticker spellings over time.
- Return-based KPIs use `daily_return` after excluding rows where `outlier_return_flag = True`. This keeps ETL quality flags intact without changing Devaansh's cleaning logic.
- Sector-level KPIs use equal-weighted daily returns across the companies available inside each industry on each trading day.
- Market-level yearly summaries use equal-weighted daily returns across the available company files in each session.

## KPI Definitions

| KPI | Formula / Computation Logic | Why It Matters | Dashboard View |
| --- | --- | --- | --- |
| `cumulative_return_percent` | `((1 + daily_return).prod() - 1) * 100` across the analysis window | Shows total wealth creation or destruction over the selected period | Stock leaderboard, sector benchmark, COVID stress view |
| `annualized_return_percent` | `(((1 + cumulative_return) ** (252 / trading_days)) - 1) * 100` | Makes long and short coverage periods more comparable | Risk-return matrix, KPI cards |
| `volatility_percent` | `std(daily_return) * sqrt(252) * 100` | Quantifies risk and price instability | Sector volatility panel, stock risk filter |
| `average_daily_return` | `mean(daily_return) * 100` | Gives the average session-level payoff in percentage terms | Market trend diagnostics, stock detail tooltips |
| `max_drawdown_percent` | Minimum value of `(wealth_index / running_peak - 1) * 100` | Measures the worst peak-to-trough capital erosion | Downside-risk comparison, watchlist review |
| `average_volume` | Mean of daily `volume` | Captures trading depth in share terms | Liquidity panel, stock tradeability filter |
| `average_turnover_cr` | Mean of daily `turnover_cr` | Captures traded value in crore rupees, which is more decision-ready for market activity tracking | Liquidity trend, sector depth view |
| `average_delivery_percent` | `mean(deliverable_percent) * 100` | Acts as a proxy for delivery-based participation and holding conviction | Delivery strength view, investor behavior view |
| `risk_adjusted_return` | `annualized_return / annualized_volatility` with no risk-free adjustment | Balances reward against instability for quick ranking | Opportunity matrix, stock shortlist |
| `liquidity_score` | `0.5 * percentile_rank(average_volume) + 0.5 * percentile_rank(average_turnover_cr)` | Creates a comparable 0-100 tradeability score across names and sectors | Liquidity ranking table, bubble-size encoding |
| `investor_confidence_score` | `0.6 * percentile_rank(average_delivery_percent) + 0.25 * percentile_rank(close_above_vwap_ratio) + 0.15 * percentile_rank(positive_return_day_ratio)` | Blends delivery participation with price-close strength to approximate conviction | Delivery dashboard, confidence watchlist |
| `opportunity_score` | `0.30 * percentile_rank(annualized_return_percent) + 0.25 * percentile_rank(risk_adjusted_return) + 0.15 * percentile_rank(max_drawdown_percent) + 0.15 * percentile_rank(liquidity_score) + 0.15 * percentile_rank(investor_confidence_score)` | Converts return, risk, liquidity, and conviction into one screening metric | Primary stock ranking, sector opportunity comparison |

## Output Tables

- `outputs/tables/stock_kpis.csv`: company-level KPI table for ranking, filtering, and Tableau drill-down.
- `outputs/tables/sector_kpis.csv`: sector-level KPI table for comparing return, risk, liquidity, and delivery quality.
- `outputs/tables/yearly_market_summary.csv`: yearly market trend summary for macro context and timeline views.
- `outputs/tables/covid_period_summary.csv`: pre-COVID, crash, and recovery comparison for stress-period storytelling.

## Dashboard Mapping

- Market Overview: `yearly_market_summary.csv`, `yearly_market_trend.png`, `volume_turnover_trend.png`, `delivery_percent_trend.png`
- Stock Opportunity Board: `stock_kpis.csv`, `top_10_stocks_return.png`, `risk_return_scatter.png`
- Sector Benchmark: `sector_kpis.csv`, `sector_return_comparison.png`, `sector_volatility_comparison.png`
- Stress and Recovery: `covid_period_summary.csv`, `covid_crash_recovery.png`
