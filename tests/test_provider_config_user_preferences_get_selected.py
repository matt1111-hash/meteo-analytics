"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json


class TestUserPreferencesGetSelected:
    """Test cases for UserPreferences.get_selected_provider() method."""

    def test_get_selected_provider_returns_saved_value(self, config_fs: dict[str, str]) -> None:
        """Should return the saved selected provider."""
        from src.config.provider_config import UserPreferences

        config_fs["prefs"] = json.dumps({"selected_provider": "meteostat"})

        result = UserPreferences.get_selected_provider()

        assert result == "meteostat"

    def test_get_selected_provider_returns_default_when_missing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Should return default provider when not set."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs.pop("prefs", None)

        result = UserPreferences.get_selected_provider()

        assert result == ProviderConfig.DEFAULT_PROVIDER
