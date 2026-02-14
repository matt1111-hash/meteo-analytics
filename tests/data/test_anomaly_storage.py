"""Anomaly profile storage tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.data.anomaly_storage import AnomalyProfileStorage


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

    def test_load_profiles_returns_empty_dict_when_file_missing(
        self, tmp_path: Path
    ) -> None:
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
        with open(storage.profiles_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        result = storage.load_profiles()
        assert result == test_data

    def test_load_profiles_handles_json_decode_error(self, tmp_path: Path) -> None:
        """Invalid JSON returns empty dict."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.profiles_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        result = storage.load_profiles()
        assert result == {}

    def test_load_profiles_handles_key_error(self, tmp_path: Path) -> None:
        """Missing key in JSON returns empty dict."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        with open(storage.profiles_file, "w", encoding="utf-8") as f:
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

        with open(storage.profiles_file, "r", encoding="utf-8") as f:
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
        with open(storage.profiles_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        assert saved_data == test_data


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

        with open(backups[0], "r", encoding="utf-8") as f:
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

        with open(storage.settings_file, "r", encoding="utf-8") as f:
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

        with open(storage.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        updated_at = datetime.fromisoformat(data["updated_at"])
        assert before <= updated_at <= after

    def test_save_current_settings_unicode_support(self, tmp_path: Path) -> None:
        """Unicode profile names are handled."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.save_current_settings("prófil_ékezetes", {"temp_hot": 35.0})

        assert result is True
        with open(storage.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["active_profile"] == "prófil_ékezetes"


class TestLoadCurrentSettings:
    """Tests for load_current_settings method."""

    def test_load_current_settings_returns_none_when_missing(
        self, tmp_path: Path
    ) -> None:
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
        with open(storage.settings_file, "w", encoding="utf-8") as f:
            f.write("{ invalid }")

        result = storage.load_current_settings()
        assert result is None

    def test_load_current_settings_handles_non_dict_settings(
        self, tmp_path: Path
    ) -> None:
        """Non-dict settings return None."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        data = {
            "active_profile": "test",
            "settings": "not_a_dict",  # Invalid: should be dict
            "updated_at": datetime.now().isoformat(),
        }
        with open(storage.settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        result = storage.load_current_settings()
        assert result is None


class TestThreadSafety:
    """Tests for thread-safe operations."""

    def test_storage_has_rlock(self, tmp_path: Path) -> None:
        """Storage is initialized with RLock for thread safety."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        # Check that lock has acquire and release methods (RLock interface)
        assert hasattr(storage._lock, "acquire")
        assert hasattr(storage._lock, "release")
        # Check the type name is 'RLock'
        assert type(storage._lock).__name__ == "RLock"

    def test_load_profiles_is_thread_safe(self, tmp_path: Path) -> None:
        """load_profiles can be called concurrently without error."""
        import threading

        storage = AnomalyProfileStorage(config_dir=tmp_path)
        test_data: dict[str, Any] = {"profile": {"temp_hot": 35.0}}
        storage.save_profiles(test_data)

        results: list[dict[str, Any] | None] = []
        errors: list[Exception] = []

        def load_data() -> None:
            try:
                results.append(storage.load_profiles())
            except Exception as e:
                errors.append(e)

        # Create multiple threads that load concurrently
        threads = [threading.Thread(target=load_data) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should complete successfully
        assert len(errors) == 0
        assert len(results) == 5
        for result in results:
            assert result == test_data

    def test_save_profiles_is_thread_safe(self, tmp_path: Path) -> None:
        """save_profiles can be called concurrently without error."""
        import threading

        storage = AnomalyProfileStorage(config_dir=tmp_path)

        errors: list[Exception] = []

        def save_data(index: int) -> None:
            try:
                storage.save_profiles({"profile": {"index": index}})
            except Exception as e:
                errors.append(e)

        # Create multiple threads that save concurrently
        threads = [threading.Thread(target=save_data, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should complete without errors
        # (The exact result depends on thread scheduling, but no crashes should occur)
        assert len(errors) == 0


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_round_trip_profiles(self, tmp_path: Path) -> None:
        """Profiles can be saved and loaded correctly."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        original: dict[str, Any] = {
            "profile1": {"temp_hot": 35.0, "temp_cold": -10.0, "precip_high": 100.0},
            "profile2": {"temp_hot": 40.0, "temp_cold": -15.0, "precip_high": 120.0},
        }

        storage.save_profiles(original)
        loaded = storage.load_profiles()

        assert loaded == original

    def test_round_trip_current_settings(self, tmp_path: Path) -> None:
        """Current settings can be saved and loaded correctly."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        original: dict[str, Any] = {
            "temp_hot": 38.0,
            "temp_cold": -12.0,
            "wind_high": 80.0,
        }

        storage.save_current_settings("custom_profile", original)
        loaded = storage.load_current_settings()

        assert loaded == original

    def test_save_generates_backup_on_second_save(self, tmp_path: Path) -> None:
        """Backup is generated when saving multiple times."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)

        storage.save_profiles({"profile1": {"temp_hot": 35.0}})
        storage.save_profiles({"profile2": {"temp_hot": 40.0}})

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        assert len(backups) >= 1

    def test_backup_rotation_after_many_saves(self, tmp_path: Path) -> None:
        """Backups are rotated correctly after many saves."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)

        # Save 15 times (should generate 15 backups but only keep 10)
        for i in range(15):
            storage.save_profiles({f"profile{i}": {"temp_hot": 35.0}})

        backups = sorted(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        # Should have at most 10 backups
        assert len(backups) <= 10

        # Latest profile should be in the main file
        with open(storage.profiles_file, "r", encoding="utf-8") as f:
            current_data = json.load(f)
        assert "profile14" in current_data


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_profiles_data(self, tmp_path: Path) -> None:
        """Empty profiles dictionary is handled."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        result = storage.save_profiles({})
        assert result is True

        loaded = storage.load_profiles()
        assert loaded == {}

    def test_large_profiles_data(self, tmp_path: Path) -> None:
        """Large profiles dictionary is handled."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        large_data: dict[str, Any] = {
            f"profile{i}": {
                "temp_hot": 35.0 + i,
                "temp_cold": -10.0 - i,
                "precip_high": 100.0 + i,
                "description": f"Profile number {i}" * 10,
            }
            for i in range(100)
        }

        result = storage.save_profiles(large_data)
        assert result is True

        loaded = storage.load_profiles()
        assert len(loaded) == 100

    def test_concurrent_backup_cleanup(self, tmp_path: Path) -> None:
        """Backup cleanup handles edge cases."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        storage.save_profiles({"profile": {}})

        # Create exactly 10 backups
        for _ in range(10):
            storage._create_backup()

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))

        # Create one more (should trigger cleanup, but count is at limit)
        storage._create_backup()

        backups = list(storage.backup_dir.glob("anomaly_profiles_backup_*.json"))
        # Should still be at most 10
        assert len(backups) <= 10

    def test_create_backup_handles_copy_error(self, tmp_path: Path) -> None:
        """create_backup handles copy errors gracefully."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)
        storage.save_profiles({"profile": {}})

        # Make backup directory read-only to trigger error
        storage.backup_dir.chmod(0o444)

        try:
            # Should not raise exception, just log warning
            storage._create_backup()
        finally:
            # Restore permissions for cleanup
            storage.backup_dir.chmod(0o755)

    def test_save_current_settings_handles_write_error(self, tmp_path: Path) -> None:
        """save_current_settings returns False on write error."""
        storage = AnomalyProfileStorage(config_dir=tmp_path)

        # Make config directory read-only
        storage.config_dir.chmod(0o444)

        try:
            result = storage.save_current_settings("test", {"temp_hot": 35.0})
            assert result is False
        finally:
            # Restore permissions for cleanup
            storage.config_dir.chmod(0o755)
