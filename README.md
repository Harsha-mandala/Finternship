# 🏨 Hotel Aditya Grand — AI Kitchen Order Assistant
### OkCredit × Google Internship POC · Team Project

> **Problem**: Small restaurant owners over-order or under-order daily stock by guessing — leading to food wastage or lost revenue.
>
> **Solution**: An AI-powered mobile web app that analyzes 45 days of real sales data and generates next-day order recommendations, adjusted for day-of-week patterns, local weather, and upcoming festivals.

---

## 📱 The App

**Live at**: `http://localhost:8000` (after starting the server)

| Screen | What it does |
|---|---|
| 📊 **Dashboard** | Today's revenue, top 5 items, 14-day revenue trend, weather |
| 🧠 **Orders** | Tomorrow's AI recommendations grouped by category with ±qty overrides |
| ✏️ **Log Sales** | Enter actual quantities sold (with search + category filter) |
| 📈 **Trends** | 30-day revenue chart, DOW pattern, category breakdown, item deep-dive |

---

## 🚀 Quick Start

### 1. Start the server
```bash
# Windows — double-click
start_server.bat

# Or manually
cd backend
py -m uvicorn main:app --reload --port 8000
```

### 2. Open the app
Open your browser at: **http://localhost:8000**

> The app auto-falls back to mock data if the server is offline, so the frontend always loads.

---

## 📁 Project Structure

```
Finternship/
│
├── 📂 backend/                    ← FastAPI server (Person 2 + support)
│   ├── main.py                    ← App entry point, all routes registered
│   ├── requirements.txt
│   ├── engine/
│   │   ├── recommender.py         ← Core AI recommendation engine
│   │   ├── weather_service.py     ← OpenWeatherMap integration
│   │   ├── festival_service.py    ← Telugu festival calendar
│   │   └── category_weather_map.py← Weather × category multipliers
│   └── routes/
│       ├── recommendations.py     ← /recommendations/* endpoints
│       └── dashboard.py           ← (reference only, routes are in main.py)
│
├── 📂 frontend/                   ← Mobile PWA (Person 3)
│   ├── index.html
│   ├── css/
│   │   ├── reset.css
│   │   ├── tokens.css             ← Design tokens (colors, spacing, radii)
│   │   └── components.css         ← All UI components
│   └── js/
│       ├── api.js                 ← Central API module + mock data fallback
│       ├── app.js                 ← Navigation, init, toast, API status
│       ├── dashboard.js           ← Dashboard screen
│       ├── recommendations.js     ← Orders screen (most important)
│       ├── log-sales.js           ← Log Sales screen
│       └── trends.js              ← Analytics screen
│
├── 📂 data_pipeline/              ← Person 1 scripts (data ingestion)
│   ├── load_real_data.py          ← Builds hotel_aditya.db from CSV
│   └── setup_and_load_db.py
│
├── 📂 analysis/                   ← Person 2 validation scripts
│   ├── explore_data.py            ← EDA on real data
│   ├── validation.py              ← Back-test MAPE accuracy
│   └── charts/                   ← Generated charts (PNG)
│
├── 📂 data/
│   └── festivals_2026.json        ← Telugu festival calendar
│
├── hotel_aditya.db                ← SQLite database (45 days, 223 items)
├── cleaned_sales_data.csv         ← Real data from Person 1
├── start_server.bat               ← One-click Windows launcher
└── vercel.json                    ← Frontend deployment config
```

---

## 🤖 How the AI Works

The recommendation engine in [`recommender.py`](backend/engine/recommender.py) uses a **4-factor multiplicative model**:

```
recommended_qty = base_avg × dow_factor × weather_factor × festival_factor × trend_factor
```

| Factor | What it does |
|---|---|
| **base_avg** | Median of last 7 appearances (median used for volatile items with CV > 0.7) |
| **dow_factor** | Day-of-week multiplier learned from real sales (Sun = 1.8×, Mon = 0.55×) |
| **weather_factor** | Weather × category rules (e.g. hot weather boosts beverages +40%) |
| **festival_factor** | +25–50% uplift if a major Telugu festival is within 1–2 days |
| **trend_factor** | Recent 3-day trend vs 7-day avg (detects growing/declining demand) |

---

## 📊 Data

- **Source**: Hotel Aditya Grand, Kandukur (real POS data)
- **Period**: 45 days (April 1 – May 15, 2026)
- **Records**: 2,500 sales rows
- **Items**: 223 unique menu items across 13 categories
- **Top earner**: Biryani (₹8.9L total)
- **Peak day**: Sunday (4,037 units avg)

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | DB health check |
| GET | `/dashboard/summary` | Today's revenue + weather |
| GET | `/dashboard/revenue-trend?days=30` | Daily revenue series |
| GET | `/dashboard/category-trends` | Revenue by category |
| GET | `/items/` | All 223 menu items |
| GET | `/sales/?date=YYYY-MM-DD` | Sales for a date |
| POST | `/sales/log` | Log today's actual sales |
| GET | `/sales/trends?item=NAME` | 30-day item trend |
| GET | `/recommendations/?date=YYYY-MM-DD` | AI recommendations |
| GET | `/recommendations/context?date=DATE` | Weather + festival context |
| PUT | `/recommendations/override` | Save merchant's qty override |
| GET | `/recommendations/accuracy` | Back-test accuracy report |

**Full interactive docs**: http://localhost:8000/docs

---

## 🎨 Design System

- **Background**: `#0F1117` (near-black)
- **Brand**: `#E8531A` (saffron-orange)
- **Font**: Outfit (headings) + Inter (body)
- **Style**: Dark glassmorphism, mobile-first (375px+)

---

## 👥 Team Roles

| Person | Role | Key Deliverable |
|---|---|---|
| **Person 1** | Data Engineering | `cleaned_sales_data.csv`, data pipeline |
| **Person 2** | AI & Backend | Recommendation engine, validation |
| **Person 3** | Frontend & Demo | Mobile PWA, API integration, this README |

---

## 📋 Week 8 Submission Checklist

- [x] 45 days of real sales data loaded
- [x] AI engine running on real data
- [x] All 4 screens built and working
- [x] Backend API with 12 endpoints
- [x] Mock data fallback (works offline)
- [x] Validation accuracy chart generated → `analysis/charts/validation_accuracy.png`
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Loom demo video recorded
- [ ] GitHub repo submitted

---

## 🚀 Deployment

### Backend → Render (free tier)
1. Push this folder to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Set root to `backend/`, build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Upload `hotel_aditya.db` as a persistent disk at `/data/hotel_aditya.db`
6. Set env var: `DB_PATH=/data/hotel_aditya.db`

### Frontend → Vercel (free tier)
1. Push to GitHub (if not already)
2. Import at [vercel.com](https://vercel.com) — it will auto-detect via `vercel.json`
3. Set `BACKEND_URL` env var to your Render URL
4. Update `frontend/js/api.js` line 3: replace the Render URL with your actual URL
