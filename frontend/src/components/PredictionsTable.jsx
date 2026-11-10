import { categoryFor, colorFor } from "../utils/aqi";

// Sample rows only. Real predictions come after the forecasting model is built.
const SAMPLE_ROWS = [
  { station: "Sample station 1", city: "Sample city", predicted: 278, actual: 284, pollutant: "PM2.5" },
  { station: "Sample station 2", city: "Sample city", predicted: 122, actual: 118, pollutant: "PM10" },
  { station: "Sample station 3", city: "Sample city", predicted: 89, actual: 96, pollutant: "NO2" },
  { station: "Sample station 4", city: "Sample city", predicted: 204, actual: 187, pollutant: "O3" },
  { station: "Sample station 5", city: "Sample city", predicted: 71, actual: 74, pollutant: "CO" },
];

export default function PredictionsTable() {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Station</th>
            <th>City</th>
            <th>Predicted AQI</th>
            <th>Actual AQI</th>
            <th>Pollutant</th>
            <th>Category</th>
            <th>Accuracy</th>
          </tr>
        </thead>
        <tbody>
          {SAMPLE_ROWS.map((r) => {
            const category = categoryFor(r.actual);
            const accuracy = Math.max(
              0,
              Math.round(100 - (Math.abs(r.predicted - r.actual) / r.actual) * 100)
            );
            return (
              <tr key={r.station}>
                <td>{r.station}</td>
                <td>{r.city}</td>
                <td>{r.predicted}</td>
                <td>{r.actual}</td>
                <td>{r.pollutant}</td>
                <td>
                  <span className="badge" style={{ background: colorFor(category) }}>
                    {category}
                  </span>
                </td>
                <td>
                  <span className="badge" style={{ background: "#16a34a" }}>
                    {accuracy}%
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}