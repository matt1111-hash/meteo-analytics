"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json


class TestIntegration:
    """Integration tests for provider_config module."""

    def test_set_and_get_selected_provider_roundtrip(
        self, config_fs: dict[str, str]
    ) -> None:
        """Setting and getting provider should work correctly."""
        from src.config.provider_config import UserPreferences

        UserPreferences.set_selected_provider("meteostat")

        result = UserPreferences.get_selected_provider()

        assert result == "meteostat"

    def test_load_save_preferences_roundtrip(self, config_fs: dict[str, str]) -> None:
        """Saving and loading preferences should preserve data."""
        from src.config.provider_config import UserPreferences

        original_prefs = {
            "selected_provider": "open-meteo",
            "auto_fallback_enabled": False,
            "show_usage_warnings": True,
            "monthly_budget_usd": 15.0,
        }

        UserPreferences.save_provider_preferences(original_prefs)

        loaded_prefs = UserPreferences.load_provider_preferences()

        assert loaded_prefs["selected_provider"] == "open-meteo"
        assert loaded_prefs["auto_fallback_enabled"] is False
        assert loaded_prefs["monthly_budget_usd"] == 15.0

    def test_provider_list_matches_validation(self) -> None:
        """All providers in list should be valid."""
        from src.config.provider_config import (
            ProviderConfig,
            UserPreferences,
            validate_provider_selection,
        )

        providers = UserPreferences.list_available_providers()

        for provider_id in providers:
            assert validate_provider_selection(provider_id) is True
            assert provider_id in ProviderConfig.PROVIDERS

    def test_auto_routing_matches_provider_config(
        self, config_fs: dict[str, str]
    ) -> None:
        """Auto routing should match ProviderConfig routing logic."""
        from src.config.provider_config import ProviderConfig, get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        routing_logic = ProviderConfig.PROVIDERS["auto"]["routing_logic"]

        for use_case, expected_provider in routing_logic.items():
            result = get_resolved_provider(use_case)
            assert result == expected_provider
