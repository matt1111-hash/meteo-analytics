# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
"""Transform and statistics service for analytics results."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Optional

from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.statistics import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_stdev,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope

logger = logging.getLogger(__name__)
