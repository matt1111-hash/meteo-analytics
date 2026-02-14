"""Analytics models domain entities."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from src.domain.entities.weather import AnomalyResult, CityWeatherResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataSource,
    QuestionType,
    RegionScope,
)


@dataclass
class AnalyticsQuestion:
    """
    Analytics question definition.

    Multi-city analytics question specification.
    """

    question_text: str
    question_type: QuestionType
    region_scope: RegionScope
    metric: AnalyticsMetric

    # Query parameters
    region_value: Optional[str] = None
    date_filter: Optional[str] = None
    ascending_order: bool = False
    max_cities: int = 50

    # Additional filters
    min_population: Optional[int] = None
    include_capitals_only: bool = False
    exclude_islands: bool = False
    climate_zones: Optional[List[str]] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation."""
        return self.question_text

    def get_region_display(self) -> str:
        """Get region display name."""
        if self.region_value:
            return f"{self.region_scope.value}: {self.region_value}"
        return self.region_scope.value

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate question.

        Returns:
            (valid, error_messages)
        """
        errors = []

        if not self.question_text.strip():
            errors.append("Kérdés szövege nem lehet üres")

        if self.max_cities <= 0:
            errors.append("Maximum városok száma pozitív kell legyen")

        if self.max_cities > 1000:
            errors.append("Maximum városok száma nem lehet 1000-nél több")

        if (
            self.region_scope in [RegionScope.COUNTRY, RegionScope.REGION]
            and not self.region_value
        ):
            errors.append(
                f"{self.region_scope.value} scope esetén region_value kötelező"
            )

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "region_scope": self.region_scope.value,
            "metric": self.metric.value,
            "region_value": self.region_value,
            "date_filter": self.date_filter,
            "ascending_order": self.ascending_order,
            "max_cities": self.max_cities,
            "min_population": self.min_population,
            "include_capitals_only": self.include_capitals_only,
            "exclude_islands": self.exclude_islands,
            "climate_zones": self.climate_zones,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
        }


@dataclass
class AnalyticsResult:
    """
    Multi-city analytics result.

    Complete analytics query result.
    """

    question: AnalyticsQuestion
    city_results: List[CityWeatherResult]

    # Execution metadata
    execution_time: float
    total_cities_found: int
    data_sources_used: List[DataSource]

    # Statistics
    statistics: Dict[str, float] = field(default_factory=dict)

    # Provider statistics
    provider_statistics: Dict[str, Any] = field(default_factory=dict)

    # Quality metrics
    average_quality_score: float = 1.0
    average_confidence: float = 1.0

    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)

    def __len__(self) -> int:
        """Result count."""
        return len(self.city_results)

    def get_top_results(self, n: int = 10) -> List[CityWeatherResult]:
        """Get top N results."""
        return self.city_results[:n]

    def get_bottom_results(self, n: int = 10) -> List[CityWeatherResult]:
        """Get bottom N results."""
        return self.city_results[-n:]

    def get_results_by_country(self, country_code: str) -> List[CityWeatherResult]:
        """Filter by country."""
        return [r for r in self.city_results if r.country_code == country_code]

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get statistical summary."""
        if not self.city_results:
            return {}

        values = [r.value for r in self.city_results]

        import statistics

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "range": max(values) - min(values),
        }

    def get_countries_represented(self) -> List[str]:
        """Get represented countries list."""
        return list(set(r.country_code for r in self.city_results))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question": self.question.to_dict(),
            "city_results": [r.to_dict() for r in self.city_results],
            "execution_time": self.execution_time,
            "total_cities_found": self.total_cities_found,
            "data_sources_used": [ds.value for ds in self.data_sources_used],
            "statistics": self.statistics,
            "provider_statistics": self.provider_statistics,
            "average_quality_score": self.average_quality_score,
            "average_confidence": self.average_confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class QueryResults:
    """
    Parameter-based query results.

    ParameterSelectorWidget query result storage.
    """

    query_parameters: Dict[str, Any]
    anomalies: Dict[str, List[AnomalyResult]]

    # Execution metadata
    execution_time: float
    total_records_analyzed: int
    date_range: Tuple[date, date]

    # Statistics
    anomaly_summary: Dict[str, int] = field(default_factory=dict)

    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)

    def get_total_anomalies(self) -> int:
        """Get total anomalies count."""
        return sum(len(anomaly_list) for anomaly_list in self.anomalies.values())

    def get_anomalies_by_severity(self) -> Dict[str, int]:
        """Get anomalies by severity."""
        severity_counts = {}
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                severity = anomaly.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts

    def get_most_active_days(self, n: int = 10) -> List[Tuple[date, int]]:
        """Get most active days by anomaly count."""
        day_counts = {}
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                day = anomaly.date
                day_counts[day] = day_counts.get(day, 0) + 1
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_days[:n]

    def get_anomalies_for_parameter(self, parameter: str) -> List[AnomalyResult]:
        """Get parameter-specific anomalies."""
        return self.anomalies.get(parameter, [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_parameters": self.query_parameters,
            "anomalies": {
                param: [a.to_dict() for a in anomalies]
                for param, anomalies in self.anomalies.items()
            },
            "execution_time": self.execution_time,
            "total_records_analyzed": self.total_records_analyzed,
            "date_range": [
                self.date_range[0].isoformat(),
                self.date_range[1].isoformat(),
            ],
            "anomaly_summary": self.anomaly_summary,
            "created_at": self.created_at.isoformat(),
        }


__all__ = ["AnalyticsQuestion", "AnalyticsResult", "QueryResults"]
