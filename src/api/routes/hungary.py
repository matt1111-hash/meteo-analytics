"""Hungary-specific API routes."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, HTTPException, Query

from src.domain.ports import CityManagerPort
from src.infrastructure.container import get_city_manager_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/hungary", tags=["hungary"])


def _normalize_county_name(county_name: str) -> str:
    """Normalize special county labels."""
    return "Budapest" if county_name.lower() in ["főváros", "budapest"] else county_name


def _sort_counties(counties: list[str]) -> list[str]:
    """Sort counties alphabetically with Budapest normalized."""
    return sorted(
        counties,
        key=lambda county_name: ("Budapest" if county_name == "Budapest" else county_name).lower(),
    )


def _build_coordinate_payload(
    city_data: dict,
    fallback_county: str | None = None,  # noqa: ARG001
) -> dict | None:
    """Build optional coordinate payload."""
    if not city_data.get("lat") or not city_data.get("lon"):
        return None
    return {
        "lat": city_data.get("lat"),
        "lon": city_data.get("lon"),
    }


def _serialize_settlement(city_data: dict, fallback_county: str | None) -> dict:
    """Serialize one settlement payload."""
    return {
        "name": city_data.get("city"),
        "county": city_data.get("megye") or fallback_county,
        "settlement_type": city_data.get("settlement_type"),
        "coordinates": _build_coordinate_payload(city_data, fallback_county),
        "population": city_data.get("population"),
        "region_priority": city_data.get("region_priority"),
    }


def _serialize_station(city_data: dict) -> dict:
    """Serialize one weather station payload."""
    return {
        "id": f"HU-{city_data.get('id')}",
        "name": city_data.get("city"),
        "county": city_data.get("megye"),
        "settlement_type": city_data.get("settlement_type"),
        "coordinates": _build_coordinate_payload(city_data),
        "population": city_data.get("population"),
        "region_priority": city_data.get("region_priority"),
    }


def _fetch_settlements(city_manager: CityManagerPort, county: str | None, limit: int) -> list[dict]:
    """Fetch settlement data with optional county filter."""
    if county:
        return city_manager.get_cities_for_hungarian_county(county)
    return city_manager.get_cities_for_region("Hungary", limit=limit)


def _filter_settlements_by_type(cities: list[dict], settlement_type: str | None) -> list[dict]:
    """Filter settlement results by settlement type when requested."""
    if not settlement_type:
        return cities
    return [city for city in cities if city.get("settlement_type") == settlement_type]


def _build_settlements_response(
    cities: list[dict],
    county: str | None,
    settlement_type: str | None,
) -> dict:
    """Build serialized settlement response payload."""
    return {
        "count": len(cities),
        "filter": {"county": county, "settlement_type": settlement_type},
        "settlements": [_serialize_settlement(city_data, county) for city_data in cities],
    }


def _fetch_station_candidates(
    city_manager: CityManagerPort, county: str | None, limit: int
) -> list[dict]:
    """Fetch candidate station settlements."""
    if county:
        return city_manager.get_cities_for_hungarian_county(county)[:limit]

    all_cities: list[dict] = []
    for county_name in city_manager.get_hungarian_counties():
        if not county_name:
            continue
        all_cities.extend(city_manager.get_cities_for_hungarian_county(county_name))
        if len(all_cities) >= limit * 2:
            break
    return all_cities


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
        cleaned = [
            _normalize_county_name(county_name)
            for county_name in counties
            if county_name and county_name.strip()
        ]
        cleaned = _sort_counties(cleaned)

        return {"count": len(cleaned), "counties": cleaned}

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
        "Közép-Dunántúl",
    ]

    return {"count": len(regions), "regions": regions}


@router.get("/settlements")
async def get_hungarian_settlements(
    county: str | None = Query(None, description="Filter by county (megye)"),
    settlement_type: str | None = Query(
        None, description="Filter by settlement type (város, község, nagyközség)"
    ),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum results"),
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
        cities = _fetch_settlements(city_manager, county, limit)
        cities = _filter_settlements_by_type(cities, settlement_type)
        cities = cities[:limit]
        return _build_settlements_response(cities, county, settlement_type)

    except Exception as exc:
        logger.error("Error getting Hungarian settlements: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get Hungarian settlements") from exc


@router.get("/stations")
async def get_hungarian_weather_stations(
    county: str | None = Query(None, description="Filter by county"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum results"),
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
        all_cities = _fetch_station_candidates(city_manager, county, limit)
        stations = [_serialize_station(city_data) for city_data in all_cities[:limit]]

        return {
            "count": len(stations),
            "filter": {"county": county},
            "stations": stations,
        }

    except Exception as exc:
        logger.error("Error getting Hungarian weather stations: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to get Hungarian weather stations"
        ) from exc


__all__ = ["router"]
