# EDA Insights

Insight:
The market delivered its strongest broad-based expansion in 2003 and its deepest drawdown in 2008.

Evidence:
The equal-weighted yearly market summary shows `2003` at `50.54%` cumulative return and `2008` at `-41.59%`, with volatility rising from `14.64%` in 2003 to `20.77%` in 2008.

Business Meaning:
The dashboard needs a time lens that separates high-return years from high-risk years instead of treating all uptrends as equally investable.

Dashboard Usage:
Use the yearly trend card and volatility view to explain regime shifts before comparing stocks or sectors.

Insight:
The 2020 COVID shock was a short, sharp drawdown followed by a stronger recovery phase.

Evidence:
The crash window from `2020-02-17` to `2020-03-31` produced `-17.25%` cumulative return with `24.82%` volatility, while the recovery window from `2020-04-01` to `2020-12-31` delivered `37.42%` cumulative return with `15.69%` volatility.

Business Meaning:
Stress periods can reverse quickly, so the project should highlight resilience and recovery potential instead of only drawdown pain.

Dashboard Usage:
Use the COVID summary table and crash-recovery chart to support stress-test storytelling and recovery comparisons.

Insight:
Turnover surged during and after the COVID shock, even while delivery participation weakened.

Evidence:
Average turnover moved from `17,196.87 Cr` in the pre-COVID baseline to `26,892.55 Cr` during the crash and `33,384.83 Cr` during recovery, while average delivery percent fell to `30.24%` in the recovery phase.

Business Meaning:
Higher trading activity did not automatically mean stronger holding conviction; much of the rebound was accompanied by faster market churn.

Dashboard Usage:
Pair turnover and delivery trend panels so users can distinguish speculative activity from stronger delivery-led participation.

Insight:
Cement led the sector opportunity ranking because it combined return strength with the strongest confidence profile.

Evidence:
`CEMENT & CEMENT PRODUCTS` posted the highest `opportunity_score` at `82.69`, the highest `average_annual_return_percent` at `20.90%`, and an `investor_confidence_score` of `90.00`.

Business Meaning:
Cement deserves a priority place in any sector shortlist because it balanced performance with relatively supportive delivery behavior.

Dashboard Usage:
Feature cement near the top of the sector benchmark and opportunity leaderboard.

Insight:
IT offered one of the cleanest quality-growth profiles in the dataset.

Evidence:
The IT sector recorded `14.85%` average annual return, `23.45%` volatility, and a `77.31` opportunity score. At the stock level, `TCS`, `INFY`, and `HCLTECH` all appear in the top opportunity cohort.

Business Meaning:
IT can be positioned as a repeatable compounder segment rather than a purely momentum-driven trade.

Dashboard Usage:
Use sector filters and the risk-return scatter to highlight IT names as balanced candidates.

Insight:
Financial services was the market's liquidity backbone even when it was not the top-returning sector.

Evidence:
`FINANCIAL SERVICES` posted the highest sector `liquidity_score` at `100.00`, while stocks such as `SBIN`, `ICICIBANK`, and `AXISBANK` rank among the most liquid names in the stock KPI table.

Business Meaning:
This sector matters for execution practicality, portfolio sizing, and dashboard default watchlists because it offers the deepest trading access.

Dashboard Usage:
Use financial services as an anchor segment in liquidity views and tradeability filters.

Insight:
The strongest all-around stock opportunities came from quality compounders rather than the most speculative movers.

Evidence:
The top five stock `opportunity_score` values belong to `TCS (91.73)`, `RELIANCE (84.80)`, `ASIANPAINT (80.61)`, `HDFC (79.69)`, and `BAJAJ-AUTO (79.64)`.

Business Meaning:
A composite score that rewards return quality, liquidity, and conviction surfaces steadier leaders than a pure-return leaderboard would.

Dashboard Usage:
Use `opportunity_score` as the default sort in the stock ranking dashboard.

Insight:
Liquidity alone did not protect investors from weak long-run outcomes.

Evidence:
`ICICIBANK` and `BHARTIARTL` rank high on liquidity, yet they still show negative cumulative returns of `-34.32%` and `-35.47%`. `COALINDIA` combines a healthy liquidity score of `74.49` with the weakest cumulative return at `-70.53%`.

Business Meaning:
Tradeability should be treated as a qualifying filter, not as a substitute for return quality.

Dashboard Usage:
Expose liquidity and return KPIs side by side to avoid false positives in stock screening.

Insight:
Delivery participation structurally weakened in the later years of the dataset.

Evidence:
Average market delivery percent was `54.81%` in `2017`, fell to `41.56%` in `2019`, and reached the dataset low of `32.77%` in `2020`, with only a mild rebound to `33.50%` in `2021`.

Business Meaning:
Recent activity became more turnover-heavy and less delivery-led, which can signal shorter holding horizons and a faster trading market.

Dashboard Usage:
Keep delivery trend and investor confidence views visible alongside market-level return charts.

Insight:
VWAP gap had a clearer same-day relationship with returns than raw liquidity variables did.

Evidence:
The correlation matrix shows `daily_return` correlating `0.271` with `vwap_gap`, versus only `0.030` with `volume`, `0.032` with `turnover_cr`, and `-0.036` with `deliverable_percent`.

Business Meaning:
Execution context and where the market closes relative to VWAP may be more informative for short-horizon trade interpretation than sheer activity levels.

Dashboard Usage:
Use VWAP gap in detail views, tooltips, or conditional formatting for trade-quality exploration.

Insight:
Services, telecom, and media were the weakest sector opportunity zones in this dataset.

Evidence:
`SERVICES` posted the lowest sector `opportunity_score` at `11.15`, while `MEDIA & ENTERTAINMENT` and `TELECOM` remained low at `19.42` and `30.58` respectively.

Business Meaning:
These sectors should be treated cautiously in dashboard default rankings unless a user is intentionally exploring turnaround or contrarian cases.

Dashboard Usage:
Sort sector views by `opportunity_score` so weaker sectors naturally fall below the higher-conviction options.
