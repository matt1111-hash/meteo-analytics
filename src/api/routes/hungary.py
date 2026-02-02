"""Hungary-specific API routes."""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.data.city_types import City
from src.domain.ports import CityManagerPort, get_city_manager_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/hungary", tags=["hungary"])


def _get_city_manager() -> CityManagerPort:
    """Get city manager instance through port (CA compliant)."""
    return get_city_manager_port()


@router.get("/counties")
async def get_hungarian_counties() -> dict:
    """Get list of Hungarian counties (megyék).

    Returns 19 counties + Budapest in alphabetical order.

    Returns:
        Dictionary with county list
    """
    try:
        city_manager = _get_city_manager()
        counties = city_manager.get_hungarian_counties()

        # Clean up: remove empty strings, normalize "főváros" → "Budapest"
        cleaned = []
        for c in counties:
            if not c or not c.strip():
                continue
            if c.lower() in ["főváros", "budapest"]:
                cleaned.append("Budapest")
            else:
                cleaned.append(c)

        # Sort alphabetically (Budapest first)
        cleaned = sorted(cleaned, key=lambda x: ("Budapest" if x == "Budapest" else x).lower())

        return {
            "count": len(cleaned),
            "counties": cleaned
        }

    except Exception as exc:
        logger.error("Error getting Hungarian counties: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get Hungarian counties") from exc


@router.get("/regions")
async def get_hungarian_regions() -> dict:
    """Get list of Hungarian statistical regions (statisztikai régiók).

    Returns 7 statistical regions:
    - Közép-Magyarország
    - Észak-Magyarország
    - Észak-Alföld
    - Dél-Alföld
    - Dél-Dunántúl
    - Nyugat-Dunántúl
    - Közép-Dunántúl

    Returns:
        Dictionary with region list
    """
    regions = [
        "Közép-Magyarország",
        "Észak-Magyarország",
        "Észak-Alföld",
        "Dél-Alföld",
        "Dél-Dunántúl",
        "Nyugat-Dunántúl",
        "Közép-Dunántúl"
    ]

    return {
        "count": len(regions),
        "regions": regions
    }


@router.get("/settlements")
async def get_hungarian_settlements(
    county: Optional[str] = Query(None, description="Filter by county (megye)"),
    settlement_type: Optional[str] = Query(None, description="Filter by settlement type (város, község, nagyközség)"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum results")
) -> dict:
    """Get Hungarian settlements with optional filtering.

    Args:
        county: Filter by county (e.g., "Pest", "Bács-Kiskun")
        settlement_type: Filter by type (város, község, nagyközség)
        limit: Maximum number of results (1-500, default 50)

    Returns:
        Dictionary with settlement list
    """
    try:
        city_manager = _get_city_manager()

        if county:
            # Get settlements for specific county
            cities = city_manager.get_cities_for_hungarian_county(county)
        else:
            # Get all Hungarian settlements (limited)
            cities = city_manager.get_cities_for_region("Hungary", limit=limit)

        # Apply additional filters if needed
        if settlement_type:
            # Filter by settlement type
            cities = [c for c in cities if c.get("settlement_type") == settlement_type]

        # Limit results
        cities = cities[:limit]

        return {
            "count": len(cities),
            "filter": {
                "county": county,
                "settlement_type": settlement_type
            },
            "settlements": [
                {
                    "name": city_data.get("city"),
                    "county": city_data.get("megye") or county,  # Use megye field or filter county
                    "settlement_type": city_data.get("settlement_type"),
                    "coordinates": {
                        "lat": city_data.get("lat"),
                        "lon": city_data.get("lon")
                    } if city_data.get("lat") and city_data.get("lon") else None,
                    "population": city_data.get("population"),
                    "region_priority": city_data.get("region_priority")
                }
                for city_data in cities
            ]
        }

    except Exception as exc:
        logger.error("Error getting Hungarian settlements: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get Hungarian settlements") from exc


@router.get("/stations")
async def get_hungarian_weather_stations(
    county: Optional[str] = Query(None, description="Filter by county"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum results")
) -> dict:
    """Get Hungarian weather stations (settlements with weather data capability).

    Returns all Hungarian settlements that can serve as weather stations.
    Filtered by county optionally.

    Args:
        county: Filter by county
        limit: Maximum number of results

    Returns:
        Dictionary with weather station list
    """
    try:
        city_manager = _get_city_manager()

        # Get all Hungarian settlements by searching for each county
        all_cities = []
        if county:
            # Get settlements for specific county
            cities = city_manager.get_cities_for_hungarian_county(county)
            all_cities = cities[:limit]
        else:
            # Get settlements from all counties (limit per county)
            for county_name in city_manager.get_hungarian_counties():
                if not county_name:
                    continue
                cities = city_manager.get_cities_for_hungarian_county(county_name)
                all_cities.extend(cities)
                if len(all_cities) >= limit * 2:  # Get more than needed for filtering
                    break

        # Transform to station format
        stations = [
            {
                "id": f"HU-{city_data.get('id')}",
                "name": city_data.get("city"),
                "county": city_data.get("megye"),
                "settlement_type": city_data.get("settlement_type"),
                "coordinates": {
                    "lat": city_data.get("lat"),
                    "lon": city_data.get("lon")
                } if city_data.get("lat") and city_data.get("lon") else None,
                "population": city_data.get("population"),
                "region_priority": city_data.get("region_priority")
            }
            for city_data in all_cities[:limit]
        ]

        return {
            "count": len(stations),
            "filter": {"county": county},
            "stations": stations
        }

    except Exception as exc:
        logger.error("Error getting Hungarian weather stations: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get Hungarian weather stations") from exc


__all__ = ['router']
