from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


TRADING_DAYS_PER_YEAR = 252
BOOLEAN_COLUMNS = [
    "missing_price_flag",
    "missing_volume_flag",
    "invalid_ohlc_flag",
    "outlier_return_flag",
]
CORRELATION_SPECS = [
    {
        "analysis_name": "daily_return_vs_volume",
        "scope": "daily_observation",
        "x": "daily_return",
        "y": "volume",
        "label": "Daily Return vs Volume",
        "x_label": "Daily Return",
        "y_label": "Volume",
    },
    {
        "analysis_name": "daily_return_vs_turnover",
        "scope": "daily_observation",
        "x": "daily_return",
        "y": "turnover_cr",
        "label": "Daily Return vs Turnover",
        "x_label": "Daily Return",
        "y_label": "Turnover (Cr)",
    },
    {
        "analysis_name": "daily_return_vs_delivery_percent",
        "scope": "daily_observation",
        "x": "daily_return",
        "y": "deliverable_percent",
        "label": "Daily Return vs Delivery Percent",
        "x_label": "Daily Return",
        "y_label": "Deliverable Percent",
    },
    {
        "analysis_name": "volatility_vs_return",
        "scope": "stock_level",
        "x": "volatility_percent",
        "y": "annualized_return_percent",
        "label": "Volatility vs Annualized Return",
        "x_label": "Volatility (%)",
        "y_label": "Annualized Return (%)",
    },
    {
        "analysis_name": "liquidity_vs_risk_adjusted_return",
        "scope": "stock_level",
        "x": "liquidity_score",
        "y": "risk_adjusted_return",
        "label": "Liquidity Score vs Risk-Adjusted Return",
        "x_label": "Liquidity Score",
        "y_label": "Risk-Adjusted Return",
    },
]
SEGMENT_LABELS = {
    "stable_score": "Stable Compounders",
    "growth_risk_score": "High Growth High Risk",
    "liquid_trading_score": "Liquid Trading Candidates",
    "weak_score": "Weak Risk-Return Candidates",
    "defensive_score": "Defensive / Low Volatility",
}
CHART_FILENAMES = {
    "correlation_heatmap": "correlation_heatmap.png",
    "risk_return_segments": "risk_return_segments.png",
    "max_drawdown_top10": "max_drawdown_top10.png",
    "sector_statistical_comparison": "sector_statistical_comparison.png",
}


def resolve_repo_root() -> Path:
    repo_root = Path.cwd().resolve()
    if (repo_root / "scripts").exists():
        return repo_root
    if (repo_root.parent / "scripts").exists():
        return repo_root.parent
    raise FileNotFoundError("Could not resolve repository root from the current working directory.")


def load_cleaned_data(data_path: Path | None = None) -> pd.DataFrame:
    repo_root = resolve_repo_root()
    target_path = data_path or repo_root / "data" / "processed" / "nifty50_cleaned.csv"
    if not target_path.exists():
        raise FileNotFoundError(
            "Processed data is missing. Run notebooks/02_cleaning.ipynb or python scripts/etl_pipeline.py "
            "to create data/processed/nifty50_cleaned.csv before running the statistical analysis."
        )

    df = pd.read_csv(target_path, parse_dates=["date"])
    df = df.sort_values(["source_symbol", "date"]).reset_index(drop=True)
    for column in BOOLEAN_COLUMNS:
        if column in df.columns and df[column].dtype == object:
            df[column] = df[column].astype(str).str.lower().eq("true")
    df["analysis_return"] = df["daily_return"].where(~df["outlier_return_flag"].fillna(False))
    return df


