"""Schemas for user management and tracking."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .common import GeoPoint, MessageResponse


class UserProfile(BaseModel):
    uid: str = Field(..., example="user-123")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, example="+237670000000")
    display_name: Optional[str] = Field(None, example="Jane Doe")
    language: Optional[str] = Field("en")
    notification_enabled: bool = Field(True)
    role: str = Field("standard")


class UpdateUserProfileRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=120)
    language: Optional[str] = Field(None)
    notification_enabled: Optional[bool] = None


class UserPreferenceRequest(BaseModel):
    language: Optional[str] = Field(None)
    marketing_opt_in: Optional[bool] = None
    travel_notifications: Optional[bool] = None
    security_alerts: Optional[bool] = None


class DeviceSession(BaseModel):
    session_id: str
    device_ip: str
    device_type: Optional[str] = None
    device_os: Optional[str] = None
    session_start: datetime
    last_activity: datetime
    is_active: bool = True
    ip_rotation_detected: bool = False


class DeviceSessionList(BaseModel):
    sessions: List[DeviceSession]


class LocationTrackRequest(BaseModel):
    latitude: float = Field(..., example=4.0511)
    longitude: float = Field(..., example=9.7679)
    accuracy_meters: Optional[float] = Field(None, example=15)
    activity_type: Optional[str] = Field(None, example="traveling")


class LocationTrackResponse(BaseModel):
    location_id: str
    device_ip: str
    recorded_at: datetime


class VerifyTokenResponse(BaseModel):
    uid: str
    role: str
    status: str = Field("valid")
