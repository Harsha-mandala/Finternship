"""
recommendations.py — Person 2 / FastAPI Route
==============================================
Adds two endpoints to the shared backend:

  GET  /recommendations/             → Get order recommendations for a date
  PUT  /recommendations/override     → Merchant overrides a suggested qty
  GET  /recommendations/context      → Get context (weather + festivals) for a date

This file is Person 2's contribution to the shared backend/routes/ folder.
Person 1 will import and register it in main.py.
"""

import sqlite3
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta

from engine.recommender import generate_recommendations, get_recommendation_context
from engine.weather_service import fetch_and_store_weather

router = APIRouter()

_HERE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(_HERE, "..", "..", "hotel_aditya.db"))


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ── Request / Response models ──────────────────────────────────────────────────

class OverrideRequest(BaseModel):
    item_name:    str
    date:         str    # 'YYYY-MM-DD'
    merchant_qty: int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/")
def get_recommendations(
    target_date: str = Query(
        default=None,
        description="Date to get recommendations FOR (YYYY-MM-DD). Defaults to tomorrow."
    )
):
    """
    Returns AI-generated order quantity recommendations for every active menu item.

    Response format:
    {
        "date": "2026-06-06",
        "total_items": 42,
        "context": { weather, festival_today, upcoming_festivals },
        "recommendations": [
            {
                "item_name": "Chicken Dum Biryani",
                "category": "biryani",
                "recommended_qty": 18,
                "base_avg": 14.5,
                "dow_factor": 1.15,
                "weather_factor": 1.20,
                "festival_factor": 1.0,
                "trend_factor": 1.05,
                "reason": "↑ Sat peak day | ↑ Rain boosts this"
            }, ...
        ]
    }
    """
    if target_date is None:
        target_date = (date.today() + timedelta(days=1)).isoformat()

    # Auto-refresh weather for this date (silently fails if no API key)
    try:
        fetch_and_store_weather(target_date)
    except Exception:
        pass

    try:
        recs    = generate_recommendations(target_date)
        context = get_recommendation_context(target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")

    return {
        "date":           target_date,
        "total_items":    len(recs),
        "context":        context,
        "recommendations": recs,
    }


@router.get("/context")
def get_context(
    target_date: str = Query(
        default=None,
        description="Date (YYYY-MM-DD). Defaults to tomorrow."
    )
):
    """
    Returns only the context (weather + festivals) for a given date.
    Used by the frontend dashboard banner.
    """
    if target_date is None:
        target_date = (date.today() + timedelta(days=1)).isoformat()

    try:
        ctx = get_recommendation_context(target_date)
        return ctx
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/override")
def override_recommendation(body: OverrideRequest):
    """
    Saves a merchant's manual override of a recommendation quantity.
    Person 3 calls this when the merchant taps +/- on an item.
    """
    conn = _conn()
    try:
        # Upsert: update if exists, insert if not
        conn.execute("""
            INSERT INTO recommendations (date, item_name, merchant_override)
            VALUES (?, ?, ?)
            ON CONFLICT(date, item_name) DO UPDATE SET merchant_override = excluded.merchant_override
        """, (body.date, body.item_name, body.merchant_qty))
        conn.commit()
    except sqlite3.OperationalError:
        # Table might not have UNIQUE constraint yet — try UPDATE then INSERT
        updated = conn.execute("""
            UPDATE recommendations
            SET merchant_override = ?
            WHERE date = ? AND item_name = ?
        """, (body.merchant_qty, body.date, body.item_name)).rowcount

        if updated == 0:
            conn.execute("""
                INSERT OR IGNORE INTO recommendations (date, item_name, merchant_override)
                VALUES (?, ?, ?)
            """, (body.date, body.item_name, body.merchant_qty))
        conn.commit()
    finally:
        conn.close()

    return {
        "status":      "override saved",
        "item_name":   body.item_name,
        "date":        body.date,
        "qty_saved":   body.merchant_qty,
    }


@router.get("/accuracy")
def get_accuracy_report(days: int = Query(default=14, ge=3, le=45)):
    """
    Returns forecast accuracy for the last N days.
    Compares stored recommendations against actual sales.
    Used by Person 3 for the History/Accuracy screen.
    """
    conn = _conn()
    rows = conn.execute("""
        SELECT
            r.date,
            r.item_name,
            r.recommended_qty,
            r.merchant_override,
            ds.qty_sold AS actual_qty,
            mi.category
        FROM recommendations r
        LEFT JOIN daily_sales ds
            ON r.date = ds.date AND r.item_name = ds.item_name
        JOIN menu_items mi ON r.item_name = mi.item_name
        WHERE r.date >= date('now', ?)
          AND ds.qty_sold IS NOT NULL
        ORDER BY r.date DESC, r.item_name
    """, (f"-{days} days",)).fetchall()
    conn.close()

    results = []
    for row in rows:
        effective_pred = row["merchant_override"] or row["recommended_qty"]
        actual         = row["actual_qty"]
        if actual and actual > 0:
            error_pct = round(abs(effective_pred - actual) / actual * 100, 1)
        else:
            error_pct = None

        results.append({
            "date":          row["date"],
            "item_name":     row["item_name"],
            "category":      row["category"],
            "predicted_qty": effective_pred,
            "actual_qty":    actual,
            "error_pct":     error_pct,
            "was_overridden": row["merchant_override"] is not None,
        })

    # Summary stats
    errors = [r["error_pct"] for r in results if r["error_pct"] is not None]
    summary = {
        "days_analysed":      days,
        "items_compared":     len(errors),
        "mean_error_pct":     round(sum(errors) / len(errors), 1) if errors else None,
        "within_20pct":       sum(1 for e in errors if e <= 20),
        "within_20pct_ratio": round(sum(1 for e in errors if e <= 20) / len(errors), 2) if errors else None,
    }

    return {"summary": summary, "details": results}
