import time
from datetime import datetime, timezone

from ingestion import openaq_client, waqi_client
from ingestion.errors import ExternalAPIError
from services import pollutants

CACHE_SECONDS = 600  # 10 minutes, to respect provider rate limits
MAX_STATIONS = 3
MAX_CANDIDATES = 6
_cache = {}


class NoAirQualityData(Exception):
    def __init__(self, message, unavailable=False):
        super().__init__(message)
        self.unavailable = unavailable


def _collect_openaq(lat, lon, warnings):
    locations = openaq_client.find_locations(lat, lon)

    def distance(loc):
        c = loc.get("coordinates") or {}
        try:
            return pollutants.haversine_km(
                lat, lon, float(c["latitude"]), float(c["longitude"])
            )
        except (KeyError, TypeError, ValueError):
            return float("inf")

    candidates = sorted(locations, key=distance)[:MAX_CANDIDATES]
    stations, dropped_total = [], 0

    for loc in candidates:
        if len(stations) >= MAX_STATIONS:
            break
        loc_id = loc.get("id")
        if loc_id is None:
            continue
        try:
            sensors = loc.get("sensors") or openaq_client.get_location_sensors(loc_id)
            latest = openaq_client.get_latest(loc_id)
        except ExternalAPIError as e:
            warnings.append(str(e))
            break

        sensor_map = {}
        for s in sensors:
            p = s.get("parameter") or {}
            if s.get("id") is not None and p.get("name"):
                sensor_map[s["id"]] = {"name": p["name"], "units": p.get("units")}

        station, dropped = pollutants.normalize_openaq_station(
            loc, sensor_map, latest, lat, lon
        )
        dropped_total += dropped
        if station:
            stations.append(station)

    if dropped_total:
        warnings.append(
            f"{dropped_total} OpenAQ readings were ignored (invalid or older than 24 hours)"
        )
    if not stations:
        warnings.append("No recent OpenAQ readings found within 25 km")
    return stations


def get_current_air_quality(lat, lon):
    key = (round(lat, 2), round(lon, 2))
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]

    warnings, stations, aqi, indices = [], [], None, {}
    failed = 0

    try:
        data = waqi_client.fetch_geo_feed(lat, lon)
        parsed = pollutants.normalize_waqi(data, lat, lon)
        warnings.extend(parsed["warnings"])
        aqi = parsed["aqi"]
        indices = parsed["indices"]
        if parsed["station"]:
            stations.append(parsed["station"])
    except ExternalAPIError as e:
        warnings.append(str(e))
        failed += 1

    try:
        stations.extend(_collect_openaq(lat, lon, warnings))
    except ExternalAPIError as e:
        warnings.append(str(e))
        failed += 1

    if aqi is None and not stations:
        if failed == 2:
            raise NoAirQualityData(
                "Air quality providers are unavailable right now", unavailable=True
            )
        raise NoAirQualityData("No air quality data found near this location")

    pollutant_summary = pollutants.summarize_pollutants(stations)

    if aqi is None:
        estimated = pollutants.estimate_aqi(pollutant_summary)
        if estimated:
            aqi = estimated
            warnings.append(
                "No live WAQI station near you, so the AQI was calculated from "
                "PM2.5 and PM10 readings at the nearest monitoring station"
            )

    stations.sort(
        key=lambda s: s["distance_km"] if s["distance_km"] is not None else float("inf")
    )
    result = {
        "latitude": lat,
        "longitude": lon,
        "aqi": aqi,
        "pollutants": pollutant_summary,
        "pollutant_indices": indices,
        "stations": stations,
        "warnings": warnings,
        "retrieved_at": datetime.now(timezone.utc),
    }
    _cache[key] = (time.time(), result)
    return result