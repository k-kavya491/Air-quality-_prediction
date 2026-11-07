export default function Header({ status }) {
  return (
    <header className="header">
      <div className="brand">🌿 AirSense</div>
      <div className="header-right">
        <span>🔌 Backend: {status}</span>
        <span className="avatar">👤</span>
      </div>
    </header>
  );
}