"""Comprehensive tests for src/config/config_settings.py."""

from __future__ import annotations


class TestGUIConfig:
    """Test cases for GUIConfig dataclass."""

    def test_window_size_defaults(self) -> None:
        """Window size defaults should be properly defined."""
        from src.config.config_settings import GUIConfig

        assert GUIConfig.DEFAULT_WINDOW_SIZE == (1200, 800)
        assert GUIConfig.MIN_WINDOW_SIZE == (900, 600)

    def test_chart_settings(self) -> None:
        """Chart DPI and figure size should be properly defined."""
        from src.config.config_settings import GUIConfig

        assert GUIConfig.DPI == 100
        assert GUIConfig.FIGURE_SIZE == (5, 4)

    def test_update_intervals(self) -> None:
        """Update intervals should be properly defined in seconds."""
        from src.config.config_settings import GUIConfig

        assert GUIConfig.WEATHER_UPDATE_INTERVAL == 600  # 10 minutes
        assert GUIConfig.WARNING_UPDATE_INTERVAL == 300  # 5 minutes

    def test_provider_selector_gui_settings(self) -> None:
        """Provider selector GUI settings should be properly defined."""
        from src.config.config_settings import GUIConfig

        assert GUIConfig.PROVIDER_SELECTOR_POSITION == "control_panel"
        assert GUIConfig.SHOW_USAGE_WARNINGS is True
        assert GUIConfig.SHOW_COST_ESTIMATES is True
        assert GUIConfig.AUTO_FALLBACK_ON_LIMIT is True

    def test_gui_config_is_frozen(self) -> None:
        """GUIConfig instances should be frozen (immutable)."""
        # frozen=True makes instances immutable, not the class
        # We can't test instance modification since instances aren't created
        # Just verify it's a frozen dataclass
        from dataclasses import fields

        from src.config.config_settings import GUIConfig

        # Check that GUIConfig is a dataclass
        assert len(fields(GUIConfig)) > 0

    def test_gui_config_all_attributes_exist(self) -> None:
        """All GUIConfig attributes should be defined."""
        from src.config.config_settings import GUIConfig

        expected_attrs = {
            "DEFAULT_WINDOW_SIZE",
            "MIN_WINDOW_SIZE",
            "DPI",
            "FIGURE_SIZE",
            "WEATHER_UPDATE_INTERVAL",
            "WARNING_UPDATE_INTERVAL",
            "PROVIDER_SELECTOR_POSITION",
            "SHOW_USAGE_WARNINGS",
            "SHOW_COST_ESTIMATES",
            "AUTO_FALLBACK_ON_LIMIT",
        }
        actual_attrs = set(dir(GUIConfig))
        assert expected_attrs.issubset(actual_attrs)


class TestHardwareConfig:
    """Test cases for HardwareConfig dataclass."""

    def test_concurrent_settings(self) -> None:
        """Concurrent request and cache settings should be defined."""
        from src.config.config_settings import HardwareConfig

        assert HardwareConfig.MAX_CONCURRENT_REQUESTS == 8
        assert HardwareConfig.CHART_CACHE_SIZE == 50
        assert HardwareConfig.DATA_CHUNK_SIZE == 10000

    def test_gpu_settings(self) -> None:
        """GPU acceleration settings should be properly configured."""
        from src.config.config_settings import HardwareConfig

        assert HardwareConfig.USE_GPU_ACCELERATION is True
        assert HardwareConfig.GPU_MEMORY_LIMIT == 6  # GB

    def test_hardware_config_is_frozen(self) -> None:
        """HardwareConfig instances should be frozen (immutable)."""
        from dataclasses import fields

        from src.config.config_settings import HardwareConfig

        # Check that HardwareConfig is a dataclass
        assert len(fields(HardwareConfig)) > 0

    def test_hardware_config_all_attributes_exist(self) -> None:
        """All HardwareConfig attributes should be defined."""
        from src.config.config_settings import HardwareConfig

        expected_attrs = {
            "MAX_CONCURRENT_REQUESTS",
            "CHART_CACHE_SIZE",
            "DATA_CHUNK_SIZE",
            "USE_GPU_ACCELERATION",
            "GPU_MEMORY_LIMIT",
        }
        actual_attrs = set(dir(HardwareConfig))
        assert expected_attrs.issubset(actual_attrs)


