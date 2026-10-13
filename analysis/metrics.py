"""Business metrics: KPIs, RFM customer segmentation, and monthly cohort retention."""
import pandas as pd


def kpis(rev: pd.DataFrame) -> dict:
    orders = rev.groupby("order_id")["line_total"].sum()
    return {
        "revenue": round(float(rev["line_total"].sum()), 2),
        "orders": int(orders.shape[0]),
        "customers": int(rev["customer_id"].nunique()),
        "avg_order_value": round(float(orders.mean()), 2),
        "units_sold": int(rev["quantity"].sum()),
    }


def repeat_customer_rate(rev: pd.DataFrame) -> float:
    per_customer = rev.groupby("customer_id")["order_id"].nunique()
    return float((per_customer > 1).mean())


def rfm(rev: pd.DataFrame, as_of=None) -> pd.DataFrame:
    """Recency / Frequency / Monetary scores (1-5 quintiles) and a simple segment label."""
    as_of = as_of or rev["order_date"].max() + pd.Timedelta(days=1)
    g = rev.groupby("customer_id").agg(
        last_order=("order_date", "max"), frequency=("order_id", "nunique"), monetary=("line_total", "sum"))
    g["recency"] = (as_of - g["last_order"]).dt.days

    def score(s, ascending):
        # rank first so ties never collapse the quantile bins
        return pd.qcut(s.rank(method="first", ascending=ascending), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    g["R"] = score(g["recency"], ascending=False)    # recent = high score
    g["F"] = score(g["frequency"], ascending=True)
    g["M"] = score(g["monetary"], ascending=True)

    def segment(r):
        if r["R"] >= 4 and r["F"] >= 4 and r["M"] >= 4:
            return "Champions"
        if r["R"] >= 3 and r["F"] >= 3:
            return "Loyal"
        if r["R"] <= 2 and r["F"] >= 3:
            return "At Risk"
        if r["R"] <= 2:
            return "Lapsed"
        return "Potential"

    g["segment"] = g.apply(segment, axis=1)
    return g.reset_index()


def cohort_retention(rev: pd.DataFrame) -> pd.DataFrame:
    """Rows = month of a customer's first order; columns = months since; values = share still ordering."""
    d = rev[["customer_id", "order_date"]].copy()
    d["order_month"] = d["order_date"].dt.to_period("M")
    d["cohort"] = d.groupby("customer_id")["order_month"].transform("min")
    d["age"] = (d["order_month"] - d["cohort"]).apply(lambda x: x.n)
    counts = d.groupby(["cohort", "age"])["customer_id"].nunique().unstack(fill_value=0)
    retention = counts.div(counts[0], axis=0)
    last = d["order_month"].max()
    for cohort in retention.index:  # months after the end of the data are unobserved, not zero
        max_age = (last - cohort).n
        retention.loc[cohort, [a for a in retention.columns if a > max_age]] = float("nan")
    retention.index = retention.index.astype(str)
    return retention
