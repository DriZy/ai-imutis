"""Travel endpoints for inter-urban mobility."""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from .. import data
from ..config import get_settings
from ..dependencies import AuthenticatedUser, get_current_user, get_rate_limit_identifier
from ..rate_limit import rate_limiter
from ..schemas.travels import (
    DepartureWindow,
    TravelBookingRequest,
    TravelBookingResponse,
    TravelDetail,
    TravelEstimateRequest,
    TravelEstimateResponse,
    TravelSearchRequest,
    TravelSearchResponse,
    TravelSummary,
)

router = APIRouter(prefix="/api/travels", tags=["Travel"])


@router.get("", response_model=List[TravelSummary])
async def list_travels() -> List[TravelSummary]:
    """Return available travel routes."""

    return [TravelSummary(**t) for t in data.travels]


@router.post("/search", response_model=TravelSearchResponse)
async def search_travels(payload: TravelSearchRequest) -> TravelSearchResponse:
    """Filter routes by origin/destination with simple matching."""

    origin = payload.origin.lower()
    destination = payload.destination.lower()
    results = [
        TravelSummary(**t)
        for t in data.travels
        if t["origin"].lower().startswith(origin)
        and t["destination"].lower().startswith(destination)
    ]
    return TravelSearchResponse(results=results)


@router.get("/{route_id}", response_model=TravelDetail)
async def get_travel(route_id: str) -> TravelDetail:
    """Return route details."""

    for item in data.travels:
        if item["id"] == route_id:
            return TravelDetail(**item)
    raise HTTPException(status_code=404, detail="Route not found")


@router.post("/estimate", response_model=TravelEstimateResponse)
async def estimate_departure(
    payload: TravelEstimateRequest,
    identifier: str = Depends(get_rate_limit_identifier),
):
    """Return AI-inspired departure windows (stubbed)."""

    settings = get_settings()
    await rate_limiter.check(
        identifier,
        limit=settings.rate_limit_ai,
        window_seconds=settings.rate_limit_window_seconds,
    )

    base_windows = [
        DepartureWindow(label="07:30-08:30", confidence=0.81, recommended=True),
        DepartureWindow(label="09:00-10:00", confidence=0.74, recommended=False),
        DepartureWindow(label="12:00-13:00", confidence=0.63, recommended=False),
    ]
    return TravelEstimateResponse(route_id=payload.route_id, windows=base_windows)


@router.post("/book", response_model=TravelBookingResponse)
async def book_travel(
    payload: TravelBookingRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    identifier: str = Depends(get_rate_limit_identifier),
):
    """Simulate a booking and return confirmation."""

    settings = get_settings()
    await rate_limiter.check(
        identifier,
        limit=settings.rate_limit_booking,
        window_seconds=settings.rate_limit_window_seconds,
    )

    # Find travel record to reuse times
    selected = next((t for t in data.travels if t["id"] == payload.route_id), None)
    if not selected:
        raise HTTPException(status_code=404, detail="Route not found")

    departure_time: datetime = selected["departure_time"]
    arrival_time: datetime = selected["estimated_arrival"]

    # Add minor offset to mimic processing
    estimated_arrival = arrival_time + timedelta(minutes=5)
    booking_id = f"bk-{payload.route_id}-{int(datetime.utcnow().timestamp())}"

    return TravelBookingResponse(
        booking_id=booking_id,
        status="confirmed",
        departure_time=departure_time,
        estimated_arrival=estimated_arrival,
    )
