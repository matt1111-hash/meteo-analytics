"""Tests split from test_profile_actions.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.anomaly_profile.test_profile_actions_support import *


class TestProfileActionsInit:
    """Test ProfileActions initialization."""

    def test_init_stores_all_dependency_functions(
        self,
        mock_save_func: Callable[[str, Dict[str, Any]], bool],
        mock_load_func: Callable[[str], Dict[str, Any]],
        mock_get_available_func: Callable[[], List[str]],
        mock_get_cache_func: Callable[[], Dict[str, Dict[str, Any]]],
        mock_active_getter: Callable[[], str],
        mock_active_setter: Callable[[str], None],
    ) -> None:
        """Initialization stores all provided dependency functions."""
        actions = ProfileActions(
            save_func=mock_save_func,
            load_func=mock_load_func,
            get_available_func=mock_get_available_func,
            get_cache_func=mock_get_cache_func,
            active_profile_getter=mock_active_getter,
            active_profile_setter=mock_active_setter,
        )

        assert actions._save == mock_save_func
        assert actions._load == mock_load_func
        assert actions._get_available == mock_get_available_func
        assert actions._get_cache == mock_get_cache_func
        assert actions._get_active == mock_active_getter
        assert actions._set_active == mock_active_setter


class TestCreateProfile:
    """Test create_profile method."""

    def test_create_profile_returns_false_when_profile_exists(
        self, profile_actions: ProfileActions
    ) -> None:
        """create_profile returns False when profile already exists."""
        result = profile_actions.create_profile("custom", "default")

        assert result is False
        profile_actions._save.assert_not_called()

    def test_create_profile_copies_base_profile_settings(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """create_profile copies settings from base profile."""
        profile_actions._get_available.return_value = ["default"]
        mock_save_func.return_value = True

        result = profile_actions.create_profile("new_profile", "default")

        assert result is True
        mock_save_func.assert_called_once()
        call_args = mock_save_func.call_args
        assert call_args[0][0] == "new_profile"
        settings = call_args[0][1]
        assert settings["profile_name"] == "new_profile"

    def test_create_profile_sets_metadata(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """create_profile sets correct metadata for new profile."""
        profile_actions._get_available.return_value = ["default"]

        result = profile_actions.create_profile("new_profile", "default")

        assert result is True
        settings = mock_save_func.call_args[0][1]
        assert "Egyedi profil - default alapján" in settings["description"]
        assert "created_at" in settings
        assert "modified_at" in settings

    def test_create_profile_returns_false_on_save_failure(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """create_profile returns False when save fails."""
        profile_actions._get_available.return_value = ["default"]
        mock_save_func.return_value = False

        result = profile_actions.create_profile("new_profile", "default")

        assert result is False

    def test_create_profile_returns_false_on_exception(
        self, profile_actions: ProfileActions, mock_load_func: Mock
    ) -> None:
        """create_profile returns False when exception occurs."""
        profile_actions._get_available.return_value = ["default"]
        mock_load_func.side_effect = Exception("Load error")

        result = profile_actions.create_profile("new_profile", "default")

        assert result is False


class TestDeleteProfile:
    """Test delete_profile method."""

    def test_delete_profile_returns_false_for_default_profile(
        self, profile_actions: ProfileActions, mock_storage: Mock
    ) -> None:
        """delete_profile returns False when trying to delete default profile."""
        result = profile_actions.delete_profile("default", mock_storage)

        assert result is False
        mock_storage.save_profiles.assert_not_called()

    def test_delete_profile_returns_false_when_profile_not_found(
        self, profile_actions: ProfileActions, mock_storage: Mock
    ) -> None:
        """delete_profile returns False when profile doesn't exist."""
        profile_actions._get_available.return_value = ["default"]

        result = profile_actions.delete_profile("nonexistent", mock_storage)

        assert result is False
        mock_storage.save_profiles.assert_not_called()

    def test_delete_profile_removes_profile_from_cache(
        self,
        profile_actions: ProfileActions,
        mock_storage: Mock,
        mock_get_cache_func: Mock,
    ) -> None:
        """delete_profile removes profile from cache."""
        cache = {"default": {}, "custom": {}, "to_delete": {}}
        mock_get_cache_func.return_value = cache
        profile_actions._get_available.return_value = ["default", "custom", "to_delete"]
        mock_storage.save_profiles.return_value = True

        result = profile_actions.delete_profile("to_delete", mock_storage)

        assert result is True
        assert "to_delete" not in cache

    def test_delete_profile_resets_to_default_when_active_deleted(
        self,
        profile_actions: ProfileActions,
        mock_storage: Mock,
        mock_active_setter: Mock,
        mock_get_cache_func: Mock,
    ) -> None:
        """delete_profile resets to default when deleting active profile."""
        cache = {"default": {}, "to_delete": {}}
        mock_get_cache_func.return_value = cache
        profile_actions._get_active.return_value = "to_delete"
        profile_actions._get_available.return_value = ["default", "to_delete"]
        mock_storage.save_profiles.return_value = True

        result = profile_actions.delete_profile("to_delete", mock_storage)

        assert result is True
        mock_active_setter.assert_called_once_with("default")

    def test_delete_profile_saves_to_storage(
        self, profile_actions: ProfileActions, mock_storage: Mock
    ) -> None:
        """delete_profile saves updated cache to storage."""
        profile_actions._get_available.return_value = ["default", "custom"]
        profile_actions._get_active.return_value = "default"
        mock_storage.save_profiles.return_value = True

        result = profile_actions.delete_profile("custom", mock_storage)

        assert result is True
        mock_storage.save_profiles.assert_called_once()

    def test_delete_profile_returns_false_on_save_failure(
        self, profile_actions: ProfileActions, mock_storage: Mock
    ) -> None:
        """delete_profile returns False when storage save fails."""
        profile_actions._get_available.return_value = ["default", "custom"]
        profile_actions._get_active.return_value = "default"
        mock_storage.save_profiles.return_value = False

        result = profile_actions.delete_profile("custom", mock_storage)

        assert result is False

    def test_delete_profile_returns_false_on_exception(
        self,
        profile_actions: ProfileActions,
        mock_storage: Mock,
        mock_get_cache_func: Mock,
    ) -> None:
        """delete_profile returns False when exception occurs."""
        mock_get_cache_func.side_effect = Exception("Cache error")

        result = profile_actions.delete_profile("custom", mock_storage)

        assert result is False
