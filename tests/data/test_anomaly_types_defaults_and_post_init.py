"""Anomaly profile types tests."""

from __future__ import annotations

from datetime import datetime

from src.data.anomaly_types import AnomalyProfileSettings


class TestAnomalyProfileSettingsDefaults:
    """Tests for AnomalyProfileSettings default values."""

    def test_default_temperature_thresholds(self) -> None:
        """Default temperature thresholds are set correctly."""
        settings = AnomalyProfileSettings()
        assert settings.temp_hot == 35.0
        assert settings.temp_cold == -10.0

    def test_default_precipitation_thresholds(self) -> None:
        """Default precipitation thresholds are set correctly."""
        settings = AnomalyProfileSettings()
        assert settings.precip_high == 100.0
        assert settings.precip_low == 5.0

    def test_default_wind_thresholds(self) -> None:
        """Default wind thresholds are set correctly."""
        settings = AnomalyProfileSettings()
        assert settings.wind_high == 70.0
        assert settings.wind_normal == 50.0
        assert settings.wind_strong == 70.0
        assert settings.wind_extreme == 100.0
        assert settings.wind_hurricane == 120.0

    def test_default_metadata(self) -> None:
        """Default metadata fields are set correctly."""
        settings = AnomalyProfileSettings()
        assert settings.profile_name == "default"
        assert settings.created_at != ""
        assert settings.modified_at != ""
        assert settings.description == ""


class TestAnomalyProfileSettingsPostInit:
    """Tests for __post_init__ method."""

    def test_created_at_set_on_initialization(self) -> None:
        """created_at is set to current ISO timestamp on init."""
        before = datetime.now()
        settings = AnomalyProfileSettings()
        after = datetime.now()

        created_at = datetime.fromisoformat(settings.created_at)
        assert before <= created_at <= after

    def test_modified_at_set_on_initialization(self) -> None:
        """modified_at is set to current ISO timestamp on init."""
        before = datetime.now()
        settings = AnomalyProfileSettings()
        after = datetime.now()

        modified_at = datetime.fromisoformat(settings.modified_at)
        assert before <= modified_at <= after

    def test_created_at_preserved_if_provided(self) -> None:
        """created_at is preserved if already set."""
        existing_timestamp = "2024-01-01T12:00:00"
        settings = AnomalyProfileSettings(created_at=existing_timestamp)
        assert settings.created_at == existing_timestamp

    def test_modified_at_updated_on_init(self) -> None:
        """modified_at is always updated to current time."""
        existing_timestamp = "2024-01-01T12:00:00"
        settings = AnomalyProfileSettings(modified_at=existing_timestamp)

        modified_at = datetime.fromisoformat(settings.modified_at)
        assert modified_at.year == datetime.now().year
