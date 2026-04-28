from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from twilize.chart_suggester import ChartSuggestion, DashboardSuggestion, ShelfAssignment
from twilize.dashboard_rules import load_rules
from twilize.pipeline import build_dashboard_from_csv


ROOT = Path("/Users/birajitsaikia/Documents/dva-final/DVA_capstone_2")
PROCESSED = ROOT / "data" / "processed"
TABLEAU = ROOT / "tableau"

MASTER_CSV = PROCESSED / "tableau_dashboard_master.csv"
OUTPUT_TWBX = TABLEAU / "nifty50_dashboard_twilize.twbx"


@dataclass
class MonthlyAgg:
    last_date: str = ""
    close_sum: float = 0.0
    close_count: int = 0
    daily_return_sum: float = 0.0
    daily_return_count: int = 0
    volume_sum: float = 0.0
    turnover_cr_sum: float = 0.0
    delivery_sum: float = 0.0
    delivery_count: int = 0
    vwap_gap_sum: float = 0.0
    vwap_gap_count: int = 0

    def update(self, row: dict[str, str]) -> None:
        row_date = row["date"]
        if not self.last_date or row_date > self.last_date:
            self.last_date = row_date
        self.close_sum += _to_float(row.get("close"))
        self.close_count += 1
        self.daily_return_sum += _to_float(row.get("daily_return"))
        self.daily_return_count += 1
        self.volume_sum += _to_float(row.get("volume"))
        self.turnover_cr_sum += _to_float(row.get("turnover_cr"))
        self.delivery_sum += _to_float(row.get("delivery_ratio"))
        self.delivery_count += 1
        self.vwap_gap_sum += _to_float(row.get("vwap_gap"))
        self.vwap_gap_count += 1

    def avg_close(self) -> float:
        return self.close_sum / self.close_count if self.close_count else 0.0

    def avg_daily_return_pct(self) -> float:
        return (self.daily_return_sum / self.daily_return_count * 100.0) if self.daily_return_count else 0.0

    def avg_delivery_pct(self) -> float:
        return (self.delivery_sum / self.delivery_count * 100.0) if self.delivery_count else 0.0

    def avg_vwap_gap_pct(self) -> float:
        return (self.vwap_gap_sum / self.vwap_gap_count * 100.0) if self.vwap_gap_count else 0.0


def _to_float(value: str | None) -> float:
    if value in (None, "", "nan", "NaN"):
        return 0.0
    return float(value)


def _to_int(value: str | None) -> int:
    return int(float(value or 0))


def _lookup_float(row: dict[str, str], key: str) -> float:
    return _to_float(row.get(key))


def _read_lookup(path: Path, key_col: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row[key_col]: row for row in reader}


