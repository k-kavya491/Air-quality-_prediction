import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 20000,
});

export const getHealth = () => api.get("/health");
export const sendLocation = (payload) => api.post("/location", payload);
export const getCurrentAirQuality = (lat, lon) =>
  api.get("/air-quality/current", { params: { lat, lon } });
export const getCities = () => api.get("/dashboard/cities");
export const getOverview = (city) =>
  api.get("/dashboard/overview", { params: { city } });

export default api;