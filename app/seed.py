"""Seed reference data from in-memory fixtures into the database."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import data
from .models import Attraction, City, TravelRoute


async def _get_existing_ids(session: AsyncSession, model) -> set[str]:
    result = await session.execute(select(model.id))
    return {row[0] for row in result}


async def seed_reference_data(session: AsyncSession) -> None:
    """Idempotently seed cities, attractions, and travel routes."""

    existing_cities = await _get_existing_ids(session, City)
    for item in data.cities:
        if item["id"] in existing_cities:
            continue
        session.add(City(**item))

    existing_attractions = await _get_existing_ids(session, Attraction)
    for item in data.attractions:
        if item["id"] in existing_attractions:
            continue
        session.add(Attraction(**item))

    existing_routes = await _get_existing_ids(session, TravelRoute)
    for item in data.travels:
        if item["id"] in existing_routes:
            continue
        session.add(TravelRoute(**item))

    await session.commit()
