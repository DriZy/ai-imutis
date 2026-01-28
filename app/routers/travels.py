"""Travel endpoints for inter-urban mobility."""
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..dependencies import AuthenticatedUser, get_current_user, get_rate_limit_identifier
from ..models import Booking, TravelRoute, User
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


def _to_travel_summary(route: TravelRoute) -> TravelSummary:
    return TravelSummary(
        id=route.id,
        origin=route.origin,
        destination=route.destination,
        departure_time=route.departure_time,
        estimated_arrival=route.estimated_arrival,
        available_seats=route.available_seats,
        price_per_seat=float(route.price_per_seat),
        confidence=route.confidence,
    )


def _to_travel_detail(route: TravelRoute) -> TravelDetail:
    return TravelDetail(
        **_to_travel_summary(route).dict(),
        route_geometry=route.route_geometry,
        distance_km=route.distance_km,
        duration_minutes=route.duration_minutes,
        amenities=route.amenities or [],
    )


async def _ensure_user_record(db: AsyncSession, user: AuthenticatedUser) -> None:
    existing = await db.get(User, user.uid)
    if existing:
        return
    db.add(User(uid=user.uid, email=user.email, role=user.role))
    await db.commit()


@router.get("", response_model=List[TravelSummary])
async def list_travels(db: AsyncSession = Depends(get_db)) -> List[TravelSummary]:
    """Return available travel routes."""

    result = await db.execute(select(TravelRoute))
    routes = result.scalars().all()
    return [_to_travel_summary(r) for r in routes]


@router.post("/search", response_model=TravelSearchResponse)
async def search_travels(
    payload: TravelSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> TravelSearchResponse:
    """Filter routes by origin/destination with simple matching."""

    stmt = select(TravelRoute).where(
        TravelRoute.origin.ilike(f"{payload.origin}%"),
        TravelRoute.destination.ilike(f"{payload.destination}%"),
    )
    result = await db.execute(stmt)
    routes = result.scalars().all()
    return TravelSearchResponse(results=[_to_travel_summary(r) for r in routes])


@router.get("/{route_id}", response_model=TravelDetail)
async def get_travel(route_id: str, db: AsyncSession = Depends(get_db)) -> TravelDetail:
    """Return route details."""

    route = await db.get(TravelRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return _to_travel_detail(route)


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
    db: AsyncSession = Depends(get_db),
):
    """Simulate a booking and return confirmation."""

    settings = get_settings()
    await rate_limiter.check(
        identifier,
        limit=settings.rate_limit_booking,
        window_seconds=settings.rate_limit_window_seconds,
    )

    await _ensure_user_record(db, user)

    result = await db.execute(
        select(TravelRoute).where(TravelRoute.id == payload.route_id).with_for_update()
    )
    route = result.scalars().first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    if route.available_seats < payload.passengers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough seats available",
        )

    route.available_seats -= payload.passengers
    booking = Booking(
        route_id=route.id,
        user_id=user.uid,
        passengers=payload.passengers,
        payment_method=payload.payment_method,
        special_requests=payload.special_requests,
        status="confirmed",
        departure_time=route.departure_time,
        estimated_arrival=route.estimated_arrival + timedelta(minutes=5),
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    await db.refresh(route)

    return TravelBookingResponse(
        booking_id=booking.id,
        status=booking.status,
        departure_time=booking.departure_time,
        estimated_arrival=booking.estimated_arrival,
    )
