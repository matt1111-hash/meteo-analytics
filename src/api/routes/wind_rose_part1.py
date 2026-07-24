# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
"""Split definitions from wind_rose.py."""

from __future__ import annotations

from pydantic import field_validator, model_validator
from src.api.dto.weather_request import validate_date_span, validate_iso_date

from .wind_rose_support import *


class WindRoseRequest(BaseModel):
    """Request for wind rose analysis."""

    city: str = Field(..., min_length=1, description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")

    @field_validator("start", "end")
    @classmethod
    def _check_date_format(cls, value: str) -> str:
        return validate_iso_date(value)

    @model_validator(mode="after")
    def _check_date_span(self) -> WindRoseRequest:
        validate_date_span(self.start, self.end)
        return self


class DirectionData(BaseModel):
    """Wind direction data with speed buckets."""

    direction: str = Field(..., description="Compass direction (N, NNE, NE, etc.)")
    angle: float = Field(..., description="Direction angle in degrees")
    speed_buckets: List[int] = Field(
        ...,
        max_length=10,
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
