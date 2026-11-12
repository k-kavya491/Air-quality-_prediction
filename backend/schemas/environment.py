from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from schemas.air_quality import AQIInfo, PollutantSummary, Station


class AirQualitySection(BaseModel):
    aqi: Optional[AQIInfo] = None
    pollutants: List[PollutantSummary]
    stations: List[Station]


class WeatherData(BaseModel):
    source: str
    observed_at: datetime
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    wind_gust_ms: Optional[float] = None
    rain_mm: Optional[float] = None
    clouds_pct: Optional[float] = None
    visibility_m: Optional[float] = None
    condition: Optional[str] = None
    description: Optional[str] = None


class TrafficData(BaseModel):
    source: str
    observed_at: datetime
    current_speed_kmh: float
    free_flow_speed_kmh: float
    current_travel_time_s: Optional[float] = None
    free_flow_travel_time_s: Optional[float] = None
    congestion_index: float
    level: str
    confidence: Optional[float] = None
    road_closure: bool
    road_class: Optional[str] = None
    note: str


class EnvironmentResponse(BaseModel):
    latitude: float
    longitude: float
    air_quality: Optional[AirQualitySection] = None
    weather: Optional[WeatherData] = None
    traffic: Optional[TrafficData] = None
    availability: Dict[str, bool]
    max_time_gap_minutes: Optional[float] = None
    warnings: List[str]
    retrieved_at: datetime
    stored_points: Optional[int] = None