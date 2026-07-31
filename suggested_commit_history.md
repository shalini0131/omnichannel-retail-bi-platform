# Suggested Git Commit History

To make your GitHub repository look clean, professional, and built using industry-standard engineering practices, we recommend pushing your work using this structured commit history.

---

### Commit 1: Initial Setup
* **Message:** `feat: initialize project folder structure and configurations`
* **Details:** Added `.gitignore`, `requirements.txt`, and base folder structure.
* **Scope:** Root directory.

### Commit 2: Data Extraction Script
* **Message:** `feat: implement raw dataset downloader and legacy source splitter`
* **Details:** Created `python/split_raw_data.py` to automate downloading the UCI dataset and split it into 6 regional CSV database sources.
* **Scope:** Python files.

### Commit 3: Database Schema DDL
* **Message:** `db: design star schema DDL and indexes for PostgreSQL`
* **Details:** Created `sql/01_schema.sql` defining `dim_date`, `dim_customers`, `dim_products`, `dim_branches`, and `fact_sales` with constraint and index definitions.
* **Scope:** SQL files.

### Commit 4: ETL Data Pipeline
* **Message:** `feat: construct robust pandas-to-postgres bulk load ETL pipeline`
* **Details:** Implemented `python/etl.py` to handle data cleaning, dimensional transformation, guest profiling, and bulk database copy logic.
* **Scope:** Python/ETL files.

### Commit 5: SQL Analysis Queries
* **Message:** `analytics: write business intelligence validation and core KPI SQL queries`
* **Details:** Added `sql/02_cleaning.sql` and `sql/03_business_queries.sql` to calculate SSSG, AOV, returns, and customer retention.
* **Scope:** SQL queries.

### Commit 6: Forecasting Model
* **Message:** `feat: implement Holt-Winters weekly sales demand forecasting model`
* **Details:** Created `python/forecasting.py` to train statsmodels Triple Exponential Smoothing, validate metrics, and save projection curves.
* **Scope:** Python/Forecasting files.

### Commit 7: Power BI Specifications
* **Message:** `docs: document Power BI dimensional relationships and DAX measures`
* **Details:** Created `powerbi/power_bi_model_spec.md` with 20+ production-grade DAX measures and page designs.
* **Scope:** BI/Documentation.

### Commit 8: Final Documentation
* **Message:** `docs: finalize business report, data dictionaries, and README`
* **Details:** Added final markdown files under `docs/` and the main `README.md`.
* **Scope:** Documentation.
