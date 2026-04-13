# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
"""Analytics models domain entities."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from src.domain.entities.weather import AnomalyResult, CityWeatherResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataSource,
    QuestionType,
    RegionScope,
)
