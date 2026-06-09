"""
explore_data.py — Person 2 / Analysis
=======================================
Exploratory Data Analysis of Hotel Aditya Grand sales data.
Run this AFTER setup_and_load_db.py has populated the DB.

Outputs:
  - Console: key stats, top items, DOW patterns, volatile items
  - PNG files: charts saved to analysis/charts/
  - dow_multipliers.csv: pre-computed DOW factors (used by recommender)

Run: py explore_data.py
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless — no GUI needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, sys

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.join(_HERE, "..")
DB_PATH = os.environ.get("DB_PATH", os.path.join(ROOT, "hotel_aditya.db"))
CHARTS_DIR = os.path.join(_HERE, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Style
plt.rcParams.update({
    "figure.facecolor": "#0F1117",
    "axes.facecolor":   "#1A1D27",
    "axes.edgecolor":   "#2E3450",
    "axes.labelcolor":  "#8B90B0",
    "xtick.color":      "#8B90B0",
    "ytick.color":      "#8B90B0",
    "text.color":       "#F0F2FF",
    "grid.color":       "#2E3450",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
})
BRAND_ORANGE = "#E8531A"


def load_data(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("""
        SELECT ds.date, ds.item_name, ds.qty_sold, ds.gross_revenue, mi.category
        FROM daily_sales ds
        LEFT JOIN menu_items mi ON ds.item_name = mi.item_name
        WHERE ds.source = 'pdf_import' OR ds.source = 'manual'
        ORDER BY ds.date
    """, conn)
    conn.close()
    df["date"]        = pd.to_datetime(df["date"])
    df["day_of_week"] = df["date"].dt.day_name()
    df["dow_num"]     = df["date"].dt.weekday     # 0=Mon
    df["week"]        = df["date"].dt.isocalendar().week
    return df


def section(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")


# ── Analysis functions ─────────────────────────────────────────────────────────

def overview(df: pd.DataFrame):
    section("1. OVERVIEW")
    print(f"  Date range : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"  Days       : {df['date'].nunique()}")
    print(f"  Unique items: {df['item_name'].nunique()}")
    print(f"  Total records: {len(df):,}")
    print(f"  Total qty sold: {df['qty_sold'].sum():,}")
    daily_rev = df.groupby("date")["gross_revenue"].sum()
    print(f"\n  Daily Revenue:")
    print(f"    Min: ₹{daily_rev.min():,.0f}")
    print(f"    Max: ₹{daily_rev.max():,.0f}")
    print(f"    Avg: ₹{daily_rev.mean():,.0f}")


def top_items(df: pd.DataFrame, n=20):
    section(f"2. TOP {n} ITEMS BY TOTAL QTY")
    top = df.groupby("item_name")["qty_sold"].sum().sort_values(ascending=False).head(n)
    for i, (item, qty) in enumerate(top.items(), 1):
        print(f"  {i:>2}. {item:<35} {qty:>5} units")

    # Chart
    fig, ax = plt.subplots(figsize=(10, 7))
    top_rev = df.groupby("item_name")["qty_sold"].sum().sort_values().tail(15)
    colors  = [BRAND_ORANGE if i == len(top_rev)-1 else "#3B4468" for i in range(len(top_rev))]
    top_rev.plot(kind="barh", ax=ax, color=colors)
    ax.set_title("Top 15 Items by Total Qty Sold", fontsize=14, color="#F0F2FF", pad=10)
    ax.set_xlabel("Total Qty", color="#8B90B0")
    ax.grid(axis="x")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "top_items.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"\n  Chart saved → {path}")


def dow_analysis(df: pd.DataFrame) -> pd.DataFrame:
    section("3. DAY-OF-WEEK SALES PATTERNS")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    # Total qty by day
    dow_qty = df.groupby("day_of_week")["qty_sold"].sum().reindex(day_order)
    print("\n  Total qty sold by day:")
    for day, qty in dow_qty.items():
        bar = "█" * int(qty // (dow_qty.max() / 30))
        print(f"  {day:<12} {bar} {qty:,}")

    # DOW multipliers per item (for the recommender)
    item_overall = df.groupby("item_name")["qty_sold"].mean().rename("overall_avg")
    item_dow     = df.groupby(["item_name","day_of_week"])["qty_sold"].mean().rename("dow_avg")
    dow_mult     = item_dow.reset_index().merge(item_overall.reset_index(), on="item_name")
    dow_mult["dow_multiplier"] = (dow_mult["dow_avg"] / dow_mult["overall_avg"]).round(3)
    dow_mult.to_csv(os.path.join(_HERE, "dow_multipliers.csv"), index=False)
    print(f"\n  ✅ dow_multipliers.csv saved → {os.path.join(_HERE, 'dow_multipliers.csv')}")

    # Chart
    fig, ax = plt.subplots(figsize=(9, 5))
    dow_mean = df.groupby("day_of_week")["qty_sold"].mean().reindex(day_order)
    colors   = [BRAND_ORANGE if d in ("Saturday","Sunday") else "#3B4468" for d in day_order]
    ax.bar(day_order, dow_mean.values, color=colors)
    ax.set_title("Average Qty Sold by Day of Week", fontsize=13, color="#F0F2FF", pad=10)
    ax.set_ylabel("Avg Qty / Item")
    ax.grid(axis="y")
    plt.xticks(rotation=20)
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "dow_patterns.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"  Chart saved → {path}")

    return dow_mult


def revenue_trend(df: pd.DataFrame):
    section("4. 30-DAY REVENUE TREND")
    daily = df.groupby("date")["gross_revenue"].sum().reset_index()
    daily["7d_rolling"] = daily["gross_revenue"].rolling(7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(daily["date"], daily["gross_revenue"], alpha=0.2, color=BRAND_ORANGE)
    ax.plot(daily["date"], daily["gross_revenue"], color=BRAND_ORANGE, linewidth=1.5, label="Daily Revenue")
    ax.plot(daily["date"], daily["7d_rolling"], color="#F59E0B", linewidth=2, linestyle="--", label="7-day avg")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.set_title("Daily Revenue Trend — Hotel Aditya Grand", fontsize=13, color="#F0F2FF", pad=10)
    ax.legend(facecolor="#1A1D27", edgecolor="#2E3450")
    ax.grid(axis="y")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "revenue_trend.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"  Chart saved → {path}")

    # week-over-week growth
    weekly = df.groupby("week")["gross_revenue"].sum()
    if len(weekly) >= 2:
        growth = (weekly.iloc[-1] / weekly.iloc[-2] - 1) * 100
        print(f"\n  Week-over-week revenue growth (last 2 weeks): {growth:+.1f}%")


def volatility_analysis(df: pd.DataFrame):
    section("5. MOST VOLATILE ITEMS (hardest to predict)")
    stats = df.groupby("item_name")["qty_sold"].agg(["mean","std","min","max","count"])
    stats["cv"] = (stats["std"] / stats["mean"]).fillna(0)   # coefficient of variation
    stats = stats[stats["count"] >= 5]    # only items with enough history
    volatile = stats.sort_values("cv", ascending=False).head(15)
    print(f"\n  {'Item':<35} {'Avg':>6} {'Std':>6} {'CV':>6}")
    print(f"  {'─'*55}")
    for item, row in volatile.iterrows():
        print(f"  {item:<35} {row['mean']:>6.1f} {row['std']:>6.1f} {row['cv']:>6.2f}")
    print("\n  Note: CV > 0.5 = high volatility — model needs more data for these items")


def category_breakdown(df: pd.DataFrame):
    section("6. SALES BY CATEGORY")
    cat_qty = df.groupby("category")["qty_sold"].sum().sort_values(ascending=False)
    cat_rev = df.groupby("category")["gross_revenue"].sum().sort_values(ascending=False)
    print(f"\n  {'Category':<15} {'Qty':>8} {'Revenue':>12}")
    print(f"  {'─'*37}")
    for cat in cat_qty.index:
        print(f"  {cat:<15} {cat_qty[cat]:>8,} ₹{cat_rev.get(cat, 0):>10,.0f}")

    # Donut chart
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = ["#E8531A","#F97316","#FBBF24","#34D399","#60A5FA","#A78BFA","#F472B6","#6EE7B7","#93C5FD","#FCA5A5","#D1FAE5"]
    wedges, texts, autotexts = ax.pie(
        cat_qty.values, labels=cat_qty.index,
        colors=colors[:len(cat_qty)],
        autopct="%1.0f%%", startangle=90,
        wedgeprops={"linewidth": 1.5, "edgecolor": "#0F1117"}
    )
    for t in texts: t.set_color("#F0F2FF")
    for t in autotexts: t.set_color("#0F1117")
    ax.set_title("Sales Mix by Category (Qty)", fontsize=13, color="#F0F2FF", pad=10)
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "category_breakdown.png")
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"\n  Chart saved → {path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🔍 Loading data from: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ DB not found! Run: py data_pipeline/setup_and_load_db.py  first.")
        sys.exit(1)

    df = load_data(DB_PATH)
    if df.empty:
        print("❌ No sales data found in DB.")
        sys.exit(1)

    overview(df)
    top_items(df)
    dow_mult = dow_analysis(df)
    revenue_trend(df)
    volatility_analysis(df)
    category_breakdown(df)

    print(f"\n{'─'*60}")
    print("✅ EDA complete!")
    print(f"   Charts → {CHARTS_DIR}")
    print(f"   DOW multipliers → analysis/dow_multipliers.csv")
    print("─"*60)


if __name__ == "__main__":
    main()
