"""
main.py — FastAPI entry point for Hotel Aditya Grand Order Assistant POC
=========================================================================
Run:  cd backend && uvicorn main:app --reload --port 8000

After starting, open:
  http://localhost:8000          ← The frontend app
  http://localhost:8000/docs     ← API explorer (Swagger)
"""

import os, sys, io
# Fix Windows stdout encoding for print() calls during startup
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Environment ───────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

import sqlite3
from datetime import date, timedelta
from typing import List

from fastapi import FastAPI, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
ROOT       = os.path.join(_HERE, "..")
DB_PATH    = os.environ.get("DB_PATH", os.path.join(ROOT, "hotel_aditya.db"))
FRONTEND   = os.path.join(ROOT, "frontend")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Hotel Aditya Grand — Order Assistant API",
    description="AI-powered daily order recommendations for Hotel Aditya Grand, Kandukur.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── DB helper ─────────────────────────────────────────────────────────────────
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ════════════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS router  (Person 2 engine)
# ════════════════════════════════════════════════════════════════════════════════
from routes.recommendations import router as recs_router
app.include_router(recs_router, prefix="/recommendations", tags=["Recommendations"])


# ════════════════════════════════════════════════════════════════════════════════
# DASHBOARD router
# ════════════════════════════════════════════════════════════════════════════════
dash_router = APIRouter()

@dash_router.get("/summary")
def dashboard_summary():
    """Today's revenue, top 5 items, weather, festival."""
    from engine.weather_service  import get_weather_for_date
    from engine.festival_service import get_festival_multiplier, get_upcoming_festivals

    today = date.today().isoformat()
    conn  = _conn()

    # Revenue for today — fall back to last available day if today has no data
    row = conn.execute("""
        SELECT SUM(gross_revenue) AS rev, SUM(qty_sold) AS qty
        FROM daily_sales WHERE date = ?
    """, (today,)).fetchone()

    if not row or row["rev"] is None:
        row = conn.execute("""
            SELECT date, SUM(gross_revenue) AS rev, SUM(qty_sold) AS qty
            FROM daily_sales GROUP BY date ORDER BY date DESC LIMIT 1
        """).fetchone()
        data_date = row["date"] if row else today
    else:
        data_date = today

    today_rev = round(row["rev"] or 0, 2)
    today_qty = int(row["qty"] or 0)

    top_rows = conn.execute("""
        SELECT item_name, SUM(qty_sold) AS qty
        FROM daily_sales WHERE date = ?
        GROUP BY item_name ORDER BY qty DESC LIMIT 5
    """, (data_date,)).fetchall()
    conn.close()

    top_items = [{"item_name": r["item_name"], "qty": r["qty"]} for r in top_rows]

    try:
        weather = get_weather_for_date(today)
    except Exception:
        weather = None

    _, festival_today = get_festival_multiplier(today)
    upcoming = get_upcoming_festivals(today, lookahead_days=3)

    return {
        "date":            data_date,
        "today_revenue":   today_rev,
        "total_qty_sold":  today_qty,
        "top_items":       top_items,
        "weather":         weather,
        "festival_today":  festival_today,
        "upcoming_festival": upcoming[0]["name"] if upcoming else None,
    }


@dash_router.get("/revenue-trend")
def revenue_trend(days: int = Query(default=30, ge=7, le=45)):
    """Daily revenue series for the last N days (ascending)."""
    conn = _conn()
    rows = conn.execute("""
        SELECT date, SUM(gross_revenue) AS revenue, SUM(qty_sold) AS total_qty
        FROM daily_sales GROUP BY date ORDER BY date DESC LIMIT ?
    """, (days,)).fetchall()
    conn.close()
    return [{"date": r["date"], "revenue": round(r["revenue"] or 0, 2),
             "total_qty": r["total_qty"]} for r in reversed(rows)]


