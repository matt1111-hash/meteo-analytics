"""DTOs for weather analysis requests."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeatherAnalysisRequest(BaseModel):
    """Incoming payload for multi-city weather analysis."""

    cities: List[str] = Field(..., min_length=1, description="City names to analyze.")
    date_range: Dict[str, Any] = Field(
        ...,
        description="Date descriptor with 'date' or 'start'/'end' keys.",
    )
    metric: Optional[str] = Field(
        default="temperature_2m_max",
        description="Weather metric to analyze (temperature_2m_max, windspeed_10m_max, etc.)",
    )

    @field_validator("cities")
    @classmethod
    def validate_cities(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("Legalább egy város kötelező.")
        normalized = [v.strip() for v in value if v and v.strip()]
        if not normalized:
            raise ValueError("Üres városnevek nem engedélyezettek.")
        return normalized

    @field_validator("date_range")
    @classmethod
    def validate_date_range(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("date_range objektum kell legyen.")
        if not any(k in value for k in ("date", "start", "end")):
            raise ValueError("date_range tartalmazzon 'date' vagy 'start'/'end' kulcsot.")
        return value

    model_config = ConfigDict(frozen=True)
