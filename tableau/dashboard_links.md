# Dashboard Links And Submission Notes

## Tableau Public URL

Status: Publication deferred. The verified packaged workbook for this submission is `tableau/nifty50_dashboard_twilize.twbx`, and it opens correctly in Tableau Desktop. Add the real Tableau Public URL here later if the dashboard is published.

Final URL:
To be added after the Tableau dashboard is published from the `.twbx` file using Tableau Desktop.

Placeholder rule:
Do not insert a fake or temporary URL here. Replace this line only when the real Tableau Public link exists.

## Packaged Workbook

- `tableau/nifty50_dashboard_twilize.twbx` — verified packaged Tableau workbook used for submission. Built from the flattened master extract by `scripts/generate_twilize_dashboard.py` and confirmed to open in Tableau Desktop.

## Reference Screenshots

Latest workbook screenshots captured from the verified Tableau workbook:

- `tableau/screenshots/00_dashboard_overview.png` — Combined dashboard overview with KPI cards and the major analytical views
- `tableau/screenshots/01_executive_kpi_cards.png` — Executive KPI summary cards
- `tableau/screenshots/02_market_trend_view.png` — Yearly market index, volume, and turnover trends
- `tableau/screenshots/03_sector_comparison.png` — Sector-level return, volatility, and delivery comparison
- `tableau/screenshots/04_stock_opportunity.png` — Risk–return scatter and top-20 opportunity ranking
- `tableau/screenshots/05_covid_crash_recovery.png` — COVID crash and recovery comparison by sector
- `tableau/screenshots/06_recommendation_view.png` — Recommendation action distribution and top stocks per bucket

## Submission Reminder

- Export the final dashboard as a packaged Tableau workbook in `.twbx` format.
- Submit the `.twbx` file only for the dashboard requirement.
- Keep the Tableau Public URL aligned with the same final workbook version.
- Add the same final Tableau Public URL to `reports/project_report.md` before creating the final submission PDF.

## Tableau Data Files Used

- `data/processed/tableau_stock_level.csv`
- `data/processed/tableau_sector_level.csv`
- `data/processed/tableau_yearly_trends.csv`
- `data/processed/tableau_risk_segments.csv`
- `data/processed/tableau_recommendation_view.csv`

## QA Reminder Before Upload

- Open the `.twbx` file on a clean machine if possible.
- Confirm filters work for year, sector, stock symbol, risk bucket, segment, and date range.
- Confirm labels and legends use the final business-friendly field names.
- Confirm screenshots saved in `tableau/screenshots/` match the workbook that is being submitted.
