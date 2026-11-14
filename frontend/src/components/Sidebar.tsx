

import { Link } from "react-router-dom";

interface SidebarLink {
  href: string;
  icon: string;
  label: string;
}

const links: SidebarLink[] = [
  { href: "#stations", icon: "📡", label: "Monitor Stations" },
  { href: "#categories", icon: "🎨", label: "AQI Categories" },
  { href: "#predictions", icon: "🔮", label: "Predictions" },
  { href: "#location", icon: "📍", label: "My Location" },
];

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <Link to="/" className="nav-link">
        📊 Dashboard
      </Link>

      {links.map((link) => (
        <a key={link.href} href={link.href} className="nav-link">
          {link.icon} {link.label}
        </a>
      ))}

      <Link to="/profile" className="nav-link">
        👤 My Profile
      </Link>
    </nav>
  );
}
