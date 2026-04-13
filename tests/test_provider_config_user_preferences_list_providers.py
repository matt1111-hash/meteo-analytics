"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations


class TestUserPreferencesListProviders:
    """Test cases for UserPreferences.list_available_providers() method."""

    def test_list_available_providers_returns_all(self) -> None:
        """Should return all available providers."""
        from src.config.provider_config import ProviderConfig, UserPreferences  # noqa: PLC0415

        providers = UserPreferences.list_available_providers()

        assert set(providers.keys()) == set(ProviderConfig.PROVIDERS.keys())

    def test_list_available_providers_returns_mutable_copies(self) -> None:
        """Returned providers should be mutable dict copies."""
        from src.config.provider_config import UserPreferences  # noqa: PLC0415

        providers = UserPreferences.list_available_providers()

        assert isinstance(providers, dict)
        providers["auto"]["new_key"] = "new_value"
        assert providers["auto"]["new_key"] == "new_value"

    def test_list_available_providers_contains_all_info(self) -> None:
        """Returned providers should contain all expected info."""
        from src.config.provider_config import UserPreferences  # noqa: PLC0415

        providers = UserPreferences.list_available_providers()

        for provider_id, provider_info in providers.items():  # noqa: B007, PERF102
            assert "name" in provider_info
            assert "icon" in provider_info
