# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analytics_models.py."""

from __future__ import annotations

from .analytics_models_part1 import AnalyticsQuestion
from .analytics_models_part2 import AnalyticsResult, QueryResults
from .analytics_models_support import *

__all__ = ["AnalyticsQuestion", "AnalyticsResult", "QueryResults"]
