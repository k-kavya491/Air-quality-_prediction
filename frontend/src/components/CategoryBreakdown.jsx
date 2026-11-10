import { CATEGORIES } from "../utils/aqi";

export default function CategoryBreakdown({ breakdown }) {
  const counts = Object.fromEntries(breakdown.map((b) => [b.category, b.count]));

  return (
    <div>
      {CATEGORIES.map((c) => (
        <div className="legend-row" key={c.name}>
          <div className="legend-left">
            <span className="dot" style={{ background: c.color }} />
            <div>
              <div>{c.name}</div>
              <div className="legend-range">AQI {c.range}</div>
            </div>
          </div>
          <strong>{counts[c.name] ?? 0}</strong>
        </div>
      ))}
    </div>
  );
}