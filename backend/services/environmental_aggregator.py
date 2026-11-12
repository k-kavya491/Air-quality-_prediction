from datetime import datetime, timezone


def aggregate_environmental_data(lat, lon, air_quality=None, weather=None, traffic=None, warnings=None):
    """Build one location-keyed response from independently retrieved data sources."""
    return {
        "location": {
            "latitude": float(lat),
            "longitude": float(lon),
        },
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "air_quality": air_quality,
        "weather": weather,
        "traffic": traffic,
        "sources_available": {
            "air_quality": air_quality is not None,
            "weather": weather is not None,
            "traffic": traffic is not None,
        },
        "warnings": list(warnings or []),
    }