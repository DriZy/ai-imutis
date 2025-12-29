"""Schemas for travel endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .common import GeoPoint


class TravelSummary(BaseModel):
    id: str = Field(..., example="route-yaounde-douala")
    origin: str = Field(..., example="Yaounde")
    destination: str = Field(..., example="Douala")
    departure_time: datetime = Field(..., example="2025-12-27T08:30:00Z")
    estimated_arrival: datetime = Field(..., example="2025-12-27T12:00:00Z")
    available_seats: int = Field(..., ge=0, example=15)
    price_per_seat: float = Field(..., example=5000.0)
    confidence: float = Field(..., ge=0, le=1, example=0.87)


class TravelDetail(TravelSummary):
    route_geometry: Optional[str] = Field(None, description="LINESTRING or encoded polyline")
    distance_km: Optional[float] = Field(None, example=230.5)
    duration_minutes: Optional[int] = Field(None, example=210)
    amenities: List[str] = Field(default_factory=list, example=["AC", "WiFi"])


class TravelEstimateRequest(BaseModel):
    route_id: str = Field(..., example="route-yaounde-douala")
    departure_date: datetime = Field(..., description="Proposed departure date/time")
    passengers: int = Field(1, ge=1, le=20)
    user_preferences: Optional[dict] = Field(None, example={"comfort": "high", "cost": "low"})


class DepartureWindow(BaseModel):
    label: str = Field(..., example="08:00-09:00")
    confidence: float = Field(..., ge=0, le=1, example=0.82)
    recommended: bool = Field(False)


class TravelEstimateResponse(BaseModel):
    route_id: str
    windows: List[DepartureWindow]
    notes: Optional[str] = None


class TravelBookingRequest(BaseModel):
    route_id: str = Field(...)
    passengers: int = Field(1, ge=1, le=20)
    payment_method: str = Field(..., example="card")
    special_requests: Optional[str] = Field(None, max_length=280)


class TravelBookingResponse(BaseModel):
    booking_id: str
    status: str = Field(..., example="confirmed")
    departure_time: datetime
    estimated_arrival: datetime


class TravelSearchRequest(BaseModel):
    origin: str = Field(..., example="douala")
    destination: str = Field(..., example="yaounde")
    departure_date: datetime
    passengers: int = Field(1, ge=1, le=20)


class TravelSearchResponse(BaseModel):
    results: List[TravelSummary]
