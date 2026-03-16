"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json


class TestUserPreferencesSetSelected:
    """Test cases for UserPreferences.set_selected_provider() method."""

    def test_set_selected_provider_valid_provider(
        self, config_fs: dict[str, str]
    ) -> None:
        """Setting a valid provider should succeed."""
        from src.config.provider_config import UserPreferences

        result = UserPreferences.set_selected_provider("meteostat")

        assert result is True

        saved = json.loads(config_fs["prefs"])
        assert saved["selected_provider"] == "meteostat"

    def test_set_selected_provider_invalid_provider(
        self, config_fs: dict[str, str]
    ) -> None:
        """Setting an invalid provider should fail."""
        from src.config.provider_config import UserPreferences

        result = UserPreferences.set_selected_provider("invalid_provider")

        assert result is False

    def test_set_selected_provider_all_valid_providers(
        self, config_fs: dict[str, str]
    ) -> None:
        """All valid providers should be settable."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        for provider in ProviderConfig.PROVIDERS:
            result = UserPreferences.set_selected_provider(provider)
            assert result is True

            saved = json.loads(config_fs["prefs"])
            assert saved["selected_provider"] == provider
