import { useEffect, useState } from "react";
import useGeolocation from "../hooks/useGeolocation";
import { getCurrentAirQuality } from "../services/api";
import { colorFor } from "../utils/aqi";

const SOURCE_LABELS = {
  waqi: "Reported by a WAQI station",
  openaq_calculated: "Calculated from PM readings (US EPA scale)",
};

export default function LocationPanel() {
  const { status, location, error, requestLocation } = useGeolocation();
  const [air, setAir] = useState(null);
  const [airError, setAirError] = useState(null);

  const lat = location?.latitude;
  const lon = location?.longitude;

  useEffect(() => {
    if (lat == null || lon == null) return;
    let cancelled = false;
    setAir(null);
    setAirError(null);
    getCurrentAirQuality(lat, lon)
      .then((res) => {
        if (!cancelled) setAir(res.data);
      })
      .catch((err) => {
        if (!cancelled)
          setAirError(
            err.response?.data?.detail || "Could not load air quality for your location."
          );
      });
    return () => {
      cancelled = true;
    };
  }, [lat, lon]);

  const aqiStation = air?.aqi
    ? air.stations.find((s) => s.name === air.aqi.station)
    : null;

  return (
    <div>
      {status === "idle" && (
        <>
          <p className="placeholder">
            Share your location to see air quality near you. Your browser will
            ask for permission first.
          </p>
          <button className="btn" onClick={requestLocation}>
            📍 Share my location
          </button>
        </>
      )}

      {status === "requesting" && (
        <p className="placeholder">⏳ Waiting for permission and locating you...</p>
      )}

      {error && <div className="error-box">⚠️ {error.message}</div>}

      {location && (
        <div className="coords">
          <p>🧭 Latitude: <strong>{location.latitude.toFixed(5)}</strong></p>
          <p>🧭 Longitude: <strong>{location.longitude.toFixed(5)}</strong></p>
          {location.accuracy_m != null && (
            <p>🎯 Accuracy: ± {Math.round(location.accuracy_m)} m</p>
          )}
          <p>🕒 Captured: {new Date(location.captured_at).toLocaleString()}</p>
        </div>
      )}

      {location && !air && !airError && (
        <p className="placeholder">⏳ Loading air quality near you...</p>
      )}

      {air && (
        <div className="coords">
          {air.aqi ? (
            <>
              <p style={{ margin: "14px 0 0", fontSize: 14, color: "var(--muted)" }}>
                💨 Air quality near you
              </p>
              <p
                style={{
                  margin: "0",
                  fontSize: 48,
                  fontWeight: 700,
                  color: colorFor(air.aqi.category),
                }}
              >
                {air.aqi.value}
              </p>
              <p style={{ margin: "0 0 8px", color: colorFor(air.aqi.category), fontWeight: 600 }}>
                {air.aqi.category}
              </p>
              <p className="placeholder">
                {SOURCE_LABELS[air.aqi.source] || air.aqi.source}
              </p>
              <p>
                📡 {air.aqi.station}
                {aqiStation?.distance_km != null ? ` (${aqiStation.distance_km} km away)` : ""}
              </p>
              {air.aqi.timestamp && (
                <p>🕒 Reading time: {new Date(air.aqi.timestamp).toLocaleString()}</p>
              )}
            </>
          ) : (
            <p className="placeholder">No AQI value from a nearby station right now.</p>
          )}

          {air.pollutants.length > 0 && <p style={{ marginTop: 14 }}>🧪 Pollutants:</p>}
          {air.pollutants.map((p) => (
            <p key={p.parameter}>
              {p.parameter.toUpperCase()}: <strong>{p.value} {p.unit}</strong>
              {" · "}
              {p.station_name} ({p.distance_km} km) ·{" "}
              {new Date(p.timestamp).toLocaleString()}
            </p>
          ))}

          {air.warnings.length > 0 && (
            <p className="placeholder">ℹ️ {air.warnings.join(" · ")}</p>
          )}
        </div>
      )}
      {airError && <div className="error-box">⚠️ {airError}</div>}

      {(status === "success" || status === "error") && (
        <button className="btn" onClick={requestLocation}>
          🔄 {status === "success" ? "Refresh location" : "Try again"}
        </button>
      )}
    </div>
  );
}