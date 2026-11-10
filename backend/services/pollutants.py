import math
from datetime import datetime, timedelta, timezone

POLLUTANTS = ["pm25", "pm10", "no2", "o3", "co"]
POLLUTANT_ALIASES = {
    "pm25": "pm25",
    "pm2.5": "pm25",
    "pm10": "pm10",
    "no2": "no2",
    "o3": "o3",
    "co": "co",
}
MAX_AGE = timedelta(hours=24)
FAR_STATION_KM = 50
EXPECTED_UNITS = {
    "pm25": {"µg/m³"},
    "pm10": {"µg/m³"},
    "no2": {"µg/m³", "ppm", "ppb"},
    "o3": {"µg/m³", "ppm", "ppb"},
    "co": {"µg/m³", "mg/m³", "ppm", "ppb"},
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def validate_value(value, max_value=100000):
    """Return a float for a valid measurement, else None."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v) or v < 0 or v > max_value:
        return None
    return v


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def clean_unit(unit):
    if not unit:
        return None
    u = str(unit).strip().replace("μ", "µ")
    if u.lower() in ("ug/m3", "µg/m3", "µg/m³"):
        return "µg/m³"
    if u.lower() in ("mg/m3", "mg/m³"):
        return "mg/m³"
    if u.lower() in ("ppm", "ppb"):
        return u.lower()
    return u


def parse_timestamp(iso=None, s=None, tz=None):
    """Parse a provider time into UTC. Returns None if unreadable."""
    for candidate in (iso, f"{s}{tz}" if s and tz else s):
        if not candidate:
            continue
        try:
            dt = datetime.fromisoformat(str(candidate))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def aqi_category(value):
    for limit, label in [
        (50, "Good"),
        (100, "Moderate"),
        (150, "Unhealthy for Sensitive Groups"),
        (200, "Unhealthy"),
        (300, "Very Unhealthy"),
    ]:
        if value <= limit:
            return label
    return "Hazardous"


def normalize_openaq_station(location, sensor_map, latest_results, lat, lon, now=None):
    """Turn one OpenAQ location plus its latest values into a clean station.

    Returns (station or None, number of readings ignored).
    """
    now = now or datetime.now(timezone.utc)
    coords = location.get("coordinates") or {}
    try:
        s_lat, s_lon = float(coords["latitude"]), float(coords["longitude"])
    except (KeyError, TypeError, ValueError):
        return None, 0

    newest = {}
    dropped = 0
    for item in latest_results:
        sensor = sensor_map.get(item.get("sensorsId"))
        if not sensor:
            continue
        name = POLLUTANT_ALIASES.get(str(sensor.get("name") or "").lower())
        if not name:
            continue  # temperature, humidity and other parameters are ignored

        value = validate_value(item.get("value"))
        ts = parse_timestamp(iso=(item.get("datetime") or {}).get("utc"))
        if (
            value is None
            or ts is None
            or ts > now + timedelta(hours=1)
            or now - ts > MAX_AGE
        ):
            dropped += 1
            continue

        unit = clean_unit(sensor.get("units"))
        if unit not in EXPECTED_UNITS[name]:
            dropped += 1
            continue

        current = newest.get(name)
        if current is None or ts > current["timestamp"]:
            newest[name] = {
                "parameter": name,
                "value": value,
                "unit": unit,
                "timestamp": ts,
                "source": "openaq",
            }

    if not newest:
        return None, dropped

    provider = (location.get("provider") or {}).get("name")
    station = {
        "id": str(location.get("id")),
        "name": location.get("name") or f"Location {location.get('id')}",
        "source": "openaq",
        "latitude": s_lat,
        "longitude": s_lon,
        "distance_km": round(haversine_km(lat, lon, s_lat, s_lon), 2),
        "provider": provider,
        "last_updated": max(m["timestamp"] for m in newest.values()),
        "measurements": list(newest.values()),
    }
    return station, dropped


def normalize_waqi(data, lat, lon, now=None):
    """Turn a WAQI feed into a clean AQI value, pollutant indices and a station."""
    now = now or datetime.now(timezone.utc)
    result = {"aqi": None, "indices": {}, "station": None, "warnings": []}

    if not isinstance(data, dict) or not data:
        result["warnings"].append("WAQI returned no station data for this location")
        return result

    t = data.get("time") or {}
    ts = parse_timestamp(iso=t.get("iso"), s=t.get("s"), tz=t.get("tz"))
    if ts is None or ts > now + timedelta(hours=1):
        result["warnings"].append("WAQI reading has no valid timestamp and was ignored")
        return result
    if now - ts > MAX_AGE:
        result["warnings"].append("WAQI reading is older than 24 hours and was ignored")
        return result

    city = data.get("city") or {}
    geo = city.get("geo") or []
    distance = None
    s_lat, s_lon = lat, lon
    try:
        s_lat, s_lon = float(geo[0]), float(geo[1])
        distance = round(haversine_km(lat, lon, s_lat, s_lon), 2)
    except (IndexError, TypeError, ValueError):
        pass
        if distance is not None and distance > FAR_STATION_KM:
            result["warnings"].append(
            f"The nearest WAQI station is {distance} km away, so its reading was not used"
        )
        return result

    # WAQI pollutant values are AQI sub-indices, not concentrations
    iaqi = data.get("iaqi") or {}
    for key in POLLUTANTS:
        v = validate_value((iaqi.get(key) or {}).get("v"), max_value=1000)
        if v is not None:
            result["indices"][key] = v

    station_name = city.get("name") or "WAQI station"
    aqi_value = to_int(data.get("aqi"))
    if aqi_value is not None and 0 <= aqi_value <= 1000:
        result["aqi"] = {
            "value": aqi_value,
            "category": aqi_category(aqi_value),
            "dominant_pollutant": data.get("dominentpol"),  # WAQI's own spelling
            "source": "waqi",
            "station": station_name,
            "timestamp": ts,
        }
    else:
        result["warnings"].append("The WAQI station has no AQI value right now")

    if result["aqi"] or result["indices"]:
        result["station"] = {
            "id": str(data.get("idx") or "waqi"),
            "name": station_name,
            "source": "waqi",
            "latitude": s_lat,
            "longitude": s_lon,
            "distance_km": distance,
            "provider": "World Air Quality Index Project",
            "last_updated": ts,
            "measurements": [
                {
                    "parameter": k,
                    "value": v,
                    "unit": "AQI index",
                    "timestamp": ts,
                    "source": "waqi",
                }
                for k, v in result["indices"].items()
            ],
        }
    return result


def summarize_pollutants(stations):
    """For each pollutant, take the reading from the nearest OpenAQ station that has it."""
    summary = []
    openaq = sorted(
        (s for s in stations if s["source"] == "openaq"),
        key=lambda s: s["distance_km"],
    )
    for name in POLLUTANTS:
        for st in openaq:
            m = next((m for m in st["measurements"] if m["parameter"] == name), None)
            if m:
                summary.append(
                    {
                        **m,
                        "station_id": st["id"],
                        "station_name": st["name"],
                        "distance_km": st["distance_km"],
                    }
                )
                break
    return summary
    

# US EPA breakpoints (the scale WAQI uses): concentration low, high, index low, high
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 350.4, 301, 400),
    (350.5, 500.4, 401, 500),
]
PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 504, 301, 400),
    (505, 604, 401, 500),
]


def _sub_index(value, table):
    for c_lo, c_hi, i_lo, i_hi in table:
        if c_lo <= value <= c_hi:
            return round((i_hi - i_lo) / (c_hi - c_lo) * (value - c_lo) + i_lo)
    return 500 if value > table[-1][1] else None


def estimate_aqi(pollutant_summary):
    """Estimate a US EPA AQI from PM2.5 and PM10 concentrations in µg/m³."""
    candidates = []
    for p in pollutant_summary:
        if p.get("unit") != "µg/m³":
            continue
        if p["parameter"] == "pm25":
            idx = _sub_index(math.floor(p["value"] * 10) / 10, PM25_BREAKPOINTS)
        elif p["parameter"] == "pm10":
            idx = _sub_index(math.floor(p["value"]), PM10_BREAKPOINTS)
        else:
            continue
        if idx is not None:
            candidates.append((idx, p))

    if not candidates:
        return None
    idx, p = max(candidates, key=lambda c: c[0])
    return {
        "value": idx,
        "category": aqi_category(idx),
        "dominant_pollutant": p["parameter"],
        "source": "openaq_calculated",
        "station": p["station_name"],
        "timestamp": p["timestamp"],
    }