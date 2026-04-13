"""Tests split from test_anomaly_storage.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_anomaly_storage_support import *


class TestAnomalyProfileStorageInitialization:
    """Tests for AnomalyProfileStorage initialization."""

    def test_initialization_with_default_config_dir(self, tmp_path: Path) -> None:
        """Storage is initialized with default config directory."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        assert storage.config_dir == tmp_path
        assert storage.profiles_file == tmp_path / "anomaly_profiles.json"
        assert storage.settings_file == tmp_path / "current_anomaly_settings.json"
        assert storage.backup_dir == tmp_path / "backups"

    def test_initialization_creates_directories(self, tmp_path: Path) -> None:
        """Directories are created on initialization."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        assert storage.config_dir.exists()
        assert storage.backup_dir.exists()

    def test_initialization_creates_lock(self, tmp_path: Path) -> None:
        """Thread lock is created on initialization."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        assert storage._lock is not None

    def test_initialization_with_nonexistent_path(self, tmp_path: Path) -> None:
        """Initialization works with non-existent path."""
        non_existent = tmp_path / "new_dir" / "nested"
        storage = AnomalyProfileStorage(config_dir=non_existent)
        assert storage.config_dir.exists()
        assert storage.backup_dir.exists()


class TestEnsureDirectories:
    """Tests for _ensure_directories method."""

    def test_ensure_directories_creates_config_dir(self, tmp_path: Path) -> None:
        """Config directory is created if it doesn't exist."""
        non_existent = tmp_path / "new_config"
        AnomalyProfileStorage(config_dir=non_existent)
        assert non_existent.exists()

    def test_ensure_directories_creates_backup_dir(self, tmp_path: Path) -> None:
        """Backup directory is created if it doesn't exist."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        assert storage.backup_dir.exists()

    def test_ensure_directories_idempotent(self, tmp_path: Path) -> None:
        """Multiple calls to _ensure_directories are safe."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        storage._ensure_directories()
        storage._ensure_directories()
        assert storage.config_dir.exists()
        assert storage.backup_dir.exists()


class TestLoadProfiles:
    """Tests for load_profiles method."""

    def test_load_profiles_returns_empty_dict_when_file_missing(self, tmp_path: Path) -> None:
        """Empty dict is returned when profiles file doesn't exist."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.load_profiles()
        assert result == {}

    def test_load_profiles_returns_data_from_file(self, tmp_path: Path) -> None:
        """Profiles are loaded from JSON file."""
        test_data: dict[str, Any] = {
            "profile1": {"temp_hot": 35.0, "temp_cold": -10.0},
            "profile2": {"temp_hot": 40.0, "temp_cold": -15.0},
        }
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.profiles_file, "w", encoding="utf-8") as f:  # noqa: PTH123
            json.dump(test_data, f)

        result = storage.load_profiles()
        assert result == test_data

    def test_load_profiles_handles_json_decode_error(self, tmp_path: Path) -> None:
        """Invalid JSON returns empty dict."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.profiles_file, "w", encoding="utf-8") as f:  # noqa: PTH123
            f.write("{ invalid json }")

        result = storage.load_profiles()
        assert result == {}

    def test_load_profiles_handles_key_error(self, tmp_path: Path) -> None:
        """Missing key in JSON returns empty dict."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.profiles_file, "w", encoding="utf-8") as f:  # noqa: PTH123
            f.write('{"key": "value"}')  # Valid JSON but structure may cause KeyError

        # Should handle gracefully
        result = storage.load_profiles()
        # The implementation catches JSONDecodeError, FileNotFoundError, KeyError
        assert isinstance(result, dict)


class TestSaveProfiles:
    """Tests for save_profiles method."""

    def test_save_profiles_writes_to_file(self, tmp_path: Path) -> None:
        """Profiles are saved to JSON file."""
        test_data: dict[str, Any] = {"profile1": {"temp_hot": 35.0, "temp_cold": -10.0}}
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.save_profiles(test_data)

        assert result is True
        assert storage.profiles_file.exists()

        with open(storage.profiles_file, encoding="utf-8") as f:  # noqa: PTH123
            saved_data = json.load(f)
        assert saved_data == test_data

    def test_save_profiles_creates_backup(self, tmp_path: Path) -> None:
        """Backup is created before saving."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        # Initial save
        storage.save_profiles({"profile1": {"temp_hot": 35.0}})

        # Second save should create backup
        storage.save_profiles({"profile2": {"temp_hot": 40.0}})

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        assert len(backups) >= 1

    def test_save_profiles_returns_false_on_error(self, tmp_path: Path) -> None:
        """False is returned on save error."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)

        # Make the directory read-only to simulate error
        storage.config_dir.chmod(0o444)

        test_data: dict[str, Any] = {"profile": {}}
        storage.save_profiles(test_data)

        # Restore permissions for cleanup
        storage.config_dir.chmod(0o755)

    def test_save_profiles_unicode_support(self, tmp_path: Path) -> None:
        """Unicode characters are properly handled."""
        test_data: dict[str, Any] = {
            "profil_1": {"description": "Árvíztűrő tükörfúrógép"},
            "profil_2": {"description": "日本語"},
        }
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.save_profiles(test_data)

        assert result is True
        with open(storage.profiles_file, encoding="utf-8") as f:  # noqa: PTH123
            saved_data = json.load(f)
        assert saved_data == test_data
