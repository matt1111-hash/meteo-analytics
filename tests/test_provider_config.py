"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from types import MappingProxyType

import pytest


class TestFreezeValue:
    """Test cases for _freeze_value() function."""

    def test_freeze_value_with_dict(self) -> None:
        """Freezing a dict should return MappingProxyType."""
        from src.config.provider_config import _freeze_value

        result = _freeze_value({"key": "value", "nested": {"inner": "data"}})

        assert isinstance(result, MappingProxyType)
        with pytest.raises(TypeError):
            result["new_key"] = "new_value"

    def test_freeze_value_with_list(self) -> None:
        """Freezing a list should return a tuple."""
        from src.config.provider_config import _freeze_value

        result = _freeze_value([1, 2, 3, "four"])

        assert isinstance(result, tuple)
        assert result == (1, 2, 3, "four")

    def test_freeze_value_with_nested_structures(self) -> None:
        """Freezing nested structures should recursively freeze all elements."""
        from src.config.provider_config import _freeze_value

        result = _freeze_value(
            {
                "dict_value": {"inner": "data"},
                "list_value": [1, 2, {"nested": "dict"}],
                "string": "text",
                "int": 42,
            }
        )

        assert isinstance(result, MappingProxyType)
        assert isinstance(result["list_value"], tuple)
        assert isinstance(result["dict_value"], MappingProxyType)
        assert isinstance(result["list_value"][2], MappingProxyType)

    def test_freeze_value_with_primitives(self) -> None:
        """Freezing primitive values should return them unchanged."""
        from src.config.provider_config import _freeze_value

        assert _freeze_value("string") == "string"
        assert _freeze_value(42) == 42
        assert _freeze_value(3.14) == 3.14
        assert _freeze_value(True) is True
        assert _freeze_value(None) is None


