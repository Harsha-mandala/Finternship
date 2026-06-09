# 🏨 Hotel Aditya Grand — AI-Powered Kitchen Order Assistant
## Detailed Project Outline (POC)

---

## 1. Problem Statement

**Merchant**: Hotel Aditya Grand, Kandukur (Food & Residency Services)

**The Pain**: Every morning, the chef manually estimates how much of each perishable item (vegetables, dairy, raw meat, etc.) to procure — entirely from memory. This guesswork is driven by two volatile, hard-to-predict forces:
- **Occupancy fluctuations** — room bookings directly affect meals served
- **Hyper-local demand events** — sudden rains, weddings, local weekend events, festivals

**The Cost**:
- **Over-ordering** → raw food spoilage → ₹4,000–₹6,000 **weekly waste**
- **Under-ordering** → missing menu items → bad customer reviews
- High stress every morning during procurement decisions

---

## 2. The Data We Have

### Source
- **45 daily Item-wise Sales Report PDFs** from the hotel's POS/billing system (via OKEN Scanner)
- **Coverage**: April 1, 2026 → May 15, 2026 (approx. 45 days, every day except 16–17 May)
- **Special note**: Two days have `_1` suffix files (April 25, May 3) — these appear to be supplementary/corrected reports for those days

### Data Structure (per PDF)
Each daily PDF contains a table with:

| Field | Description | Example |
|---|---|---|
| **Item** | Menu item name | "CHICKEN DUM BIRYANI", "Butter Non", "COOL DRINK 250 ML" |
| **Qty** | Total quantity sold that day | 16, 22, 33 |
| **Gross** | Revenue from that item (₹) | 4,128.00 |

**Summary rows at the bottom** of each PDF:
| Field | Value |
|---|---|
| Total | ₹46,480.00 (e.g., April 1) |
| NoCash | ₹0.00 |
| Discount | ₹0.00 |
| CGST | ₹1,103.69 |
| SGST | ₹1,103.69 |
| **Grand Total** | **₹48,689.18** |

### Menu Categories Identified
From the April 1 data alone, ~80+ distinct menu items across:
- **Biryanis** — Chicken Dum Biryani, Veg Biryani, EGG BIRYANI, Chota Cb Biryani, etc.
- **Chicken dishes** — Chilli Chicken BL, Butter Chicken BL, Kadai Chicken, Andhra Chicken, Dragon Chicken, Chicken Fry, Chicken 65, etc.
- **Breads** — Butter Naan (22 sold!), Roti, etc.
- **Rice dishes** — Curd Rice, Veg Fried Rice, Biryani Rice
- **Beverages** — Cool Drink 250ml (33 sold!), Lassi Salt, Lassi Sweet, Milk Shakes (Belgium Choco, Butr Scotch)
- **Ice Creams** — American Nuts, Anjeerbadam, Strawberry, Vanilla, Chocochips
- **Starters/Snacks** — Chicken Lollypop (various), French Fries, Gobi Manchuria
- **Seafood** — Fish Curry, Chilli Prawns, Fish Appolo
- **Soups** — Chicken Manchow Soup
- **Eggs** — Boiled Egg, Egg Biryani, Chicken Egg Drop
- **Family Packs** — CB FAMILY PACK, CDB FAMILLY PACK

### Key Insight from Data
> The data contains **what was SOLD**, not what was ordered or wasted. This is the "cold start" challenge — we have strong signal on demand (sold qty) but no direct wastage data yet.

---

## 3. The Solution — What We're Building

### Vision
> *"A daily AI assistant that tells the merchant exactly how much of each item to order tomorrow — by automatically reading tomorrow's weather, upcoming local festivals, and their own past sales patterns."*

### POC Scope (3-week build)
A **mobile-friendly web app** where:
1. The merchant can **log daily sales** (quantities sold per item)
2. The system **automatically pulls** tomorrow's weather + upcoming festivals for Kandukur/Nellore district
3. An AI engine generates **next-day order recommendations** per item
4. The merchant reviews and optionally adjusts the recommendation

---

## 4. Solving the Cold Start Problem

> **Panel feedback**: *"Users prefer value first before making more investment."*

Since we have 45 days of historical sales data, we can **pre-populate** the system with real data before the merchant ever touches the app. This eliminates the cold start wall entirely.

### Strategy:
- **Phase 0 (Before Launch)**: Parse all 45 PDFs → extract item-level daily quantities → load into the database as historical records
- **On Day 1 of use**: The merchant opens the app and already sees:
  - Trend charts for their top items
  - A recommendation based on 45 days of real history + tomorrow's weather
