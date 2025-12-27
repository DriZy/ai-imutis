"""AI-related endpoints (stubbed implementations)."""
import asyncio
from datetime import datetime, timedelta
from random import random
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..config import get_settings
from ..dependencies import AuthenticatedUser, get_current_user, get_rate_limit_identifier
from ..rate_limit import rate_limiter
from ..schemas.ai import (
    AttractionRecommendation,
    AttractionRecommendationRequest,
    AttractionRecommendationResponse,
    DepartureEstimationRequest,
    DepartureEstimationResponse,
    DepartureWindow,
    TourismSuggestionResponse,
    TouristGuideRequest,
    TouristGuideResponse,
    TrafficPredictionResponse,
    TravelPatternInsight,
    TravelPatternRequest,
    TravelPatternResponse,
)

router = APIRouter(prefix="/api/ai", tags=["AI"])


async def _check_ai_rate(identifier: str) -> None:
    settings = get_settings()
    await rate_limiter.check(
        identifier,
        limit=settings.rate_limit_ai,
        window_seconds=settings.rate_limit_window_seconds,
    )


@router.post("/estimate-departure", response_model=DepartureEstimationResponse)
async def estimate_departure(
    payload: DepartureEstimationRequest,
    identifier: str = Depends(get_rate_limit_identifier),
) -> DepartureEstimationResponse:
    """Predict optimal departure windows (demo values)."""

    await _check_ai_rate(identifier)
    windows = [
        DepartureWindow(window="08:00-09:00", confidence=0.84, recommended=True),
        DepartureWindow(window="11:00-12:00", confidence=0.71, recommended=False),
        DepartureWindow(window="16:00-17:00", confidence=0.65, recommended=False),
    ]
    return DepartureEstimationResponse(route_id=payload.route_id, windows=windows, notes="Demo inference")


@router.get("/traffic-prediction/{route_id}", response_model=TrafficPredictionResponse)
async def traffic_prediction(
    route_id: str,
    identifier: str = Depends(get_rate_limit_identifier),
) -> TrafficPredictionResponse:
    """Return stubbed traffic prediction for a route."""

    await _check_ai_rate(identifier)
    return TrafficPredictionResponse(
        route_id=route_id,
        congestion_score=0.35,
        average_speed_kmh=64.5,
        updated_at=datetime.utcnow(),
    )


@router.post("/recommend-attractions", response_model=AttractionRecommendationResponse)
async def recommend_attractions(
    payload: AttractionRecommendationRequest,
    identifier: str = Depends(get_rate_limit_identifier),
) -> AttractionRecommendationResponse:
    """Return simple ranked recommendations based on provided interests."""

    await _check_ai_rate(identifier)
    base = [
        AttractionRecommendation(
            attraction_id="douala-waterfront",
            name="Douala Waterfront",
            score=0.88,
            reason="Matches interest: waterfront",
        ),
        AttractionRecommendation(
            attraction_id="yaounde-mfoundi",
            name="Mfoundi Market",
            score=0.76,
            reason="Cultural experience",
        ),
    ]
    limited = base[: payload.max_results]
    return AttractionRecommendationResponse(recommendations=limited)


@router.post("/tourist-guide/{attraction_id}", response_model=TouristGuideResponse)
async def tourist_guide(
    attraction_id: str,
    payload: TouristGuideRequest,
    identifier: str = Depends(get_rate_limit_identifier),
) -> TouristGuideResponse:
    """Generate a brief guide for an attraction (demo text)."""

    await _check_ai_rate(identifier)
    guide = (
        f"Explore {attraction_id} with local insights, best visiting hours, and safety tips. "
        f"Language: {payload.language}."
    )
    return TouristGuideResponse(
        attraction_id=attraction_id,
        guide=guide,
        generated_at=datetime.utcnow(),
    )


@router.get("/tourism-suggestions/{city_id}", response_model=TourismSuggestionResponse)
async def tourism_suggestions(
    city_id: str,
    identifier: str = Depends(get_rate_limit_identifier),
) -> TourismSuggestionResponse:
    """Return curated suggestions for a city."""

    await _check_ai_rate(identifier)
    suggestions = [
        "Start at the central market for breakfast",
        "Visit key attractions before noon to avoid heat",
        "Book inter-urban transfers a day in advance",
    ]
    return TourismSuggestionResponse(city_id=city_id, suggestions=suggestions)


@router.post("/analyze-travel-pattern", response_model=TravelPatternResponse)
async def analyze_travel_pattern(
    payload: TravelPatternRequest,
    identifier: str = Depends(get_rate_limit_identifier),
) -> TravelPatternResponse:
    """Return synthetic travel pattern insights."""

    await _check_ai_rate(identifier)
    insights = [
        TravelPatternInsight(trend="increasing", confidence=0.78, commentary="More riders on weekends"),
        TravelPatternInsight(trend="stable", confidence=0.64, commentary="Weekday morning demand steady"),
    ]
    return TravelPatternResponse(
        route_id=payload.route_id,
        insights=insights,
        generated_at=datetime.utcnow(),
    )


@router.websocket("/ws/route/{route_id}/traffic")
async def traffic_ws(websocket: WebSocket, route_id: str) -> None:
    """Send periodic traffic updates over WebSocket."""

    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(10)
            await websocket.send_json(
                {
                    "route_id": route_id,
                    "congestion_score": round(0.2 + random() * 0.5, 2),
                    "average_speed_kmh": round(50 + random() * 20, 1),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        return
