import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from influxdb_client import Point

from db.influx_client import write_points

load_dotenv()

OWM_KEY = os.getenv("OWM_KEY")

# Visakhapatnam city centre
CITY_NAME = "visakhapatnam"
CITY_LAT = 17.6868
CITY_LON = 83.2185


def fetch_and_store():
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": CITY_LAT,
            "lon": CITY_LON,
            "appid": OWM_KEY,
            "units": "metric",
        },
        timeout=20,
    )
    if r.status_code != 200:
        print("Weather request failed:", r.status_code, r.text)
        return

    d = r.json()
    main = d.get("main", {})
    wind = d.get("wind", {})
    ts = datetime.fromtimestamp(d["dt"], tz=timezone.utc)

    point = (
        Point("weather")
        .tag("city", CITY_NAME)
        .tag("source", "openweathermap")
        .time(ts)
    )

    fields = {
        "temperature": main.get("temp"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind_speed": wind.get("speed"),
        "wind_deg": wind.get("deg"),
        "clouds": d.get("clouds", {}).get("all"),
    }
    # Skip missing values instead of crashing
    for name, value in fields.items():
        if value is not None:
            point.field(name, float(value))

    write_points([point])
    print("Stored weather reading")


if __name__ == "__main__":
    fetch_and_store()