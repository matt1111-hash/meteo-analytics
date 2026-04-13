"""Tests for the wind rose API route."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from src.api.routes import wind_rose


def test_process_wind_rose_data_prefers_gusts_and_filters_invalid_rows() -> None:
    """Wind rose processing should use gust data when present."""
    daily_data = {
        "time": ["2026-03-01", "2026-03-02", "2026-03-03"],
        "winddirection_10m_dominant": [10.0, 40.0, None],
        "wind_gusts_10m_max": [12.0, 35.0, 50.0],
        "windspeed_10m_max": [8.0, 20.0, 25.0],
    }

    result = wind_rose._process_wind_rose_data(daily_data)

    assert result["total_observations"] == 2
    assert result["statistics"]["data_source"] == "wind_gusts_max"
    assert result["statistics"]["calms_count"] == 0
    assert result["directions"][0]["direction"] == "N"
    assert result["directions"][0]["speed_buckets"][0] == 1
    assert result["directions"][1]["direction"] == "NNE"
    assert result["directions"][1]["speed_buckets"][1] == 1


def test_process_wind_rose_data_raises_without_valid_speed_data() -> None:
    """Wind rose processing should reject payloads without valid speeds."""
    daily_data = {
        "time": ["2026-03-01"],
        "winddirection_10m_dominant": [45.0],
        "wind_gusts_10m_max": ["bad"],
        "windspeed_10m_max": [None],
    }

    with pytest.raises(HTTPException, match="No valid wind speed data available"):
        wind_rose._process_wind_rose_data(daily_data)


def test_process_wind_rose_data_falls_back_to_windspeed_and_counts_calms() -> None:
    """Processing should use windspeed when gust data is unusable."""
    daily_data = {
        "time": ["2026-03-01", "2026-03-02", "2026-03-03"],
        "winddirection_10m_dominant": [0.0, 200.0, 350.0],
        "wind_gusts_10m_max": ["bad", None, "bad"],
        "windspeed_10m_max": [2.0, 130.0, 80.0],
    }

    result = wind_rose._process_wind_rose_data(daily_data)

    assert result["statistics"]["data_source"] == "windspeed_10m_max"
    assert result["statistics"]["calms_count"] == 1
    assert result["calms_percentage"] == 33.3
    assert result["directions"][0]["speed_buckets"][0] == 1
    assert result["directions"][8]["speed_buckets"][-1] == 1


def test_process_wind_rose_data_rejects_missing_dates_or_direction() -> None:
    """Missing dates or direction data should raise a 400 error."""
    with pytest.raises(HTTPException, match="Missing required data"):
        wind_rose._process_wind_rose_data({"time": [], "winddirection_10m_dominant": []})


def test_process_wind_rose_data_rejects_when_all_rows_filtered_out() -> None:
    """All-invalid rows should raise a no valid data error."""
    daily_data = {
        "time": ["2026-03-01", "2026-03-02"],
        "winddirection_10m_dominant": [-5.0, "bad"],
        "windspeed_10m_max": [10.0, 20.0],
    }

    with pytest.raises(HTTPException, match="No valid wind data after filtering"):
        wind_rose._process_wind_rose_data(daily_data)
