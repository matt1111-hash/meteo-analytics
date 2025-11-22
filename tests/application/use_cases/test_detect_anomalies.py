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
    weather_data = {
        "temperature_2m_max": [35.0],
        "temperature_2m_min": [15.0],
        "precipitation_sum": [60.0],
        "windspeed_10m_max": [90.0],
    }
    use_case = DetectAnomaliesUseCase(today_provider=lambda: date(2024, 1, 1))

    anomalies = use_case.execute(weather_data, _default_thresholds(), location_name="Budapest")

    assert anomalies["temperature"] is not None
    assert anomalies["precipitation"] is not None
    assert anomalies["wind"] is not None
    assert anomalies["temperature"].location_name == "Budapest"


def test_execute_raises_when_threshold_missing() -> None:
    use_case = DetectAnomaliesUseCase()
    thresholds = _default_thresholds()
    thresholds.pop("temp_hot")

    with pytest.raises(ValueError):
        use_case.execute({}, thresholds)
