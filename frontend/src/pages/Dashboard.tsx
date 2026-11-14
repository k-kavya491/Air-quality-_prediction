

import { useEffect, useState } from "react";
import BarChart from "../components/BarChart";
import CategoryBreakdown from "../components/CategoryBreakdown";
import LocationPanel from "../components/LocationPanel";
import PredictionsTable from "../components/PredictionsTable";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";

import {
  getCities,
  getOverview,
  getCurrentEnvironmentalData,
} from "../services/api";

import type {
  City,
  EnvironmentalData,
} from "../services/api";

import { colorFor } from "../utils/aqi";

interface Station {
  uid: string;
  name: string;
  aqi: number;
  category: string;
}

interface DashboardStats {
  active_stations: number;
  alerts_now: number;
  alert_threshold: number;
  severe_now: number;
  avg_aqi: number;
  avg_category: string;
}

interface CategoryBreakdownItem {
  category: string;
  count: number;
}

interface DashboardData {
  city_label: string;
  updated_at: string;
  is_fallback: boolean;
  stats: DashboardStats;
  stations: Station[];
  category_breakdown: CategoryBreakdownItem[];
  warnings?: string[];
}

function getErrorMessage(err: unknown): string {
  if (typeof err === "object" && err !== null) {
    if ("response" in err) {
      const response = (
        err as {
          response?: { data?: { detail?: string } };
        }
      ).response;

      if (response?.data?.detail) {
        return response.data.detail;
      }
    }

    if (err instanceof Error) {
      return err.message;
    }
  }

  return "Could not load weather and traffic data.";
}

