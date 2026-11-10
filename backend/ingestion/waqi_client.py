import requests

from core.config import settings
from ingestion.errors import ExternalAPIError


def _request(url, params=None):
    if not settings.WAQI_TOKEN:
        raise ExternalAPIError("WAQI token is missing")
    query = {"token": settings.WAQI_TOKEN, **(params or {})}
    try:
        r = requests.get(url, params=query, timeout=15)
        r.raise_for_status()
        body = r.json()
    except (requests.RequestException, ValueError):
        # The error text is not passed on because it would contain the token
        raise ExternalAPIError("WAQI is unreachable")
    if body.get("status") != "ok":
        raise ExternalAPIError("WAQI has no data for this request")
    return body.get("data")


def fetch_geo_feed(lat, lon):
    """Nearest WAQI station feed for a coordinate."""
    return _request(f"https://api.waqi.info/feed/geo:{lat:.4f};{lon:.4f}/") or {}


def fetch_bounds(bounds):
    """All WAQI stations inside a box: 'lat1,lon1,lat2,lon2'."""
    return _request("https://api.waqi.info/map/bounds/", {"latlng": bounds}) or []


def search_stations(keyword):
    """WAQI stations matching a name."""
    return _request("https://api.waqi.info/search/", {"keyword": keyword}) or []