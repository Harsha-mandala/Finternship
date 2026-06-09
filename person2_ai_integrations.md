# 👤 Person 2 — AI/ML Engineer + External Integrations
## Hotel Aditya Grand · AI Kitchen Order Assistant · POC

---

> **Your Role**: You are the brain of the project.
> You take Person 1's clean historical data + real-world signals (weather, festivals)
> and turn them into smart, explainable next-day order recommendations.
> Person 3's UI is only as good as the recommendations you generate.

---

## 🎯 What You Own

| Area | Your Responsibility |
|---|---|
| Data Analysis | Explore 45 days of sales data, find patterns |
| Weather Integration | Fetch daily weather for Kandukur via OpenWeatherMap API |
| Festival Calendar | Build the 2026 Indian + AP festival JSON dataset |
| Recommendation Engine | Build the core algorithm that generates order quantities |
| Recommendation API Route | Write the `/recommendations/` endpoint in the backend |
| Accuracy Validation | Test your predictions against known historical data |

---

## 📦 Your Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Primary language |
| **pandas** | Data analysis and pattern extraction |
| **numpy** | Mathematical operations |
| **requests** | Call OpenWeatherMap API |
| **sqlite3** | Read from the shared DB (created by Person 1) |
| **matplotlib / seaborn** | Visualize patterns (for your own analysis) |
| **FastAPI** | Add your recommendation route to shared backend |
| **python-dotenv** | Store API keys safely in `.env` file |

```bash
pip install pandas numpy requests matplotlib seaborn python-dotenv
```

---

## 📁 Your Folder Structure

```
project/
├── backend/
│   ├── routes/
│   │   └── recommendations.py   ← YOUR main file in shared backend
│   └── engine/
│       ├── recommender.py        ← Core recommendation logic
│       ├── weather_service.py    ← OpenWeatherMap integration
│       └── festival_service.py  ← Festival calendar lookup
├── analysis/
│   ├── explore_data.ipynb        ← Your Jupyter notebook for EDA
│   ├── dow_analysis.py           ← Day-of-week pattern analysis
│   └── category_weather_map.py   ← Weather → category impact rules
├── data/
│   └── festivals_2026.json       ← Festival calendar you build
└── .env                          ← API keys (never commit this!)
```

---

## 📅 Week-by-Week Task Breakdown

---

### ✅ WEEK 1 — Data Analysis & Understanding Patterns

Wait for Person 1 to deliver `cleaned_sales_data.csv` and `hotel_aditya.db`.
Once you have them, do the following exploration.

#### Day 1–2: Exploratory Data Analysis (EDA)

Open a Jupyter notebook (`explore_data.ipynb`) and run these analyses:

```python
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Load from CSV
df = pd.read_csv("cleaned_sales_data.csv")
df['date'] = pd.to_datetime(df['date'])
df['day_of_week'] = df['date'].dt.day_name()
df['week_number'] = df['date'].dt.isocalendar().week

print("Date range:", df['date'].min(), "→", df['date'].max())
print("Total unique items:", df['item_name'].nunique())
print("Total sales records:", len(df))
print("\nTop 20 items by total qty sold:")
print(df.groupby('item_name')['qty_sold'].sum().sort_values(ascending=False).head(20))
```

**Key questions to answer from your analysis:**

1. **Which 10 items sell the most overall?** (These are the critical ones to recommend accurately)
2. **What day of week has highest total sales?** (Friday? Sunday?)
3. **Is there a week-over-week growth trend?** (Hotel getting busier over April→May?)
4. **Which items have the most volatile sales?** (High std deviation = hardest to predict)
5. **Are there obvious outlier days?** (Sudden spike could be a festival/event)

```python
# Day-of-week analysis
dow_totals = df.groupby('day_of_week')['qty_sold'].sum()
print("\nSales by day of week:\n", dow_totals.sort_values(ascending=False))

# Item volatility
item_stats = df.groupby('item_name')['qty_sold'].agg(['mean','std','min','max'])
item_stats['cv'] = item_stats['std'] / item_stats['mean']  # Coefficient of variation
print("\nMost volatile items (hard to predict):")
print(item_stats.sort_values('cv', ascending=False).head(15))
```

---

#### Day 2–3: Day-of-Week Pattern Analysis

