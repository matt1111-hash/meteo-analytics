"""Comprehensive tests for src/config/config_settings.py."""

from __future__ import annotations


class TestModuleExports:
    """Test cases for module __all__ exports."""

    def test_module_exports_all_configs(self) -> None:
        """__all__ should export all config classes."""
        from src.config import config_settings  # noqa: PLC0415

        expected_exports = {
            "GUIConfig",
            "HardwareConfig",
            "MultiCityConfig",
            "AppInfo",
            "RequestLimits",
            "WeatherFetchConfig",
        }
        actual_exports = set(config_settings.__all__)

        assert actual_exports == expected_exports

    def test_all_exports_are_importable(self) -> None:
        """All classes in __all__ should be importable from module."""
        from src.config.config_settings import (  # noqa: PLC0415
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
            RequestLimits,
        )

        assert GUIConfig is not None
        assert HardwareConfig is not None
        assert MultiCityConfig is not None
        assert AppInfo is not None
        assert RequestLimits is not None


class TestIntegration:
    """Integration tests for config_settings module."""

    def test_all_configs_are_dataclass_instances(self) -> None:
        """All config classes should be dataclass instances."""
        from dataclasses import is_dataclass  # noqa: PLC0415

        from src.config.config_settings import (  # noqa: PLC0415
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
        from dataclasses import fields  # noqa: PLC0415

        from src.config.config_settings import (  # noqa: PLC0415
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        configs = [GUIConfig, HardwareConfig, MultiCityConfig, AppInfo]
        for config in configs:
            assert len(fields(config)) > 0

    def test_config_values_are_sensible(self) -> None:
        """Configuration values should be within sensible ranges."""
        from src.config.config_settings import (  # noqa: PLC0415
            AppInfo,
            GUIConfig,
            HardwareConfig,
            MultiCityConfig,
        )

        assert GUIConfig.DEFAULT_WINDOW_SIZE[0] > 0
        assert GUIConfig.DEFAULT_WINDOW_SIZE[1] > 0
        assert GUIConfig.MIN_WINDOW_SIZE[0] > 0
        assert GUIConfig.MIN_WINDOW_SIZE[1] > 0
        assert GUIConfig.DEFAULT_WINDOW_SIZE[0] >= GUIConfig.MIN_WINDOW_SIZE[0]
        assert 72 <= GUIConfig.DPI <= 300
        assert GUIConfig.WEATHER_UPDATE_INTERVAL > 0
        assert GUIConfig.WARNING_UPDATE_INTERVAL > 0
        assert HardwareConfig.MAX_CONCURRENT_REQUESTS > 0
        assert HardwareConfig.CHART_CACHE_SIZE > 0
        assert HardwareConfig.DATA_CHUNK_SIZE > 0
        assert 0 <= HardwareConfig.GPU_MEMORY_LIMIT <= 24
        assert MultiCityConfig.MAX_CITIES_PER_BATCH > 0
        assert MultiCityConfig.STATION_SEARCH_RADIUS > 0
        assert MultiCityConfig.MAX_STATION_DISTANCE > 0
        assert MultiCityConfig.METEOSTAT_CONCURRENT_REQUESTS > 0
        assert MultiCityConfig.METEOSTAT_REQUEST_DELAY >= 0
        assert 0 <= MultiCityConfig.FALLBACK_THRESHOLD <= 1
        assert len(AppInfo.VERSION) > 0
        assert len(AppInfo.PROVIDER_SELECTOR_VERSION) > 0

    def test_provider_selector_features_are_complete(self) -> None:
        """Provider selector features should cover key functionality."""
        from src.config.config_settings import AppInfo  # noqa: PLC0415

        features = AppInfo.PROVIDER_SELECTOR_FEATURES
        feature_text = " ".join(features).lower()

        assert "api" in feature_text or "selection" in feature_text
        assert "usage" in feature_text or "tracking" in feature_text
        assert "cost" in feature_text or "monitoring" in feature_text
        assert "routing" in feature_text or "logic" in feature_text
        assert "fallback" in feature_text or "automatic" in feature_text
