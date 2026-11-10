const links = [
  { href: "#overview", icon: "🏠", label: "Dashboard" },
  { href: "#stations", icon: "📡", label: "Monitor Stations" },
  { href: "#categories", icon: "🎨", label: "AQI Categories" },
  { href: "#predictions", icon: "🔮", label: "Predictions" },
  { href: "#location", icon: "📍", label: "My Location" },
];

export default function Sidebar() {
  return (
    <nav className="sidebar">
      {links.map((link) => (
        <a key={link.href} href={link.href} className="nav-link">
          {link.icon} {link.label}
        </a>
      ))}
    </nav>
  );
}