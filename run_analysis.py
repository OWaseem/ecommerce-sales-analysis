"""End-to-end pipeline: clean -> load to SQLite -> SQL + pandas metrics -> charts -> reports/summary.md"""
from pathlib import Path

import pandas as pd

from analysis import charts, db, metrics
from analysis.clean import clean_orders, revenue_orders

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"


def main():
    raw = pd.read_csv(ROOT / "data" / "orders_raw.csv")
    clean, log = clean_orders(raw)
    clean.to_csv(ROOT / "data" / "orders_clean.csv", index=False)
    conn = db.load(clean, ROOT / "data" / "shop.db")
    rev = revenue_orders(clean)

    monthly = db.run(conn, "monthly_revenue")
    cat = db.run(conn, "revenue_by_category")
    top = db.run(conn, "top_products")
    country = db.run(conn, "revenue_by_country")
    status = db.run(conn, "return_and_cancel_rate")
    k = metrics.kpis(rev)
    repeat = metrics.repeat_customer_rate(rev)
    rfm = metrics.rfm(rev)
    ret = metrics.cohort_retention(rev)

    REPORTS.mkdir(exist_ok=True)
    charts.monthly_revenue(monthly, REPORTS / "monthly_revenue.png")
    charts.category_revenue(cat, REPORTS / "category_revenue.png")
    charts.cohort_heatmap(ret, REPORTS / "cohort_retention.png")
    charts.rfm_segments(rfm, REPORTS / "rfm_segments.png")

    best = monthly.loc[monthly["revenue"].idxmax()]
    worst = monthly.loc[monthly["revenue"].idxmin()]
    holiday = monthly[monthly["month"].isin(["2025-11", "2025-12"])]["revenue"].sum() / monthly["revenue"].sum()
    m1 = ret[1].mean() if 1 in ret.columns else float("nan")
    seg = rfm["segment"].value_counts()
    champ_rev = rfm[rfm["segment"] == "Champions"]["monetary"].sum() / rfm["monetary"].sum()

    lines = ["# Findings", "",
             "All figures are computed from the synthetic dataset by `run_analysis.py`.", "",
             "## Data cleaning", ""] + [f"- {k_.replace('_', ' ')}: {v}" for k_, v in log.steps.items()] + [
             "", "## Headline KPIs (completed orders)", "",
             f"- Revenue: ${k['revenue']:,.2f} across {k['orders']:,} orders and {k['customers']:,} customers",
             f"- Average order value: ${k['avg_order_value']:,.2f}",
             f"- Repeat customer rate: {repeat:.1%}", "",
             "## What the data shows", "",
             f"- **Seasonality:** {best['month']} was the strongest month (${best['revenue']:,.0f}) and {worst['month']} the weakest "
             f"(${worst['revenue']:,.0f}). November and December together account for {holiday:.0%} of annual revenue.",
             f"- **Category mix:** {cat.iloc[0]['category']} leads with {cat.iloc[0]['pct_of_revenue']}% of revenue.",
             f"- **Top product:** {top.iloc[0]['product_name']} (${top.iloc[0]['revenue']:,.0f}).",
             f"- **Geography:** {country.iloc[0]['country']} generates the most revenue (${country.iloc[0]['revenue']:,.0f}).",
             f"- **Returns and cancellations:** " + ", ".join(f"{r.status} {r.pct_of_orders}%" for r in status.itertuples()) + " of orders.",
             f"- **Retention:** on average {m1:.1%} of a cohort orders again in the month after their first order.",
             f"- **RFM segments:** " + ", ".join(f"{s} {n}" for s, n in seg.items()) + f". Champions drive {champ_rev:.0%} of customer revenue.", "",
             "## Charts", "",
             "![Monthly revenue](monthly_revenue.png)", "", "![Category revenue](category_revenue.png)", "",
             "![Cohort retention](cohort_retention.png)", "", "![RFM segments](rfm_segments.png)", ""]
    (REPORTS / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
