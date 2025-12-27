"""Schemas for tourism-related endpoints."""
from typing import List, Optional

from pydantic import BaseModel, Field

from .common import GeoPoint


class City(BaseModel):
    id: str = Field(..., example="douala")
    name: str = Field(..., example="Douala")
    country: str = Field("Cameroon")
    description: Optional[str] = Field(None, example="Economic capital of Cameroon")
    population: Optional[int] = Field(None, example=2000000)


class Attraction(BaseModel):
    id: str = Field(..., example="douala-waterfront")
    city_id: str = Field(..., example="douala")
    name: str = Field(..., example="Douala Waterfront")
    description: Optional[str] = None
    category: Optional[str] = Field(None, example="nature")
    rating: Optional[float] = Field(None, ge=0, le=5, example=4.6)
    opening_hours: Optional[str] = Field(None, example="08:00-18:00")
    entry_fee: Optional[str] = Field(None, example="2000 XAF")
    location: Optional[GeoPoint] = None
    tags: List[str] = Field(default_factory=list)


class AttractionSearchRequest(BaseModel):
    query: str = Field(..., example="museum")
    city_id: Optional[str] = Field(None, example="yaounde")
    category: Optional[str] = Field(None, example="culture")
    min_rating: float = Field(0, ge=0, le=5)


class AttractionSearchResponse(BaseModel):
    results: List[Attraction]
