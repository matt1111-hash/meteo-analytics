"""Tests for ClimateAnomaly entity."""
from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities.climate_anomaly import ClimateAnomaly


def test_create_valid_temperature_anomaly() -> None:
    """Create a valid temperature anomaly and inspect flags."""
    anomaly = ClimateAnomaly(
        location_name="Budapest",
        date=date(2024, 7, 15),
        parameter="temperature",
        measured_value=42.5,
        category="hot",
        severity="error",
        message="🔥 Extrém hőség: 42.5°C",
        threshold=35.0,
        details="Maximum hőmérséklet meghaladja a 35°C küszöböt",
    )

    assert anomaly.is_extreme is True
    assert anomaly.is_normal is False
    assert "Budapest 2024-07-15" in str(anomaly)


def test_invalid_parameter_rejected() -> None:
    """Parameter must be one of the allowed domain values."""
    with pytest.raises(ValueError, match="Invalid parameter"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="invalid",
            measured_value=10.0,
            category="hot",
            severity="error",
            message="Test",
        )


def test_invalid_severity_rejected() -> None:
    """Severity must be one of the allowed domain values."""
    with pytest.raises(ValueError, match="Invalid severity"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="temperature",
            measured_value=10.0,
            category="hot",
            severity="invalid",
            message="Test",
        )


def test_negative_precipitation_rejected() -> None:
    """Precipitation anomalies cannot have negative measured values."""
    with pytest.raises(ValueError, match="Negative value not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="precipitation",
            measured_value=-1.0,
            category="drought",
            severity="warning",
            message="Test",
        )


def test_negative_wind_rejected() -> None:
    """Wind anomalies cannot have negative measured values."""
    with pytest.raises(ValueError, match="Negative value not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="wind",
            measured_value=-5.0,
            category="calm",
            severity="success",
            message="Test",
        )


def test_empty_location_rejected() -> None:
    """Location name must be provided."""
    with pytest.raises(ValueError, match="location_name must not be empty"):
        ClimateAnomaly(
            location_name="",
            date=date.today(),
            parameter="temperature",
            measured_value=20.0,
            category="normal",
            severity="success",
            message="Test",
        )


def test_normal_severity_flag() -> None:
    """Success severity sets is_normal True and is_extreme False."""
    anomaly = ClimateAnomaly(
        location_name="Szeged",
        date=date(2024, 5, 15),
        parameter="temperature",
        measured_value=24.0,
        category="normal",
        severity="success",
        message="🌡️ Normális: 24.0°C",
    )

    assert anomaly.is_normal is True
    assert anomaly.is_extreme is False
