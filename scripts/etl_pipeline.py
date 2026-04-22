"""Reproducible ETL pipeline for the NIFTY-50 capstone dataset."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = REPO_ROOT / "data" / "raw"
DEFAULT_PROCESSED_DIR = REPO_ROOT / "data" / "processed"
DEFAULT_OUTPUTS_DIR = REPO_ROOT / "outputs" / "tables"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs"

PRICE_COLUMNS = [
    "prev_close",
    "open",
    "high",
    "low",
    "last",
    "close",
    "vwap",
]
NUMERIC_COLUMNS = PRICE_COLUMNS + [
    "volume",
    "turnover",
    "trades",
    "deliverable_volume",
    "deliverable_percent",
]
VOLUME_COLUMNS = [
    "volume",
    "turnover",
    "trades",
    "deliverable_volume",
    "deliverable_percent",
]
METADATA_COLUMNS = ["company_name", "industry", "isin_code"]


def to_snake_case(column_name: str) -> str:
    """Convert source column names into reproducible snake_case labels."""
    aliases = {
        "%Deliverble": "deliverable_percent",
        "Deliverable Volume": "deliverable_volume",
        "Prev Close": "prev_close",
        "Company Name": "company_name",
        "ISIN Code": "isin_code",
    }
    if column_name in aliases:
        return aliases[column_name]

    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", column_name.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower()


def detect_csv_role(csv_path: Path) -> str:
    """Classify a CSV file as stock, combined stock, metadata, or unknown."""
    header = list(pd.read_csv(csv_path, nrows=0).columns)
    normalized = {to_snake_case(column) for column in header}
    trading_signature = {"date", "open", "high", "low", "close", "volume"}
    metadata_signature = {"company_name", "industry", "symbol"}

    if metadata_signature.issubset(normalized):
        return "metadata"
    if trading_signature.issubset(normalized):
        lower_name = csv_path.stem.lower()
        if any(token in lower_name for token in ("all", "combined", "master")):
            return "combined_stock"
        return "stock"
    return "unknown"


def load_metadata_frame(metadata_path: Path) -> pd.DataFrame:
    """Load and minimally sanitize metadata before attaching it to trading rows."""
    metadata = pd.read_csv(metadata_path)
    metadata.columns = [column.strip() for column in metadata.columns]
    metadata["Symbol"] = metadata["Symbol"].astype(str).str.strip()
    return metadata.drop_duplicates(subset=["Symbol"])


def load_raw_stock_files(raw_dir: Path | str = DEFAULT_RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame | None, dict[str, Any]]:
    """Load trading CSVs from the raw directory and attach metadata when available."""
    raw_dir = Path(raw_dir)
    csv_files = sorted(raw_dir.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found under {raw_dir}. "
            "Add the Kaggle NIFTY files to data/raw/ before running the ETL pipeline."
        )

    stock_files: list[Path] = []
    combined_stock_files: list[Path] = []
    metadata_files: list[Path] = []
    unknown_files: list[Path] = []

    for csv_path in csv_files:
        role = detect_csv_role(csv_path)
        if role == "stock":
            stock_files.append(csv_path)
        elif role == "combined_stock":
            combined_stock_files.append(csv_path)
        elif role == "metadata":
            metadata_files.append(csv_path)
        else:
            unknown_files.append(csv_path)

    selected_stock_files = stock_files or combined_stock_files
    selection_strategy = "individual_stock_files" if stock_files else "combined_stock_file"
    if not selected_stock_files:
        raise FileNotFoundError(
            "Trading CSV files were not detected in the raw data folder. "
            "Expected either per-stock CSVs or a combined stock-market CSV."
        )

    stock_frames: list[pd.DataFrame] = []
    for csv_path in selected_stock_files:
        frame = pd.read_csv(csv_path)
        frame.columns = [column.strip() for column in frame.columns]
        source_symbol = csv_path.stem
        if "Symbol" not in frame.columns:
            frame["Symbol"] = source_symbol
        else:
            missing_symbol_mask = frame["Symbol"].isna() | (frame["Symbol"].astype(str).str.strip() == "")
            frame.loc[missing_symbol_mask, "Symbol"] = source_symbol
        frame["source_file"] = csv_path.name
        frame["source_symbol"] = source_symbol
        stock_frames.append(frame)

    combined = pd.concat(stock_frames, ignore_index=True)

    metadata = load_metadata_frame(metadata_files[0]) if metadata_files else None
    metadata_report = {
        "metadata_file": str(metadata_files[0].relative_to(REPO_ROOT)) if metadata_files else None,
        "metadata_available": metadata is not None,
    }

    if metadata is not None:
        company_map = metadata.set_index("Symbol")["Company Name"]
        industry_map = metadata.set_index("Symbol")["Industry"]
        isin_map = metadata.set_index("Symbol")["ISIN Code"]

        direct_company = combined["Symbol"].map(company_map)
        fallback_company = combined["source_symbol"].map(company_map)

        combined["Company Name"] = direct_company.fillna(fallback_company)
        combined["Industry"] = combined["Symbol"].map(industry_map).fillna(
            combined["source_symbol"].map(industry_map)
        )
        combined["ISIN Code"] = combined["Symbol"].map(isin_map).fillna(
            combined["source_symbol"].map(isin_map)
        )
        combined["metadata_join_key"] = np.where(
            direct_company.notna(),
            "symbol",
            np.where(fallback_company.notna(), "source_symbol", pd.NA),
        )
        metadata_report["rows_with_metadata"] = int(combined["Company Name"].notna().sum())
        metadata_report["rows_without_metadata"] = int(combined["Company Name"].isna().sum())
    else:
        combined["metadata_join_key"] = pd.NA
        metadata_report["rows_with_metadata"] = 0
        metadata_report["rows_without_metadata"] = int(len(combined))

    extraction_report: dict[str, Any] = {
        "raw_dir": str(raw_dir),
        "csv_files_found": len(csv_files),
        "stock_files_found": len(stock_files),
        "combined_stock_files_found": len(combined_stock_files),
        "unknown_files_found": len(unknown_files),
        "selection_strategy": selection_strategy,
        "selected_stock_files": [str(path.relative_to(REPO_ROOT)) for path in selected_stock_files],
        "combined_stock_files": [str(path.relative_to(REPO_ROOT)) for path in combined_stock_files],
        "unknown_files": [str(path.relative_to(REPO_ROOT)) for path in unknown_files],
    }
    extraction_report.update(metadata_report)

    return combined, metadata, extraction_report


def standardize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Rename all columns into snake_case for downstream reproducibility."""
    renamed = dataframe.copy()
    renamed.columns = [to_snake_case(column) for column in renamed.columns]
    return renamed


