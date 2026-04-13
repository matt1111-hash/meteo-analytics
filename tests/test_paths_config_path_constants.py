"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path


class TestPathConstants:
    """Test cases for path constants."""

    def test_project_root_is_path(self) -> None:
        """PROJECT_ROOT should be a Path object."""
        from src.config.paths_config import PROJECT_ROOT  # noqa: PLC0415

        assert isinstance(PROJECT_ROOT, Path)

    def test_project_root_exists(self) -> None:
        """PROJECT_ROOT should point to an existing directory."""
        from src.config.paths_config import PROJECT_ROOT  # noqa: PLC0415

        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()

    def test_data_dir_is_path(self) -> None:
        """DATA_DIR should be a Path object under PROJECT_ROOT."""
        from src.config.paths_config import DATA_DIR, PROJECT_ROOT  # noqa: PLC0415

        assert isinstance(DATA_DIR, Path)
        assert PROJECT_ROOT in DATA_DIR.parents or DATA_DIR.parent == PROJECT_ROOT

    def test_cache_dir_is_path(self) -> None:
        """CACHE_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import CACHE_DIR, DATA_DIR  # noqa: PLC0415

        assert isinstance(CACHE_DIR, Path)
        assert DATA_DIR in CACHE_DIR.parents or CACHE_DIR.parent == DATA_DIR

    def test_climate_cache_dir_is_path(self) -> None:
        """CLIMATE_CACHE_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import CLIMATE_CACHE_DIR, DATA_DIR  # noqa: PLC0415

        assert isinstance(CLIMATE_CACHE_DIR, Path)
        assert DATA_DIR in CLIMATE_CACHE_DIR.parents or CLIMATE_CACHE_DIR.parent == DATA_DIR

    def test_exports_dir_is_path(self) -> None:
        """EXPORTS_DIR should be a Path object."""
        from src.config.paths_config import EXPORTS_DIR, PROJECT_ROOT  # noqa: PLC0415

        assert isinstance(EXPORTS_DIR, Path)
        assert PROJECT_ROOT in EXPORTS_DIR.parents or EXPORTS_DIR.parent == PROJECT_ROOT

    def test_logs_dir_is_path(self) -> None:
        """LOGS_DIR should be a Path object."""
        from src.config.paths_config import LOGS_DIR, PROJECT_ROOT  # noqa: PLC0415

        assert isinstance(LOGS_DIR, Path)
        assert PROJECT_ROOT in LOGS_DIR.parents or LOGS_DIR.parent == PROJECT_ROOT

    def test_user_prefs_dir_is_path(self) -> None:
        """USER_PREFS_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import DATA_DIR, USER_PREFS_DIR  # noqa: PLC0415

        assert isinstance(USER_PREFS_DIR, Path)
        assert DATA_DIR in USER_PREFS_DIR.parents or USER_PREFS_DIR.parent == DATA_DIR

    def test_provider_prefs_file_is_path(self) -> None:
        """PROVIDER_PREFS_FILE should be a Path object."""
        from src.config.paths_config import PROVIDER_PREFS_FILE  # noqa: PLC0415

        assert isinstance(PROVIDER_PREFS_FILE, Path)
        assert PROVIDER_PREFS_FILE.name == "provider_preferences.json"

    def test_usage_tracking_file_is_path(self) -> None:
        """USAGE_TRACKING_FILE should be a Path object."""
        from src.config.paths_config import USAGE_TRACKING_FILE  # noqa: PLC0415

        assert isinstance(USAGE_TRACKING_FILE, Path)
        assert USAGE_TRACKING_FILE.name == "api_usage_tracking.json"

    def test_weather_db_path_is_path(self) -> None:
        """WEATHER_DB_PATH should be a Path object."""
        from src.config.paths_config import WEATHER_DB_PATH  # noqa: PLC0415

        assert isinstance(WEATHER_DB_PATH, Path)
        assert WEATHER_DB_PATH.name == "weather.db"

    def test_cache_db_path_is_path(self) -> None:
        """CACHE_DB_PATH should be a Path object."""
        from src.config.paths_config import CACHE_DB_PATH  # noqa: PLC0415

        assert isinstance(CACHE_DB_PATH, Path)
        assert CACHE_DB_PATH.name == "cache.db"

    def test_legacy_db_path_is_path(self) -> None:
        """LEGACY_DB_PATH should be a Path object."""
        from src.config.paths_config import LEGACY_DB_PATH, PROJECT_ROOT  # noqa: PLC0415

        assert isinstance(LEGACY_DB_PATH, Path)
        assert PROJECT_ROOT in LEGACY_DB_PATH.parents

    def test_all_path_constants_are_absolute(self) -> None:
        """All path constants should be absolute paths."""
        from src.config.paths_config import (  # noqa: PLC0415
            CACHE_DB_PATH,
            CACHE_DIR,
            CLIMATE_CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LEGACY_DB_PATH,
            LOGS_DIR,
            PROJECT_ROOT,
            PROVIDER_PREFS_FILE,
            USAGE_TRACKING_FILE,
            USER_PREFS_DIR,
            WEATHER_DB_PATH,
        )

        paths = [
            PROJECT_ROOT,
            DATA_DIR,
            CACHE_DIR,
            CLIMATE_CACHE_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            USER_PREFS_DIR,
            PROVIDER_PREFS_FILE,
            USAGE_TRACKING_FILE,
            WEATHER_DB_PATH,
            CACHE_DB_PATH,
            LEGACY_DB_PATH,
        ]

        for path in paths:
            assert path.is_absolute(), f"{path} is not an absolute path"
