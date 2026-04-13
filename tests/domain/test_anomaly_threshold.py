"""Tests for AnomalyThresholdSet value object."""

from __future__ import annotations

import pytest
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet


def test_default_thresholds() -> None:
    """Default constructor uses continental standard values."""
    ts = AnomalyThresholdSet()
    assert ts.temp_hot == 35.0
    assert ts.temp_cold == -10.0
    assert ts.precip_high == 100.0
    assert ts.precip_low == 5.0
    assert ts.wind_hurricane == 120.0


def test_tropical_thresholds() -> None:
    """Tropical helper uses higher heat and precip bounds."""
    ts = AnomalyThresholdSet.tropical()
    assert ts.temp_hot == 40.0
    assert ts.precip_high == 200.0


def test_arctic_thresholds() -> None:
    """Arctic helper uses much lower cold bounds."""
    ts = AnomalyThresholdSet.arctic()
    assert ts.temp_cold == -30.0
    assert ts.temp_hot == 25.0


def test_invalid_temperature_order_raises() -> None:
    """ValueError raised if hot <= cold."""
    with pytest.raises(ValueError, match="must be greater than"):
        AnomalyThresholdSet(temp_hot=10.0, temp_cold=20.0)


def test_invalid_temperature_bounds_raises() -> None:
    """ValueError raised if temperatures out of reasonable bounds."""
    with pytest.raises(ValueError, match="temp_cold must be between"):
        AnomalyThresholdSet(temp_cold=-60.0)
    with pytest.raises(ValueError, match="temp_cold must be between"):
        # temp_hot must be > temp_cold to reach boundary check
        AnomalyThresholdSet(temp_cold=45.0, temp_hot=50.0)
    with pytest.raises(ValueError, match="temp_hot must be between"):
        # temp_hot default is 35, so temp_hot=70 is enough
        AnomalyThresholdSet(temp_hot=70.0)


def test_invalid_precipitation_order_raises() -> None:
    """ValueError raised if high <= low."""
    with pytest.raises(ValueError, match="must be greater than"):
        AnomalyThresholdSet(precip_high=5.0, precip_low=10.0)


def test_invalid_precipitation_bounds_raises() -> None:
    """ValueError raised if precipitation out of reasonable bounds."""
    with pytest.raises(ValueError, match="precip_low must be between"):
        AnomalyThresholdSet(precip_low=-1.0)
    with pytest.raises(ValueError, match="precip_low must be between"):
        # precip_high must be > precip_low to reach boundary check
        AnomalyThresholdSet(precip_low=110.0, precip_high=150.0)
    with pytest.raises(ValueError, match="precip_high must be between"):
        # precip_low must be < precip_high to reach boundary check
        AnomalyThresholdSet(precip_high=5.0, precip_low=2.0)
    with pytest.raises(ValueError, match="precip_high must be between"):
        AnomalyThresholdSet(precip_high=600.0)


def test_invalid_wind_order_raises() -> None:
    """ValueError raised if wind thresholds not ascending."""
    with pytest.raises(ValueError, match="ascending order"):
        AnomalyThresholdSet(wind_strong=100.0, wind_extreme=80.0)


def test_invalid_wind_bounds_raises() -> None:
    """ValueError raised if wind speed out of reasonable bounds."""
    with pytest.raises(ValueError, match="between 5 and 300"):
        AnomalyThresholdSet(wind_normal=2.0)
    with pytest.raises(ValueError, match="between 5 and 300"):
        AnomalyThresholdSet(wind_hurricane=350.0)


def test_from_dict_applies_defaults() -> None:
    """Constructor from dict handles missing keys."""
    ts = AnomalyThresholdSet.from_dict({"temp_hot": 42.0})
    assert ts.temp_hot == 42.0
    assert ts.temp_cold == -10.0  # default


def test_to_dict_roundtrip() -> None:
    """to_dict produces dictionary that can recreate object."""
    ts = AnomalyThresholdSet(temp_hot=38.0, wind_hurricane=150.0)
    data = ts.to_dict()
    ts2 = AnomalyThresholdSet.from_dict(data)
    assert ts == ts2
