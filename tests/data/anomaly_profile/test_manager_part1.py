"""Tests split from test_manager.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.anomaly_profile.test_manager_support import *


class TestAnomalyProfileManagerInit:
    """Test AnomalyProfileManager initialization."""

    def test_init_creates_storage(self, temp_dir: Path) -> None:
        """Initialization creates storage."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        assert manager.storage is not None
        assert manager.storage.config_dir == temp_dir

    def test_init_creates_default_profiles_when_none_exist(self, temp_dir: Path) -> None:
        """Initialization creates default profiles when storage is empty."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        assert "default" in manager._profiles_cache
        assert manager._active_profile == "default"

    def test_init_loads_existing_profiles(self, temp_dir: Path) -> None:
        """Initialization loads existing profiles from storage."""
        from src.infrastructure.anomaly.anomaly_storage import (  # noqa: PLC0415
            AnomalyProfileStorage,
        )

        storage = AnomalyProfileStorage(config_dir=temp_dir)
        profiles_data = {
            "profiles": {"custom": AnomalyProfileSettings(profile_name="custom").to_dict()},
            "active_profile": "custom",
            "version": "1.0",
        }
        storage.save_profiles(profiles_data)

        manager = AnomalyProfileManager(config_dir=temp_dir)

        assert "custom" in manager._profiles_cache
        assert manager._active_profile == "custom"


class TestGetAvailableProfiles:
    """Test get_available_profiles method."""

    def test_get_available_profiles_returns_list_of_profile_names(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """get_available_profiles returns list of profile names."""
        result = manager_with_profiles.get_available_profiles()

        assert "default" in result
        assert "custom" in result

    def test_get_available_profiles_returns_empty_list_when_no_profiles(
        self, temp_dir: Path
    ) -> None:
        """get_available_profiles returns empty list when no profiles exist."""
        from src.infrastructure.anomaly.anomaly_storage import (  # noqa: PLC0415
            AnomalyProfileStorage,
        )

        storage = AnomalyProfileStorage(config_dir=temp_dir)
        storage.save_profiles({"profiles": {}, "active_profile": "default"})

        manager = AnomalyProfileManager(config_dir=temp_dir)

        result = manager.get_available_profiles()

        assert result == []


class TestGetActiveProfile:
    """Test get_active_profile method."""

    def test_get_active_profile_returns_active_profile_name(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """get_active_profile returns the name of the active profile."""
        manager_with_profiles._active_profile = "custom"

        result = manager_with_profiles.get_active_profile()

        assert result == "custom"

    def test_get_active_profile_returns_default_when_none_set(self, temp_dir: Path) -> None:
        """get_active_profile returns 'default' when no active profile is set."""
        from src.infrastructure.anomaly.anomaly_storage import (  # noqa: PLC0415
            AnomalyProfileStorage,
        )

        storage = AnomalyProfileStorage(config_dir=temp_dir)
        storage.save_profiles({"profiles": {}, "active_profile": None})

        manager = AnomalyProfileManager(config_dir=temp_dir)
        manager._active_profile = None

        result = manager.get_active_profile()

        assert result == "default"


class TestLoadProfile:
    """Test load_profile method."""

    def test_load_profile_returns_profile_settings(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """load_profile returns settings for requested profile."""
        result = manager_with_profiles.load_profile("custom")

        assert result["profile_name"] == "custom"
        assert isinstance(result, dict)

    def test_load_profile_returns_copy_not_reference(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """load_profile returns a copy, not the original reference."""
        result = manager_with_profiles.load_profile("custom")
        original_temp_hot = result["temp_hot"]
        result["temp_hot"] = 999.0

        # Reload to verify original wasn't modified
        reloaded = manager_with_profiles.load_profile("custom")
        assert reloaded["temp_hot"] == original_temp_hot
        assert reloaded["temp_hot"] != 999.0

    def test_load_profile_returns_default_when_profile_not_found(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """load_profile returns default profile when requested profile doesn't exist."""
        result = manager_with_profiles.load_profile("nonexistent")

        assert result["profile_name"] == "default"


class TestSetActiveProfile:
    """Test set_active_profile method."""

    def test_set_active_profile_returns_false_for_unknown_profile(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """set_active_profile returns False when profile doesn't exist."""
        result = manager_with_profiles.set_active_profile("unknown")

        assert result is False

    def test_set_active_profile_updates_active_profile(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """set_active_profile updates the active profile."""
        result = manager_with_profiles.set_active_profile("custom")

        assert result is True
        assert manager_with_profiles._active_profile == "custom"


class TestSaveProfile:
    """Test save_profile method."""

    def test_save_profile_validates_settings(self, temp_dir: Path) -> None:
        """save_profile validates settings before saving."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        # Invalid settings: temp_hot <= temp_cold
        invalid_settings = {"temp_hot": 10.0, "temp_cold": 20.0, "profile_name": "test"}

        result = manager.save_profile("test", invalid_settings)

        assert result is False

    def test_save_profile_saves_valid_settings(self, temp_dir: Path) -> None:
        """save_profile saves valid settings to cache and storage."""
        manager = AnomalyProfileManager(config_dir=temp_dir)

        valid_settings = AnomalyProfileSettings(profile_name="test").to_dict()

        result = manager.save_profile("test", valid_settings)

        assert result is True
        assert "test" in manager._profiles_cache


class TestGetCurrentSettings:
    """Test get_current_settings method."""

    def test_get_current_settings_loads_active_profile(
        self, manager_with_profiles: AnomalyProfileManager
    ) -> None:
        """get_current_settings loads active profile settings."""
        manager_with_profiles._active_profile = "custom"

        result = manager_with_profiles.get_current_settings()

        assert result["profile_name"] == "custom"