- **Value delivered immediately** — no data entry needed to get the first useful output

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Web App)                    │
│  Mobile-friendly PWA • Next.js or plain HTML/JS/CSS      │
├──────────────┬───────────────┬──────────────────────────┤
│  Dashboard   │  Log Sales    │  Tomorrow's Orders       │
│  (trends,    │  (quick item  │  (AI recommendations     │
│   revenue)   │   qty input)  │   with weather context)  │
└──────────────┴───────────────┴──────────────────────────┘
                        │
              ┌─────────▼──────────┐
              │   Backend API       │
              │  (Node.js/Python)   │
              └──┬──────────┬───┬──┘
                 │          │   │
        ┌────────▼──┐  ┌───▼───▼──────────┐
        │  Database  │  │  External APIs    │
        │ (SQLite or │  │  • Weather API    │
        │  Supabase) │  │    (OpenWeather   │
        └────────────┘  │    or similar)    │
                        │  • Festival/      │
                        │    Calendar API   │
                        └──────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   AI/ML Recommendation    │
                    │   Engine                  │
                    │   • Weighted moving avg   │
                    │   • Weather adjustment    │
                    │   • Festival multiplier   │
                    │   • Day-of-week patterns  │
                    └───────────────────────────┘
```

---

## 6. Feature Breakdown

### Feature 1 — Historical Data Ingestion (Pre-launch)
- Parse all 45 PDF files using PyMuPDF + OCR (or Google Vision API)
- Extract: `date`, `item_name`, `qty_sold`, `gross_revenue`
- Normalize item names (handle duplicates like "Chota Cb Biryani" vs "CB FAMILY PACK")
- Store in database as historical sales records

### Feature 2 — Dashboard (Home Screen)
- **Top items by quantity** this week / this month
- **Revenue trend** chart (last 30 days)
- **Day-of-week pattern** — e.g., "Sundays sell 2.3x more Biryani"
- **Weather widget** — tomorrow's forecast for Kandukur
- **Upcoming festivals/events** banner

### Feature 3 — Daily Sales Logging
- Simple mobile-first UI: item list with qty input
- Pre-fills with yesterday's quantities as a quick starting point
- Items sorted by popularity (most ordered first)
- Optional: quick +/- stepper buttons per item
- Auto-saves to database

### Feature 4 — Next-Day Order Recommendations ⭐
- **Core output**: "Tomorrow, order X units of [Item]"
- Recommendation logic:
  - **Base**: 7-day rolling average for that item
  - **Day-of-week multiplier**: e.g., if Sundays are 30% busier
  - **Weather adjustment**: Rain → +20% soups, -30% cold drinks; Hot day → +40% cold drinks, ice cream
  - **Festival multiplier**: Major festivals → +50-100% across non-veg items
  - **Trend adjustment**: If item is trending up/down over last 3 days
- Output displayed as a clean table: Item | Recommended Qty | Reason
- Merchant can override with a simple tap+edit

### Feature 5 — Auto-enrichment
- **Weather API**: Daily auto-fetch for Kandukur/Nellore (OpenWeatherMap free tier)
- **Festival data**: Pre-loaded calendar for 2026 Indian festivals + local Andhra Pradesh events
- Both enrichments happen automatically — zero effort from merchant

### Feature 6 — Waste Tracker (Future / Phase 2)
- After Phase 1 proves value, add: "What was leftover today?" input
- This closes the loop: ordered → sold → wasted
- Enables true wastage-minimization optimization

---

## 7. Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **Frontend** | HTML + Vanilla JS + CSS (or Next.js) | Fast to build, mobile-friendly |
| **Charts** | Chart.js | Lightweight, beautiful |
| **Backend** | Python (FastAPI) or Node.js | Quick API development |
| **Database** | SQLite (local) → Supabase (hosted) | Simple start, easy scale |
| **PDF Parsing** | PyMuPDF + pytesseract OCR | Already installed on system |
| **Weather** | OpenWeatherMap API (free tier) | 1000 calls/day free |
| **Festival data** | Static JSON calendar | Sufficient for POC |
| **AI/ML** | Python (NumPy/Pandas) + simple rules | No GPU needed for POC |
| **Hosting** | Vercel (frontend) + Render (backend) | Free tier suitable for POC |

---

## 8. Database Schema

```sql
-- Historical and ongoing daily sales
CREATE TABLE daily_sales (
  id INTEGER PRIMARY KEY,
  date DATE NOT NULL,
  item_name TEXT NOT NULL,
  qty_sold INTEGER NOT NULL,
  gross_revenue REAL,
  source TEXT DEFAULT 'manual'  -- 'pdf_import' or 'manual'
);

-- Menu item catalog (normalized)
CREATE TABLE menu_items (
  id INTEGER PRIMARY KEY,
  item_name TEXT UNIQUE NOT NULL,
  category TEXT,  -- 'biryani', 'chicken', 'beverage', etc.
  unit_price REAL,
  is_perishable BOOLEAN DEFAULT TRUE
);

-- Weather data (auto-fetched)
CREATE TABLE weather_data (
  date DATE PRIMARY KEY,
  max_temp REAL,
  min_temp REAL,
  condition TEXT,  -- 'sunny', 'rainy', 'cloudy'
  rainfall_mm REAL
);

-- Festival calendar
CREATE TABLE festivals (
  date DATE NOT NULL,
  name TEXT NOT NULL,
  type TEXT,  -- 'national', 'regional', 'local'
  demand_multiplier REAL DEFAULT 1.0
);

