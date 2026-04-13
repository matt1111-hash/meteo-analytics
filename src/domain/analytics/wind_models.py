"""Wind analysis models and constants."""

from __future__ import annotations

import dataclasses
import datetime
from typing import TypedDict

# Konstansok
WINDY_DAY_THRESHOLD_KMH = 43.0
MONTHS_HU = [
    "Január",
    "Február",
    "Március",
    "Április",
    "Május",
    "Június",
    "Július",
    "Augusztus",
    "Szeptember",
    "Október",
    "November",
    "December",
]


@dataclasses.dataclass
class WindyDayStats:
    """Szeles nap statisztikák egy hónapra."""

    year: int
    month: int
    month_name: str
    windy_days_count: int
    total_days: int
    windy_percentage: float
    max_wind_speed: float
    avg_wind_speed: float
    windy_days_list: list[datetime.date]


@dataclasses.dataclass
class WindAnalysisResult:
    """Teljes szél analízis eredmény."""

    location_name: str
    analysis_period: tuple[datetime.date, datetime.date]
    threshold_kmh: float
    monthly_stats: list[WindyDayStats]
    total_windy_days: int
    total_days: int
    overall_windy_percentage: float
    windiest_month: WindyDayStats | None
    calmest_month: WindyDayStats | None


class WindChartData(TypedDict):
    """Chart adatstruktúra havi szeles napokhoz."""

    months: list[str]
    counts: list[int]
    percentages: list[float]
    labels: list[str]
