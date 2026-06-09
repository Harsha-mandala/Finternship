# 👤 Person 1 — Data Engineer + Backend Developer
## Hotel Aditya Grand · AI Kitchen Order Assistant · POC

---

> **Your Role**: You are the foundation of the entire project.
> Without your work, Person 2 has no data to analyse and Person 3 has no API to call.
> You must finish your Week 1 deliverables on time so the others can proceed.

---

## 🎯 What You Own

| Area | Your Responsibility |
|---|---|
| PDF Data Extraction | Parse all 45 daily sales PDFs into clean structured data |
| Data Cleaning | Normalize inconsistent item names across all PDFs |
| Database | Design, create and populate the SQLite database |
| Backend API | Build all REST API endpoints using FastAPI (Python) |
| Deployment | Deploy the backend to Render (free tier) |

---

## 📦 Your Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Primary language |
| **PyMuPDF (fitz)** | Render PDF pages as images |
| **pytesseract** | OCR — extract text from rendered images |
| **pandas** | Clean and analyse tabular data |
| **SQLite** | Local database (file-based, no install needed) |
| **FastAPI** | REST API framework |
| **uvicorn** | ASGI server to run FastAPI |
| **Render.com** | Free hosting for the backend API |

---

## 📁 Project Folder Structure You Will Create

```
project/
├── backend/
│   ├── main.py               ← FastAPI app entry point
│   ├── database.py           ← DB connection + table creation
│   ├── models.py             ← Pydantic request/response models
│   ├── routes/
│   │   ├── sales.py          ← Sales log endpoints
│   │   ├── recommendations.py← Recommendation endpoints
│   │   ├── items.py          ← Menu items endpoints
│   │   └── dashboard.py      ← Dashboard summary endpoints
│   └── requirements.txt
├── data_pipeline/
│   ├── parse_pdfs.py         ← Main PDF extraction script
│   ├── clean_data.py         ← Item name normalizer
│   ├── load_to_db.py         ← Insert cleaned data into SQLite
│   └── item_name_map.json    ← Manual mapping of fuzzy item names
├── data/                     ← The 45 PDF files (already exist)
└── hotel_aditya.db           ← SQLite database file (you create this)
```

---

## 📅 Week-by-Week Task Breakdown

---

### ✅ WEEK 1 — Data Pipeline + Database

#### Day 1–2: Set Up Environment & Understand the Data

```bash
# Install required packages
pip install pymupdf pytesseract pandas fastapi uvicorn python-multipart

# Also install Tesseract OCR engine (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH after install
```

**Your first task**: Look at 5 PDFs manually (open them). Understand:
- How many pages per PDF? (Answer: ~4 pages)
- What columns exist? (Answer: Item | Qty | Gross)
- Are item names consistent across dates? (Answer: NO — this is the hard part)
- What appears in the summary rows at the bottom? (Total, NoCash, Discount, CGST, SGST, Grand Total)

---

#### Day 2–3: Write the PDF Parser (`parse_pdfs.py`)

This is your **most important script**. It must:
1. Loop through all 45 PDF files in `data/` folder
2. For each PDF, render each page as an image using PyMuPDF
3. Run pytesseract OCR on each image
4. Use regex to extract rows: `Item | Qty | Gross`
5. Skip the summary rows (Total, NoCash, CGST, etc.)
6. Tag each row with the date (extracted from filename e.g. `01-04-2026.pdf` → `2026-04-01`)
7. Save all extracted rows into a raw CSV: `raw_sales_data.csv`

```python
# parse_pdfs.py — starter template

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pandas as pd
import re
import os
from pathlib import Path

# Point to your Tesseract install path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DATA_DIR = Path("../data")
OUTPUT_CSV = "raw_sales_data.csv"

SKIP_KEYWORDS = ["Total", "NoCash", "Discount", "CGST", "SGST", "Grand", "Printed", "Period", "Item"]

def parse_date_from_filename(filename):
    # "01-04-2026.pdf" or "25-04-2026_1.pdf" → "2026-04-01"
    base = filename.replace("_1", "").replace(".pdf", "")
    parts = base.split("-")
    return f"{parts[2]}-{parts[1]}-{parts[0]}"

def extract_rows_from_text(text, date):
    rows = []
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or any(kw in line for kw in SKIP_KEYWORDS):
            continue
        # Match: Item name (text) followed by qty (integer) followed by gross (decimal)
        match = re.match(r'^(.+?)\s+(\d+)\s+([\d,]+\.\d{2})$', line)
        if match:
            item = match.group(1).strip()
            qty = int(match.group(2))
            gross = float(match.group(3).replace(",", ""))
            rows.append({"date": date, "item_raw": item, "qty_sold": qty, "gross_revenue": gross})
    return rows

def process_pdf(pdf_path):
    date = parse_date_from_filename(pdf_path.name)
    doc = fitz.open(str(pdf_path))
    all_rows = []
    for page in doc:
        mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR accuracy
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, config='--psm 6')
        rows = extract_rows_from_text(text, date)
        all_rows.extend(rows)
    return all_rows

def main():
    all_data = []
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        try:
            rows = process_pdf(pdf_path)
            print(f"  → {len(rows)} rows extracted")
            all_data.extend(rows)
        except Exception as e:
            print(f"  ERROR: {e}")
    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone! Total rows: {len(df)} → saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
```

