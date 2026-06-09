"""
dashboard.py — Person 2/3 shared FastAPI routes
=================================================
Dashboard summary, revenue trends, and item/sales endpoints.
These complement Person 2's recommendations.py.

Endpoints:
  GET /dashboard/summary          → Today's revenue, top items, weather
  GET /dashboard/revenue-trend    → N-day daily revenue series
  GET /dashboard/category-trends  → Total qty + revenue per category
  GET /items/                     → All menu items (sorted by popularity)
  GET /sales/                     → Sales for a given date
  POST /sales/log                 → Log/update sales for a date
"""

import sqlite3
import os
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List

router = APIRouter()

_HERE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(_HERE, "..", "..", "hotel_aditya.db"))


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ── Dashboard ──────────────────────────────────────────────────────────────────

@router.get("/summary")
def dashboard_summary():
    """
    Returns a one-shot summary for the dashboard screen:
    - Today's revenue + qty sold
    - Top 5 items by qty today
    - Weather for today
    - Upcoming festival (if within 3 days)
    """
    from engine.weather_service  import get_weather_for_date
    from engine.festival_service import get_festival_multiplier, get_upcoming_festivals

    today = date.today().isoformat()
    conn  = _conn()

    # Revenue + qty for today
    row = conn.execute("""
        SELECT SUM(gross_revenue) AS rev, SUM(qty_sold) AS qty
        FROM daily_sales WHERE date = ?
    """, (today,)).fetchone()

    # If no data for today (weekend/no sales logged yet), use latest available day
    if not row or row["rev"] is None:
        row2 = conn.execute("""
            SELECT date, SUM(gross_revenue) AS rev, SUM(qty_sold) AS qty
            FROM daily_sales
            GROUP BY date ORDER BY date DESC LIMIT 1
        """).fetchone()
        today_rev = round(row2["rev"], 2) if row2 and row2["rev"] else 0
        today_qty = int(row2["qty"]) if row2 and row2["qty"] else 0
        data_date = row2["date"] if row2 else today
    else:
        today_rev = round(row["rev"], 2) if row["rev"] else 0
        today_qty = int(row["qty"]) if row["qty"] else 0
        data_date = today

    # Top 5 items for that day
    top_rows = conn.execute("""
        SELECT item_name, SUM(qty_sold) AS qty
        FROM daily_sales WHERE date = ?
        GROUP BY item_name ORDER BY qty DESC LIMIT 5
    """, (data_date,)).fetchall()
    top_items = [{"item_name": r["item_name"], "qty": r["qty"]} for r in top_rows]

    conn.close()

    # Weather + festivals
    try:
        weather = get_weather_for_date(today)
    except Exception:
        weather = None

    _, festival_today = get_festival_multiplier(today)
    upcoming = get_upcoming_festivals(today, lookahead_days=3)

    return {
        "date":           data_date,
        "today_revenue":  today_rev,
        "total_qty_sold": today_qty,
        "top_items":      top_items,
        "weather":        weather,
        "festival_today": festival_today,
        "upcoming_festival": upcoming[0]["name"] if upcoming else None,
    }


@router.get("/revenue-trend")
def revenue_trend(days: int = Query(default=30, ge=7, le=45)):
    """Returns daily revenue for the last N days."""
    conn = _conn()
    rows = conn.execute("""
        SELECT date, SUM(gross_revenue) AS revenue, SUM(qty_sold) AS total_qty
        FROM daily_sales
        GROUP BY date
        ORDER BY date DESC
        LIMIT ?
    """, (days,)).fetchall()
    conn.close()

    # Return in ascending order
    data = [{"date": r["date"], "revenue": round(r["revenue"], 2), "total_qty": r["total_qty"]}
            for r in reversed(rows)]
    return data


