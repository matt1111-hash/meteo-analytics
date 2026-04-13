"""Tests for ProfileActions from anomaly_profile/profile_actions.py."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

import pytest
from src.data.anomaly_profile.profile_actions import ProfileActions
from src.data.anomaly_types import AnomalyProfileSettings


@pytest.fixture
def mock_storage() -> Mock:
    """Mock AnomalyProfileStorage."""
    storage = Mock()
    storage.save_profiles.return_value = True
    return storage


@pytest.fixture
def mock_save_func() -> Callable[[str, dict[str, Any]], bool]:
    """Mock save function."""
    return Mock(return_value=True)


@pytest.fixture
def mock_load_func() -> Callable[[str], dict[str, Any]]:
    """Mock load function."""

    def load(profile_name: str) -> dict[str, Any]:
        if profile_name == "default":
            return AnomalyProfileSettings(profile_name="default").to_dict()
        return {}

    return Mock(side_effect=load)


@pytest.fixture
def mock_get_available_func() -> Callable[[], list[str]]:
    """Mock get_available function."""
    return Mock(return_value=["default", "custom"])


@pytest.fixture
def mock_get_cache_func() -> Callable[[], dict[str, dict[str, Any]]]:
    """Mock get_cache function."""
    cache = {
        "default": AnomalyProfileSettings(profile_name="default").to_dict(),
        "custom": AnomalyProfileSettings(profile_name="custom").to_dict(),
    }
    return Mock(return_value=cache)


@pytest.fixture
def mock_active_getter() -> Callable[[], str]:
    """Mock active profile getter."""
    return Mock(return_value="default")


@pytest.fixture
def mock_active_setter() -> Callable[[str], None]:
    """Mock active profile setter."""
    return Mock()


@pytest.fixture
def profile_actions(
    mock_save_func: Callable[[str, dict[str, Any]], bool],
    mock_load_func: Callable[[str], dict[str, Any]],
    mock_get_available_func: Callable[[], list[str]],
    mock_get_cache_func: Callable[[], dict[str, dict[str, Any]]],
    mock_active_getter: Callable[[], str],
    mock_active_setter: Callable[[str], None],
) -> ProfileActions:
    """Create ProfileActions with mocked dependencies."""
    return ProfileActions(
        save_func=mock_save_func,
        load_func=mock_load_func,
        get_available_func=mock_get_available_func,
        get_cache_func=mock_get_cache_func,
        active_profile_getter=mock_active_getter,
        active_profile_setter=mock_active_setter,
    )
