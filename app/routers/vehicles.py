"""Vehicle registration and management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..dependencies import AuthenticatedUser, get_current_user
from ..models import User, Vehicle
from ..schemas.vehicles import VehicleRegistrationRequest, VehicleResponse, VehicleUpdateRequest

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


async def _ensure_user_record(db: AsyncSession, user: AuthenticatedUser) -> None:
    """Ensure user exists in database."""
    existing = await db.get(User, user.uid)
    if existing:
        return
    db.add(User(uid=user.uid, email=user.email, role=user.role))
    await db.commit()


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def register_vehicle(
    payload: VehicleRegistrationRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VehicleResponse:
    """Register a new vehicle for the authenticated user."""
    
    await _ensure_user_record(db, user)
    
    # Check if license plate already exists
    stmt = select(Vehicle).where(Vehicle.license_plate == payload.license_plate)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this license plate is already registered",
        )
    
    vehicle = Vehicle(
        owner_id=user.uid,
        vehicle_type=payload.vehicle_type,
        license_plate=payload.license_plate,
        capacity=payload.capacity,
        photo_url=str(payload.photo_url),
        make=payload.make,
        model=payload.model,
        year=payload.year,
        color=payload.color,
        amenities=payload.amenities,
    )
    
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    
    return VehicleResponse.from_orm(vehicle)


@router.get("", response_model=List[VehicleResponse])
async def list_my_vehicles(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[VehicleResponse]:
    """List all vehicles owned by the authenticated user."""
    
    stmt = select(Vehicle).where(Vehicle.owner_id == user.uid).order_by(Vehicle.created_at.desc())
    result = await db.execute(stmt)
    vehicles = result.scalars().all()
    
    return [VehicleResponse.from_orm(v) for v in vehicles]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VehicleResponse:
    """Get details of a specific vehicle."""
    
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    # Only the owner can view their vehicle details
    if vehicle.owner_id != user.uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this vehicle")
    
    return VehicleResponse.from_orm(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VehicleResponse:
    """Update vehicle information."""
    
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    if vehicle.owner_id != user.uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this vehicle")
    
    # Update only provided fields
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "photo_url" and value is not None:
            value = str(value)
        setattr(vehicle, field, value)
    
    await db.commit()
    await db.refresh(vehicle)
    
    return VehicleResponse.from_orm(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vehicle (sets is_active to False)."""
    
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    if vehicle.owner_id != user.uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this vehicle")
    
    # Soft delete by setting is_active to False
    vehicle.is_active = False
    await db.commit()
