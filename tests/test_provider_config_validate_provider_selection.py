"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations


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
