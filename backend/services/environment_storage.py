from influxdb_client import Point

from db.influx_client import write_points


def _location_key(lat, lon):
    return f"{lat:.2f},{lon:.2f}"


def build_points(env):
    lat, lon = env["latitude"], env["longitude"]
    loc = _location_key(lat, lon)
    points = []

    air = env.get("air_quality")
    if air:
        for p in air["pollutants"]:
            points.append(
                Point("env_pollutants")
                .tag("location_key", loc)
                .tag("parameter", p["parameter"])
                .tag("station_id", str(p["station_id"]))
                .tag("source", p["source"])
                .field("value", float(p["value"]))
                .field("unit", p["unit"])
                .field("station_name", p["station_name"])
                .field("distance_km", float(p["distance_km"]))
                .field("query_latitude", float(lat))
                .field("query_longitude", float(lon))
                .time(p["timestamp"])
            )
        aqi = air.get("aqi")
        if aqi:
            point = (
                Point("env_aqi")
                .tag("location_key", loc)
                .tag("source", aqi["source"])
                .field("value", float(aqi["value"]))
                .field("category", aqi["category"])
                .field("station_name", aqi.get("station") or "")
                .field("query_latitude", float(lat))
                .field("query_longitude", float(lon))
                .time(aqi.get("timestamp") or env["retrieved_at"])
            )
            if aqi.get("dominant_pollutant"):
                point.field("dominant_pollutant", aqi["dominant_pollutant"])
            points.append(point)

    w = env.get("weather")
    if w:
        point = (
            Point("env_weather")
            .tag("location_key", loc)
            .tag("source", w["source"])
            .field("query_latitude", float(lat))
            .field("query_longitude", float(lon))
            .time(w["observed_at"])
        )
        for name in (
            "temperature_c", "humidity_pct", "pressure_hpa", "wind_speed_ms",
            "wind_direction_deg", "wind_gust_ms", "rain_mm", "clouds_pct", "visibility_m",
        ):
            if w.get(name) is not None:
                point.field(name, float(w[name]))
        if w.get("condition"):
            point.field("condition", w["condition"])
        points.append(point)

    t = env.get("traffic")
    if t:
        point = (
            Point("env_traffic")
            .tag("location_key", loc)
            .tag("source", t["source"])
            .field("congestion_index", float(t["congestion_index"]))
            .field("level", t["level"])
            .field("road_closure", bool(t["road_closure"]))
            .field("query_latitude", float(lat))
            .field("query_longitude", float(lon))
            .time(t["observed_at"])
        )
        for name in (
            "current_speed_kmh", "free_flow_speed_kmh",
            "current_travel_time_s", "free_flow_travel_time_s", "confidence",
        ):
            if t.get(name) is not None:
                point.field(name, float(t[name]))
        if t.get("road_class"):
            point.tag("road_class", t["road_class"])
        points.append(point)

    return points


def store_environment(env):
    """Write one environment snapshot to InfluxDB. Returns the number of points."""
    points = build_points(env)
    if points:
        write_points(points)
    return len(points)