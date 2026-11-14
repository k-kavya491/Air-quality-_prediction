
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../services/api";

export default function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [hasAsthma, setHasAsthma] = useState(false);
  const [isElderly, setIsElderly] = useState(false);
  const [isChild, setIsChild] = useState(false);

  const [alertEnabled, setAlertEnabled] = useState(true);
  const [notifyPush, setNotifyPush] = useState(true);
  const [notifyEmail, setNotifyEmail] = useState(false);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8 || !/[a-zA-Z]/.test(password) || !/[0-9]/.test(password)) {
      setError("Password must contain at least 8 characters, including a letter and a number.");
      return;
    }

    try {
      setLoading(true);

      await registerUser({
        name,
        email,
        password,
        profile: {
          has_asthma: hasAsthma,
          is_elderly: isElderly,
          is_child: isChild,
          alert_enabled: alertEnabled,
          notify_push: notifyPush,
          notify_email: notifyEmail,
        },
      });

      navigate("/login", {
        state: { message: "Registration successful. Please log in." },
      });
    } catch (err: unknown) {
      if (
        typeof err === "object" &&
        err !== null &&
        "response" in err
      ) {
        const response = (
          err as { response?: { data?: { detail?: string } } }
        ).response;

        setError(response?.data?.detail || "Registration failed. Please try again.");
      } else {
        setError("Unable to connect to the server.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Create your AirSense account</h1>
        <p className="subtitle">
          Register to personalize your air quality alerts.
        </p>

        {error && <p className="error-box">{error}</p>}

        <label>
          Full name
          <input
            className="auth-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            minLength={2}
            maxLength={100}
            required
          />
        </label>

        <label>
          Email
          <input
            className="auth-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            className="auth-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            maxLength={128}
            required
          />
        </label>

        <label>
          Confirm password
          <input
            className="auth-input"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </label>

        <h2>Health sensitivity (optional)</h2>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={hasAsthma}
            onChange={(e) => setHasAsthma(e.target.checked)}
          />
          Asthma sensitivity
        </label>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={isElderly}
            onChange={(e) => setIsElderly(e.target.checked)}
          />
          Elderly sensitivity
        </label>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={isChild}
            onChange={(e) => setIsChild(e.target.checked)}
          />
          Child sensitivity
        </label>

        <h2>Notification preferences</h2>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={alertEnabled}
            onChange={(e) => setAlertEnabled(e.target.checked)}
          />
          Enable AQI alerts
        </label>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={notifyPush}
            onChange={(e) => setNotifyPush(e.target.checked)}
          />
          Push notifications preference
        </label>

        <label className="auth-checkbox">
          <input
            type="checkbox"
            checked={notifyEmail}
            onChange={(e) => setNotifyEmail(e.target.checked)}
          />
          Email notifications preference
        </label>

        <button className="btn auth-submit" type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Register"}
        </button>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}
