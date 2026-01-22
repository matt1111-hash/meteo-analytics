"""Tests for AnomalyThresholdSet value object."""
from __future__ import annotations

import pytest

from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet


def test_default_thresholds() -> None:
    """Defaults should match expected baseline values."""
    thresholds = AnomalyThresholdSet.default()

    assert thresholds.temp_hot == 35.0
    assert thresholds.temp_cold == -10.0
    assert thresholds.precip_high == 100.0
    assert thresholds.precip_low == 5.0
    assert thresholds.wind_hurricane == 120.0


def test_tropical_thresholds() -> None:
    """Tropical preset uses higher heat and precipitation limits."""
    thresholds = AnomalyThresholdSet.tropical()

    assert thresholds.temp_hot == 40.0
    assert thresholds.temp_cold == 10.0
    assert thresholds.precip_high == 200.0
    assert thresholds.wind_hurricane == 150.0


def test_arctic_thresholds() -> None:
    """Arctic preset uses colder and lower precipitation limits."""
    thresholds = AnomalyThresholdSet.arctic()

    assert thresholds.temp_hot == 25.0
    assert thresholds.temp_cold == -30.0
    assert thresholds.precip_high == 50.0
    assert thresholds.wind_extreme == 80.0
    assert thresholds.wind_hurricane == 100.0


def test_invalid_temperature_order_raises() -> None:
    """temp_hot must be greater than temp_cold."""
    with pytest.raises(ValueError):
        AnomalyThresholdSet(temp_hot=5.0, temp_cold=10.0)


def test_invalid_precipitation_order_raises() -> None:
    """precip_high must be greater than precip_low."""
    with pytest.raises(ValueError):
        AnomalyThresholdSet(precip_high=10.0, precip_low=50.0)


def test_invalid_wind_order_raises() -> None:
    """Wind thresholds must be strictly ascending."""
    with pytest.raises(ValueError):
        AnomalyThresholdSet(
            wind_normal=100.0,
            wind_strong=50.0,
            wind_extreme=120.0,
            wind_hurricane=150.0,
        )


def test_from_dict_applies_defaults() -> None:
    """from_dict should fill missing fields with defaults."""
    data = {"temp_hot": 40.0, "temp_cold": 5.0, "precip_high": 150.0}
    thresholds = AnomalyThresholdSet.from_dict(data)

    assert thresholds.temp_hot == 40.0
    assert thresholds.temp_cold == 5.0
    assert thresholds.precip_high == 150.0
    assert thresholds.wind_normal == 50.0


def test_to_dict_roundtrip() -> None:
    """to_dict should reflect the object's values."""
    thresholds = AnomalyThresholdSet(
        temp_hot=39.0,
        temp_cold=1.0,
        precip_high=180.0,
        precip_low=4.0,
        wind_normal=60.0,
        wind_strong=80.0,
        wind_extreme=110.0,
        wind_hurricane=140.0,
    )
    data = thresholds.to_dict()

    assert data["temp_hot"] == 39.0
    assert data["temp_cold"] == 1.0
    assert data["precip_high"] == 180.0
    assert data["precip_low"] == 4.0
    assert data["wind_normal"] == 60.0
    assert data["wind_hurricane"] == 140.0