def clean_numeric_fields(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Convert fields safely, profile missingness, normalize known issues, and flag quality concerns."""
    cleaned = dataframe.copy()
    audit: dict[str, Any] = {}

    missing_before = cleaned.isna().sum().sort_values(ascending=False)
    audit["missing_before"] = missing_before
    audit["rows_before_cleaning"] = int(len(cleaned))

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if "deliverable_percent" in cleaned.columns:
        over_one_mask = cleaned["deliverable_percent"] > 1
        cleaned.loc[over_one_mask, "deliverable_percent"] = cleaned.loc[over_one_mask, "deliverable_percent"] / 100

    if {"turnover", "vwap", "volume"}.issubset(cleaned.columns):
        expected_turnover = cleaned["vwap"] * cleaned["volume"]
        ratio = cleaned["turnover"] / expected_turnover.replace(0, np.nan)
        ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
        median_ratio = float(ratio.median()) if not ratio.empty else np.nan
        scale_factor = 100000.0 if 90000 <= median_ratio <= 110000 else 1.0
        if scale_factor != 1.0:
            cleaned["turnover"] = cleaned["turnover"] / scale_factor
        audit["turnover_scale_factor"] = scale_factor
        audit["turnover_ratio_median"] = median_ratio
    else:
        audit["turnover_scale_factor"] = 1.0
        audit["turnover_ratio_median"] = np.nan

    duplicate_count = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates().copy()
    audit["exact_duplicates_removed"] = duplicate_count

    cleaned = cleaned.sort_values(["symbol", "date", "series", "source_file"], kind="stable").reset_index(drop=True)

    price_missing_before_fill = cleaned[PRICE_COLUMNS].isna()
    price_fill_mask = price_missing_before_fill.any(axis=1)
    cleaned[PRICE_COLUMNS] = cleaned.groupby("symbol", dropna=False)[PRICE_COLUMNS].transform(
        lambda column: column.ffill().bfill()
    )
    audit["rows_with_price_missing_before_fill"] = int(price_fill_mask.sum())
    audit["price_missing_cells_filled"] = int(
        price_missing_before_fill.sum().sum() - cleaned[PRICE_COLUMNS].isna().sum().sum()
    )

    cleaned["missing_price_flag"] = cleaned[PRICE_COLUMNS].isna().any(axis=1)
    cleaned["missing_volume_flag"] = cleaned[VOLUME_COLUMNS].isna().any(axis=1)

    high_low_invalid = (cleaned["high"] < cleaned["low"]) & cleaned["high"].notna() & cleaned["low"].notna()
    high_open_invalid = (cleaned["high"] < cleaned["open"]) & cleaned["high"].notna() & cleaned["open"].notna()
    high_close_invalid = (cleaned["high"] < cleaned["close"]) & cleaned["high"].notna() & cleaned["close"].notna()
    low_open_invalid = (cleaned["low"] > cleaned["open"]) & cleaned["low"].notna() & cleaned["open"].notna()
    low_close_invalid = (cleaned["low"] > cleaned["close"]) & cleaned["low"].notna() & cleaned["close"].notna()
    cleaned["invalid_ohlc_flag"] = (
        high_low_invalid | high_open_invalid | high_close_invalid | low_open_invalid | low_close_invalid
    )

    missing_after = cleaned.isna().sum().sort_values(ascending=False)
    audit["missing_after"] = missing_after
    audit["rows_after_cleaning"] = int(len(cleaned))
    audit["invalid_ohlc_rows"] = int(cleaned["invalid_ohlc_flag"].sum())

    return cleaned, audit


def flag_symbol_outliers(symbol_returns: pd.Series) -> pd.Series:
    """Flag daily-return outliers within each symbol using an IQR rule with a z-score fallback."""
    valid_returns = symbol_returns.dropna()
    if len(valid_returns) < 4:
        return pd.Series(False, index=symbol_returns.index)

    q1 = valid_returns.quantile(0.25)
    q3 = valid_returns.quantile(0.75)
    iqr = q3 - q1
    if pd.notna(iqr) and iqr > 0:
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return symbol_returns.notna() & ~symbol_returns.between(lower_bound, upper_bound)

    std_dev = valid_returns.std(ddof=0)
    if pd.isna(std_dev) or std_dev == 0:
        return pd.Series(False, index=symbol_returns.index)

    z_scores = (symbol_returns - valid_returns.mean()) / std_dev
    return symbol_returns.notna() & (z_scores.abs() > 3)


def add_features(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Engineer derived trading features after the core cleaning pass."""
    enriched = dataframe.copy()
    feature_audit: dict[str, Any] = {}

    enriched["daily_return"] = np.where(
        enriched["prev_close"] > 0,
        (enriched["close"] - enriched["prev_close"]) / enriched["prev_close"],
        np.nan,
    )
    enriched["intraday_return"] = np.where(
        enriched["open"] > 0,
        (enriched["close"] - enriched["open"]) / enriched["open"],
        np.nan,
    )
    enriched["high_low_spread"] = enriched["high"] - enriched["low"]
    enriched["vwap_gap"] = enriched["close"] - enriched["vwap"]
    enriched["turnover_cr"] = enriched["turnover"] / 10_000_000
    enriched["delivery_ratio"] = enriched["deliverable_percent"]

    enriched["year"] = enriched["date"].dt.year
    enriched["month"] = enriched["date"].dt.month
    enriched["quarter"] = enriched["date"].dt.quarter
    enriched["day_of_week"] = enriched["date"].dt.day_name()

    enriched["outlier_return_flag"] = (
        enriched.groupby("symbol", group_keys=False)["daily_return"].apply(flag_symbol_outliers).astype(bool)
    )

    feature_audit["outlier_return_rows"] = int(enriched["outlier_return_flag"].sum())
    feature_audit["daily_return_nulls"] = int(enriched["daily_return"].isna().sum())

    return enriched, feature_audit


def build_cleaning_summary(
    combined_raw: pd.DataFrame,
    cleaned: pd.DataFrame,
    extraction_report: dict[str, Any],
    cleaning_audit: dict[str, Any],
    feature_audit: dict[str, Any],
) -> pd.DataFrame:
    """Produce a compact summary table for export and grading evidence."""
    metrics: list[dict[str, Any]] = [
        {"metric": "raw_rows_combined", "value": int(len(combined_raw))},
        {"metric": "cleaned_rows", "value": int(len(cleaned))},
        {"metric": "stock_files_found", "value": extraction_report["stock_files_found"]},
        {"metric": "combined_stock_files_found", "value": extraction_report["combined_stock_files_found"]},
        {"metric": "metadata_available", "value": extraction_report["metadata_available"]},
        {"metric": "rows_with_metadata", "value": extraction_report["rows_with_metadata"]},
        {"metric": "rows_without_metadata", "value": extraction_report["rows_without_metadata"]},
        {"metric": "exact_duplicates_removed", "value": cleaning_audit["exact_duplicates_removed"]},
        {"metric": "rows_with_price_missing_before_fill", "value": cleaning_audit["rows_with_price_missing_before_fill"]},
        {"metric": "price_missing_cells_filled", "value": cleaning_audit["price_missing_cells_filled"]},
        {"metric": "missing_price_flag_rows", "value": int(cleaned["missing_price_flag"].sum())},
        {"metric": "missing_volume_flag_rows", "value": int(cleaned["missing_volume_flag"].sum())},
        {"metric": "invalid_ohlc_flag_rows", "value": int(cleaned["invalid_ohlc_flag"].sum())},
        {"metric": "outlier_return_flag_rows", "value": feature_audit["outlier_return_rows"]},
        {"metric": "turnover_scale_factor", "value": cleaning_audit["turnover_scale_factor"]},
        {"metric": "turnover_ratio_median", "value": cleaning_audit["turnover_ratio_median"]},
        {"metric": "min_date", "value": cleaned["date"].min().date().isoformat()},
        {"metric": "max_date", "value": cleaned["date"].max().date().isoformat()},
        {"metric": "distinct_symbols", "value": int(cleaned["symbol"].nunique())},
        {"metric": "distinct_source_symbols", "value": int(cleaned["source_symbol"].nunique())},
    ]

    for column, value in cleaning_audit["missing_before"].items():
        metrics.append({"metric": f"missing_before::{column}", "value": int(value)})
    for column, value in cleaning_audit["missing_after"].items():
        metrics.append({"metric": f"missing_after::{column}", "value": int(value)})

    return pd.DataFrame(metrics)


def generate_quality_report(
    combined_raw: pd.DataFrame,
    cleaned: pd.DataFrame,
    extraction_report: dict[str, Any],
    cleaning_audit: dict[str, Any],
    feature_audit: dict[str, Any],
) -> tuple[pd.DataFrame, str]:
    """Create the exported summary table plus a Markdown quality report."""
    summary = build_cleaning_summary(combined_raw, cleaned, extraction_report, cleaning_audit, feature_audit)

    selected_files = "\n".join(f"- `{path}`" for path in extraction_report["selected_stock_files"])
    unknown_files = "\n".join(f"- `{path}`" for path in extraction_report["unknown_files"]) or "- None"
    missing_before_lines = "\n".join(
        f"| `{column}` | {int(value)} |"
        for column, value in cleaning_audit["missing_before"].items()
        if int(value) > 0
    ) or "| None | 0 |"
    missing_after_lines = "\n".join(
        f"| `{column}` | {int(value)} |"
        for column, value in cleaning_audit["missing_after"].items()
        if int(value) > 0
    ) or "| None | 0 |"

    report = f"""# Cleaning Log

## Run Context

- Generated by: `python scripts/etl_pipeline.py`
- Raw directory scanned: `{Path(extraction_report['raw_dir']).resolve()}`
- Extraction strategy: `{extraction_report['selection_strategy']}`
- Stock files used: {len(extraction_report['selected_stock_files'])}
- Combined stock files detected but not stacked: {extraction_report['combined_stock_files_found']}
- Metadata file: `{extraction_report['metadata_file'] or 'Not found'}`

## Files Used

{selected_files}

## Detection Notes

- Unknown CSV files skipped: {extraction_report['unknown_files_found']}
- Unknown file list:
{unknown_files}
- The committed raw dataset contains both per-stock files and `NIFTY50_all.csv`. The ETL prefers per-stock files when available so the master dataset is rebuilt without double-counting rows.

## Combined Dataset Profile

- Combined raw shape: `{combined_raw.shape[0]:,} rows x {combined_raw.shape[1]:,} columns`
- Cleaned dataset shape: `{cleaned.shape[0]:,} rows x {cleaned.shape[1]:,} columns`
- Date range: `{cleaned['date'].min().date().isoformat()}` to `{cleaned['date'].max().date().isoformat()}`
- Distinct row-level symbols: `{cleaned['symbol'].nunique()}`
- Distinct source-file symbols: `{cleaned['source_symbol'].nunique()}`
- Rows with metadata attached: `{extraction_report['rows_with_metadata']:,}`
- Rows without metadata attached: `{extraction_report['rows_without_metadata']:,}`

## Missingness Before Cleaning

| Column | Missing Rows |
| --- | ---: |
{missing_before_lines}

## Missingness After Cleaning

| Column | Missing Rows |
| --- | ---: |
{missing_after_lines}

## Cleaning Actions

- Exact duplicate rows removed: `{cleaning_audit['exact_duplicates_removed']:,}`
- Rows with missing price fields before symbol-wise fill: `{cleaning_audit['rows_with_price_missing_before_fill']:,}`
- Price cells filled via symbol-wise forward/backward fill: `{cleaning_audit['price_missing_cells_filled']:,}`
- Rows still flagged with missing price values: `{int(cleaned['missing_price_flag'].sum()):,}`
- Rows flagged with missing volume or delivery fields: `{int(cleaned['missing_volume_flag'].sum()):,}`
- Rows flagged with invalid OHLC logic: `{int(cleaned['invalid_ohlc_flag'].sum()):,}`
- Rows flagged as daily-return outliers: `{feature_audit['outlier_return_rows']:,}`

## Turnover Standardization

- Median raw `turnover / (vwap * volume)` ratio: `{cleaning_audit['turnover_ratio_median']:.6f}`
- Applied turnover scale factor: `{cleaning_audit['turnover_scale_factor']}`
- Interpretation: the raw turnover field is approximately `100000x` the implied traded value in the committed dataset, so the cleaned output rescales turnover back to rupee-like units before deriving `turnover_cr`.

## Output Files

- `data/processed/nifty50_combined_raw.csv`
- `data/processed/nifty50_cleaned.csv`
- `outputs/tables/cleaning_summary.csv`
- `docs/cleaning_log.md`
"""

    return summary, report


def save_outputs(
    combined_raw: pd.DataFrame,
    cleaned: pd.DataFrame,
    cleaning_summary: pd.DataFrame,
    quality_report: str,
    processed_dir: Path | str = DEFAULT_PROCESSED_DIR,
    outputs_dir: Path | str = DEFAULT_OUTPUTS_DIR,
    docs_dir: Path | str = DEFAULT_DOCS_DIR,
) -> dict[str, Path]:
    """Persist all ETL artifacts to the expected capstone directories."""
    processed_dir = Path(processed_dir)
    outputs_dir = Path(outputs_dir)
    docs_dir = Path(docs_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    raw_output = processed_dir / "nifty50_combined_raw.csv"
    cleaned_output = processed_dir / "nifty50_cleaned.csv"
    summary_output = outputs_dir / "cleaning_summary.csv"
    report_output = docs_dir / "cleaning_log.md"

    combined_raw.to_csv(raw_output, index=False)
    cleaned.to_csv(cleaned_output, index=False)
    cleaning_summary.to_csv(summary_output, index=False)
    report_output.write_text(quality_report, encoding="utf-8")

    return {
        "raw_output": raw_output,
        "cleaned_output": cleaned_output,
        "summary_output": summary_output,
        "report_output": report_output,
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for raw and output directories."""
    parser = argparse.ArgumentParser(description="Run the NIFTY-50 extraction and cleaning pipeline.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="Folder containing raw CSV inputs.")
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=DEFAULT_PROCESSED_DIR,
        help="Folder where processed CSV files should be written.",
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_OUTPUTS_DIR,
        help="Folder where summary tables should be written.",
    )
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR, help="Folder for Markdown ETL logs.")
    return parser.parse_args()


def main() -> int:
    """Run the full ETL workflow and print a concise execution summary."""
    args = parse_args()

    try:
        combined_raw, _, extraction_report = load_raw_stock_files(args.raw_dir)
    except FileNotFoundError as error:
        print(f"ETL failed: {error}", file=sys.stderr)
        return 1

    standardized = standardize_columns(combined_raw)
    cleaned, cleaning_audit = clean_numeric_fields(standardized)
    enriched, feature_audit = add_features(cleaned)
    cleaning_summary, quality_report = generate_quality_report(
        combined_raw=combined_raw,
        cleaned=enriched,
        extraction_report=extraction_report,
        cleaning_audit=cleaning_audit,
        feature_audit=feature_audit,
    )
    output_paths = save_outputs(
        combined_raw=combined_raw,
        cleaned=enriched,
        cleaning_summary=cleaning_summary,
        quality_report=quality_report,
        processed_dir=args.processed_dir,
        outputs_dir=args.outputs_dir,
        docs_dir=args.docs_dir,
    )

    print("ETL completed successfully.")
    print(f"Combined raw output: {output_paths['raw_output']}")
    print(f"Cleaned output: {output_paths['cleaned_output']}")
    print(f"Cleaning summary: {output_paths['summary_output']}")
    print(f"Cleaning log: {output_paths['report_output']}")
    print(f"Cleaned dataset shape: {enriched.shape}")
    print(f"Date range: {enriched['date'].min().date().isoformat()} to {enriched['date'].max().date().isoformat()}")
    print(f"Distinct symbols: {enriched['symbol'].nunique()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
