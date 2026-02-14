"""Tests for AnomalyDetectorService."""
from __future__ import annotations

from datetime import date

from src.domain.services.anomaly_detector import AnomalyDetectorService
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet


def test_detect_extreme_heat() -> None:
    """Detect hot anomaly when max temp exceeds threshold."""
    thresholds = AnomalyThresholdSet(temp_hot=35.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_temperature_anomaly(
        location_name="Budapest",
        analysis_date=date(2024, 7, 15),
        max_temps=[42.5, 38.2, 45.1],
        min_temps=[25.0, 22.0, 28.0],
    )

    assert result is not None
    assert result.category == "hot"
    assert result.severity == "error"
    assert result.measured_value == 45.1
    assert result.is_extreme is True


def test_detect_extreme_cold() -> None:
    """Detect cold anomaly when min temp below threshold."""
    thresholds = AnomalyThresholdSet(temp_cold=-10.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_temperature_anomaly(
        location_name="Miskolc",
        analysis_date=date(2024, 1, 15),
        max_temps=[5.0, 2.0, -3.0],
        min_temps=[-15.5, -12.0, -18.2],
    )

    assert result is not None
    assert result.category == "cold"
    assert result.severity == "error"
    assert result.measured_value == -18.2


def test_detect_normal_temperature() -> None:
    """Return success anomaly when temps within thresholds."""
    thresholds = AnomalyThresholdSet(temp_hot=35.0, temp_cold=-10.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_temperature_anomaly(
        location_name="Szeged",
        analysis_date=date(2024, 5, 15),
        max_temps=[22.0, 24.5, 26.0],
        min_temps=[12.0, 14.0, 15.5],
    )

    assert result is not None
    assert result.category == "normal"
    assert result.severity == "success"
    assert result.is_extreme is False


def test_detect_heavy_rain() -> None:
    """Detect heavy rain when max precip exceeds threshold."""
    thresholds = AnomalyThresholdSet(precip_high=100.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_precipitation_anomaly(
        location_name="Debrecen",
        analysis_date=date(2024, 6, 15),
        precipitation_values=[125.5, 85.0, 20.0, 5.0],
    )

    assert result is not None
    assert result.category == "heavy_rain"
    assert result.severity == "error"
    assert result.measured_value == 125.5


def test_detect_drought() -> None:
    """Detect drought when average precip below threshold."""
    thresholds = AnomalyThresholdSet(precip_low=5.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_precipitation_anomaly(
        location_name="Pécs",
        analysis_date=date(2024, 8, 15),
        precipitation_values=[0.5, 0.0, 1.2, 0.8],
    )

    assert result is not None
    assert result.category == "drought"
    assert result.severity == "warning"
    assert result.measured_value < 5.0


def test_detect_normal_precipitation() -> None:
    """Detect normal precipitation when within thresholds."""
    thresholds = AnomalyThresholdSet(precip_high=100.0, precip_low=5.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_precipitation_anomaly(
        location_name="Siófok",
        analysis_date=date(2024, 5, 20),
        precipitation_values=[10.0, 15.0, 8.0],
    )

    assert result is not None
    assert result.category == "normal"
    assert result.severity == "success"


def test_detect_hurricane_wind() -> None:
    """Detect hurricane wind when max exceeds hurricane threshold."""
    thresholds = AnomalyThresholdSet(wind_hurricane=120.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_wind_anomaly(
        location_name="Balatonfüred",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[135.5, 85.0, 25.0],
    )

    assert result is not None
    assert result.category == "hurricane"
    assert result.severity == "error"
    assert result.measured_value == 135.5


def test_detect_extreme_wind() -> None:
    """Detect extreme wind when max exceeds extreme threshold."""
    thresholds = AnomalyThresholdSet(wind_extreme=100.0, wind_hurricane=120.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_wind_anomaly(
        location_name="Pápa",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[105.0, 85.0, 25.0],
    )

    assert result is not None
    assert result.category == "extreme_wind"
    assert result.severity == "error"


def test_detect_strong_wind() -> None:
    """Detect strong wind when max exceeds strong threshold."""
    thresholds = AnomalyThresholdSet(wind_strong=70.0, wind_extreme=100.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_wind_anomaly(
        location_name="Győr",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[75.0, 65.0, 25.0],
    )

    assert result is not None
    assert result.category == "strong_wind"
    assert result.severity == "warning"


def test_detect_moderate_wind() -> None:
    """Detect moderate wind when max exceeds normal threshold."""
    thresholds = AnomalyThresholdSet(wind_normal=50.0, wind_strong=70.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_wind_anomaly(
        location_name="Sopron",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[55.0, 45.0, 25.0],
    )

    assert result is not None
    assert result.category == "moderate_wind"
    assert result.severity == "warning"


def test_detect_calm_wind() -> None:
    """Detect calm wind when max below normal threshold."""
    thresholds = AnomalyThresholdSet(wind_normal=50.0)
    service = AnomalyDetectorService(thresholds)

    result = service.detect_wind_anomaly(
        location_name="Eger",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[10.0, 15.0, 5.0],
    )

    assert result is not None
    assert result.category == "calm"
    assert result.severity == "success"


def test_handle_none_and_negative_values() -> None:
    """None or negative values are ignored for precip/wind; temperature keeps negatives."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)

    temp_result = service.detect_temperature_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        max_temps=[None, 25.0, None, 30.0],
        min_temps=[10.0, None, 15.0, None],
    )
    assert temp_result is not None
    assert temp_result.category == "normal"

    precip_result = service.detect_precipitation_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        precipitation_values=[-1.0, None],
    )
    assert precip_result is None

    wind_result = service.detect_wind_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        wind_speeds=[-5.0, None],
    )
    assert wind_result is None


def test_empty_inputs_return_none() -> None:
    """Empty lists should return None detections."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)

    assert (
        service.detect_temperature_anomaly(
            "Nowhere", date.today(), [], []
        )
        is None
    )
    assert (
        service.detect_precipitation_anomaly(
            "Nowhere", date.today(), []
        )
        is None
    )
    assert (
        service.detect_wind_anomaly(
            "Nowhere", date.today(), []
        )
        is None
    )
