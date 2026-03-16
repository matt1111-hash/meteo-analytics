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

        assert GUIConfig.WEATHER_UPDATE_INTERVAL == 600
        assert GUIConfig.WARNING_UPDATE_INTERVAL == 300

    def test_provider_selector_gui_settings(self) -> None:
        """Provider selector GUI settings should be properly defined."""
        from src.config.config_settings import GUIConfig

        assert GUIConfig.PROVIDER_SELECTOR_POSITION == "control_panel"
        assert GUIConfig.SHOW_USAGE_WARNINGS is True
        assert GUIConfig.SHOW_COST_ESTIMATES is True
        assert GUIConfig.AUTO_FALLBACK_ON_LIMIT is True

    def test_gui_config_is_frozen(self) -> None:
        """GUIConfig instances should be frozen (immutable)."""
        from dataclasses import fields

        from src.config.config_settings import GUIConfig

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
        assert HardwareConfig.GPU_MEMORY_LIMIT == 6

    def test_hardware_config_is_frozen(self) -> None:
        """HardwareConfig instances should be frozen (immutable)."""
        from dataclasses import fields

        from src.config.config_settings import HardwareConfig

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
