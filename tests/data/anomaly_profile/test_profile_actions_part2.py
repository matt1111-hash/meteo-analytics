"""Tests split from test_profile_actions.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.anomaly_profile.test_profile_actions_support import *


class TestRenameProfile:
    """Test rename_profile method."""

    def test_rename_profile_returns_false_for_default_profile(
        self, profile_actions: ProfileActions
    ) -> None:
        """rename_profile returns False when trying to rename default profile."""
        result = profile_actions.rename_profile("default", "new_name")

        assert result is False
        profile_actions._save.assert_not_called()

    def test_rename_profile_returns_false_when_new_name_exists(
        self, profile_actions: ProfileActions
    ) -> None:
        """rename_profile returns False when new profile name already exists."""
        result = profile_actions.rename_profile("custom", "default")

        assert result is False
        profile_actions._save.assert_not_called()

    def test_rename_profile_creates_new_profile_and_deletes_old(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """rename_profile creates new profile and deletes old one."""
        profile_actions._get_available.return_value = ["default", "old_name"]
        mock_save_func.return_value = True

        # Mock delete_profile to avoid actual deletion
        with patch.object(profile_actions, "delete_profile", return_value=True) as mock_delete:
            result = profile_actions.rename_profile("old_name", "new_name")

            assert result is True
            mock_delete.assert_called_once_with("old_name", storage=None)

    def test_rename_profile_updates_profile_name_in_settings(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """rename_profile updates profile_name in settings."""
        profile_actions._get_available.return_value = ["default", "old_name"]
        mock_save_func.return_value = True

        with patch.object(profile_actions, "delete_profile", return_value=True):
            result = profile_actions.rename_profile("old_name", "new_name")

            assert result is True
            saved_settings = mock_save_func.call_args[0][1]
            assert saved_settings["profile_name"] == "new_name"

    def test_rename_profile_updates_modified_timestamp(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """rename_profile updates modified_at timestamp."""
        profile_actions._get_available.return_value = ["default", "old_name"]
        mock_save_func.return_value = True

        with patch.object(profile_actions, "delete_profile", return_value=True):
            result = profile_actions.rename_profile("old_name", "new_name")

            assert result is True
            saved_settings = mock_save_func.call_args[0][1]
            assert "modified_at" in saved_settings

    def test_rename_profile_returns_false_when_save_fails(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """rename_profile returns False when saving new profile fails."""
        profile_actions._get_available.return_value = ["default", "old_name"]
        mock_save_func.return_value = False

        result = profile_actions.rename_profile("old_name", "new_name")

        assert result is False

    def test_rename_profile_returns_false_on_exception(
        self, profile_actions: ProfileActions, mock_load_func: Mock
    ) -> None:
        """rename_profile returns False when exception occurs."""
        profile_actions._get_available.return_value = ["default", "old_name"]
        mock_load_func.side_effect = Exception("Load error")

        result = profile_actions.rename_profile("old_name", "new_name")

        assert result is False


class TestResetProfileToDefaults:
    """Test reset_profile_to_defaults method."""

    def test_reset_profile_to_defaults_creates_new_default_settings(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """reset_profile_to_defaults creates new AnomalyProfileSettings with defaults."""
        mock_save_func.return_value = True

        result = profile_actions.reset_profile_to_defaults("custom")

        assert result is True
        mock_save_func.assert_called_once()
        call_args = mock_save_func.call_args
        assert call_args[0][0] == "custom"
        settings = call_args[0][1]
        # Check that default values are set
        assert settings["temp_hot"] == 35.0
        assert settings["temp_cold"] == -10.0

    def test_reset_profile_to_defaults_preserves_profile_name(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """reset_profile_to_defaults preserves the profile name."""
        mock_save_func.return_value = True

        result = profile_actions.reset_profile_to_defaults("custom")

        assert result is True
        settings = mock_save_func.call_args[0][1]
        assert settings["profile_name"] == "custom"

    def test_reset_profile_to_defaults_returns_false_on_save_failure(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """reset_profile_to_defaults returns False when save fails."""
        mock_save_func.return_value = False

        result = profile_actions.reset_profile_to_defaults("custom")

        assert result is False

    def test_reset_profile_to_defaults_returns_false_on_exception(
        self, profile_actions: ProfileActions, mock_save_func: Mock
    ) -> None:
        """reset_profile_to_defaults returns False when exception occurs."""
        mock_save_func.side_effect = Exception("Save error")

        result = profile_actions.reset_profile_to_defaults("custom")

        assert result is False
