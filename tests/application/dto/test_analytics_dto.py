#!/usr/bin/env python3
"""Tests for application DTOs."""

from datetime import date

from src.application.dto.analytics_dto import (
    AnalyticsResultDTO,
    CityWeatherResultDTO,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataSource,
    QuestionType,
    RegionScope,
)


class TestCityWeatherResultDTO:
    """Tests for CityWeatherResultDTO."""

    def test_from_domain(self):
        """Test creating DTO from domain entity."""
        domain_result = CityWeatherResult(
            city_name="Budapest",
            country="Magyarország",
            country_code="HU",
            latitude=47.4979,
            longitude=19.0402,
            value=25.5,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            date=date(2024, 6, 15),
            rank=1,
            data_source=DataSource.OPEN_METEO,
        )

        dto = CityWeatherResultDTO.from_domain(domain_result)

        assert dto.city_name == "Budapest"
        assert dto.country == "Magyarország"
        assert dto.country_code == "HU"
        assert dto.latitude == 47.4979
        assert dto.longitude == 19.0402
        assert dto.value == 25.5
        assert dto.metric == "temperature_2m_max"
        assert dto.date == "2024-06-15"
        assert dto.rank == 1
        assert dto.data_source == "open-meteo"

    def test_to_dict(self):
        """Test DTO to_dict method."""
        dto = CityWeatherResultDTO(
            city_name="Debrecen",
            country="Magyarország",
            country_code="HU",
            latitude=47.5316,
            longitude=21.6273,
            value=12.3,
            metric="precipitation_sum",
            date="2024-06-15",
        )

        result = dto.to_dict()

        assert result["city_name"] == "Debrecen"
        assert result["metric"] == "precipitation_sum"
        assert result["date"] == "2024-06-15"


class TestAnalyticsResultDTO:
    """Tests for AnalyticsResultDTO."""

    def test_from_domain(self):
        """Test creating DTO from domain AnalyticsResult."""
        question = AnalyticsQuestion(
            question_text="Legmelegebb magyar városok",
            question_type=QuestionType.TEMPERATURE_MAX,
            region_scope=RegionScope.COUNTRY,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            region_value="HU",
        )

        city_results = [
            CityWeatherResult(
                city_name="Szeged",
                country="Magyarország",
                country_code="HU",
                latitude=46.2530,
                longitude=20.1414,
                value=32.5,
                metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
                date=date(2024, 7, 15),
            ),
        ]

        domain_result = AnalyticsResult(
            question=question,
            city_results=city_results,
            execution_time=1.5,
            total_cities_found=1,
            data_sources_used=[DataSource.OPEN_METEO],
        )

        dto = AnalyticsResultDTO.from_domain(domain_result)

        assert dto.question_text == "Legmelegebb magyar városok"
        assert len(dto.city_results) == 1
        assert dto.execution_time == 1.5
        assert dto.total_cities_found == 1
        assert dto.data_sources_used == ["open-meteo"]

    def test_get_top_results(self):
        """Test get_top_results method."""
        dto = AnalyticsResultDTO(
            question_text="Test",
            city_results=[
                CityWeatherResultDTO(
                    city_name=f"City{i}",
                    country="Country",
                    country_code="CC",
                    latitude=0.0,
                    longitude=0.0,
                    value=float(i),
                    metric="temperature_2m_max",
                    date="2024-01-01",
                )
                for i in range(10)
            ],
            execution_time=1.0,
            total_cities_found=10,
            data_sources_used=["open_meteo"],
        )

        top_3 = dto.get_top_results(3)

        assert len(top_3) == 3
        assert top_3[0].city_name == "City0"
        assert top_3[2].city_name == "City2"

    def test_len(self):
        """Test __len__ method."""
        dto = AnalyticsResultDTO(
            question_text="Test",
            city_results=[
                CityWeatherResultDTO(
                    city_name="City",
                    country="Country",
                    country_code="CC",
                    latitude=0.0,
                    longitude=0.0,
                    value=1.0,
                    metric="temperature_2m_max",
                    date="2024-01-01",
                )
                for _ in range(5)
            ],
            execution_time=1.0,
            total_cities_found=5,
            data_sources_used=["open_meteo"],
        )

        assert len(dto) == 5
