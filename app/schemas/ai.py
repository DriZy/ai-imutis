"""Schemas for AI endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field



class DepartureEstimationRequest(BaseModel):
    route_id: str = Field(..., example="route-yaounde-douala")
    current_time: datetime = Field(..., example="2025-12-27T08:00:00Z")
    user_preferences: Optional[dict] = Field(None, example={"comfort": "high"})


class DepartureWindow(BaseModel):
    window: str = Field(..., example="08:00-09:00")
    confidence: float = Field(..., ge=0, le=1, example=0.82)
    recommended: bool = False


class DepartureEstimationResponse(BaseModel):
    route_id: str
    windows: List[DepartureWindow]
    notes: Optional[str] = None


class TrafficPredictionResponse(BaseModel):
    route_id: str
    congestion_score: float = Field(..., ge=0, le=1, example=0.35)
    average_speed_kmh: float = Field(..., example=65.0)
    updated_at: datetime


class AttractionRecommendationRequest(BaseModel):
    city_id: str
    interests: List[str] = Field(default_factory=list)
    max_results: int = Field(5, ge=1, le=20)


class AttractionRecommendation(BaseModel):
    attraction_id: str
    name: str
    score: float = Field(..., ge=0, le=1)
    reason: Optional[str] = None


class AttractionRecommendationResponse(BaseModel):
    recommendations: List[AttractionRecommendation]


class TouristGuideRequest(BaseModel):
    language: str = Field("en")
    preferences: Optional[dict] = None


class TouristGuideResponse(BaseModel):
    attraction_id: str
    guide: str
    generated_at: datetime


class TourismSuggestionResponse(BaseModel):
    city_id: str
    suggestions: List[str]


class TravelPatternRequest(BaseModel):
    route_id: str
    recent_trips: int = Field(10, ge=1, le=100)


class TravelPatternInsight(BaseModel):
    trend: str = Field(..., example="increasing")
    confidence: float = Field(..., ge=0, le=1)
    commentary: str


class TravelPatternResponse(BaseModel):
    route_id: str
    insights: List[TravelPatternInsight]
    generated_at: datetime
