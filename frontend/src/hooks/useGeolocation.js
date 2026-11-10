import { useCallback, useState } from "react";
import { sendLocation } from "../services/api";

const MESSAGES = {
  insecure:
    "Location access only works on a secure (HTTPS) page or on localhost.",
  unsupported:
    "Your browser does not support location access. Try a current version of Chrome, Edge, Firefox or Safari.",
  denied:
    "Location permission was denied. Allow location access for this site in your browser's address bar settings, then try again.",
  unavailable:
    "Your location could not be determined. Check that location services are turned on for your device.",
  timeout:
    "Finding your location took too long. Check your connection or signal and try again.",
  invalid: "Your device returned an invalid location. Please try again.",
  server:
    "Your location was found, but it could not be sent to the server. Check that the backend is running.",
};

function validCoords(lat, lon) {
  return (
    Number.isFinite(lat) &&
    Number.isFinite(lon) &&
    Math.abs(lat) <= 90 &&
    Math.abs(lon) <= 180 &&
    !(lat === 0 && lon === 0)
  );
}

export default function useGeolocation() {
  const [state, setState] = useState({ status: "idle", location: null, error: null });

  const fail = (type, location = null) =>
    setState({
      status: "error",
      location,
      error: { type, message: MESSAGES[type] },
    });

  const requestLocation = useCallback(() => {
    if (!window.isSecureContext) return fail("insecure");
    if (!("geolocation" in navigator)) return fail("unsupported");

    setState({ status: "requesting", location: null, error: null });

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude, accuracy } = pos.coords;
        if (!validCoords(latitude, longitude)) return fail("invalid");

        const local = {
          latitude,
          longitude,
          accuracy_m: accuracy,
          captured_at: new Date(pos.timestamp).toISOString(),
        };
        try {
          const res = await sendLocation({
            latitude,
            longitude,
            accuracy_m: accuracy,
            source: "browser",
          });
          setState({ status: "success", location: res.data, error: null });
        } catch {
          fail("server", local);
        }
      },
      (err) => {
        if (err.code === 1) fail("denied");
        else if (err.code === 3) fail("timeout");
        else fail("unavailable");
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
    );
  }, []);

  return { ...state, requestLocation };
}