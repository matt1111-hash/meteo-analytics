#!/usr/bin/env python3

"""
Global Weather Analyzer - Geo Utils Region
🌍 Region-based geographic utilities.

Part of the geo_utils refactoring - split into focused modules.
"""

import logging
import math
from typing import Any

from .geo_types import BoundingBox, GeographicRegion, GeoPoint
from .geo_utils_core import GeoUtils

logger = logging.getLogger(__name__)


class GeoUtilsRegion(GeoUtils):
    """
    Extended GeoUtils with region operations.

    Region-specific operations:
    - Region calculation from cities
    - City proximity grouping
    - Optimal city selection
    """

    def __init__(self, distance_calculator=None):
        """Initialize GeoUtilsRegion."""
        super().__init__(distance_calculator)
        self.region_cache: dict[str, GeographicRegion] = {}

    def calculate_region_from_cities(
        self, cities_data: list[dict[str, Any]], region_name: str
    ) -> GeographicRegion:
        """Calculate geographic region from cities."""
        if not cities_data:
            raise ValueError("Cities list is empty")

        coordinates = [(city["lat"], city["lon"]) for city in cities_data]

        bbox = self.calculate_bounding_box(coordinates, padding_degrees=0.1)
        center = self.calculate_geographic_center(coordinates)

        total_population = sum(
            city.get("population", 0) for city in cities_data if city.get("population")
        )
        cities_count = len(cities_data)
        area_km2 = self._estimate_bounding_box_area(bbox)

        region = GeographicRegion(
            name=region_name,
            bounding_box=bbox,
            center_point=center,
            area_km2=area_km2,
            population=total_population if total_population > 0 else None,
            cities_count=cities_count,
        )

        self.region_cache[region_name] = region
        return region

    def _estimate_bounding_box_area(self, bbox: BoundingBox) -> float:
        """Estimate bounding box area in km²."""
        lat_diff = bbox.max_latitude - bbox.min_latitude
        lon_diff = bbox.max_longitude - bbox.min_longitude

        avg_lat = (bbox.max_latitude + bbox.min_latitude) / 2
        lat_correction = math.cos(math.radians(avg_lat))

        lat_km = lat_diff * 111.32
        lon_km = lon_diff * 111.32 * lat_correction

        return abs(lat_km * lon_km)

    def group_cities_by_proximity(
        self, cities_data: list[dict[str, Any]], max_distance_km: float = 100
    ) -> list[list[dict[str, Any]]]:
        """Group cities by geographic proximity."""
        if not cities_data:
            return []

        groups = []
        remaining_cities = cities_data.copy()

        while remaining_cities:
            current_group = [remaining_cities.pop(0)]
            added_to_group = True

            while added_to_group and remaining_cities:
                added_to_group = False

                for group_city in current_group[:]:
                    for i, city in enumerate(remaining_cities):
                        distance = self.distance_calculator.haversine_distance(
                            group_city["lat"],
                            group_city["lon"],
                            city["lat"],
                            city["lon"],
                        )

                        if distance <= max_distance_km:
                            current_group.append(remaining_cities.pop(i))
                            added_to_group = True
                            break

                    if added_to_group:
                        break

            groups.append(current_group)

        groups.sort(key=len, reverse=True)
        return groups

    def _filter_cities_in_region(
        self,
        all_cities: list[dict[str, Any]],
        region_bbox: BoundingBox | None,
    ) -> list[dict[str, Any]]:
        """Filter cities by bounding box when provided."""
        if region_bbox is None:
            return all_cities

        filtered_cities: list[dict[str, Any]] = []
        for city in all_cities:
            point = GeoPoint(city["lat"], city["lon"])
            if region_bbox.contains_point(point):
                filtered_cities.append(city)
        return filtered_cities

    def _split_cities_by_population(
        self, cities: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Split cities into with/without population buckets."""
        cities_with_pop = [city for city in cities if city.get("population", 0) > 0]
        cities_without_pop = [city for city in cities if city.get("population", 0) <= 0]
        cities_with_pop.sort(key=lambda c: c.get("population", 0), reverse=True)
        return cities_with_pop, cities_without_pop

    def _calculate_city_selection_score(
        self,
        city: dict[str, Any],
        selected_cities: list[dict[str, Any]],
    ) -> float:
        """Calculate spacing and population score for one city."""
        min_distance = float("inf")
        for selected in selected_cities:
            distance = self.distance_calculator.haversine_distance(
                city["lat"], city["lon"], selected["lat"], selected["lon"]
            )
            min_distance = min(min_distance, distance)

        distance_score = min(min_distance / 1000, 1.0)
        population_score = min(city.get("population", 1) / 1000000, 1.0)
        return distance_score * 0.7 + population_score * 0.3

    def _select_best_remaining_city(
        self,
        remaining_cities: list[dict[str, Any]],
        selected_cities: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Select the best remaining city based on distance and population."""
        best_city: dict[str, Any] | None = None
        best_score = -1.0

        for city in remaining_cities:
            combined_score = self._calculate_city_selection_score(city, selected_cities)
            if combined_score > best_score:
                best_score = combined_score
                best_city = city

        return best_city

    def find_optimal_cities_for_region(
        self,
        all_cities: list[dict[str, Any]],
        target_count: int,
        region_bbox: BoundingBox | None = None,
    ) -> list[dict[str, Any]]:
        """Find optimal cities for region analytics."""
        filtered_cities = self._filter_cities_in_region(all_cities, region_bbox)

        if len(filtered_cities) <= target_count:
            return filtered_cities

        cities_with_pop, cities_without_pop = self._split_cities_by_population(filtered_cities)
        selected_cities = []
        remaining_cities = cities_with_pop + cities_without_pop

        if remaining_cities:
            selected_cities.append(remaining_cities.pop(0))

        while len(selected_cities) < target_count and remaining_cities:
            best_city = self._select_best_remaining_city(remaining_cities, selected_cities)
            if best_city:
                selected_cities.append(best_city)
                remaining_cities.remove(best_city)
            else:
                break

        return selected_cities


__all__ = ["GeoUtilsRegion"]
