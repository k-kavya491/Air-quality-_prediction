export default function SectionCard({ id, title, icon, accent, children }) {
  return (
    <section
      id={id}
      className="card"
      style={accent ? { borderTopColor: accent } : undefined}
    >
      <h2>
        <span className="card-icon">{icon}</span>
        {title}
      </h2>
      <div>{children}</div>
    </section>
  );
}