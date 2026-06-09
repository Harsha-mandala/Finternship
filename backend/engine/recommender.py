"""
recommender.py — Person 2 / AI Engine  ⭐ CORE FILE
====================================================
Generates next-day order quantity recommendations for Hotel Aditya Grand.

Algorithm (per item):
    recommended = base_7day_avg
                × day_of_week_factor
                × weather_factor
                × festival_factor
                × trend_factor
    final_qty   = ceil(recommended × 1.10)   ← +10% safety buffer

All factors are ≥ 0. Each is explainable to the merchant.
"""

import os
import sqlite3
from math import ceil
from datetime import datetime, date, timedelta
from typing import Optional

from engine.weather_service    import get_weather_for_date, fetch_and_store_weather
from engine.festival_service   import get_festival_multiplier, get_upcoming_festivals
from engine.category_weather_map import compute_weather_factor

# ── DB path (env-overrideable so both local dev and Render work) ───────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(_HERE, "..", "..", "hotel_aditya.db"))

# Day-of-week name lookup (0=Monday)
_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_DAY_SHORT  = ["Mon",    "Tue",     "Wed",       "Thu",      "Fri",    "Sat",      "Sun"]


# ── DB helpers ─────────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _get_rolling_avg(item_name: str, before_date: str, days: int, conn) -> float:
    """
    Returns the average (or median for high-volatility items) qty_sold
    over the last `days` appearances before `before_date`.

    Uses MEDIAN for items with CV > 0.7 (event-driven spikes) to avoid
    enormous over-predictions caused by rare banquet/event days.
    """
    rows = conn.execute("""
        SELECT qty_sold FROM daily_sales
        WHERE item_name = ? AND date < ?
        ORDER BY date DESC
        LIMIT ?
    """, (item_name, before_date, days)).fetchall()

    if not rows:
        return 0.0

    qtys = sorted([r[0] for r in rows])
    n = len(qtys)
    mean_val = sum(qtys) / n

    # Compute coefficient of variation to detect volatile items
    if n >= 3:
        variance = sum((q - mean_val)**2 for q in qtys) / n
        std_val  = variance ** 0.5
        cv = std_val / mean_val if mean_val > 0 else 0
        # High volatility: use median to ignore event spikes
        if cv > 0.7:
            median_val = qtys[n // 2]
            return float(median_val)

    return float(mean_val)


def _get_dow_multiplier(item_name: str, target_dow: int, conn) -> float:
    """
    Computes (avg_daily_qty on target day-of-week) / (overall_daily_avg_qty).
    Uses calendar-day denominator for sparse items to avoid inflated multipliers.
    """
    sqlite_dow = str((target_dow + 1) % 7)   # Python DOW -> SQLite DOW

    # Total sold on this DOW, divided by how many of those days exist in data
    dow_row = conn.execute("""
        SELECT SUM(qty_sold), COUNT(DISTINCT date) FROM daily_sales
        WHERE item_name = ? AND strftime('%w', date) = ?
    """, (item_name, sqlite_dow)).fetchone()

    overall_row = conn.execute("""
        SELECT SUM(qty_sold), COUNT(DISTINCT date) FROM daily_sales
        WHERE item_name = ?
    """, (item_name,)).fetchone()

    if not overall_row or not overall_row[1] or overall_row[1] == 0:
        return 1.0

    # Get total calendar days in data to normalise properly
    total_days_row = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM daily_sales WHERE item_name = ?", (item_name,)
    ).fetchone()
    # Total calendar days (including days item did not appear)
    all_days_row = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM daily_sales"
    ).fetchone()

    # How many days of this DOW are in entire dataset
    dow_days_total = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM daily_sales WHERE strftime('%w', date) = ?",
        (sqlite_dow,)
    ).fetchone()[0] or 1

    dow_qty = float(dow_row[0] or 0)
    all_qty = float(overall_row[0] or 0)
    all_days = float(all_days_row[0] or 1)

    if all_qty == 0 or all_days == 0:
        return 1.0

    overall_daily_avg = all_qty / all_days
    dow_daily_avg     = dow_qty / dow_days_total

    if overall_daily_avg == 0:
        return 1.0
    return round(dow_daily_avg / overall_daily_avg, 3)


def _get_trend_factor(item_name: str, before_date: str, conn) -> float:
    """
    Checks if item is trending up or down over the last 5 days.
    Compares last 2 days vs days 3–5 (simple momentum signal).
    """
    rows = conn.execute("""
        SELECT qty_sold FROM daily_sales
        WHERE item_name = ? AND date < ?
        ORDER BY date DESC LIMIT 5
    """, (item_name, before_date)).fetchall()

    qtys = [r[0] for r in rows]
    if len(qtys) < 3:
        return 1.0

    recent = sum(qtys[:2]) / 2.0      # avg of last 2 days
    older  = sum(qtys[2:]) / len(qtys[2:])  # avg of earlier days

    if older == 0:
        return 1.0
    ratio = recent / older

    # Cap trend adjustment: ±8% at most to avoid overcorrection
    if ratio > 1.08:
        return 1.08
    elif ratio < 0.92:
        return 0.92
    return round(ratio, 3)


def _get_item_category(item_name: str, conn) -> str:
    row = conn.execute(
        "SELECT category FROM menu_items WHERE item_name = ?", (item_name,)
    ).fetchone()
    return row["category"] if row and row["category"] else "other"


