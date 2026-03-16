# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analytics_transform_service.py."""

from __future__ import annotations

from .analytics_transform_service_part1 import AnalyticsTransformServicePart1Mixin
from .analytics_transform_service_part2 import AnalyticsTransformServicePart2Mixin
from .analytics_transform_service_part3 import AnalyticsTransformServicePart3Mixin
from .analytics_transform_service_support import *


class AnalyticsTransformService(
    AnalyticsTransformServicePart1Mixin,
    AnalyticsTransformServicePart2Mixin,
    AnalyticsTransformServicePart3Mixin,
):
    """Handle weather result transformation, sorting, and statistics."""
