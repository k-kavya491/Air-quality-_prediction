

import axios from "axios";

interface LocationPayload {
  latitude?: number;
  longitude?: number;
  [key: string]: unknown;
}

export interface City {
  key: string;
  label: string;
  latitude: number;
  longitude: number;
}

export interface WeatherData {
  temperature_c?: number | null;
  feels_like_c?: number | null;
  humidity_percent?: number | null;
  pressure_hpa?: number | null;
  wind_speed_mps?: number | null;
  condition?: string;
  source?: string;
  rainfall_mm?: number | null;
rainfall_period?: string | null;
}


export interface TrafficData {
  current_speed_kmh?: number | null;
  free_flow_speed_kmh?: number | null;
  current_travel_time_seconds?: number | null;
  free_flow_travel_time_seconds?: number | null;
  confidence?: number | null;
  road_closed?: boolean;
  source?: string;
}
export interface PollutantMeasurement {
  parameter: string;
  value: number | null;
  unit: string;
  timestamp?: string | null;
  source?: string;
}

export interface EnvironmentalAirQuality {
  aqi?: {
    value: number | null;
    category?: string;
    dominant_pollutant?: string;
    source?: string;
  } | null;
  pollutants?: PollutantMeasurement[];
}

export interface EnvironmentalData {
  location: {
    latitude: number;
    longitude: number;
  };
  weather: WeatherData | null;
  traffic: TrafficData | null;
  sources_available: {
    air_quality: boolean;
    weather: boolean;
    traffic: boolean;
  };
  warnings: string[];
  retrieved_at: string;
  air_quality?: EnvironmentalAirQuality | null;
}

// User and profile types

export interface HealthProfile {
  has_asthma: boolean;
  is_elderly: boolean;
  is_child: boolean;
  alert_threshold: number;
  alert_enabled: boolean;
  notify_push: boolean;
  notify_email: boolean;
}

export interface HealthProfilePayload {
  has_asthma: boolean;
  is_elderly: boolean;
  is_child: boolean;
  alert_threshold?: number | null;
  alert_enabled: boolean;
  notify_push: boolean;
  notify_email: boolean;
}

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
  profile: HealthProfile;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  profile?: HealthProfilePayload;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 60000,
});

// Existing API functions

export const getHealth = () =>
  api.get<{ status: string }>("/health");

export const sendLocation = (payload: LocationPayload) =>
  api.post("/location", payload);

export const getCurrentAirQuality = (lat: number, lon: number) =>
  api.get("/air-quality/current", { params: { lat, lon } });

export const getCities = () =>
  api.get<City[]>("/dashboard/cities");

export const getOverview = (city: string) =>
  api.get("/dashboard/overview", { params: { city } });

export const getCurrentEnvironmentalData = (lat: number, lon: number) =>
  api.get<EnvironmentalData>("/environmental/current", {
    params: { lat, lon },
  });

// User API functions

export const registerUser = (payload: RegisterPayload) =>
  api.post<User>("/users/register", payload);

export const loginUser = (payload: LoginPayload) =>
  api.post<User>("/users/login", payload);

export const getUser = (userId: number) =>
  api.get<User>(`/users/${userId}`);

export const updateUserName = (
  userId: number,
  name: string,
) =>
  api.put<User>(`/users/${userId}`, { name });

export const changeUserPassword = (
  userId: number,
  payload: PasswordChangePayload,
) =>
  api.put<{ message: string }>(
    `/users/${userId}/password`,
    payload,
  );

export const getUserProfile = (userId: number) =>
  api.get<HealthProfile>(`/users/${userId}/profile`);

export const updateUserProfile = (
  userId: number,
  payload: HealthProfilePayload,
) =>
  api.put<HealthProfile>(`/users/${userId}/profile`, payload);

export default api;
