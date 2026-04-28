"""
Generate six data-accurate dashboard reference screenshots from the processed
Tableau CSV data sources using matplotlib.

Output directory: tableau/screenshots/
Generated files:
  1. 01_executive_kpi_cards.png
  2. 02_market_trend_view.png
  3. 03_sector_comparison.png
  4. 04_stock_opportunity.png
  5. 05_covid_crash_recovery.png
  6. 06_recommendation_view.png
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tableau", "screenshots")
os.makedirs(OUT, exist_ok=True)

STOCK = pd.read_csv(os.path.join(ROOT, "data/processed/tableau_stock_level.csv"))
SECTOR = pd.read_csv(os.path.join(ROOT, "data/processed/tableau_sector_level.csv"))
TRENDS = pd.read_csv(os.path.join(ROOT, "data/processed/tableau_yearly_trends.csv"))
RISK = pd.read_csv(os.path.join(ROOT, "data/processed/tableau_risk_segments.csv"))
RECO = pd.read_csv(os.path.join(ROOT, "data/processed/tableau_recommendation_view.csv"))

COLORS = {
    "Buy": "#2ca02c",
    "Watch": "#ff7f0e",
    "Trade Candidate": "#1f77b4",
    "Avoid": "#d62728",
}

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#f9f9f9",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 10,
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ── 1. Executive KPI Cards ──────────────────────────────────────────────────
def plot_executive_kpis():
    total_stocks = STOCK["Stock Symbol"].nunique()
    date_min = TRENDS["Date"].min() if "Date" in TRENDS.columns else STOCK["Start Date"].min()
    date_max = TRENDS["Date"].max() if "Date" in TRENDS.columns else STOCK["End Date"].max()
    best_stock = STOCK.loc[STOCK["Annualized Return (%)"].idxmax()]
    best_sector = SECTOR.loc[SECTOR["Annualized Return (%)"].idxmax()]
    highest_risk = RISK.loc[RISK["Risk Score"].idxmax()]
    avg_delivery = STOCK["Average Delivery (%)"].mean()
    avg_turnover = STOCK["Average Turnover (Cr)"].mean()

    kpis = [
        ("Stocks Analyzed", str(total_stocks)),
        ("Date Range", f"{date_min}\nto {date_max}"),
        ("Best Stock", f"{best_stock['Stock Symbol']}\n{best_stock['Annualized Return (%)']:.1f}% ann."),
        ("Best Sector", f"{best_sector['Sector / Industry']}\n{best_sector['Annualized Return (%)']:.1f}% ann."),
        ("Highest Risk", f"{highest_risk['Stock Symbol']}\nScore {highest_risk['Risk Score']:.1f}"),
        ("Avg Delivery %", f"{avg_delivery:.1f}%"),
        ("Avg Turnover", f"{avg_turnover:.0f} Cr"),
    ]

    fig, axes = plt.subplots(1, len(kpis), figsize=(18, 3))
    fig.suptitle("NIFTY-50 Sectoral Performance & Risk Intelligence Dashboard — Executive KPIs",
                 fontsize=13, fontweight="bold", y=1.05)
    for ax, (label, value) in zip(axes, kpis):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(0.5, 0.18, label, ha="center", va="center", fontsize=9, color="#555")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#ccc")
    save(fig, "01_executive_kpi_cards.png")


# ── 2. Market Trend View ────────────────────────────────────────────────────
def plot_market_trend():
    # Use overall/market level rows if available
    if "View Level" in TRENDS.columns:
        market = TRENDS[TRENDS["View Level"].str.lower().str.contains("overall|market", na=False)].copy()
        if market.empty:
            market = TRENDS.copy()
    else:
        market = TRENDS.copy()

    if "Year" in market.columns:
        yearly = market.groupby("Year").agg({
            "Equal Weighted Index": "last" if "Equal Weighted Index" in market.columns else "mean",
            "Volume": "mean",
            "Turnover (Cr)": "mean",
        }).dropna(subset=["Equal Weighted Index"] if "Equal Weighted Index" in market.columns else [])
    else:
        yearly = market

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle("Market Trend View", fontsize=14, fontweight="bold")

    if "Equal Weighted Index" in yearly.columns:
        ax1.plot(yearly.index, yearly["Equal Weighted Index"], color="#1f77b4", linewidth=1.5)
        ax1.set_ylabel("Equal Weighted Index")
        ax1.set_title("Yearly Equal-Weighted Market Index")
    elif "Daily Return" in yearly.columns:
        ax1.plot(yearly.index, yearly["Daily Return"], color="#1f77b4", linewidth=1.5)
        ax1.set_ylabel("Daily Return")
        ax1.set_title("Yearly Average Daily Return")

    if "Volume" in yearly.columns and "Turnover (Cr)" in yearly.columns:
        ax2.bar(yearly.index, yearly["Volume"], color="#2ca02c", alpha=0.6, label="Volume")
        ax2b = ax2.twinx()
        ax2b.plot(yearly.index, yearly["Turnover (Cr)"], color="#d62728", linewidth=1.5, label="Turnover (Cr)")
        ax2.set_ylabel("Volume")
        ax2b.set_ylabel("Turnover (Cr)")
        ax2.set_title("Volume & Turnover Trend")
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax2.set_xlabel("Year")
    fig.tight_layout()
    save(fig, "02_market_trend_view.png")


# ── 3. Sector Comparison ────────────────────────────────────────────────────
def plot_sector_comparison():
    df = SECTOR.sort_values("Annualized Return (%)", ascending=True)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 7))
    fig.suptitle("Sector Comparison View", fontsize=14, fontweight="bold")

    ax1.barh(df["Sector / Industry"], df["Annualized Return (%)"], color="#1f77b4")
    ax1.set_xlabel("Annualized Return (%)")
    ax1.set_title("Return by Sector")

    ax2.barh(df["Sector / Industry"], df["Volatility (%)"], color="#ff7f0e")
    ax2.set_xlabel("Volatility (%)")
    ax2.set_title("Volatility by Sector")

    ax3.barh(df["Sector / Industry"], df["Average Delivery (%)"], color="#2ca02c")
    ax3.set_xlabel("Average Delivery (%)")
    ax3.set_title("Delivery % by Sector")

    fig.tight_layout()
    save(fig, "03_sector_comparison.png")


# ── 4. Stock Opportunity ────────────────────────────────────────────────────
def plot_stock_opportunity():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Stock Opportunity View", fontsize=14, fontweight="bold")

    # Risk-return scatter
    for bucket in RISK["Risk Bucket"].unique():
        subset = RISK[RISK["Risk Bucket"] == bucket]
        ax1.scatter(
            subset["Volatility (%)"],
            subset["Annualized Return (%)"],
            s=subset["Opportunity Score"] * 2,
            alpha=0.65,
            label=bucket,
        )
    ax1.set_xlabel("Volatility (%)")
    ax1.set_ylabel("Annualized Return (%)")
    ax1.set_title("Risk–Return Scatter (size = Opportunity Score)")
    ax1.legend(title="Risk Bucket", fontsize=8)
    for _, row in RISK.iterrows():
        if row["Opportunity Score"] > 80:
            ax1.annotate(row["Stock Symbol"], (row["Volatility (%)"], row["Annualized Return (%)"]),
                         fontsize=7, alpha=0.8)

    # Top-20 opportunity bar
    top = STOCK.nlargest(20, "Opportunity Score").sort_values("Opportunity Score")
    ax2.barh(top["Stock Symbol"], top["Opportunity Score"], color="#2ca02c")
    ax2.set_xlabel("Opportunity Score")
    ax2.set_title("Top 20 Stocks by Opportunity Score")

    fig.tight_layout()
    save(fig, "04_stock_opportunity.png")


# ── 5. COVID Crash Recovery ─────────────────────────────────────────────────
def plot_covid():
    df = SECTOR.sort_values("Recovery Minus Crash (pp)", ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("COVID Crash & Recovery View", fontsize=14, fontweight="bold")

    ax1.barh(df["Sector / Industry"], df["COVID Crash Return (%)"], color="#d62728")
    ax1.set_xlabel("COVID Crash Return (%)")
    ax1.set_title("2020 COVID Crash by Sector")
    ax1.axvline(0, color="black", linewidth=0.5)

    width = 0.35
    y = np.arange(len(df))
    ax2.barh(y - width / 2, df["COVID Crash Return (%)"], width, label="Crash", color="#d62728", alpha=0.7)
    ax2.barh(y + width / 2, df["COVID Recovery Return (%)"], width, label="Recovery", color="#2ca02c", alpha=0.7)
    ax2.set_yticks(y)
    ax2.set_yticklabels(df["Sector / Industry"])
    ax2.set_xlabel("Return (%)")
    ax2.set_title("Crash vs Recovery Comparison")
    ax2.legend()
    ax2.axvline(0, color="black", linewidth=0.5)

    fig.tight_layout()
    save(fig, "05_covid_crash_recovery.png")


# ── 6. Recommendation View ──────────────────────────────────────────────────
def plot_recommendation():
    if "Recommendation Action" in RECO.columns:
        action_col = "Recommendation Action"
    else:
        action_col = RECO.columns[RECO.columns.str.contains("action", case=False)][0]

    counts = RECO[action_col].value_counts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Recommendation View", fontsize=14, fontweight="bold")

    colors = [COLORS.get(a, "#999") for a in counts.index]
    ax1.barh(counts.index, counts.values, color=colors)
    ax1.set_xlabel("Number of Stocks")
    ax1.set_title("Stocks by Recommendation Action")

    for action in ["Buy", "Watch", "Trade Candidate", "Avoid"]:
        sub = RECO[RECO[action_col] == action].sort_values("Opportunity Score", ascending=False).head(5)
        if sub.empty:
            continue
        ax2.barh(
            [f"{r['Stock Symbol']} ({action})" for _, r in sub.iterrows()],
            sub["Opportunity Score"],
            color=COLORS.get(action, "#999"),
            alpha=0.8,
            label=action,
        )
    ax2.set_xlabel("Opportunity Score")
    ax2.set_title("Top 5 Stocks per Recommendation Bucket")
    handles, labels = ax2.get_legend_handles_labels()
    seen = set()
    unique = [(h, l) for h, l in zip(handles, labels) if l not in seen and not seen.add(l)]
    if unique:
        ax2.legend(*zip(*unique), fontsize=8)

    fig.tight_layout()
    save(fig, "06_recommendation_view.png")


if __name__ == "__main__":
    print("Generating dashboard reference screenshots...")
    plot_executive_kpis()
    plot_market_trend()
    plot_sector_comparison()
    plot_stock_opportunity()
    plot_covid()
    plot_recommendation()
    print("Done. All screenshots saved to tableau/screenshots/")
