

import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  getUser,
  getUserProfile,
  updateUserName,
  updateUserProfile,
  changeUserPassword,
  type HealthProfile,
  type HealthProfilePayload,
} from "../services/api";

export default function Profile() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const [profile, setProfile] = useState<HealthProfile>({
    has_asthma: false,
    is_elderly: false,
    is_child: false,
    alert_threshold: 100,
    alert_enabled: true,
    notify_push: true,
    notify_email: false,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingName, setSavingName] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [nameMessage, setNameMessage] = useState("");
  const [nameError, setNameError] = useState("");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordError, setPasswordError] = useState("");

  useEffect(() => {
    const storedUserId = sessionStorage.getItem("airsenseUserId");

    if (!storedUserId) {
      navigate("/login", { replace: true });
      return;
    }

    const userId = Number(storedUserId);

    if (!Number.isInteger(userId) || userId <= 0) {
      sessionStorage.removeItem("airsenseUserId");
      navigate("/login", { replace: true });
      return;
    }

    async function loadProfile() {
      try {
        const [userResponse, profileResponse] = await Promise.all([
          getUser(userId),
          getUserProfile(userId),
        ]);

        setName(userResponse.data.name);
        setEmail(userResponse.data.email);
        setProfile(profileResponse.data);
      } catch {
        setError("Unable to load your profile. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [navigate]);

  function handleChange(
    field: keyof HealthProfile,
    value: boolean | number,
  ) {
    setProfile((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  async function handleNameSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNameError("");
    setNameMessage("");

    const cleanedName = name.trim();

    if (cleanedName.length < 2 || cleanedName.length > 100) {
      setNameError("Name must contain between 2 and 100 characters.");
      return;
    }

    const storedUserId = sessionStorage.getItem("airsenseUserId");
    const userId = Number(storedUserId);

    if (!storedUserId || !Number.isInteger(userId) || userId <= 0) {
      navigate("/login", { replace: true });
      return;
    }

    try {
      setSavingName(true);

      const response = await updateUserName(userId, cleanedName);

      setName(response.data.name);
      setNameMessage("Your name has been updated successfully.");
    } catch {
      setNameError("Unable to update your name. Please try again.");
    } finally {
      setSavingName(false);
    }
  }

  async function handlePasswordSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setPasswordError("");
    setPasswordMessage("");

    if (newPassword.length < 8 || newPassword.length > 128) {
      setPasswordError("New password must contain 8 to 128 characters.");
      return;
    }

    if (
      !/[a-zA-Z]/.test(newPassword) ||
      !/[0-9]/.test(newPassword)
    ) {
      setPasswordError(
        "New password must contain at least one letter and one number.",
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New password and confirmation do not match.");
      return;
    }

    if (currentPassword === newPassword) {
      setPasswordError(
        "New password must be different from your current password.",
      );
      return;
    }

    const storedUserId = sessionStorage.getItem("airsenseUserId");
    const userId = Number(storedUserId);

    if (!storedUserId || !Number.isInteger(userId) || userId <= 0) {
      navigate("/login", { replace: true });
      return;
    }

    try {
      setSavingPassword(true);

      const response = await changeUserPassword(userId, {
        current_password: currentPassword,
        new_password: newPassword,
      });

      setPasswordMessage(response.data.message);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      const message =
        typeof err === "object" &&
        err !== null &&
        "response" in err &&
        typeof err.response === "object" &&
        err.response !== null &&
        "data" in err.response &&
        typeof err.response.data === "object" &&
        err.response.data !== null &&
        "detail" in err.response.data &&
        typeof err.response.data.detail === "string"
          ? err.response.data.detail
          : "Unable to change password. Please try again.";

      setPasswordError(message);
    } finally {
      setSavingPassword(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const storedUserId = sessionStorage.getItem("airsenseUserId");
    const userId = Number(storedUserId);

    if (!storedUserId || !Number.isInteger(userId) || userId <= 0) {
      navigate("/login", { replace: true });
      return;
    }

    const payload: HealthProfilePayload = {
      has_asthma: profile.has_asthma,
      is_elderly: profile.is_elderly,
      is_child: profile.is_child,
      alert_threshold: profile.alert_threshold,
      alert_enabled: profile.alert_enabled,
      notify_push: profile.notify_push,
      notify_email: profile.notify_email,
    };

    try {
      setSaving(true);

      const response = await updateUserProfile(userId, payload);

      setProfile(response.data);
      setMessage("Your profile has been updated successfully.");
    } catch {
      setError("Unable to save your profile. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="auth-page">Loading your profile...</div>;
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>My Profile</h1>
        <p className="subtitle">
          Manage your account and air-quality alert preferences.
        </p>

        <h2>Account Information</h2>

        <form onSubmit={handleNameSubmit}>
          {nameError && <p className="error-box">{nameError}</p>}
          {nameMessage && <p className="status-line">{nameMessage}</p>}

          <label>
            Name
            <input
              className="auth-input"
              type="text"
              value={name}
              minLength={2}
              maxLength={100}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>

          <label>
            Email
            <input className="auth-input" value={email} readOnly />
          </label>

          <button
            className="btn auth-submit"
            type="submit"
            disabled={savingName}
          >
            {savingName ? "Saving Name..." : "Update Name"}
          </button>
        </form>

        <h2>Change Password</h2>

        <form onSubmit={handlePasswordSubmit}>
          {passwordError && (
            <p className="error-box">{passwordError}</p>
          )}

          {passwordMessage && (
            <p className="status-line">{passwordMessage}</p>
          )}

          <label>
            Current Password
            <input
              className="auth-input"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              maxLength={128}
              autoComplete="current-password"
              required
            />
          </label>

          <label>
            New Password
            <input
              className="auth-input"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              required
            />
          </label>

          <label>
            Confirm New Password
            <input
              className="auth-input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              required
            />
          </label>

          <p className="subtitle">
            Use at least 8 characters, including one letter and one number.
          </p>

          <button
            className="btn auth-submit"
            type="submit"
            disabled={savingPassword}
          >
            {savingPassword ? "Updating Password..." : "Change Password"}
          </button>
        </form>

        <form onSubmit={handleSubmit}>
          {error && <p className="error-box">{error}</p>}
          {message && <p className="status-line">{message}</p>}

          <h2>Health Sensitivity Settings</h2>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.has_asthma}
              onChange={(e) =>
                handleChange("has_asthma", e.target.checked)
              }
            />
            Asthma sensitivity
          </label>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.is_elderly}
              onChange={(e) =>
                handleChange("is_elderly", e.target.checked)
              }
            />
            Elderly person
          </label>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.is_child}
              onChange={(e) =>
                handleChange("is_child", e.target.checked)
              }
            />
            Child
          </label>

          <h2>Alert Settings</h2>

          <label>
            AQI Alert Threshold (50–300)
            <input
              className="auth-input"
              type="number"
              min="50"
              max="300"
              value={profile.alert_threshold}
              onChange={(e) =>
                handleChange("alert_threshold", Number(e.target.value))
              }
              required
            />
          </label>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.alert_enabled}
              onChange={(e) =>
                handleChange("alert_enabled", e.target.checked)
              }
            />
            Enable AQI alerts
          </label>

          <h2>Notification Preferences</h2>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.notify_push}
              onChange={(e) =>
                handleChange("notify_push", e.target.checked)
              }
            />
            Push notifications
          </label>

          <label className="auth-checkbox">
            <input
              type="checkbox"
              checked={profile.notify_email}
              onChange={(e) =>
                handleChange("notify_email", e.target.checked)
              }
            />
            Email notifications
          </label>

          <button
            className="btn auth-submit"
            type="submit"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
