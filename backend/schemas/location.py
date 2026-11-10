from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class Coordinates(BaseModel):
    """Shared coordinate structure for all modules."""

    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)

    @model_validator(mode="after")
    def reject_null_island(self):
        # 0,0 is almost always a device error, not a real position
        if self.latitude == 0 and self.longitude == 0:
            raise ValueError("Coordinates 0,0 are not a valid location")
        return self


class LocationIn(Coordinates):
    accuracy_m: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    user_id: Optional[int] = Field(default=None, ge=1)
    source: Literal["browser", "manual"] = "browser"
    captured_at: Optional[datetime] = None


class LocationOut(Coordinates):
    accuracy_m: Optional[float] = None
    user_id: Optional[int] = None
    source: str = "browser"
    captured_at: datetime
    stored: bool = False