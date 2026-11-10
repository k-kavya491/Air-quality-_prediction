from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StationAQI(BaseModel):
    uid: str
    name: str
    aqi: int
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_updated: datetime


class CategoryCount(BaseModel):
    category: str
    count: int


class DashboardStats(BaseModel):
    active_stations: int
    alerts_now: int
    severe_now: int
    alert_threshold: int
    avg_aqi: int
    avg_category: str


class DashboardOverview(BaseModel):
    city: str
    city_label: str
    stats: DashboardStats
    stations: List[StationAQI]
    category_breakdown: List[CategoryCount]
    warnings: List[str]
    is_fallback: bool = False
    updated_at: datetime