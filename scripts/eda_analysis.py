from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


TRADING_DAYS_PER_YEAR = 252
COVID_WINDOWS = [
    ("Pre-COVID Baseline", "2019-01-01", "2020-02-14"),
    ("Crash Phase", "2020-02-17", "2020-03-31"),
    ("Recovery Phase", "2020-04-01", "2020-12-31"),
]
CHART_FILENAMES = {
    "yearly_market_trend": "yearly_market_trend.png",
    "top_10_stocks_return": "top_10_stocks_return.png",
    "sector_return_comparison": "sector_return_comparison.png",
    "sector_volatility_comparison": "sector_volatility_comparison.png",
    "volume_turnover_trend": "volume_turnover_trend.png",
    "delivery_percent_trend": "delivery_percent_trend.png",
    "risk_return_scatter": "risk_return_scatter.png",
    "covid_crash_recovery": "covid_crash_recovery.png",
}


def resolve_repo_root() -> Path:
    repo_root = Path.cwd().resolve()
    if (repo_root / "scripts").exists():
        return repo_root
    if (repo_root.parent / "scripts").exists():
        return repo_root.parent
    raise FileNotFoundError("Could not resolve the repository root from the current working directory.")


def load_cleaned_data(data_path: Path | None = None) -> pd.DataFrame:
    repo_root = resolve_repo_root()
    target_path = data_path or repo_root / "data" / "processed" / "nifty50_cleaned.csv"
    if not target_path.exists():
        raise FileNotFoundError(
            "Processed data is missing. Run notebooks/02_cleaning.ipynb or python scripts/etl_pipeline.py "
            "to create data/processed/nifty50_cleaned.csv before running the EDA notebook."
        )

    df = pd.read_csv(target_path, parse_dates=["date"])
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    for column in ["missing_price_flag", "missing_volume_flag", "invalid_ohlc_flag", "outlier_return_flag"]:
        if column in df.columns and df[column].dtype == object:
            df[column] = df[column].astype(str).str.lower().eq("true")
    df["analysis_return"] = df["daily_return"].where(~df["outlier_return_flag"].fillna(False))
    return df


def summarize_dataset(df: pd.DataFrame) -> pd.Series:
    reported_columns = int(df.shape[1] - (1 if "analysis_return" in df.columns else 0))
    summary = {
        "rows": int(df.shape[0]),
        "columns": reported_columns,
        "date_start": df["date"].min().date().isoformat(),
        "date_end": df["date"].max().date().isoformat(),
        "stock_count": int(df["source_symbol"].nunique()),
        "row_level_symbol_count": int(df["symbol"].nunique()),
        "sector_count": int(df["industry"].nunique(dropna=True)),
        "industry_count": int(df["industry"].nunique(dropna=True)),
        "company_count": int(df["company_name"].nunique(dropna=True)),
        "missing_delivery_percent_rows": int(df["deliverable_percent"].isna().sum()),
        "missing_trades_rows": int(df["trades"].isna().sum()),
    }
    return pd.Series(summary, name="dataset_summary")


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


