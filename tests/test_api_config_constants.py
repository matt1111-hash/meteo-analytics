"""Comprehensive tests for src/config/api_config.py."""

from __future__ import annotations

import pytest


class TestAPIConfig:
    """Test cases for APIConfig class constants."""

    def test_open_meteo_endpoints_defined(self) -> None:
        """Open-Meteo API endpoints should be properly defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.OPEN_METEO_BASE == "https://api.open-meteo.com/v1"
        assert APIConfig.OPEN_METEO_ARCHIVE == "https://archive-api.open-meteo.com/v1/archive"
        assert APIConfig.OPEN_METEO_GEOCODING == "https://geocoding-api.open-meteo.com/v1/search"

    def test_meteostat_endpoints_defined(self) -> None:
        """Meteostat API endpoints should be properly defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.METEOSTAT_BASE == "https://meteostat.p.rapidapi.com"

    def test_meteostat_monthly_limit(self) -> None:
        """Meteostat monthly request limit should be defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.METEOSTAT_MONTHLY_LIMIT == 10000
        assert APIConfig.METEOSTAT_RATE_LIMIT == 0.1

    def test_request_configuration(self) -> None:
        """Request timeout and retry configuration should be defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.REQUEST_TIMEOUT == 30
        assert APIConfig.MAX_RETRIES == 3
        assert APIConfig.CACHE_DURATION == 3600

    def test_data_source_defaults(self) -> None:
        """Default data sources for different use cases should be defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.SINGLE_CITY_SOURCE == "open-meteo"
        assert APIConfig.MULTI_CITY_SOURCE == "meteostat"
        assert APIConfig.HISTORICAL_SOURCE == "meteostat"

    def test_rate_limits(self) -> None:
        """Rate limits for both providers should be defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.OPENMETEO_RATE_LIMIT == 0.1
        assert APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE == 10000

    def test_source_display_names(self) -> None:
        """Source display names should be immutable mapping."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert APIConfig.SOURCE_DISPLAY_NAMES["open-meteo"] == "🌍 Open-Meteo API"
        assert APIConfig.SOURCE_DISPLAY_NAMES["meteostat"] == "💎 Meteostat API"
        with pytest.raises(TypeError):
            APIConfig.SOURCE_DISPLAY_NAMES["open-meteo"] = "modified"

    def test_user_agent(self) -> None:
        """User agent string should be defined."""
        from src.config.api_config import APIConfig  # noqa: PLC0415

        assert "Global Weather Analyzer" in APIConfig.USER_AGENT
        assert "2.2.0" in APIConfig.USER_AGENT
        assert "Provider-Selector Edition" in APIConfig.USER_AGENT


class TestDataConstants:
    """Test cases for DataConstants class."""

    def test_open_meteo_daily_fields(self) -> None:
        """Open-Meteo daily field names should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        expected_fields = (
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "winddirection_10m_dominant",
            "weathercode",
        )
        assert expected_fields == DataConstants.OPEN_METEO_DAILY_FIELDS

    def test_open_meteo_hourly_fields(self) -> None:
        """Open-Meteo hourly field names should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        expected_fields = ("wind_gusts_10m", "windspeed_10m")
        assert expected_fields == DataConstants.OPEN_METEO_HOURLY_FIELDS

    def test_meteostat_daily_fields(self) -> None:
        """Meteostat daily field names should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

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
        assert expected_fields == DataConstants.METEOSTAT_DAILY_FIELDS

    def test_processed_daily_fields(self) -> None:
        """Processed daily field names should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

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
        assert expected_fields == DataConstants.PROCESSED_DAILY_FIELDS

    def test_export_formats(self) -> None:
        """Supported export formats should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        assert "csv" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "excel" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "json" in DataConstants.SUPPORTED_EXPORT_FORMATS
        assert "pdf" in DataConstants.SUPPORTED_EXPORT_FORMATS

    def test_page_size_limits(self) -> None:
        """Page size limits should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        assert DataConstants.DEFAULT_PAGE_SIZE == 100
        assert DataConstants.MAX_PAGE_SIZE == 1000

    def test_cache_configuration(self) -> None:
        """Cache expiry and size limits should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        assert DataConstants.CACHE_EXPIRY_HOURS == 24
        assert DataConstants.MAX_CACHE_SIZE_MB == 100

    def test_use_case_source_mapping(self) -> None:
        """Use case to source mapping should be immutable."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        assert DataConstants.USE_CASE_SOURCE_MAPPING["single_city"] == "open-meteo"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["multi_city"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["historical_deep"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["real_time"] == "open-meteo"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["station_based"] == "meteostat"
        assert DataConstants.USE_CASE_SOURCE_MAPPING["interpolated"] == "open-meteo"
        with pytest.raises(TypeError):
            DataConstants.USE_CASE_SOURCE_MAPPING["single_city"] = "modified"

    def test_data_source_priority(self) -> None:
        """Data source priority order should be defined."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        assert DataConstants.DATA_SOURCE_PRIORITY == ("open-meteo", "meteostat")

    def test_source_capabilities(self) -> None:
        """Source capabilities mapping should be defined and immutable."""
        from src.config.api_config import DataConstants  # noqa: PLC0415

        open_meteo_caps = DataConstants.SOURCE_CAPABILITIES["open-meteo"]
        assert open_meteo_caps["historical"] is True
        assert open_meteo_caps["real_time"] is True
        assert open_meteo_caps["multi_city"] is True
        assert open_meteo_caps["station_based"] is False
        assert open_meteo_caps["cost"] == "free"
        assert open_meteo_caps["rate_limit"] == "10/sec"
        assert open_meteo_caps["wind_gusts"] is True
        assert open_meteo_caps["rich_params"] is False

        meteostat_caps = DataConstants.SOURCE_CAPABILITIES["meteostat"]
        assert meteostat_caps["historical"] is True
        assert meteostat_caps["real_time"] is False
        assert meteostat_caps["multi_city"] is True
        assert meteostat_caps["station_based"] is True
        assert meteostat_caps["cost"] == "premium"
        assert meteostat_caps["rate_limit"] == "10k/month"
        assert meteostat_caps["wind_gusts"] is True
        assert meteostat_caps["rich_params"] is True

        with pytest.raises(TypeError):
            DataConstants.SOURCE_CAPABILITIES["open-meteo"] = "modified"
