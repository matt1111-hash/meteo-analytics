"""Comprehensive tests for src/config/provider_config.py."""

from __future__ import annotations

import json
from datetime import datetime


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

        parsed = datetime.fromisoformat(saved["last_updated"])
        assert isinstance(parsed, datetime)

    def test_save_preferences_overwrites_existing(
        self, config_fs: dict[str, str]
    ) -> None:
        """Saving should overwrite existing preferences file."""
        from src.config.provider_config import UserPreferences

        config_fs["prefs"] = json.dumps({"selected_provider": "meteostat"})

        new_prefs = {"selected_provider": "open-meteo", "show_usage_warnings": False}
        UserPreferences.save_provider_preferences(new_prefs)

        saved = json.loads(config_fs["prefs"])
        assert saved["selected_provider"] == "open-meteo"
        assert saved["show_usage_warnings"] is False
