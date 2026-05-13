"""Metadata API routes - available metrics, regions, etc."""

from __future__ import annotations  # noqa: I001

from fastapi import APIRouter

from src.analytics.multi_city_engine_core import MultiCityEngine
from src.domain.constants.regions import REGIONS
from src.domain.value_objects.enums import AnalyticsMetric

router = APIRouter(prefix="/api/weather", tags=["metadata"])


@router.get("/metrics")
async def get_available_metrics() -> dict:
    """Get list of all available weather metrics.

    Returns:
        Dictionary with metric names and descriptions.
    """
    metrics = {
        "temperature_2m_max": {
            "name": "Maximum Temperature",
            "unit": "°C",
            "description": "Daily maximum temperature at 2m height",
        },
        "temperature_2m_min": {
            "name": "Minimum Temperature",
            "unit": "°C",
            "description": "Daily minimum temperature at 2m height",
        },
        "temperature_2m_mean": {
            "name": "Mean Temperature",
            "unit": "°C",
            "description": "Daily mean temperature at 2m height",
        },
        "precipitation_sum": {
            "name": "Precipitation",
            "unit": "mm",
            "description": "Daily total precipitation (rain + snow)",
        },
        "windspeed_10m_max": {
            "name": "Maximum Wind Speed",
            "unit": "km/h",
            "description": "Daily maximum wind speed at 10m height",
        },
        "windgusts_10m_max": {
            "name": "Maximum Wind Gusts",
            "unit": "km/h",
            "description": "Daily maximum wind gusts at 10m height",
        },
        "temperature_range": {
            "name": "Temperature Range",
            "unit": "°C",
            "description": "Difference between max and min temperature",
        },
    }

    return {
        "metrics": metrics,
        "total_count": len(metrics),
        "enum_values": [m.value for m in AnalyticsMetric],
    }


@router.get("/regions")
async def get_available_regions() -> dict:
    """Get list of all available regions and countries.

    Returns:
        Dictionary with region names and metadata.
    """
    # Transform to frontend-friendly format
    formatted_regions = {}
    for region_key, region_config in REGIONS.items():
        formatted_regions[region_key] = {
            "name": region_config.get("name", region_key),
            "max_cities": region_config.get("max_cities", 50),
            "country_codes": region_config.get("country_codes", []),
        }

    return {
        "regions": formatted_regions,
        "total_count": len(formatted_regions),
        "region_keys": list(REGIONS.keys()),
    }


@router.get("/query-types")
async def get_query_types() -> dict:
    """Get list of all available query types (analysis modes).

    Returns:
        Dictionary with query type names and configurations.
    """
    # Transform to frontend-friendly format
    formatted_types = {}
    for query_key, query_config in MultiCityEngine.QUERY_TYPES.items():
        metric_enum_raw = query_config.get("metric_enum", "")
        if isinstance(metric_enum_raw, AnalyticsMetric):
            metric_enum_str = metric_enum_raw.value
        else:
            metric_enum_str = str(metric_enum_raw)

        formatted_types[query_key] = {
            "question_template": query_config.get("question_template", ""),
            "metric": query_config.get("metric", ""),
            "metric_enum": metric_enum_str,
            "sort_desc": query_config.get("sort_desc", True),
        }

    return {
        "query_types": formatted_types,
        "total_count": len(formatted_types),
        "query_keys": list(MultiCityEngine.QUERY_TYPES.keys()),
    }
