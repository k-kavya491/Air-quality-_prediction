import SectionCard from "../components/SectionCard";

export default function Dashboard() {
  return (
    <div>
      <h1 id="overview" className="page-title">🌍 Dashboard</h1>
      <p className="subtitle">Air quality and weather for your location</p>

      <div className="grid">
        <SectionCard id="location" title="Current Location" icon="📍" accent="#f472b6">
          <p className="placeholder">Location not shared yet.</p>
        </SectionCard>

        <SectionCard id="air-quality" title="Air Quality" icon="💨" accent="#34d399">
          <p className="placeholder">AQI information will appear here.</p>
        </SectionCard>

        <SectionCard id="weather" title="Weather" icon="🌤️" accent="#fbbf24">
          <p className="placeholder">Weather information will appear here.</p>
        </SectionCard>
      </div>

      <SectionCard
        id="analytics"
        title="Environmental Analytics"
        icon="📊"
        accent="#a78bfa"
      >
        <p className="placeholder">Forecasts and trends will appear here.</p>
      </SectionCard>
    </div>
  );
}