import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis import db, metrics  # noqa: E402
from analysis.clean import clean_orders, revenue_orders  # noqa: E402


def raw_frame():
    return pd.DataFrame({
        "order_id": ["O1", "O1", "O2", "O3", "O4", "O5"],
        "order_date": ["2025-01-05", "2025-01-05", "01/20/2025", "2025-02-02", "2025-02-10", "not a date"],
        "customer_id": ["C1", "C1", "C1", "C2", "C3", "C4"],
        "country": ["united states", "united states", " CANADA ", None, "Germany", "India"],
        "product_id": ["P1"] * 6, "product_name": ["Lamp"] * 6, "category": ["Home"] * 6,
        "quantity": [2, 2, 1, -1, 3, 1],
        "unit_price": [10.0, 10.0, 10.0, 10.0, 5.0, 5.0],
        "status": ["completed", "completed", "completed", "completed", "cancelled", "completed"],
    })


def test_cleaning_steps_and_log():
    clean, log = clean_orders(raw_frame())
    assert log.steps["duplicate_rows_removed"] == 1
    assert log.steps["invalid_quantity_rows_dropped"] == 1
    assert log.steps["unparseable_dates_dropped"] == 1
    assert set(clean["country"]) <= {"United States", "Canada", "Germany", "India", "Unknown"}
    assert pd.api.types.is_datetime64_any_dtype(clean["order_date"])
    assert (clean["line_total"] == clean["quantity"] * clean["unit_price"]).all()


def test_revenue_excludes_cancelled():
    clean, _ = clean_orders(raw_frame())
    rev = revenue_orders(clean)
    assert "cancelled" not in set(rev["status"])
    assert metrics.kpis(rev)["revenue"] == pytest.approx(rev["line_total"].sum())


def test_sql_matches_pandas():
    clean, _ = clean_orders(raw_frame())
    conn = db.load(clean, ":memory:")
    sql_total = db.run(conn, "monthly_revenue")["revenue"].sum()
    assert sql_total == pytest.approx(revenue_orders(clean)["line_total"].sum())


def test_rfm_scores_in_range_and_every_customer_has_segment():
    rows = []
    for i in range(30):
        for j in range(1 + i % 5):
            rows.append({"order_id": f"O{i}-{j}", "customer_id": f"C{i}", "order_date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i * 5 + j),
                         "line_total": 10.0 * (i + 1)})
    out = metrics.rfm(pd.DataFrame(rows))
    assert len(out) == 30
    assert out[["R", "F", "M"]].stack().between(1, 5).all()
    assert out["segment"].notna().all()


def test_cohort_retention_first_period_is_one():
    rev = pd.DataFrame({
        "customer_id": ["A", "A", "B", "C"],
        "order_date": pd.to_datetime(["2025-01-03", "2025-02-04", "2025-01-10", "2025-02-01"]),
    })
    ret = metrics.cohort_retention(rev)
    assert (ret[0] == 1).all()
    assert ret.loc["2025-01", 1] == pytest.approx(0.5)  # A returned in Feb, B did not


def test_repeat_rate():
    rev = pd.DataFrame({"customer_id": ["A", "A", "B"], "order_id": ["1", "2", "3"]})
    assert metrics.repeat_customer_rate(rev) == pytest.approx(0.5)


def test_cohort_future_months_are_nan_not_zero():
    rev = pd.DataFrame({
        "customer_id": ["A", "B"],
        "order_date": pd.to_datetime(["2025-01-03", "2025-03-10"]),
    })
    ret = metrics.cohort_retention(rev)
    assert ret.loc["2025-03"].isna().sum() == len(ret.columns) - 1  # March cohort can only be observed at age 0
