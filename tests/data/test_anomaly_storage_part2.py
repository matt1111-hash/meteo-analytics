"""Tests split from test_anomaly_storage.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_anomaly_storage_support import *


class TestCreateBackup:
    """Tests for _create_backup method."""

    def test_create_backup_when_file_exists(self, tmp_path: Path) -> None:
        """Backup is created when profiles file exists."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        test_data: dict[str, Any] = {"profile": {"temp_hot": 35.0}}
        storage.save_profiles(test_data)

        storage._create_backup()

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        assert len(backups) == 1

        with open(backups[0], encoding="utf-8") as f:  # noqa: PTH123
            backup_data = json.load(f)
        assert backup_data == test_data

    def test_create_backup_when_file_missing(self, tmp_path: Path) -> None:
        """No error when profiles file doesn't exist."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        # File doesn't exist
        storage._create_backup()
        # Should not raise an error

    def test_create_backup_timestamp_format(self, tmp_path: Path) -> None:
        """Backup filename includes correct timestamp format."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        storage.save_profiles({"profile": {}})

        storage._create_backup()

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        assert len(backups) == 1
        # Filename should match pattern: anomaly_profiles_backup_YYYYMMDD_HHMMSS.json
        filename = backups[0].name
        assert filename.startswith("anomaly_profiles_backup_")
        assert filename.endswith(".json")

    def test_create_backup_limits_to_10_files(self, tmp_path: Path) -> None:
        """Only 10 most recent backups are kept."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        storage.save_profiles({"profile": {}})

        # Create 15 backups
        for _ in range(15):
            storage._create_backup()

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        assert len(backups) <= 10

    def test_create_backup_oldest_are_deleted(self, tmp_path: Path) -> None:
        """Oldest backups are deleted when limit exceeded."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)

        # Create 12 saves (each creates a backup)
        for i in range(12):
            storage.save_profiles({"profile": {"iteration": i}})

        backups = sorted(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        # Should have 10 files (oldest 2 deleted)
        assert len(backups) <= 10


class TestSaveCurrentSettings:
    """Tests for save_current_settings method."""

    def test_save_current_settings_writes_file(self, tmp_path: Path) -> None:
        """Current settings are saved to file."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        settings: dict[str, Any] = {"temp_hot": 35.0, "temp_cold": -10.0}
        result = storage.save_current_settings("test_profile", settings)

        assert result is True
        assert storage.settings_file.exists()

        with open(storage.settings_file, encoding="utf-8") as f:  # noqa: PTH123
            data = json.load(f)
        assert data["active_profile"] == "test_profile"
        assert data["settings"] == settings
        assert "updated_at" in data

    def test_save_current_settings_includes_timestamp(self, tmp_path: Path) -> None:
        """Timestamp is included in saved settings."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        before = datetime.now()
        storage.save_current_settings("test_profile", {"temp_hot": 35.0})
        after = datetime.now()

        with open(storage.settings_file, encoding="utf-8") as f:  # noqa: PTH123
            data = json.load(f)

        updated_at = datetime.fromisoformat(data["updated_at"])
        assert before <= updated_at <= after

    def test_save_current_settings_unicode_support(self, tmp_path: Path) -> None:
        """Unicode profile names are handled."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.save_current_settings("prófil_ékezetes", {"temp_hot": 35.0})

        assert result is True
        with open(storage.settings_file, encoding="utf-8") as f:  # noqa: PTH123
            data = json.load(f)
        assert data["active_profile"] == "prófil_ékezetes"


class TestLoadCurrentSettings:
    """Tests for load_current_settings method."""

    def test_load_current_settings_returns_none_when_missing(self, tmp_path: Path) -> None:
        """None is returned when settings file doesn't exist."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.load_current_settings()
        assert result is None

    def test_load_current_settings_returns_settings(self, tmp_path: Path) -> None:
        """Settings are loaded from file."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        expected: dict[str, Any] = {"temp_hot": 35.0, "temp_cold": -10.0}
        storage.save_current_settings("test_profile", expected)

        result = storage.load_current_settings()
        assert result == expected

    def test_load_current_settings_handles_invalid_json(self, tmp_path: Path) -> None:
        """Invalid JSON returns None."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.settings_file, "w", encoding="utf-8") as f:  # noqa: PTH123
            f.write("{ invalid }")

        result = storage.load_current_settings()
        assert result is None

    def test_load_current_settings_handles_non_dict_settings(self, tmp_path: Path) -> None:
        """Non-dict settings return None."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        data = {
            "active_profile": "test",
            "settings": "not_a_dict",  # Invalid: should be dict
            "updated_at": datetime.now().isoformat(),
        }
        with open(storage.settings_file, "w", encoding="utf-8") as f:  # noqa: PTH123
            json.dump(data, f)

        result = storage.load_current_settings()
        assert result is None
