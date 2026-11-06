import { useEffect, useState } from "react";
import { getHealth } from "./services/api";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    getHealth()
      .then((res) => setStatus(`Connected (${res.data.status})`))
      .catch(() => setStatus("Backend not reachable"));
  }, []);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>AirSense</h1>
      <p>AI-Powered Air Quality Prediction and Smart Mobility</p>
      <p>
        Backend status: <strong>{status}</strong>
      </p>
    </div>
  );
}

export default App;