This is the foundation of your recommendation engine. Every item sells differently on different days.

```python
# day-of-week averages per item
dow_avg = df.groupby(['item_name', 'day_of_week'])['qty_sold'].mean().reset_index()
dow_avg.columns = ['item_name', 'day_of_week', 'avg_qty_on_dow']

# Overall average per item
overall_avg = df.groupby('item_name')['qty_sold'].mean().reset_index()
overall_avg.columns = ['item_name', 'overall_avg']

# Merge to get multiplier = (avg on that day) / (overall avg)
dow_merged = dow_avg.merge(overall_avg, on='item_name')
dow_merged['dow_multiplier'] = dow_merged['avg_qty_on_dow'] / dow_merged['overall_avg']

# Save to DB / CSV for use in recommendation engine
dow_merged.to_csv("dow_multipliers.csv", index=False)
print(dow_merged[dow_merged['item_name'] == 'Chicken Dum Biryani'])
```

**Expected insight example**:
> Chicken Dum Biryani: Monday avg = 12, Sunday avg = 20, Overall avg = 15
> → Sunday multiplier = 1.33 (33% more on Sundays)

---

#### Day 3–4: Build Festival Calendar (`festivals_2026.json`)

Manually research and build this JSON file. These are the key dates that impact Hotel Aditya Grand (Kandukur, Andhra Pradesh):

```json
[
  {"date": "2026-04-06", "name": "Ram Navami", "type": "national", "demand_multiplier": 1.4},
  {"date": "2026-04-14", "name": "Ambedkar Jayanti / Telugu New Year", "type": "regional", "demand_multiplier": 1.5},
  {"date": "2026-04-15", "name": "Baisakhi / Vishu", "type": "national", "demand_multiplier": 1.3},
  {"date": "2026-05-01", "name": "May Day / Labour Day", "type": "national", "demand_multiplier": 1.2},
  {"date": "2026-05-23", "name": "Buddha Purnima", "type": "national", "demand_multiplier": 1.2},
  {"date": "2026-06-17", "name": "Eid al-Adha", "type": "national", "demand_multiplier": 1.6},
  {"date": "2026-08-15", "name": "Independence Day", "type": "national", "demand_multiplier": 1.3},
  {"date": "2026-08-19", "name": "Raksha Bandhan", "type": "national", "demand_multiplier": 1.2},
  {"date": "2026-09-17", "name": "Ganesh Chaturthi", "type": "regional", "demand_multiplier": 1.5},
  {"date": "2026-10-02", "name": "Gandhi Jayanti / Dussehra", "type": "national", "demand_multiplier": 1.3},
  {"date": "2026-10-20", "name": "Diwali", "type": "national", "demand_multiplier": 1.5},
  {"date": "2026-11-08", "name": "Diwali (Bali Pratipada)", "type": "national", "demand_multiplier": 1.3}
]
```

Also add **local events** if you know of any:
- Kandukur local fair/jatara dates
- Cricket match days (IPL finals, India matches)
- Weekend before/after major festivals (often see uplift too)

Add these with `demand_multiplier` between 1.1–1.2.

Load this into the DB:
```python
import json, sqlite3

with open("data/festivals_2026.json") as f:
    festivals = json.load(f)

conn = sqlite3.connect("hotel_aditya.db")
cur = conn.cursor()
for f in festivals:
    cur.execute(
        "INSERT OR REPLACE INTO festivals (date, name, type, demand_multiplier) VALUES (?,?,?,?)",
        (f['date'], f['name'], f['type'], f['demand_multiplier'])
    )
conn.commit()
conn.close()
print(f"Loaded {len(festivals)} festivals into DB")
```

---

### ✅ WEEK 2 — Build the Recommendation Engine

#### Day 1–2: Weather Service (`weather_service.py`)

