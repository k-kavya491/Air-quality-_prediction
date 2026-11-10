import time
from datetime import datetime, timedelta, timezone

from core.cities import CITIES
from ingestion import waqi_client
from ingestion.errors import ExternalAPIError
from services import pollutants

CACHE_SECONDS = 600  # 10 minutes, to respect WAQI limits
ALERT_THRESHOLD = 150
SEVERE_THRESHOLD = 200
CATEGORY_ORDER = [
    "Good",
    "Moderate",
    "Unhealthy for Sensitive Groups",
    "Unhealthy",
    "Very Unhealthy",
    "Hazardous",
]
_cache = {}


class NoDashboardData(Exception):
    pass


def _parse_station(item, now):
    """Return a clean station, or None if it has no current reading."""
    aqi = pollutants.to_int(item.get("aqi"))  # "-" means no reading
    if aqi is None or not 0 <= aqi <= 1000:
        return None

    station = item.get("station") or {}
    t = item.get("time") or {}
    if station.get("time"):
        ts = pollutants.parse_timestamp(s=station["time"])
    else:
        ts = pollutants.parse_timestamp(s=t.get("stime"), tz=t.get("tz"))
    if ts is None or ts > now + timedelta(hours=1) or now - ts > pollutants.MAX_AGE:
        return None

    lat, lon = item.get("lat"), item.get("lon")
    geo = station.get("geo") or []
    if (lat is None or lon is None) and len(geo) == 2:
        lat, lon = geo
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        lat = lon = None

    return {
        "uid": str(item.get("uid")),
        "name": station.get("name") or f"Station {item.get('uid')}",
        "aqi": aqi,
        "category": pollutants.aqi_category(aqi),
        "latitude": lat,
        "longitude": lon,
        "last_updated": ts,
    }


def _nearest_live_station(city, now):
    """When no city stations report, use the live station nearest the city centre."""
    lat, lon = city["center"]
    try:
        data = waqi_client.fetch_geo_feed(lat, lon)
    except ExternalAPIError:
        return None

    parsed = pollutants.normalize_waqi(data, lat, lon, now)
    aqi, st = parsed["aqi"], parsed["station"]
    if not aqi or not st:
        return None

    distance = st.get("distance_km")
    where = f"{distance} km away" if distance is not None else "distance unknown"
    return {
        "station": {
            "uid": st["id"],
            "name": aqi["station"],
            "aqi": aqi["value"],
            "category": aqi["category"],
            "latitude": st["latitude"],
            "longitude": st["longitude"],
            "last_updated": aqi["timestamp"],
        },
        "warning": (
            f"No stations in {city['label']} are reporting right now, so the nearest "
            f"live station is shown ({aqi['station']}, {where})"
        ),
    }


def get_overview(city_key):
    hit = _cache.get(city_key)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]

    city = CITIES[city_key]
    warnings = []

    raw = waqi_client.fetch_bounds(city["bounds"])
    if not raw:
        warnings.append("No stations found in the city area, so a name search was used")
        raw = waqi_client.search_stations(city["keyword"])

    now = datetime.now(timezone.utc)
    seen, stations, skipped = set(), [], 0
    for item in raw:
        uid = item.get("uid")
        if uid in seen:
            continue
        seen.add(uid)
        parsed = _parse_station(item, now)
        if parsed:
            stations.append(parsed)
        else:
            skipped += 1

    if skipped:
        warnings.append(
            f"{skipped} stations were ignored (no current reading or older than 24 hours)"
        )
    is_fallback = False

    if not stations:
        fallback = _nearest_live_station(city, now)
        if fallback is None:
            raise NoDashboardData(
                f"No current air quality readings found for {city['label']} "
                f"({len(seen)} stations found, none with a reading from the last 24 hours)"
            )
        stations = [fallback["station"]]
        is_fallback = True
        warnings.append(fallback["warning"])

    stations.sort(key=lambda s: s["aqi"], reverse=True)
    aqis = [s["aqi"] for s in stations]
    avg = round(sum(aqis) / len(aqis))

    counts = {name: 0 for name in CATEGORY_ORDER}
    for s in stations:
        counts[s["category"]] += 1

    result = {
        "city": city_key,
        "city_label": city["label"],
        "stats": {
            "active_stations": len(stations),
            "alerts_now": sum(1 for a in aqis if a > ALERT_THRESHOLD),
            "severe_now": sum(1 for a in aqis if a > SEVERE_THRESHOLD),
            "alert_threshold": ALERT_THRESHOLD,
            "avg_aqi": avg,
            "avg_category": pollutants.aqi_category(avg),
        },
        "stations": stations,
        "category_breakdown": [
            {"category": name, "count": counts[name]} for name in CATEGORY_ORDER
        ],
        "warnings": warnings,
                "is_fallback": is_fallback,
        "updated_at": now,
    }
    _cache[city_key] = (time.time(), result)
    return result