**Expected output**: `raw_sales_data.csv` with ~3,500–4,000 rows.

---

#### Day 3–4: Clean Item Names (`clean_data.py`)

This is the **trickiest part**. The same item appears under different names across PDFs:
- `"chi lolypop 6 pic"` = `"Chicken Loly Pop 6 pes"` = `"Chicken Lollypop 6pc"`
- `"CHILLI CHICKEN BL"` = `"Chilli Chicken BL"` = `"chilli chicken bl"`

**Your cleaning steps**:

1. **Load `raw_sales_data.csv`**
2. **Lowercase all item names** → find how many unique items exist
3. **Print a sorted list of all unique raw item names** → you'll see the duplicates
4. **Create `item_name_map.json`** — a manual JSON file mapping raw names to clean canonical names:

```json
{
  "chi lolypop 6 pic": "Chicken Lollypop 6pc",
  "chicken loly pop 6 pes": "Chicken Lollypop 6pc",
  "chilli chicken bl": "Chilli Chicken BL",
  "butter non": "Butter Naan",
  "cool drink 250 ml": "Cool Drink 250ml",
  "cdb familly pack": "CDB Family Pack"
}
```

5. **Apply the mapping** to create `item_name` (clean) column in the data
6. **Assign categories** to each canonical item:

```python
CATEGORIES = {
    "biryani": ["Biryani", "Biriyani"],
    "chicken": ["Chicken", "Chilli Chicken", "Dragon Chicken"],
    "beverage": ["Cool Drink", "Lassi", "Milk Shake", "Juice"],
    "ice_cream": ["Ice Cream"],
    "bread": ["Naan", "Roti", "Paratha"],
    "rice": ["Fried Rice", "Curd Rice"],
    "starter": ["Lollypop", "French Fries", "Manchuria", "Gobi"],
    "seafood": ["Fish", "Prawn"],
    "soup": ["Soup"],
    "egg": ["Egg"],
    "family_pack": ["Family Pack", "Pack"],
}
```

7. **Save final cleaned file** as `cleaned_sales_data.csv`

---

#### Day 4–5: Database Setup & Data Load

**Create the database** (`database.py`):

```python
import sqlite3

DB_PATH = "hotel_aditya.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS daily_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            item_name TEXT NOT NULL,
            qty_sold INTEGER NOT NULL,
            gross_revenue REAL,
            source TEXT DEFAULT 'manual'
        );
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            category TEXT,
            unit_price REAL,
            is_perishable INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS weather_data (
            date DATE PRIMARY KEY,
            max_temp REAL,
            min_temp REAL,
            condition TEXT,
            rainfall_mm REAL
        );
        CREATE TABLE IF NOT EXISTS festivals (
            date DATE NOT NULL,
            name TEXT NOT NULL,
            type TEXT,
            demand_multiplier REAL DEFAULT 1.0
        );
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            item_name TEXT NOT NULL,
            recommended_qty INTEGER,
            base_qty REAL,
            weather_factor REAL,
            festival_factor REAL,
            day_factor REAL,
            merchant_override INTEGER
        );
    """)
    conn.commit()
    conn.close()
    print("Tables created.")

if __name__ == "__main__":
    create_tables()
```

**Load data** (`load_to_db.py`):

```python
import pandas as pd
import sqlite3
from database import get_connection, create_tables

def load_sales_data():
    df = pd.read_csv("cleaned_sales_data.csv")
    conn = get_connection()
    # Load daily_sales
    df[["date","item_name","qty_sold","gross_revenue"]].assign(source="pdf_import") \
      .to_sql("daily_sales", conn, if_exists="append", index=False)
    # Load unique menu_items
    items_df = df[["item_name","category"]].drop_duplicates("item_name")
    items_df.to_sql("menu_items", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"Loaded {len(df)} sales records and {len(items_df)} menu items.")

if __name__ == "__main__":
    create_tables()
    load_sales_data()
```

**Run and verify**:
```bash
python database.py
python load_to_db.py
# Then check:
sqlite3 hotel_aditya.db "SELECT count(*) FROM daily_sales;"
sqlite3 hotel_aditya.db "SELECT count(*) FROM menu_items;"
```

---

### ✅ WEEK 2 — Backend API (FastAPI)

Build the REST API that Person 3's frontend will call.

#### Main app (`main.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import sales, recommendations, items, dashboard

