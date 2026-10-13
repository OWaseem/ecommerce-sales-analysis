# E-Commerce Sales Analysis (SQL + Python)

An end-to-end analysis of a year of online-store orders: clean messy raw data, load it into SQLite, answer business questions with SQL, then use pandas for customer segmentation and retention and produce charts and a written summary.

**The dataset is synthetic.** `scripts/generate_data.py` creates about 6,000 order lines (seeded, so it is reproducible) and deliberately injects realistic problems: duplicate rows, missing and inconsistently written countries, invalid quantities, and mixed date formats. The findings describe that generated data and are not real business results.

## Pipeline

```
orders_raw.csv  ->  analysis/clean.py  ->  SQLite (orders_clean)  ->  sql/queries.sql
                                    \->  analysis/metrics.py (KPIs, RFM, cohorts)  ->  charts + reports/summary.md
```

1. **Clean** (`analysis/clean.py`): remove duplicates, parse mixed date formats, standardize country names, drop invalid quantities and prices, and record how many rows each step changed.
2. **Query** (`sql/queries.sql`): monthly revenue, revenue by category and country, top products, top customers, and cancel/return rates.
3. **Analyze** (`analysis/metrics.py`):
   - KPIs: revenue, orders, average order value, repeat-customer rate
   - **RFM segmentation:** recency, frequency, and monetary quintile scores grouped into Champions, Loyal, At Risk, Potential, and Lapsed
   - **Cohort retention:** share of each first-order-month cohort that orders again in later months (months that have not happened yet are shown as unobserved, not zero)
4. **Report:** four charts and `reports/summary.md`, with every number computed by the code.

## Run it

```bash
pip install -r requirements.txt
python scripts/generate_data.py
python run_analysis.py        # writes reports/summary.md and four PNG charts
pytest -q
```

## Example findings (from the synthetic data)

- Revenue is concentrated in the holiday months: November and December together account for about 36% of the year.
- Electronics is the largest category at about 42% of revenue, led by the Smart Watch.
- About 43% of customers ordered more than once, but only about 22% order again in the month right after their first purchase.
- "Champions" are the smallest RFM segment yet generate about a quarter of customer revenue.

See `reports/summary.md` for the full output and charts.

## Tests

7 tests cover each cleaning step and its log, the revenue definition (cancelled orders excluded), a check that the SQL totals match the pandas totals, RFM score ranges, cohort retention math (including unobserved months), and the repeat-customer rate.

## Structure

```
analysis/   clean.py  metrics.py  db.py  charts.py
sql/        queries.sql
scripts/    generate_data.py
tests/      test_analysis.py
reports/    summary.md and charts
run_analysis.py
```

## Limitations

Synthetic data has no real seasonality, pricing, or customer behavior beyond what the generator encodes, so the value of this project is the method (cleaning, SQL, segmentation, cohorts), not the conclusions. Built with AI assistance (Claude); I reviewed and ran all of the code.
