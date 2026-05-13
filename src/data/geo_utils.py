#!/usr/bin/env python3

"""
Global Weather Analyzer - Geographic Utilities Module (Legacy Export)
🌍 Multi-City Analytics: Földrajzi számítások és koordináta műveletek

BACKWARD COMPATIBILITY SHIM — Re-exports from src.infrastructure.geo.*

NEW STRUCTURE (moved to infrastructure):
- geo_types.py - Enums and dataclasses (GeoPoint, BoundingBox, etc.)
- distance_calculator.py - DistanceCalculator class (Haversine, Vincenty)
- geo_utils_core.py - GeoUtils core class (basic operations)
- geo_utils_region.py - GeoUtilsRegion class (region operations)
- geo_utils_analytics.py - GeoUtilsAnalytics class (analytics operations)

HASZNÁLAT (Legacy - működik tovább):
from src.data.geo_utils import GeoUtils, DistanceCalculator, GeoPoint

Javasolt új használat:
from src.infrastructure.geo.geo_utils_core import GeoUtils
from src.infrastructure.geo.geo_utils_region import GeoUtilsRegion
from src.infrastructure.geo.geo_utils_analytics import GeoUtilsAnalytics
from src.infrastructure.geo.distance_calculator import DistanceCalculator
from src.infrastructure.geo.geo_types import GeoPoint
"""

# Re-export all types from infrastructure
from src.infrastructure.geo.distance_calculator import DistanceCalculator
from src.infrastructure.geo.geo_types import (
    BoundingBox,
    CoordinateSystem,
    DistanceUnit,
    GeographicRegion,
    GeoPoint,
)
from src.infrastructure.geo.geo_utils_analytics import GeoUtilsAnalytics
from src.infrastructure.geo.geo_utils_core import GeoUtils
from src.infrastructure.geo.geo_utils_region import GeoUtilsRegion

__all__ = [
    "BoundingBox",
    "CoordinateSystem",
    # Calculator
    "DistanceCalculator",
    # Types
    "DistanceUnit",
    "GeoPoint",
    # GeoUtils classes
    "GeoUtils",
    "GeoUtilsAnalytics",
    "GeoUtilsRegion",
    "GeographicRegion",
]
