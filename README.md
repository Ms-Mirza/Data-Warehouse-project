# Python + MySQL data warehouse ETL

Python replacement for the `bronze.load_bronze()` / `silver.load_silver()`
T-SQL stored procedures. The MySQL schema itself (from the earlier
conversion) is unchanged — this just swaps what *runs* the ETL.

## Setup

1. Create the databases and tables first, using the SQL files from the
   MySQL conversion, in order:
   `01_init_database.sql` → `02_ddl_bronze.sql` → `03_ddl_silver.sql` →
   `04_ddl_gold.sql`

2. Install dependencies (a virtual environment is recommended):
   ```
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the database connection:
   ```
   cp .env.example .env
   ```
   Then edit `.env` with your MySQL host/user/password and the path to
   your CSVs (`DATA_DIR`, expecting `source_crm/` and `source_erp/`
   subfolders inside it, same layout as the original project).

## Run

```
python main.py
```

This runs bronze (extract CSVs → load raw) then silver (read bronze →
clean/standardize → load) in one pass, printing the same kind of
step-by-step timing log the original stored procedures did.

To run a layer on its own:
```
python etl_bronze.py
python etl_silver.py
```

## Web control panel

Instead of (or alongside) running `main.py` from the terminal, you can use
a small local dashboard:

```
python app.py
```

Then open **http://localhost:5000**. It gives you:
- Buttons to run the bronze load, silver load, or the full pipeline, with
  the same step-by-step log output printed to the page as it runs
- A browser for the gold layer (`dim_customers`, `dim_products`,
  `fact_sales`) with pagination, so you can sanity-check results without
  opening MySQL Workbench

It's a local Flask app — it imports `etl_bronze.py`, `etl_silver.py`, and
`main.py` directly and talks to MySQL using the same `.env` config as the
command-line version, so nothing about the pipeline itself changes. Each
run happens synchronously in the request (fine for course-sized data); if
you outgrow that later, moving the run to a background task/queue is the
natural next step.

## Gold layer

Gold stays as plain MySQL views (`04_ddl_gold.sql`) — nothing to run in
Python; the views recompute from silver automatically on every query.

If you're using the optional materialized gold tables for faster repeated
ML/analytics queries (`07_gold_materialized_optional.sql`), re-run that
script after `python main.py` finishes, since it snapshots gold into real
tables that need refreshing whenever silver changes.

## File map

| File | Role |
|---|---|
| `config.py` | DB credentials (from `.env`), source file paths, column mappings |
| `db.py` | SQLAlchemy engine factory (one engine per database) |
| `extract.py` | CSV → DataFrame |
| `transform.py` | Cleansing rules for each silver table (pandas port of `proc_load_silver.sql`) |
| `load.py` | Truncate + bulk-insert a DataFrame into MySQL |
| `etl_bronze.py` | Orchestrates the bronze load |
| `etl_silver.py` | Orchestrates the silver load (read bronze → transform → load) |
| `main.py` | Runs bronze then silver |
| `app.py` | Flask control panel (web UI for the pipeline + gold browser) |
| `templates/index.html`, `static/style.css` | Control panel front end |

## Extending this for ML work

Since gold is just MySQL tables/views, you can pull training data straight
into pandas from a notebook or script with no extra export step:

```python
import pandas as pd
from db import get_engine
import config

engine = get_engine(config.GOLD_DB)
sales = pd.read_sql("SELECT * FROM fact_sales", con=engine)
```

If you add a feature-engineering step later, a natural place for it is a
new `etl_gold.py` that reads from silver, builds features (e.g. customer
tenure, order recency/frequency), and writes them into their own table in
`gold` — following the same extract/transform/load pattern as the silver
step.