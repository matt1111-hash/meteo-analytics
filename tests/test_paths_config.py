"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


class TestPathConstants:
    """Test cases for path constants."""

    def test_project_root_is_path(self) -> None:
        """PROJECT_ROOT should be a Path object."""
        from src.config.paths_config import PROJECT_ROOT

        assert isinstance(PROJECT_ROOT, Path)

    def test_project_root_exists(self) -> None:
        """PROJECT_ROOT should point to an existing directory."""
        from src.config.paths_config import PROJECT_ROOT

        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()

    def test_data_dir_is_path(self) -> None:
        """DATA_DIR should be a Path object under PROJECT_ROOT."""
        from src.config.paths_config import DATA_DIR, PROJECT_ROOT

        assert isinstance(DATA_DIR, Path)
        assert PROJECT_ROOT in DATA_DIR.parents or DATA_DIR.parent == PROJECT_ROOT

    def test_cache_dir_is_path(self) -> None:
        """CACHE_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import CACHE_DIR, DATA_DIR

        assert isinstance(CACHE_DIR, Path)
        assert DATA_DIR in CACHE_DIR.parents or CACHE_DIR.parent == DATA_DIR

    def test_climate_cache_dir_is_path(self) -> None:
        """CLIMATE_CACHE_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import CLIMATE_CACHE_DIR, DATA_DIR

        assert isinstance(CLIMATE_CACHE_DIR, Path)
        assert (
            DATA_DIR in CLIMATE_CACHE_DIR.parents
            or CLIMATE_CACHE_DIR.parent == DATA_DIR
        )

    def test_exports_dir_is_path(self) -> None:
        """EXPORTS_DIR should be a Path object."""
        from src.config.paths_config import EXPORTS_DIR, PROJECT_ROOT

        assert isinstance(EXPORTS_DIR, Path)
        assert PROJECT_ROOT in EXPORTS_DIR.parents or EXPORTS_DIR.parent == PROJECT_ROOT

    def test_logs_dir_is_path(self) -> None:
        """LOGS_DIR should be a Path object."""
        from src.config.paths_config import LOGS_DIR, PROJECT_ROOT

        assert isinstance(LOGS_DIR, Path)
        assert PROJECT_ROOT in LOGS_DIR.parents or LOGS_DIR.parent == PROJECT_ROOT

    def test_user_prefs_dir_is_path(self) -> None:
        """USER_PREFS_DIR should be a Path object under DATA_DIR."""
        from src.config.paths_config import DATA_DIR, USER_PREFS_DIR

        assert isinstance(USER_PREFS_DIR, Path)
        assert DATA_DIR in USER_PREFS_DIR.parents or USER_PREFS_DIR.parent == DATA_DIR

    def test_provider_prefs_file_is_path(self) -> None:
        """PROVIDER_PREFS_FILE should be a Path object."""
        from src.config.paths_config import PROVIDER_PREFS_FILE

        assert isinstance(PROVIDER_PREFS_FILE, Path)
        assert PROVIDER_PREFS_FILE.name == "provider_preferences.json"

    def test_usage_tracking_file_is_path(self) -> None:
        """USAGE_TRACKING_FILE should be a Path object."""
        from src.config.paths_config import USAGE_TRACKING_FILE

        assert isinstance(USAGE_TRACKING_FILE, Path)
        assert USAGE_TRACKING_FILE.name == "api_usage_tracking.json"

    def test_weather_db_path_is_path(self) -> None:
        """WEATHER_DB_PATH should be a Path object."""
        from src.config.paths_config import WEATHER_DB_PATH

        assert isinstance(WEATHER_DB_PATH, Path)
        assert WEATHER_DB_PATH.name == "weather.db"

    def test_cache_db_path_is_path(self) -> None:
        """CACHE_DB_PATH should be a Path object."""
        from src.config.paths_config import CACHE_DB_PATH

        assert isinstance(CACHE_DB_PATH, Path)
        assert CACHE_DB_PATH.name == "cache.db"

    def test_legacy_db_path_is_path(self) -> None:
        """LEGACY_DB_PATH should be a Path object."""
        from src.config.paths_config import LEGACY_DB_PATH, PROJECT_ROOT

        assert isinstance(LEGACY_DB_PATH, Path)
        assert PROJECT_ROOT in LEGACY_DB_PATH.parents

    def test_all_path_constants_are_absolute(self) -> None:
        """All path constants should be absolute paths."""
        from src.config.paths_config import (
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


class TestEnsureDirectories:
    """Test cases for ensure_directories() function."""

    def test_ensure_directories_creates_all_directories(self, tmp_path: Path) -> None:
        """ensure_directories should create all necessary directories."""
        from src.config.paths_config import ensure_directories

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                tmp_path / "data" / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
        ):
            # Clear existing directories
            import shutil

            if tmp_path.exists():
                shutil.rmtree(tmp_path)

            ensure_directories()

            # Check all directories were created
            assert (tmp_path / "data").exists()
            assert (tmp_path / "data" / "cache").exists()
            assert (tmp_path / "data" / "climate_cache").exists()
            assert (tmp_path / "exports").exists()
            assert (tmp_path / "logs").exists()
            assert (tmp_path / "data" / "user_preferences").exists()

    def test_ensure_directories_idempotent(self, tmp_path: Path) -> None:
        """ensure_directories should be safe to call multiple times."""
        from src.config.paths_config import ensure_directories

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                tmp_path / "data" / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
        ):
            # Call once
            ensure_directories()

            # Call again - should not raise any errors
            ensure_directories()

            # All directories should still exist
            assert (tmp_path / "data").exists()
            assert (tmp_path / "data" / "cache").exists()

    def test_ensure_directories_creates_nested_paths(self, tmp_path: Path) -> None:
        """ensure_directories should create parent directories when needed."""
        from src.config.paths_config import ensure_directories

        nested_dir = tmp_path / "level1" / "level2" / "level3"

        with (
            patch("src.config.paths_config.DATA_DIR", nested_dir),
            patch("src.config.paths_config.CACHE_DIR", nested_dir / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                nested_dir / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                nested_dir / "user_preferences",
            ),
        ):
            ensure_directories()

            # Nested directory should be created
            assert nested_dir.exists()
            assert nested_dir.is_dir()

    def test_ensure_directories_returns_none(self) -> None:
        """ensure_directories should not return anything."""
        from src.config.paths_config import ensure_directories

        result = ensure_directories()
        assert result is None


