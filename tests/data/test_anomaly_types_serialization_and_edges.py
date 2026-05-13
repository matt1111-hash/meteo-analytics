"""Anomaly profile types tests."""

from __future__ import annotations

from typing import Any

from src.infrastructure.anomaly.anomaly_types import AnomalyProfileSettings


class TestAnomalyProfileSettingsSerialization:
    """Tests for to_dict and from_dict methods."""

    def test_to_dict_returns_all_fields(self) -> None:
        """to_dict returns all settings as dictionary."""
        settings = AnomalyProfileSettings(
            temp_hot=40.0,
            temp_cold=-15.0,
            precip_high=120.0,
            precip_low=3.0,
            profile_name="custom",
            description="Custom profile",
        )
        result = settings.to_dict()
        assert result["temp_hot"] == 40.0
        assert result["temp_cold"] == -15.0
        assert result["precip_high"] == 120.0
        assert result["precip_low"] == 3.0
        assert result["profile_name"] == "custom"
        assert result["description"] == "Custom profile"
        assert "created_at" in result
        assert "modified_at" in result

    def test_from_dict_creates_settings(self) -> None:
        """from_dict creates AnomalyProfileSettings from dictionary."""
        data: dict[str, Any] = {
            "temp_hot": 40.0,
            "temp_cold": -15.0,
            "precip_high": 120.0,
            "precip_low": 3.0,
            "wind_high": 80.0,
            "wind_normal": 50.0,
            "wind_strong": 70.0,
            "wind_extreme": 100.0,
            "wind_hurricane": 120.0,
            "profile_name": "custom",
            "created_at": "2024-01-01T12:00:00",
            "modified_at": "2024-01-01T12:00:00",
            "description": "Custom profile",
        }
        settings = AnomalyProfileSettings.from_dict(data)
        assert settings.temp_hot == 40.0
        assert settings.temp_cold == -15.0
        assert settings.precip_high == 120.0
        assert settings.precip_low == 3.0
        assert settings.profile_name == "custom"
        assert settings.description == "Custom profile"

    def test_from_dict_with_default_values(self) -> None:
        """from_dict works with partial dictionary (defaults applied)."""
        data = {"temp_hot": 30.0, "temp_cold": -5.0}
        settings = AnomalyProfileSettings.from_dict(data)
        assert settings.temp_hot == 30.0
        assert settings.temp_cold == -5.0
        assert settings.precip_high == 100.0
        assert settings.precip_low == 5.0

    def test_round_trip_serialization(self) -> None:
        """to_dict and from_dict are inverses of each other."""
        original = AnomalyProfileSettings(
            temp_hot=38.0,
            temp_cold=-12.0,
            precip_high=150.0,
            precip_low=2.0,
            profile_name="test_profile",
            description="Test description",
        )
        data = original.to_dict()
        restored = AnomalyProfileSettings.from_dict(data)

        assert restored.temp_hot == original.temp_hot
        assert restored.temp_cold == original.temp_cold
        assert restored.precip_high == original.precip_high
        assert restored.precip_low == original.precip_low
        assert restored.profile_name == original.profile_name
        assert restored.description == original.description


class TestAnomalyProfileSettingsEdgeCases:
    """Edge case tests for AnomalyProfileSettings."""

    def test_zero_values(self) -> None:
        """Zero values are handled correctly."""
        settings = AnomalyProfileSettings(temp_cold=0.0, precip_low=0.0)
        errors = settings.validate()
        assert errors == []

    def test_negative_values_validation(self) -> None:
        """Negative values are validated appropriately."""
        settings = AnomalyProfileSettings(temp_cold=-30.0)
        errors = settings.validate()
        assert errors == []

        settings = AnomalyProfileSettings(precip_low=-10.0)
        errors = settings.validate()
        assert len(errors) > 0

    def test_very_large_values(self) -> None:
        """Very large values are rejected."""
        settings = AnomalyProfileSettings(
            temp_hot=1000.0, precip_high=10000.0, wind_hurricane=10000.0
        )
        errors = settings.validate()
        assert len(errors) >= 3

    def test_all_wind_thresholds_equal(self) -> None:
        """All wind thresholds being equal is invalid."""
        settings = AnomalyProfileSettings(
            wind_normal=50.0, wind_strong=50.0, wind_extreme=50.0, wind_hurricane=50.0
        )
        errors = settings.validate()
        assert errors == []
