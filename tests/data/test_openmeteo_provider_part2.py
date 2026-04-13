"""Tests split from test_openmeteo_provider.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_openmeteo_provider_support import *


class TestGetWeatherDataBatched:
    """Test get_weather_data_batched method."""

    def test_get_weather_data_batched_creates_correct_batches(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched creates 90-day batches correctly."""
        # 180 days = 2 batches
        batch1_data = [{"date": "2020-01-01", "temperature_2m_max": 10.0}]
        batch2_data = [{"date": "2020-03-31", "temperature_2m_max": 15.0}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1_data, batch2_data]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            assert mock_single.call_count == 2
            assert len(result) == 2

    def test_get_weather_data_batched_handles_365_day_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched handles full year with correct batch count."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-12-31")

            # 365 days / 89 days per batch + 1 = ~5 batches (since max-1=89)
            # Jan 1 - Mar 30 (90 days), Mar 31 - Jun 28 (90 days), Jun 29 - Sep 26 (90 days), Sep 27 - Dec 25 (90 days), Dec 26 - Dec 31 (6 days)
            assert provider.get_weather_data_single.call_count == 5

    def test_get_weather_data_batched_sleeps_between_batches(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched sleeps between batches except last."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            with patch("time.sleep") as mock_sleep:
                provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-12-31")

                # 5 batches, 4 sleeps between them
                assert mock_sleep.call_count == 4

    def test_get_weather_data_batched_continues_on_weather_api_error(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched continues when one batch fails with WeatherAPIError."""
        with patch.object(provider, "get_weather_data_single") as mock_single:
            # First batch fails, second succeeds
            mock_single.side_effect = [
                WeatherAPIError("API error"),
                [{"date": "2020-03-31", "temperature_2m_max": 15.0}],
            ]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            # Should return only second batch data
            assert len(result) == 1
            assert result[0]["date"] == "2020-03-31"

    def test_get_weather_data_batched_returns_sorted_results(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched returns results sorted by date."""
        batch1 = [{"date": "2020-03-31"}]
        batch2 = [{"date": "2020-01-01"}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1, batch2]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            assert result[0]["date"] == "2020-01-01"
            assert result[1]["date"] == "2020-03-31"


class TestGenerateBatches:
    """Test _generate_batches method."""

    def test_generate_batches_creates_single_batch_for_short_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates single batch for period < 90 days."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 30)  # 89 days < 90

        batches = provider._generate_batches(start, end)

        assert len(batches) == 1
        assert batches[0][0] == start
        assert batches[0][1] == end

    def test_generate_batches_creates_multiple_batches_for_long_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates multiple 90-day batches."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)  # 365 days

        batches = provider._generate_batches(start, end)

        # 365 days requires 5 batches (max_days_per_request - 1 = 89 days per batch)
        assert len(batches) == 5

        # Check first batch: Jan 1 - Mar 30 (90 days inclusive, using timedelta(days=89))
        assert batches[0][0] == datetime(2020, 1, 1)
        assert batches[0][1] == datetime(2020, 3, 30)

    def test_generate_batches_handles_exact_90_day_multiple(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches handles exact 90-day period correctly."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 30)  # 89 days from Jan 1 (within 90-day limit)

        batches = provider._generate_batches(start, end)

        assert len(batches) == 1

    def test_generate_batches_creates_correct_overlap_free_intervals(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates non-overlapping intervals."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 31)  # 90 days = 2 batches

        batches = provider._generate_batches(start, end)

        assert len(batches) == 2

        # First batch: Jan 1 - Mar 30 (89 days using timedelta)
        assert batches[0][0] == datetime(2020, 1, 1)
        assert batches[0][1] == datetime(2020, 3, 30)

        # Second batch: Mar 31 - Mar 31 (1 day)
        assert batches[1][0] == datetime(2020, 3, 31)
        assert batches[1][1] == datetime(2020, 3, 31)
