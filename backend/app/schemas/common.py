"""Shared Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str = Field(..., example="ok")


class PaginationMeta(BaseModel):
    total: int = Field(..., example=1)
    page: int = Field(..., example=1)
    page_size: int = Field(..., example=10)


class GeoPoint(BaseModel):
    latitude: float = Field(..., example=4.0511)
    longitude: float = Field(..., example=9.7679)
    accuracy_meters: Optional[float] = Field(None, example=15)
    recorded_at: Optional[datetime] = Field(None, example="2025-01-15T10:30:00Z")
