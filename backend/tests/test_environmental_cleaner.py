from services.environment_cleaning import clean_environmental_data


def test_cleaner_keeps_valid_values_and_removes_invalid_values():
    payload = {
        "location": {
            "latitude": 17.6868,
            "longitude": 83.2183,
        },
        "weather": {
            "temperature_c": 28.5,
            "humidity_percent": 150,
            "wind_speed_mps": "not-a-number",
        },
        "traffic": {"current_speed_kmh": 42},
    }

    cleaned, warnings = clean_environmental_data(payload)

    assert cleaned["weather"]["temperature_c"] == 28.5
    assert cleaned["weather"]["humidity_percent"] is None
    assert cleaned["weather"]["wind_speed_mps"] is None
    assert cleaned["traffic"]["current_speed_kmh"] == 42
    assert len(warnings) == 2


def test_cleaner_does_not_mutate_original_payload():
    payload = {
        "location": {
            "latitude": 17.6868,
            "longitude": 83.2183,
        },
        "weather": {"humidity_percent": 150},
    }

    clean_environmental_data(payload)

    assert payload["weather"]["humidity_percent"] == 150