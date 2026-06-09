"""
category_weather_map.py — Person 2 / AI Engine
================================================
Maps weather conditions to demand multipliers for each food category.
Tuned for Kandukur, Andhra Pradesh climate:
  - April/May: very hot pre-monsoon (37–43°C)
  - June onwards: southwest monsoon

Usage:
    from engine.category_weather_map import compute_weather_factor
    factor = compute_weather_factor("biryani", weather_dict)
"""

def compute_weather_factor(category: str, weather: dict) -> float:
    """
    Returns a demand multiplier for the given food category based on weather.

    Args:
        category: one of 'biryani', 'chicken', 'beverage', 'ice_cream',
                  'soup', 'bread', 'rice', 'starter', 'seafood', 'egg',
                  'family_pack', 'veg'
        weather: dict with keys: condition (str), max_temp (float),
                 min_temp (float), rainfall_mm (float)

    Returns:
        float multiplier (e.g. 1.30 = 30% more demand, 0.70 = 30% less)
    """
    if not weather:
        return 1.0

    condition   = (weather.get("condition") or "Clear").lower()
    max_temp    = float(weather.get("max_temp") or 32)
    rainfall_mm = float(weather.get("rainfall_mm") or 0)

    is_rainy    = rainfall_mm > 2.0 or "rain" in condition or "thunder" in condition
    is_very_hot = max_temp >= 39          # scorching day (common in AP April–May)
    is_hot      = 35 <= max_temp < 39     # warm-hot
    is_cool     = max_temp < 28           # cool / overcast post-rain

    # ── Beverages (Cold Drinks, Lassi, Milk Shakes) ──
    if category == "beverage":
        if is_rainy:   return 0.65   # Rain → fewer people → less drink demand
        if is_very_hot: return 1.55  # Scorching → everyone wants cold drinks
        if is_hot:     return 1.25
        if is_cool:    return 0.85
        return 1.0

    # ── Ice Cream ──
    if category == "ice_cream":
        if is_rainy:   return 0.45   # Rainy day kills ice cream orders
        if is_very_hot: return 1.65
        if is_hot:     return 1.30
        if is_cool:    return 0.75
        return 1.0

    # ── Soups ──
    if category == "soup":
        if is_rainy:   return 1.50   # Rain → hot soup comfort food
        if is_cool:    return 1.35
        if is_very_hot: return 0.75  # Nobody orders soup at 42°C
        return 1.0

    # ── Biryani ── (comfort food, slightly higher on rainy/festival days)
    if category == "biryani":
        if is_rainy:   return 1.20
        if is_very_hot: return 0.95  # Slight dip when it's too hot to go out
        return 1.0

    # ── Chicken ──
    if category == "chicken":
        if is_rainy:   return 1.18   # Rainy-day non-veg comfort
        return 1.0

    # ── Family Packs ──
    if category == "family_pack":
        if is_rainy:   return 1.20   # Takeaway packs when families don't want to eat out
        if is_very_hot: return 0.90  # Less footfall on extremely hot days
        return 1.0

    # ── Starters (Lollypop, Fries, Gobi, Baby Corn) ──
    if category == "starter":
        if is_rainy:   return 0.85   # Fewer walkins
        if is_very_hot: return 0.90
        return 1.0

    # ── Dairy (Paneer, Curd) ── mostly stable, slight dip in extreme heat
    if category == "dairy":
        if is_very_hot: return 0.92  # Slight dip on very hot days
        if is_cool:    return 1.08
        return 1.0

    # ── Other / Veg (Mushroom, Pulka, Mixed items) ── mostly weather-neutral
    if category in ("other", "veg"):
        if is_rainy:   return 0.88
        return 1.0

    # ── Bread (Naan, Roti, Pulka) ── mostly weather-neutral
    if category in ("bread", "rice", "egg", "seafood"):
        if is_rainy:   return 0.90   # Slightly lower due to fewer walkins
        return 1.0

    return 1.0  # default: no weather impact


def get_weather_description(weather: dict) -> str:
    """Returns a human-readable weather summary for UI display."""
    if not weather:
        return "Weather data unavailable"

    temp      = weather.get("max_temp", "--")
    condition = weather.get("condition", "--")
    rain      = weather.get("rainfall_mm", 0)

    desc = f"{condition}, {temp}°C"
    if rain > 2:
        desc += f" ({rain:.1f}mm rain expected)"
    return desc
