"""
weather_service.py — Person 2 / AI Engine
==========================================
Fetches and stores daily weather for Kandukur, Andhra Pradesh.
Uses OpenWeatherMap free tier (1,000 calls/day limit).

Setup:
  1. Get free API key at openweathermap.org (takes 2 min)
  2. Add to .env:  OPENWEATHER_API_KEY=your_key_here
  3. Run: py -c "from engine.weather_service import fetch_and_store_weather; fetch_and_store_weather()"

Kandukur coordinates: lat=15.2131, lon=79.9042 (Nellore district, AP)
"""

import os
import sqlite3
import requests
from datetime import date, timedelta, datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
API_KEY   = os.getenv("OPENWEATHER_API_KEY", "")
CITY_NAME = "Kandukur,IN"
LAT       = 15.2131
LON       = 79.9042
UNITS     = "metric"

_HERE    = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.environ.get("DB_PATH", os.path.join(_HERE, "..", "..", "hotel_aditya.db"))


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    """Create weather_data table if it doesn't exist (resilient if Person 1 already made it)."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            date        TEXT PRIMARY KEY,
            max_temp    REAL,
            min_temp    REAL,
            condition   TEXT,
            rainfall_mm REAL
        )
    """)
    conn.commit()
    conn.close()


# ── Public API ─────────────────────────────────────────────────────────────────

def fetch_and_store_weather(target_date: Optional[str] = None) -> Optional[dict]:
    """
    Fetches weather forecast for target_date (default = tomorrow) and saves to DB.

    Uses the /forecast endpoint (free tier) — returns 3-hourly data for next 5 days.
    We pick the 8 slots covering the target date and aggregate.

    Args:
        target_date: 'YYYY-MM-DD' string (default: tomorrow)

    Returns:
        Weather dict or None if API call fails
    """
    if not API_KEY:
        print("[weather_service] WARNING: OPENWEATHER_API_KEY not set. Returning mock data.")
        return _mock_weather(target_date)

    if target_date is None:
        target_date = (date.today() + timedelta(days=1)).isoformat()

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat":   LAT,
            "lon":   LON,
            "appid": API_KEY,
            "units": UNITS,
            "cnt":   40,  # max forecast slots (5 days × 8 slots/day)
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Filter slots for target date
        slots = [
            item for item in data["list"]
            if item["dt_txt"].startswith(target_date)
        ]

        if not slots:
            # Target date beyond 5-day window — use last available slot
            slots = data["list"][-4:]

        temps      = [s["main"]["temp"] for s in slots]
        conditions = [s["weather"][0]["main"] for s in slots]
        rainfall   = sum(s.get("rain", {}).get("3h", 0) for s in slots)

        weather = {
            "date":        target_date,
            "max_temp":    round(max(temps), 1),
            "min_temp":    round(min(temps), 1),
            "condition":   max(set(conditions), key=conditions.count),  # most common
            "rainfall_mm": round(rainfall, 2),
        }

        _store_weather(weather)
        print(f"[weather_service] Fetched: {weather}")
        return weather

    except requests.RequestException as e:
        print(f"[weather_service] API request failed: {e}")
        return _mock_weather(target_date)
    except Exception as e:
        print(f"[weather_service] Unexpected error: {e}")
        return _mock_weather(target_date)


def get_weather_for_date(target_date: str) -> Optional[dict]:
    """
    Returns weather from DB for a given date.
    If not in DB, tries to fetch it from API.

    Args:
        target_date: 'YYYY-MM-DD'

    Returns:
        dict with keys: date, max_temp, min_temp, condition, rainfall_mm
        or None if unavailable
    """
    _ensure_table()
    conn = _get_conn()
    row = conn.execute(
        "SELECT date, max_temp, min_temp, condition, rainfall_mm FROM weather_data WHERE date = ?",
        (target_date,)
    ).fetchone()
    conn.close()

    if row:
        return dict(row)

    # Not in DB — try to fetch (works if within 5-day window)
    return fetch_and_store_weather(target_date)


def get_weather_context_string(weather: Optional[dict]) -> str:
    """Returns a short human-readable string for the UI banner."""
    if not weather:
        return "Weather unavailable"
    cond = weather.get("condition", "Clear")
    temp = weather.get("max_temp", "--")
    rain = weather.get("rainfall_mm", 0)
    icons = {
        "Clear": "☀️", "Clouds": "⛅", "Rain": "🌧️",
        "Thunderstorm": "⛈️", "Drizzle": "🌦️", "Mist": "🌫️",
    }
    icon = icons.get(cond, "🌡️")
    base = f"{icon} {cond}  {temp}°C"
    if rain > 2:
        base += f"  💧 {rain:.1f}mm rain"
    return base


# ── Internal helpers ───────────────────────────────────────────────────────────

def _store_weather(weather: dict):
    _ensure_table()
    conn = _get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO weather_data (date, max_temp, min_temp, condition, rainfall_mm)
        VALUES (:date, :max_temp, :min_temp, :condition, :rainfall_mm)
    """, weather)
    conn.commit()
    conn.close()


def _mock_weather(target_date: str) -> dict:
    """
    Returns realistic mock weather for Kandukur (April–May = hot & dry).
    Used when API key is missing or request fails.
    """
    import random
    rng = random.Random(hash(target_date) % 10000)
    temp = round(rng.uniform(37, 42), 1)
    rain = round(rng.uniform(0, 3), 2) if rng.random() < 0.10 else 0.0
    cond = "Rain" if rain > 1.5 else ("Clouds" if rng.random() < 0.15 else "Clear")
    mock = {
        "date":        target_date,
        "max_temp":    temp,
        "min_temp":    round(temp - rng.uniform(6, 9), 1),
        "condition":   cond,
        "rainfall_mm": rain,
    }
    print(f"[weather_service] Using MOCK weather for {target_date}: {mock}")
    _store_weather(mock)
    return mock
