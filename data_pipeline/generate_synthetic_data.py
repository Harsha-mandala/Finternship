"""
generate_synthetic_data.py  — Person 2 / Data Pipeline
=======================================================
Generates a realistic cleaned_sales_data.csv that mirrors the format
Person 1 will produce from the 45 real PDFs.

Data visible in actual PDFs (April 5, 2026 sample):
  - Items: Butter Naan (43!), Cool Drink, Ice Creams, Chicken dishes, Biryanis etc.
  - Grand Total that day: ₹1,02,321

Replace this CSV with Person 1's real file when ready.
Run:  py generate_synthetic_data.py
Output: ../data_pipeline/cleaned_sales_data.csv
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import random
from datetime import date, timedelta
from math import ceil

random.seed(42)
np.random.seed(42)

# ── 1. MENU CATALOGUE ─────────────────────────────────────────────────────────
# Based on actual items visible in Hotel Aditya Grand PDFs.
# base_daily = average qty on a normal weekday
# unit_price  = approximate price per item (₹)

MENU_ITEMS = [
    # ── Biryani ──────────────────────────────────────────────
    {"name": "Chicken Dum Biryani",        "category": "biryani",     "base": 16,  "price": 258},
    {"name": "Veg Biryani",                "category": "biryani",     "base": 8,   "price": 198},
    {"name": "Egg Biryani",                "category": "biryani",     "base": 6,   "price": 198},
    {"name": "Chota Cb Biryani",           "category": "biryani",     "base": 5,   "price": 149},
    {"name": "Cashewnut Biryani",          "category": "biryani",     "base": 3,   "price": 229},
    {"name": "Cashewnut Panner Biryani",   "category": "biryani",     "base": 2,   "price": 250},

    # ── Family Packs ─────────────────────────────────────────
    {"name": "CB Family Pack",             "category": "family_pack", "base": 2,   "price": 575},
    {"name": "CDB Family Pack",            "category": "family_pack", "base": 1,   "price": 650},

    # ── Chicken (BL = Boneless) ───────────────────────────────
    {"name": "Butter Chicken BL",          "category": "chicken",     "base": 7,   "price": 307},
    {"name": "Chilli Chicken BL",          "category": "chicken",     "base": 9,   "price": 307},
    {"name": "Andhra Chicken BL",          "category": "chicken",     "base": 4,   "price": 316},
    {"name": "Andhra Chicken (B)",         "category": "chicken",     "base": 2,   "price": 290},
    {"name": "Dragon Chicken",             "category": "chicken",     "base": 4,   "price": 307},
    {"name": "Kadai Chicken",              "category": "chicken",     "base": 3,   "price": 307},
    {"name": "Chicken 65",                 "category": "chicken",     "base": 6,   "price": 307},
    {"name": "Chicken Fry",                "category": "chicken",     "base": 5,   "price": 280},
    {"name": "Cashewnut Curry",            "category": "chicken",     "base": 5,   "price": 240},
    {"name": "Cashewnut Fry",              "category": "chicken",     "base": 2,   "price": 240},

    # ── Starters ─────────────────────────────────────────────
    {"name": "Chicken Lollypop 6pc",       "category": "starter",     "base": 5,   "price": 220},
    {"name": "Gobi Manchuria",             "category": "starter",     "base": 4,   "price": 180},
    {"name": "French Fries",               "category": "starter",     "base": 6,   "price": 120},

    # ── Breads ───────────────────────────────────────────────
    {"name": "Butter Naan",                "category": "bread",       "base": 40,  "price": 50},
    {"name": "Butter Roti",                "category": "bread",       "base": 8,   "price": 35},

    # ── Rice ─────────────────────────────────────────────────
    {"name": "Curd Rice",                  "category": "rice",        "base": 8,   "price": 80},
    {"name": "1 BY 2 Curd Rice",           "category": "rice",        "base": 5,   "price": 40},
    {"name": "Veg Fried Rice",             "category": "rice",        "base": 4,   "price": 150},

    # ── Beverages ────────────────────────────────────────────
    {"name": "Cool Drink 250ml",           "category": "beverage",    "base": 30,  "price": 40},
    {"name": "Lassi Sweet",                "category": "beverage",    "base": 6,   "price": 60},
    {"name": "Lassi Salt",                 "category": "beverage",    "base": 5,   "price": 60},
    {"name": "Butter Milk",                "category": "beverage",    "base": 3,   "price": 45},
    {"name": "Belgium Choco Milk Shake",   "category": "beverage",    "base": 3,   "price": 140},
    {"name": "Caramel Nuts Milk Shake",    "category": "beverage",    "base": 2,   "price": 140},

    # ── Ice Cream ────────────────────────────────────────────
    {"name": "Belgium Chocolate Ice Cream","category": "ice_cream",   "base": 6,   "price": 130},
    {"name": "Black Current Ice Cream",    "category": "ice_cream",   "base": 7,   "price": 130},
    {"name": "American Nuts Ice Cream",    "category": "ice_cream",   "base": 3,   "price": 150},
    {"name": "Caramel Nuts Ice Cream",     "category": "ice_cream",   "base": 2,   "price": 130},
    {"name": "Strawberry Ice Cream",       "category": "ice_cream",   "base": 4,   "price": 110},
    {"name": "Vanilla Ice Cream",          "category": "ice_cream",   "base": 4,   "price": 100},
    {"name": "Anjeer Badam Ice Cream",     "category": "ice_cream",   "base": 2,   "price": 150},

    # ── Seafood ──────────────────────────────────────────────
    {"name": "Fish Curry",                 "category": "seafood",     "base": 3,   "price": 280},
    {"name": "Chilli Prawns",              "category": "seafood",     "base": 2,   "price": 350},
    {"name": "Fish Appolo",                "category": "seafood",     "base": 3,   "price": 260},

    # ── Egg ──────────────────────────────────────────────────
    {"name": "Boiled Egg",                 "category": "egg",         "base": 3,   "price": 35},
    {"name": "Chicken Egg Drop",           "category": "egg",         "base": 2,   "price": 120},

    # ── Soup ─────────────────────────────────────────────────
    {"name": "Chicken Manchow Soup",       "category": "soup",        "base": 3,   "price": 120},

    # ── Paneer / Veg ─────────────────────────────────────────
    {"name": "Cashewnut Panner Curry",     "category": "veg",         "base": 3,   "price": 250},
]

# ── 2. DAY-OF-WEEK MULTIPLIERS ─────────────────────────────────────────────────
# 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
BASE_DOW = {0: 0.80, 1: 0.85, 2: 0.88, 3: 0.92, 4: 1.10, 5: 1.28, 6: 1.50}

# Category-specific Sunday boost (biryani is extra popular on weekends)
CAT_SUNDAY_BOOST = {
    "biryani":     1.25,
    "family_pack": 1.30,
    "chicken":     1.10,
    "ice_cream":   1.20,
    "beverage":    1.15,
}

# ── 3. FESTIVAL CALENDAR (April–May 2026 only, for this synthetic data) ───────
# Full calendar lives in data/festivals_2026.json
FESTIVALS_IN_RANGE = {
    "2026-04-06": 1.40,  # Ram Navami
    "2026-04-13": 1.40,  # Ugadi Eve
    "2026-04-14": 1.70,  # Ugadi — BIGGEST
    "2026-04-20": 1.30,  # Akshaya Tritiya
    "2026-05-01": 1.25,  # Labour Day
}

# ── 4. WEATHER SIMULATION ──────────────────────────────────────────────────────
# Kandukur, AP — April/May is very hot (37–43°C), pre-monsoon
# Occasional pre-monsoon showers in May
def simulate_weather(d: date):
    """Returns (temp, is_rainy) for a given date."""
    if d.month == 4:
        temp = np.random.normal(39, 2)  # April: hot and dry
        is_rainy = random.random() < 0.05  # 5% chance of rain
    else:  # May
        temp = np.random.normal(40, 2)
        is_rainy = random.random() < 0.12  # 12% chance of pre-monsoon showers
    return round(temp, 1), is_rainy

def weather_factor(category: str, temp: float, is_rainy: bool) -> float:
    """Rough weather impact on demand (same logic as category_weather_map.py)."""
    factors = {
        "beverage":   0.65 if is_rainy else (1.50 if temp > 39 else 1.20),
        "ice_cream":  0.40 if is_rainy else (1.60 if temp > 39 else 1.20),
        "soup":       1.45 if is_rainy else (0.80 if temp > 39 else 1.0),
        "biryani":    1.20 if is_rainy else 1.0,
        "chicken":    1.15 if is_rainy else 1.0,
        "family_pack":1.20 if is_rainy else 1.0,
    }
    return factors.get(category, 1.0)

# ── 5. GENERATE DATA ───────────────────────────────────────────────────────────
def generate_dates():
    """April 1 – May 15, 2026, excluding April 16–17 (missing PDFs)."""
    start = date(2026, 4, 1)
    end   = date(2026, 5, 15)
    skip  = {date(2026, 4, 16), date(2026, 4, 17)}
    d = start
    dates = []
    while d <= end:
        if d not in skip:
            dates.append(d)
        d += timedelta(days=1)
    return dates

def generate_qty(base, dow_factor, fest_factor, w_factor, noise_pct=0.20):
    """Apply all multipliers + Gaussian noise."""
    qty = base * dow_factor * fest_factor * w_factor
    noise = np.random.normal(1.0, noise_pct)
    qty = max(0, round(qty * noise))
    return int(qty)

def main():
    dates = generate_dates()
    rows = []
    for d in dates:
        dow = d.weekday()
        d_str = d.isoformat()
        dow_mult = BASE_DOW[dow]
        fest_mult = FESTIVALS_IN_RANGE.get(d_str, 1.0)
        temp, is_rainy = simulate_weather(d)

        for item in MENU_ITEMS:
            cat = item["category"]
            base = item["base"]

            # Apply DOW — with category-specific Sunday boost
            d_factor = dow_mult
            if dow == 6:  # Sunday
                d_factor *= CAT_SUNDAY_BOOST.get(cat, 1.0)

            w_factor = weather_factor(cat, temp, is_rainy)
            qty = generate_qty(base, d_factor, fest_mult, w_factor)

            if qty <= 0:
                continue  # Don't log zero-sales days (matches real PDF behaviour)

            gross = round(qty * item["price"], 2)
            rows.append({
                "date":          d_str,
                "item_name":     item["name"],
                "category":      cat,
                "qty_sold":      qty,
                "gross_revenue": gross,
                "source":        "pdf_import",
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(["date", "category", "item_name"]).reset_index(drop=True)

    output_path = "cleaned_sales_data.csv"
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated {len(df)} rows across {df['date'].nunique()} days")
    print(f"   Items: {df['item_name'].nunique()}")
    print(f"   Date range: {df['date'].min()} -> {df['date'].max()}")
    print(f"   Saved -> {output_path}")
    print()
    print("Top 10 items by total qty:")
    top = df.groupby("item_name")["qty_sold"].sum().sort_values(ascending=False).head(10)
    print(top.to_string())

if __name__ == "__main__":
    main()
