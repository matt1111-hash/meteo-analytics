"""Comprehensive tests for src/config/api_config.py."""

from __future__ import annotations

import pytest


class TestAPIConfig:
    """Test cases for APIConfig class constants."""

    def test_open_meteo_endpoints_defined(self) -> None:
        """Open-Meteo API endpoints should be properly defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.OPEN_METEO_BASE == "https://api.open-meteo.com/v1"
        assert (
            APIConfig.OPEN_METEO_ARCHIVE
            == "https://archive-api.open-meteo.com/v1/archive"
        )
        assert (
            APIConfig.OPEN_METEO_GEOCODING
            == "https://geocoding-api.open-meteo.com/v1/search"
        )

    def test_meteostat_endpoints_defined(self) -> None:
        """Meteostat API endpoints should be properly defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.METEOSTAT_BASE == "https://meteostat.p.rapidapi.com"

    def test_meteostat_monthly_limit(self) -> None:
        """Meteostat monthly request limit should be defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.METEOSTAT_MONTHLY_LIMIT == 10000
        assert APIConfig.METEOSTAT_RATE_LIMIT == 0.1

    def test_request_configuration(self) -> None:
        """Request timeout and retry configuration should be defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.REQUEST_TIMEOUT == 30
        assert APIConfig.MAX_RETRIES == 3
        assert APIConfig.CACHE_DURATION == 3600

    def test_data_source_defaults(self) -> None:
        """Default data sources for different use cases should be defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.SINGLE_CITY_SOURCE == "open-meteo"
        assert APIConfig.MULTI_CITY_SOURCE == "meteostat"
        assert APIConfig.HISTORICAL_SOURCE == "meteostat"

    def test_rate_limits(self) -> None:
        """Rate limits for both providers should be defined."""
        from src.config.api_config import APIConfig

        assert APIConfig.OPENMETEO_RATE_LIMIT == 0.1
        assert APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE == 10000

    def test_source_display_names(self) -> None:
        """Source display names should be immutable mapping."""
        from src.config.api_config import APIConfig

        assert APIConfig.SOURCE_DISPLAY_NAMES["open-meteo"] == "🌍 Open-Meteo API"
        assert APIConfig.SOURCE_DISPLAY_NAMES["meteostat"] == "💎 Meteostat API"
        # Should be immutable (MappingProxyType)
        with pytest.raises(TypeError):
            APIConfig.SOURCE_DISPLAY_NAMES["open-meteo"] = "modified"

    def test_user_agent(self) -> None:
        """User agent string should be defined."""
        from src.config.api_config import APIConfig

        assert "Global Weather Analyzer" in APIConfig.USER_AGENT
        assert "2.2.0" in APIConfig.USER_AGENT
        assert "Provider-Selector Edition" in APIConfig.USER_AGENT


class TestDataConstants:
    """Test cases for DataConstants class."""

    def test_open_meteo_daily_fields(self) -> None:
        """Open-Meteo daily field names should be defined."""
        from src.config.api_config import DataConstants

        expected_fields = (
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "winddirection_10m_dominant",
            "weathercode",
        )
        assert DataConstants.OPEN_METEO_DAILY_FIELDS == expected_fields

    def test_open_meteo_hourly_fields(self) -> None:
        """Open-Meteo hourly field names should be defined."""
        from src.config.api_config import DataConstants

        expected_fields = (
            "wind_gusts_10m",
            "windspeed_10m",
        )
        assert DataConstants.OPEN_METEO_HOURLY_FIELDS == expected_fields

    def test_meteostat_daily_fields(self) -> None:
        """Meteostat daily field names should be defined."""
        from src.config.api_config import DataConstants

        expected_fields = (
            "tavg",
            "tmin",
            "tmax",
            "prcp",
            "snow",
            "wdir",
            "wspd",
            "wpgt",
            "pres",
            "tsun",
        )
        assert DataConstants.METEOSTAT_DAILY_FIELDS == expected_fields

    def test_processed_daily_fields(self) -> None:
        """Processed daily field names should be defined."""
        from src.config.api_config import DataConstants

        expected_fields = (
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "wind_gusts_max",
            "winddirection_10m_dominant",
            "weathercode",
        )
        assert DataConstants.PROCESSED_DAILY_FIELDS == expected_fields

    def test_export_formats(self) -> None:
        """Supported export formats should be defined."""
        from src.config.api_config import DataConstants

        assert "csv" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "excel" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "json" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "pdf" in DataConstants.SUPPORTED_EXPORT_FORMATS

    def test_page_size_limits(self) -> None:
        """Page size limits should be defined."""
        from src.config.api_config import DataConstants

        assert DataConstants.DEFAULT_PAGE_SIZE == 100
        assert DataConstants.MAX_PAGE_SIZE == 1000

    def test_cache_configuration(self) -> None:
        """Cache expiry and size limits should be defined."""
        from src.config.api_config import DataConstants

        assert DataConstants.CACHE_EXPIRY_HOURS == 24
        assert DataConstants.MAX_CACHE_SIZE_MB == 100

    def test_use_case_source_mapping(self) -> None:
        """Use case to source mapping should be immutable."""
        from src.config.api_config import DataConstants

        assert DataConstants.USE_CASE_SOURCE_MAPPING["single_city"] == "open-meteo"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["multi_city"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["historical_deep"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["real_time"] == "open-meteo"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["station_based"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["interpolated"] == "open-meteo"

        # Should be immutable (MappingProxyType)
        with pytest.raises(TypeError):
            DataConstants.USE_CASE_SOURCE_MAPPING["single_city"] = "modified"

    def test_data_source_priority(self) -> None:
        """Data source priority order should be defined."""
        from src.config.api_config import DataConstants

        assert DataConstants.DATA_SOURCE_PRIORITY == ("open-meteo", "meteostat")

    def test_source_capabilities(self) -> None:
        """Source capabilities mapping should be defined and immutable."""
        from src.config.api_config import DataConstants

        # Check open-meteo capabilities
        open_meteo_caps = DataConstants.SOURCE_CAPABILITIES["open-meteo"]
        assert open_meteo_caps["historical"] is True
        assert open_meteo_caps["real_time"] is True
        assert open_meteo_caps["multi_city"] is True
        assert open_meteo_caps["station_based"] is False
        assert open_meteo_caps["cost"] == "free"
        assert open_meteo_caps["rate_limit"] == "10/sec"
        assert open_meteo_caps["wind_gusts"] is True
        assert open_meteo_caps["rich_params"] is False

        # Check meteostat capabilities
        meteostat_caps = DataConstants.SOURCE_CAPABILITIES["meteostat"]
        assert meteostat_caps["historical"] is True
        assert meteostat_caps["real_time"] is False
        assert meteostat_caps["multi_city"] is True
        assert meteostat_caps["station_based"] is True
        assert meteostat_caps["cost"] == "premium"
        assert meteostat_caps["rate_limit"] == "10k/month"
        assert meteostat_caps["wind_gusts"] is True
        assert meteostat_caps["rich_params"] is True

        # Should be immutable (MappingProxyType)
        with pytest.raises(TypeError):
            DataConstants.SOURCE_CAPABILITIES["open-meteo"] = "modified"


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

        # Test with no Meteostat key
        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        result_no_key = validate_api_keys()
        assert result_no_key["openmeteo_available"] is True

        # Test with valid Meteostat key
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

        # Test without key
        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", None)
        sources_no_key = get_active_data_sources()
        assert len(sources_no_key) == 2
        assert set(sources_no_key.keys()) == {"open-meteo", "meteostat"}

        # Test with key
        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        sources_with_key = get_active_data_sources()
        assert len(sources_with_key) == 2
        assert set(sources_with_key.keys()) == {"open-meteo", "meteostat"}


class TestBackwardCompatibility:
    """Test cases for backward compatibility aliases."""

    def test_api_constants_alias(self) -> None:
        """APIConstants should be an alias for APIConfig."""
        from src.config.api_config import APIConfig, APIConstants

        assert APIConstants is APIConfig

    def test_api_constants_has_same_attributes(self) -> None:
        """APIConstants should expose the same attributes as APIConfig."""
        from src.config.api_config import APIConfig, APIConstants

        assert APIConfig.OPEN_METEO_BASE == APIConstants.OPEN_METEO_BASE
        assert APIConfig.METEOSTAT_BASE == APIConstants.METEOSTAT_BASE
        assert APIConfig.REQUEST_TIMEOUT == APIConstants.REQUEST_TIMEOUT
        assert APIConfig.SOURCE_DISPLAY_NAMES == APIConstants.SOURCE_DISPLAY_NAMES


class TestIntegration:
    """Integration tests for api_config module."""

    def test_validate_keys_and_get_sources_consistency(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_api_keys and get_active_data_sources should be consistent."""
        from src.config.api_config import (
            APIConfig,
            get_active_data_sources,
            validate_api_keys,
        )

        # Test with valid key
        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        validation = validate_api_keys()
        sources = get_active_data_sources()

        assert validation["meteostat_key_valid"] is True
        assert sources["meteostat"]["status"] == "active"

    def test_constants_are_not_modified_at_runtime(self) -> None:
        """Module constants should not be modifiable at runtime."""
        from src.config.api_config import APIConfig, DataConstants

        # Test that we can't modify MappingProxyType objects
        with pytest.raises(TypeError):
            APIConfig.SOURCE_DISPLAY_NAMES["new_key"] = "value"

        with pytest.raises(TypeError):
            DataConstants.USE_CASE_SOURCE_MAPPING["new_key"] = "value"

        with pytest.raises(TypeError):
            DataConstants.SOURCE_CAPABILITIES["new_source"] = {}

    def test_all_required_constants_exist(self) -> None:
        """All required constants should be defined."""
        from src.config.api_config import APIConfig, DataConstants

        # APIConfig constants
        assert hasattr(APIConfig, "OPEN_METEO_BASE")
        assert hasattr(APIConfig, "OPEN_METEO_ARCHIVE")
        assert hasattr(APIConfig, "OPEN_METEO_GEOCODING")
        assert hasattr(APIConfig, "METEOSTAT_BASE")
        assert hasattr(APIConfig, "REQUEST_TIMEOUT")
        assert hasattr(APIConfig, "MAX_RETRIES")
        assert hasattr(APIConfig, "CACHE_DURATION")

        # DataConstants fields
        assert hasattr(DataConstants, "OPEN_METEO_DAILY_FIELDS")
        assert hasattr(DataConstants, "METEOSTAT_DAILY_FIELDS")
        assert hasattr(DataConstants, "PROCESSED_DAILY_FIELDS")
        assert hasattr(DataConstants, "SUPPORTED_EXPORT_FORMATS")
