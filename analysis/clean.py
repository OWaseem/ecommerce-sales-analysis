"""Data cleaning with an explicit log of what was changed."""
from dataclasses import dataclass, field
from typing import Dict, Tuple

import pandas as pd


@dataclass
class CleaningLog:
    steps: Dict[str, int] = field(default_factory=dict)

    def add(self, name: str, n: int):
        self.steps[name] = int(n)


def clean_orders(raw: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningLog]:
    log = CleaningLog()
    df = raw.copy()
    log.add("rows_raw", len(df))

    before = len(df)
    df = df.drop_duplicates()
    log.add("duplicate_rows_removed", before - len(df))

    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    log.add("unparseable_dates_dropped", df["order_date"].isna().sum())
    df = df.dropna(subset=["order_date"])

    df["country"] = df["country"].astype("string").str.strip().str.title()
    df["country"] = df["country"].replace({"United States Of America": "United States", "Usa": "United States", "Uk": "United Kingdom"})
    log.add("missing_country_filled_unknown", df["country"].isna().sum())
    df["country"] = df["country"].fillna("Unknown").astype(str)

    bad_qty = (df["quantity"] <= 0) | df["quantity"].isna()
    log.add("invalid_quantity_rows_dropped", bad_qty.sum())
    df = df[~bad_qty]

    bad_price = (df["unit_price"] <= 0) | df["unit_price"].isna()
    log.add("invalid_price_rows_dropped", bad_price.sum())
    df = df[~bad_price]

    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    log.add("rows_clean", len(df))
    return df.reset_index(drop=True), log


def revenue_orders(clean: pd.DataFrame) -> pd.DataFrame:
    """Rows that count as revenue: completed orders only (cancelled and returned are excluded)."""
    return clean[clean["status"] == "completed"].copy()
