from copy import deepcopy
from datetime import datetime, timezone


RANGES = {
    "aqi": (0, 1000),
    "value": (0, 100000),
    "pm25": (0, 2000),
    "pm10": (0, 3000),
    "no2": (0, 2000),
    "o3": (0, 2000),
    "co": (0, 100000),
    "so2": (0, 2000),
    "temperature_c": (-100, 70),
    "feels_like_c": (-100, 80),
    "humidity_percent": (0, 100),
    "pressure_hpa": (800, 1200),
    "wind_speed_mps": (0, 150),
    "wind_direction_degrees": (0, 360),
    "rainfall_mm": (0, 1000),
    "cloudiness_percent": (0, 100),
    "current_speed_kmh": (0, 300),
    "free_flow_speed_kmh": (0, 300),
    "current_travel_time_seconds": (0, 100000),
    "free_flow_travel_time_seconds": (0, 100000),
    "confidence": (0, 1),
}


def _deduplicate_measurements(items, warnings, field_name):
    if not isinstance(items, list):
        return items
    seen = set()
    result = []
    for item in items:
        if not isinstance(item, dict):
            result.append(item)
            continue
        identity = (
            item.get("parameter"),
            item.get("station_id") or item.get("station_name"),
            str(item.get("timestamp") or item.get("last_updated") or ""),
            item.get("source"),
        )
        if identity in seen:
            warnings.append(f"Duplicate reading removed from {field_name}")
            continue
        seen.add(identity)
        result.append(item)
    return result


def _clean_value(value, warnings, field_name):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, dict):
        return _clean_mapping(value, warnings, field_name)
    if isinstance(value, list):
        if field_name.endswith(".pollutants"):
            value = _deduplicate_measurements(value, warnings, field_name)
        return [
            _clean_value(item, warnings, f"{field_name}[{index}]")
            for index, item in enumerate(value)
        ]
    key = field_name.rsplit(".", 1)[-1].split("[", 1)[0]
    if key in RANGES and value is not None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            warnings.append(f"{field_name} was removed because it was not numeric")
            return None
        low, high = RANGES[key]
        if not low <= number <= high:
            warnings.append(f"{field_name} was removed because it was outside the valid range")
            return None
        return number
    return value


def _clean_mapping(data, warnings, prefix=""):
    cleaned = {}
    for key, value in data.items():
        field_name = f"{prefix}.{key}" if prefix else key
        cleaned[key] = _clean_value(value, warnings, field_name)
    return cleaned


def clean_environmental_data(data: dict) -> tuple[dict, list[str]]:
    """Validate ranges, normalize datetime objects, and remove duplicate readings."""
    warnings = []
    cleaned = _clean_mapping(deepcopy(data), warnings)
    location = cleaned.get("location") or {}
    try:
        lat = float(location["latitude"])
        lon = float(location["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
        location["latitude"] = lat
        location["longitude"] = lon
    except (KeyError, TypeError, ValueError):
        raise ValueError("Environmental data contains invalid coordinates")
    return cleaned, warnings