def build_master_csv() -> Path:
    stock_level = _read_lookup(PROCESSED / "tableau_stock_level.csv", "Stock Symbol")
    sector_level = _read_lookup(PROCESSED / "tableau_sector_level.csv", "Sector / Industry")
    risk_level = _read_lookup(PROCESSED / "tableau_risk_segments.csv", "Stock Symbol")
    recommendation_level = _read_lookup(PROCESSED / "tableau_recommendation_view.csv", "Stock Symbol")

    monthly: dict[tuple[int, int, int, str], MonthlyAgg] = defaultdict(MonthlyAgg)
    stock_meta: dict[str, dict[str, str]] = {}

    with (PROCESSED / "nifty50_cleaned.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = _to_int(row["year"])
            month = _to_int(row["month"])
            quarter = _to_int(row["quarter"])
            symbol = row["symbol"]
            monthly[(year, month, quarter, symbol)].update(row)
            if symbol not in stock_meta:
                stock_meta[symbol] = {
                    "Company Name": row.get("company_name", ""),
                    "Sector / Industry": row.get("industry", ""),
                }

    total_stocks = len(stock_level)
    MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Date",
        "Year",
        "Year Label",
        "Total Stocks Analyzed",
        "Stock Symbol",
        "Company Name",
        "Sector / Industry",
        "Average Close",
        "Average Daily Return (%)",
        "Volume",
        "Turnover (Cr)",
        "Average Delivery (%)",
        "Average VWAP Gap (%)",
        "Stock Annualized Return (%)",
        "Stock Volatility (%)",
        "Stock Max Drawdown (%)",
        "Stock Risk-Adjusted Return",
        "Stock Average Turnover (Cr)",
        "Stock Average Delivery (%)",
        "Opportunity Score",
        "Liquidity Score",
        "Investor Confidence Score",
        "Risk Score",
        "Risk Bucket",
        "Segment",
        "Segment Score",
        "Recommendation Action",
        "Sector Annualized Return (%)",
        "Sector Volatility (%)",
        "Sector Average Delivery (%)",
        "COVID Crash Return (%)",
        "COVID Recovery Return (%)",
        "Recovery Minus Crash (pp)",
    ]

    with MASTER_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (year, month, quarter, symbol), agg in sorted(monthly.items()):
            meta = stock_meta.get(symbol, {})
            sector_name = meta.get("Sector / Industry", "")
            stock_row = stock_level.get(symbol, {})
            risk_row = risk_level.get(symbol, {})
            rec_row = recommendation_level.get(symbol, {})
            sector_row = sector_level.get(sector_name, {})

            writer.writerow(
                {
                    "Date": agg.last_date,
                    "Year": year,
                    "Year Label": str(year),
                    "Total Stocks Analyzed": total_stocks,
                    "Stock Symbol": symbol,
                    "Company Name": meta.get("Company Name", ""),
                    "Sector / Industry": sector_name,
                    "Average Close": round(agg.avg_close(), 4),
                    "Average Daily Return (%)": round(agg.avg_daily_return_pct(), 6),
                    "Volume": round(agg.volume_sum, 2),
                    "Turnover (Cr)": round(agg.turnover_cr_sum, 4),
                    "Average Delivery (%)": round(agg.avg_delivery_pct(), 4),
                    "Average VWAP Gap (%)": round(agg.avg_vwap_gap_pct(), 6),
                    "Stock Annualized Return (%)": _lookup_float(stock_row, "Annualized Return (%)"),
                    "Stock Volatility (%)": _lookup_float(stock_row, "Volatility (%)"),
                    "Stock Max Drawdown (%)": _lookup_float(stock_row, "Max Drawdown (%)"),
                    "Stock Risk-Adjusted Return": _lookup_float(stock_row, "Risk-Adjusted Return"),
                    "Stock Average Turnover (Cr)": _lookup_float(stock_row, "Average Turnover (Cr)"),
                    "Stock Average Delivery (%)": _lookup_float(stock_row, "Average Delivery (%)"),
                    "Opportunity Score": _lookup_float(risk_row or stock_row, "Opportunity Score"),
                    "Liquidity Score": _lookup_float(risk_row or stock_row, "Liquidity Score"),
                    "Investor Confidence Score": _lookup_float(risk_row or stock_row, "Investor Confidence Score"),
                    "Risk Score": _lookup_float(risk_row or stock_row, "Risk Score"),
                    "Risk Bucket": risk_row.get("Risk Bucket", stock_row.get("Risk Bucket", "")),
                    "Segment": risk_row.get("Segment", stock_row.get("Segment", "")),
                    "Segment Score": _lookup_float(risk_row or stock_row, "Segment Score"),
                    "Recommendation Action": rec_row.get("Recommendation Action", stock_row.get("Recommendation Action", "")),
                    "Sector Annualized Return (%)": _lookup_float(sector_row, "Annualized Return (%)"),
                    "Sector Volatility (%)": _lookup_float(sector_row, "Volatility (%)"),
                    "Sector Average Delivery (%)": _lookup_float(sector_row, "Average Delivery (%)"),
                    "COVID Crash Return (%)": _lookup_float(sector_row, "COVID Crash Return (%)"),
                    "COVID Recovery Return (%)": _lookup_float(sector_row, "COVID Recovery Return (%)"),
                    "Recovery Minus Crash (pp)": _lookup_float(sector_row, "Recovery Minus Crash (pp)"),
                }
            )

    return MASTER_CSV


