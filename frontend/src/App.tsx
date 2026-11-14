
import { useEffect, useState } from "react";
import {
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import { getHealth } from "./services/api";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";

function App() {
  const [status, setStatus] = useState<string>("checking...");

  // Re-render App whenever the route changes.
  useLocation();

  useEffect(() => {
    getHealth()
      .then((res) => setStatus(`connected (${res.data.status})`))
      .catch(() => setStatus("not reachable"));
  }, []);

  // Read the logged-in user's ID.
  const userId = sessionStorage.getItem("airsenseUserId");

  return (
    <Routes>
      {/* Login page */}
      <Route
        path="/login"
        element={<Login />}
      />

      {/* Registration page */}
      <Route
        path="/register"
        element={<Register />}
      />

      {/* Dashboard page */}
      <Route
        path="/"
        element={
          userId ? (
            <div className="app">
              <Header status={status} />
              <Sidebar />

              <main className="main">
                <Dashboard />
              </main>
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* User Profile page */}
      <Route
        path="/profile"
        element={
          userId ? (
            <div className="app">
              <Header status={status} />
              <Sidebar />

              <main className="main">
                <Profile />
              </main>
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* Invalid routes */}
      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

export default App;
