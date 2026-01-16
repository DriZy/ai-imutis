"""Tourism endpoints for cities and attractions."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Attraction as AttractionModel, City as CityModel
from ..schemas.tourism import Attraction, AttractionSearchRequest, AttractionSearchResponse, City

router = APIRouter(prefix="/api", tags=["Tourism"])


def _to_city(model: CityModel) -> City:
    return City(
        id=model.id,
        name=model.name,
        country=model.country,
        description=model.description,
        population=model.population,
    )


def _to_attraction(model: AttractionModel) -> Attraction:
    return Attraction(
        id=model.id,
        city_id=model.city_id,
        name=model.name,
        description=model.description,
        category=model.category,
        rating=model.rating,
        opening_hours=model.opening_hours,
        entry_fee=model.entry_fee,
        location=model.location,
        tags=model.tags or [],
    )


@router.get("/cities", response_model=List[City])
async def list_cities(db: AsyncSession = Depends(get_db)) -> List[City]:
    """Return available cities."""

    result = await db.execute(select(CityModel))
    return [_to_city(c) for c in result.scalars().all()]


@router.get("/cities/{city_id}/attractions", response_model=List[Attraction])
async def list_city_attractions(city_id: str, db: AsyncSession = Depends(get_db)) -> List[Attraction]:
    """Return attractions in a city."""

    city = await db.get(CityModel, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    result = await db.execute(select(AttractionModel).where(AttractionModel.city_id == city_id))
    return [_to_attraction(a) for a in result.scalars().all()]


@router.get("/attractions/{attraction_id}", response_model=Attraction)
async def get_attraction(attraction_id: str, db: AsyncSession = Depends(get_db)) -> Attraction:
    """Return attraction detail."""

    attraction = await db.get(AttractionModel, attraction_id)
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return _to_attraction(attraction)


@router.post("/attractions/search", response_model=AttractionSearchResponse)
async def search_attractions(
    payload: AttractionSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> AttractionSearchResponse:
    """Simple search across name/description/category."""

    stmt = select(AttractionModel)
    if payload.city_id:
        stmt = stmt.where(AttractionModel.city_id == payload.city_id)
    if payload.category:
        stmt = stmt.where(AttractionModel.category == payload.category)
    if payload.min_rating:
        stmt = stmt.where(AttractionModel.rating >= payload.min_rating)

    result = await db.execute(stmt)
    matched = []
    query_lc = payload.query.lower()
    for item in result.scalars().all():
        content = f"{item.name or ''} {item.description or ''} {item.category or ''}".lower()
        if query_lc in content:
            matched.append(_to_attraction(item))
    return AttractionSearchResponse(results=matched)
