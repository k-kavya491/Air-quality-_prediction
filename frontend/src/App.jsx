import { useEffect, useState } from "react";
import { getHealth } from "./services/api";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    getHealth()
      .then((res) => setStatus(`connected (${res.data.status})`))
      .catch(() => setStatus("not reachable"));
  }, []);

  return (
    <div className="app">
      <Header status={status} />
      <Sidebar />
      <main className="main">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
