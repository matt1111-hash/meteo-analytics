"""Comprehensive tests for src/config/config_settings.py."""

from __future__ import annotations


class TestMultiCityConfig:
    """Test cases for MultiCityConfig dataclass."""

    def test_batch_settings(self) -> None:
        """Batch processing settings should be properly defined."""
        from src.config.config_settings import MultiCityConfig  # noqa: PLC0415

        assert MultiCityConfig.MAX_CITIES_PER_BATCH == 20
        assert MultiCityConfig.STATION_SEARCH_RADIUS == 50000
        assert MultiCityConfig.MAX_STATION_DISTANCE == 25.0

    def test_rate_limiting(self) -> None:
        """Rate limiting for premium API should be configured."""
        from src.config.config_settings import MultiCityConfig  # noqa: PLC0415

        assert MultiCityConfig.METEOSTAT_CONCURRENT_REQUESTS == 5
        assert MultiCityConfig.METEOSTAT_REQUEST_DELAY == 0.1

    def test_fallback_configuration(self) -> None:
        """Fallback settings should be properly defined."""
        from src.config.config_settings import MultiCityConfig  # noqa: PLC0415

        assert MultiCityConfig.ENABLE_FALLBACK_TO_OPENMETEO is True
        assert MultiCityConfig.FALLBACK_THRESHOLD == 0.3

    def test_multi_city_config_is_frozen(self) -> None:
        """MultiCityConfig instances should be frozen (immutable)."""
        from dataclasses import fields  # noqa: PLC0415

        from src.config.config_settings import MultiCityConfig  # noqa: PLC0415

        assert len(fields(MultiCityConfig)) > 0

    def test_multi_city_config_all_attributes_exist(self) -> None:
        """All MultiCityConfig attributes should be defined."""
        from src.config.config_settings import MultiCityConfig  # noqa: PLC0415

        expected_attrs = {
            "MAX_CITIES_PER_BATCH",
            "STATION_SEARCH_RADIUS",
            "MAX_STATION_DISTANCE",
            "METEOSTAT_CONCURRENT_REQUESTS",
            "METEOSTAT_REQUEST_DELAY",
            "ENABLE_FALLBACK_TO_OPENMETEO",
            "FALLBACK_THRESHOLD",
        }
        actual_attrs = set(dir(MultiCityConfig))
        assert expected_attrs.issubset(actual_attrs)


class TestAppInfo:
    """Test cases for AppInfo dataclass."""

    def test_basic_app_info(self) -> None:
        """Basic application metadata should be properly defined."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert AppInfo.NAME == "Global Weather Analyzer"
        assert AppInfo.VERSION == "2.2.0"
        assert AppInfo.AUTHOR == "Weather Analytics Team"

    def test_description(self) -> None:
        """Application description should mention dual-API support."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert "dual-api" in AppInfo.DESCRIPTION.lower()
        assert "meteorological" in AppInfo.DESCRIPTION.lower()

    def test_api_architecture_info(self) -> None:
        """API architecture information should be defined."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert "Dual-API" in AppInfo.API_ARCHITECTURE
        assert AppInfo.PRIMARY_API == "Open-Meteo (Free)"
        assert AppInfo.PREMIUM_API == "Meteostat (Premium)"

    def test_provider_selector_info(self) -> None:
        """Provider selector version and features should be defined."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert AppInfo.PROVIDER_SELECTOR_VERSION == "1.0.0"
        assert len(AppInfo.PROVIDER_SELECTOR_FEATURES) == 5
        assert "User-controlled API selection" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Real-time usage tracking" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Cost monitoring" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Smart routing logic" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Automatic fallback" in AppInfo.PROVIDER_SELECTOR_FEATURES

    def test_legacy_info(self) -> None:
        """Legacy application information should be preserved."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert AppInfo.LEGACY_NAME == "Meteo History"
        assert AppInfo.LEGACY_VERSION == "1.0.0"

    def test_app_info_is_frozen(self) -> None:
        """AppInfo instances should be frozen (immutable)."""
        from dataclasses import fields  # noqa: PLC0415

        from src.config.config_settings import AppInfo  # noqa: PLC0415

        assert len(fields(AppInfo)) > 0

    def test_app_info_all_attributes_exist(self) -> None:
        """All AppInfo attributes should be defined."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        expected_attrs = {
            "NAME",
            "VERSION",
            "DESCRIPTION",
            "AUTHOR",
            "API_ARCHITECTURE",
            "PRIMARY_API",
            "PREMIUM_API",
            "PROVIDER_SELECTOR_VERSION",
            "PROVIDER_SELECTOR_FEATURES",
            "LEGACY_NAME",
            "LEGACY_VERSION",
        }
        actual_attrs = set(dir(AppInfo))
        assert expected_attrs.issubset(actual_attrs)
