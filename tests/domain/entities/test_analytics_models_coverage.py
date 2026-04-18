"""Coverage tests for analytics_models domain entities.

Targets uncovered branches in AnalyticsQuestion, AnalyticsResult,
AnomalyResult (via QueryResults), and QueryResults.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from src.domain.entities.analytics_models import (
    AnalyticsQuestion,
    AnalyticsResult,
    QueryResults,
)
from src.domain.entities.weather import AnomalyResult, CityWeatherResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    AnomalySeverity,
    AnomalyType,
    DataSource,
    QuestionType,
    RegionScope,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_question(**overrides: Any) -> AnalyticsQuestion:
    """Create an AnalyticsQuestion with sensible defaults."""
    defaults: dict[str, Any] = {
        "question_text": "Melyik város a legmelegebb?",
        "question_type": QuestionType.TEMPERATURE_MAX,
        "region_scope": RegionScope.GLOBAL,
        "metric": AnalyticsMetric.TEMPERATURE_2M_MAX,
        "max_cities": 50,
    }
    defaults.update(overrides)
    return AnalyticsQuestion(**defaults)


def _make_city_result(
    city_name: str = "Budapest",
    country_code: str = "HU",
    value: float = 25.0,
    date_val: date | None = None,
) -> CityWeatherResult:
    """Create a CityWeatherResult with defaults."""
    return CityWeatherResult(
        city_name=city_name,
        country="Hungary",
        country_code=country_code,
        latitude=47.5,
        longitude=19.1,
        value=value,
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        date=date_val or date(2025, 7, 15),
    )


def _make_anomaly(
    anomaly_date: date | None = None,
    severity: AnomalySeverity = AnomalySeverity.HIGH,
    metric: AnalyticsMetric = AnalyticsMetric.TEMPERATURE_2M_MAX,
) -> AnomalyResult:
    """Create an AnomalyResult with defaults."""
    return AnomalyResult(
        date=anomaly_date or date(2025, 7, 15),
        metric=metric,
        value=40.0,
        expected_value=28.0,
        deviation=3.5,
        severity=severity,
        anomaly_type=AnomalyType.HIGH,
        description="Extreme heat anomaly",
    )


def _make_analytics_result(
    city_results: list[CityWeatherResult] | None = None,
    **overrides: Any,
) -> AnalyticsResult:
    """Create an AnalyticsResult with defaults."""
    defaults: dict[str, Any] = {
        "question": _make_question(),
        "city_results": city_results or [_make_city_result()],
        "execution_time": 0.5,
        "total_cities_found": 1,
        "data_sources_used": [DataSource.OPEN_METEO],
    }
    defaults.update(overrides)
    return AnalyticsResult(**defaults)


# ===================================================================
# AnalyticsQuestion tests
# ===================================================================


class TestAnalyticsQuestionStr:
    """Test AnalyticsQuestion.__str__ returns question_text (line 51)."""

    def test_str_returns_question_text(self) -> None:
        # Arrange
        question = _make_question(question_text="Melyik a legcsapadekosabb varos?")

        # Act
        result = str(question)

        # Assert
        assert result == "Melyik a legcsapadekosabb varos?"


class TestAnalyticsQuestionGetRegionDisplay:
    """Test AnalyticsQuestion.get_region_display (lines 55-57)."""

    def test_with_region_value_returns_scope_and_value(self) -> None:
        # Arrange
        question = _make_question(
            region_scope=RegionScope.COUNTRY,
            region_value="HU",
        )

        # Act
        result = question.get_region_display()

        # Assert
        assert result == "country: HU"

    def test_without_region_value_returns_scope_only(self) -> None:
        # Arrange
        question = _make_question(
            region_scope=RegionScope.GLOBAL,
            region_value=None,
        )

        # Act
        result = question.get_region_display()

        # Assert
        assert result == "global"

    def test_with_empty_region_value_returns_scope_only(self) -> None:
        # Arrange
        question = _make_question(
            region_scope=RegionScope.CONTINENT,
            region_value="",
        )

        # Act
        result = question.get_region_display()

        # Assert
        # Empty string is falsy, so scope-only path is taken (line 57)
        assert result == "continent"


class TestAnalyticsQuestionValidate:
    """Test AnalyticsQuestion.validate (lines 68->71, 71->74, 75, 77->80)."""

    def test_valid_question_passes(self) -> None:
        # Arrange
        question = _make_question()

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is True
        assert _errors == []

    def test_empty_question_text_fails(self) -> None:
        # Arrange — whitespace-only text is treated as empty (line 68->71)
        question = _make_question(question_text="   ")

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("nem lehet \u00fcr" in e for e in _errors)

    def test_max_cities_zero_fails(self) -> None:
        # Arrange — max_cities <= 0 (line 71->74)
        question = _make_question(max_cities=0)

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("pozit\u00edv" in e for e in _errors)

    def test_max_cities_negative_fails(self) -> None:
        # Arrange
        question = _make_question(max_cities=-5)

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("pozit\u00edv" in e for e in _errors)

    def test_max_cities_above_1000_fails(self) -> None:
        # Arrange — max_cities > 1000 (line 75)
        question = _make_question(max_cities=1500)

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("1000" in e for e in _errors)

    def test_country_scope_without_region_value_fails(self) -> None:
        # Arrange — RegionScope.COUNTRY with no region_value (line 77->80)
        question = _make_question(
            region_scope=RegionScope.COUNTRY,
            region_value=None,
        )

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("region_value k\u00f6telez\u0151" in e for e in _errors)

    def test_region_scope_without_region_value_fails(self) -> None:
        # Arrange — RegionScope.REGION with no region_value (line 77->80)
        question = _make_question(
            region_scope=RegionScope.REGION,
            region_value=None,
        )

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert any("region_value k\u00f6telez\u0151" in e for e in _errors)

    def test_country_scope_with_region_value_passes(self) -> None:
        # Arrange
        question = _make_question(
            region_scope=RegionScope.COUNTRY,
            region_value="HU",
        )

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is True

    def test_multiple_errors_accumulate(self) -> None:
        # Arrange — empty text AND max_cities=0 AND country scope without value
        question = _make_question(
            question_text="  ",
            max_cities=0,
            region_scope=RegionScope.COUNTRY,
            region_value=None,
        )

        # Act
        valid, _errors = question.validate()

        # Assert
        assert valid is False
        assert len(_errors) == 3


class TestAnalyticsQuestionToDict:
    """Test AnalyticsQuestion.to_dict (line 84)."""

    def test_to_dict_returns_all_fields(self) -> None:
        # Arrange
        created = datetime(2025, 1, 1, 12, 0, 0)
        question = _make_question(
            question_text="Test question",
            question_type=QuestionType.TEMPERATURE_MAX,
            region_scope=RegionScope.COUNTRY,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            region_value="HU",
            date_filter="2025-01",
            ascending_order=True,
            max_cities=100,
            min_population=50000,
            include_capitals_only=True,
            exclude_islands=True,
            climate_zones=["temperate"],
            created_at=created,
            created_by="tester",
            tags=["heat"],
        )

        # Act
        result = question.to_dict()

        # Assert
        assert result["question_text"] == "Test question"
        assert result["question_type"] == "temperature_max"
        assert result["region_scope"] == "country"
        assert result["metric"] == "temperature_2m_max"
        assert result["region_value"] == "HU"
        assert result["date_filter"] == "2025-01"
        assert result["ascending_order"] is True
        assert result["max_cities"] == 100
        assert result["min_population"] == 50000
        assert result["include_capitals_only"] is True
        assert result["exclude_islands"] is True
        assert result["climate_zones"] == ["temperate"]
        assert result["created_at"] == created.isoformat()
        assert result["created_by"] == "tester"
        assert result["tags"] == ["heat"]


# ===================================================================
# AnalyticsResult tests
# ===================================================================


class TestAnalyticsResultLen:
    """Test AnalyticsResult.__len__ (line 134)."""

    def test_len_with_results(self) -> None:
        # Arrange
        cities = [_make_city_result(city_name=f"City{i}") for i in range(3)]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = len(ar)

        # Assert
        assert result == 3

    def test_len_with_empty_results(self) -> None:
        # Arrange
        ar = AnalyticsResult(
            question=_make_question(),
            city_results=[],
            execution_time=0.1,
            total_cities_found=0,
            data_sources_used=[],
        )

        # Act
        result = len(ar)

        # Assert
        assert result == 0


class TestAnalyticsResultGetTopResults:
    """Test AnalyticsResult.get_top_results (line 138)."""

    def test_returns_first_n(self) -> None:
        # Arrange
        cities = [_make_city_result(city_name=f"City{i}", value=float(i)) for i in range(5)]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_top_results(3)

        # Assert
        assert len(result) == 3
        assert result[0].city_name == "City0"
        assert result[2].city_name == "City2"

    def test_n_larger_than_list_returns_all(self) -> None:
        # Arrange
        cities = [_make_city_result(city_name="Only")]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_top_results(10)

        # Assert
        assert len(result) == 1


class TestAnalyticsResultGetBottomResults:
    """Test AnalyticsResult.get_bottom_results (line 142)."""

    def test_returns_last_n(self) -> None:
        # Arrange
        cities = [_make_city_result(city_name=f"City{i}", value=float(i)) for i in range(5)]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_bottom_results(2)

        # Assert
        assert len(result) == 2
        assert result[0].city_name == "City3"
        assert result[1].city_name == "City4"

    def test_n_larger_than_list_returns_all(self) -> None:
        # Arrange
        cities = [_make_city_result(city_name="Only")]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_bottom_results(10)

        # Assert
        assert len(result) == 1


class TestAnalyticsResultGetResultsByCountry:
    """Test AnalyticsResult.get_results_by_country (line 146)."""

    def test_filters_by_country_code(self) -> None:
        # Arrange
        hu1 = _make_city_result(city_name="Budapest", country_code="HU")
        hu2 = _make_city_result(city_name="Debrecen", country_code="HU")
        de = _make_city_result(city_name="Berlin", country_code="DE")
        ar = _make_analytics_result(city_results=[hu1, hu2, de])

        # Act
        result = ar.get_results_by_country("HU")

        # Assert
        assert len(result) == 2
        assert all(r.country_code == "HU" for r in result)

    def test_no_match_returns_empty(self) -> None:
        # Arrange
        hu = _make_city_result(city_name="Budapest", country_code="HU")
        ar = _make_analytics_result(city_results=[hu])

        # Act
        result = ar.get_results_by_country("FR")

        # Assert
        assert result == []


class TestAnalyticsResultGetStatisticsSummary:
    """Test AnalyticsResult.get_statistics_summary (line 151)."""

    def test_empty_results_returns_empty_dict(self) -> None:
        # Arrange
        ar = AnalyticsResult(
            question=_make_question(),
            city_results=[],
            execution_time=0.1,
            total_cities_found=0,
            data_sources_used=[],
        )

        # Act
        result = ar.get_statistics_summary()

        # Assert
        assert result == {}

    def test_single_result_summary(self) -> None:
        # Arrange
        cities = [_make_city_result(value=10.0)]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_statistics_summary()

        # Assert
        assert result["count"] == 1
        assert result["min"] == 10.0
        assert result["max"] == 10.0
        assert result["mean"] == 10.0
        assert result["median"] == 10.0
        assert result["stdev"] == 0

    def test_multiple_results_summary(self) -> None:
        # Arrange
        cities = [
            _make_city_result(value=10.0, city_name="A"),
            _make_city_result(value=20.0, city_name="B"),
            _make_city_result(value=30.0, city_name="C"),
        ]
        ar = _make_analytics_result(city_results=cities)

        # Act
        result = ar.get_statistics_summary()

        # Assert
        assert result["count"] == 3
        assert result["min"] == 10.0
        assert result["max"] == 30.0
        assert result["mean"] == 20.0
        assert result["range"] == 20.0
        assert result["stdev"] > 0


class TestAnalyticsResultGetCountriesRepresented:
    """Test AnalyticsResult.get_countries_represented (line 169)."""

    def test_returns_unique_country_codes(self) -> None:
        # Arrange
        hu1 = _make_city_result(city_name="Budapest", country_code="HU")
        hu2 = _make_city_result(city_name="Debrecen", country_code="HU")
        de = _make_city_result(city_name="Berlin", country_code="DE")
        ar = _make_analytics_result(city_results=[hu1, hu2, de])

        # Act
        result = ar.get_countries_represented()

        # Assert
        assert set(result) == {"HU", "DE"}

    def test_empty_results_returns_empty_list(self) -> None:
        # Arrange
        ar = AnalyticsResult(
            question=_make_question(),
            city_results=[],
            execution_time=0.1,
            total_cities_found=0,
            data_sources_used=[],
        )

        # Act
        result = ar.get_countries_represented()

        # Assert
        assert result == []


class TestAnalyticsResultToDict:
    """Test AnalyticsResult.to_dict (line 173)."""

    def test_to_dict_includes_all_fields(self) -> None:
        # Arrange
        question = _make_question(region_value="HU")
        city = _make_city_result()
        ar = _make_analytics_result(
            city_results=[city],
            question=question,
            execution_time=1.23,
            total_cities_found=5,
            data_sources_used=[DataSource.OPEN_METEO, DataSource.ECMWF],
            statistics={"mean": 20.0},
            provider_statistics={"open-meteo": {"calls": 1}},
            average_quality_score=0.95,
            average_confidence=0.88,
        )

        # Act
        result = ar.to_dict()

        # Assert
        assert result["question"]["question_text"] == "Melyik város a legmelegebb?"
        assert len(result["city_results"]) == 1
        assert result["execution_time"] == 1.23
        assert result["total_cities_found"] == 5
        assert result["data_sources_used"] == ["open-meteo", "ecmwf"]
        assert result["statistics"] == {"mean": 20.0}
        assert result["provider_statistics"] == {"open-meteo": {"calls": 1}}
        assert result["average_quality_score"] == 0.95
        assert result["average_confidence"] == 0.88
        assert "created_at" in result


# ===================================================================
# QueryResults tests (AnomalyResult utility methods)
# ===================================================================


def _make_query_results(
    anomalies: dict[str, list[AnomalyResult]] | None = None,
    **overrides: Any,
) -> QueryResults:
    """Create a QueryResults with defaults."""
    defaults: dict[str, Any] = {
        "query_parameters": {"metric": "temperature"},
        "anomalies": anomalies or {},
        "execution_time": 0.3,
        "total_records_analyzed": 100,
        "date_range": (date(2025, 1, 1), date(2025, 12, 31)),
    }
    defaults.update(overrides)
    return QueryResults(**defaults)


class TestQueryResultsGetTotalAnomalies:
    """Test QueryResults.get_total_anomalies (line 211)."""

    def test_empty_anomalies_returns_zero(self) -> None:
        # Arrange
        qr = _make_query_results(anomalies={})

        # Act
        result = qr.get_total_anomalies()

        # Assert
        assert result == 0

    def test_counts_all_anomalies_across_parameters(self) -> None:
        # Arrange
        a1 = _make_anomaly(anomaly_date=date(2025, 6, 1))
        a2 = _make_anomaly(anomaly_date=date(2025, 6, 2))
        a3 = _make_anomaly(anomaly_date=date(2025, 6, 3))
        qr = _make_query_results(
            anomalies={
                "temperature": [a1, a2],
                "precipitation": [a3],
            },
        )

        # Act
        result = qr.get_total_anomalies()

        # Assert
        assert result == 3


class TestQueryResultsGetAnomaliesBySeverity:
    """Test QueryResults.get_anomalies_by_severity (lines 215-220)."""

    def test_empty_returns_empty_dict(self) -> None:
        # Arrange
        qr = _make_query_results(anomalies={})

        # Act
        result = qr.get_anomalies_by_severity()

        # Assert
        assert result == {}

    def test_counts_severities_correctly(self) -> None:
        # Arrange
        high_anomaly = _make_anomaly(severity=AnomalySeverity.HIGH)
        extreme_anomaly = _make_anomaly(severity=AnomalySeverity.EXTREME)
        high_anomaly_2 = _make_anomaly(severity=AnomalySeverity.HIGH)
        qr = _make_query_results(
            anomalies={
                "temperature": [high_anomaly, extreme_anomaly],
                "wind": [high_anomaly_2],
            },
        )

        # Act
        result = qr.get_anomalies_by_severity()

        # Assert
        assert result["high"] == 2
        assert result["extreme"] == 1

    def test_single_parameter_single_anomaly(self) -> None:
        # Arrange
        moderate = _make_anomaly(severity=AnomalySeverity.MODERATE)
        qr = _make_query_results(anomalies={"humidity": [moderate]})

        # Act
        result = qr.get_anomalies_by_severity()

        # Assert
        assert result == {"moderate": 1}


class TestQueryResultsGetMostActiveDays:
    """Test QueryResults.get_most_active_days (lines 224-230)."""

    def test_empty_returns_empty_list(self) -> None:
        # Arrange
        qr = _make_query_results(anomalies={})

        # Act
        result = qr.get_most_active_days()

        # Assert
        assert result == []

    def test_returns_sorted_by_count_desc(self) -> None:
        # Arrange
        day1 = date(2025, 6, 1)
        day2 = date(2025, 6, 2)
        day3 = date(2025, 6, 3)
        a1 = _make_anomaly(anomaly_date=day1)
        a2 = _make_anomaly(anomaly_date=day1)
        a3 = _make_anomaly(anomaly_date=day1)
        a4 = _make_anomaly(anomaly_date=day2)
        a5 = _make_anomaly(anomaly_date=day2)
        a6 = _make_anomaly(anomaly_date=day3)
        qr = _make_query_results(
            anomalies={
                "temperature": [a1, a2, a3, a4],
                "precipitation": [a5, a6],
            },
        )

        # Act
        result = qr.get_most_active_days(n=10)

        # Assert
        assert result[0] == (day1, 3)
        assert result[1] == (day2, 2)
        assert result[2] == (day3, 1)

    def test_limits_to_n(self) -> None:
        # Arrange
        anomalies_by_day = [_make_anomaly(anomaly_date=date(2025, 6, d)) for d in range(1, 6)]
        qr = _make_query_results(
            anomalies={"temperature": anomalies_by_day},
        )

        # Act
        result = qr.get_most_active_days(n=3)

        # Assert
        assert len(result) == 3

    def test_single_day_multiple_anomalies(self) -> None:
        # Arrange
        single_day = date(2025, 7, 20)
        a1 = _make_anomaly(anomaly_date=single_day)
        a2 = _make_anomaly(anomaly_date=single_day)
        qr = _make_query_results(
            anomalies={"temperature": [a1], "wind": [a2]},
        )

        # Act
        result = qr.get_most_active_days(n=10)

        # Assert
        assert result == [(single_day, 2)]


class TestQueryResultsGetAnomaliesForParameter:
    """Test QueryResults.get_anomalies_for_parameter (line 234)."""

    def test_existing_parameter_returns_list(self) -> None:
        # Arrange
        a1 = _make_anomaly(anomaly_date=date(2025, 6, 1))
        a2 = _make_anomaly(anomaly_date=date(2025, 6, 2))
        qr = _make_query_results(
            anomalies={"temperature": [a1, a2], "wind": []},
        )

        # Act
        result = qr.get_anomalies_for_parameter("temperature")

        # Assert
        assert len(result) == 2

    def test_missing_parameter_returns_empty_list(self) -> None:
        # Arrange
        qr = _make_query_results(anomalies={"temperature": [_make_anomaly()]})

        # Act
        result = qr.get_anomalies_for_parameter("humidity")

        # Assert
        assert result == []


class TestQueryResultsToDict:
    """Test QueryResults.to_dict (line 238)."""

    def test_to_dict_returns_all_fields(self) -> None:
        # Arrange
        a1 = _make_anomaly(anomaly_date=date(2025, 6, 1))
        qr = _make_query_results(
            query_parameters={"metric": "temperature", "region": "HU"},
            anomalies={"temperature": [a1]},
            execution_time=2.5,
            total_records_analyzed=500,
            date_range=(date(2025, 1, 1), date(2025, 12, 31)),
            anomaly_summary={"total": 1, "high": 1},
        )

        # Act
        result = qr.to_dict()

        # Assert
        assert result["query_parameters"] == {"metric": "temperature", "region": "HU"}
        assert "temperature" in result["anomalies"]
        assert len(result["anomalies"]["temperature"]) == 1
        assert result["execution_time"] == 2.5
        assert result["total_records_analyzed"] == 500
        assert result["date_range"] == ["2025-01-01", "2025-12-31"]
        assert result["anomaly_summary"] == {"total": 1, "high": 1}
        assert "created_at" in result

    def test_to_dict_with_empty_anomalies(self) -> None:
        # Arrange
        qr = _make_query_results(anomalies={})

        # Act
        result = qr.to_dict()

        # Assert
        assert result["anomalies"] == {}

    def test_to_dict_date_range_serialized_as_iso(self) -> None:
        # Arrange
        qr = _make_query_results(
            date_range=(date(2025, 3, 1), date(2025, 9, 30)),
        )

        # Act
        result = qr.to_dict()

        # Assert
        assert result["date_range"] == ["2025-03-01", "2025-09-30"]
