
import type { ReactNode, CSSProperties } from "react";

interface SectionCardProps {
  id?: string;
  title: string;
  icon?: ReactNode;
  accent?: string;
  children: ReactNode;
}

export default function SectionCard({
  id,
  title,
  icon,
  accent,
  children,
}: SectionCardProps) {
  const accentStyle: CSSProperties | undefined = accent
    ? { borderTopColor: accent }
    : undefined;

  return (
    <section
      id={id}
      className="card"
      style={accentStyle}
    >
      <h2>
        <span className="card-icon">{icon}</span>
        {title}
      </h2>
      <div>{children}</div>
    </section>
  );
}