def build_market_daily(df: pd.DataFrame) -> pd.DataFrame:
    market_daily = (
        df.groupby("date", as_index=False)
        .agg(
            daily_return=("analysis_return", "mean"),
            volume=("volume", "sum"),
            turnover_cr=("turnover_cr", "sum"),
            deliverable_percent=("deliverable_percent", "mean"),
            vwap_gap=("vwap_gap", "mean"),
            stock_count=("source_symbol", "nunique"),
            sector_count=("industry", "nunique"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    market_daily["year"] = market_daily["date"].dt.year
    return market_daily


def build_sector_daily(df: pd.DataFrame) -> pd.DataFrame:
    sector_daily = (
        df.groupby(["industry", "date"], as_index=False)
        .agg(
            daily_return=("analysis_return", "mean"),
            volume=("volume", "sum"),
            turnover_cr=("turnover_cr", "sum"),
            deliverable_percent=("deliverable_percent", "mean"),
            vwap_gap=("vwap_gap", "mean"),
            stock_count=("source_symbol", "nunique"),
        )
        .sort_values(["industry", "date"])
        .reset_index(drop=True)
    )
    sector_daily["year"] = sector_daily["date"].dt.year
    return sector_daily


def build_stock_kpis(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source_symbol, group in df.groupby("source_symbol", sort=True):
        group = group.sort_values("date")
        metrics = _return_metrics(group["analysis_return"])
        rows.append(
            {
                "symbol": source_symbol,
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
            }
        )

    stock_kpis = pd.DataFrame(rows)
    stock_kpis["liquidity_score"] = (
        0.5 * _percentile_rank(stock_kpis["average_volume"])
        + 0.5 * _percentile_rank(stock_kpis["average_turnover_cr"])
    )
    stock_kpis["investor_confidence_score"] = (
        0.6 * _percentile_rank(stock_kpis["average_delivery_percent"])
        + 0.25 * _percentile_rank(stock_kpis["close_above_vwap_ratio"])
        + 0.15 * _percentile_rank(stock_kpis["positive_return_day_ratio"])
    )
    stock_kpis["opportunity_score"] = (
        0.3 * _percentile_rank(stock_kpis["annualized_return_percent"])
        + 0.25 * _percentile_rank(stock_kpis["risk_adjusted_return"])
        + 0.15 * _percentile_rank(stock_kpis["max_drawdown_percent"])
        + 0.15 * _percentile_rank(stock_kpis["liquidity_score"])
        + 0.15 * _percentile_rank(stock_kpis["investor_confidence_score"])
    )

    stock_kpis = stock_kpis.sort_values(
        ["opportunity_score", "annualized_return_percent"],
        ascending=[False, False],
    ).reset_index(drop=True)
    return stock_kpis


def build_sector_kpis(df: pd.DataFrame, sector_daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sector_yearly_rows = []
    for industry, group in sector_daily.groupby("industry", sort=True):
        group = group.sort_values("date")
        metrics = _return_metrics(group["daily_return"])
        source_rows = df[df["industry"] == industry]

        for year, year_group in group.groupby("year", sort=True):
            sector_yearly_rows.append(
                {
                    "industry": industry,
                    "year": int(year),
                    "annual_return_percent": _return_metrics(year_group["daily_return"])[
                        "cumulative_return_percent"
                    ],
                }
            )

        rows.append(
            {
                "industry": industry,
                "constituent_stock_count": int(source_rows["source_symbol"].nunique()),
                **metrics,
                "average_volume": group["volume"].mean(),
                "average_turnover_cr": group["turnover_cr"].mean(),
                "average_delivery_percent": group["deliverable_percent"].mean() * 100,
                "positive_return_day_ratio": (group["daily_return"] > 0).mean() * 100,
                "close_above_vwap_ratio": (group["vwap_gap"] > 0).mean() * 100,
            }
        )

    sector_kpis = pd.DataFrame(rows)
    sector_yearly = pd.DataFrame(sector_yearly_rows)
    sector_avg_annual = (
        sector_yearly.groupby("industry", as_index=False)["annual_return_percent"]
        .mean()
        .rename(columns={"annual_return_percent": "average_annual_return_percent"})
    )
    sector_kpis = sector_kpis.merge(sector_avg_annual, on="industry", how="left")
    sector_kpis["liquidity_score"] = (
        0.5 * _percentile_rank(sector_kpis["average_volume"])
        + 0.5 * _percentile_rank(sector_kpis["average_turnover_cr"])
    )
    sector_kpis["investor_confidence_score"] = (
        0.6 * _percentile_rank(sector_kpis["average_delivery_percent"])
        + 0.25 * _percentile_rank(sector_kpis["close_above_vwap_ratio"])
        + 0.15 * _percentile_rank(sector_kpis["positive_return_day_ratio"])
    )
    sector_kpis["opportunity_score"] = (
        0.3 * _percentile_rank(sector_kpis["annualized_return_percent"])
        + 0.25 * _percentile_rank(sector_kpis["risk_adjusted_return"])
        + 0.15 * _percentile_rank(sector_kpis["max_drawdown_percent"])
        + 0.15 * _percentile_rank(sector_kpis["liquidity_score"])
        + 0.15 * _percentile_rank(sector_kpis["investor_confidence_score"])
    )
    sector_kpis = sector_kpis.sort_values(
        ["opportunity_score", "annualized_return_percent"],
        ascending=[False, False],
    ).reset_index(drop=True)
    return sector_kpis


def build_yearly_market_summary(market_daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, group in market_daily.groupby("year", sort=True):
        metrics = _return_metrics(group["daily_return"])
        rows.append(
            {
                "year": int(year),
                **metrics,
                "average_volume": group["volume"].mean(),
                "average_turnover_cr": group["turnover_cr"].mean(),
                "average_delivery_percent": group["deliverable_percent"].mean() * 100,
                "average_vwap_gap": group["vwap_gap"].mean(),
                "average_stock_count": group["stock_count"].mean(),
                "average_sector_count": group["sector_count"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def build_covid_period_summary(market_daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period_name, start_date, end_date in COVID_WINDOWS:
        mask = (market_daily["date"] >= start_date) & (market_daily["date"] <= end_date)
        group = market_daily.loc[mask].copy()
        metrics = _return_metrics(group["daily_return"])
        rows.append(
            {
                "period": period_name,
                "start_date": start_date,
                "end_date": end_date,
                **metrics,
                "average_volume": group["volume"].mean(),
                "average_turnover_cr": group["turnover_cr"].mean(),
                "average_delivery_percent": group["deliverable_percent"].mean() * 100,
                "average_vwap_gap": group["vwap_gap"].mean(),
            }
        )
    return pd.DataFrame(rows)


def build_analysis_artifacts(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    market_daily = build_market_daily(df)
    sector_daily = build_sector_daily(df)
    stock_kpis = build_stock_kpis(df)
    sector_kpis = build_sector_kpis(df, sector_daily)
    yearly_market_summary = build_yearly_market_summary(market_daily)
    covid_period_summary = build_covid_period_summary(market_daily)
    yearly_sector_returns = (
        sector_daily.groupby(["industry", "year"], as_index=False)["daily_return"]
        .apply(lambda s: _return_metrics(s)["cumulative_return_percent"])
        .rename(columns={"daily_return": "annual_return_percent"})
    )
    top_bottom_stocks = pd.concat(
        [
            stock_kpis.nlargest(5, "cumulative_return_percent"),
            stock_kpis.nsmallest(5, "cumulative_return_percent"),
        ],
        ignore_index=True,
    ).drop_duplicates("symbol")
    correlation_table = (
        df[["analysis_return", "volume", "turnover_cr", "deliverable_percent", "vwap_gap"]]
        .rename(columns={"analysis_return": "daily_return"})
        .corr()
    )
    vwap_summary = (
        df.assign(close_above_vwap=df["vwap_gap"] > 0)
        .groupby("source_symbol", as_index=False)
        .agg(
            average_vwap_gap=("vwap_gap", "mean"),
            close_above_vwap_ratio=("close_above_vwap", "mean"),
        )
        .rename(columns={"source_symbol": "symbol"})
        .sort_values("average_vwap_gap", ascending=False)
        .reset_index(drop=True)
    )

    return {
        "dataset_summary": summarize_dataset(df),
        "market_daily": market_daily,
        "sector_daily": sector_daily,
        "stock_kpis": stock_kpis,
        "sector_kpis": sector_kpis,
        "yearly_market_summary": yearly_market_summary,
        "covid_period_summary": covid_period_summary,
        "yearly_sector_returns": yearly_sector_returns,
        "top_bottom_stocks": top_bottom_stocks,
        "correlation_table": correlation_table,
        "vwap_summary": vwap_summary,
    }


def _format_axes(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, fontsize=14, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def create_charts(artifacts: Dict[str, pd.DataFrame], output_dir: Path | None = None) -> Dict[str, Path]:
    repo_root = resolve_repo_root()
    charts_dir = output_dir or repo_root / "outputs" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", palette="deep")
    chart_paths: Dict[str, Path] = {}

    yearly_market_summary = artifacts["yearly_market_summary"]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=yearly_market_summary, x="year", y="cumulative_return_percent", marker="o", linewidth=2.5, ax=ax)
    ax.axhline(0, color="black", linewidth=1, alpha=0.5)
    _format_axes(ax, "Equal-Weighted Market Return by Year", "Year", "Annual Market Return (%)")
    chart_paths["yearly_market_trend"] = charts_dir / CHART_FILENAMES["yearly_market_trend"]
    fig.tight_layout()
    fig.savefig(chart_paths["yearly_market_trend"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    top_bottom = artifacts["top_bottom_stocks"].copy()
    top_bottom["label"] = top_bottom["symbol"] + " (" + top_bottom["industry"] + ")"
    top_bottom = top_bottom.sort_values("cumulative_return_percent")
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = np.where(top_bottom["cumulative_return_percent"] >= 0, "#2a9d8f", "#e76f51")
    ax.barh(top_bottom["label"], top_bottom["cumulative_return_percent"], color=colors)
    ax.axvline(0, color="black", linewidth=1, alpha=0.5)
    _format_axes(ax, "Top 5 and Bottom 5 Stocks by Cumulative Return", "Cumulative Return (%)", "")
    chart_paths["top_10_stocks_return"] = charts_dir / CHART_FILENAMES["top_10_stocks_return"]
    fig.tight_layout()
    fig.savefig(chart_paths["top_10_stocks_return"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    sector_kpis = artifacts["sector_kpis"].sort_values("average_annual_return_percent", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=sector_kpis, x="average_annual_return_percent", y="industry", hue="industry", dodge=False, palette="viridis", legend=False, ax=ax)
    _format_axes(ax, "Average Annual Return by Sector", "Average Annual Return (%)", "")
    chart_paths["sector_return_comparison"] = charts_dir / CHART_FILENAMES["sector_return_comparison"]
    fig.tight_layout()
    fig.savefig(chart_paths["sector_return_comparison"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    sector_vol = artifacts["sector_kpis"].sort_values("volatility_percent", ascending=False)
    sns.barplot(data=sector_vol, x="volatility_percent", y="industry", hue="industry", dodge=False, palette="magma", legend=False, ax=ax)
    _format_axes(ax, "Annualized Volatility by Sector", "Volatility (%)", "")
    chart_paths["sector_volatility_comparison"] = charts_dir / CHART_FILENAMES["sector_volatility_comparison"]
    fig.tight_layout()
    fig.savefig(chart_paths["sector_volatility_comparison"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    color_volume = "#457b9d"
    color_turnover = "#f4a261"
    ax1.plot(yearly_market_summary["year"], yearly_market_summary["average_volume"], color=color_volume, marker="o", linewidth=2.5)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Average Daily Volume", color=color_volume)
    ax1.tick_params(axis="y", labelcolor=color_volume)
    ax2 = ax1.twinx()
    ax2.plot(yearly_market_summary["year"], yearly_market_summary["average_turnover_cr"], color=color_turnover, marker="s", linewidth=2.5)
    ax2.set_ylabel("Average Daily Turnover (Cr)", color=color_turnover)
    ax2.tick_params(axis="y", labelcolor=color_turnover)
    ax1.set_title("Market Liquidity Trend by Year", fontsize=14, pad=14)
    ax1.grid(axis="y", linestyle="--", alpha=0.25)
    chart_paths["volume_turnover_trend"] = charts_dir / CHART_FILENAMES["volume_turnover_trend"]
    fig.tight_layout()
    fig.savefig(chart_paths["volume_turnover_trend"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=yearly_market_summary, x="year", y="average_delivery_percent", marker="o", linewidth=2.5, color="#1d3557", ax=ax)
    _format_axes(ax, "Average Delivery Percentage by Year", "Year", "Average Delivery (%)")
    chart_paths["delivery_percent_trend"] = charts_dir / CHART_FILENAMES["delivery_percent_trend"]
    fig.tight_layout()
    fig.savefig(chart_paths["delivery_percent_trend"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = sns.scatterplot(
        data=artifacts["stock_kpis"],
        x="volatility_percent",
        y="annualized_return_percent",
        hue="industry",
        size="liquidity_score",
        sizes=(60, 320),
        alpha=0.85,
        ax=ax,
    )
    for _, row in artifacts["stock_kpis"].nlargest(6, "opportunity_score").iterrows():
        ax.text(row["volatility_percent"], row["annualized_return_percent"], row["symbol"], fontsize=8)
    _format_axes(ax, "Risk-Return Positioning of NIFTY Stocks", "Volatility (%)", "Annualized Return (%)")
    scatter.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    chart_paths["risk_return_scatter"] = charts_dir / CHART_FILENAMES["risk_return_scatter"]
    fig.tight_layout()
    fig.savefig(chart_paths["risk_return_scatter"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    covid_daily = artifacts["market_daily"].loc[
        (artifacts["market_daily"]["date"] >= "2020-01-01")
        & (artifacts["market_daily"]["date"] <= "2020-12-31")
    ].copy()
    covid_daily["market_index"] = (1 + covid_daily["daily_return"].fillna(0)).cumprod() * 100
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=covid_daily, x="date", y="market_index", linewidth=2.5, color="#264653", ax=ax)
    ax.axvspan(pd.Timestamp("2020-02-17"), pd.Timestamp("2020-03-31"), color="#e76f51", alpha=0.18)
    ax.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2020-12-31"), color="#2a9d8f", alpha=0.10)
    _format_axes(ax, "2020 Market Crash and Recovery Path", "Date", "Indexed Market Level (2020-01-01 = 100)")
    chart_paths["covid_crash_recovery"] = charts_dir / CHART_FILENAMES["covid_crash_recovery"]
    fig.tight_layout()
    fig.savefig(chart_paths["covid_crash_recovery"], dpi=200, bbox_inches="tight")
    plt.close(fig)

    return chart_paths


def save_tables(artifacts: Dict[str, pd.DataFrame], output_dir: Path | None = None) -> Dict[str, Path]:
    repo_root = resolve_repo_root()
    tables_dir = output_dir or repo_root / "outputs" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    table_paths = {
        "stock_kpis": tables_dir / "stock_kpis.csv",
        "sector_kpis": tables_dir / "sector_kpis.csv",
        "yearly_market_summary": tables_dir / "yearly_market_summary.csv",
        "covid_period_summary": tables_dir / "covid_period_summary.csv",
    }

    artifacts["stock_kpis"].to_csv(table_paths["stock_kpis"], index=False)
    artifacts["sector_kpis"].to_csv(table_paths["sector_kpis"], index=False)
    artifacts["yearly_market_summary"].to_csv(table_paths["yearly_market_summary"], index=False)
    artifacts["covid_period_summary"].to_csv(table_paths["covid_period_summary"], index=False)
    return table_paths


def run_eda_pipeline() -> Dict[str, object]:
    df = load_cleaned_data()
    artifacts = build_analysis_artifacts(df)
    table_paths = save_tables(artifacts)
    chart_paths = create_charts(artifacts)
    return {
        "data": df,
        "artifacts": artifacts,
        "table_paths": table_paths,
        "chart_paths": chart_paths,
    }


if __name__ == "__main__":
    result = run_eda_pipeline()
    print("Generated tables:")
    for name, path in result["table_paths"].items():
        print(f"- {name}: {path}")
    print("\nGenerated charts:")
    for name, path in result["chart_paths"].items():
        print(f"- {name}: {path}")
