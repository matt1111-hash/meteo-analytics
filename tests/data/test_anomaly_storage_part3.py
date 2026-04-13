"""Tests split from test_anomaly_storage.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_anomaly_storage_support import *


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
        with open(storage.profiles_file, encoding="utf-8") as f:  # noqa: PTH123
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