app = FastAPI(title="Hotel Aditya Grand API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Hotel Aditya Grand API running"}
```

#### All API Endpoints You Must Build:

| Method | Endpoint | What it does | Used by |
|---|---|---|---|
| GET | `/dashboard/summary` | Today's revenue, top 5 items, weather | Person 3 Dashboard |
| GET | `/dashboard/revenue-trend` | Last 30 days daily revenue | Person 3 Charts |
| GET | `/items/` | All menu items with categories | Person 3 Log Sales form |
| GET | `/sales/?date=YYYY-MM-DD` | Sales for a specific date | Person 3 |
| POST | `/sales/log` | Save today's sales entry | Person 3 Log Sales |
| GET | `/recommendations/?date=YYYY-MM-DD` | Get order recommendations | Person 2 feeds this, Person 3 displays |
| PUT | `/recommendations/override` | Merchant overrides a qty | Person 3 |
| GET | `/sales/trends?item=X&days=30` | Item-specific trend data | Person 3 Trends screen |
| GET | `/sales/dow-patterns` | Day-of-week avg per item | Person 2 algorithm uses this |

#### Example — `routes/sales.py`:

```python
from fastapi import APIRouter
from database import get_connection
import sqlite3

router = APIRouter()

@router.get("/")
def get_sales(date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT item_name, qty_sold, gross_revenue FROM daily_sales WHERE date = ?", (date,))
    rows = cur.fetchall()
    conn.close()
    return [{"item_name": r[0], "qty_sold": r[1], "gross_revenue": r[2]} for r in rows]

@router.post("/log")
def log_sales(entries: list[dict]):
    conn = get_connection()
    cur = conn.cursor()
    for entry in entries:
        cur.execute(
            "INSERT INTO daily_sales (date, item_name, qty_sold, gross_revenue, source) VALUES (?,?,?,?,?)",
            (entry["date"], entry["item_name"], entry["qty_sold"], entry.get("gross_revenue", 0), "manual")
        )
    conn.commit()
    conn.close()
    return {"status": "ok", "logged": len(entries)}

@router.get("/trends")
def get_trends(item: str, days: int = 30):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, qty_sold FROM daily_sales
        WHERE item_name = ? ORDER BY date DESC LIMIT ?
    """, (item, days))
    rows = cur.fetchall()
    conn.close()
    return [{"date": r[0], "qty": r[1]} for r in rows]

@router.get("/dow-patterns")
def get_dow_patterns():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT item_name,
               strftime('%w', date) as dow,
               AVG(qty_sold) as avg_qty
        FROM daily_sales
        GROUP BY item_name, dow
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"item": r[0], "dow": r[1], "avg_qty": r[2]} for r in rows]
```

#### `requirements.txt`:
```
fastapi
uvicorn
pandas
pymupdf
pytesseract
Pillow
python-multipart
```

#### Run locally:
```bash
uvicorn main:app --reload --port 8000
# Test at: http://localhost:8000/docs (auto Swagger UI)
```

---

### ✅ WEEK 3 — Testing, Integration & Deployment

#### Testing Checklist:
- [ ] All 45 PDFs parsed with < 5% OCR error rate
- [ ] `cleaned_sales_data.csv` has no duplicate item rows for same date
- [ ] All 9 API endpoints return correct data
- [ ] CORS is enabled (Person 3's frontend can call your API)
- [ ] `/recommendations/` endpoint returns data in correct format for Person 2

#### Deploy to Render.com (Free):
1. Push your `backend/` folder to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Share the live URL (e.g. `https://hotel-aditya-api.onrender.com`) with Person 2 and Person 3

---

## 📤 What You Hand Off to Others

| Deliverable | Goes to | Deadline |
|---|---|---|
| `hotel_aditya.db` (populated) | Person 2 | End of Week 1 |
| `cleaned_sales_data.csv` | Person 2 | End of Week 1 |
| List of all API endpoint URLs + formats | Person 3 | Start of Week 2 |
| Live Render.com API URL | Person 3 | End of Week 2 |
| DB schema documentation | Person 2 & 3 | End of Week 1 |

---

## ⚠️ Key Risks & How to Handle Them

| Risk | Solution |
|---|---|
| OCR fails on some pages | Manually extract data for failed pages from the PDF visually |
| Item names too messy | Print all unique names, do manual mapping in `item_name_map.json` |
| Tesseract not installed | Download from UB-Mannheim GitHub, add to Windows PATH |
| Render free tier is slow | Add a `/ping` endpoint — Person 3 pings it on app load to wake it up |

---

## ✅ Final Deliverables Checklist

- [ ] `raw_sales_data.csv` — raw OCR output from all 45 PDFs
- [ ] `item_name_map.json` — manual normalization mapping
- [ ] `cleaned_sales_data.csv` — final clean data with categories
- [ ] `hotel_aditya.db` — SQLite DB with all 5 tables populated
- [ ] FastAPI backend with all 9 endpoints working
- [ ] Live API URL on Render.com shared with team
- [ ] Swagger docs accessible at `/docs`
