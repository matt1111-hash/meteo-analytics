from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from src.domain.value_objects.enums import (
    AnalyticsMetric,
    AnomalySeverity,
    AnomalyType,
    DataSource,
    get_metric_unit,
    get_severity_color,
)


@dataclass
class CityWeatherResult:
    """
    Egyetlen város időjárási eredménye.

    Multi-city analytics alapegysége.
    """

    city_name: str
    country: str
    country_code: str
    latitude: float
    longitude: float

    # Weather data
    value: float  # Fő metrika értéke
    metric: AnalyticsMetric  # Metrika típusa
    date: date  # Adat dátuma
    rank: int | None = None  # 🔧 FIX: UI compatibility - eredmény rangsor

    # Additional data
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Metadata
    data_source: DataSource = DataSource.AUTO
    quality_score: float = 1.0  # 0.0-1.0 adat minőség
    confidence: float = 1.0  # 0.0-1.0 megbízhatóság

    # Geographical context
    population: int | None = None
    elevation: float | None = None
    timezone: str | None = None
    admin_name: str | None = None  # Régió/állam

    def __str__(self) -> str:
        """String reprezentáció."""
        unit = self._get_metric_unit()
        return f"{self.city_name}: {self.value:.1f}{unit}"

    def _get_metric_unit(self) -> str:
        """Metrika mértékegység lekérdezése."""
        return get_metric_unit(self.metric)

    def get_display_name(self) -> str:
        """Teljes display név."""
        return f"{self.city_name}, {self.country}"

    def get_coordinates(self) -> tuple[float, float]:
        """Koordináták tuple-ként."""
        return (self.latitude, self.longitude)

    def to_dict(self) -> dict[str, Any]:
        """Dictionary konverzió."""
        return {
            "city_name": self.city_name,
            "country": self.country,
            "country_code": self.country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "value": self.value,
            "metric": self.metric.value,
            "date": self.date.isoformat(),
            "rank": self.rank,  # 🔧 FIX: rank mező hozzáadva
            "additional_data": self.additional_data,
            "data_source": self.data_source.value,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "population": self.population,
            "elevation": self.elevation,
            "timezone": self.timezone,
            "admin_name": self.admin_name,
        }


@dataclass
class AnomalyResult:
    """
    Anomália detektálási eredmény.

    Parameter-based analytics anomália eredménye.
    """

    date: date
    metric: AnalyticsMetric
    value: float
    expected_value: float
    deviation: float  # Standard deviáció
    severity: AnomalySeverity
    anomaly_type: AnomalyType  # HIGH/LOW

    # Context
    description: str
    confidence: float = 1.0

    # Statistical context
    percentile: float | None = None
    z_score: float | None = None

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    detection_method: str = "statistical"

    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.date}: {self.description}"

    def get_severity_color(self) -> str:
        """Súlyosság színkód."""
        return get_severity_color(self.severity)

    def to_dict(self) -> dict[str, Any]:
        """Dictionary konverzió."""
        return {
            "date": self.date.isoformat(),
            "metric": self.metric.value,
            "value": self.value,
            "expected_value": self.expected_value,
            "deviation": self.deviation,
            "severity": self.severity.value,
            "anomaly_type": self.anomaly_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "percentile": self.percentile,
            "z_score": self.z_score,
            "detected_at": self.detected_at.isoformat(),
            "detection_method": self.detection_method,
        }


def create_city_weather_result(
    city_name: str,
    country: str,
    country_code: str,
    latitude: float,
    longitude: float,
    value: float,
    metric: AnalyticsMetric,
    result_date: date,
    **kwargs,
) -> CityWeatherResult:
    """
    CityWeatherResult factory function.
    """
    return CityWeatherResult(
        city_name=city_name,
        country=country,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        value=value,
        metric=metric,
        date=result_date,
        **kwargs,
    )
