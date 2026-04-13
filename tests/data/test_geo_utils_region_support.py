"""Tests for GeoUtilsRegion from geo_utils_region.py."""

from __future__ import annotations  # noqa: I001

from typing import Any

import pytest

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import BoundingBox, GeoPoint, GeographicRegion
from src.data.geo_utils_region import GeoUtilsRegion

__all__ = [
    "BoundingBox",
    "DistanceCalculator",
    "GeoPoint",
    "GeoUtilsRegion",
    "GeographicRegion",
    "geo_utils",
    "pytest",
    "sample_cities",
]


@pytest.fixture
def geo_utils() -> GeoUtilsRegion:
    """Create GeoUtilsRegion instance."""
    return GeoUtilsRegion()


@pytest.fixture
def sample_cities() -> list[dict[str, Any]]:
    """Sample city data for testing."""
    return [
        {"city": "Budapest", "lat": 47.4979, "lon": 19.0402, "population": 1752286},
        {"city": "Debrecen", "lat": 47.5314, "lon": 21.6269, "population": 201881},
        {"city": "Szeged", "lat": 46.2530, "lon": 20.1414, "population": 161837},
        {"city": "Miskolc", "lat": 48.1035, "lon": 20.7784, "population": 157177},
    ]
