"""Comprehensive tests for src/config/api_config.py."""

from __future__ import annotations

import pytest


class TestValidateApiKeys:
    """Test cases for validate_api_keys() function."""

    def test_no_meteostat_key_returns_not_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When Meteostat API key is not set, validation should reflect that."""
        from src.config.api_config import APIConfig, validate_api_keys

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        result = validate_api_keys()

        assert result["meteostat_key_present"] is False
        assert result["meteostat_key_valid"] is False
        assert result["openmeteo_available"] is True

    def test_short_meteostat_key_returns_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Short Meteostat API key should be marked as invalid."""
        from src.config.api_config import APIConfig, validate_api_keys

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "short_key")
        result = validate_api_keys()

        assert result["meteostat_key_present"] is True
        assert result["meteostat_key_valid"] is False

    def test_valid_meteostat_key_returns_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Valid length Meteostat API key should pass validation."""
        from src.config.api_config import APIConfig, validate_api_keys

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        result = validate_api_keys()

        assert result["meteostat_key_present"] is True
        assert result["meteostat_key_valid"] is True

    def test_meteostat_key_with_whitespace_strips_before_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat API key with surrounding whitespace should be stripped."""
        from src.config.api_config import APIConfig, validate_api_keys

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "  " + "a" * 32 + "  ")
        result = validate_api_keys()

        assert result["meteostat_key_present"] is True
        assert result["meteostat_key_valid"] is True

    def test_openmeteo_always_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Open-Meteo should always be available regardless of API key status."""
        from src.config.api_config import APIConfig, validate_api_keys

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        result_no_key = validate_api_keys()
        assert result_no_key["openmeteo_available"] is True

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        result_with_key = validate_api_keys()
        assert result_with_key["openmeteo_available"] is True


class TestGetActiveDataSources:
    """Test cases for get_active_data_sources() function."""

    def test_always_returns_open_meteo(self) -> None:
        """Open-Meteo should always be in active sources."""
        from src.config.api_config import get_active_data_sources

        sources = get_active_data_sources()

        assert "open-meteo" in sources
        assert sources["open-meteo"]["name"] == "Open-Meteo API"
        assert sources["open-meteo"]["type"] == "free"
        assert sources["open-meteo"]["status"] == "active"

    def test_open_meteo_properties(self) -> None:
        """Open-Meteo source properties should be correctly defined."""
        from src.config.api_config import get_active_data_sources

        sources = get_active_data_sources()
        open_meteo = sources["open-meteo"]

        assert open_meteo["rate_limit"] == "10 requests/second"
        assert open_meteo["cost"] == "Free"
        assert set(open_meteo["use_cases"]) == {
            "single-city",
            "basic-historical",
            "real-time",
        }

    def test_meteostat_inactive_without_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat should be marked inactive without valid API key."""
        from src.config.api_config import APIConfig, get_active_data_sources

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        sources = get_active_data_sources()

        assert "meteostat" in sources
        assert sources["meteostat"]["name"] == "Meteostat API"
        assert sources["meteostat"]["type"] == "premium"
        assert "inactive" in sources["meteostat"]["status"]
        assert sources["meteostat"]["cost"] == "$10 USD/month"

    def test_meteostat_active_with_valid_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat should be marked active with valid API key."""
        from src.config.api_config import APIConfig, get_active_data_sources

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        sources = get_active_data_sources()

        assert "meteostat" in sources
        assert sources["meteostat"]["status"] == "active"
        assert sources["meteostat"]["rate_limit"] == "10000 requests/month"

    def test_meteostat_inactive_use_cases(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat use cases should be defined even when inactive."""
        from src.config.api_config import APIConfig, get_active_data_sources

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        sources = get_active_data_sources()

        meteostat = sources["meteostat"]
        assert set(meteostat["use_cases"]) == {
            "multi-city",
            "rich-historical",
            "station-based",
        }

    def test_meteostat_active_use_cases(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Meteostat use cases should be defined when active."""
        from src.config.api_config import APIConfig, get_active_data_sources

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        sources = get_active_data_sources()

        meteostat = sources["meteostat"]
        assert set(meteostat["use_cases"]) == {
            "multi-city",
            "rich-historical",
            "station-based",
        }

    def test_returns_dict_with_both_sources(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should return a dict with both sources regardless of key status."""
        from src.config.api_config import APIConfig, get_active_data_sources

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        sources_no_key = get_active_data_sources()
        assert len(sources_no_key) == 2
        assert set(sources_no_key.keys()) == {"open-meteo", "meteostat"}

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        sources_with_key = get_active_data_sources()
        assert len(sources_with_key) == 2
        assert set(sources_with_key.keys()) == {"open-meteo", "meteostat"}
