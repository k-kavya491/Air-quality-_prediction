from datetime import datetime, timezone

from influxdb_client import Point

from core.config import settings
from db.influx_client import write_points


def store_environmental_reading(data: dict) -> None:
    """Persist available combined measurements as one InfluxDB time-series point."""
    location = data.get("location") or {}
    lat = location.get("latitude")
    lon = location.get("longitude")
    if lat is None or lon is None:
        raise ValueError("Environmental record is missing coordinates")

    try:
        timestamp = datetime.fromisoformat(data["retrieved_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        timestamp = datetime.now(timezone.utc)

    point = (
        Point("environmental_readings")
        .tag("location_key", f"{float(lat):.4f},{float(lon):.4f}")
        .tag("source", "airsense_combined")
        .field("latitude", float(lat))
        .field("longitude", float(lon))
        .time(timestamp)
    )

    air_quality = data.get("air_quality") or {}
    aqi = air_quality.get("aqi")
    if isinstance(aqi, dict):
        aqi = aqi.get("value")
    if isinstance(aqi, (int, float)):
        point.field("aqi", float(aqi))

    for item in air_quality.get("pollutants") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("parameter", "")).lower().replace(".", "_")
        value = item.get("value")
        if name and name.replace("_", "").isalnum() and isinstance(value, (int, float)):
            point.field(f"pollutant_{name}", float(value))

    weather = data.get("weather") or {}
    for name in (
        "temperature_c", "feels_like_c", "humidity_percent", "pressure_hpa",
        "wind_speed_mps", "wind_direction_degrees", "rainfall_mm",
        "cloudiness_percent",
    ):
        value = weather.get(name)
        if isinstance(value, (int, float)):
            point.field(name, float(value))

    traffic = data.get("traffic") or {}
    for name in (
        "current_speed_kmh", "free_flow_speed_kmh",
        "current_travel_time_seconds", "free_flow_travel_time_seconds", "confidence",
    ):
        value = traffic.get(name)
        if isinstance(value, (int, float)):
            point.field(name, float(value))

    write_points([point])
