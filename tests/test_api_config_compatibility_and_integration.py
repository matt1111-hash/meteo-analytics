"""Comprehensive tests for src/config/api_config.py."""

from __future__ import annotations

import pytest


class TestBackwardCompatibility:
    """Test cases for backward compatibility aliases."""

    def test_api_constants_alias(self) -> None:
        """APIConstants should be an alias for APIConfig."""
        from src.config.api_config import APIConfig, APIConstants

        assert APIConstants is APIConfig

    def test_api_constants_has_same_attributes(self) -> None:
        """APIConstants should expose the same attributes as APIConfig."""
        from src.config.api_config import APIConfig, APIConstants

        assert APIConfig.OPEN_METEO_BASE == APIConstants.OPEN_METEO_BASE
        assert APIConfig.METEOSTAT_BASE == APIConstants.METEOSTAT_BASE
        assert APIConfig.REQUEST_TIMEOUT == APIConstants.REQUEST_TIMEOUT
        assert APIConfig.SOURCE_DISPLAY_NAMES == APIConstants.SOURCE_DISPLAY_NAMES


class TestIntegration:
    """Integration tests for api_config module."""

    def test_validate_keys_and_get_sources_consistency(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """validate_api_keys and get_active_data_sources should be consistent."""
        from src.config.api_config import (
            APIConfig,
            get_active_data_sources,
            validate_api_keys,
        )

        monkeypatch.setattr(APIConfig, "METEOSTAT_API_KEY", "a" * 32)
        validation = validate_api_keys()
        sources = get_active_data_sources()

        assert validation["meteostat_key_valid"] is True
        assert sources["meteostat"]["status"] == "active"

    def test_constants_are_not_modified_at_runtime(self) -> None:
        """Module constants should not be modifiable at runtime."""
        from src.config.api_config import APIConfig, DataConstants

        with pytest.raises(TypeError):
            APIConfig.SOURCE_DISPLAY_NAMES["new_key"] = "value"

        with pytest.raises(TypeError):
            DataConstants.USE_CASE_SOURCE_MAPPING["new_key"] = "value"

        with pytest.raises(TypeError):
            DataConstants.SOURCE_CAPABILITIES["new_source"] = {}

    def test_all_required_constants_exist(self) -> None:
        """All required constants should be defined."""
        from src.config.api_config import APIConfig, DataConstants

        assert hasattr(APIConfig, "OPEN_METEO_BASE")
        assert hasattr(APIConfig, "OPEN_METEO_ARCHIVE")
        assert hasattr(APIConfig, "OPEN_METEO_GEOCODING")
        assert hasattr(APIConfig, "METEOSTAT_BASE")
        assert hasattr(APIConfig, "REQUEST_TIMEOUT")
        assert hasattr(APIConfig, "MAX_RETRIES")
        assert hasattr(APIConfig, "CACHE_DURATION")
        assert hasattr(DataConstants, "OPEN_METEO_DAILY_FIELDS")
        assert hasattr(DataConstants, "METEOSTAT_DAILY_FIELDS")
        assert hasattr(DataConstants, "PROCESSED_DAILY_FIELDS")
        assert hasattr(DataConstants, "SUPPORTED_EXPORT_FORMATS")
