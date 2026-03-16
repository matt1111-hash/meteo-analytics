#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
GUI wrapper around domain anomaly detection, backward-compatible interface.
"""

from __future__ import annotations

# pylint: disable=import-error
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from src.presentation.gui.utils import AnomalyConstants

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Backward-compatible anomaly result for GUI usage."""

    category: str
    message: str
    status: str  # 'success' | 'warning' | 'error' | 'disabled'
    value: Optional[float] = None
    threshold: Optional[float] = None
    details: Optional[str] = None


class AnomalySettingsProvider:
    """Provides dynamic anomaly thresholds with validation."""

    def __init__(self, initial_settings: Optional[Dict[str, Any]] = None):
        self._settings = initial_settings or self._default_settings()
        self._validate_settings()
        logger.debug("AnomalySettingsProvider initialized")

    def _default_settings(self) -> Dict[str, Any]:
        """Return baseline thresholds for anomalies."""
        return {
            "temp_hot": AnomalyConstants.TEMP_HOT_THRESHOLD,
            "temp_cold": AnomalyConstants.TEMP_COLD_THRESHOLD,
            "precip_high": AnomalyConstants.PRECIP_HIGH_THRESHOLD,
            "precip_low": AnomalyConstants.PRECIP_LOW_THRESHOLD,
            "wind_normal": 50.0,
            "wind_strong": 70.0,
            "wind_extreme": 100.0,
            "wind_hurricane": 120.0,
        }

    def _validate_settings(self) -> None:
        """Fill missing keys with defaults."""
        defaults = self._default_settings()
        for key, default_value in defaults.items():
            if key not in self._settings:
                self._settings[key] = default_value
                logger.warning(
                    "Missing setting filled: %s=%s",
                    key,
                    default_value,
                )

    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """Merge and validate new threshold settings."""
        self._settings.update(new_settings)
        self._validate_settings()
        logger.info("Settings updated (%d keys)", len(new_settings))

    def to_threshold_config(self) -> Dict[str, float]:
        """Return thresholds as numeric dictionary."""
        return {
            "temp_hot": float(self._settings["temp_hot"]),
            "temp_cold": float(self._settings["temp_cold"]),
            "precip_high": float(self._settings["precip_high"]),
            "precip_low": float(self._settings["precip_low"]),
            "wind_normal": float(self._settings["wind_normal"]),
            "wind_strong": float(self._settings["wind_strong"]),
            "wind_extreme": float(self._settings["wind_extreme"]),
            "wind_hurricane": float(self._settings["wind_hurricane"]),
        }

    def get_all_settings(self) -> Dict[str, Any]:
        """Return a shallow copy of current settings."""
        return self._settings.copy()


class AnomalyDetector:
    """GUI-facing wrapper that delegates to the domain anomaly detector."""

    def __init__(
        self,
        settings_provider: Optional[AnomalySettingsProvider] = None,
    ):
        self.settings_provider = settings_provider or AnomalySettingsProvider()
        self.use_case = DetectAnomaliesUseCase()
        logger.info("AnomalyDetector wrapper initialized (domain-backed)")

    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """Update thresholds and keep wrapper in sync."""
        self.settings_provider.update_settings(new_settings)

    def detect_all_anomalies(
        self,
        daily_data: Dict[str, List],
    ) -> List[AnomalyResult]:
        """Run domain anomaly detection and return GUI-friendly results."""
        thresholds = self.settings_provider.to_threshold_config()
        anomalies = self.use_case.execute(daily_data, thresholds)

        results: List[AnomalyResult] = []
        results.append(
            self._convert_anomaly(
                "temperature",
                anomalies.get("temperature"),
                "🌡️ Hőmérséklet: Nincs vagy érvénytelen adat",
            )
        )
        results.append(
            self._convert_anomaly(
                "precipitation",
                anomalies.get("precipitation"),
                "🌧️ Csapadék: Nincs vagy érvénytelen adat",
            )
        )
        results.append(
            self._convert_anomaly(
                "wind",
                anomalies.get("wind"),
                "🌪️ Szél: Nincs vagy érvénytelen adat",
            )
        )

        logger.debug("Anomaly detection completed: %d result(s)", len(results))
        return [res for res in results if res is not None]

    def _convert_anomaly(
        self,
        category: str,
        anomaly: Optional[Any],
        disabled_message: str,
    ) -> Optional[AnomalyResult]:
        if anomaly is None:
            return _disabled(category, disabled_message)

        return AnomalyResult(
            category=category,
            message=anomaly.message,
            status=anomaly.severity,
            value=anomaly.measured_value,
            threshold=anomaly.threshold,
            details=anomaly.details,
        )


def _disabled(category: str, message: str) -> AnomalyResult:
    """Helper for disabled/no-data scenarios."""
    return AnomalyResult(category=category, message=message, status="disabled")


def create_anomaly_detector_with_settings(
    settings: Optional[Dict[str, Any]] = None,
) -> AnomalyDetector:
    """Factory retained for backward compatibility."""
    settings_provider = AnomalySettingsProvider(settings)
    return AnomalyDetector(settings_provider)


def demo_dynamic_anomaly_detection() -> None:
    """Simple demonstration for manual runs."""
    sample = {
        "temperature_2m_max": [42.5, 38.2, 45.1, 39.8],
        "temperature_2m_min": [25.1, 22.3, 28.4, 24.7],
        "precipitation_sum": [0.0, 125.5, 2.1, 0.5],
        "wind_speed_10m_max": [15.2, 85.3, 25.1, 45.8],
    }
    detector = AnomalyDetector()
    for res in detector.detect_all_anomalies(sample):
        print(f"{res.category}: {res.message} ({res.status})")


if __name__ == "__main__":
    demo_dynamic_anomaly_detection()
