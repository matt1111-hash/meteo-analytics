"""Domain entity representing a detected weather anomaly."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


_VALID_PARAMETERS = {"temperature", "precipitation", "wind"}
_VALID_SEVERITIES = {"success", "warning", "error", "disabled"}


@dataclass(frozen=True)
class ClimateAnomaly:  # pylint: disable=too-many-instance-attributes
    """Immutable anomaly record with basic validation and convenience flags."""

    location_name: str
    date: date
    parameter: str  # "temperature" | "precipitation" | "wind"
    measured_value: float
    category: str
    severity: str  # "success" | "warning" | "error" | "disabled"
    message: str
    threshold: Optional[float] = None
    details: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate required business rules for anomalies."""
        if not self.location_name:
            raise ValueError("location_name must not be empty")

        if not isinstance(self.date, date):
            raise TypeError("date must be a datetime.date instance")

        if self.parameter not in _VALID_PARAMETERS:
            raise ValueError(f"Invalid parameter: {self.parameter}")

        if self.severity not in _VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")

        if (
            self.parameter in {"precipitation", "wind"}
            and self.measured_value < 0
        ):
            raise ValueError(
                f"Negative value not allowed for {self.parameter}"
            )

    @property
    def is_extreme(self) -> bool:
        """Return True if anomaly is extreme (error severity)."""
        return self.severity == "error"

    @property
    def is_normal(self) -> bool:
        """Return True if anomaly severity is success."""
        return self.severity == "success"

    def __str__(self) -> str:
        """Compact human string representation."""
        return f"{self.location_name} {self.date}: {self.message}"
