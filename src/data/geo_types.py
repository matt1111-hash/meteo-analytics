#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geographic Data Types
🌍 Geographic data structures and enums.

Part of the geo_utils refactoring - split into focused modules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class DistanceUnit(Enum):
    """Distance measurement units."""

    KILOMETERS = "km"
    MILES = "miles"
    NAUTICAL_MILES = "nm"
    METERS = "m"


class CoordinateSystem(Enum):
    """Coordinate systems."""

    WGS84 = "WGS84"
    WGS72 = "WGS72"
    NAD83 = "NAD83"
    ETRS89 = "ETRS89"


@dataclass
class GeoPoint:
    """Geographic point data structure."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    name: Optional[str] = None

    def __post_init__(self):
        """Validate coordinates on initialization."""
        if not self.is_valid():
            raise ValueError(
                f"Invalid coordinates: lat={self.latitude}, lon={self.longitude}"
            )

    def is_valid(self) -> bool:
        """Check if coordinates are valid."""
        return (-90 <= self.latitude <= 90) and (-180 <= self.longitude <= 180)

    def normalize(self) -> "GeoPoint":
        """Normalize coordinates."""
        # Longitude wraparound (-180 to 180)
        normalized_lon = ((self.longitude + 180) % 360) - 180

        # Latitude clamping (-90 to 90)
        normalized_lat = max(-90, min(90, self.latitude))

        return GeoPoint(
            latitude=normalized_lat,
            longitude=normalized_lon,
            altitude=self.altitude,
            name=self.name,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert GeoPoint to dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeoPoint":
        """Create GeoPoint from dictionary."""
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude"),
            name=data.get("name"),
        )


@dataclass
class BoundingBox:
    """Bounding box data structure."""

    min_latitude: float
    max_latitude: float
    min_longitude: float
    max_longitude: float

    def __post_init__(self):
        """Validate bounding box."""
        if self.min_latitude > self.max_latitude:
            raise ValueError("min_latitude > max_latitude")
        if self.min_longitude > self.max_longitude:
            if not (self.min_longitude > 0 and self.max_longitude < 0):
                raise ValueError("min_longitude > max_longitude")

    def contains_point(self, point: GeoPoint) -> bool:
        """Check if point is inside bounding box."""
        lat_in_range = self.min_latitude <= point.latitude <= self.max_latitude

        if self.min_longitude <= self.max_longitude:
            lon_in_range = self.min_longitude <= point.longitude <= self.max_longitude
        else:
            # Dateline crossing
            lon_in_range = (point.longitude >= self.min_longitude) or (
                point.longitude <= self.max_longitude
            )

        return lat_in_range and lon_in_range

    def get_center(self) -> GeoPoint:
        """Calculate bounding box center."""
        center_lat = (self.min_latitude + self.max_latitude) / 2

        if self.min_longitude <= self.max_longitude:
            center_lon = (self.min_longitude + self.max_longitude) / 2
        else:
            # Dateline crossing
            center_lon = ((self.min_longitude + self.max_longitude + 360) / 2) % 360
            if center_lon > 180:
                center_lon -= 360

        return GeoPoint(latitude=center_lat, longitude=center_lon)

    def expand_by_padding(self, padding_degrees: float) -> "BoundingBox":
        """Expand bounding box by padding."""
        return BoundingBox(
            min_latitude=max(-90, self.min_latitude - padding_degrees),
            max_latitude=min(90, self.max_latitude + padding_degrees),
            min_longitude=max(-180, self.min_longitude - padding_degrees),
            max_longitude=min(180, self.max_longitude + padding_degrees),
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert BoundingBox to dictionary."""
        return {
            "min_latitude": self.min_latitude,
            "max_latitude": self.max_latitude,
            "min_longitude": self.min_longitude,
            "max_longitude": self.max_longitude,
        }


@dataclass
class GeographicRegion:
    """Geographic region data structure."""

    name: str
    bounding_box: BoundingBox
    center_point: GeoPoint
    area_km2: Optional[float] = None
    population: Optional[int] = None
    cities_count: Optional[int] = None
    timezone: Optional[str] = None

    def is_point_in_region(self, point: GeoPoint) -> bool:
        """Check if point is in region."""
        return self.bounding_box.contains_point(point)


__all__ = [
    "DistanceUnit",
    "CoordinateSystem",
    "GeoPoint",
    "BoundingBox",
    "GeographicRegion",
]
