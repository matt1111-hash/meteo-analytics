#!/usr/bin/env python3
"""Tests for TrendAnalysisRequest validation edge cases."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.api.dto.trend_request import TrendAnalysisRequest


class TestLocationValidation:
    """Tests for location field validation."""

    def test_empty_string_location_raises_value_error(self) -> None:
        with pytest.raises(ValidationError):
            TrendAnalysisRequest(location="")

    def test_whitespace_only_location_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="A helység neve kötelező"):
            TrendAnalysisRequest(location="   ")

    def test_valid_location_passes(self) -> None:
        req = TrendAnalysisRequest(location="Budapest")
        assert req.location == "Budapest"

    def test_location_stripped(self) -> None:
        req = TrendAnalysisRequest(location="  Budapest  ")
        assert req.location == "Budapest"


class TestTimePeriodsValidation:
    """Tests for time_periods field validation."""

    def test_empty_time_periods_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="Legalább egy időszak megadása kötelező"):
            TrendAnalysisRequest(location="Budapest", time_periods=[])

    def test_all_invalid_periods_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="Érvénytelen időszak"):
            TrendAnalysisRequest(location="Budapest", time_periods=[1, 2, 3])

    def test_valid_periods_are_normalized_and_sorted(self) -> None:
        req = TrendAnalysisRequest(location="Budapest", time_periods=[55, 10, 10, 5])
        assert req.time_periods == [5, 10, 55]

    def test_mixed_valid_and_invalid_periods_filters_invalid(self) -> None:
        req = TrendAnalysisRequest(location="Budapest", time_periods=[5, 99, 25, 7])
        assert req.time_periods == [5, 25]

    def test_default_time_periods(self) -> None:
        req = TrendAnalysisRequest(location="Budapest")
        assert req.time_periods == [5, 10, 25, 55]


class TestDateFormatValidation:
    """Tests for start_date and end_date validation."""

    def test_invalid_start_date_format_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="Dátum formátum: YYYY-MM-DD"):
            TrendAnalysisRequest(location="Budapest", start_date="18-04-2026")

    def test_invalid_end_date_format_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="Dátum formátum: YYYY-MM-DD"):
            TrendAnalysisRequest(location="Budapest", end_date="2026/04/18")

    def test_valid_start_date_passes(self) -> None:
        req = TrendAnalysisRequest(location="Budapest", start_date="2020-01-01")
        assert req.start_date == "2020-01-01"

    def test_valid_end_date_passes(self) -> None:
        req = TrendAnalysisRequest(location="Budapest", end_date="2026-12-31")
        assert req.end_date == "2026-12-31"

    def test_none_dates_are_accepted(self) -> None:
        req = TrendAnalysisRequest(location="Budapest")
        assert req.start_date is None
        assert req.end_date is None

    def test_gibberish_date_raises_value_error(self) -> None:
        with pytest.raises(ValidationError, match="Dátum formátum: YYYY-MM-DD"):
            TrendAnalysisRequest(location="Budapest", start_date="not-a-date")
