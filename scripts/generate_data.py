"""Generate a SYNTHETIC e-commerce order-line dataset with deliberate data-quality problems.

Output: data/orders_raw.csv (one row per order line). Seeded, so results are reproducible.
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data"

CATALOG = {
    "Electronics": [("Wireless Earbuds", 59.0), ("USB-C Hub", 34.5), ("Smart Watch", 149.0), ("Portable Charger", 29.0)],
    "Home": [("Desk Lamp", 24.0), ("Coffee Maker", 79.0), ("Throw Blanket", 32.0), ("Storage Bins", 18.0)],
    "Fitness": [("Yoga Mat", 28.0), ("Resistance Bands", 16.0), ("Water Bottle", 22.0), ("Dumbbell Set", 89.0)],
    "Books": [("Data Science Handbook", 39.0), ("Cooking Basics", 21.0), ("Mystery Novel", 14.0)],
}
COUNTRIES = ["United States", "Canada", "United Kingdom", "Germany", "India"]
COUNTRY_WEIGHTS = [0.55, 0.12, 0.13, 0.1, 0.1]
MONTH_WEIGHT = {1: 0.8, 2: 0.7, 3: 0.9, 4: 0.9, 5: 1.0, 6: 1.0, 7: 0.95, 8: 1.0, 9: 1.05, 10: 1.1, 11: 1.6, 12: 1.9}


def main(n_customers=3500, n_orders=4200):
    products = []
    i = 0
    for cat, items in CATALOG.items():
        for name, price in items:
            i += 1
            products.append((f"P{i:03d}", name, cat, price))
    days = [date(2025, 1, 1) + timedelta(days=k) for k in range(365)]
    day_weights = [MONTH_WEIGHT[d.month] for d in days]
    customers = []
    for cid in range(1, n_customers + 1):
        signup = random.choices(days, day_weights)[0]
        customers.append((f"C{cid:04d}", signup, random.choices(COUNTRIES, COUNTRY_WEIGHTS)[0]))
    rows = []
    for oid in range(1, n_orders + 1):
        cid, signup, country = random.choice(customers)
        d = signup + timedelta(days=int(random.expovariate(1 / 45)))
        if d.year != 2025:
            d = signup
        status = random.choices(["completed", "cancelled", "returned"], [0.9, 0.06, 0.04])[0]
        for _ in range(random.choices([1, 2, 3], [0.65, 0.25, 0.10])[0]):
            pid, name, cat, price = random.choice(products)
            rows.append({"order_id": f"O{oid:05d}", "order_date": d.isoformat(), "customer_id": cid, "country": country,
                         "product_id": pid, "product_name": name, "category": cat,
                         "quantity": random.choices([1, 2, 3, 4], [0.7, 0.2, 0.07, 0.03])[0],
                         "unit_price": price, "status": status})
    df = pd.DataFrame(rows).sort_values("order_id").reset_index(drop=True)
    n = len(df)

    # --- inject data-quality problems ---
    n = len(df)
    dup = df.sample(frac=0.02, random_state=3)
    df = pd.concat([df, dup]).reset_index(drop=True)                       # exact duplicate rows
    df.loc[df.sample(frac=0.03, random_state=4).index, "country"] = None   # missing country
    messy = df.sample(frac=0.05, random_state=5).index
    df.loc[messy, "country"] = df.loc[messy, "country"].map(lambda c: f" {c.upper()} " if isinstance(c, str) else c)  # casing/whitespace
    df.loc[df.sample(frac=0.01, random_state=6).index, "quantity"] = -1    # invalid quantity
    mixed = df.sample(frac=0.08, random_state=7).index
    df.loc[mixed, "order_date"] = pd.to_datetime(df.loc[mixed, "order_date"]).dt.strftime("%m/%d/%Y")  # mixed date format
    df = df.sample(frac=1.0, random_state=8).reset_index(drop=True)
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "orders_raw.csv", index=False)
    print(f"wrote {len(df)} raw rows (from {n} clean rows) to {OUT / 'orders_raw.csv'}")


if __name__ == "__main__":
    main()
