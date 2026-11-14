
import { useNavigate } from "react-router-dom";

interface HeaderProps {
  status: string;
}

export default function Header({ status }: HeaderProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.removeItem("airsenseUserId");
    navigate("/login", { replace: true });
  };

  return (
    <header className="header">
      <div className="brand">🌿 AirSense</div>

      <div className="header-right">
       
        <span className="avatar">👤</span>

        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}


