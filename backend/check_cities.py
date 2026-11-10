from datetime import datetime, timezone

from core.cities import CITIES
from ingestion import waqi_client
from services import dashboard

now = datetime.now(timezone.utc)
for key, city in CITIES.items():
    try:
        raw = waqi_client.fetch_bounds(city["bounds"])
        source = "box"
        if not raw:
            raw = waqi_client.search_stations(city["keyword"])
            source = "name search"
        usable = sum(1 for i in raw if dashboard._parse_station(i, now))
        print(f"{city['label']:15} found {len(raw):3} via {source:12} usable {usable}")
    except Exception as e:
        print(f"{city['label']:15} error: {e}")