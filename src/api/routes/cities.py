"""Cities search API routes."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, HTTPException, Query

from src.domain.ports import CityRepositoryPort
from src.infrastructure.container import get_city_repository_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cities", tags=["cities"])


def _get_city_repository() -> CityRepositoryPort:
    """Get city repository instance through port (CA compliant)."""
    return get_city_repository_port()


@router.get("/search")
async def search_cities(
    query: str = Query(..., min_length=2, description="Search query for city names"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum number of results"),
) -> dict:
    """Search for cities by name.

    Args:
        query: Search term (minimum 2 characters)
        limit: Maximum number of results to return (1-50, default 20)

    Returns:
        Dictionary with search results containing city information
    """
    try:
        city_repo = _get_city_repository()

        # Use the repository's autocomplete method
        results = city_repo.autocomplete_city_name(query, limit=limit)

        return {
            "query": query,
            "count": len(results),
            "cities": [
                {
                    "name": city_data["city"],
                    "country": city_data["country"],
                    "country_code": city_data["country_code"],
                    "coordinates": {"lat": city_data["lat"], "lon": city_data["lon"]}
                    if city_data["lat"] and city_data["lon"]
                    else None,
                    "population": city_data["population"],
                    "meteostat_station_id": city_data["meteostat_station_id"],
                    "data_quality_score": city_data["data_quality_score"],
                }
                for city_data in results
            ],
        }

    except Exception as exc:
        logger.error("Error searching cities: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search cities") from exc
