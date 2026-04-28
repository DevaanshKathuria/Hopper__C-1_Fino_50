# Viva Questions And Model Answers

## Dataset Choice

1. **Why did the team choose this dataset?**  
Because it provides long-horizon daily stock data with price, volume, turnover, trades, and delivery fields, which gives enough scope for ETL, KPI design, risk analysis, and Tableau storytelling.

2. **Why is the dataset suitable for a finance capstone?**  
It supports real investor questions such as return comparison, sector behavior, liquidity evaluation, and downside-risk measurement instead of only descriptive plotting.

3. **What is the date range of the final cleaned dataset?**  
The cleaned dataset spans `2000-01-03` to `2021-04-30`.

4. **How many rows and columns are in the cleaned dataset?**  
The cleaned dataset has `235,192` rows and `35` columns.

5. **Why does a NIFTY-50 dataset show more than 50 symbols historically?**  
Because the historical combined data reflects constituent changes and ticker changes over time, so the row-level symbol count is `65` even though the stable file-level stock count used in KPI aggregation is `49`.

## Cleaning And ETL

6. **What was the main ETL challenge?**  
The biggest challenge was turning raw CSVs with inconsistent naming and scaled turnover values into a reproducible, analysis-ready dataset without hiding quality issues.

7. **How were column names standardized?**  
The ETL script converted raw fields into `snake_case`, while preserving the original raw files unchanged.

8. **Why was turnover rescaled?**  
The raw turnover field was about `100000x` larger than `VWAP * Volume`, so the ETL standardized it before calculating turnover in crore.

9. **Did you delete missing rows?**  
No. Missingness was profiled and flagged so the project stayed transparent. Only derived analysis fields excluded flagged outlier returns when appropriate.

10. **How were duplicate rows handled?**  
Exact duplicates were checked, and none were found in the committed dataset.

11. **How did you validate price consistency?**  
The ETL created an `invalid_ohlc_flag` to identify impossible price relationships such as `high < low` or `low > close`. The final count was zero.

12. **Why keep quality flags instead of cleaning everything silently?**  
Because it is more reproducible and academically safer to show where the source data is imperfect than to hide issues that affect interpretation.

## Missing Values

13. **Which fields had the largest missing-value problem?**  
`trades` had `114,848` missing rows, while `deliverable_percent` and `deliverable_volume` each had `16,077` missing rows.

14. **How did missing delivery fields affect the project?**  
They limited some delivery-based interpretations, so delivery measures were used carefully and the report avoids treating them as definitive return signals.

15. **Did missing values break the Tableau pack?**  
No. The final-load validation shows that four Tableau exports have full KPI availability, and the trend file has expected early-history gaps in rolling averages and delivery coverage, leaving `99.5%` KPI availability.

## KPI Formulas

16. **What is cumulative return in this project?**  
It is `((1 + daily_return).prod() - 1) * 100` over the analysis window.

17. **How is annualized return computed?**  
It is derived from compounded growth using `252` trading days per year so periods of different lengths remain comparable.

18. **What does volatility mean here?**  
It is the annualized standard deviation of daily returns, expressed in percentage terms.

19. **What is max drawdown?**  
It is the worst peak-to-trough fall in the cumulative wealth curve, shown as a negative percentage.

20. **Why create liquidity score instead of using only volume?**  
Because volume and turnover capture different aspects of tradeability, so the score combines both into a comparable screening measure.

21. **What is investor confidence score?**  
It blends average delivery percent, close-above-VWAP ratio, and positive-return-day ratio as a proxy for stronger participation quality.

22. **What is opportunity score?**  
It is a composite screening metric combining return, risk-adjusted return, drawdown behavior, liquidity, and confidence into one 0-100 style rank.

## EDA And Results

23. **What were the strongest market years?**  
`2003` was the strongest equal-weighted year in the sample at `50.54%`, while `2008` was the weakest at `-41.59%`.

24. **What did the COVID analysis show?**  
The crash phase delivered `-17.25%`, but the recovery phase rebounded `37.42%`, so the story is sharp drawdown followed by strong reversal rather than permanent collapse.

25. **Which stock ranked best overall?**  
`TCS` ranked best overall with `21.15%` annualized return and `91.73` opportunity score.

26. **Which sector performed best overall?**  
`CEMENT & CEMENT PRODUCTS` ranked best on annualized return and opportunity score in the final KPI framework.

## Statistical Methods

27. **Why use correlation analysis?**  
To test whether activity variables such as volume, turnover, and delivery had meaningful relationships with returns instead of relying only on visual impressions.

28. **Why say some significant results are still weak?**  
Because a very large sample can make tiny effects statistically significant even when the relationship is too small to be practically useful.

29. **What was the result of the delivery-based hypothesis test?**  
The high-delivery vs low-delivery stock return comparison had `p = 0.4856`, so we did not find strong evidence of a return advantage from delivery intensity alone.

30. **Why use Kruskal-Wallis for sector comparison?**  
Because equal-variance assumptions were not ideal for sector returns, so a non-parametric distribution comparison was more defensible.

31. **What did the sector test conclude?**  
Sector return distributions were statistically different at the `5%` level with `p = 0.0379`, which supports sector-aware analysis.

## Risk And Segmentation

32. **Why add VaR and CVaR instead of stopping at volatility?**  
Because investors experience downside risk through tail losses and drawdowns, not standard deviation alone.

33. **Which stock was the riskiest in the final risk table?**  
`VEDL` had the highest risk score at `98.98`.

34. **Why did the team use rule-based segmentation instead of KMeans clusters?**  
The silhouette check did not strongly support a forced five-cluster structure, so rule-based segments were easier to explain, reproduce, and defend.

35. **What are the five segments?**  
`Stable Compounders`, `High Growth High Risk`, `Liquid Trading Candidates`, `Weak Risk-Return Candidates`, and `Defensive / Low Volatility`.

## Tableau Design

36. **Why were five Tableau-ready files created instead of one huge file?**  
Because splitting stock, sector, trend, risk, and recommendation views makes Tableau easier to manage and keeps each sheet focused on one business question.

37. **What is the purpose of the recommendation view?**  
It converts analytical segments into transparent action labels such as `Buy`, `Watch`, `Trade Candidate`, and `Avoid` for faster investor screening.

38. **Why is the dashboard described as decision support and not decoration?**  
Because every section is tied to an investor question: market regime, sector comparison, stock opportunity, crash recovery, or recommendation filtering.

## Limitations And Contributions

39. **What is the biggest limitation of the project?**  
It is a historical, backward-looking analysis with missing activity fields and no live benchmark or valuation overlay, so it supports screening rather than forecasting.

40. **What was your individual contribution?**  
Birajit Saikia handled the final Tableau asset pack, final report assembly, presentation outline, QA, and submission-readiness layer, including `notebooks/05_final_load_prep.ipynb`, the Tableau docs, the report draft, the checklist, and the viva prep file.
