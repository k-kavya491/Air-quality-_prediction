import { useEffect, useState } from "react";
import BarChart from "../components/BarChart";
import CategoryBreakdown from "../components/CategoryBreakdown";
import LocationPanel from "../components/LocationPanel";
import PredictionsTable from "../components/PredictionsTable";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import { getCities, getOverview } from "../services/api";
import { colorFor } from "../utils/aqi";

export default function Dashboard() {
  const [cities, setCities] = useState([]);
  const [city, setCity] = useState("delhi");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    getCities()
      .then((res) => setCities(res.data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getOverview(city)
      .then((res) => {
        if (!cancelled) setData(res.data);
      })
      .catch((err) => {
        if (!cancelled) {
          setData(null);
          setError(err.response?.data?.detail || "Could not load air quality data.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [city, refreshKey]);

  const stats = data?.stats;
  const chartData = (data?.stations || []).slice(0, 12).map((s) => ({
    key: s.uid,
    label: s.name.split(",")[0].slice(0, 14),
    fullLabel: s.name,
    value: s.aqi,
    color: colorFor(s.category),
  }));

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1 id="overview" className="page-title">🌍 Air Quality Dashboard</h1>
          <p className="subtitle">
            Real-time AQI monitoring
            {data ? ` · updated ${new Date(data.updated_at).toLocaleTimeString()}` : ""}
          </p>
        </div>
        <div className="toolbar-controls">
          <select
            className="select"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          >
            {cities.length === 0 && <option value={city}>{city}</option>}
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

      {loading && <p className="status-line">⏳ Loading air quality data...</p>}
      {error && <div className="error-box">⚠️ {error}</div>}
      {data?.is_fallback && (
        <div className="error-box">
          ⚠️ No stations in {data.city_label} are reporting right now. These values
          come from the nearest live station and are not city-wide figures.
        </div>
      )}
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
          icon="🏙️"
          title="Avg City AQI"
          value={stats ? stats.avg_aqi : "—"}
          sub={stats ? stats.avg_category : "waiting for data"}
          accent={stats ? colorFor(stats.avg_category) : "#f97316"}
        />
      </div>

      <div className="charts">
        <SectionCard id="stations" title="AQI Levels by Station (Current Reading)" icon="📊" accent="#38bdf8">
          {chartData.length > 0 ? (
            <BarChart data={chartData} />
          ) : (
            <p className="placeholder">No station readings to show.</p>
          )}
        </SectionCard>

        <SectionCard id="categories" title="AQI Category Breakdown" icon="🎨" accent="#a78bfa">
          {data ? (
            <CategoryBreakdown breakdown={data.category_breakdown} />
          ) : (
            <p className="placeholder">No data yet.</p>
          )}
        </SectionCard>
      </div>

      {data?.warnings?.length > 0 && (
        <p className="status-line">ℹ️ {data.warnings.join(" · ")}</p>
      )}

      <SectionCard id="location" title="Your Location" icon="📍" accent="#f472b6">
        <LocationPanel />
      </SectionCard>

      <div style={{ height: 18 }} />

      <SectionCard id="predictions" title="Recent AQI Predictions vs Actual" icon="🔮" accent="#fbbf24">
        <p className="sample-pill">Sample data. Real predictions appear after the forecasting model is built.</p>
        <PredictionsTable />
      </SectionCard>
    </div>
  );
}