# Recommendation Evidence

## Candidate 1

Insight:
Stable compounders appear to offer the cleanest balance of return quality and risk discipline in this dataset.

Statistical evidence:
The strongest stable-compounder names in `stock_segments.csv` are `TCS`, `BAJAJ-AUTO`, and `DRREDDY`. They rank highly on the rule-based compounder score, which rewards annualized return, risk-adjusted return, lower volatility, delivery strength, and more manageable drawdowns.

Recommended action:
Use the stable-compounder segment as the default long-horizon shortlist in the report and Tableau story.

Expected business impact:
This improves the quality of the capstone's recommended watchlist by prioritizing names with stronger all-around evidence rather than pure-return chasing.

Feasibility note:
High. The logic already exists in `outputs/tables/stock_segments.csv` and is easy to expose through filters or highlight cards.

## Candidate 2

Insight:
High-growth names can still be valuable, but only if the project frames them as risk-capped tactical positions.

Statistical evidence:
`JSWSTEEL`, `HCLTECH`, and `HINDALCO` score highly inside the `High Growth High Risk` segment. Their annualized returns are attractive, but the risk table also shows elevated volatility, historical VaR, and downside-volatility values.

Recommended action:
Position this segment as a tactical sleeve with explicit position limits, not as a core holding basket.

Expected business impact:
The recommendation preserves upside optionality while showing that the team understands downside control, which is important for the capstone's decision-quality standard.

Feasibility note:
High. The segment is already labeled and can be used directly in visual filters, stock rankings, and watchlist tables.

## Candidate 3

Insight:
Liquidity improves execution quality, but it does not guarantee superior risk-adjusted performance.

Statistical evidence:
The correlation between `liquidity_score` and `risk_adjusted_return` is weak and not statistically significant (`r = -0.1498`, `p = 0.3042`). At the same time, highly liquid names such as `SBIN`, `ICICIBANK`, and `TATAMOTORS` are easy to trade but do not all qualify as strong long-run holdings.

Recommended action:
Use the liquid segment as an execution-first shortlist for active trading or dashboard defaults, but always pair it with return-quality and drawdown filters.

Expected business impact:
This reduces the chance of recommending highly tradable but weak-performing names simply because they are liquid.

Feasibility note:
Very high. Liquidity score is already present in the KPI layer and the new segmentation output.

## Candidate 4

Insight:
Defensive names become more valuable when market momentum softens.

Statistical evidence:
The equal-weighted market closes the sample on `2021-04-30` with a `Downtrend` signal because the 20-day moving average (`366.95`) is below the 60-day moving average (`368.84`). Defensive names such as `NESTLEIND`, `ASIANPAINT`, `HDFCBANK`, and `SUNPHARMA` show lower volatility and downside-volatility profiles than the broader stock universe.

Recommended action:
Use a simple moving-average regime rule in the report narrative: when broad momentum weakens, tilt attention toward the defensive segment rather than higher-beta names.

Expected business impact:
This adds a practical market-regime recommendation without pretending to forecast prices precisely.

Feasibility note:
Moderate to high. The moving-average fields are already produced in the notebook, and the defensive names are pre-labeled in `stock_segments.csv`.

## Candidate 5

Insight:
Some stocks and sectors should be explicitly deprioritized because the risk taken was not rewarded.

Statistical evidence:
Weak risk-return names such as `ADANIPORTS`, `EICHERMOT`, `ZEEL`, `BHARTIARTL`, and `COALINDIA` combine negative or weak annualized returns with deep drawdowns. The sector comparison test also finds statistically detectable sector-return distribution differences (`Kruskal-Wallis p = 0.0379`), while the high-delivery vs low-delivery return test is not significant (`p = 0.4856`).

Recommended action:
Underweight or flag weak risk-return candidates in Tableau and keep stronger sectors such as `CEMENT & CEMENT PRODUCTS`, `PHARMA`, and `IT` above them in recommendation lists.

Expected business impact:
This improves screening quality and prevents the capstone from overstating the usefulness of delivery strength or liquidity without return support.

Feasibility note:
High. The rule can be implemented directly with the new risk, segment, and statistical-test outputs.
