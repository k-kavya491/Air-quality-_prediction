from datetime import datetime, timezone

import requests

from core.config import settings
from ingestion.errors import ExternalAPIError


TRAFFIC_FLOW_URL = (
    "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
)


def fetch_traffic(lat: float, lon: float) -> dict:
    """Fetch traffic flow for the road segment nearest the supplied coordinates."""
    if not settings.TOMTOM_API_KEY:
        raise ExternalAPIError("TomTom API key is missing")

    try:
        response = requests.get(
            TRAFFIC_FLOW_URL,
            params={
                "point": f"{lat},{lon}",
                "key": settings.TOMTOM_API_KEY,
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        raise ExternalAPIError("TomTom Traffic API is unreachable or returned invalid data")

    segment = payload.get("flowSegmentData") or {}
    if not segment:
        raise ExternalAPIError("TomTom returned no traffic flow data for this location")

    return {
        "current_speed_kmh": segment.get("currentSpeed"),
        "free_flow_speed_kmh": segment.get("freeFlowSpeed"),
        "current_travel_time_seconds": segment.get("currentTravelTime"),
        "free_flow_travel_time_seconds": segment.get("freeFlowTravelTime"),
        "confidence": segment.get("confidence"),
        "road_closed": segment.get("roadClosure"),
        "functional_road_class": segment.get("frc"),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source": "tomtom",
    }
