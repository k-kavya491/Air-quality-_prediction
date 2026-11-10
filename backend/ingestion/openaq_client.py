import requests

from core.config import settings
from ingestion.errors import ExternalAPIError

BASE = "https://api.openaq.org/v3"


def _get(path, params=None):
    if not settings.OPENAQ_KEY:
        raise ExternalAPIError("OpenAQ key is missing")
    try:
        r = requests.get(
            BASE + path,
            params=params,
            headers={"X-API-Key": settings.OPENAQ_KEY},
            timeout=20,
        )
    except requests.RequestException:
        raise ExternalAPIError("OpenAQ is unreachable")

    if r.status_code == 429:
        raise ExternalAPIError("OpenAQ rate limit reached, try again later")
    if r.status_code in (401, 403):
        raise ExternalAPIError("OpenAQ rejected the API key")
    if r.status_code != 200:
        raise ExternalAPIError(f"OpenAQ returned an error ({r.status_code})")
    try:
        return r.json().get("results", [])
    except ValueError:
        raise ExternalAPIError("OpenAQ returned an unreadable response")


def find_locations(lat, lon, radius_m=25000, limit=10):
    return _get(
        "/locations",
        {"coordinates": f"{lat:.5f},{lon:.5f}", "radius": radius_m, "limit": limit},
    )


def get_location_sensors(location_id):
    return _get(f"/locations/{location_id}/sensors")


def get_latest(location_id):
    return _get(f"/locations/{location_id}/latest", {"limit": 100})


def get_sensor_measurements(sensor_id, datetime_from, datetime_to, limit=1000):
    """Historical readings for one sensor. Dates are ISO strings."""
    return _get(
        f"/sensors/{sensor_id}/measurements",
        {"datetime_from": datetime_from, "datetime_to": datetime_to, "limit": limit},
    )