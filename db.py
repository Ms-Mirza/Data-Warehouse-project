"""
SQLAlchemy engine helpers. One engine per database (bronze / silver / gold),
since MySQL keeps them as separate databases (see 01_init_database.sql).
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import config


def get_engine(database: str) -> Engine:
    """Create a SQLAlchemy engine connected to the given MySQL database."""
    url = (
        f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}/{database}"
        "?charset=utf8mb4"
    )
    return create_engine(url, pool_pre_ping=True)