class TestValidatePaths:
    """Test cases for validate_paths() function."""

    def test_validate_paths_success(self, tmp_path: Path) -> None:
        """validate_paths should return success status when all paths are valid."""
        from src.config.paths_config import validate_paths

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
        ):
            result = validate_paths()

            assert result["directories_valid"] is True
            assert result["write_permissions"] is True
            assert isinstance(result["legacy_db_exists"], bool)
            assert len(result["issues"]) == 0

    def test_validate_paths_with_legacy_db(self, tmp_path: Path) -> None:
        """validate_paths should detect existing legacy database."""
        from src.config.paths_config import validate_paths

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
        ):
            # Create legacy database
            (tmp_path / "legacy.db").touch()

            result = validate_paths()

            assert result["legacy_db_exists"] is True

    def test_validate_paths_without_legacy_db(self, tmp_path: Path) -> None:
        """validate_paths should report missing legacy database."""
        from src.config.paths_config import validate_paths

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
            patch(
                "src.config.paths_config.LEGACY_DB_PATH", tmp_path / "nonexistent.db"
            ),
        ):
            result = validate_paths()

            assert result["legacy_db_exists"] is False

    def test_validate_paths_detects_missing_directory(self, tmp_path: Path) -> None:
        """validate_paths should detect missing critical directories."""
        from src.config.paths_config import validate_paths

        non_existent_dir = tmp_path / "does_not_exist"

        with (
            patch("src.config.paths_config.DATA_DIR", non_existent_dir / "data"),
            patch(
                "src.config.paths_config.CACHE_DIR", non_existent_dir / "data" / "cache"
            ),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                non_existent_dir / "data" / "user_preferences",
            ),
            patch(
                "src.config.paths_config.ensure_directories",
                side_effect=RuntimeError("Directory creation failed"),
            ),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
        ):
            result = validate_paths()

            assert result["directories_valid"] is False
            assert len(result["issues"]) > 0

    def test_validate_paths_write_permission_error(self, tmp_path: Path) -> None:
        """validate_paths should detect write permission errors."""
        from src.config.paths_config import validate_paths

        # Create DATA_DIR first
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch("src.config.paths_config.DATA_DIR", data_dir),
            patch("src.config.paths_config.CACHE_DIR", data_dir / "cache"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR", data_dir / "user_preferences"
            ),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
            patch(
                "src.config.paths_config.Path.write_text",
                side_effect=PermissionError("Write denied"),
            ),
        ):
            result = validate_paths()

            assert result["write_permissions"] is False
            assert len(result["issues"]) > 0
            assert any(
                "write permissions" in issue.lower() for issue in result["issues"]
            )

    def test_validate_paths_missing_directory_after_ensure(
        self, tmp_path: Path
    ) -> None:
        """validate_paths should detect directories that don't exist after ensure_directories."""
        from src.config.paths_config import validate_paths

        # Create DATA_DIR so write test doesn't fail, but leave CACHE_DIR missing
        data_dir = tmp_path / "data"
        cache_dir = data_dir / "cache"  # This won't exist
        user_prefs_dir = data_dir / "user_preferences"  # Create this one

        data_dir.mkdir(parents=True, exist_ok=True)
        user_prefs_dir.mkdir(parents=True, exist_ok=True)
        # cache_dir is intentionally NOT created

        with (
            patch("src.config.paths_config.DATA_DIR", data_dir),
            patch("src.config.paths_config.CACHE_DIR", cache_dir),
            patch("src.config.paths_config.USER_PREFS_DIR", user_prefs_dir),
            patch(
                "src.config.paths_config.ensure_directories",
                side_effect=lambda: None,  # Don't create directories
            ),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
        ):
            result = validate_paths()

            # CACHE_DIR doesn't exist
            assert result["directories_valid"] is False
            assert len(result["issues"]) > 0
            # Check for missing directory issue
            issues_text = " ".join(result["issues"]).lower()
            assert "directory" in issues_text or "cache" in issues_text.lower()

    def test_validate_paths_exception_handling(self, tmp_path: Path) -> None:
        """validate_paths should handle exceptions gracefully."""
        from src.config.paths_config import validate_paths

        with patch(
            "src.config.paths_config.ensure_directories",
            side_effect=PermissionError("Access denied"),
        ):
            result = validate_paths()

            assert result["directories_valid"] is False
            assert len(result["issues"]) > 0
            assert any("Access denied" in issue for issue in result["issues"])


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


