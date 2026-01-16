"""AI-related endpoints (data-backed heuristics)."""
import asyncio
from datetime import datetime, timedelta
from random import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..dependencies import AuthenticatedUser, get_current_user, get_rate_limit_identifier
from ..models import Attraction, TravelRoute
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
    db: AsyncSession = Depends(get_db),
) -> DepartureEstimationResponse:
    """Predict optimal departure windows using route schedule and duration."""

    await _check_ai_rate(identifier)
    route = await db.get(TravelRoute, payload.route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    base_start = route.departure_time.replace(second=0, microsecond=0)
    duration = route.duration_minutes or 0
    buffer = 15 if duration and duration > 180 else 10

    windows = [
        DepartureWindow(
            window=f"{(base_start - timedelta(minutes=buffer)).strftime('%H:%M')}-{(base_start + timedelta(minutes=15)).strftime('%H:%M')}",
            confidence=0.82,
            recommended=True,
        ),
        DepartureWindow(
            window=f"{(base_start + timedelta(minutes=30)).strftime('%H:%M')}-{(base_start + timedelta(minutes=75)).strftime('%H:%M')}",
            confidence=0.68,
            recommended=False,
        ),
    ]

    note = "Based on schedule and duration heuristics"
    return DepartureEstimationResponse(route_id=payload.route_id, windows=windows, notes=note)


@router.get("/traffic-prediction/{route_id}", response_model=TrafficPredictionResponse)
async def traffic_prediction(
    route_id: str,
    identifier: str = Depends(get_rate_limit_identifier),
    db: AsyncSession = Depends(get_db),
) -> TrafficPredictionResponse:
    """Estimate congestion using distance/duration heuristics."""

    await _check_ai_rate(identifier)
    route = await db.get(TravelRoute, route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    if route.distance_km and route.duration_minutes:
        avg_speed = (route.distance_km / (route.duration_minutes / 60))
    else:
        avg_speed = 60.0
    congestion_score = max(0.0, min(1.0, 1 - (avg_speed / 90)))

    return TrafficPredictionResponse(
        route_id=route_id,
        congestion_score=round(congestion_score, 2),
        average_speed_kmh=round(avg_speed, 1),
        updated_at=datetime.utcnow(),
    )


@router.post("/recommend-attractions", response_model=AttractionRecommendationResponse)
async def recommend_attractions(
    payload: AttractionRecommendationRequest,
    identifier: str = Depends(get_rate_limit_identifier),
    db: AsyncSession = Depends(get_db),
) -> AttractionRecommendationResponse:
    """Rank attractions in a city by interest overlap and rating."""

    await _check_ai_rate(identifier)
    interests = [s.lower() for s in (payload.interests or [])]

    result = await db.execute(select(Attraction).where(Attraction.city_id == payload.city_id))
    scored: List[AttractionRecommendation] = []
    for item in result.scalars().all():
        tags = [t.lower() for t in (item.tags or [])]
        name_words = (item.name or "").lower().split()
        cat = (item.category or "").lower()
        overlap = len(set(interests) & (set(tags) | set(name_words) | {cat}))
        base_score = item.rating or 3.5
        score = min(0.99, 0.5 + 0.1 * overlap + 0.05 * (base_score - 3))
        reason = "Matches interests" if overlap else "Top rated nearby"
        scored.append(
            AttractionRecommendation(
                attraction_id=item.id,
                name=item.name,
                score=round(score, 2),
                reason=reason,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return AttractionRecommendationResponse(recommendations=scored[: payload.max_results])


@router.post("/tourist-guide/{attraction_id}", response_model=TouristGuideResponse)
async def tourist_guide(
    attraction_id: str,
    payload: TouristGuideRequest,
    identifier: str = Depends(get_rate_limit_identifier),
    db: AsyncSession = Depends(get_db),
) -> TouristGuideResponse:
    """Generate a brief guide using stored attraction metadata."""

    await _check_ai_rate(identifier)
    attraction = await db.get(Attraction, attraction_id)
    if not attraction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attraction not found")

    highlights = ", ".join((attraction.tags or [])[:3]) or "local highlights"
    category = attraction.category or "spot"
    guide = (
        f"{attraction.name} is a {category} in {attraction.city_id}. Suggested visit: {attraction.opening_hours or 'daytime'}. "
        f"Don't miss: {highlights}. Language: {payload.language}."
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
    db: AsyncSession = Depends(get_db),
) -> TourismSuggestionResponse:
    """Return curated suggestions derived from attractions."""

    await _check_ai_rate(identifier)
    result = await db.execute(select(Attraction).where(Attraction.city_id == city_id))
    attractions = result.scalars().all()
    if not attractions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City or attractions not found")

    top = sorted(attractions, key=lambda a: a.rating or 0, reverse=True)[:3]
    suggestions = [f"Visit {a.name} ({a.category or 'attraction'})" for a in top]
    suggestions.append("Book inter-urban transfers a day in advance")
    suggestions.append("Aim for morning visits to avoid heat and traffic")
    return TourismSuggestionResponse(city_id=city_id, suggestions=suggestions)


@router.post("/analyze-travel-pattern", response_model=TravelPatternResponse)
async def analyze_travel_pattern(
    payload: TravelPatternRequest,
    identifier: str = Depends(get_rate_limit_identifier),
    db: AsyncSession = Depends(get_db),
) -> TravelPatternResponse:
    """Provide heuristic travel pattern insights."""

    await _check_ai_rate(identifier)
    route = await db.get(TravelRoute, payload.route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    duration = route.duration_minutes or 0
    trend = "increasing" if duration > 180 else "stable"
    confidence = 0.75 if trend == "increasing" else 0.6
    commentary = "Higher demand on long-haul routes" if trend == "increasing" else "Short routes maintain steady demand"

    insights = [
        TravelPatternInsight(trend=trend, confidence=confidence, commentary=commentary),
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
