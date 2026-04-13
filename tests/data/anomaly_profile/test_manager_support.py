"""Tests for AnomalyProfileManager from anomaly_profile/manager.py."""

from __future__ import annotations

from pathlib import Path

import pytest
from src.data.anomaly_profile.manager import AnomalyProfileManager
from src.data.anomaly_types import AnomalyProfileSettings


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Temporary directory for test files."""
    return tmp_path / "config"


@pytest.fixture
def manager_with_empty_storage(temp_dir: Path) -> AnomalyProfileManager:
    """Create manager with empty storage."""
    return AnomalyProfileManager(config_dir=temp_dir)


@pytest.fixture
def manager_with_profiles(temp_dir: Path) -> AnomalyProfileManager:
    """Create manager with existing profiles."""
    from src.data.anomaly_storage import AnomalyProfileStorage  # noqa: PLC0415

    storage = AnomalyProfileStorage(config_dir=temp_dir)
    default_profiles = {
        "profiles": {
            "default": AnomalyProfileSettings(profile_name="default").to_dict(),
            "custom": AnomalyProfileSettings(profile_name="custom").to_dict(),
        },
        "active_profile": "default",
        "version": "1.0",
    }
    storage.save_profiles(default_profiles)

    return AnomalyProfileManager(config_dir=temp_dir)