class TestProviderConfig:
    """Test cases for ProviderConfig class."""

    def test_provider_data_contains_all_providers(self) -> None:
        """ProviderConfig should contain all expected providers."""
        from src.config.provider_config import ProviderConfig

        assert "auto" in ProviderConfig.PROVIDERS
        assert "open-meteo" in ProviderConfig.PROVIDERS
        assert "meteostat" in ProviderConfig.PROVIDERS

    def test_provider_data_is_immutable(self) -> None:
        """PROVIDERS should be immutable (MappingProxyType)."""
        from src.config.provider_config import ProviderConfig

        assert isinstance(ProviderConfig.PROVIDERS, MappingProxyType)
        with pytest.raises(TypeError):
            ProviderConfig.PROVIDERS["new_provider"] = {}

    def test_provider_auto_routing_logic(self) -> None:
        """Auto provider should have routing logic defined."""
        from src.config.provider_config import ProviderConfig

        auto_provider = ProviderConfig.PROVIDERS["auto"]
        assert "routing_logic" in auto_provider
        assert auto_provider["routing_logic"]["single_city"] == "open-meteo"
        assert auto_provider["routing_logic"]["multi_city"] == "meteostat"
        assert auto_provider["routing_logic"]["historical_deep"] == "meteostat"
        assert auto_provider["routing_logic"]["real_time"] == "open-meteo"

    def test_provider_open_meteo_attributes(self) -> None:
        """Open-Meteo provider should have correct attributes."""
        from src.config.provider_config import ProviderConfig

        open_meteo = ProviderConfig.PROVIDERS["open-meteo"]
        assert "Open-Meteo" in open_meteo["name"]
        assert open_meteo["icon"] == "🌍"
        assert open_meteo["cost"] == "Ingyenes"
        assert "limitations" in open_meteo

    def test_provider_meteostat_attributes(self) -> None:
        """Meteostat provider should have correct attributes."""
        from src.config.provider_config import ProviderConfig

        meteostat = ProviderConfig.PROVIDERS["meteostat"]
        assert "Meteostat" in meteostat["name"]
        assert meteostat["icon"] == "💎"
        assert "$10" in meteostat["cost"]
        assert "features" in meteostat

    def test_default_provider(self) -> None:
        """Default provider should be 'auto'."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.DEFAULT_PROVIDER == "auto"

    def test_usage_reset_day(self) -> None:
        """Usage reset day should be 1 (first of month)."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.USAGE_RESET_DAY == 1

    def test_warning_threshold(self) -> None:
        """Warning threshold should be 0.8 (80%)."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.WARNING_THRESHOLD == 0.8

    def test_critical_threshold(self) -> None:
        """Critical threshold should be 0.95 (95%)."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.CRITICAL_THRESHOLD == 0.95

    def test_meteostat_cost_per_request(self) -> None:
        """Meteostat cost per request should be defined."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.METEOSTAT_COST_PER_REQUEST == 0.001

    def test_monthly_budget_usd(self) -> None:
        """Monthly budget should be $10 USD."""
        from src.config.provider_config import ProviderConfig

        assert ProviderConfig.MONTHLY_BUDGET_USD == 10.0

    def test_provider_data_frozen(self) -> None:
        """Nested provider data should be frozen (immutable)."""
        from src.config.provider_config import ProviderConfig

        # Provider dict itself should be immutable
        with pytest.raises(TypeError):
            ProviderConfig.PROVIDERS["auto"]["new_key"] = "value"

        # Nested structures should also be immutable
        auto_routing = ProviderConfig.PROVIDERS["auto"]["routing_logic"]
        with pytest.raises(TypeError):
            auto_routing["new_route"] = "provider"


class TestUserPreferencesLoad:
    """Test cases for UserPreferences.load_provider_preferences() method."""

    def test_load_preferences_returns_defaults_when_file_missing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Missing preferences file should return default preferences."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        # Remove prefs file if it exists
        config_fs.pop("prefs", None)

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == ProviderConfig.DEFAULT_PROVIDER
        assert prefs["auto_fallback_enabled"] is True
        assert prefs["show_usage_warnings"] is True
        assert prefs["show_cost_estimates"] is True
        assert prefs["monthly_budget_usd"] == ProviderConfig.MONTHLY_BUDGET_USD
        assert prefs["warning_threshold"] == ProviderConfig.WARNING_THRESHOLD
        assert "last_updated" in prefs

    def test_load_preferences_merges_with_saved_values(
        self, config_fs: dict[str, str]
    ) -> None:
        """Saved preferences should be merged with defaults."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs["prefs"] = json.dumps(
            {"selected_provider": "meteostat", "auto_fallback_enabled": False}
        )

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == "meteostat"
        assert prefs["auto_fallback_enabled"] is False
        # Other fields should have defaults
        assert prefs["show_usage_warnings"] is True
        assert prefs["monthly_budget_usd"] == ProviderConfig.MONTHLY_BUDGET_USD

    def test_load_preferences_handles_corrupted_json(
        self, config_fs: dict[str, str]
    ) -> None:
        """Corrupted JSON should return default preferences."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        config_fs["prefs"] = "{ not valid json"

        prefs = UserPreferences.load_provider_preferences()

        assert prefs["selected_provider"] == ProviderConfig.DEFAULT_PROVIDER

    def test_load_preferences_includes_timestamp(
        self, config_fs: dict[str, str]
    ) -> None:
        """Preferences should include last_updated timestamp."""
        from src.config.provider_config import UserPreferences

        prefs = UserPreferences.load_provider_preferences()

        assert "last_updated" in prefs
        # Should be a valid ISO format datetime string
        datetime.fromisoformat(prefs["last_updated"])


class TestUserPreferencesSave:
    """Test cases for UserPreferences.save_provider_preferences() method."""

    def test_save_preferences_writes_to_file(self, config_fs: dict[str, str]) -> None:
        """Saving preferences should write to file with timestamp."""
        from src.config.provider_config import UserPreferences

        payload = {"selected_provider": "meteostat", "auto_fallback_enabled": False}

        result = UserPreferences.save_provider_preferences(payload)

        assert result is True
        assert "prefs" in config_fs

        saved = json.loads(config_fs["prefs"])
        assert saved["selected_provider"] == "meteostat"
        assert saved["auto_fallback_enabled"] is False
        assert "last_updated" in saved

    def test_save_preferences_adds_timestamp(self, config_fs: dict[str, str]) -> None:
        """Saving preferences should add/update last_updated timestamp."""
        from src.config.provider_config import UserPreferences

        payload = {"selected_provider": "open-meteo"}

        UserPreferences.save_provider_preferences(payload)

        saved = json.loads(config_fs["prefs"])
        assert "last_updated" in saved

        # Verify it's a valid ISO format datetime
        parsed = datetime.fromisoformat(saved["last_updated"])
        assert isinstance(parsed, datetime)

    def test_save_preferences_overwrites_existing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Saving should overwrite existing preferences file."""
        from src.config.provider_config import UserPreferences

        # Create initial file
        config_fs["prefs"] = json.dumps({"selected_provider": "meteostat"})

        # Save new preferences
        new_prefs = {"selected_provider": "open-meteo", "show_usage_warnings": False}
        UserPreferences.save_provider_preferences(new_prefs)

        saved = json.loads(config_fs["prefs"])
        assert saved["selected_provider"] == "open-meteo"
        assert saved["show_usage_warnings"] is False


