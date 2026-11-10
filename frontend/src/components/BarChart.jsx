export default function BarChart({ data, height = 260 }) {
  const max = Math.max(...data.map((d) => d.value), 100) * 1.15;

  return (
    <div className="bar-chart" style={{ height }}>
      {data.map((d) => (
        <div className="bar-col" key={d.key} title={`${d.fullLabel}: AQI ${d.value}`}>
          <div className="bar-area">
            <span className="bar-value">{d.value}</span>
            <div
              className="bar"
              style={{ height: `${(d.value / max) * 100}%`, background: d.color }}
            />
          </div>
          <span className="bar-label">{d.label}</span>
        </div>
      ))}
    </div>
  );
}