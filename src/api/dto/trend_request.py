"""DTOs for trend analytics requests."""

from __future__ import annotations  # noqa: I001

from typing import List  # noqa: UP035

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.value_objects.enums import AnalyticsMetric


class TrendAnalysisRequest(BaseModel):
    """Incoming payload for trend analysis.

    Calculates linear trends over specified time periods with statistical metrics.
    """

    location: str = Field(..., min_length=1, description="City name to analyze.")
    metric: AnalyticsMetric = Field(
        default=AnalyticsMetric.TEMPERATURE_2M_MAX,
        description="Weather metric to analyze.",
    )
    time_periods: List[int] = Field(  # noqa: UP006
        default=[5, 10, 25, 55],
        description="Time periods in years (e.g., 5, 10, 25, 55).",
    )
    start_date: str | None = Field(
        default=None,
        description="Optional start date (YYYY-MM-DD). If not provided, uses available data.",
    )
    end_date: str | None = Field(
        default=None,
        description="Optional end date (YYYY-MM-DD). If not provided, uses current date.",
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:  # noqa: D102
        if not value or not value.strip():
            raise ValueError("A helység neve kötelező.")
        return value.strip()

    @field_validator("time_periods")
    @classmethod
    def validate_time_periods(cls, value: List[int]) -> List[int]:  # noqa: D102, UP006
        if not value:
            raise ValueError("Legalább egy időszak megadása kötelező.")
        valid_periods = {5, 10, 25, 55}
        normalized = [p for p in value if p in valid_periods]
        if not normalized:
            raise ValueError(f"Érvénytelen időszak. Engedélyezett: {valid_periods}")
        return sorted(set(normalized))

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, value: str | None) -> str | None:  # noqa: D102
        if value is None:
            return None
        try:
            from datetime import datetime  # noqa: PLC0415

            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError as exc:
            raise ValueError("Dátum formátum: YYYY-MM-DD") from exc

    model_config = ConfigDict(frozen=True)
