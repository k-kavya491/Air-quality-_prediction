import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from influxdb_client import Point

from db.influx_client import write_points

load_dotenv()

WAQI_TOKEN = os.getenv("WAQI_TOKEN")

# Bounding box: south-west lat, south-west lon, north-east lat, north-east lon
CITY_BOUNDS = "17.55,83.05,17.90,83.45"
# Fallback: search WAQI by city name
CITY_KEYWORD = "visakhapatnam"


def get_stations():
    """List WAQI stations: try the bounding box, then fall back to keyword search."""
    stations = []

    r = requests.get(
        "https://api.waqi.info/map/bounds/",
        params={"latlng": CITY_BOUNDS, "token": WAQI_TOKEN},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "ok":
        stations = data["data"]
    else:
        print("Bounds request failed:", data)

    if not stations:
        print("Bounding box empty, trying keyword search...")
        r = requests.get(
            "https://api.waqi.info/search/",
            params={"keyword": CITY_KEYWORD, "token": WAQI_TOKEN},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "ok":
            stations = data["data"]
        if not stations:
            print("Keyword search also empty. Raw response:", data)

    return stations


def get_station_feed(uid):
    """Fetch pollutant readings for one station."""
    r = requests.get(
        f"https://api.waqi.info/feed/@{uid}/",
        params={"token": WAQI_TOKEN},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "ok":
        return None
    return data["data"]


def pollutant(iaqi, key):
    """Return a pollutant value, or None if the sensor doesn't report it."""
    value = iaqi.get(key, {}).get("v")
    return float(value) if value is not None else None

def parse_time(d):
    """Read the reading time from WAQI data, trying more than one format."""
    t = d.get("time") or {}

    iso = t.get("iso")
    if iso:
        try:
            return datetime.fromisoformat(iso)
        except ValueError:
            pass

    s = t.get("s")    # looks like "2026-11-05 10:00:00"
    tz = t.get("tz")  # looks like "+05:30"
    if s:
        try:
            return datetime.fromisoformat(f"{s}{tz}" if tz else s)
        except ValueError:
            pass

    print("Unreadable time:", t)
    return None
def fetch_and_store():
    points = []
    stations = get_stations()
    print(f"Stations found in area: {len(stations)}")

    for s in stations:
        uid = s["uid"]
        try:
            d = get_station_feed(uid)
        except Exception as e:
            print(f"Skipping station {uid}: {e}")
            continue
        if not d:
            print(f"Station {uid}: no data returned")
            continue

        iaqi = d.get("iaqi", {})
        ts = parse_time(d)
        if ts is None:
            print(f"Skipping station {uid}: bad timestamp")
            continue

        point = (
            Point("aqi_readings")
            .tag("station_id", str(uid))
            .tag("station_name", d["city"]["name"])
            .tag("source", "waqi")
            .time(ts)
        )

        fields = {
            "aqi": float(d["aqi"]) if str(d.get("aqi")).isdigit() else None,
            "pm25": pollutant(iaqi, "pm25"),
            "pm10": pollutant(iaqi, "pm10"),
            "no2": pollutant(iaqi, "no2"),
            "o3": pollutant(iaqi, "o3"),
            "co": pollutant(iaqi, "co"),
        }
        # Only store fields that have a value, so offline sensors don't crash the pipeline
        for name, value in fields.items():
            if value is not None:
                point.field(name, value)

        geo = d["city"].get("geo")
        if geo:
            point.field("lat", float(geo[0])).field("lon", float(geo[1]))
        points.append(point)

    if points:
        write_points(points)
    print(f"Stored {len(points)} station readings")


if __name__ == "__main__":
    fetch_and_store()