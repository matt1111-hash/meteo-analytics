"""Tests for GeoUtils from geo_utils_core.py."""

from __future__ import annotations

import pytest

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import BoundingBox, DistanceUnit, GeoPoint
from src.data.geo_utils_core import GeoUtils
