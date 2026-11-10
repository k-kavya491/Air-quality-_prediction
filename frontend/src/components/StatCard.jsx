export default function StatCard({ title, value, sub, accent, icon }) {
  return (
    <div className="stat-card" style={{ borderTopColor: accent }}>
      <p className="stat-title">
        {icon} {title}
      </p>
      <p className="stat-value" style={{ color: accent }}>
        {value}
      </p>
      <p className="stat-sub">{sub}</p>
    </div>
  );
}