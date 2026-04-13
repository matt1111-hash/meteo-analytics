# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
# mypy: ignore-errors
"""Split definitions from wind_rose.py."""

from __future__ import annotations

from .wind_rose_support import *


class WindRoseRequest(BaseModel):
    """Request for wind rose analysis."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")


class DirectionData(BaseModel):
    """Wind direction data with speed buckets."""

    direction: str = Field(..., description="Compass direction (N, NNE, NE, etc.)")
    angle: float = Field(..., description="Direction angle in degrees")
    speed_buckets: List[int] = Field(
        ...,
        description="Count of observations in each speed category: "
        "[0-25, 25-50, 50-70, 70-100, 100-120, 120+] km/h",
    )


class WindRoseResponse(BaseModel):
    """Wind rose analysis response."""

    city: str = Field(..., description="City name")
    start: str = Field(..., description="Start date")
    end: str = Field(..., description="End date")
    directions: List[DirectionData] = Field(
        ..., description="16 compass directions with speed data"
    )
    calms_percentage: float = Field(..., description="Percentage of calm winds (< 5 km/h)")
    total_observations: int = Field(..., description="Total number of wind observations")
    statistics: Dict[str, Any] = Field(
        ..., description="Additional statistics (avg_speed, max_speed, data_source)"
    )


# Direction configuration (16 compass points)
DIRECTION_BINS = [
    0,
    22.5,
    45,
    67.5,
    90,
    112.5,
    135,
    157.5,
    180,
    202.5,
    225,
    247.5,
    270,
    292.5,
    315,
    337.5,
    360,
]
DIRECTION_LABELS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

# Speed buckets (Beaufort-based categories)
SPEED_BINS = [0, 25, 50, 70, 100, 120, 999]  # Last bucket is 120+
SPEED_LABELS = ["0-25", "25-50", "50-70", "70-100", "100-120", "120+"]
