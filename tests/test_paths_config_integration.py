"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path


class TestIntegration:
    """Integration tests for paths_config module."""

    def test_validate_paths_and_get_project_info_consistency(self) -> None:
        """validate_paths and get_project_info should be consistent."""
        from src.config.paths_config import get_project_info, validate_paths  # noqa: PLC0415

        result = validate_paths()
        project_info = get_project_info()

        if result["directories_valid"]:
            for key, value in project_info.items():
                path = Path(value)
                if key == "project_root":
                    assert path.exists()

    def test_all_critical_paths_unique(self) -> None:
        """All critical path constants should have unique values."""
        from src.config.paths_config import (  # noqa: PLC0415
            CACHE_DB_PATH,
            CACHE_DIR,
            CLIMATE_CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            PROJECT_ROOT,
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
            WEATHER_DB_PATH,
            CACHE_DB_PATH,
        ]

        path_strings = [str(p) for p in paths]
        assert len(path_strings) == len(set(path_strings)), "Path values are not unique"

    def test_parent_child_relationships(self) -> None:
        """Directory paths should have correct parent-child relationships."""
        from src.config.paths_config import (  # noqa: PLC0415
            CACHE_DIR,
            CLIMATE_CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            PROJECT_ROOT,
            USER_PREFS_DIR,
        )

        assert DATA_DIR == PROJECT_ROOT / "data"
        assert CACHE_DIR == DATA_DIR / "cache"
        assert CLIMATE_CACHE_DIR == DATA_DIR / "climate_cache"
        assert USER_PREFS_DIR == DATA_DIR / "user_preferences"
        assert EXPORTS_DIR == PROJECT_ROOT / "exports"
        assert LOGS_DIR == PROJECT_ROOT / "logs"

    def test_file_paths_under_correct_directories(self) -> None:
        """File paths should be under correct parent directories."""
        from src.config.paths_config import (  # noqa: PLC0415
            CACHE_DB_PATH,
            DATA_DIR,
            PROVIDER_PREFS_FILE,
            USAGE_TRACKING_FILE,
            USER_PREFS_DIR,
            WEATHER_DB_PATH,
        )

        assert DATA_DIR in WEATHER_DB_PATH.parents or WEATHER_DB_PATH.parent == DATA_DIR
        assert DATA_DIR in CACHE_DB_PATH.parents or CACHE_DB_PATH.parent == DATA_DIR
        assert (
            USER_PREFS_DIR in PROVIDER_PREFS_FILE.parents
            or PROVIDER_PREFS_FILE.parent == USER_PREFS_DIR
        )
        assert (
            USER_PREFS_DIR in USAGE_TRACKING_FILE.parents
            or USAGE_TRACKING_FILE.parent == USER_PREFS_DIR
        )
