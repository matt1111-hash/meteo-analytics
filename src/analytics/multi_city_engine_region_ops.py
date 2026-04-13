# mypy: ignore-errors
"""Regional lookup helpers for the multi-city engine."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS

if TYPE_CHECKING:
    from .multi_city_engine_core import MultiCityEngine

logger = logging.getLogger(__name__)


def _resolve_region_metadata(
    engine: MultiCityEngine,
    region: str,
    limit: int | None,
    max_cities: int | None,
) -> tuple[str, dict[str, Any], int]:
    """Resolve mapped region, config and effective limit."""
    mapped_region = engine.resolve_region_name(region)
    region_config = REGIONS[mapped_region]
    final_limit = max_cities or limit or region_config["max_cities"]
    return mapped_region, region_config, final_limit


def _log_region_fetch(original_region: str, mapped_region: str, final_limit: int) -> None:
    """Log normalized region lookup parameters."""
    logger.info(
        "🔧 get_cities_for_region: original='%s' → mapped='%s', limit=%s",
        original_region,
        mapped_region,
        final_limit,
    )


def _log_region_fetch_result(
    original_region: str, mapped_region: str, cities: list[dict[str, Any]]
) -> None:
    """Log region lookup result with Hungarian mapping details when available."""
    if original_region in HUNGARIAN_REGIONAL_MAPPING:
        logger.info(
            "✅ REGIONÁLIS lekérdezés: %d város %s régióból (%s)",
            len(cities),
            original_region,
            HUNGARIAN_REGIONAL_MAPPING[original_region],
        )
        return
    logger.info(
        "✅ ORSZÁGOS lekérdezés: %d város %s régióból",
        len(cities),
        mapped_region,
    )


def get_cities_for_region(
    engine: MultiCityEngine,
    region: str,
    limit: int | None = None,
    max_cities: int | None = None,
) -> list[dict[str, Any]]:
    """Resolve a region and fetch its cities through the repository."""
    original_region = region

    try:
        mapped_region, region_config, final_limit = _resolve_region_metadata(
            engine, region, limit, max_cities
        )
    except ValueError as exc:
        logger.error("⚠ Invalid region: %s - %s", region, exc)
        return []

    country_codes = region_config["country_codes"]
    _log_region_fetch(original_region, mapped_region, final_limit)

    try:
        cities = engine.city_repository.get_cities_for_region(
            mapped_region=mapped_region,
            original_region=original_region,
            country_codes=country_codes,
            limit=final_limit,
            hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
        )
        _log_region_fetch_result(original_region, mapped_region, cities)
        return cities
    except Exception as exc:
        logger.error("⚠ Hiba városok lekérdezésénél: %s", exc, exc_info=True)
        return []