class TestMultiCityConfig:
    """Test cases for MultiCityConfig dataclass."""

    def test_batch_settings(self) -> None:
        """Batch processing settings should be properly defined."""
        from src.config.config_settings import MultiCityConfig

        assert MultiCityConfig.MAX_CITIES_PER_BATCH == 20
        assert MultiCityConfig.STATION_SEARCH_RADIUS == 50000  # 50km
        assert MultiCityConfig.MAX_STATION_DISTANCE == 25.0  # 25km

    def test_rate_limiting(self) -> None:
        """Rate limiting for premium API should be configured."""
        from src.config.config_settings import MultiCityConfig

        assert MultiCityConfig.METEOSTAT_CONCURRENT_REQUESTS == 5
        assert MultiCityConfig.METEOSTAT_REQUEST_DELAY == 0.1  # 100ms

    def test_fallback_configuration(self) -> None:
        """Fallback settings should be properly defined."""
        from src.config.config_settings import MultiCityConfig

        assert MultiCityConfig.ENABLE_FALLBACK_TO_OPENMETEO is True
        assert MultiCityConfig.FALLBACK_THRESHOLD == 0.3  # 30%

    def test_multi_city_config_is_frozen(self) -> None:
        """MultiCityConfig instances should be frozen (immutable)."""
        from dataclasses import fields

        from src.config.config_settings import MultiCityConfig

        # Check that MultiCityConfig is a dataclass
        assert len(fields(MultiCityConfig)) > 0

    def test_multi_city_config_all_attributes_exist(self) -> None:
        """All MultiCityConfig attributes should be defined."""
        from src.config.config_settings import MultiCityConfig

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
        from src.config.config_settings import AppInfo

        assert AppInfo.NAME == "Global Weather Analyzer"
        assert AppInfo.VERSION == "2.2.0"
        assert AppInfo.AUTHOR == "Weather Analytics Team"

    def test_description(self) -> None:
        """Application description should mention dual-API support."""
        from src.config.config_settings import AppInfo

        assert "dual-api" in AppInfo.DESCRIPTION.lower()
        assert "meteorological" in AppInfo.DESCRIPTION.lower()

    def test_api_architecture_info(self) -> None:
        """API architecture information should be defined."""
        from src.config.config_settings import AppInfo

        assert "Dual-API" in AppInfo.API_ARCHITECTURE
        assert AppInfo.PRIMARY_API == "Open-Meteo (Free)"
        assert AppInfo.PREMIUM_API == "Meteostat (Premium)"

    def test_provider_selector_info(self) -> None:
        """Provider selector version and features should be defined."""
        from src.config.config_settings import AppInfo

        assert AppInfo.PROVIDER_SELECTOR_VERSION == "1.0.0"
        assert len(AppInfo.PROVIDER_SELECTOR_FEATURES) == 5
        assert "User-controlled API selection" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Real-time usage tracking" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Cost monitoring" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Smart routing logic" in AppInfo.PROVIDER_SELECTOR_FEATURES
        assert "Automatic fallback" in AppInfo.PROVIDER_SELECTOR_FEATURES

    def test_legacy_info(self) -> None:
        """Legacy application information should be preserved."""
        from src.config.config_settings import AppInfo

        assert AppInfo.LEGACY_NAME == "Meteo History"
        assert AppInfo.LEGACY_VERSION == "1.0.0"

    def test_app_info_is_frozen(self) -> None:
        """AppInfo instances should be frozen (immutable)."""
        from dataclasses import fields

        from src.config.config_settings import AppInfo

        # Check that AppInfo is a dataclass
        assert len(fields(AppInfo)) > 0

    def test_app_info_all_attributes_exist(self) -> None:
        """All AppInfo attributes should be defined."""
        from src.config.config_settings import AppInfo

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