def _get_active_items(before_date: str, conn, min_days: int = 5) -> list[dict]:
    """
    Returns items that appear in at least `min_days` of sales data before the target.
    min_days=5 ensures the 7-day rolling avg has enough signal (real data has 223 items
    but many appear rarely — only recommend items with meaningful history).
    """
    rows = conn.execute("""
        SELECT mi.item_name, mi.category
        FROM menu_items mi
        WHERE EXISTS (
            SELECT 1 FROM daily_sales ds
            WHERE ds.item_name = mi.item_name AND ds.date < ?
            GROUP BY ds.item_name
            HAVING COUNT(DISTINCT ds.date) >= ?
        )
        ORDER BY mi.category, mi.item_name
    """, (before_date, min_days)).fetchall()
    return [dict(r) for r in rows]


# ── Main recommendation engine ─────────────────────────────────────────────────

def generate_recommendations(target_date: str) -> list[dict]:
    """
    Generate next-day order recommendations for all active menu items.

    Args:
        target_date: 'YYYY-MM-DD' — the date you want recommendations FOR
                     (not the date you're running this on)

    Returns:
        List of recommendation dicts, sorted by category then item name.
        Each dict has: item_name, category, recommended_qty, base_avg,
                       dow_factor, weather_factor, festival_factor, trend_factor, reason
    """
    conn = _conn()
    target_dt  = datetime.strptime(target_date, "%Y-%m-%d")
    target_dow = target_dt.weekday()   # 0=Mon, 6=Sun

    # ── Fetch context ──────────────────────────────────────────────────────────
    # Weather: try DB first, then API, then mock
    try:
        weather = get_weather_for_date(target_date)
    except Exception:
        weather = None

    # Festival
    festival_mult, festival_name = get_festival_multiplier(target_date)

    # Look ahead for upcoming festivals (for reason string on nearby days)
    upcoming = get_upcoming_festivals(target_date, lookahead_days=3)

    # ── Get items to recommend ────────────────────────────────────────────────
    items = _get_active_items(target_date, conn)
    if not items:
        conn.close()
        return []

    recommendations = []
    for item in items:
        item_name = item["item_name"]
        category  = item["category"] or "other"

        # 1 ─ Base: 7-day rolling average
        base_avg = _get_rolling_avg(item_name, target_date, days=7, conn=conn)
        if base_avg < 0.5:
            continue   # Skip items with negligible recent history

        # 2 ─ Day-of-week factor
        dow_factor = _get_dow_multiplier(item_name, target_dow, conn)
        # Clamp: 0.50 – 2.00 to avoid extremes on sparse data
        dow_factor = max(0.55, min(dow_factor, 1.80))

        # 3 ─ Weather factor
        weather_factor = compute_weather_factor(category, weather)

        # 4 ─ Festival factor
        fest_factor = festival_mult   # already 1.0 if no festival

        # 5 ─ Trend factor (3-day momentum)
        trend_factor = _get_trend_factor(item_name, target_date, conn)

        # ── Final calculation ──────────────────────────────────────────────────
        raw_qty   = base_avg * dow_factor * weather_factor * fest_factor * trend_factor
        # +8% safety buffer; cap at 1.8x base_avg to prevent wild over-ordering
        # on sparse items (handles Pulka-type items that spike irregularly)
        buffered  = raw_qty * 1.08
        max_cap   = base_avg * 1.80
        final_qty = max(1, ceil(min(buffered, max_cap)))

        # ── Reason string (human-readable for UI) ─────────────────────────────
        reasons = []

        if festival_name:
            reasons.append(f"🎉 {festival_name}")
        elif upcoming:
            nxt = upcoming[0]
            reasons.append(f"📅 {nxt['name']} in {nxt['days_away']} day{'s' if nxt['days_away']>1 else ''}")

        if dow_factor >= 1.12:
            reasons.append(f"↑ {_DAY_SHORT[target_dow]} peak day")
        elif dow_factor <= 0.88:
            reasons.append(f"↓ Slow {_DAY_SHORT[target_dow]}")

        if weather:
            if weather_factor >= 1.12:
                reasons.append(f"↑ {weather['condition']} boosts this")
            elif weather_factor <= 0.88:
                reasons.append(f"↓ {weather['condition']} reduces demand")

        if trend_factor >= 1.06:
            reasons.append("↑ Trending up recently")
        elif trend_factor <= 0.94:
            reasons.append("↓ Trending down recently")

        reason_str = " | ".join(reasons) if reasons else "Based on 7-day average"

        recommendations.append({
            "item_name":       item_name,
            "category":        category,
            "recommended_qty": final_qty,
            "base_avg":        round(base_avg, 1),
            "dow_factor":      round(dow_factor, 2),
            "weather_factor":  round(weather_factor, 2),
            "festival_factor": round(fest_factor, 2),
            "trend_factor":    round(trend_factor, 2),
            "reason":          reason_str,
        })

    conn.close()
    # Sort: category first, then item name
    recommendations.sort(key=lambda x: (x["category"], x["item_name"]))
    return recommendations


def get_recommendation_context(target_date: str) -> dict:
    """
    Returns the full context object for a given date (for the frontend context banner).
    """
    try:
        weather = get_weather_for_date(target_date)
    except Exception:
        weather = None

    festival_mult, festival_name = get_festival_multiplier(target_date)
    upcoming = get_upcoming_festivals(target_date, lookahead_days=7)

    return {
        "date":            target_date,
        "weather":         weather,
        "festival_today":  festival_name,
        "festival_mult":   festival_mult,
        "upcoming_festivals": upcoming,
    }
