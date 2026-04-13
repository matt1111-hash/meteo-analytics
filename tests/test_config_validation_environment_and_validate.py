"""Comprehensive tests for src/config/config_validation.py."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch


class TestCheckEnvironment:
    """Test cases for check_environment() function."""

    def test_check_environment_success(self, tmp_path: Path) -> None:
        """Successful environment check should return all True values."""
        from src.config.config_validation import check_environment

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": True}

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = check_environment()

            assert result["directories_created"] is True
            assert result["api_keys_valid"] is True
            assert result["write_permissions"] is True
            assert result["cache_available"] is True
            assert result["provider_selector_ready"] is True
            assert result["error"] is None

    def test_check_environment_no_api_key(self, tmp_path: Path) -> None:
        """Environment check without valid API key should reflect that."""
        from src.config.config_validation import check_environment

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": False}

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = check_environment()

            assert result["api_keys_valid"] is False

    def test_check_environment_write_permission_denied(self, tmp_path: Path) -> None:
        """Environment check should handle write permission errors."""
        from src.config.config_validation import check_environment

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": True}

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = check_environment()
            assert "write_permissions" in result

    def test_check_environment_exception_handling(self) -> None:
        """Environment check should handle exceptions gracefully."""
        from src.config.config_validation import check_environment

        with patch(
            "src.config.config_validation.ensure_directories",
            side_effect=RuntimeError("Test error"),
        ):
            result = check_environment()

            assert result["directories_created"] is False
            assert result["error"] == "Test error"

    def test_check_environment_write_error(self, tmp_path: Path) -> None:
        """Environment check should handle write errors when creating test file."""
        from src.config.config_validation import check_environment

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": True}

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)

            os.chmod(tmp_path, 0o444)  # noqa: PTH101

            try:
                result = check_environment()
                assert "write_permissions" in result
            finally:
                os.chmod(tmp_path, 0o755)  # noqa: PTH101


class TestValidateConfig:
    """Test cases for validate_config() function."""

    def test_validate_config_success(self, tmp_path: Path) -> None:
        """Successful config validation should return all True values."""
        from src.config.config_validation import validate_config

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.LEGACY_DB_PATH", tmp_path / "legacy.db"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {
                "meteostat_key_valid": True,
                "openmeteo_available": True,
            }

            (tmp_path / "legacy.db").touch()
            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = validate_config()

            assert result["directories"] is True
            assert result["legacy_db"] is True
            assert result["write_permissions"] is True
            assert result["api_configuration"] is True
            assert result["multi_city_ready"] is True
            assert result["provider_selector_ready"] is True
            assert result["validation_error"] is None

    def test_validate_config_no_legacy_db(self, tmp_path: Path) -> None:
        """Config validation without legacy DB should reflect that."""
        from src.config.config_validation import validate_config

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch(
                "src.config.config_validation.LEGACY_DB_PATH",
                tmp_path / "nonexistent.db",
            ),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {
                "meteostat_key_valid": True,
                "openmeteo_available": True,
            }

            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = validate_config()

            assert result["legacy_db"] is False

    def test_validate_config_no_meteostat_key(self, tmp_path: Path) -> None:
        """Config validation without Meteostat key should affect multi_city_ready."""
        from src.config.config_validation import validate_config

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.LEGACY_DB_PATH", tmp_path / "legacy.db"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {
                "meteostat_key_valid": False,
                "openmeteo_available": True,
            }

            (tmp_path / "legacy.db").touch()
            (tmp_path / "prefs").mkdir(exist_ok=True)

            result = validate_config()

            assert result["multi_city_ready"] is False

    def test_validate_config_permission_error(self, tmp_path: Path) -> None:
        """Config validation should handle permission errors."""
        from src.config.config_validation import validate_config

        with patch(
            "src.config.config_validation.ensure_directories",
            side_effect=PermissionError("Access denied"),
        ):
            result = validate_config()

            assert result["directories"] is False
            assert result["write_permissions"] is False
            assert result["provider_selector_ready"] is False
            assert "Access denied" in result["validation_error"]

    def test_validate_config_generic_exception(self) -> None:
        """Config validation should handle generic exceptions."""
        from src.config.config_validation import validate_config

        with patch(
            "src.config.config_validation.ensure_directories",
            side_effect=ValueError("Generic error"),
        ):
            result = validate_config()

            assert "validation_error" in result
            assert "Generic error" in result["validation_error"]
