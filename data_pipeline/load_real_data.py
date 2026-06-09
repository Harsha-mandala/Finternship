import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import sqlite3, pandas as pd, json, os

ROOT    = r'd:\Finternship'
DB_PATH = os.path.join(ROOT, 'hotel_aditya.db')
CSV_PATH = os.path.join(ROOT, 'cleaned_sales_data.csv')
FESTIVALS_JSON = os.path.join(ROOT, 'data', 'festivals_2026.json')

SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_sales (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    item_name       TEXT NOT NULL,
    qty_sold        INTEGER NOT NULL,
    gross_revenue   REAL,
    source          TEXT DEFAULT 'pdf_import'
);
CREATE TABLE IF NOT EXISTS menu_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name       TEXT UNIQUE NOT NULL,
    category        TEXT,
    unit_price      REAL,
    is_perishable   INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS weather_data (
    date        TEXT PRIMARY KEY,
    max_temp    REAL,
    min_temp    REAL,
    condition   TEXT,
    rainfall_mm REAL
);
CREATE TABLE IF NOT EXISTS festivals (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT NOT NULL,
    name              TEXT NOT NULL,
    type              TEXT,
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

# Delete and recreate DB fresh
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print('[OK] Old DB removed')

conn = sqlite3.connect(DB_PATH)
conn.executescript(SCHEMA)
conn.commit()
print('[OK] Tables created')

# Load CSV
df = pd.read_csv(CSV_PATH)
print(f'[INFO] CSV loaded: {len(df)} rows, {df["item_name"].nunique()} items, {df["date"].nunique()} days')

# Add source column if missing
if 'source' not in df.columns:
    df['source'] = 'pdf_import'

# Load daily_sales
df[['date','item_name','qty_sold','gross_revenue','source']].to_sql('daily_sales', conn, if_exists='append', index=False)
print(f'[OK] {len(df)} rows loaded into daily_sales')

# Load menu_items with category + compute unit_price
items_df = df.groupby('item_name').agg(
    category=('category', 'first'),
    unit_price=('gross_revenue', lambda x: (x / df.loc[x.index, 'qty_sold']).median())
).reset_index()
for _, row in items_df.iterrows():
    conn.execute(
        'INSERT OR IGNORE INTO menu_items (item_name, category, unit_price) VALUES (?,?,?)',
        (row['item_name'], row['category'], round(row['unit_price'], 2))
    )
conn.commit()
print(f'[OK] {len(items_df)} unique items loaded into menu_items')

# Load festivals
with open(FESTIVALS_JSON, encoding='utf-8') as f:
    festivals = json.load(f)
conn.execute('DELETE FROM festivals')
for fest in festivals:
    conn.execute('INSERT INTO festivals (date, name, type, demand_multiplier) VALUES (?,?,?,?)',
        (fest['date'], fest['name'], fest.get('type','national'), fest.get('demand_multiplier', 1.0)))
conn.commit()
print(f'[OK] {len(festivals)} festivals loaded')

# Summary
print()
print('=== DATABASE SUMMARY ===')
for t in ['daily_sales','menu_items','weather_data','festivals','recommendations']:
    cnt = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'  {t:<25} {cnt:>6} rows')

date_range = conn.execute('SELECT MIN(date), MAX(date) FROM daily_sales').fetchone()
print(f'  Date range: {date_range[0]} to {date_range[1]}')
print(f'  DB: {DB_PATH}')
conn.close()
print('[DONE] Real data loaded successfully!')