class TestUserPreferencesGetSelected:
    """Test cases for UserPreferences.get_selected_provider() method."""

    def test_get_selected_provider_returns_saved_value(
        self, config_fs: dict[str, str]
    ) -> None:
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


class TestUserPreferencesGetProviderInfo:
    """Test cases for UserPreferences.get_provider_info() method."""

    def test_get_provider_info_valid_provider(self) -> None:
        """Should return provider info for valid provider."""
        from src.config.provider_config import UserPreferences

        info = UserPreferences.get_provider_info("auto")

        assert info is not None
        assert info["name"] == "Automatikus (Smart Routing)"
        assert info["icon"] == "🤖"

    def test_get_provider_info_invalid_provider(self) -> None:
        """Should return None for invalid provider."""
        from src.config.provider_config import UserPreferences

        info = UserPreferences.get_provider_info("invalid")

        assert info is None

    def test_get_provider_info_returns_mutable_copy(self) -> None:
        """Returned provider info should be a mutable dict copy."""
        from src.config.provider_config import UserPreferences

        info = UserPreferences.get_provider_info("auto")

        # Should be a regular dict, not MappingProxyType
        assert isinstance(info, dict)
        # Should be modifiable
        info["new_key"] = "new_value"
        assert info["new_key"] == "new_value"

    def test_get_provider_info_all_providers(self) -> None:
        """Should return info for all valid providers."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        for provider in ProviderConfig.PROVIDERS:
            info = UserPreferences.get_provider_info(provider)
            assert info is not None
            assert "name" in info
            assert "icon" in info


class TestUserPreferencesListProviders:
    """Test cases for UserPreferences.list_available_providers() method."""

    def test_list_available_providers_returns_all(self) -> None:
        """Should return all available providers."""
        from src.config.provider_config import ProviderConfig, UserPreferences

        providers = UserPreferences.list_available_providers()

        assert set(providers.keys()) == set(ProviderConfig.PROVIDERS.keys())

    def test_list_available_providers_returns_mutable_copies(self) -> None:
        """Returned providers should be mutable dict copies."""
        from src.config.provider_config import UserPreferences

        providers = UserPreferences.list_available_providers()

        # Should be regular dicts
        assert isinstance(providers, dict)
        # Values should be mutable
        providers["auto"]["new_key"] = "new_value"
        assert providers["auto"]["new_key"] == "new_value"

    def test_list_available_providers_contains_all_info(self) -> None:
        """Returned providers should contain all expected info."""
        from src.config.provider_config import UserPreferences

        providers = UserPreferences.list_available_providers()

        for provider_id, provider_info in providers.items():
            assert "name" in provider_info
            assert "icon" in provider_info


class TestGetResolvedProvider:
    """Test cases for get_resolved_provider() function."""

    def test_resolved_provider_user_override_takes_precedence(
        self, config_fs: dict[str, str]
    ) -> None:
        """User override should take precedence over saved preference."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "meteostat"})

        result = get_resolved_provider("single_city", user_override="open-meteo")

        assert result == "open-meteo"

    def test_resolved_provider_auto_routing_single_city(
        self, config_fs: dict[str, str]
    ) -> None:
        """Auto routing for single_city should return open-meteo."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("single_city")

        assert result == "open-meteo"

    def test_resolved_provider_auto_routing_multi_city(
        self, config_fs: dict[str, str]
    ) -> None:
        """Auto routing for multi_city should return meteostat."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("multi_city")

        assert result == "meteostat"

    def test_resolved_provider_auto_routing_historical_deep(
        self, config_fs: dict[str, str]
    ) -> None:
        """Auto routing for historical_deep should return meteostat."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("historical_deep")

        assert result == "meteostat"

    def test_resolved_provider_auto_routing_real_time(
        self, config_fs: dict[str, str]
    ) -> None:
        """Auto routing for real_time should return open-meteo."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("real_time")

        assert result == "open-meteo"

    def test_resolved_provider_fixed_selection(self, config_fs: dict[str, str]) -> None:
        """Fixed provider selection should bypass routing."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "meteostat"})

        result = get_resolved_provider("single_city")

        assert result == "meteostat"

    def test_resolved_provider_unknown_use_case_defaults_to_open_meteo(
        self, config_fs: dict[str, str]
    ) -> None:
        """Unknown use case should default to open-meteo."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("unknown_use_case")

        assert result == "open-meteo"