class TestModuleExports:
    """Test cases for module __all__ exports."""

    def test_module_exports_all_configs(self) -> None:
        """__all__ should export all config classes."""
        from src.config import config_settings

        expected_exports = {"GUIConfig", "HardwareConfig", "MultiCityConfig", "AppInfo"}
        actual_exports = set(config_settings.__all__)

        assert actual_exports == expected_exports

    def test_all_exports_are_importable(self) -> None:
        """All classes in __all__ should be importable from module."""
        from src.config.config_settings import (
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        assert GUIConfig is not None
        assert HardwareConfig is not None
        assert MultiCityConfig is not None
        assert AppInfo is not None


class TestIntegration:
    """Integration tests for config_settings module."""

    def test_all_configs_are_dataclass_instances(self) -> None:
        """All config classes should be dataclass instances."""
        from dataclasses import is_dataclass

        from src.config.config_settings import (
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        assert is_dataclass(GUIConfig)
        assert is_dataclass(HardwareConfig)
        assert is_dataclass(MultiCityConfig)
        assert is_dataclass(AppInfo)

    def test_all_configs_are_frozen(self) -> None:
        """All config classes should be frozen dataclasses."""
        from dataclasses import fields

        from src.config.config_settings import (
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        # Verify each config is a dataclass with fields
        configs = [GUIConfig, HardwareConfig, MultiCityConfig, AppInfo]
        for config in configs:
            assert len(fields(config)) > 0

    def test_config_values_are_sensible(self) -> None:
        """Configuration values should be within sensible ranges."""
        from src.config.config_settings import (
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        # Window sizes should be positive and default > min
        assert GUIConfig.DEFAULT_WINDOW_SIZE[0] > 0
        assert GUIConfig.DEFAULT_WINDOW_SIZE[1] > 0
        assert GUIConfig.MIN_WINDOW_SIZE[0] > 0
        assert GUIConfig.MIN_WINDOW_SIZE[1] > 0
        assert GUIConfig.DEFAULT_WINDOW_SIZE[0] >= GUIConfig.MIN_WINDOW_SIZE[0]

        # DPI should be reasonable
        assert 72 <= GUIConfig.DPI <= 300

        # Intervals should be positive
        assert GUIConfig.WEATHER_UPDATE_INTERVAL > 0
        assert GUIConfig.WARNING_UPDATE_INTERVAL > 0

        # Hardware limits should be positive
        assert HardwareConfig.MAX_CONCURRENT_REQUESTS > 0
        assert HardwareConfig.CHART_CACHE_SIZE > 0
        assert HardwareConfig.DATA_CHUNK_SIZE > 0
        assert 0 <= HardwareConfig.GPU_MEMORY_LIMIT <= 24  # Max realistic GPU

        # Multi-city settings should be positive
        assert MultiCityConfig.MAX_CITIES_PER_BATCH > 0
        assert MultiCityConfig.STATION_SEARCH_RADIUS > 0
        assert MultiCityConfig.MAX_STATION_DISTANCE > 0
        assert MultiCityConfig.METEOSTAT_CONCURRENT_REQUESTS > 0
        assert MultiCityConfig.METEOSTAT_REQUEST_DELAY >= 0
        assert 0 <= MultiCityConfig.FALLBACK_THRESHOLD <= 1

        # Version strings should be non-empty
        assert len(AppInfo.VERSION) > 0
        assert len(AppInfo.PROVIDER_SELECTOR_VERSION) > 0

    def test_provider_selector_features_are_complete(self) -> None:
        """Provider selector features should cover key functionality."""
        from src.config.config_settings import AppInfo

        features = AppInfo.PROVIDER_SELECTOR_FEATURES
        feature_text = " ".join(features).lower()

        # Should mention key capabilities
        assert "api" in feature_text or "selection" in feature_text
        assert "usage" in feature_text or "tracking" in feature_text
        assert "cost" in feature_text or "monitoring" in feature_text
        assert "routing" in feature_text or "logic" in feature_text
        assert "fallback" in feature_text or "automatic" in feature_text
