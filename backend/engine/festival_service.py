"""
festival_service.py — Person 2 / AI Engine
===========================================
Loads festivals_2026.json and answers two questions:
  1. Is there a festival ON a given date? → return multiplier + name
  2. Is there a festival SOON (next N days)? → return closest festival

Usage:
    from engine.festival_service import get_festival_multiplier, get_upcoming_festivals
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Optional

# ── Path resolution ────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_JSON = os.path.join(_HERE, "..", "..", "data", "festivals_2026.json")
FESTIVALS_JSON_PATH = os.environ.get("FESTIVALS_JSON", _DEFAULT_JSON)

# ── Load once at module import ─────────────────────────────────────────────────
def _load_festivals() -> dict:
    """Returns {date_str: {"name": ..., "multiplier": ...}} for fast lookup."""
    lookup = {}
    try:
        with open(FESTIVALS_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            d = entry["date"]
            mult = float(entry.get("demand_multiplier", 1.0))
            name = entry["name"]
            # If two festivals on same date, take the higher multiplier
            if d not in lookup or lookup[d]["multiplier"] < mult:
                lookup[d] = {"name": name, "multiplier": mult}
    except FileNotFoundError:
        print(f"[festival_service] WARNING: {FESTIVALS_JSON_PATH} not found. Using no festivals.")
    except Exception as e:
        print(f"[festival_service] ERROR loading festivals: {e}")
    return lookup

FESTIVAL_LOOKUP: dict = _load_festivals()


# ── Public API ─────────────────────────────────────────────────────────────────

def get_festival_multiplier(target_date: str) -> tuple[float, Optional[str]]:
    """
    Returns (demand_multiplier, festival_name) for the given date.
    If no festival, returns (1.0, None).

    Args:
        target_date: 'YYYY-MM-DD' string

    Returns:
        (float, str | None)  e.g. (1.7, 'Ugadi (Telugu New Year)')
    """
    entry = FESTIVAL_LOOKUP.get(target_date)
    if entry:
        return entry["multiplier"], entry["name"]
    return 1.0, None


def get_upcoming_festivals(from_date: str, lookahead_days: int = 7) -> list[dict]:
    """
    Returns a list of festivals in the next N days.

    Args:
        from_date: start date 'YYYY-MM-DD'
        lookahead_days: how many days ahead to look

    Returns:
        List of dicts sorted by date:
        [{"date": ..., "name": ..., "multiplier": ..., "days_away": ...}]
    """
    start = datetime.strptime(from_date, "%Y-%m-%d").date()
    results = []
    for i in range(1, lookahead_days + 1):
        check_date = (start + timedelta(days=i)).isoformat()
        entry = FESTIVAL_LOOKUP.get(check_date)
        if entry:
            results.append({
                "date":       check_date,
                "name":       entry["name"],
                "multiplier": entry["multiplier"],
                "days_away":  i,
            })
    return results


def get_next_festival(from_date: str, lookahead_days: int = 30) -> Optional[dict]:
    """Returns the next single upcoming festival within N days, or None."""
    upcoming = get_upcoming_festivals(from_date, lookahead_days)
    return upcoming[0] if upcoming else None


def reload_festivals():
    """Hot-reload the festival JSON (useful if file is updated at runtime)."""
    global FESTIVAL_LOOKUP
    FESTIVAL_LOOKUP = _load_festivals()
    print(f"[festival_service] Reloaded {len(FESTIVAL_LOOKUP)} festival entries.")
