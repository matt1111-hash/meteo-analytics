"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json
from datetime import datetime


class TestUserPreferencesLoad:
    """Test cases for UserPreferences.load_provider_preferences() method."""

    def test_load_preferences_returns_defaults_when_file_missing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Missing preferences file should return default preferences."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs.pop("prefs", None)

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == ProviderConfig.DEFAULT_PROVIDER
        assert prefs["auto_fallback_enabled"] is True
        assert prefs["show_usage_warnings"] is True
        assert prefs["show_cost_estimates"] is True
        assert prefs["monthly_budget_usd"] == ProviderConfig.MONTHLY_BUDGET_USD
        assert prefs["warning_threshold"] == ProviderConfig.WARNING_THRESHOLD
        assert "last_updated" in prefs

    def test_load_preferences_merges_with_saved_values(self, config_fs: dict[str, str]) -> None:
        """Saved preferences should be merged with defaults."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs["prefs"] = json.dumps(
            {"selected_provider": "meteostat", "auto_fallback_enabled": False}
        )

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == "meteostat"
        assert prefs["auto_fallback_enabled"] is False
        assert prefs["show_usage_warnings"] is True
        assert prefs["monthly_budget_usd"] == ProviderConfig.MONTHLY_BUDGET_USD

    def test_load_preferences_handles_corrupted_json(self, config_fs: dict[str, str]) -> None:
        """Corrupted JSON should return default preferences."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs["prefs"] = "{ not valid json"

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == ProviderConfig.DEFAULT_PROVIDER

    def test_load_preferences_includes_timestamp(self, config_fs: dict[str, str]) -> None:
        """Preferences should include last_updated timestamp."""
        from src.config.provider_config import UserPreferences

        prefs = UserPreferences.load_provider_preferences()

        assert "last_updated" in prefs
        datetime.fromisoformat(prefs["last_updated"])
