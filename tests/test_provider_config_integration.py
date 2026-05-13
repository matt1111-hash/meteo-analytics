"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations


class TestIntegration:
    """Integration tests for provider_config module."""

    def test_set_and_get_selected_provider_roundtrip(self, config_fs: dict[str, str]) -> None:
        """Setting and getting provider should work correctly."""
        from src.config.provider_config import UserPreferences  # noqa: PLC0415

        UserPreferences.set_selected_provider("meteostat")

        result = UserPreferences.get_selected_provider()

        assert result == "meteostat"

    def test_load_save_preferences_roundtrip(self, config_fs: dict[str, str]) -> None:
        """Saving and loading preferences should preserve data."""
        from src.config.provider_config import UserPreferences  # noqa: PLC0415

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
        from src.config.provider_config import (  # noqa: PLC0415
            ProviderConfig,
            UserPreferences,
            validate_provider_selection,
        )

        providers = UserPreferences.list_available_providers()

        for provider_id in providers:
            assert validate_provider_selection(provider_id) is True
            assert provider_id in ProviderConfig.PROVIDERS

    def test_auto_routing_matches_provider_config(self, config_fs: dict[str, str]) -> None:
        """Auto routing config should define correct routing logic."""
        from src.config.provider_config import ProviderConfig  # noqa: PLC0415

        routing_logic = ProviderConfig.PROVIDERS["auto"]["routing_logic"]
        assert "single_city" in routing_logic
        assert "multi_city" in routing_logic
        assert routing_logic.get("single_city") == "open-meteo"
        assert routing_logic.get("multi_city") == "meteostat"