class TestModuleInitialization:
    """Test cases for module initialization behavior."""

    def test_ensure_directories_called_on_import(self) -> None:
        """ensure_directories should be called when module is imported."""
        # This is tested implicitly by the fact that the module works
        # The directories are created on import (line 112 in paths_config.py)
        from src.config.paths_config import DATA_DIR

        # DATA_DIR should exist after module import
        assert DATA_DIR.exists()


class TestIntegration:
    """Integration tests for paths_config module."""

    def test_validate_paths_and_get_project_info_consistency(self) -> None:
        """validate_paths and get_project_info should be consistent."""
        from src.config.paths_config import get_project_info, validate_paths

        result = validate_paths()
        project_info = get_project_info()

        # If paths are valid, project info should return valid paths
        if result["directories_valid"]:
            for key, value in project_info.items():
                path = Path(value)
                # At least project_root should exist
                if key == "project_root":
                    assert path.exists()

    def test_all_critical_paths_unique(self) -> None:
        """All critical path constants should have unique values."""
        from src.config.paths_config import (
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

        # All paths should be unique
        path_strings = [str(p) for p in paths]
        assert len(path_strings) == len(set(path_strings)), "Path values are not unique"

    def test_parent_child_relationships(self) -> None:
        """Directory paths should have correct parent-child relationships."""
        from src.config.paths_config import (
            CACHE_DIR,
            CLIMATE_CACHE_DIR,
            DATA_DIR,
            EXPORTS_DIR,
            LOGS_DIR,
            PROJECT_ROOT,
            USER_PREFS_DIR,
        )

        # DATA_DIR should be under PROJECT_ROOT
        assert DATA_DIR == PROJECT_ROOT / "data"

        # CACHE_DIR should be under DATA_DIR
        assert CACHE_DIR == DATA_DIR / "cache"

        # CLIMATE_CACHE_DIR should be under DATA_DIR
        assert CLIMATE_CACHE_DIR == DATA_DIR / "climate_cache"

        # USER_PREFS_DIR should be under DATA_DIR
        assert USER_PREFS_DIR == DATA_DIR / "user_preferences"

        # EXPORTS_DIR should be under PROJECT_ROOT
        assert EXPORTS_DIR == PROJECT_ROOT / "exports"

        # LOGS_DIR should be under PROJECT_ROOT
        assert LOGS_DIR == PROJECT_ROOT / "logs"

    def test_file_paths_under_correct_directories(self) -> None:
        """File paths should be under correct parent directories."""
        from src.config.paths_config import (
            CACHE_DB_PATH,
            DATA_DIR,
            PROVIDER_PREFS_FILE,
            USAGE_TRACKING_FILE,
            USER_PREFS_DIR,
            WEATHER_DB_PATH,
        )

        # Database files should be under DATA_DIR
        assert DATA_DIR in WEATHER_DB_PATH.parents or WEATHER_DB_PATH.parent == DATA_DIR
        assert DATA_DIR in CACHE_DB_PATH.parents or CACHE_DB_PATH.parent == DATA_DIR

        # Preference files should be under USER_PREFS_DIR
        assert (
            USER_PREFS_DIR in PROVIDER_PREFS_FILE.parents
            or PROVIDER_PREFS_FILE.parent == USER_PREFS_DIR
        )
        assert (
            USER_PREFS_DIR in USAGE_TRACKING_FILE.parents
            or USAGE_TRACKING_FILE.parent == USER_PREFS_DIR
        )
