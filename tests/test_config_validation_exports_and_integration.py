"""Comprehensive tests for src/config/config_validation.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


class TestModuleExports:
    """Test cases for module __all__ exports."""

    def test_module_exports_all_functions(self) -> None:
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
            assert env_result["write_permissions"] == config_result["write_permissions"]

    def test_get_optimal_source_and_fallback_chain_consistency(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import (
            get_fallback_source_chain,
            get_optimal_data_source,
        )

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        use_cases = ["single_city", "multi_city", "real_time", "historical_deep"]

        for use_case in use_cases:
            optimal = get_optimal_data_source(use_case)
            fallback_chain = get_fallback_source_chain(optimal)
            assert fallback_chain[0] == optimal
