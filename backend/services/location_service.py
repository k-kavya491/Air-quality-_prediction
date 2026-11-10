from datetime import datetime, timezone

from influxdb_client import Point

from core.config import settings
from db.influx_client import client, write_points
from schemas.location import LocationIn, LocationOut


def process_location(data: LocationIn) -> LocationOut:
    """Validate-and-normalize a location. Saves history if a user id is given."""
    now = datetime.now(timezone.utc)
    captured = data.captured_at or now
    if captured.tzinfo is None:
        captured = captured.replace(tzinfo=timezone.utc)
    if captured > now:
        captured = now

    lat = round(data.latitude, 5)
    lon = round(data.longitude, 5)

    stored = False
    if data.user_id is not None:
        point = (
            Point("user_location_history")
            .tag("user_id", str(data.user_id))
            .tag("source", data.source)
            .field("latitude", lat)
            .field("longitude", lon)
            .time(captured)
        )
        if data.accuracy_m is not None:
            point.field("accuracy_m", float(data.accuracy_m))
        try:
            write_points([point])
            stored = True
        except Exception:
            stored = False

    return LocationOut(
        latitude=lat,
        longitude=lon,
        accuracy_m=data.accuracy_m,
        user_id=data.user_id,
        source=data.source,
        captured_at=captured,
        stored=stored,
    )


def get_latest_location(user_id: int):
    """Most recent saved location for a user, or None."""
    uid = int(user_id)
    query = f'''
from(bucket: "{settings.INFLUX_BUCKET}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "user_location_history" and r.user_id == "{uid}")
  |> last()
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
    try:
        tables = client.query_api().query(query)
    except Exception:
        return None

    for table in tables:
        for rec in table.records:
            v = rec.values
            if v.get("latitude") is None or v.get("longitude") is None:
                continue
            return LocationOut(
                latitude=v["latitude"],
                longitude=v["longitude"],
                accuracy_m=v.get("accuracy_m"),
                user_id=uid,
                source=v.get("source") or "browser",
                captured_at=rec.get_time(),
                stored=True,
            )
    return None