const links = [
  { href: "#overview", icon: "🏠", label: "Dashboard" },
  { href: "#location", icon: "📍", label: "Current Location" },
  { href: "#air-quality", icon: "💨", label: "Air Quality" },
  { href: "#weather", icon: "🌤️", label: "Weather" },
  { href: "#analytics", icon: "📊", label: "Analytics" },
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