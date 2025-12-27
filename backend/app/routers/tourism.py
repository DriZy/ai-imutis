"""Tourism endpoints for cities and attractions."""
from typing import List

from fastapi import APIRouter, HTTPException

from .. import data
from ..schemas.tourism import Attraction, AttractionSearchRequest, AttractionSearchResponse, City

router = APIRouter(prefix="/api", tags=["Tourism"])


@router.get("/cities", response_model=List[City])
async def list_cities() -> List[City]:
    """Return available cities."""

    return [City(**c) for c in data.cities]


@router.get("/cities/{city_id}/attractions", response_model=List[Attraction])
async def list_city_attractions(city_id: str) -> List[Attraction]:
    """Return attractions in a city."""

    city_exists = any(c["id"] == city_id for c in data.cities)
    if not city_exists:
        raise HTTPException(status_code=404, detail="City not found")

    items = [a for a in data.attractions if a["city_id"] == city_id]
    return [Attraction(**a) for a in items]


@router.get("/attractions/{attraction_id}", response_model=Attraction)
async def get_attraction(attraction_id: str) -> Attraction:
    """Return attraction detail."""

    for item in data.attractions:
        if item["id"] == attraction_id:
            return Attraction(**item)
    raise HTTPException(status_code=404, detail="Attraction not found")


@router.post("/attractions/search", response_model=AttractionSearchResponse)
async def search_attractions(payload: AttractionSearchRequest) -> AttractionSearchResponse:
    """Simple search across name/description/category."""

    query = payload.query.lower()
    results = []
    for item in data.attractions:
        if payload.city_id and item["city_id"] != payload.city_id:
            continue
        if payload.category and item.get("category") != payload.category:
            continue
        if item.get("rating", 0) < payload.min_rating:
            continue
        content = f"{item.get('name', '')} {item.get('description', '')} {item.get('category', '')}".lower()
        if query in content:
            results.append(Attraction(**item))
    return AttractionSearchResponse(results=results)
