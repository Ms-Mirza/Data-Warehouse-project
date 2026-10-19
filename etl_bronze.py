"""
Loads the bronze layer: for each configured source file, extract the CSV
and truncate+load it into the matching bronze.<table>. Equivalent to
bronze.load_bronze() in 05_proc_load_bronze.sql.
"""

import time
import config
import db
import extract
import load


def run() -> None:
    print("=" * 48)
    print("Loading Bronze Layer")
    print("=" * 48)

    engine = db.get_engine(config.BRONZE_DB)
    batch_start = time.perf_counter()

    for table in config.SOURCE_FILES:
        print(f">> Extracting: {config.SOURCE_FILES[table]}")
        df = extract.extract_csv(table)

        print(f">> Truncating + loading: bronze.{table}")
        duration = load.truncate_and_load(engine, table, df)
        print(f">> Load duration: {duration:.2f} seconds")
        print(">> -------------")

    total = time.perf_counter() - batch_start
    print("=" * 48)
    print(f"Bronze layer completed in {total:.2f} seconds")
    print("=" * 48)


if __name__ == "__main__":
    run()
