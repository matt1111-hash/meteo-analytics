"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

from types import MappingProxyType

import pytest


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
