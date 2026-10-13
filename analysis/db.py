"""Load cleaned data into SQLite and run the named queries in sql/queries.sql."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "queries.sql"


def load(clean: pd.DataFrame, db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    out = clean.copy()
    out["order_date"] = out["order_date"].dt.strftime("%Y-%m-%d")
    out.to_sql("orders_clean", conn, if_exists="replace", index=False)
    return conn


def named_queries(path=SQL_FILE) -> dict:
    text = Path(path).read_text()
    parts = re.split(r"--\s*name:\s*(\w+)\s*\n", text)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def run(conn, name: str) -> pd.DataFrame:
    return pd.read_sql_query(named_queries()[name], conn)