Get a **free API key** from [openweathermap.org](https://openweathermap.org/api) (takes 2 minutes).

```python
# weather_service.py
import requests
import os
from datetime import date, timedelta
import sqlite3
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Kandukur"
COUNTRY_CODE = "IN"

def fetch_weather_for_tomorrow():
    """Fetch tomorrow's forecast and store in DB"""
    url = f"https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{CITY},{COUNTRY_CODE}",
        "appid": API_KEY,
        "units": "metric",
        "cnt": 8  # 8 x 3-hour slots = next 24 hours
    }
    response = requests.get(url, params=params)
    data = response.json()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    temps = [item['main']['temp'] for item in data['list'][:8]]
    conditions = [item['weather'][0]['main'] for item in data['list'][:8]]
    rainfall = sum(item.get('rain', {}).get('3h', 0) for item in data['list'][:8])

    weather_record = {
        "date": tomorrow,
        "max_temp": max(temps),
        "min_temp": min(temps),
        "condition": max(set(conditions), key=conditions.count),  # most common condition
        "rainfall_mm": rainfall
    }

    # Save to DB
    conn = sqlite3.connect("hotel_aditya.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO weather_data (date, max_temp, min_temp, condition, rainfall_mm)
        VALUES (:date, :max_temp, :min_temp, :condition, :rainfall_mm)
    """, weather_record)
    conn.commit()
    conn.close()
    return weather_record

def get_weather_for_date(target_date: str):
    """Get weather from DB for a given date"""
    conn = sqlite3.connect("hotel_aditya.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM weather_data WHERE date = ?", (target_date,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"date": row[0], "max_temp": row[1], "min_temp": row[2], 
                "condition": row[3], "rainfall_mm": row[4]}
    return None
```

**.env file** (add to `.gitignore`!):
```
OPENWEATHER_API_KEY=your_key_here
```

---

#### Day 2–3: Weather → Food Demand Rules (`category_weather_map.py`)

This is the **core intelligence** of your system. Research and define how weather affects each food category:

```python
# category_weather_map.py

def compute_weather_factor(category: str, weather: dict) -> float:
    """
    Returns a multiplier (e.g. 1.3 = 30% more, 0.7 = 30% less)
    based on weather conditions for a food category.
    """
    condition = weather.get("condition", "Clear").lower()
    max_temp = weather.get("max_temp", 30)
    rainfall = weather.get("rainfall_mm", 0)

    is_rainy = rainfall > 2 or "rain" in condition
    is_hot = max_temp > 36
    is_cold = max_temp < 24  # cool day for Kandukur

    factors = {
        "biryani":    1.2 if is_rainy else (1.1 if is_hot else 1.0),
        "chicken":    1.15 if is_rainy else 1.0,
        "soup":       1.4 if is_rainy else (1.1 if is_cold else 0.9),
        "beverage":   0.7 if is_rainy else (1.5 if is_hot else 1.1),
        "ice_cream":  0.5 if is_rainy else (1.6 if is_hot else 1.0),
        "bread":      1.0 if is_rainy else 1.0,
        "rice":       1.1 if is_rainy else 1.0,
        "starter":    0.9 if is_rainy else 1.0,
        "seafood":    1.0,  # stable demand
        "egg":        1.1 if is_rainy else 1.0,
        "family_pack":1.2 if is_rainy else 1.0,
    }

    return factors.get(category, 1.0)
```

---

#### Day 3–4: Core Recommender (`recommender.py`)

```python
# engine/recommender.py
import sqlite3
import pandas as pd
import numpy as np
from math import ceil
from datetime import datetime
from weather_service import get_weather_for_date
from category_weather_map import compute_weather_factor

DB_PATH = "hotel_aditya.db"

DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def get_item_category(item_name: str, conn) -> str:
    cur = conn.cursor()
    cur.execute("SELECT category FROM menu_items WHERE item_name = ?", (item_name,))
    row = cur.fetchone()
    return row[0] if row and row[0] else "other"

def get_rolling_avg(item_name: str, target_date: str, days: int, conn) -> float:
    """Get average qty sold for item in the last N days before target date"""
    cur = conn.cursor()
    cur.execute("""
        SELECT AVG(qty_sold) FROM daily_sales
        WHERE item_name = ?
          AND date < ?
        ORDER BY date DESC
        LIMIT ?
    """, (item_name, target_date, days))
    row = cur.fetchone()
    return float(row[0]) if row and row[0] else 0.0

def get_dow_multiplier(item_name: str, target_dow: int, conn) -> float:
    """Compute how much more/less this item sells on target day vs average"""
    cur = conn.cursor()
    # Get avg on target day of week
    cur.execute("""
        SELECT AVG(qty_sold) FROM daily_sales
        WHERE item_name = ?
          AND strftime('%w', date) = ?
    """, (item_name, str(target_dow % 7)))
    dow_avg = cur.fetchone()[0] or 0

    # Get overall avg
    cur.execute("SELECT AVG(qty_sold) FROM daily_sales WHERE item_name = ?", (item_name,))
    overall_avg = cur.fetchone()[0] or 1

    return (dow_avg / overall_avg) if overall_avg > 0 else 1.0

def get_festival_multiplier(target_date: str, conn) -> tuple[float, str]:
    """Check if target date has a festival"""
    cur = conn.cursor()
    cur.execute("SELECT demand_multiplier, name FROM festivals WHERE date = ?", (target_date,))
    row = cur.fetchone()
    if row:
        return row[0], row[1]
    return 1.0, None

def get_trend_factor(item_name: str, target_date: str, conn) -> float:
    """Check if item has been trending up or down over last 3 days"""
    cur = conn.cursor()
    cur.execute("""
        SELECT qty_sold FROM daily_sales
        WHERE item_name = ? AND date < ?
        ORDER BY date DESC LIMIT 3
    """, (item_name, target_date))
    recent = [row[0] for row in cur.fetchall()]
    if len(recent) < 2:
        return 1.0
    # Simple: if last 2 days trend is up, add 5% buffer
    if recent[0] > recent[-1]:
        return 1.05
    elif recent[0] < recent[-1]:
        return 0.97
    return 1.0

def generate_recommendations(target_date: str) -> list[dict]:
    """
    Generate next-day order recommendations for all menu items.
    target_date: the date you want recommendations FOR (YYYY-MM-DD)
    """
    conn = sqlite3.connect(DB_PATH)
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_dow = target_dt.weekday()  # 0=Monday, 6=Sunday

    # Get weather
    weather = get_weather_for_date(target_date)

    # Get festival
    festival_multiplier, festival_name = get_festival_multiplier(target_date, conn)

    # Get all items
    cur = conn.cursor()
    cur.execute("SELECT item_name FROM menu_items ORDER BY item_name")
    items = [row[0] for row in cur.fetchall()]

    recommendations = []
    for item_name in items:
        base_avg = get_rolling_avg(item_name, target_date, days=7, conn=conn)
        if base_avg == 0:
            continue  # Skip items with no recent history

        dow_factor = get_dow_multiplier(item_name, target_dow, conn)
        category = get_item_category(item_name, conn)
        weather_factor = compute_weather_factor(category, weather) if weather else 1.0
        trend_factor = get_trend_factor(item_name, target_date, conn)

        raw_qty = base_avg * dow_factor * weather_factor * festival_multiplier * trend_factor
        final_qty = ceil(raw_qty * 1.1)  # +10% safety buffer

        # Build reason string for UI display
        reasons = []
        if dow_factor > 1.05:
            reasons.append(f"↑ {DAY_NAMES[target_dow]} uplift")
        elif dow_factor < 0.95:
            reasons.append(f"↓ Slow {DAY_NAMES[target_dow]}")
        if weather and weather_factor != 1.0:
            reasons.append(f"{'↑' if weather_factor > 1 else '↓'} Weather ({weather['condition']})")
        if festival_name:
            reasons.append(f"🎉 {festival_name}")

        recommendations.append({
            "item_name": item_name,
            "category": category,
            "recommended_qty": final_qty,
            "base_avg": round(base_avg, 1),
            "dow_factor": round(dow_factor, 2),
            "weather_factor": round(weather_factor, 2),
            "festival_factor": festival_multiplier,
            "trend_factor": round(trend_factor, 2),
            "reason": " | ".join(reasons) if reasons else "Based on 7-day average"
        })

    # Sort by category then item name
    recommendations.sort(key=lambda x: (x['category'], x['item_name']))
    conn.close()
    return recommendations
```

---

#### Day 4–5: Hook Up to FastAPI Route (`routes/recommendations.py`)

```python
# routes/recommendations.py
from fastapi import APIRouter
from engine.recommender import generate_recommendations
from weather_service import fetch_weather_for_tomorrow
import sqlite3
from datetime import date, timedelta

router = APIRouter()

@router.get("/")
def get_recommendations(target_date: str = None):
    """Get order recommendations for a given date (defaults to tomorrow)"""
    if not target_date:
        target_date = (date.today() + timedelta(days=1)).isoformat()

    # Auto-fetch weather for that date
    try:
        fetch_weather_for_tomorrow()
    except Exception as e:
        print(f"Weather fetch failed: {e}")

    recommendations = generate_recommendations(target_date)
    return {
        "date": target_date,
        "total_items": len(recommendations),
        "recommendations": recommendations
    }

@router.put("/override")
def override_recommendation(item_name: str, date: str, merchant_qty: int):
    """Save merchant's manual override of a recommendation"""
    conn = sqlite3.connect("hotel_aditya.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE recommendations
        SET merchant_override = ?
        WHERE item_name = ? AND date = ?
    """, (merchant_qty, item_name, date))
    conn.commit()
    conn.close()
    return {"status": "override saved", "item": item_name, "qty": merchant_qty}
```

---

### ✅ WEEK 3 — Validation, Testing & Accuracy Check

#### Back-test Your Algorithm

The most important week for you: **prove your algorithm works**.

Use the last 7 days of data (May 9–15) as your test set. Train on days before that.

```python
# validation.py
import pandas as pd
import sqlite3
from engine.recommender import generate_recommendations

TEST_DATES = ["2026-05-09","2026-05-10","2026-05-11",
              "2026-05-12","2026-05-13","2026-05-14","2026-05-15"]

conn = sqlite3.connect("hotel_aditya.db")
results = []

for test_date in TEST_DATES:
    recs = generate_recommendations(test_date)
    # Get actual sales for that date
    cur = conn.cursor()
    cur.execute("SELECT item_name, qty_sold FROM daily_sales WHERE date = ?", (test_date,))
    actuals = {row[0]: row[1] for row in cur.fetchall()}

    for rec in recs:
        actual = actuals.get(rec['item_name'], None)
        if actual is not None:
            error = abs(rec['recommended_qty'] - actual) / actual * 100
            results.append({
                "date": test_date,
                "item": rec['item_name'],
                "predicted": rec['recommended_qty'],
                "actual": actual,
                "error_pct": round(error, 1)
            })

df = pd.DataFrame(results)
print("Mean Absolute % Error:", df['error_pct'].mean())
print("Items within 20% accuracy:", (df['error_pct'] <= 20).sum(), "/", len(df))
print("\nWorst predicted items:")
print(df.sort_values('error_pct', ascending=False).head(10))
```

**Target**: Mean error < 25%, at least 70% of items within ±20% accuracy.

If accuracy is poor, tune:
- Increase rolling window from 7 to 14 days
- Adjust weather multipliers
- Check if specific items have outlier days skewing the average

---

## 📤 What You Hand Off to Others

| Deliverable | Goes to | Deadline |
|---|---|---|
| `dow_multipliers.csv` | Person 1 (to load to DB) | End of Week 1 |
| `festivals_2026.json` | Person 1 (to load to DB) | End of Week 1 |
| `/recommendations/` API endpoint | Person 3 (frontend) | End of Week 2 |
| API response format documentation | Person 3 | Start of Week 2 |
| Validation accuracy report | Everyone (for demo) | End of Week 3 |

---

## 📌 API Response Format for Person 3

Your `/recommendations/?date=2026-06-06` must return exactly this format:

```json
{
  "date": "2026-06-06",
  "total_items": 82,
  "recommendations": [
    {
      "item_name": "Chicken Dum Biryani",
      "category": "biryani",
      "recommended_qty": 18,
      "base_avg": 14.5,
      "dow_factor": 1.15,
      "weather_factor": 1.2,
      "festival_factor": 1.0,
      "trend_factor": 1.05,
      "reason": "↑ Friday uplift | ↑ Weather (Rain)"
    }
  ]
}
```

---

## ✅ Final Deliverables Checklist

- [ ] EDA notebook with key insights documented
- [ ] `festivals_2026.json` with 15+ entries loaded into DB
- [ ] Weather service fetching live data for Kandukur
- [ ] `recommender.py` working end-to-end
- [ ] `/recommendations/` API endpoint returning correct format
- [ ] Back-test validation showing < 25% mean error
- [ ] Weather → category impact rules documented
