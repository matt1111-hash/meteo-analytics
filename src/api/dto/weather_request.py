"""DTOs for weather analysis requests."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class WeatherAnalysisRequest(BaseModel):
    """Incoming payload for multi-city weather analysis."""

    cities: List[str] = Field(..., min_length=1, description="City names to analyze.")
    date_range: Dict[str, Any] = Field(
        ...,
        description="Date descriptor with 'date' or 'start'/'end' keys.",
    )

    @validator("cities")
    def validate_cities(cls, values: List[str]) -> List[str]:
        if not values:
            raise ValueError("Legalább egy város kötelező.")
        normalized = [v.strip() for v in values if v and v.strip()]
        if not normalized:
            raise ValueError("Üres városnevek nem engedélyezettek.")
        return normalized

    @validator("date_range")
    def validate_date_range(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("date_range objektum kell legyen.")
        if not any(k in value for k in ("date", "start", "end")):
            raise ValueError("date_range tartalmazzon 'date' vagy 'start'/'end' kulcsot.")
        return value

    class Config:
        """Pydantic config."""

        allow_mutation = False
        frozen = True
