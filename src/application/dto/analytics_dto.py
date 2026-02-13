#!/usr/bin/env python3
"""
Analytics DTOs - Data Transfer Objects for Analytics Results.

These DTOs provide a stable interface for the presentation layer
to consume analytics results without depending on domain entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.entities.analytics_models import AnalyticsResult
from src.domain.entities.weather import CityWeatherResult


@dataclass
class CityWeatherResultDTO:
    """
    DTO for single city weather result.

    Provides a stable interface for presentation layer.
    """

    city_name: str
    country: str
    country_code: str
    latitude: float
    longitude: float
    value: float
    metric: str  # Metric name as string
    date: str  # ISO date string
    rank: Optional[int] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    data_source: str = "auto"
    quality_score: float = 1.0
    confidence: float = 1.0
    population: Optional[int] = None
    timezone: Optional[str] = None
    admin_name: Optional[str] = None

    @classmethod
    def from_domain(cls, result: CityWeatherResult) -> "CityWeatherResultDTO":
        """Create DTO from domain entity."""
        return cls(
            city_name=result.city_name,
            country=result.country,
            country_code=result.country_code,
            latitude=result.latitude,
            longitude=result.longitude,
            value=result.value,
            metric=result.metric.value,
            date=result.date.isoformat(),
            rank=result.rank,
            additional_data=result.additional_data,
            data_source=result.data_source.value,
            quality_score=result.quality_score,
            confidence=result.confidence,
            population=result.population,
            timezone=result.timezone,
            admin_name=result.admin_name,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "city_name": self.city_name,
            "country": self.country,
            "country_code": self.country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "value": self.value,
            "metric": self.metric,
            "date": self.date,
            "rank": self.rank,
            "additional_data": self.additional_data,
            "data_source": self.data_source,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "population": self.population,
            "timezone": self.timezone,
            "admin_name": self.admin_name,
        }


@dataclass
class AnalyticsResultDTO:
    """
    DTO for multi-city analytics result.

    Provides a stable interface for presentation layer.
    """

    question_text: str
    city_results: List[CityWeatherResultDTO]
    execution_time: float
    total_cities_found: int
    data_sources_used: List[str]
    statistics: Dict[str, float] = field(default_factory=dict)
    provider_statistics: Dict[str, Any] = field(default_factory=dict)
    average_quality_score: float = 1.0
    average_confidence: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_domain(cls, result: AnalyticsResult) -> "AnalyticsResultDTO":
        """Create DTO from domain entity."""
        return cls(
            question_text=result.question.question_text,
            city_results=[
                CityWeatherResultDTO.from_domain(r) for r in result.city_results
            ],
            execution_time=result.execution_time,
            total_cities_found=result.total_cities_found,
            data_sources_used=[ds.value for ds in result.data_sources_used],
            statistics=result.statistics,
            provider_statistics=result.provider_statistics,
            average_quality_score=result.average_quality_score,
            average_confidence=result.average_confidence,
            created_at=result.created_at.isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_text": self.question_text,
            "city_results": [r.to_dict() for r in self.city_results],
            "execution_time": self.execution_time,
            "total_cities_found": self.total_cities_found,
            "data_sources_used": self.data_sources_used,
            "statistics": self.statistics,
            "provider_statistics": self.provider_statistics,
            "average_quality_score": self.average_quality_score,
            "average_confidence": self.average_confidence,
            "created_at": self.created_at,
        }

    def get_top_results(self, n: int = 10) -> List[CityWeatherResultDTO]:
        """Get top N results."""
        return self.city_results[:n]

    def __len__(self) -> int:
        """Result count."""
        return len(self.city_results)


__all__ = ["AnalyticsResultDTO", "CityWeatherResultDTO"]
