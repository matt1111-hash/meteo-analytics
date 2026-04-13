#!/usr/bin/env python3

"""
Global Weather Analyzer - Geo Utils Analytics
🌍 Analytics-specific geographic utilities.

Part of the geo_utils refactoring - split into focused modules.
"""

import logging
import statistics
from typing import Any

from .geo_utils_region import GeoUtilsRegion

logger = logging.getLogger(__name__)


def _resolve_filter_config(analytics_type: str) -> dict[str, float]:
    """Resolve population/distribution config for analytics type."""
    filters = {
        "temperature": {"min_population": 100000, "distribution_weight": 0.8},
        "precipitation": {"min_population": 50000, "distribution_weight": 0.6},
        "wind": {"min_population": 200000, "distribution_weight": 0.9},
        "global": {"min_population": 500000, "distribution_weight": 0.7},
    }
    return filters.get(analytics_type, filters["global"])


def _filter_cities_by_population(
    cities_data: list[dict[str, Any]], minimum_population: float
) -> list[dict[str, Any]]:
    """Filter cities by minimum population."""
    return [city for city in cities_data if city.get("population", 0) >= minimum_population]


def _build_coverage_distances(
    geo_utils: "GeoUtilsAnalytics",
    cities_data: list[dict[str, Any]],
    center_lat: float,
    center_lon: float,
) -> list[float]:
    """Build city-to-center distances."""
    return [
        geo_utils.distance_calculator.haversine_distance(
            center_lat, center_lon, city["lat"], city["lon"]
        )
        for city in cities_data
    ]


def _build_coverage_stats(
    bbox: Any,
    center: Any,
    area_km2: float,
    cities_data: list[dict[str, Any]],
    distances: list[float],
) -> dict[str, Any]:
    """Build coverage statistics payload."""
    max_distance = max(distances) if distances else 0
    avg_distance = statistics.mean(distances) if distances else 0
    return {
        "bounding_box": bbox.to_dict(),
        "geographic_center": center.to_dict(),
        "area_km2": area_km2,
        "cities_count": len(cities_data),
        "distances": {
            "max_distance_from_center": max_distance,
            "avg_distance_from_center": avg_distance,
            "coverage_radius_km": max_distance,
        },
    }


class GeoUtilsAnalytics(GeoUtilsRegion):
    """
    Extended GeoUtils with analytics operations.

    Analytics-specific operations:
    - Multi-city analytics optimization
    - Coverage area calculation
    - Weather analytics city selection
    """

    def optimize_cities_for_weather_analytics(
        self,
        cities_data: list[dict[str, Any]],
        analytics_type: str,
        max_cities: int = 50,
    ) -> list[dict[str, Any]]:
        """Optimize cities for weather analytics type."""
        filter_config = _resolve_filter_config(analytics_type)
        filtered_cities = _filter_cities_by_population(cities_data, filter_config["min_population"])

        if len(filtered_cities) < max_cities // 2:
            filtered_cities = _filter_cities_by_population(
                cities_data, filter_config["min_population"] // 2
            )

        if len(filtered_cities) > max_cities:
            filtered_cities = self.find_optimal_cities_for_region(filtered_cities, max_cities)

        logger.info(
            f"Weather analytics cities optimized ({analytics_type}): {len(filtered_cities)}"
        )
        return filtered_cities

    def calculate_multi_city_coverage_area(
        self, cities_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate multi-city analytics coverage area."""
        if not cities_data:
            return {}

        coordinates = [(city["lat"], city["lon"]) for city in cities_data]
        bbox = self.calculate_bounding_box(coordinates)
        center = self.calculate_geographic_center(coordinates)
        area_km2 = self._estimate_bounding_box_area(bbox)

        center_lat, center_lon = center.latitude, center.longitude
        distances = _build_coverage_distances(self, cities_data, center_lat, center_lon)
        return _build_coverage_stats(bbox, center, area_km2, cities_data, distances)


__all__ = ["GeoUtilsAnalytics"]
