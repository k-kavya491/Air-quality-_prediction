
import type { ReactNode, CSSProperties } from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  sub: string;
  accent: string;
  icon?: ReactNode;
}

export default function StatCard({
  title,
  value,
  sub,
  accent,
  icon,
}: StatCardProps) {
  const cardStyle: CSSProperties = {
    borderTopColor: accent,
  };

  const valueStyle: CSSProperties = {
    color: accent,
  };

  return (
    <div className="stat-card" style={cardStyle}>
      <p className="stat-title">
        {icon} {title}
      </p>
      <p className="stat-value" style={valueStyle}>
        {value}
      </p>
      <p className="stat-sub">{sub}</p>
    </div>
  );
}
