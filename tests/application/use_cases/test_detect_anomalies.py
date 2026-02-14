"""Tests for DetectAnomaliesUseCase."""
from __future__ import annotations

from datetime import date

import pytest

from src.application.use_cases.detect_anomalies import DetectAnomaliesUseCase


def _default_thresholds() -> dict[str, float]:
    return {
        "temp_hot": 30.0,
        "temp_cold": -5.0,
        "precip_high": 50.0,
        "precip_low": 5.0,
        "wind_normal": 20.0,
        "wind_strong": 40.0,
        "wind_extreme": 60.0,
        "wind_hurricane": 80.0,
    }


def test_execute_returns_anomalies_for_all_categories() -> None:
    """Verify that execute coordinates all detection types."""
    weather_data = {
        "temperature_2m_max": [35.0],
        "temperature_2m_min": [15.0],
        "precipitation_sum": [60.0],
        "windspeed_10m_max": [90.0],
    }
    use_case = DetectAnomaliesUseCase(today_provider=lambda: date(2024, 1, 1))

    anomalies = use_case.execute(
        weather_data, _default_thresholds(), location_name="Budapest"
    )

    assert anomalies["temperature"] is not None
    assert anomalies["precipitation"] is not None
    assert anomalies["wind"] is not None
    assert anomalies["temperature"].category == "hot"
    assert anomalies["precipitation"].category == "heavy_rain"
    assert anomalies["wind"].category == "hurricane"
    assert anomalies["temperature"].location_name == "Budapest"


def test_execute_raises_when_threshold_missing() -> None:
    """ValueError raised if required threshold key is missing."""
    use_case = DetectAnomaliesUseCase()
    thresholds = _default_thresholds()
    thresholds.pop("temp_hot")

    with pytest.raises(ValueError, match="Hiányzó threshold kulcsok"):
        use_case.execute({}, thresholds)


def test_execute_raises_on_invalid_threshold_types() -> None:
    """ValueError raised if threshold values are not numeric."""
    use_case = DetectAnomaliesUseCase()
    thresholds = _default_thresholds()
    thresholds["temp_hot"] = "very hot"

    with pytest.raises(ValueError, match="Threshold values must be numeric"):
        use_case.execute({}, thresholds)


def test_execute_handles_missing_weather_data_gracefully() -> None:
    """None returned for categories where weather data is missing."""
    use_case = DetectAnomaliesUseCase()
    # Empty data
    anomalies = use_case.execute({}, _default_thresholds())
    assert anomalies["temperature"] is None
    assert anomalies["precipitation"] is None
    assert anomalies["wind"] is None


def test_wind_field_fallback_logic() -> None:
    """Verify priority order of wind fields."""
    thresholds = _default_thresholds()
    use_case = DetectAnomaliesUseCase()

    # wind_speed_10m_max should be first choice
    data1 = {
        "wind_speed_10m_max": [50.0],
        "wind_gusts_10m_max": [100.0],
        "windspeed_10m_max": [10.0],
    }
    res1 = use_case.execute(data1, thresholds)
    assert res1["wind"].measured_value == 50.0

    # wind_gusts_10m_max is second
    data2 = {
        "wind_gusts_10m_max": [100.0],
        "windspeed_10m_max": [10.0],
    }
    res2 = use_case.execute(data2, thresholds)
    assert res2["wind"].measured_value == 100.0

    # windspeed_10m_max is third
    data3 = {
        "windspeed_10m_max": [10.0],
    }
    res3 = use_case.execute(data3, thresholds)
    assert res3["wind"].measured_value == 10.0


def test_safe_float_list_skips_invalid_values() -> None:
    """Non-numeric values in list should be skipped."""
    use_case = DetectAnomaliesUseCase()
    # pylint: disable=protected-access
    result = use_case._safe_float_list([10.0, "invalid", None, 20.0])
    assert result == [10.0, None, 20.0]


def test_execute_requires_weather_data() -> None:
    """ValueError raised if weather_data is None."""
    use_case = DetectAnomaliesUseCase()
    with pytest.raises(ValueError, match="weather_data is required"):
        use_case.execute(None, _default_thresholds())  # type: ignore
