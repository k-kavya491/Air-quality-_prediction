
import pytest

from services import environment
from ingestion.errors import ExternalAPIError


def test_weather_failure_does_not_stop_other_providers(monkeypatch):
    monkeypatch.setattr(
        environment.air_quality,
        "get_current_air_quality",
        lambda lat, lon: {"aqi": 50},
    )

    def fail_weather(lat, lon):
        raise ExternalAPIError("Weather API unavailable")

    monkeypatch.setattr(environment.weather_client, "fetch_weather", fail_weather)
    monkeypatch.setattr(
        environment.traffic_client,
        "fetch_traffic",
        lambda lat, lon: {"current_speed_kmh": 30},
    )
    monkeypatch.setattr(
        environment,
        "store_environmental_reading",
        lambda data: None,
    )

    result = environment.get_current_environmental_data(17.6868, 83.2183)

    assert result["air_quality"] is not None
    assert result["traffic"] is not None
    assert any("Weather:" in warning for warning in result["warnings"])


def test_all_provider_failures_raise_no_environmental_data(monkeypatch):
    def fail_aqi(lat, lon):
        raise environment.air_quality.NoAirQualityData("AQI unavailable")

    def fail_weather(lat, lon):
        raise ExternalAPIError("Weather unavailable")

    def fail_traffic(lat, lon):
        raise ExternalAPIError("Traffic unavailable")

    monkeypatch.setattr(environment.air_quality, "get_current_air_quality", fail_aqi)
    monkeypatch.setattr(environment.weather_client, "fetch_weather", fail_weather)
    monkeypatch.setattr(environment.traffic_client, "fetch_traffic", fail_traffic)

    with pytest.raises(environment.NoEnvironmentalData):
        environment.get_current_environmental_data(17.6868, 83.2183)
