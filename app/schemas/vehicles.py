"""Schemas for vehicle endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class VehicleRegistrationRequest(BaseModel):
    """Request to register a new vehicle."""
    
    vehicle_type: str = Field(..., example="car", description="Type: car, bus, van, minibus")
    license_plate: str = Field(..., example="ABC-123-XY", description="Unique license plate")
    capacity: int = Field(..., ge=1, le=100, example=4, description="Total passenger capacity")
    photo_url: HttpUrl = Field(..., example="https://cdn.example.com/vehicles/abc123.jpg", description="Public URL of the vehicle photo")
    make: Optional[str] = Field(None, example="Toyota")
    model: Optional[str] = Field(None, example="Hiace")
    year: Optional[int] = Field(None, example=2020, ge=1900, le=2030)
    color: Optional[str] = Field(None, example="White")
    amenities: List[str] = Field(default_factory=list, example=["AC", "WiFi", "USB Charging"])


class VehicleUpdateRequest(BaseModel):
    """Request to update vehicle details."""
    
    vehicle_type: Optional[str] = Field(None, example="van")
    capacity: Optional[int] = Field(None, ge=1, le=100, example=6)
    photo_url: Optional[HttpUrl] = Field(None, example="https://cdn.example.com/vehicles/abc123.jpg")
    make: Optional[str] = Field(None, example="Toyota")
    model: Optional[str] = Field(None, example="Hiace")
    year: Optional[int] = Field(None, example=2021, ge=1900, le=2030)
    color: Optional[str] = Field(None, example="Silver")
    amenities: Optional[List[str]] = Field(None, example=["AC", "WiFi"])
    is_active: Optional[bool] = Field(None, example=True)


class VehicleResponse(BaseModel):
    """Vehicle details response."""
    
    id: str
    owner_id: str
    vehicle_type: str
    license_plate: str
    capacity: int
    photo_url: HttpUrl
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleRideRequest(BaseModel):
    """Request to schedule a new ride."""
    
    vehicle_id: str = Field(..., description="ID of the vehicle to use")
    origin: str = Field(..., example="Yaoundé", description="Starting location")
    destination: str = Field(..., example="Douala", description="Destination location")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    estimated_arrival: datetime = Field(..., description="Estimated arrival time")
    available_seats: int = Field(..., ge=1, example=4, description="Number of seats available for booking")
    price_per_seat: float = Field(..., ge=0, example=5000.0, description="Price per seat in local currency")
    amenities: List[str] = Field(default_factory=list, example=["AC", "WiFi"])
    distance_km: Optional[float] = Field(None, example=250.0)
    duration_minutes: Optional[int] = Field(None, example=240)