def load_optional_table(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def _percentile_rank(series: pd.Series) -> pd.Series:
    valid = series.dropna()
    if valid.empty:
        return pd.Series(50.0, index=series.index)
    ranked = valid.rank(pct=True, method="average") * 100
    return ranked.reindex(series.index).fillna(50.0)


def _return_metrics(daily_returns: pd.Series) -> Dict[str, float]:
    returns = daily_returns.dropna().astype(float)
    if returns.empty:
        return {
            "trading_days": 0,
            "cumulative_return_percent": np.nan,
            "annualized_return_percent": np.nan,
            "volatility_percent": np.nan,
            "average_daily_return": np.nan,
            "max_drawdown_percent": np.nan,
            "risk_adjusted_return": np.nan,
        }

    compounded_growth = (1 + returns).prod()
    cumulative_return = compounded_growth - 1
    trading_days = int(returns.shape[0])
    annualized_return = np.nan
    if trading_days > 0 and compounded_growth > 0:
        annualized_return = compounded_growth ** (TRADING_DAYS_PER_YEAR / trading_days) - 1

    volatility = returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    average_daily_return = returns.mean() * 100
    wealth_index = (1 + returns).cumprod()
    running_peak = wealth_index.cummax()
    max_drawdown = (wealth_index / running_peak - 1).min()
    risk_adjusted = np.nan
    if pd.notna(volatility) and volatility > 0:
        risk_adjusted = annualized_return / volatility if pd.notna(annualized_return) else np.nan

    return {
        "trading_days": trading_days,
        "cumulative_return_percent": cumulative_return * 100,
        "annualized_return_percent": annualized_return * 100 if pd.notna(annualized_return) else np.nan,
        "volatility_percent": volatility * 100 if pd.notna(volatility) else np.nan,
        "average_daily_return": average_daily_return,
        "max_drawdown_percent": max_drawdown * 100,
        "risk_adjusted_return": risk_adjusted,
    }


def _safe_quantile(series: pd.Series, q: float) -> float:
    clean = series.dropna().astype(float)
    if clean.empty:
        return np.nan
    return float(np.quantile(clean, q))


def _safe_std(series: pd.Series) -> float:
    clean = series.dropna().astype(float)
    if clean.shape[0] <= 1:
        return np.nan
    return float(clean.std(ddof=1))


def _cohens_d(sample_a: Iterable[float], sample_b: Iterable[float]) -> float:
    values_a = np.asarray(list(sample_a), dtype=float)
    values_b = np.asarray(list(sample_b), dtype=float)
    values_a = values_a[~np.isnan(values_a)]
    values_b = values_b[~np.isnan(values_b)]
    if values_a.size < 2 or values_b.size < 2:
        return np.nan

    pooled_variance = (
        ((values_a.size - 1) * values_a.var(ddof=1)) + ((values_b.size - 1) * values_b.var(ddof=1))
    ) / (values_a.size + values_b.size - 2)
    if pooled_variance <= 0:
        return np.nan
    return float((values_a.mean() - values_b.mean()) / np.sqrt(pooled_variance))


def build_stock_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for symbol, group in df.groupby("source_symbol", sort=True):
        group = group.sort_values("date")
        metrics = _return_metrics(group["analysis_return"])
        negative_returns = group.loc[group["analysis_return"] < 0, "analysis_return"]
        historical_var_95 = -_safe_quantile(group["analysis_return"], 0.05) * 100
        historical_cvar_95 = -negative_returns[negative_returns <= _safe_quantile(group["analysis_return"], 0.05)].mean() * 100
        rows.append(
            {
                "symbol": symbol,
                "company_name": group["company_name"].dropna().iloc[0],
                "industry": group["industry"].dropna().iloc[0],
                "start_date": group["date"].min().date().isoformat(),
                "end_date": group["date"].max().date().isoformat(),
                **metrics,
                "average_volume": group["volume"].mean(),
                "average_turnover_cr": group["turnover_cr"].mean(),
                "average_delivery_percent": group["deliverable_percent"].mean() * 100,
                "positive_return_day_ratio": (group["analysis_return"] > 0).mean() * 100,
                "close_above_vwap_ratio": (group["vwap_gap"] > 0).mean() * 100,
                "downside_volatility_percent": _safe_std(negative_returns) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100,
                "historical_var_95_percent": historical_var_95,
                "historical_cvar_95_percent": historical_cvar_95,
                "median_daily_return_percent": group["analysis_return"].median() * 100,
            }
        )

    stock_summary = pd.DataFrame(rows)
    stock_summary["liquidity_score"] = (
        0.5 * _percentile_rank(stock_summary["average_volume"])
        + 0.5 * _percentile_rank(stock_summary["average_turnover_cr"])
    )
    stock_summary["investor_confidence_score"] = (
        0.6 * _percentile_rank(stock_summary["average_delivery_percent"])
        + 0.25 * _percentile_rank(stock_summary["close_above_vwap_ratio"])
        + 0.15 * _percentile_rank(stock_summary["positive_return_day_ratio"])
    )
    stock_summary["opportunity_score"] = (
        0.3 * _percentile_rank(stock_summary["annualized_return_percent"])
        + 0.25 * _percentile_rank(stock_summary["risk_adjusted_return"])
        + 0.15 * _percentile_rank(stock_summary["max_drawdown_percent"])
        + 0.15 * _percentile_rank(stock_summary["liquidity_score"])
        + 0.15 * _percentile_rank(stock_summary["investor_confidence_score"])
    )
    stock_summary = stock_summary.sort_values(
        ["opportunity_score", "annualized_return_percent"],
        ascending=[False, False],
    ).reset_index(drop=True)
    return stock_summary


def build_sector_daily(df: pd.DataFrame) -> pd.DataFrame:
    sector_daily = (
        df.groupby(["industry", "date"], as_index=False)
        .agg(
            daily_return=("analysis_return", "mean"),
            volume=("volume", "sum"),
            turnover_cr=("turnover_cr", "sum"),
            deliverable_percent=("deliverable_percent", "mean"),
            stock_count=("source_symbol", "nunique"),
        )
        .dropna(subset=["daily_return"])
        .sort_values(["industry", "date"])
        .reset_index(drop=True)
    )
    return sector_daily


def build_market_daily(df: pd.DataFrame) -> pd.DataFrame:
    market_daily = (
        df.groupby("date", as_index=False)
        .agg(
            daily_return=("analysis_return", "mean"),
            volume=("volume", "sum"),
            turnover_cr=("turnover_cr", "sum"),
            deliverable_percent=("deliverable_percent", "mean"),
            stock_count=("source_symbol", "nunique"),
        )
        .dropna(subset=["daily_return"])
        .sort_values("date")
        .reset_index(drop=True)
    )
    return market_daily


def compute_correlation_analysis(df: pd.DataFrame, stock_summary: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    daily_data = df.copy()
    daily_data["daily_return_for_analysis"] = daily_data["analysis_return"]
    for spec in CORRELATION_SPECS:
        frame = daily_data if spec["scope"] == "daily_observation" else stock_summary
        x_column = "daily_return_for_analysis" if spec["x"] == "daily_return" and spec["scope"] == "daily_observation" else spec["x"]
        y_column = "daily_return_for_analysis" if spec["y"] == "daily_return" and spec["scope"] == "daily_observation" else spec["y"]
        sample = frame[[x_column, y_column]].dropna()
        pearson = stats.pearsonr(sample[x_column], sample[y_column])
        spearman = stats.spearmanr(sample[x_column], sample[y_column], nan_policy="omit")
        rows.append(
            {
                "analysis_type": "correlation",
                "analysis_name": spec["analysis_name"],
                "scope": spec["scope"],
                "test_name": "Pearson correlation",
                "metric_1": spec["x"],
                "metric_2": spec["y"],
                "n_obs": int(sample.shape[0]),
                "statistic": pearson.statistic,
                "p_value": pearson.pvalue,
                "effect_size": pearson.statistic,
                "secondary_test_name": "Spearman correlation",
                "secondary_statistic": spearman.statistic,
                "secondary_p_value": spearman.pvalue,
                "null_hypothesis": f"There is no linear relationship between {spec['x']} and {spec['y']}.",
                "alternative_hypothesis": f"There is a linear relationship between {spec['x']} and {spec['y']}.",
                "interpretation": interpret_correlation(pearson.statistic, pearson.pvalue),
            }
        )
    return pd.DataFrame(rows)


def interpret_correlation(coefficient: float, p_value: float) -> str:
    strength = "weak"
    abs_coefficient = abs(coefficient)
    if abs_coefficient >= 0.5:
        strength = "strong"
    elif abs_coefficient >= 0.3:
        strength = "moderate"
    direction = "positive" if coefficient > 0 else "negative"
    significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
    return f"The relationship is {strength}, {direction}, and {significance} at the 5% level."


def compute_hypothesis_tests(stock_summary: pd.DataFrame, sector_daily: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    delivery_cutoff = float(stock_summary["average_delivery_percent"].median())
    high_delivery = stock_summary.loc[
        stock_summary["average_delivery_percent"] >= delivery_cutoff, "average_daily_return"
    ].dropna()
    low_delivery = stock_summary.loc[
        stock_summary["average_delivery_percent"] < delivery_cutoff, "average_daily_return"
    ].dropna()
    high_normality = stats.shapiro(high_delivery)
    low_normality = stats.shapiro(low_delivery)
    equal_variance = stats.levene(high_delivery, low_delivery, center="median")
    use_parametric = high_normality.pvalue > 0.05 and low_normality.pvalue > 0.05
    if use_parametric:
        equal_var = equal_variance.pvalue > 0.05
        delivery_test = stats.ttest_ind(high_delivery, low_delivery, equal_var=equal_var, nan_policy="omit")
        delivery_test_name = "Independent two-sample t-test" if equal_var else "Welch t-test"
    else:
        delivery_test = stats.mannwhitneyu(high_delivery, low_delivery, alternative="two-sided")
        delivery_test_name = "Mann-Whitney U test"
    delivery_effect = _cohens_d(high_delivery, low_delivery)
    rows.append(
        {
            "analysis_type": "hypothesis_test",
            "analysis_name": "high_delivery_vs_low_delivery_returns",
            "scope": "stock_level",
            "test_name": delivery_test_name,
            "metric_1": "average_daily_return",
            "metric_2": "delivery_group",
            "n_obs": int(high_delivery.shape[0] + low_delivery.shape[0]),
            "statistic": delivery_test.statistic,
            "p_value": delivery_test.pvalue,
            "effect_size": delivery_effect,
            "secondary_test_name": "Levene variance test",
            "secondary_statistic": equal_variance.statistic,
            "secondary_p_value": equal_variance.pvalue,
            "null_hypothesis": "High-delivery and low-delivery stocks have the same average daily return.",
            "alternative_hypothesis": "High-delivery and low-delivery stocks have different average daily returns.",
            "group_a_name": "High delivery",
            "group_a_value": high_delivery.mean(),
            "group_a_n": int(high_delivery.shape[0]),
            "group_b_name": "Low delivery",
            "group_b_value": low_delivery.mean(),
            "group_b_n": int(low_delivery.shape[0]),
            "group_cutoff": delivery_cutoff,
            "interpretation": interpret_hypothesis_test(
                delivery_test_name,
                delivery_test.pvalue,
                "There is not enough evidence to say delivery intensity changes average stock-level returns."
                if delivery_test.pvalue >= 0.05
                else "Delivery intensity is associated with a statistically detectable return difference."
            ),
        }
    )

    sector_groups = [group["daily_return"].to_numpy() for _, group in sector_daily.groupby("industry", sort=True)]
    sector_levene = stats.levene(*sector_groups, center="median")
    sector_anova = stats.f_oneway(*sector_groups)
    if sector_levene.pvalue > 0.05:
        sector_test = sector_anova
        sector_test_name = "One-way ANOVA"
    else:
        sector_test = stats.kruskal(*sector_groups)
        sector_test_name = "Kruskal-Wallis test"

    sector_means = (
        sector_daily.groupby("industry", as_index=False)["daily_return"]
        .mean()
        .sort_values("daily_return", ascending=False)
    )
    rows.append(
        {
            "analysis_type": "hypothesis_test",
            "analysis_name": "sector_return_difference_test",
            "scope": "sector_day_level",
            "test_name": sector_test_name,
            "metric_1": "daily_return",
            "metric_2": "industry",
            "n_obs": int(sector_daily.shape[0]),
            "statistic": sector_test.statistic,
            "p_value": sector_test.pvalue,
            "effect_size": np.nan,
            "secondary_test_name": "One-way ANOVA" if sector_test_name != "One-way ANOVA" else "Levene variance test",
            "secondary_statistic": sector_anova.statistic if sector_test_name != "One-way ANOVA" else sector_levene.statistic,
            "secondary_p_value": sector_anova.pvalue if sector_test_name != "One-way ANOVA" else sector_levene.pvalue,
            "null_hypothesis": "Sector return distributions are the same across industries.",
            "alternative_hypothesis": "At least one sector has a different return distribution.",
            "group_a_name": "Top mean-return sector",
            "group_a_value": sector_means.iloc[0]["daily_return"],
            "group_a_n": int(sector_daily.loc[sector_daily["industry"] == sector_means.iloc[0]["industry"]].shape[0]),
            "group_b_name": "Bottom mean-return sector",
            "group_b_value": sector_means.iloc[-1]["daily_return"],
            "group_b_n": int(sector_daily.loc[sector_daily["industry"] == sector_means.iloc[-1]["industry"]].shape[0]),
            "group_cutoff": np.nan,
            "interpretation": interpret_hypothesis_test(
                sector_test_name,
                sector_test.pvalue,
                "Sector return dispersion is statistically detectable, but the test reflects distribution differences as much as mean differences."
                if sector_test.pvalue < 0.05
                else "Sector means are not cleanly separated enough to support a strong statistical difference claim."
            ),
        }
    )

    return pd.DataFrame(rows)


def interpret_hypothesis_test(test_name: str, p_value: float, evidence_statement: str) -> str:
    if p_value < 0.05:
        return f"{test_name} rejects the null hypothesis at the 5% level. {evidence_statement}"
    return f"{test_name} does not reject the null hypothesis at the 5% level. {evidence_statement}"


def build_risk_summary(stock_summary: pd.DataFrame) -> pd.DataFrame:
    risk_summary = stock_summary.copy()
    risk_summary["drawdown_risk_rank"] = _percentile_rank(-risk_summary["max_drawdown_percent"])
    risk_summary["downside_risk_rank"] = _percentile_rank(risk_summary["downside_volatility_percent"])
    risk_summary["var_risk_rank"] = _percentile_rank(risk_summary["historical_var_95_percent"])
    risk_summary["cvar_risk_rank"] = _percentile_rank(risk_summary["historical_cvar_95_percent"])
    risk_summary["volatility_risk_rank"] = _percentile_rank(risk_summary["volatility_percent"])
    risk_summary["risk_score"] = (
        0.25 * risk_summary["volatility_risk_rank"]
        + 0.25 * risk_summary["drawdown_risk_rank"]
        + 0.25 * risk_summary["downside_risk_rank"]
        + 0.25 * risk_summary["var_risk_rank"]
    )
    risk_rank = risk_summary["risk_score"].rank(method="first")
    risk_summary["risk_bucket"] = pd.qcut(risk_rank, q=3, labels=["Low", "Medium", "High"])
    risk_summary = risk_summary.sort_values(
        ["risk_score", "historical_var_95_percent"],
        ascending=[False, False],
    ).reset_index(drop=True)
    columns = [
        "symbol",
        "company_name",
        "industry",
        "annualized_return_percent",
        "volatility_percent",
        "max_drawdown_percent",
        "downside_volatility_percent",
        "historical_var_95_percent",
        "historical_cvar_95_percent",
        "risk_adjusted_return",
        "liquidity_score",
        "risk_score",
        "risk_bucket",
    ]
    return risk_summary[columns]


def build_segments(stock_summary: pd.DataFrame, risk_summary: pd.DataFrame) -> pd.DataFrame:
    segment_df = stock_summary.merge(
        risk_summary[["symbol", "risk_score", "risk_bucket"]],
        on="symbol",
        how="left",
    )
    feature_columns = [
        "annualized_return_percent",
        "risk_adjusted_return",
        "liquidity_score",
        "average_delivery_percent",
        "volatility_percent",
        "max_drawdown_percent",
        "downside_volatility_percent",
        "historical_var_95_percent",
        "average_turnover_cr",
        "average_volume",
    ]
    for column in feature_columns:
        segment_df[f"{column}_rank"] = _percentile_rank(segment_df[column])
    segment_df["stable_score"] = (
        0.28 * segment_df["annualized_return_percent_rank"]
        + 0.24 * segment_df["risk_adjusted_return_rank"]
        + 0.16 * (100 - segment_df["volatility_percent_rank"])
        + 0.16 * segment_df["average_delivery_percent_rank"]
        + 0.16 * segment_df["max_drawdown_percent_rank"]
    )
    segment_df["growth_risk_score"] = (
        0.35 * segment_df["annualized_return_percent_rank"]
        + 0.25 * segment_df["volatility_percent_rank"]
        + 0.20 * segment_df["historical_var_95_percent_rank"]
        + 0.20 * segment_df["downside_volatility_percent_rank"]
    )
    segment_df["liquid_trading_score"] = (
        0.45 * segment_df["liquidity_score_rank"]
        + 0.30 * segment_df["average_turnover_cr_rank"]
        + 0.25 * segment_df["average_volume_rank"]
    )
    segment_df["weak_score"] = (
        0.35 * (100 - segment_df["annualized_return_percent_rank"])
        + 0.30 * (100 - segment_df["risk_adjusted_return_rank"])
        + 0.20 * _percentile_rank(-segment_df["max_drawdown_percent"])
        + 0.15 * segment_df["historical_var_95_percent_rank"]
    )
    segment_df["defensive_score"] = (
        0.30 * (100 - segment_df["volatility_percent_rank"])
        + 0.30 * (100 - segment_df["downside_volatility_percent_rank"])
        + 0.20 * (100 - segment_df["historical_var_95_percent_rank"])
        + 0.20 * segment_df["average_delivery_percent_rank"]
    )
    score_columns = list(SEGMENT_LABELS)
    segment_df["dominant_score_column"] = segment_df[score_columns].idxmax(axis=1)
    segment_df["segment"] = segment_df["dominant_score_column"].map(SEGMENT_LABELS)
    segment_df["segment_score"] = segment_df[score_columns].max(axis=1)
    segment_df["segment_rationale"] = segment_df.apply(segment_rationale, axis=1)
    segment_df = segment_df.sort_values(
        ["segment", "segment_score", "annualized_return_percent"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    output_columns = [
        "symbol",
        "company_name",
        "industry",
        "segment",
        "segment_score",
        "annualized_return_percent",
        "volatility_percent",
        "risk_adjusted_return",
        "liquidity_score",
        "average_delivery_percent",
        "max_drawdown_percent",
        "downside_volatility_percent",
        "historical_var_95_percent",
        "historical_cvar_95_percent",
        "risk_bucket",
        "stable_score",
        "growth_risk_score",
        "liquid_trading_score",
        "weak_score",
        "defensive_score",
        "segment_rationale",
    ]
    return segment_df[output_columns]


def segment_rationale(row: pd.Series) -> str:
    if row["segment"] == "Stable Compounders":
        return (
            f"High return quality ({row['annualized_return_percent']:.2f}% annualized) with solid risk-adjusted "
            f"performance ({row['risk_adjusted_return']:.2f}) and manageable drawdown ({row['max_drawdown_percent']:.2f}%)."
        )
    if row["segment"] == "High Growth High Risk":
        return (
            f"Growth remains attractive ({row['annualized_return_percent']:.2f}% annualized), but volatility "
            f"({row['volatility_percent']:.2f}%) and left-tail risk (VaR {row['historical_var_95_percent']:.2f}%) are elevated."
        )
    if row["segment"] == "Liquid Trading Candidates":
        return (
            f"Execution profile is strong with liquidity score {row['liquidity_score']:.2f}, making the stock easier "
            f"to trade even when return quality is mixed."
        )
    if row["segment"] == "Weak Risk-Return Candidates":
        return (
            f"Returns are weak relative to risk, with risk-adjusted return {row['risk_adjusted_return']:.2f} and "
            f"drawdown {row['max_drawdown_percent']:.2f}%."
        )
    return (
        f"Volatility ({row['volatility_percent']:.2f}%) and downside risk ({row['downside_volatility_percent']:.2f}%) "
        f"sit toward the safer end of the universe."
    )


def build_trend_analysis(market_daily: pd.DataFrame, sector_daily: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    market_trend = market_daily.copy()
    market_trend["market_index"] = (1 + market_trend["daily_return"].fillna(0)).cumprod() * 100
    market_trend["ma_20"] = market_trend["market_index"].rolling(20).mean()
    market_trend["ma_60"] = market_trend["market_index"].rolling(60).mean()
    market_trend["trend_signal"] = market_trend.apply(
        lambda row: classify_trend(row["ma_20"], row["ma_60"]),
        axis=1,
    )

    sector_rows: List[Dict[str, object]] = []
    for industry, group in sector_daily.groupby("industry", sort=True):
        sector_group = group.sort_values("date").copy()
        sector_group["sector_index"] = (1 + sector_group["daily_return"].fillna(0)).cumprod() * 100
        sector_group["ma_20"] = sector_group["sector_index"].rolling(20).mean()
        sector_group["ma_60"] = sector_group["sector_index"].rolling(60).mean()
        latest = sector_group.iloc[-1]
        sector_rows.append(
            {
                "industry": industry,
                "latest_date": latest["date"].date().isoformat(),
                "latest_index": latest["sector_index"],
                "ma_20": latest["ma_20"],
                "ma_60": latest["ma_60"],
                "ma_gap_percent": (latest["ma_20"] / latest["ma_60"] - 1) * 100 if latest["ma_60"] else np.nan,
                "trend_signal": classify_trend(latest["ma_20"], latest["ma_60"]),
                "observation_count": int(sector_group.shape[0]),
            }
        )
    sector_trend = pd.DataFrame(sector_rows).sort_values("ma_gap_percent", ascending=False).reset_index(drop=True)
    return {"market_trend": market_trend, "sector_trend": sector_trend}


def classify_trend(short_ma: float, long_ma: float) -> str:
    if pd.isna(short_ma) or pd.isna(long_ma) or long_ma == 0:
        return "Insufficient history"
    gap = short_ma / long_ma - 1
    if gap > 0.005:
        return "Uptrend"
    if gap < -0.005:
        return "Downtrend"
    return "Sideways"


def build_recommendation_evidence(
    segments: pd.DataFrame,
    risk_summary: pd.DataFrame,
    sector_table: pd.DataFrame | None,
    hypothesis_tests: pd.DataFrame,
    trend_analysis: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    market_trend = trend_analysis["market_trend"]
    sector_trend = trend_analysis["sector_trend"]
    latest_market_trend = market_trend.iloc[-1]

    stable_names = (
        segments.loc[segments["segment"] == "Stable Compounders"]
        .sort_values("segment_score", ascending=False)
        .head(3)["symbol"]
        .tolist()
    )
    growth_names = (
        segments.loc[segments["segment"] == "High Growth High Risk"]
        .sort_values("segment_score", ascending=False)
        .head(3)["symbol"]
        .tolist()
    )
    liquid_names = (
        segments.loc[segments["segment"] == "Liquid Trading Candidates"]
        .sort_values("liquidity_score", ascending=False)
        .head(3)["symbol"]
        .tolist()
    )
    defensive_names = (
        segments.loc[
            (segments["segment"] == "Defensive / Low Volatility")
            & (segments["annualized_return_percent"] > 0)
        ]
        .sort_values("defensive_score", ascending=False)
        .head(3)["symbol"]
        .tolist()
    )
    weak_names = (
        segments.loc[segments["segment"] == "Weak Risk-Return Candidates"]
        .sort_values("weak_score", ascending=False)
        .head(3)["symbol"]
        .tolist()
    )

    sector_test = hypothesis_tests.loc[
        hypothesis_tests["analysis_name"] == "sector_return_difference_test"
    ].iloc[0]
    delivery_test = hypothesis_tests.loc[
        hypothesis_tests["analysis_name"] == "high_delivery_vs_low_delivery_returns"
    ].iloc[0]

    sector_leaders = []
    if sector_table is not None and "opportunity_score" in sector_table.columns:
        sector_leaders = (
            sector_table.sort_values("opportunity_score", ascending=False)
            .head(2)["industry"]
            .tolist()
        )
    if not sector_leaders:
        sector_leaders = sector_trend.head(2)["industry"].tolist()

    recommendation_rows = [
        {
            "recommendation_id": "R1",
            "theme": "Core Compounder Basket",
            "insight": "A small set of names combines strong annualized returns with better-than-average risk efficiency.",
            "statistical_evidence": (
                f"Top stable-compounder candidates {', '.join(stable_names)} rank highest on the rule-based "
                "compounder score built from annualized return, risk-adjusted return, lower volatility, delivery "
                "strength, and shallower drawdowns."
            ),
            "recommended_action": "Use these stocks as the core shortlist for long-horizon allocation discussions.",
            "expected_business_impact": "Improves the odds of holding names with both wealth creation and better risk discipline.",
            "feasibility_note": "High feasibility because the basket uses existing KPI outputs and does not require new data sources.",
        },
        {
            "recommendation_id": "R2",
            "theme": "Risk-Capped Growth Sleeve",
            "insight": "Growth-heavy names can add upside, but their left-tail risk is materially higher than the market median.",
            "statistical_evidence": (
                f"High-growth/high-risk names {', '.join(growth_names)} score well on return but also carry elevated "
                "volatility, VaR, and downside-volatility measures in the risk summary."
            ),
            "recommended_action": "Treat the segment as a capped tactical sleeve with explicit position and stop-loss rules.",
            "expected_business_impact": "Keeps upside optionality while reducing the chance that one high-beta name dominates portfolio risk.",
            "feasibility_note": "Operationally simple because the segment is already tagged in `stock_segments.csv`.",
        },
        {
            "recommendation_id": "R3",
            "theme": "Execution-Friendly Trading List",
            "insight": "The most liquid names remain the easiest to trade even when return quality is mixed.",
            "statistical_evidence": (
                f"Stocks such as {', '.join(liquid_names)} sit at the top of the liquidity-score distribution, while the "
                "liquidity-to-risk-adjusted-return correlation stays weak, so liquidity should be used as an execution filter rather than a performance signal."
            ),
            "recommended_action": "Use the liquid segment as the default short-term trading watchlist, but pair it with return-quality filters.",
            "expected_business_impact": "Improves execution practicality and lowers slippage risk for active monitoring in Tableau.",
            "feasibility_note": "Very feasible because liquidity scores already exist and are easy to expose in filters.",
        },
        {
            "recommendation_id": "R4",
            "theme": "Defensive Rotation Rule",
            "insight": "When broad momentum softens, lower-volatility names become more useful as ballast than as pure alpha plays.",
            "statistical_evidence": (
                f"The market closes the sample with a {latest_market_trend['trend_signal'].lower()} signal from the 20-day vs 60-day moving average, "
                f"while defensive names such as {', '.join(defensive_names)} show lower volatility and downside-volatility profiles."
            ),
            "recommended_action": "Use a simple moving-average regime filter to tilt watchlists toward the defensive segment during softer market phases.",
            "expected_business_impact": "Can reduce portfolio swings during weaker momentum regimes without fully exiting the market.",
            "feasibility_note": "Moderate feasibility because it needs only rolling averages that are already computed in the notebook.",
        },
        {
            "recommendation_id": "R5",
            "theme": "Deprioritize Weak Risk-Return Areas",
            "insight": "Some names and sectors fail to compensate investors for the risk they took over the sample window.",
            "statistical_evidence": (
                f"Weak candidates such as {', '.join(weak_names)} have poor risk-adjusted returns and deep drawdowns. "
                f"The sector comparison test ({sector_test['test_name']}, p={sector_test['p_value']:.4f}) also suggests sector return distributions are not uniform, "
                f"while the high-vs-low delivery return test remains non-significant (p={delivery_test['p_value']:.4f}), so conviction proxies alone should not drive selection. "
                f"Top sector leaders currently include {', '.join(sector_leaders)}."
            ),
            "recommended_action": "Underweight or explicitly flag weak risk-return candidates and prioritize sectors with stronger opportunity or trend evidence.",
            "expected_business_impact": "Reduces false positives from chasing liquidity or delivery strength without return support.",
            "feasibility_note": "High feasibility because the rule can be encoded directly in Tableau filters and report callouts.",
        },
    ]
    return pd.DataFrame(recommendation_rows)


def create_charts(
    correlations: pd.DataFrame,
    risk_summary: pd.DataFrame,
    segments: pd.DataFrame,
    sector_daily: pd.DataFrame,
    output_dir: Path | None = None,
) -> Dict[str, Path]:
    repo_root = resolve_repo_root()
    charts_dir = output_dir or repo_root / "outputs" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="deep")
    chart_paths: Dict[str, Path] = {}

    corr_plot = correlations[["analysis_name", "effect_size"]].copy()
    corr_plot["label"] = corr_plot["analysis_name"].map(
        {
            "daily_return_vs_volume": "Daily Return vs Volume",
            "daily_return_vs_turnover": "Daily Return vs Turnover",
            "daily_return_vs_delivery_percent": "Daily Return vs Delivery %",
            "volatility_vs_return": "Volatility vs Annualized Return",
            "liquidity_vs_risk_adjusted_return": "Liquidity vs Risk-Adjusted Return",
        }
    )
    corr_plot = corr_plot.set_index("label")[["effect_size"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(
        corr_plot,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        center=0,
        cbar_kws={"label": "Pearson r"},
        ax=ax,
    )
    ax.set_title("Target Correlation Check", fontsize=14, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    chart_paths["correlation_heatmap"] = charts_dir / CHART_FILENAMES["correlation_heatmap"]
    fig.tight_layout()
    fig.savefig(chart_paths["correlation_heatmap"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = sns.scatterplot(
        data=segments,
        x="volatility_percent",
        y="annualized_return_percent",
        hue="segment",
        size="liquidity_score",
        sizes=(80, 320),
        alpha=0.85,
        ax=ax,
    )
    for _, row in segments.sort_values("segment_score", ascending=False).head(8).iterrows():
        ax.text(row["volatility_percent"], row["annualized_return_percent"], row["symbol"], fontsize=8)
    ax.axhline(0, color="black", linewidth=1, alpha=0.4)
    ax.set_title("Risk-Return Positioning by Statistical Segment", fontsize=14, pad=12)
    ax.set_xlabel("Annualized Volatility (%)")
    ax.set_ylabel("Annualized Return (%)")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    scatter.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    chart_paths["risk_return_segments"] = charts_dir / CHART_FILENAMES["risk_return_segments"]
    fig.tight_layout()
    fig.savefig(chart_paths["risk_return_segments"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    worst_drawdowns = risk_summary.nsmallest(10, "max_drawdown_percent").sort_values("max_drawdown_percent")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(worst_drawdowns["symbol"], worst_drawdowns["max_drawdown_percent"], color="#c44e52")
    ax.axvline(0, color="black", linewidth=1, alpha=0.4)
    ax.set_title("Top 10 Worst Max Drawdowns", fontsize=14, pad=12)
    ax.set_xlabel("Max Drawdown (%)")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    chart_paths["max_drawdown_top10"] = charts_dir / CHART_FILENAMES["max_drawdown_top10"]
    fig.tight_layout()
    fig.savefig(chart_paths["max_drawdown_top10"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    sector_plot = sector_daily.copy()
    ordering = (
        sector_plot.groupby("industry")["daily_return"]
        .median()
        .sort_values(ascending=False)
        .index
    )
    fig, ax = plt.subplots(figsize=(13, 7))
    sns.boxplot(
        data=sector_plot,
        x="daily_return",
        y="industry",
        order=ordering,
        showfliers=False,
        color="#4c72b0",
        ax=ax,
    )
    ax.axvline(0, color="black", linewidth=1, alpha=0.4)
    ax.set_title("Daily Return Distribution by Sector", fontsize=14, pad=12)
    ax.set_xlabel("Equal-Weighted Daily Return")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    chart_paths["sector_statistical_comparison"] = charts_dir / CHART_FILENAMES["sector_statistical_comparison"]
    fig.tight_layout()
    fig.savefig(chart_paths["sector_statistical_comparison"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    return chart_paths


def save_tables(
    correlations: pd.DataFrame,
    hypothesis_tests: pd.DataFrame,
    risk_summary: pd.DataFrame,
    segments: pd.DataFrame,
    recommendation_evidence: pd.DataFrame,
    output_dir: Path | None = None,
) -> Dict[str, Path]:
    repo_root = resolve_repo_root()
    tables_dir = output_dir or repo_root / "outputs" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    statistical_test_results = pd.concat([correlations, hypothesis_tests], ignore_index=True)

    table_paths = {
        "statistical_test_results": tables_dir / "statistical_test_results.csv",
        "risk_summary": tables_dir / "risk_summary.csv",
        "stock_segments": tables_dir / "stock_segments.csv",
        "recommendation_evidence": tables_dir / "recommendation_evidence.csv",
    }
    statistical_test_results.to_csv(table_paths["statistical_test_results"], index=False)
    risk_summary.to_csv(table_paths["risk_summary"], index=False)
    segments.to_csv(table_paths["stock_segments"], index=False)
    recommendation_evidence.to_csv(table_paths["recommendation_evidence"], index=False)
    return table_paths


def run_statistical_pipeline() -> Dict[str, object]:
    repo_root = resolve_repo_root()
    df = load_cleaned_data()
    stock_summary = build_stock_summary(df)
    sector_daily = build_sector_daily(df)
    market_daily = build_market_daily(df)
    existing_stock_kpis = load_optional_table(repo_root / "outputs" / "tables" / "stock_kpis.csv")
    existing_sector_kpis = load_optional_table(repo_root / "outputs" / "tables" / "sector_kpis.csv")
    correlations = compute_correlation_analysis(df, stock_summary)
    hypothesis_tests = compute_hypothesis_tests(stock_summary, sector_daily)
    risk_summary = build_risk_summary(stock_summary)
    segments = build_segments(stock_summary, risk_summary)
    trend_analysis = build_trend_analysis(market_daily, sector_daily)
    recommendation_evidence = build_recommendation_evidence(
        segments,
        risk_summary,
        existing_sector_kpis,
        hypothesis_tests,
        trend_analysis,
    )
    table_paths = save_tables(
        correlations,
        hypothesis_tests,
        risk_summary,
        segments,
        recommendation_evidence,
    )
    chart_paths = create_charts(correlations, risk_summary, segments, sector_daily)
    return {
        "data": df,
        "stock_summary": stock_summary,
        "sector_daily": sector_daily,
        "market_daily": market_daily,
        "existing_stock_kpis": existing_stock_kpis,
        "existing_sector_kpis": existing_sector_kpis,
        "correlations": correlations,
        "hypothesis_tests": hypothesis_tests,
        "risk_summary": risk_summary,
        "segments": segments,
        "trend_analysis": trend_analysis,
        "recommendation_evidence": recommendation_evidence,
        "table_paths": table_paths,
        "chart_paths": chart_paths,
    }


if __name__ == "__main__":
    results = run_statistical_pipeline()
    print("Generated statistical tables:")
    for name, path in results["table_paths"].items():
        print(f"- {name}: {path}")
    print("\nGenerated statistical charts:")
    for name, path in results["chart_paths"].items():
        print(f"- {name}: {path}")
