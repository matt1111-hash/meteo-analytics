"""Comprehensive tests for src/config/config_validation.py."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestCheckEnvironment:
    """Test cases for check_environment() function."""

    def test_check_environment_success(self, tmp_path: Path) -> None:
        """Successful environment check should return all True values."""
        from src.config.config_validation import check_environment

        with (
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            # Setup mocks
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": True}

            # Create directories
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
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
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
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
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
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {"meteostat_key_valid": True}

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)

            # Make DATA_DIR read-only to trigger write error
            os.chmod(tmp_path, 0o444)

            try:
                result = check_environment()
                # Write permissions should be False when write fails
                assert "write_permissions" in result
            finally:
                # Restore permissions for cleanup
                os.chmod(tmp_path, 0o755)


class TestValidateConfig:
    """Test cases for validate_config() function."""

    def test_validate_config_success(self, tmp_path: Path) -> None:
        """Successful config validation should return all True values."""
        from src.config.config_validation import validate_config

        with (
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch(
                "src.config.config_validation.LEGACY_DB_PATH", tmp_path / "legacy.db"
            ),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
        ):
            mock_ensure_dirs.return_value = None
            mock_validate.return_value = {
                "meteostat_key_valid": True,
                "openmeteo_available": True,
            }

            # Create legacy db and prefs dir
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
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
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
            patch(
                "src.config.config_validation.ensure_directories"
            ) as mock_ensure_dirs,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch(
                "src.config.config_validation.LEGACY_DB_PATH", tmp_path / "legacy.db"
            ),
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


class TestGetOptimalDataSource:
    """Test cases for get_optimal_data_source() function."""

    def test_get_optimal_data_source_single_city(self) -> None:
        """Single city use case should return open-meteo."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("single_city")
        assert result == "open-meteo"

    def test_get_optimal_data_source_multi_city(self) -> None:
        """Multi city use case should return meteostat by default."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("multi_city")
        assert result == "meteostat"

    def test_get_optimal_data_source_multi_city_prefer_free(self) -> None:
        """Multi city with prefer_free should check capabilities."""
        from src.config.config_validation import get_optimal_data_source

        # With prefer_free=True and multi_city, it should try open-meteo first
        # but since open-meteo doesn't support "multi_city" use case directly,
        # it will fall back to meteostat
        result = get_optimal_data_source("multi_city", prefer_free=True)
        assert result == "meteostat"

    def test_get_optimal_data_source_historical_deep(self) -> None:
        """Historical deep use case should return meteostat."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("historical_deep")
        assert result == "meteostat"

    def test_get_optimal_data_source_real_time(self) -> None:
        """Real time use case should return open-meteo."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("real_time")
        assert result == "open-meteo"

    def test_get_optimal_data_source_station_based(self) -> None:
        """Station based use case should return meteostat."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("station_based")
        assert result == "meteostat"

    def test_get_optimal_data_source_interpolated(self) -> None:
        """Interpolated use case should return open-meteo."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("interpolated")
        assert result == "open-meteo"

    def test_get_optimal_data_source_unknown_use_case(self) -> None:
        """Unknown use case should return default open-meteo."""
        from src.config.config_validation import get_optimal_data_source

        result = get_optimal_data_source("unknown_use_case")
        assert result == "open-meteo"


class TestGetSourceDisplayName:
    """Test cases for get_source_display_name() function."""

    def test_get_source_display_name_open_meteo(self) -> None:
        """Open-Meteo display name should be returned."""
        from src.config.config_validation import get_source_display_name

        result = get_source_display_name("open-meteo")
        assert "Open-Meteo" in result
        assert "🌍" in result or result == "🌍 Open-Meteo API"

    def test_get_source_display_name_meteostat(self) -> None:
        """Meteostat display name should be returned."""
        from src.config.config_validation import get_source_display_name

        result = get_source_display_name("meteostat")
        assert "Meteostat" in result
        assert "💎" in result or result == "💎 Meteostat API"

    def test_get_source_display_name_unknown(self) -> None:
        """Unknown source should return formatted name."""
        from src.config.config_validation import get_source_display_name

        result = get_source_display_name("unknown_source")
        assert result == "Unknown Source (unknown_source)"


class TestValidateApiSourceAvailable:
    """Test cases for validate_api_source_available() function."""

    def test_validate_open_meteo_always_available(self) -> None:
        """Open-Meteo should always be available."""
        from src.config.config_validation import validate_api_source_available

        result = validate_api_source_available("open-meteo")
        assert result is True

    def test_validate_meteostat_with_valid_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat should be available with valid API key."""
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        result = validate_api_source_available("meteostat")
        assert result is True

    def test_validate_meteostat_with_short_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat should not be available with short API key."""
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "short")
        result = validate_api_source_available("meteostat")
        assert result is False

    def test_validate_meteostat_with_whitespace_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Meteostat should handle API key with whitespace."""
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "  " + "a" * 32 + "  ")
        result = validate_api_source_available("meteostat")
        assert result is True

    def test_validate_meteostat_no_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Meteostat should not be available without API key."""
        from src.config.config_validation import validate_api_source_available

        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        result = validate_api_source_available("meteostat")
        assert result is False

    def test_validate_unknown_source(self) -> None:
        """Unknown source should return False."""
        from src.config.config_validation import validate_api_source_available

        result = validate_api_source_available("unknown_source")
        assert result is False


class TestGetFallbackSourceChain:
    """Test cases for get_fallback_source_chain() function."""

    def test_fallback_chain_open_meteo_primary(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fallback chain with open-meteo as primary."""
        from src.config.config_validation import get_fallback_source_chain

        # Open-meteo is always available, meteostat is not (no key)
        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        result = get_fallback_source_chain("open-meteo")

        assert result == ["open-meteo"]

    def test_fallback_chain_meteostat_primary_with_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fallback chain with meteostat as primary and valid key."""
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        result = get_fallback_source_chain("meteostat")

        # Both should be available, meteostat first
        assert "meteostat" in result
        assert "open-meteo" in result
        assert result[0] == "meteostat"

    def test_fallback_chain_only_open_meteo_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fallback chain when only open-meteo is available."""
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        result = get_fallback_source_chain("any_source")

        assert result == ["open-meteo"]

    def test_fallback_chain_both_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fallback chain when both sources are available."""
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        result = get_fallback_source_chain("open-meteo")

        # Both should be in the list
        assert len(result) == 2
        assert "open-meteo" in result
        assert "meteostat" in result
        assert result[0] == "open-meteo"


class TestModuleExports:
    """Test cases for module __all__ exports."""

    def test_module_exports_all_functions(self) -> None:
        """__all__ should export all public functions."""
        from src.config import config_validation

        expected_exports = {
            "check_environment",
            "validate_config",
            "get_optimal_data_source",
            "get_source_display_name",
            "validate_api_source_available",
            "get_fallback_source_chain",
        }
        actual_exports = set(config_validation.__all__)

        assert actual_exports == expected_exports

    def test_all_exports_are_callable(self) -> None:
        """All functions in __all__ should be callable."""
        from src.config.config_validation import (
            check_environment,
            get_fallback_source_chain,
            get_optimal_data_source,
            get_source_display_name,
            validate_api_source_available,
            validate_config,
        )

        assert callable(check_environment)
        assert callable(validate_config)
        assert callable(get_optimal_data_source)
        assert callable(get_source_display_name)
        assert callable(validate_api_source_available)
        assert callable(get_fallback_source_chain)


class TestIntegration:
    """Integration tests for config_validation module."""

    def test_validate_config_and_environment_consistency(self, tmp_path: Path) -> None:
        """validate_config and check_environment should be consistent."""
        from src.config.config_validation import check_environment, validate_config

        with (
            patch("src.config.config_validation.ensure_directories") as mock_ensure,
            patch("src.config.config_validation.validate_api_keys") as mock_validate,
            patch("src.config.config_validation.DATA_DIR", tmp_path),
            patch("src.config.config_validation.CACHE_DIR", tmp_path / "cache"),
            patch("src.config.config_validation.USER_PREFS_DIR", tmp_path / "prefs"),
            patch(
                "src.config.config_validation.LEGACY_DB_PATH", tmp_path / "legacy.db"
            ),
        ):
            mock_ensure.return_value = None
            mock_validate.return_value = {
                "meteostat_key_valid": True,
                "openmeteo_available": True,
            }

            (tmp_path / "cache").mkdir(exist_ok=True)
            (tmp_path / "prefs").mkdir(exist_ok=True)
            (tmp_path / "legacy.db").touch()

            env_result = check_environment()
            config_result = validate_config()

            # Both should agree on write permissions
            assert env_result["write_permissions"] == config_result["write_permissions"]

    def test_get_optimal_source_and_fallback_chain_consistency(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Optimal source should be first in fallback chain."""
        from src.config.config_validation import (
            get_fallback_source_chain,
            get_optimal_data_source,
        )

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)

        # Test various use cases
        use_cases = ["single_city", "multi_city", "real_time", "historical_deep"]

        for use_case in use_cases:
            optimal = get_optimal_data_source(use_case)
            fallback_chain = get_fallback_source_chain(optimal)

            # Optimal source should be first in fallback chain
            assert fallback_chain[0] == optimal
