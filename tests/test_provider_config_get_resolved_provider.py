"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json


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

    def test_resolved_provider_auto_routing_single_city(self, config_fs: dict[str, str]) -> None:
        """Auto routing for single_city should return open-meteo."""
        from src.config.provider_config import get_resolved_provider

        config_fs["prefs"] = json.dumps({"selected_provider": "auto"})

        result = get_resolved_provider("single_city")

        assert result == "open-meteo"

    def test_resolved_provider_auto_routing_multi_city(self, config_fs: dict[str, str]) -> None:
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

    def test_resolved_provider_auto_routing_real_time(self, config_fs: dict[str, str]) -> None:
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
