"""DTOs for weather analysis requests."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List  # noqa: UP035

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.config.config_settings import RequestLimits

_MAX_CITIES = RequestLimits.MAX_CITIES_PER_REQUEST
_MAX_DATE_RANGE_DAYS = RequestLimits.MAX_DATE_RANGE_DAYS
_DATE_FORMAT = RequestLimits.DATE_FORMAT


def _normalize_city_names(value: List[str]) -> List[str]:  # noqa: UP006
    """Strip empty city names from the payload."""
    return [city.strip() for city in value if city and city.strip()]


def _has_supported_date_keys(value: Dict[str, Any]) -> bool:  # noqa: UP006
    """Return whether the date range contains supported keys."""
    return any(key in value for key in ("date", "start", "end"))


def validate_iso_date(value: str) -> str:
    """Validate an ISO ``YYYY-MM-DD`` date string and return it unchanged.

    Raises ``ValueError`` (→ HTTP 422 at the API boundary) on malformed input,
    so invalid dates never reach the provider/fetch layer.
    """
    try:
        datetime.strptime(value, _DATE_FORMAT)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Érvénytelen dátum: {value!r} (várva YYYY-MM-DD).") from exc
    return value


def validate_date_span(start: str, end: str) -> None:
    """Validate ordering and bounded span of a ``start``/``end`` date pair.

    Rejects inverted ranges and spans exceeding ``MAX_DATE_RANGE_DAYS`` to keep
    a single request from fanning out into thousands of provider calls.
    """
    start_dt = datetime.strptime(start, _DATE_FORMAT)
    end_dt = datetime.strptime(end, _DATE_FORMAT)
    if start_dt > end_dt:
        raise ValueError("A kezdő dátum nem lehet későbbi a végdátumnál.")
    span_days = (end_dt - start_dt).days
    if span_days > _MAX_DATE_RANGE_DAYS:
        raise ValueError(
            f"A dátumtartomány túl nagy: {span_days} nap "
            f"(maximum {_MAX_DATE_RANGE_DAYS} nap / ~5 év)."
        )


class WeatherAnalysisRequest(BaseModel):
    """Incoming payload for multi-city weather analysis."""

    cities: List[str] = Field(  # noqa: UP006
        ...,
        min_length=1,
        max_length=_MAX_CITIES,
        description="City names to analyze.",
    )
    date_range: Dict[str, Any] = Field(  # noqa: UP006
        ...,
        description="Date descriptor with 'date' or 'start'/'end' keys.",
    )
    metric: str | None = Field(
        default="temperature_2m_max",
        description="Weather metric to analyze (temperature_2m_max, windspeed_10m_max, etc.)",
    )

    @field_validator("cities")
    @classmethod
    def validate_cities(cls, value: List[str]) -> List[str]:  # noqa: D102, UP006
        if not value:
            raise ValueError("Legalább egy város kötelező.")
        normalized = _normalize_city_names(value)
        if not normalized:
            raise ValueError("Üres városnevek nem engedélyezettek.")
        if len(normalized) > _MAX_CITIES:
            raise ValueError(
                f"Túl sok város: {len(normalized)} (maximum {_MAX_CITIES} város/kérés)."
            )
        return normalized

    @field_validator("date_range")
    @classmethod
    def validate_date_range(cls, value: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D102, UP006
        if not isinstance(value, dict):
            raise ValueError("date_range objektum kell legyen.")
        if not _has_supported_date_keys(value):
            raise ValueError("date_range tartalmazzon 'date' vagy 'start'/'end' kulcsot.")
        # Validate every present date field. The adapter prefers a `date` field
        # over start/end, so `date` must be validated even when a range is also
        # present — otherwise a malformed `date` slips past the API boundary.
        date_value = value.get("date")
        start = value.get("start")
        end = value.get("end")
        if date_value:
            validate_iso_date(str(date_value))
        if start:
            validate_iso_date(str(start))
        if end:
            validate_iso_date(str(end))
        if start and end:
            validate_date_span(str(start), str(end))
        return value

    model_config = ConfigDict(frozen=True)
