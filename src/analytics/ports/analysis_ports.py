"""Analysis-specific ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WindAnalysisResult:
    """Result of wind analysis."""

    windy_days_count: int
    total_days: int
    windy_percentage: float
    max_wind_speed: float
    max_wind_date: str | None
    avg_wind_speed: float
    data: list[dict[str, Any]]
    threshold: float
