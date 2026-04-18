#!/usr/bin/env python3

"""Tests for TrendAnalysisCommand — application-layer command."""

from __future__ import annotations

from src.application.commands.trend_command import TrendAnalysisCommand


def test_command_stores_fields() -> None:
    cmd = TrendAnalysisCommand(
        location="Budapest",
        metric="temperature_2m_max",
        time_periods=[5, 10, 25],
        start_date="2020-01-01",
        end_date="2024-12-31",
    )
    assert cmd.location == "Budapest"
    assert cmd.metric == "temperature_2m_max"
    assert cmd.time_periods == [5, 10, 25]
    assert cmd.start_date == "2020-01-01"
    assert cmd.end_date == "2024-12-31"


def test_command_defaults() -> None:
    cmd = TrendAnalysisCommand(
        location="Debrecen",
        metric="precipitation_sum",
        time_periods=[5],
    )
    assert cmd.start_date is None
    assert cmd.end_date is None


def test_command_is_frozen() -> None:
    cmd = TrendAnalysisCommand(
        location="Pecs",
        metric="windspeed_10m_max",
        time_periods=[10],
    )
    try:
        cmd.location = "Miskolc"  # type: ignore[misc]
        raise AssertionError("Should have raised FrozenInstanceError")
    except AttributeError:
        pass
