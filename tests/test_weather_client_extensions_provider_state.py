"""WeatherClientExtensions tesztjei."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.data.weather_client_extensions import WeatherClientExtensions


class TestSetPreferredProvider:
    """set_preferred_provider metódus tesztjei."""

    def test_set_auto_provider(self) -> None:
        client = WeatherClientExtensions()
        client.set_preferred_provider("auto")
        assert client.preferred_provider == "auto"

    def test_set_openmeteo_provider(self) -> None:
        client = WeatherClientExtensions()
        client.set_preferred_provider("open-meteo")
        assert client.preferred_provider == "open-meteo"

    def test_set_meteostat_provider(self) -> None:
        client = WeatherClientExtensions()
        client.set_preferred_provider("meteostat")
        assert client.preferred_provider == "meteostat"

    def test_set_unknown_provider_raises_error(self) -> None:
        client = WeatherClientExtensions()
        with pytest.raises(ValueError, match="Unknown provider"):
            client.set_preferred_provider("unknown_provider")


class TestGetCurrentProvider:
    """get_current_provider metódus tesztjei."""

    def test_get_current_provider_initially_none(self) -> None:
        client = WeatherClientExtensions()
        assert client.get_current_provider() is None

    def test_get_current_provider_after_request(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "_select_provider", return_value="open-meteo"):
            with patch.object(
                client,
                "_retry_weather_request",
                return_value=[{"data_source": "open-meteo"}],
            ):
                client.get_weather_data(47.4979, 19.0402, "2024-01-01", "2024-01-02")
                assert client.get_current_provider() == "open-meteo"


class TestGetAvailableProviders:
    """get_available_providers metódus tesztjei."""

    def test_get_available_providers_contains_openmeteo(self) -> None:
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        assert "open-meteo" in available

    def test_get_available_providers_excludes_invalid(self) -> None:
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        assert "meteostat" not in available

    def test_get_available_providers_returns_list(self) -> None:
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        assert isinstance(available, list)


class TestGetProviderStatus:
    """get_provider_status metódus tesztjei."""

    def test_get_provider_status_returns_dict(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert isinstance(status, dict)

    def test_get_provider_status_contains_all_providers(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert "open-meteo" in status
        assert "meteostat" in status

    def test_get_provider_status_has_required_fields(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        openmeteo_status = status["open-meteo"]
        required_fields = {
            "display_name",
            "available",
            "request_count",
            "usage_count",
            "is_current",
        }
        assert set(openmeteo_status.keys()) == required_fields

    def test_get_provider_status_openmeteo_available(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["available"] is True

    def test_get_provider_status_meteostat_unavailable_without_key(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["meteostat"]["available"] is False

    def test_get_provider_status_request_count_initial_zero(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["request_count"] == 0

    def test_get_provider_status_usage_count_initial_zero(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["usage_count"] == 0

    def test_get_provider_status_is_current_initially_false(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["is_current"] is False

    def test_get_provider_status_display_name_correct(self) -> None:
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["display_name"] == "Open-Meteo API"
        assert status["meteostat"]["display_name"] == "Meteostat API"


class TestResetProviderUsageStats:
    """reset_provider_usage_stats metódus tesztjei."""

    def test_reset_clears_usage_stats(self) -> None:
        client = WeatherClientExtensions()
        client.provider_usage_stats["open-meteo"] = 5
        client.reset_provider_usage_stats()
        assert len(client.provider_usage_stats) == 0

    def test_reset_clears_provider_request_counts(self) -> None:
        client = WeatherClientExtensions()
        client.providers["open-meteo"]._update_request_tracking()
        assert client.providers["open-meteo"].get_request_count() > 0
        client.reset_provider_usage_stats()
        assert client.providers["open-meteo"].get_request_count() == 0

    def test_reset_works_with_empty_stats(self) -> None:
        client = WeatherClientExtensions()
        client.reset_provider_usage_stats()
        assert len(client.provider_usage_stats) == 0
