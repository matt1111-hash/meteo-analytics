"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations


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

        assert isinstance(info, dict)
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
