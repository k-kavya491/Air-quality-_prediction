from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Measurement(BaseModel):
    parameter: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    source: str


class PollutantSummary(Measurement):
    station_id: str
    station_name: str
    distance_km: float


class Station(BaseModel):
    id: str
    name: str
    source: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    provider: Optional[str] = None
    last_updated: Optional[datetime] = None
    measurements: List[Measurement]


class AQIInfo(BaseModel):
    value: int
    category: str
    dominant_pollutant: Optional[str] = None
    source: str
    station: Optional[str] = None
    timestamp: Optional[datetime] = None


class AirQualityResponse(BaseModel):
    latitude: float
    longitude: float
    aqi: Optional[AQIInfo] = None
    pollutants: List[PollutantSummary]
    pollutant_indices: Dict[str, float]
    stations: List[Station]
    warnings: List[str]
    retrieved_at: datetime