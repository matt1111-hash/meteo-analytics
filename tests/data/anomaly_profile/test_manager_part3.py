"""Tests split from test_manager.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.anomaly_profile.test_manager_support import *


class TestSaveProfileEdgeCases:
    """Test edge cases for save_profile method."""

    def test_save_profile_handles_validation_errors(self, temp_dir: Path) -> None:
        """save_profile returns False when validation fails."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        # Settings that will fail validation
        invalid_settings = {
            "profile_name": "test",
            "temp_hot": 10.0,
            "temp_cold": 20.0,  # temp_cold > temp_hot, invalid
        }

        result = manager.save_profile("test", invalid_settings)

        assert result is False

    def test_save_profile_handles_exception_during_save(self, temp_dir: Path) -> None:
        """save_profile returns False when exception occurs."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        valid_settings = AnomalyProfileSettings(profile_name="test").to_dict()

        # Mock save_profiles to raise exception
        with patch.object(manager.storage, "save_profiles", side_effect=Exception("Test error")):
            result = manager.save_profile("test", valid_settings)

        assert result is False


class TestGetCurrentSettingsEdgeCases:
    """Test edge cases for get_current_settings method."""

    def test_get_current_settings_handles_load_exception(self, temp_dir: Path) -> None:
        """get_current_settings falls back to default on exception."""
        from src.data.anomaly_storage import AnomalyProfileStorage

        storage = AnomalyProfileStorage(config_dir=temp_dir)
        profiles_data = {
            "profiles": {"custom": AnomalyProfileSettings(profile_name="custom").to_dict()},
            "active_profile": "custom",
            "version": "1.0",
        }
        storage.save_profiles(profiles_data)

        manager = AnomalyProfileManager(config_dir=temp_dir)

        # Mock load_current_settings to raise exception
        with patch.object(
            manager.storage,
            "load_current_settings",
            side_effect=Exception("Test error"),
        ):
            result = manager.get_current_settings()

        # Should fall back to loading active profile, which succeeds
        assert result is not None

    def test_get_current_settings_propagates_exception_on_complete_failure(
        self, temp_dir: Path
    ) -> None:
        """get_current_settings propagates exception when everything fails."""
        from src.data.anomaly_storage import AnomalyProfileStorage

        storage = AnomalyProfileStorage(config_dir=temp_dir)
        profiles_data = {
            "profiles": {"default": AnomalyProfileSettings(profile_name="default").to_dict()},
            "active_profile": "default",
            "version": "1.0",
        }
        storage.save_profiles(profiles_data)

        manager = AnomalyProfileManager(config_dir=temp_dir)

        # Mock load_profile to raise exception (this is the final fallback)
        with patch.object(manager, "load_profile", side_effect=Exception("Complete failure")):
            with pytest.raises(Exception, match="Complete failure"):
                manager.get_current_settings()
