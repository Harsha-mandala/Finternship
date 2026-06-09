"""
setup_and_load_db.py - Person 2 / Data Pipeline
================================================
Standalone script: creates the SQLite DB tables and loads the
synthetic (or real) cleaned_sales_data.csv.

Run from the data_pipeline/ folder:
    py setup_and_load_db.py

Or specify a custom CSV path:
    py setup_and_load_db.py --csv path/to/cleaned_sales_data.csv

When Person 1 delivers the real cleaned_sales_data.csv:
  - Simply run this script again (or Person 1's load_to_db.py)
  - The DB will be rebuilt with real data
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import pandas as pd
import json
import os
import sys
import argparse

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.join(_HERE, "..")
DB_PATH = os.environ.get("DB_PATH", os.path.join(ROOT, "hotel_aditya.db"))
DEFAULT_CSV = os.path.join(_HERE, "cleaned_sales_data.csv")
FESTIVALS_JSON = os.path.join(ROOT, "data", "festivals_2026.json")


# ── Schema ─────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_sales (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    item_name       TEXT NOT NULL,
    qty_sold        INTEGER NOT NULL,
    gross_revenue   REAL,
    source          TEXT DEFAULT 'manual'
);

CREATE TABLE IF NOT EXISTS menu_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name       TEXT UNIQUE NOT NULL,
    category        TEXT,
    unit_price      REAL,
    is_perishable   INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS weather_data (
    date            TEXT PRIMARY KEY,
    max_temp        REAL,
    min_temp        REAL,
    condition       TEXT,
    rainfall_mm     REAL
);

CREATE TABLE IF NOT EXISTS festivals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    name            TEXT NOT NULL,
    type            TEXT,
    demand_multiplier REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS recommendations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT NOT NULL,
    item_name         TEXT NOT NULL,
    recommended_qty   INTEGER,
    base_qty          REAL,
    weather_factor    REAL,
    festival_factor   REAL,
    day_factor        REAL,
    merchant_override INTEGER,
    UNIQUE(date, item_name)
);

CREATE INDEX IF NOT EXISTS idx_sales_date      ON daily_sales(date);
CREATE INDEX IF NOT EXISTS idx_sales_item      ON daily_sales(item_name);
CREATE INDEX IF NOT EXISTS idx_sales_date_item ON daily_sales(date, item_name);
"""


def create_tables(conn: sqlite3.Connection):
    conn.executescript(SCHEMA)
    conn.commit()
    print("✅ Tables created (or already exist).")


def load_sales_csv(conn: sqlite3.Connection, csv_path: str):
    print(f"\n📂 Loading sales data from: {csv_path}")
    df = pd.read_csv(csv_path)
    required_cols = {"date", "item_name", "qty_sold"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"❌ CSV missing required columns: {missing}")
        sys.exit(1)

    # Ensure optional columns exist
    if "gross_revenue" not in df.columns:
        df["gross_revenue"] = None
    if "category" not in df.columns:
        df["category"] = "other"
    if "source" not in df.columns:
        df["source"] = "pdf_import"

    # ── daily_sales ────────────────────────────────────────────────────────────
    conn.execute("DELETE FROM daily_sales WHERE source = 'pdf_import'")  # fresh load
    sales_df = df[["date", "item_name", "qty_sold", "gross_revenue", "source"]].copy()
    sales_df.to_sql("daily_sales", conn, if_exists="append", index=False)
    print(f"   ✅ Loaded {len(sales_df):,} rows into daily_sales")

    # ── menu_items (unique items with category) ────────────────────────────────
    items_df = (
        df[["item_name", "category"]]
        .drop_duplicates("item_name")
        .rename(columns={"category": "category"})
    )
    for _, row in items_df.iterrows():
        conn.execute("""
            INSERT OR IGNORE INTO menu_items (item_name, category)
            VALUES (?, ?)
        """, (row["item_name"], row["category"]))
    conn.commit()
    print(f"   ✅ Loaded {len(items_df):,} unique items into menu_items")


def load_festivals(conn: sqlite3.Connection, json_path: str):
    if not os.path.exists(json_path):
        print(f"⚠️  festivals_2026.json not found at {json_path} — skipping.")
        return
    with open(json_path, encoding="utf-8") as f:
        festivals = json.load(f)

    conn.execute("DELETE FROM festivals")   # fresh load
    for fest in festivals:
        conn.execute("""
            INSERT INTO festivals (date, name, type, demand_multiplier)
            VALUES (?, ?, ?, ?)
        """, (fest["date"], fest["name"], fest.get("type", "national"),
              fest.get("demand_multiplier", 1.0)))
    conn.commit()
    print(f"\n✅ Loaded {len(festivals)} festivals into festivals table")


def print_summary(conn: sqlite3.Connection):
    print("\n── Database Summary ──────────────────────────────────────────")
    tables = ["daily_sales", "menu_items", "weather_data", "festivals", "recommendations"]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"   {t:<20} → {count:>6} rows")

    date_range = conn.execute(
        "SELECT MIN(date), MAX(date) FROM daily_sales"
    ).fetchone()
    print(f"\n   Sales date range: {date_range[0]} → {date_range[1]}")
    print(f"   DB location: {DB_PATH}")
    print("─" * 60)


def main():
    parser = argparse.ArgumentParser(description="Set up Hotel Aditya Grand DB")
    parser.add_argument("--csv",  default=DEFAULT_CSV, help="Path to cleaned_sales_data.csv")
    parser.add_argument("--db",   default=DB_PATH,     help="Path to SQLite DB file")
    args = parser.parse_args()

    db_path = args.db
    csv_path = args.csv

    if not os.path.exists(csv_path):
        print(f"⚠️  CSV not found at {csv_path}")
        print("   Generating synthetic data first...")
        import subprocess
        gen_script = os.path.join(_HERE, "generate_synthetic_data.py")
        subprocess.run([sys.executable, gen_script], check=True)

    print(f"\n🗄️  Setting up database at: {db_path}")
    conn = sqlite3.connect(db_path)

    create_tables(conn)
    load_sales_csv(conn, csv_path)
    load_festivals(conn, FESTIVALS_JSON)
    print_summary(conn)
    conn.close()
    print("\n🎉 Database ready! You can now run the FastAPI backend.")


if __name__ == "__main__":
    main()
