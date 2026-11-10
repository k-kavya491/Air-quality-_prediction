import sys
from datetime import datetime, timezone

from core.cities import CITIES
from ingestion import waqi_client
from services import dashboard

key = sys.argv[1] if len(sys.argv) > 1 else "kolkata"
city = CITIES[key]

raw = waqi_client.fetch_bounds(city["bounds"])
print("Stations in the box:", len(raw))
if not raw:
    raw = waqi_client.search_stations(city["keyword"])
    print("Stations from name search:", len(raw))

now = datetime.now(timezone.utc)
for item in raw[:10]:
    station = item.get("station") or {}
    t = item.get("time") or {}
    when = station.get("time") or t.get("stime")
    print(item.get("uid"), "| aqi:", item.get("aqi"), "| time:", when, "|", station.get("name"))

print("Stations the dashboard accepts:", sum(1 for i in raw if dashboard._parse_station(i, now)))