-- Order recommendations (generated)
CREATE TABLE recommendations (
  id INTEGER PRIMARY KEY,
  date DATE NOT NULL,  -- recommendation FOR this date
  item_name TEXT NOT NULL,
  recommended_qty INTEGER,
  base_qty REAL,
  weather_factor REAL,
  festival_factor REAL,
  day_factor REAL,
  merchant_override INTEGER  -- if merchant edited it
);
```

---

## 9. Data Pipeline (PDF → Database)

```
45 PDF files
     │
     ▼
PyMuPDF renders each page as image
     │
     ▼
pytesseract OCR extracts text
     │
     ▼
Parser: regex to extract Item | Qty | Gross rows
     │
     ▼
Name normalizer: fuzzy match + manual mapping
(e.g., "chi lolypop 6 pic" == "Chicken Lollypop 6pc")
     │
     ▼
SQLite insertion: daily_sales table
     │
     ▼
45 days × ~80 items = ~3,600 clean records ready for analysis
```

---

## 10. Recommendation Algorithm (v1 — Rule-Based ML)

```python
def get_recommendation(item, target_date):
    # 1. Base: 7-day rolling average
    base = avg_sales(item, last_n_days=7)
    
    # 2. Day-of-week factor
    dow = target_date.weekday()
    dow_factor = compute_dow_multiplier(item, dow)
    
    # 3. Weather factor
    weather = get_weather(target_date)
    weather_factor = compute_weather_factor(item, weather)
    
    # 4. Festival factor
    festival = get_festival(target_date)
    festival_factor = festival.demand_multiplier if festival else 1.0
    
    # 5. Final recommendation
    recommended_qty = base * dow_factor * weather_factor * festival_factor
    
    # 6. Add buffer (e.g., +10% to avoid under-ordering)
    return ceil(recommended_qty * 1.1)
```

---

## 11. Mobile UI — Key Screens

### Screen 1: Home Dashboard
- Header: "Good morning, Hotel Aditya Grand 🌅"
- Tomorrow's weather card: "🌧️ Rain expected — boosting soup & hot food orders"
- Today's revenue summary
- Top 5 items by qty chart

### Screen 2: Today's Recommendations
- Card list: [Item] → Recommend [X] units → [Reason icon]
- Example: "🍗 Chicken Dum Biryani → Order **18** units (↑ from avg 16, Sunday uplift)"
- Example: "🥤 Cool Drink 250ml → Order **25** units (↓ from avg 33, rain expected)"
- One-tap "Looks good" confirmation or edit qty

### Screen 3: Log Yesterday's Sales
- Simple form: item list with qty fields
- "Import from PDF" button (future feature)
- Save button

### Screen 4: Trends & Insights
- 30-day chart per item
- Best/worst selling days
- Revenue by category (Biryanis vs Beverages vs Chicken, etc.)

---

## 12. Implementation Roadmap

### Week 1 — Foundation
- [ ] Set up project repo + basic web app shell
- [ ] Write PDF parser script (PyMuPDF + OCR)
- [ ] Extract and clean all 45 days of data
- [ ] Set up SQLite database with schema
- [ ] Basic dashboard UI with hardcoded data

### Week 2 — Core Intelligence
- [ ] Integrate OpenWeatherMap API for Kandukur
- [ ] Build recommendation engine (rule-based)
- [ ] Pre-load festival calendar for 2026
- [ ] Wire up recommendation screen with real data
- [ ] Sales logging screen

### Week 3 — Polish & Demo
- [ ] Mobile-responsive design polish
- [ ] Add trend charts (Chart.js)
- [ ] End-to-end flow testing
- [ ] Record demo session with Marripudi Akhil
- [ ] Prepare GitHub repo + send to finternship@okcredit.in

---

## 13. Success Metrics

| Metric | Target |
|---|---|
| Recommendation accuracy | Within ±20% of actual daily sales |
| Time saved for chef | < 5 min to review tomorrow's orders (vs. guesswork) |
| Waste reduction (projected) | 30-50% reduction in over-ordering |
| Weekly savings (projected) | ₹1,500–₹3,000 of the ₹4,000–₹6,000 waste |
| App load time | < 2 seconds on mobile |
| Merchant adoption | Akhil confirms usefulness after demo |

---

## 14. Open Questions / Risks

> [!IMPORTANT]
> **Confirm POC scope with Marripudi Akhil** before building — especially the weather + festival auto-enrichment feature. Does he understand and approve this approach?

> [!WARNING]
> **Item name normalization** is non-trivial. The 45 PDFs likely have inconsistent naming ("chi lolypop 6 pic" vs "Chicken Lolypop 6 pes" vs "Chicken Lollypop Biryani"). A fuzzy matching + manual review pass is needed before the data is usable.

> [!NOTE]
> **No wastage data exists yet**. The 45 days only show what was *sold*. The app should be designed to start collecting wastage data from Day 1 of use, but the initial recommendations will be purely demand-based (not waste-minimizing).

> [!NOTE]
> **16-17 April 2026 data is missing** from the dataset. This is a 2-day gap that should be noted but doesn't significantly affect model quality.