def build_suggestion() -> DashboardSuggestion:
    return DashboardSuggestion(
        title="NIFTY-50 Sectoral Performance & Risk Intelligence Dashboard",
        layout="grid",
        charts=[
            ChartSuggestion(
                chart_type="Text",
                title="Total Stocks Analyzed",
                shelves=[ShelfAssignment("Total Stocks Analyzed", "label", "AVG")],
                reason="Executive KPI card",
                priority=100,
            ),
            ChartSuggestion(
                chart_type="Text",
                title="Average Delivery KPI",
                shelves=[ShelfAssignment("Average Delivery (%)", "label", "AVG")],
                reason="Executive KPI card",
                priority=99,
            ),
            ChartSuggestion(
                chart_type="Text",
                title="Average Turnover KPI",
                shelves=[ShelfAssignment("Turnover (Cr)", "label", "AVG")],
                reason="Executive KPI card",
                priority=98,
            ),
            ChartSuggestion(
                chart_type="Text",
                title="Opportunity Score KPI",
                shelves=[ShelfAssignment("Opportunity Score", "label", "AVG")],
                reason="Executive KPI card",
                priority=97,
            ),
            ChartSuggestion(
                chart_type="Line",
                title="Market Trend View",
                shelves=[
                    ShelfAssignment("MONTH(Date)", "columns"),
                    ShelfAssignment("Average Close", "rows", "AVG"),
                    ShelfAssignment("Sector / Industry", "color"),
                ],
                reason="Trend view over time",
                priority=95,
            ),
            ChartSuggestion(
                chart_type="Bar",
                title="Sector Comparison View",
                shelves=[
                    ShelfAssignment("Sector / Industry", "rows"),
                    ShelfAssignment("Sector Annualized Return (%)", "columns", "AVG"),
                ],
                reason="Sector performance comparison",
                priority=94,
                sort_descending="AVG(Sector Annualized Return (%))",
            ),
            ChartSuggestion(
                chart_type="Scatterplot",
                title="Stock Opportunity View",
                shelves=[
                    ShelfAssignment("Stock Volatility (%)", "columns", "AVG"),
                    ShelfAssignment("Stock Annualized Return (%)", "rows", "AVG"),
                    ShelfAssignment("Stock Symbol", "detail"),
                    ShelfAssignment("Risk Bucket", "color"),
                ],
                reason="Risk-return opportunity mapping",
                priority=93,
            ),
            ChartSuggestion(
                chart_type="Bar",
                title="COVID Crash Recovery View",
                shelves=[
                    ShelfAssignment("Sector / Industry", "rows"),
                    ShelfAssignment("Recovery Minus Crash (pp)", "columns", "AVG"),
                ],
                reason="Recovery versus crash comparison",
                priority=92,
                sort_descending="AVG(Recovery Minus Crash (pp))",
            ),
            ChartSuggestion(
                chart_type="Bar",
                title="Recommendation View",
                shelves=[
                    ShelfAssignment("Recommendation Action", "rows"),
                    ShelfAssignment("Opportunity Score", "columns", "AVG"),
                    ShelfAssignment("Risk Bucket", "color"),
                ],
                reason="Segment-wise action summary",
                priority=91,
                sort_descending="AVG(Opportunity Score)",
            ),
        ],
    )


def main() -> None:
    master_csv = build_master_csv()
    rules = load_rules(str(master_csv))
    rules.setdefault("layout", {}).setdefault("filters", {})["max_filters"] = 5
    result = build_dashboard_from_csv(
        csv_path=master_csv,
        output_path=OUTPUT_TWBX,
        dashboard_title="NIFTY-50 Sectoral Performance & Risk Intelligence Dashboard",
        max_charts=9,
        suggestion=build_suggestion(),
        theme="modern-light",
        rules=rules,
    )
    print(result)


if __name__ == "__main__":
    main()
