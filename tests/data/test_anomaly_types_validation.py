"""Anomaly profile types tests."""

from __future__ import annotations

from src.data.anomaly_types import AnomalyProfileSettings


class TestAnomalyProfileSettingsValidation:
    """Tests for validate method."""

    def test_validate_returns_empty_list_for_valid_settings(self) -> None:
        """validate returns empty list when all settings are valid."""
        settings = AnomalyProfileSettings()
        errors = settings.validate()
        assert errors == []

    def test_validate_error_hot_threshold_equal_cold(self) -> None:
        """Error when temp_hot equals temp_cold."""
        settings = AnomalyProfileSettings(temp_hot=20.0, temp_cold=20.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any(
            "Meleg küszöb nem lehet kisebb vagy egyenlő" in err for err in errors
        )

    def test_validate_error_hot_threshold_less_than_cold(self) -> None:
        """Error when temp_hot is less than temp_cold."""
        settings = AnomalyProfileSettings(temp_hot=10.0, temp_cold=20.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any(
            "Meleg küszöb nem lehet kisebb vagy egyenlő" in err for err in errors
        )

    def test_validate_error_hot_threshold_too_high(self) -> None:
        """Error when temp_hot exceeds maximum."""
        settings = AnomalyProfileSettings(temp_hot=70.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Meleg küszöb tartománya" in err for err in errors)

    def test_validate_error_hot_threshold_too_low(self) -> None:
        """Error when temp_hot is below minimum."""
        settings = AnomalyProfileSettings(temp_hot=-60.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Meleg küszöb tartománya" in err for err in errors)

    def test_validate_error_cold_threshold_too_high(self) -> None:
        """Error when temp_cold exceeds maximum."""
        settings = AnomalyProfileSettings(temp_cold=50.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Hideg küszöb tartománya" in err for err in errors)

    def test_validate_error_cold_threshold_too_low(self) -> None:
        """Error when temp_cold is below minimum."""
        settings = AnomalyProfileSettings(temp_cold=-60.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Hideg küszöb tartománya" in err for err in errors)

    def test_validate_error_precip_high_equal_low(self) -> None:
        """Error when precip_high equals precip_low."""
        settings = AnomalyProfileSettings(precip_high=50.0, precip_low=50.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any(
            "Magas csapadék küszöb nem lehet kisebb vagy egyenlő" in err
            for err in errors
        )

    def test_validate_error_precip_high_less_than_low(self) -> None:
        """Error when precip_high is less than precip_low."""
        settings = AnomalyProfileSettings(precip_high=20.0, precip_low=50.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any(
            "Magas csapadék küszöb nem lehet kisebb vagy egyenlő" in err
            for err in errors
        )

    def test_validate_error_precip_low_too_high(self) -> None:
        """Error when precip_low exceeds maximum."""
        settings = AnomalyProfileSettings(precip_low=60.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Alacsony csapadék küszöb tartománya" in err for err in errors)

    def test_validate_error_precip_low_negative(self) -> None:
        """Error when precip_low is negative."""
        settings = AnomalyProfileSettings(precip_low=-10.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Alacsony csapadék küszöb tartománya" in err for err in errors)

    def test_validate_error_precip_high_too_high(self) -> None:
        """Error when precip_high exceeds maximum."""
        settings = AnomalyProfileSettings(precip_high=600.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Magas csapadék küszöb tartománya" in err for err in errors)

    def test_validate_error_precip_high_too_low(self) -> None:
        """Error when precip_high is below minimum."""
        settings = AnomalyProfileSettings(precip_high=5.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Magas csapadék küszöb tartománya" in err for err in errors)

    def test_validate_error_wind_thresholds_not_sorted(self) -> None:
        """Error when wind thresholds are not in increasing order."""
        settings = AnomalyProfileSettings(
            wind_normal=70.0, wind_strong=50.0, wind_extreme=100.0, wind_hurricane=120.0
        )
        errors = settings.validate()
        assert len(errors) > 0
        assert any(
            "Szél küszöbök nem növekvő sorrendben vannak" in err for err in errors
        )

    def test_validate_error_wind_threshold_too_low(self) -> None:
        """Error when wind threshold is below minimum."""
        settings = AnomalyProfileSettings(wind_normal=5.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Szél küszöb tartománya" in err for err in errors)

    def test_validate_error_wind_threshold_too_high(self) -> None:
        """Error when wind threshold exceeds maximum."""
        settings = AnomalyProfileSettings(wind_hurricane=350.0)
        errors = settings.validate()
        assert len(errors) > 0
        assert any("Szél küszöb tartománya" in err for err in errors)

    def test_validate_multiple_errors(self) -> None:
        """Multiple validation errors are returned."""
        settings = AnomalyProfileSettings(
            temp_hot=10.0,
            temp_cold=20.0,
            precip_high=20.0,
            precip_low=50.0,
            wind_normal=70.0,
            wind_strong=50.0,
        )
        errors = settings.validate()
        assert len(errors) >= 3

    def test_validate_boundary_values_valid(self) -> None:
        """Boundary values are accepted as valid."""
        settings = AnomalyProfileSettings(
            temp_hot=60.0,
            temp_cold=-50.0,
            precip_low=0.0,
            precip_high=500.0,
            wind_normal=10.0,
            wind_strong=100.0,
            wind_extreme=200.0,
            wind_hurricane=300.0,
        )
        errors = settings.validate()
        assert errors == []

    def test_validate_wind_high_not_used_in_validation(self) -> None:
        """wind_high is stored but not part of the sorted wind validation."""
        settings = AnomalyProfileSettings(
            wind_normal=30.0,
            wind_strong=50.0,
            wind_extreme=80.0,
            wind_hurricane=120.0,
            wind_high=1000.0,
        )
        errors = settings.validate()
        assert errors == []