@router.get("/category-trends")
def category_trends():
    """Total qty and revenue aggregated by category (all-time from DB)."""
    conn = _conn()
    rows = conn.execute("""
        SELECT mi.category, SUM(ds.qty_sold) AS qty, SUM(ds.gross_revenue) AS revenue
        FROM daily_sales ds
        JOIN menu_items mi ON ds.item_name = mi.item_name
        GROUP BY mi.category
        ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return [{"category": r["category"], "qty": r["qty"], "revenue": round(r["revenue"], 2)}
            for r in rows]


# ── Items ──────────────────────────────────────────────────────────────────────

@router.get("/")
def get_all_items(category: str = Query(default=None)):
    """Returns all menu items sorted by average quantity (most popular first)."""
    conn = _conn()
    if category:
        rows = conn.execute("""
            SELECT mi.item_name, mi.category, mi.unit_price,
                   AVG(ds.qty_sold) AS avg_qty, COUNT(ds.id) AS days_sold
            FROM menu_items mi
            LEFT JOIN daily_sales ds ON mi.item_name = ds.item_name
            WHERE mi.category = ?
            GROUP BY mi.item_name ORDER BY avg_qty DESC NULLS LAST
        """, (category,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT mi.item_name, mi.category, mi.unit_price,
                   AVG(ds.qty_sold) AS avg_qty, COUNT(ds.id) AS days_sold
            FROM menu_items mi
            LEFT JOIN daily_sales ds ON mi.item_name = ds.item_name
            GROUP BY mi.item_name ORDER BY avg_qty DESC NULLS LAST
        """).fetchall()
    conn.close()
    return [{"item_name": r["item_name"], "category": r["category"],
             "unit_price": r["unit_price"], "avg_qty": round(r["avg_qty"] or 0, 1),
             "days_sold": r["days_sold"]} for r in rows]


# ── Sales ──────────────────────────────────────────────────────────────────────

@router.get("/")
def get_sales(
    sale_date: str = Query(default=None, alias="date"),
    limit: int = Query(default=100, le=500)
):
    """Returns sales records for a given date (defaults to today)."""
    if sale_date is None:
        sale_date = date.today().isoformat()
    conn = _conn()
    rows = conn.execute("""
        SELECT ds.date, ds.item_name, ds.qty_sold, ds.gross_revenue, mi.category
        FROM daily_sales ds
        LEFT JOIN menu_items mi ON ds.item_name = mi.item_name
        WHERE ds.date = ?
        ORDER BY ds.qty_sold DESC
        LIMIT ?
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


@router.post("/log")
def log_sales(body: SalesLogRequest):
    """Upserts daily sales entries. Called by the Log Sales screen."""
    if not body.entries:
        raise HTTPException(status_code=400, detail="No entries provided")

    conn = _conn()
    saved = 0
    for entry in body.entries:
        # Get unit price for revenue estimate if not provided
        rev = entry.gross_revenue
        if rev == 0:
            price_row = conn.execute(
                "SELECT unit_price FROM menu_items WHERE item_name = ?", (entry.item_name,)
            ).fetchone()
            if price_row and price_row["unit_price"]:
                rev = entry.qty_sold * price_row["unit_price"]

        conn.execute("""
            INSERT INTO daily_sales (date, item_name, qty_sold, gross_revenue, source)
            VALUES (?, ?, ?, ?, 'manual_entry')
            ON CONFLICT DO NOTHING
        """, (body.date, entry.item_name, entry.qty_sold, rev))
        saved += 1

    conn.commit()
    conn.close()
    return {"status": "saved", "date": body.date, "entries_saved": saved}


@router.get("/trends")
def item_trend(
    item: str = Query(..., description="Item name"),
    days: int = Query(default=30, ge=7, le=45)
):
    """Returns qty_sold per day for a specific item over last N days."""
    conn = _conn()
    rows = conn.execute("""
        SELECT date, SUM(qty_sold) AS qty_sold
        FROM daily_sales
        WHERE item_name = ?
        GROUP BY date
        ORDER BY date DESC
        LIMIT ?
    """, (item, days)).fetchall()
    conn.close()
    return [{"date": r["date"], "qty_sold": r["qty_sold"]} for r in reversed(rows)]
