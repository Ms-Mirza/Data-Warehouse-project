"""
Load: truncate a table and bulk-insert a DataFrame into it. Equivalent to
the TRUNCATE + BULK INSERT / INSERT INTO ... SELECT steps in the original
SQL Server stored procedures.
"""

import time

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def truncate_and_load(
    engine: Engine,
    table: str,
    df: pd.DataFrame,
    chunksize: int = 5000,
) -> float:
    """
    Truncate `table` (unqualified name; the engine is already bound to the
    right database) and insert `df` into it. Returns the duration in seconds.
    """
    start = time.perf_counter()

    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table}"))

    df.to_sql(
        table,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=chunksize,
        method="multi",
    )

    return time.perf_counter() - start
