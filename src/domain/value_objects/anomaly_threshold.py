"""Value object for anomaly detection thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnomalyThresholdSet:  # pylint: disable=too-many-instance-attributes
    """Immutable threshold set with self-validation and helpers."""

    temp_hot: float = 35.0
    temp_cold: float = -10.0
    precip_high: float = 100.0
    precip_low: float = 5.0
    wind_normal: float = 50.0
    wind_strong: float = 70.0
    wind_extreme: float = 100.0
    wind_hurricane: float = 120.0

    def __post_init__(self) -> None:
        """Validate ordering and reasonable bounds."""
        self._validate_temperature_thresholds()
        self._validate_precipitation_thresholds()
        self._validate_wind_thresholds()

    def _validate_temperature_thresholds(self) -> None:
        """Validate temperature threshold ordering and ranges."""
        if self.temp_hot <= self.temp_cold:
            raise ValueError(
                f"temp_hot ({self.temp_hot}) must be greater than temp_cold ({self.temp_cold})"
            )
        if self.temp_cold < -50.0 or self.temp_cold > 40.0:  # noqa: PLR2004
            raise ValueError("temp_cold must be between -50 and 40")
        if self.temp_hot < -50.0 or self.temp_hot > 60.0:  # noqa: PLR2004
            raise ValueError("temp_hot must be between -50 and 60")

    def _validate_precipitation_thresholds(self) -> None:
        """Validate precipitation threshold ordering and ranges."""
        if self.precip_high <= self.precip_low:
            raise ValueError(
                f"precip_high ({self.precip_high}) must be greater than "
                f"precip_low ({self.precip_low})"
            )
        if self.precip_low < 0.0 or self.precip_low > 100.0:  # noqa: PLR2004
            raise ValueError("precip_low must be between 0 and 100 mm/day")
        if self.precip_high < 10.0 or self.precip_high > 500.0:  # noqa: PLR2004
            raise ValueError("precip_high must be between 10 and 500 mm/day")

    def _validate_wind_thresholds(self) -> None:
        """Validate wind threshold ordering and ranges."""
        wind_values = self._wind_values()
        if wind_values != sorted(wind_values):
            raise ValueError("Wind thresholds must be in ascending order")
        for wind_value in wind_values:
            if wind_value < 5.0 or wind_value > 300.0:  # noqa: PLR2004
                raise ValueError("Wind thresholds must be between 5 and 300 km/h")

    def _wind_values(self) -> list[float]:
        """Return wind threshold list in severity order."""
        return [
            self.wind_normal,
            self.wind_strong,
            self.wind_extreme,
            self.wind_hurricane,
        ]

    @classmethod
    def default(cls) -> AnomalyThresholdSet:
        """Return default continental thresholds."""
        return cls()

    @classmethod
    def tropical(cls) -> AnomalyThresholdSet:
        """Return thresholds tuned for tropical climates."""
        return cls(
            temp_hot=40.0,
            temp_cold=10.0,
            precip_high=200.0,
            precip_low=2.0,
            wind_hurricane=150.0,
        )

    @classmethod
    def arctic(cls) -> AnomalyThresholdSet:
        """Return thresholds tuned for arctic climates."""
        return cls(
            temp_hot=25.0,
            temp_cold=-30.0,
            precip_high=50.0,
            precip_low=1.0,
            wind_extreme=80.0,
            wind_hurricane=100.0,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyThresholdSet:
        """Construct from dictionary data with sane defaults."""
        return cls(
            temp_hot=float(data.get("temp_hot", 35.0)),
            temp_cold=float(data.get("temp_cold", -10.0)),
            precip_high=float(data.get("precip_high", 100.0)),
            precip_low=float(data.get("precip_low", 5.0)),
            wind_normal=float(data.get("wind_normal", 50.0)),
            wind_strong=float(data.get("wind_strong", 70.0)),
            wind_extreme=float(data.get("wind_extreme", 100.0)),
            wind_hurricane=float(data.get("wind_hurricane", 120.0)),
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to plain dictionary for persistence/serialization."""
        return {
            "temp_hot": self.temp_hot,
            "temp_cold": self.temp_cold,
            "precip_high": self.precip_high,
            "precip_low": self.precip_low,
            "wind_normal": self.wind_normal,
            "wind_strong": self.wind_strong,
            "wind_extreme": self.wind_extreme,
            "wind_hurricane": self.wind_hurricane,
        }
