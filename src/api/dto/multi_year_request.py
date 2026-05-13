"""DTO for multi-year batch weather request."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MultiYearBatchRequest(BaseModel):
    """Request for multi-year batch weather data."""

    city: str = Field(..., description="City name")
    years: list[int] = Field(..., min_length=1, max_length=20, description="Years to compare")
    metric: str = Field(default="temperature_2m_max", description="Weather metric")
