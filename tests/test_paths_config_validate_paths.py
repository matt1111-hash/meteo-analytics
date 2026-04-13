"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


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
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "nonexistent.db"),
        ):
            result = validate_paths()

            assert result["legacy_db_exists"] is False

    def test_validate_paths_detects_missing_directory(self, tmp_path: Path) -> None:
        """validate_paths should detect missing critical directories."""
        from src.config.paths_config import validate_paths

        non_existent_dir = tmp_path / "does_not_exist"

        with (
            patch("src.config.paths_config.DATA_DIR", non_existent_dir / "data"),
            patch("src.config.paths_config.CACHE_DIR", non_existent_dir / "data" / "cache"),
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

        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch("src.config.paths_config.DATA_DIR", data_dir),
            patch("src.config.paths_config.CACHE_DIR", data_dir / "cache"),
            patch("src.config.paths_config.USER_PREFS_DIR", data_dir / "user_preferences"),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
            patch(
                "src.config.paths_config.Path.write_text",
                side_effect=PermissionError("Write denied"),
            ),
        ):
            result = validate_paths()

            assert result["write_permissions"] is False
            assert len(result["issues"]) > 0
            assert any("write permissions" in issue.lower() for issue in result["issues"])

    def test_validate_paths_missing_directory_after_ensure(self, tmp_path: Path) -> None:
        """validate_paths should detect directories that don't exist after ensure_directories."""
        from src.config.paths_config import validate_paths

        data_dir = tmp_path / "data"
        cache_dir = data_dir / "cache"
        user_prefs_dir = data_dir / "user_preferences"

        data_dir.mkdir(parents=True, exist_ok=True)
        user_prefs_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch("src.config.paths_config.DATA_DIR", data_dir),
            patch("src.config.paths_config.CACHE_DIR", cache_dir),
            patch("src.config.paths_config.USER_PREFS_DIR", user_prefs_dir),
            patch("src.config.paths_config.ensure_directories", side_effect=lambda: None),
            patch("src.config.paths_config.LEGACY_DB_PATH", tmp_path / "legacy.db"),
        ):
            result = validate_paths()

            assert result["directories_valid"] is False
            assert len(result["issues"]) > 0
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