export default function Dashboard() {
  const [cities, setCities] = useState<City[]>([]);
  const [city, setCity] = useState("delhi");

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [environmentData, setEnvironmentData] =
    useState<EnvironmentalData | null>(null);

  const [environmentLoading, setEnvironmentLoading] = useState(false);
  const [environmentError, setEnvironmentError] =
    useState<string | null>(null);

  const [refreshKey, setRefreshKey] = useState(0);

  // Load available cities
  useEffect(() => {
    let cancelled = false;

    getCities()
      .then((res) => {
        if (!cancelled) {
          setCities(res.data);
        }
      })
      .catch((err: unknown) => {
        console.error("Could not load cities:", err);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load dashboard AQI data
  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    getOverview(city)
      .then((res) => {
        if (!cancelled) {
          setData(res.data as DashboardData);
        }
      })
      .catch((err: unknown) => {
        console.error("AQI request error:", err);

        if (!cancelled) {
          setData(null);
          setError(getErrorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [city, refreshKey]);

  // Find selected city coordinates
  const selectedCity = cities.find(
    (item) => item.key === city
  );

  const selectedLatitude = selectedCity?.latitude;
  const selectedLongitude = selectedCity?.longitude;

  // Load weather and traffic for selected city
  useEffect(() => {
    if (
      selectedLatitude == null ||
      selectedLongitude == null
    ) {
      setEnvironmentData(null);
      setEnvironmentLoading(false);
      return;
    }

    let cancelled = false;

    setEnvironmentLoading(true);
    setEnvironmentError(null);

    getCurrentEnvironmentalData(
      selectedLatitude,
      selectedLongitude
    )
      .then((res) => {
        console.log("Environmental response:", res.data);

        if (!cancelled) {
          setEnvironmentData(res.data);
          setEnvironmentError(null);
        }
      })
      .catch((err: unknown) => {
        console.error("Environmental request failed:", err);

        if (!cancelled) {
          setEnvironmentData(null);
          setEnvironmentError(getErrorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setEnvironmentLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedLatitude, selectedLongitude, refreshKey]);

  const stats = data?.stats;
  const weather = environmentData?.weather;
  const traffic = environmentData?.traffic;

  // Prepare station chart data
  const chartData = (data?.stations || [])
    .slice(0, 12)
    .map((s) => ({
      key: s.uid,
      label: s.name.split(",")[0].slice(0, 14),
      fullLabel: s.name,
      value: s.aqi,
      color: colorFor(s.category),
    }));

  return (
    <div>
      {/* Dashboard Header */}
      <div className="toolbar">
        <div>
          <h1 id="overview" className="page-title">
            🌍 Air Quality Dashboard
          </h1>

          <p className="subtitle">
            Real-time AQI monitoring
            {data
              ? ` · updated ${new Date(
                  data.updated_at
                ).toLocaleTimeString()}`
              : ""}
          </p>
        </div>

        <div className="toolbar-controls">
          <select
            className="select"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          >
            {cities.length === 0 && (
              <option value={city}>{city}</option>
            )}

            {cities.map((c) => (
              <option key={c.key} value={c.key}>
                {c.label}
              </option>
            ))}
          </select>

          <button
            className="btn btn-ghost"
            onClick={() => setRefreshKey((k) => k + 1)}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* AQI Loading and Errors */}
      {loading && (
        <p className="status-line">
          Loading air quality data...
        </p>
      )}

      {error && (
        <div className="error-box">
          ⚠️ {error}
        </div>
      )}

      {data?.is_fallback && (
        <div className="error-box">
          ⚠️ No stations in {data.city_label} are reporting right now.
          These values come from the nearest live station and are not
          city-wide figures.
        </div>
      )}

      {/* AQI Statistics */}
      <div className="stats">
        <StatCard
          icon="📡"
          title="Active Stations"
          value={stats ? stats.active_stations : "—"}
          sub={
            data
              ? data.is_fallback
                ? "nearest live station, not in this city"
                : `in ${data.city_label}`
              : "waiting for data"
          }
          accent="#38bdf8"
        />

        <StatCard
          icon="🚨"
          title="AQI Alerts"
          value={stats ? stats.alerts_now : "—"}
          sub={
            stats
              ? `stations above AQI ${stats.alert_threshold} now · ${stats.severe_now} very unhealthy or worse`
              : "waiting for data"
          }
          accent="#ef4444"
        />

        <StatCard
          icon="🎯"
          title="Forecast Accuracy"
          value="—"
          sub="Available after the forecasting model is trained"
          accent="#22c55e"
        />

        <StatCard
          icon="🙂"
          title="Avg City AQI"
          value={stats ? stats.avg_aqi : "—"}
          sub={stats ? stats.avg_category : "waiting for data"}
          accent={stats ? colorFor(stats.avg_category) : "#f97316"}
        />
      </div>

      {/* AQI Charts */}
      <div className="charts">
        <SectionCard
          id="stations"
          title="AQI Levels by Station (Current Reading)"
          icon="📊"
          accent="#38bdf8"
        >
          {chartData.length > 0 ? (
            <BarChart data={chartData} />
          ) : (
            <p className="placeholder">
              No station readings to show.
            </p>
          )}
        </SectionCard>

        <SectionCard
          id="categories"
          title="AQI Category Breakdown"
          icon="🎨"
          accent="#a78bfa"
        >
          {data ? (
            <CategoryBreakdown
              breakdown={data.category_breakdown}
            />
          ) : (
            <p className="placeholder">No data yet.</p>
          )}
        </SectionCard>
      </div>

      {/* AQI Warnings */}
      {data?.warnings && data.warnings.length > 0 && (
        <p className="status-line">
          ℹ️ {data.warnings.join(" · ")}
        </p>
      )}

      
{/* Weather Information */}
<SectionCard
  id="weather"
  title="Current Weather"
  icon="🌤️"
  accent="#38bdf8"
>
  <p className="subtitle">
    Conditions near the selected city center
  </p>

  {environmentLoading && (
    <p className="placeholder">
      Loading weather data...
    </p>
  )}

  {environmentError && (
    <p className="error-box">{environmentError}</p>
  )}

  {!environmentLoading && weather && (
    <div className="stats">
      <StatCard
        icon="🌡️"
        title="Temperature"
        value={
          weather.temperature_c != null
            ? `${weather.temperature_c} °C`
            : "N/A"
        }
        sub={weather.condition || "Current temperature"}
        accent="#f97316"
      />

      <StatCard
        icon="💧"
        title="Humidity"
        value={
          weather.humidity_percent != null
            ? `${weather.humidity_percent}%`
            : "N/A"
        }
        sub="Relative humidity"
        accent="#38bdf8"
      />

      <StatCard
        icon="💨"
        title="Wind Speed"
        value={
          weather.wind_speed_mps != null
            ? `${weather.wind_speed_mps} m/s`
            : "N/A"
        }
        sub="Current wind speed"
        accent="#a78bfa"
      />

      <StatCard
        icon="🌡️"
        title="Feels Like"
        value={
          weather.feels_like_c != null
            ? `${weather.feels_like_c} °C`
            : "N/A"
        }
        sub="Feels-like temperature"
        accent="#22c55e"
      />

      <StatCard
        icon="🌧️"
        title="Rainfall"
        value={
          weather.rainfall_mm != null
            ? `${weather.rainfall_mm} mm`
            : "N/A"
        }
        sub={
          weather.rainfall_period
            ? `Rainfall period: ${weather.rainfall_period}`
            : "Rainfall measurement"
        }
        accent="#60a5fa"
      />
    </div>
  )}

  {!environmentLoading &&
    !weather &&
    !environmentError && (
      <p className="placeholder">
        Weather data is currently unavailable.
      </p>
    )}

  {weather?.source && (
    <p className="status-line">
      Source: {weather.source}
    </p>
  )}
</SectionCard>

{/* Pollutant Measurements */}
<SectionCard
  id="pollutants"
  title="Pollutant Measurements"
  icon="🧪"
  accent="#a78bfa"
>
  <p className="subtitle">
    Latest available pollutant concentrations near the selected city
  </p>

  {environmentLoading && (
    <p className="placeholder">
      Loading pollutant data...
    </p>
  )}

  {environmentError && (
    <p className="error-box">{environmentError}</p>
  )}

  {!environmentLoading && !environmentError && (
    <>
      <div className="stats">
        {[
          { key: "pm25", title: "PM2.5", accent: "#f97316" },
          { key: "pm10", title: "PM10", accent: "#eab308" },
          { key: "no2", title: "NO₂", accent: "#38bdf8" },
          { key: "o3", title: "O₃", accent: "#a78bfa" },
          { key: "co", title: "CO", accent: "#22c55e" },
        ].map((item) => {
          const pollutant =
            environmentData?.air_quality?.pollutants?.find(
              (p) => p.parameter.toLowerCase() === item.key
            );

          const unit = pollutant?.unit
            ?.replace(/Âµ/g, "µ")
            .replace(/Â³/g, "³");

          return (
            <StatCard
              key={item.key}
              icon="🧪"
              title={item.title}
              value={
                pollutant?.value != null
                  ? `${pollutant.value} ${unit || ""}`.trim()
                  : "N/A"
              }
              sub={
                pollutant?.source
                  ? `Source: ${pollutant.source}`
                  : "Measurement unavailable"
              }
              accent={item.accent}
            />
          );
        })}
      </div>
    </>
  )}
</SectionCard>


      {/* Traffic Information */}
      <SectionCard
        id="traffic"
        title="Current Traffic"
        icon="🚦"
        accent="#fbbf24"
      >
        <p className="subtitle">
          Traffic conditions near the selected city center
        </p>

        {environmentLoading && (
          <p className="placeholder">
            Loading traffic data...
          </p>
        )}

        {environmentError && (
          <p className="error-box">
            {environmentError}
          </p>
        )}

        {!environmentLoading && traffic && (
          <div className="stats">
            <StatCard
              icon="🚗"
              title="Current Speed"
              value={
                traffic.current_speed_kmh != null
                  ? `${traffic.current_speed_kmh} km/h`
                  : "—"
              }
              sub="Current road speed"
              accent="#38bdf8"
            />

            <StatCard
              icon="🛣️"
              title="Free Flow Speed"
              value={
                traffic.free_flow_speed_kmh != null
                  ? `${traffic.free_flow_speed_kmh} km/h`
                  : "—"
              }
              sub="Speed without congestion"
              accent="#22c55e"
            />

            <StatCard
              icon="⏱️"
              title="Travel Time"
              value={
                traffic.current_travel_time_seconds != null
                  ? `${Math.round(
                      traffic.current_travel_time_seconds / 60
                    )} min`
                  : "—"
              }
              sub="Current estimated travel time"
              accent="#f97316"
            />

            <StatCard
              icon="🚧"
              title="Road Status"
              value={
                traffic.road_closed === true
                  ? "Closed"
                  : traffic.road_closed === false
                    ? "Open"
                    : "Unknown"
              }
              sub="Reported road condition"
              accent="#a78bfa"
            />
          </div>
        )}

        {!environmentLoading &&
          !traffic &&
          !environmentError && (
            <p className="placeholder">
              Traffic data is currently unavailable.
            </p>
          )}

        {traffic?.source && (
          <p className="status-line">
            Source: {traffic.source}
          </p>
        )}
      </SectionCard>

      {/* Combined Environmental Warnings */}
      {environmentData?.warnings &&
        environmentData.warnings.length > 0 && (
          <p className="status-line">
            ℹ️ {environmentData.warnings.join(" · ")}
          </p>
        )}

      {/* User Location */}
      <SectionCard
        id="location"
        title="Your Location"
        icon="📍"
        accent="#f472b6"
      >
        <LocationPanel />
      </SectionCard>

      <div style={{ height: 18 }} />

      {/* AQI Predictions */}
      <SectionCard
        id="predictions"
        title="AQI Forecasting"
        icon="🔮"
        accent="#fbbf24"
      >
        <p className="status-line">
          Forecasting model integration is pending.
        </p>

        <PredictionsTable />
      </SectionCard>
    </div>
  );
}
