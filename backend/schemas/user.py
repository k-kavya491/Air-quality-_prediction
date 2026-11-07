from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class HealthProfileIn(BaseModel):
    has_asthma: bool = False
    is_elderly: bool = False
    is_child: bool = False
    alert_threshold: Optional[int] = Field(default=None, ge=50, le=300)
    alert_enabled: bool = True
    notify_push: bool = True
    notify_email: bool = False


class HealthProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    has_asthma: bool
    is_elderly: bool
    is_child: bool
    alert_threshold: int
    alert_enabled: bool
    notify_push: bool
    notify_email: bool


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    profile: HealthProfileIn = Field(default_factory=HealthProfileIn)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must have at least 2 characters")
        return v

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one number")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime
    profile: HealthProfileOut