import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def monthly_revenue(df, path):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["month"], df["revenue"], color="#2a6f97")
    ax.set_title("Monthly revenue (completed orders)")
    ax.set_ylabel("Revenue ($)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def category_revenue(df, path):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(df["category"][::-1], df["revenue"][::-1], color="#468faf")
    ax.set_title("Revenue by category")
    ax.set_xlabel("Revenue ($)")
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def cohort_heatmap(retention, path):
    data = np.ma.masked_invalid(retention.iloc[:, :9].to_numpy(dtype=float))
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("#eeeeee")  # grey = not yet observable
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=0.5, aspect="auto")
    ax.set_xticks(range(data.shape[1])); ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels(retention.index)
    ax.set_xlabel("Months since first order"); ax.set_ylabel("Cohort (first order month)")
    ax.set_title("Customer retention by cohort")
    fig.colorbar(im, ax=ax, label="Share of cohort ordering (grey = not yet observable)")
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def rfm_segments(rfm_df, path):
    counts = rfm_df["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index, counts.values, color="#76b7b2")
    ax.set_title("Customers by RFM segment"); ax.set_ylabel("Customers")
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)
