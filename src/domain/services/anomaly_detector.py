"""Domain service for detecting weather anomalies."""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from ..entities.climate_anomaly import ClimateAnomaly
from ..value_objects.anomaly_threshold import AnomalyThresholdSet


class AnomalyDetectorService:
    """Pure business-logic detector using stdlib only."""

    def __init__(self, thresholds: AnomalyThresholdSet) -> None:
        self.thresholds = thresholds

    def detect_temperature_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        max_temps: list[Optional[float]],
        min_temps: list[Optional[float]],
    ) -> Optional[ClimateAnomaly]:
        """Detect temperature anomalies based on extrema and average."""
        valid_max = _filter_numbers(max_temps)
        valid_min = _filter_numbers(min_temps)
        if not valid_max or not valid_min:
            return None

        max_temp = max(valid_max)
        min_temp = min(valid_min)
        avg_temp = _average(valid_max)

        if max_temp > self.thresholds.temp_hot:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=max_temp,
                category="hot",
                severity="error",
                message=f"🔥 Extrém hőség: {max_temp:.1f}°C",
                threshold=self.thresholds.temp_hot,
                details=f"Max hőmérséklet > {self.thresholds.temp_hot}°C",
            )

        if min_temp < self.thresholds.temp_cold:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=min_temp,
                category="cold",
                severity="error",
                message=f"❄️ Extrém hideg: {min_temp:.1f}°C",
                threshold=self.thresholds.temp_cold,
                details=f"Min hőmérséklet < {self.thresholds.temp_cold}°C",
            )

        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="temperature",
            measured_value=avg_temp,
            category="normal",
            severity="success",
            message=f"🌡️ Normális: {avg_temp:.1f}°C átlag",
            details="Hőmérséklet normál tartományban",
        )

    def detect_precipitation_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        precipitation_values: list[Optional[float]],
    ) -> Optional[ClimateAnomaly]:
        """Detect precipitation anomalies using max and average values."""
        valid_precip = _filter_non_negative(precipitation_values)
        if not valid_precip:
            return None

        max_precip = max(valid_precip)
        avg_precip = _average(valid_precip)

        if max_precip > self.thresholds.precip_high:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=max_precip,
                category="heavy_rain",
                severity="error",
                message=f"🌊 Esős időszak: {max_precip:.1f} mm/nap",
                threshold=self.thresholds.precip_high,
                details=f"Max csapadék > {self.thresholds.precip_high} mm",
            )

        if avg_precip < self.thresholds.precip_low:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=avg_precip,
                category="drought",
                severity="warning",
                message=f"🏜️ Száraz: {avg_precip:.1f} mm/nap átlag",
                threshold=self.thresholds.precip_low,
                details=f"Átlag csapadék < {self.thresholds.precip_low} mm",
            )

        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="precipitation",
            measured_value=avg_precip,
            category="normal",
            severity="success",
            message=f"🌧️ Normális: {avg_precip:.1f} mm/nap",
            details="Csapadék normál tartományban",
        )

    def detect_wind_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        wind_speeds: list[Optional[float]],
    ) -> Optional[ClimateAnomaly]:
        """Detect wind anomalies by maximum speed thresholds."""
        valid_winds = _filter_non_negative(wind_speeds)
        if not valid_winds:
            return None

        max_wind = max(valid_winds)
        avg_wind = _average(valid_winds)

        if max_wind > self.thresholds.wind_hurricane:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="hurricane",
                severity="error",
                message=f"🌀 Orkán: {max_wind:.1f} km/h",
                threshold=self.thresholds.wind_hurricane,
                details=(f"Szélsebesség > {self.thresholds.wind_hurricane} km/h"),
            )

        if max_wind > self.thresholds.wind_extreme:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="extreme_wind",
                severity="error",
                message=f"🌪️ Extrém szél: {max_wind:.1f} km/h",
                threshold=self.thresholds.wind_extreme,
                details=(f"Szélsebesség > {self.thresholds.wind_extreme} km/h"),
            )

        if max_wind > self.thresholds.wind_strong:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="strong_wind",
                severity="warning",
                message=f"🌬️ Erős szél: {max_wind:.1f} km/h",
                threshold=self.thresholds.wind_strong,
                details=(f"Szélsebesség > {self.thresholds.wind_strong} km/h"),
            )

        if max_wind > self.thresholds.wind_normal:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="moderate_wind",
                severity="warning",
                message=f"💨 Mérsékelt szél: {max_wind:.1f} km/h",
                threshold=self.thresholds.wind_normal,
                details=(f"Szélsebesség > {self.thresholds.wind_normal} km/h"),
            )

        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="wind",
            measured_value=avg_wind,
            category="calm",
            severity="success",
            message=f"🌿 Csendes: {avg_wind:.1f} km/h",
            details="Szél normál tartományban",
        )


def _filter_numbers(values: Iterable[Optional[float]]) -> list[float]:
    """Filter iterable to finite numeric values."""
    return [float(v) for v in values if v is not None]


def _filter_non_negative(values: Iterable[Optional[float]]) -> list[float]:
    """Filter iterable to non-negative numeric values."""
    return [float(v) for v in values if v is not None and v >= 0]


def _average(values: list[float]) -> float:
    """Return arithmetic mean of non-empty list."""
    return sum(values) / len(values)
