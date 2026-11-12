from datetime import datetime, timezone

import requests

from core.config import settings
from ingestion.errors import ExternalAPIError


WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather for a coordinate pair using OpenWeatherMap."""
    if not settings.OWM_KEY:
        raise ExternalAPIError("OpenWeatherMap API key is missing")

    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": settings.OWM_KEY,
                "units": "metric",
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        raise ExternalAPIError("OpenWeatherMap is unreachable or returned invalid data")

    main = payload.get("main") or {}
    wind = payload.get("wind") or {}
    rain = payload.get("rain") or {}
    weather_items = payload.get("weather") or []
    weather = weather_items[0] if weather_items else {}

    timestamp = payload.get("dt")
    try:
        observed_at = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        observed_at = datetime.now(timezone.utc)

    rainfall = rain.get("1h")
    rainfall_period = "1h"
    if rainfall is None:
        rainfall = rain.get("3h")
        rainfall_period = "3h"

    return {
        "temperature_c": main.get("temp"),
        "feels_like_c": main.get("feels_like"),
        "humidity_percent": main.get("humidity"),
        "pressure_hpa": main.get("pressure"),
        "wind_speed_mps": wind.get("speed"),
        "wind_direction_degrees": wind.get("deg"),
        "rainfall_mm": rainfall,
        "rainfall_period": rainfall_period if rainfall is not None else None,
        "cloudiness_percent": (payload.get("clouds") or {}).get("all"),
        "condition": weather.get("description") or weather.get("main"),
        "icon": weather.get("icon"),
        "observed_at": observed_at.isoformat(),
        "source": "openweathermap",
    }
