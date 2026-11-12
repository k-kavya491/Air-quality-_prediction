from ingestion import weather_client, traffic_client
from ingestion.errors import ExternalAPIError
from services import air_quality
from services.environment_cleaning import clean_environmental_data
from services.environmental_aggregator import aggregate_environmental_data
from db.environmental_storage import store_environmental_reading


class NoEnvironmentalData(Exception):
    pass


def get_current_environmental_data(lat: float, lon: float) -> dict:
    warnings = []
    aq_data = weather_data = traffic_data = None

    try:
        aq_data = air_quality.get_current_air_quality(lat, lon)
    except air_quality.NoAirQualityData as exc:
        warnings.append(f"Air quality: {exc}")
    except Exception:
        warnings.append("Air quality provider failed")

    try:
        weather_data = weather_client.fetch_weather(lat, lon)
    except ExternalAPIError as exc:
        warnings.append(f"Weather: {exc}")

    try:
        traffic_data = traffic_client.fetch_traffic(lat, lon)
    except ExternalAPIError as exc:
        warnings.append(f"Traffic: {exc}")

    if aq_data is None and weather_data is None and traffic_data is None:
        raise NoEnvironmentalData("No environmental providers returned data")

    combined = aggregate_environmental_data(
        lat, lon, aq_data, weather_data, traffic_data, warnings
    )
    cleaned, cleaning_warnings = clean_environmental_data(combined)
    cleaned["warnings"].extend(cleaning_warnings)

    try:
        store_environmental_reading(cleaned)
        cleaned["storage"] = {"stored": True, "database": "influxdb"}
    except Exception:
        cleaned["storage"] = {
            "stored": False,
            "database": "influxdb",
            "warning": "Historical storage is unavailable; live data is still returned",
        }
        cleaned["warnings"].append("InfluxDB write failed; live response was not discarded")

    return cleaned
