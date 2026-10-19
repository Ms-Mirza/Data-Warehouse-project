"""
Extract: read a source CSV into a DataFrame, aligned to a bronze table's
column names. Equivalent to the "E" in the original BULK INSERT step.
"""

import pandas as pd
import config


def extract_csv(table_name: str) -> pd.DataFrame:
    """Read the CSV mapped to `table_name` and return it as a DataFrame."""
    path = config.SOURCE_FILES[table_name]
    columns = config.BRONZE_COLUMNS[table_name]

    if not path.exists():
        raise FileNotFoundError(
            f"Source file for '{table_name}' not found at {path}. "
            "Check DATA_DIR in your .env file."
        )

    # header=0 skips the CSV's own header row; names=columns applies our
    # bronze column names in the order config.BRONZE_COLUMNS defines.
    df = pd.read_csv(path, header=0, names=columns)
    return df