@dash_router.get("/category-trends")
def category_trends():
    """Revenue and qty totals per category."""
    conn = _conn()
    rows = conn.execute("""
        SELECT mi.category, SUM(ds.qty_sold) AS qty, SUM(ds.gross_revenue) AS revenue
        FROM daily_sales ds JOIN menu_items mi ON ds.item_name = mi.item_name
        GROUP BY mi.category ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return [{"category": r["category"], "qty": r["qty"],
             "revenue": round(r["revenue"] or 0, 2)} for r in rows]


app.include_router(dash_router, prefix="/dashboard", tags=["Dashboard"])


# ════════════════════════════════════════════════════════════════════════════════
# ITEMS router
# ════════════════════════════════════════════════════════════════════════════════
items_router = APIRouter()

@items_router.get("/")
def get_all_items(category: str = Query(default=None)):
    """All menu items sorted by popularity (avg qty sold/day)."""
    conn = _conn()
    if category:
        rows = conn.execute("""
            SELECT mi.item_name, mi.category, mi.unit_price,
                   AVG(ds.qty_sold) AS avg_qty, COUNT(DISTINCT ds.date) AS days_sold
            FROM menu_items mi LEFT JOIN daily_sales ds ON mi.item_name = ds.item_name
            WHERE mi.category = ?
            GROUP BY mi.item_name ORDER BY avg_qty DESC
        """, (category,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT mi.item_name, mi.category, mi.unit_price,
                   AVG(ds.qty_sold) AS avg_qty, COUNT(DISTINCT ds.date) AS days_sold
            FROM menu_items mi LEFT JOIN daily_sales ds ON mi.item_name = ds.item_name
            GROUP BY mi.item_name ORDER BY avg_qty DESC
        """).fetchall()
    conn.close()
    return [{"item_name": r["item_name"], "category": r["category"],
             "unit_price": r["unit_price"],
             "avg_qty": round(r["avg_qty"] or 0, 1),
             "days_sold": r["days_sold"] or 0} for r in rows]

app.include_router(items_router, prefix="/items", tags=["Items"])


# ════════════════════════════════════════════════════════════════════════════════
# SALES router
# ════════════════════════════════════════════════════════════════════════════════
sales_router = APIRouter()

@sales_router.get("/")
def get_sales(sale_date: str = Query(default=None, alias="date"),
              limit: int = Query(default=200)):
    if sale_date is None:
        sale_date = date.today().isoformat()
    conn = _conn()
    rows = conn.execute("""
        SELECT ds.date, ds.item_name, ds.qty_sold, ds.gross_revenue, mi.category
        FROM daily_sales ds LEFT JOIN menu_items mi ON ds.item_name = mi.item_name
        WHERE ds.date = ? ORDER BY ds.qty_sold DESC LIMIT ?
    """, (sale_date, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


class SalesEntry(BaseModel):
    item_name: str
    qty_sold:  int
    gross_revenue: float = 0.0

class SalesLogRequest(BaseModel):
    date: str
    entries: List[SalesEntry]

@sales_router.post("/log")
def log_sales(body: SalesLogRequest):
    conn = _conn()
    saved = 0
    for entry in body.entries:
        rev = entry.gross_revenue
        if rev == 0:
            r = conn.execute(
                "SELECT unit_price FROM menu_items WHERE item_name = ?",
                (entry.item_name,)).fetchone()
            if r and r["unit_price"]:
                rev = entry.qty_sold * r["unit_price"]
        conn.execute("""
            INSERT INTO daily_sales (date, item_name, qty_sold, gross_revenue, source)
            VALUES (?, ?, ?, ?, 'manual_entry')
            ON CONFLICT DO NOTHING
        """, (body.date, entry.item_name, entry.qty_sold, rev))
        saved += 1
    conn.commit()
    conn.close()
    return {"status": "saved", "date": body.date, "entries_saved": saved}

@sales_router.get("/trends")
def item_trend(item: str = Query(...), days: int = Query(default=30, ge=7, le=45)):
    conn = _conn()
    rows = conn.execute("""
        SELECT date, SUM(qty_sold) AS qty_sold FROM daily_sales
        WHERE item_name = ? GROUP BY date ORDER BY date DESC LIMIT ?
    """, (item, days)).fetchall()
    conn.close()
    return [{"date": r["date"], "qty_sold": r["qty_sold"]} for r in reversed(rows)]

app.include_router(sales_router, prefix="/sales", tags=["Sales"])


# ════════════════════════════════════════════════════════════════════════════════
# HEALTH + STATIC FRONTEND
# ════════════════════════════════════════════════════════════════════════════════
@app.get("/health", tags=["Health"])
def health():
    try:
        conn = _conn()
        rows = conn.execute("SELECT COUNT(*) FROM daily_sales").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
        conn.close()
        return {"status": "healthy", "sales_rows": rows, "menu_items": items, "db": DB_PATH}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# Serve frontend static files at root so css/, js/ paths work directly
# MUST be after all API routes so /health etc. are not intercepted
if os.path.isdir(FRONTEND):
    # Mount at /css and /js directly so the HTML paths work as-is
    _css = os.path.join(FRONTEND, "css")
    _js  = os.path.join(FRONTEND, "js")
    if os.path.isdir(_css): app.mount("/css", StaticFiles(directory=_css), name="css")
    if os.path.isdir(_js):  app.mount("/js",  StaticFiles(directory=_js),  name="js")

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(os.path.join(FRONTEND, "index.html"))

    @app.get("/app", include_in_schema=False)
    def serve_app():
        return FileResponse(os.path.join(FRONTEND, "index.html"))
