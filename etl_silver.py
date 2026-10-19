"""
Loads the silver layer: read each bronze table, apply its cleansing rules
(transform.py), and truncate+load the result into silver.<table>.
Equivalent to silver.load_silver() in 06_proc_load_silver.sql.
"""

import time

import pandas as pd

import config
import db
import load
from transform import SILVER_TRANSFORMS


def run() -> None:
    print("=" * 48)
    print("Loading Silver Layer")
    print("=" * 48)

    bronze_engine = db.get_engine(config.BRONZE_DB)
    silver_engine = db.get_engine(config.SILVER_DB)
    batch_start = time.perf_counter()

    for table, transform_fn in SILVER_TRANSFORMS.items():
        print(f">> Reading: bronze.{table}")
        raw = pd.read_sql(f"SELECT * FROM {table}", con=bronze_engine)

        print(f">> Transforming: {table}")
        clean = transform_fn(raw)

        print(f">> Truncating + loading: silver.{table}")
        duration = load.truncate_and_load(silver_engine, table, clean)
        print(f">> Load duration: {duration:.2f} seconds")
        print(">> -------------")

    total = time.perf_counter() - batch_start
    print("=" * 48)
    print(f"Silver layer completed in {total:.2f} seconds")
    print("=" * 48)


if __name__ == "__main__":
    run()
