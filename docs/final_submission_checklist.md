# Final Submission Checklist

Use this checklist as the final handoff gate before the NST DVA Capstone 2 submission form is filled.

## Repository And Code

- [ ] GitHub repository is public and the final link opens correctly.
- [ ] README is complete, current, and matches the final folder structure.
- [x] Raw data is present under `data/raw/nifty-dataset/`.
- [x] Processed data is present under `data/processed/`.
- [x] All core notebooks are present: `01_extraction.ipynb`, `02_cleaning.ipynb`, `03_eda.ipynb`, `04_statistical_analysis.ipynb`, `05_final_load_prep.ipynb`.
- [x] ETL script is present: `scripts/etl_pipeline.py`.
- [x] EDA and statistical scripts are present under `scripts/`.
- [x] Data dictionary is present: `docs/data_dictionary.md`.
- [x] KPI framework is present: `docs/kpi_framework.md`.

## Tableau Package

- [x] Tableau-ready CSV pack is present in `data/processed/`.
- [x] Validation output for Tableau pack is present: `outputs/tables/final_load_validation.csv`.
- [ ] Tableau workbook has been packaged and exported as `.twbx`.
- [ ] Only the `.twbx` file is prepared for dashboard submission.
- [ ] Tableau dashboard screenshots are saved under `tableau/screenshots/`.
- [ ] Tableau Public URL has been added to `tableau/dashboard_links.md`.
- [x] No fake Tableau URL is stored anywhere in the repository.
- [x] Dashboard blueprint is present: `tableau/dashboard_blueprint.md`.
- [x] Dashboard links file is present: `tableau/dashboard_links.md`.

## Report And Presentation

- [x] Final report draft is present: `reports/project_report.md`.
- [x] Report clearly includes group name and all team members.
- [x] Report states that cited numbers come from actual versioned output tables.
- [x] Presentation outline is present: `reports/presentation_outline.md`.
- [x] Report DOCX has been generated: `reports/project_report.docx`.
- [x] Report PDF has been generated: `reports/project_report.pdf`.
- [x] Presentation PPTX has been generated: `reports/presentation.pptx`.
- [x] Presentation PDF has been generated: `reports/presentation.pdf`.
- [x] PDF exports match the current Markdown content, with Tableau URL and screenshots still pending final workbook publication.

## Submission Form Readiness

- [x] Contribution matrix is included in the report.
- [x] Contribution matrix has been cross-checked against local git shortlog.
- [ ] Google Form fields are pre-filled and reviewed.
- [x] Team member names are ready in semicolon-separated format where required.
- [x] Semicolon-separated team line:
Aryan Verma; Devaansh Kathuria; Birajit Saikia; Abhey Dua; Atharv Paharia
- [x] Form-ready field draft is present: `docs/submission_form_ready.md`.
- [x] Enrollment IDs and ADYPU emails have been filled in `docs/submission_form_ready.md`.
- [x] GitHub link is listed in the report and ready for the form.

## QA And Consistency

- [x] README paths have been checked against the repository.
- [x] Notebook naming is internally consistent across README and docs.
- [x] Final-load notebook exports the required Tableau CSV files without index columns.
- [x] Tableau files use business-friendly field names.
- [x] Final-load notebook includes checks for missing values, duplicate keys, date range, stock count, sector count, and KPI availability.
- [x] Docs do not claim unavailable outputs.
- [x] Statistical findings, recommendations, and Tableau instructions are aligned with the actual output files.
- [ ] Final manual walkthrough completed by the team before submission upload.
