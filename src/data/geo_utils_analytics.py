#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geo Utils Analytics
🌍 Analytics-specific geographic utilities.

Part of the geo_utils refactoring - split into focused modules.
"""

import logging
import statistics
from typing import Any, Dict, List

from .geo_utils_region import GeoUtilsRegion

logger = logging.getLogger(__name__)


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
        cities_data: List[Dict[str, Any]],
        analytics_type: str,
        max_cities: int = 50,
    ) -> List[Dict[str, Any]]:
        """Optimize cities for weather analytics type."""
        filters = {
            "temperature": {"min_population": 100000, "distribution_weight": 0.8},
            "precipitation": {"min_population": 50000, "distribution_weight": 0.6},
            "wind": {"min_population": 200000, "distribution_weight": 0.9},
            "global": {"min_population": 500000, "distribution_weight": 0.7},
        }

        filter_config = filters.get(analytics_type, filters["global"])

        filtered_cities = [
            city
            for city in cities_data
            if city.get("population", 0) >= filter_config["min_population"]
        ]

        if len(filtered_cities) < max_cities // 2:
            filtered_cities = [
                city
                for city in cities_data
                if city.get("population", 0) >= filter_config["min_population"] // 2
            ]

        if len(filtered_cities) > max_cities:
            filtered_cities = self.find_optimal_cities_for_region(
                filtered_cities, max_cities
            )

        logger.info(
            f"Weather analytics cities optimized ({analytics_type}): {len(filtered_cities)}"
        )
        return filtered_cities

    def calculate_multi_city_coverage_area(
        self, cities_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate multi-city analytics coverage area."""
        if not cities_data:
            return {}

        coordinates = [(city["lat"], city["lon"]) for city in cities_data]
        bbox = self.calculate_bounding_box(coordinates)
        center = self.calculate_geographic_center(coordinates)
        area_km2 = self._estimate_bounding_box_area(bbox)

        distances = []
        center_lat, center_lon = center.latitude, center.longitude

        for city in cities_data:
            distance = self.distance_calculator.haversine_distance(
                center_lat, center_lon, city["lat"], city["lon"]
            )
            distances.append(distance)

        coverage_stats = {
            "bounding_box": bbox.to_dict(),
            "geographic_center": center.to_dict(),
            "area_km2": area_km2,
            "cities_count": len(cities_data),
            "distances": {
                "max_distance_from_center": max(distances) if distances else 0,
                "avg_distance_from_center": statistics.mean(distances)
                if distances
                else 0,
                "coverage_radius_km": max(distances) if distances else 0,
            },
        }

        return coverage_stats


__all__ = ["GeoUtilsAnalytics"]
