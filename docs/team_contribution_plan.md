# Team Contribution Plan

## Team Members

- Aryan Verma
- Devaansh Kathuria
- Birajit Saikia
- Abhey Dua
- Atharv Paharia

## Planned Ownership

### Atharv Paharia

- repository setup
- dataset sourcing and organization
- problem framing
- initial documentation

### Devaansh Kathuria

- ETL pipeline development
- raw-data cleaning and validation
- processed dataset generation

### Aryan Verma

- exploratory data analysis
- KPI definition and descriptive insights
- chart support for report and Tableau requirements

### Abhey Dua

- statistical analysis
- volatility and risk scoring methods
- comparative interpretation of stock and sector behavior

### Birajit Saikia

- final Tableau pack
- final report assembly
- presentation/deck support
- QA and submission readiness

## Collaboration Guidelines

- Each member should work in clearly scoped files or folders to reduce merge conflicts.
- Raw data in `data/raw/` should not be edited directly.
- Processed outputs should be reproducible from code, not manually altered without documentation.
- Any major schema, naming, or calculation changes should be reflected in the documentation before final submission.
- Final analytical claims must be supported by versioned notebooks, scripts, tables, or dashboard assets.

## Review and Handoff Expectations

- ETL changes should update downstream assumptions in notebooks and Tableau extracts.
- EDA and statistical outputs should clearly reference the processed dataset version used.
- Final report and deck material should be checked against repository evidence before submission.
- Responsibility can evolve during the project, but ownership changes should be documented in this file.