class TestValidateProviderSelection:
    """Test cases for validate_provider_selection() function."""

    def test_validate_provider_valid_providers(self) -> None:
        """All valid providers should pass validation."""
        from src.config.provider_config import (
            ProviderConfig,
            validate_provider_selection,
        )

        for provider in ProviderConfig.PROVIDERS:
            assert validate_provider_selection(provider) is True

    def test_validate_provider_invalid_provider(self) -> None:
        """Invalid provider should fail validation."""
        from src.config.provider_config import validate_provider_selection

        assert validate_provider_selection("invalid_provider") is False
        assert validate_provider_selection("") is False
        assert validate_provider_selection("unknown") is False


class TestModuleHelpers:
    """Test cases for module helper functions."""

    def test_resolve_config_attr_with_fallback(self) -> None:
        """Should return fallback when attribute not in config module."""
        from src.config.provider_config import _resolve_config_attr

        result = _resolve_config_attr("nonexistent_attr", "fallback_value")
        assert result == "fallback_value"

    def test_get_provider_prefs_file_returns_path(self) -> None:
        """Should return a Path object."""
        from src.config.provider_config import _get_provider_prefs_file

        result = _get_provider_prefs_file()
        assert isinstance(result, Path)

    def test_freeze_value_preserves_data(self) -> None:
        """Freezing should preserve the original data structure."""
        from src.config.provider_config import _freeze_value

        original = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        frozen = _freeze_value(original)

        assert frozen["string"] == "value"
        assert frozen["number"] == 42
        assert frozen["list"] == (1, 2, 3)
        assert frozen["nested"]["key"] == "value"


class TestIntegration:
    """Integration tests for provider_config module."""

    def test_set_and_get_selected_provider_roundtrip(
        self, config_fs: dict[str, str]
    ) -> None:
        """Setting and getting provider should work correctly."""
        from src.config.provider_config import UserPreferences

        # Set provider
        UserPreferences.set_selected_provider("meteostat")

        # Get provider
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

        # Save
        UserPreferences.save_provider_preferences(original_prefs)

        # Load
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

        # Set selected provider to "auto" to enable smart routing
        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        routing_logic = ProviderConfig.PROVIDERS["auto"]["routing_logic"]

        for use_case, expected_provider in routing_logic.items():
            result = get_resolved_provider(use_case)
            assert result == expected_provider
