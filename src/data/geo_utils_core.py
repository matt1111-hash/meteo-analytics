#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geo Utils Core
🌍 Core geographic utilities.

Part of the geo_utils refactoring - split into focused modules.
"""

import logging
import math
import statistics
from typing import List, Optional, Tuple

from .geo_types import BoundingBox, GeoPoint
from .distance_calculator import DistanceCalculator


logger = logging.getLogger(__name__)


class GeoUtils:
    """
    Core geographic utilities.

    Basic geographic operations and coordinate calculations:
    - Bounding box calculations
    - Geographic center calculation
    - Coordinate validation and transformation
    """

    def __init__(self, distance_calculator: Optional[DistanceCalculator] = None):
        """Initialize GeoUtils."""
        self.distance_calculator = distance_calculator or DistanceCalculator()
        logger.debug("GeoUtils initialized")

    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate coordinates."""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

    def normalize_coordinates(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """Normalize coordinates."""
        norm_lat = max(-90, min(90, latitude))
        norm_lon = ((longitude + 180) % 360) - 180
        return norm_lat, norm_lon

    def calculate_bounding_box(self, points: List[Tuple[float, float]],
                              padding_degrees: float = 0.0) -> BoundingBox:
        """Calculate bounding box for points."""
        if not points:
            raise ValueError("Points list is empty")

        latitudes = [point[0] for point in points]
        longitudes = [point[1] for point in points]

        bbox = BoundingBox(
            min_latitude=min(latitudes),
            max_latitude=max(latitudes),
            min_longitude=min(longitudes),
            max_longitude=max(longitudes)
        )

        if padding_degrees > 0:
            bbox = bbox.expand_by_padding(padding_degrees)

        return bbox

    def calculate_geographic_center(self, points: List[Tuple[float, float]]) -> GeoPoint:
        """Calculate geographic center (centroid) of points."""
        if not points:
            raise ValueError("Points list is empty")

        x_coords = []
        y_coords = []
        z_coords = []

        for lat, lon in points:
            lat_rad = math.radians(lat)
            lon_rad = math.radians(lon)

            x = math.cos(lat_rad) * math.cos(lon_rad)
            y = math.cos(lat_rad) * math.sin(lon_rad)
            z = math.sin(lat_rad)

            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)

        avg_x = statistics.mean(x_coords)
        avg_y = statistics.mean(y_coords)
        avg_z = statistics.mean(z_coords)

        center_lon = math.atan2(avg_y, avg_x)
        center_lat = math.atan2(avg_z, math.sqrt(avg_x**2 + avg_y**2))

        return GeoPoint(
            latitude=math.degrees(center_lat),
            longitude=math.degrees(center_lon),
            name="Geographic Center"
        )

    def convert_to_web_mercator(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """Convert WGS84 coordinates to Web Mercator projection."""
        x = longitude * 20037508.34 / 180
        y = math.log(math.tan((90 + latitude) * math.pi / 360)) / (math.pi / 180)
        y = y * 20037508.34 / 180
        return x, y

    def suggest_map_zoom_level(self, bbox: BoundingBox, map_width_px: int = 800) -> int:
        """Suggest map zoom level for bounding box."""
        lon_span = abs(bbox.max_longitude - bbox.min_longitude)
        world_width = 256

        zoom = 0
        while zoom < 18:
            if world_width >= map_width_px * lon_span / 360:
                break
            world_width *= 2
            zoom += 1

        return max(0, min(18, zoom))


__all__ = ['GeoUtils']
