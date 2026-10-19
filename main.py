"""
Entry point for the ETL pipeline: loads bronze, then silver.

The gold layer stays as plain MySQL views (04_ddl_gold.sql) — there's
nothing to run in Python for it, since views recompute automatically from
silver on every query. If you're using the optional materialized gold
tables (07_gold_materialized_optional.sql), re-run that SQL script after
this pipeline finishes.

Usage:
    python main.py
"""

import time

import etl_bronze
import etl_silver


def run() -> None:
    start = time.perf_counter()

    etl_bronze.run()
    print()
    etl_silver.run()

    total = time.perf_counter() - start
    print()
    print(f"Full pipeline (bronze -> silver) completed in {total:.2f} seconds")


if __name__ == "__main__":
    run()
