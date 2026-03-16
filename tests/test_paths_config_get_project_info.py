"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path


class TestGetProjectInfo:
    """Test cases for get_project_info() function."""

    def test_get_project_info_returns_dict(self) -> None:
        """get_project_info should return a dictionary."""
        from src.config.paths_config import get_project_info

        result = get_project_info()

        assert isinstance(result, dict)

    def test_get_project_info_contains_all_keys(self) -> None:
        """get_project_info should contain all expected keys."""
        from src.config.paths_config import get_project_info

        result = get_project_info()

        expected_keys = {
            "project_root",
            "data_dir",
            "cache_dir",
            "exports_dir",
            "logs_dir",
            "weather_db",
            "cache_db",
        }

        assert set(result.keys()) == expected_keys

    def test_get_project_info_values_are_strings(self) -> None:
        """get_project_info should return string values for all paths."""
        from src.config.paths_config import get_project_info

        result = get_project_info()

        for key, value in result.items():
            assert isinstance(value, str), f"{key} value is not a string: {type(value)}"

    def test_get_project_info_values_are_absolute_paths(self) -> None:
        """get_project_info should return absolute paths."""
        from src.config.paths_config import get_project_info

        result = get_project_info()

        for key, value in result.items():
            path = Path(value)
            assert path.is_absolute(), f"{key} is not an absolute path: {value}"

    def test_get_project_info_consistent_with_constants(self) -> None:
        """get_project_info values should be consistent with path constants."""
        from src.config.paths_config import (
            CACHE_DB_PATH,
            CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            PROJECT_ROOT,
            WEATHER_DB_PATH,
            get_project_info,
        )

        result = get_project_info()

        assert result["project_root"] == str(PROJECT_ROOT)
        assert result["data_dir"] == str(DATA_DIR)
        assert result["cache_dir"] == str(CACHE_DIR)
        assert result["exports_dir"] == str(EXPORTS_DIR)
        assert result["logs_dir"] == str(LOGS_DIR)
        assert result["weather_db"] == str(WEATHER_DB_PATH)
        assert result["cache_db"] == str(CACHE_DB_PATH)
