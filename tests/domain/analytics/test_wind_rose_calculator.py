#!/usr/bin/env python3

"""Tests for WindRoseCalculator domain service."""

from __future__ import annotations

import pytest
from src.domain.analytics.services.wind_rose_calculator import WindRoseCalculator


def _sample_daily_data() -> dict:
    return {
        "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "winddirection_10m_dominant": [180.0, 270.0, 45.0],
        "wind_gusts_10m_max": [30.0, 60.0, 10.0],
        "windspeed_10m_max": [20.0, 40.0, 5.0],
    }


def test_calculate_returns_directions_and_statistics() -> None:
    result = WindRoseCalculator().calculate(_sample_daily_data())
    assert "directions" in result
    assert len(result["directions"]) == 16
    assert "calms_percentage" in result
    assert "total_observations" in result
    assert result["total_observations"] == 3


def test_calculate_raises_on_missing_dates() -> None:
    with pytest.raises(ValueError, match="Missing required data"):
        WindRoseCalculator().calculate({"winddirection_10m_dominant": [180.0]})


def test_calculate_raises_on_missing_direction() -> None:
    with pytest.raises(ValueError, match="Missing required data"):
        WindRoseCalculator().calculate({"time": ["2024-01-01"]})


def test_calculate_raises_on_no_wind_speed() -> None:
    data = {
        "time": ["2024-01-01"],
        "winddirection_10m_dominant": [180.0],
        "wind_gusts_10m_max": [None],
        "windspeed_10m_max": [None],
    }
    with pytest.raises(ValueError, match="No valid wind speed"):
        WindRoseCalculator().calculate(data)


def test_calculate_raises_on_no_valid_paired_data() -> None:
    data = {
        "time": ["2024-01-01"],
        "winddirection_10m_dominant": [999.0],
        "wind_gusts_10m_max": [30.0],
    }
    with pytest.raises(ValueError, match="No valid wind data"):
        WindRoseCalculator().calculate(data)


def test_calculate_uses_gusts_when_available() -> None:
    result = WindRoseCalculator().calculate(_sample_daily_data())
    assert result["statistics"]["data_source"] == "wind_gusts_max"


def test_calculate_falls_back_to_windspeed() -> None:
    data = {
        "time": ["2024-01-01"],
        "winddirection_10m_dominant": [180.0],
        "wind_gusts_10m_max": [None],
        "windspeed_10m_max": [30.0],
    }
    result = WindRoseCalculator().calculate(data)
    assert result["statistics"]["data_source"] == "windspeed_10m_max"
