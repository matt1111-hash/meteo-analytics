"""Validation and edge-case tests for AnalyzeMultiCityUseCase.

Targets uncovered lines in src/application/use_cases/analyze_multi_city.py:
constructor validation (50, 52), empty cities (89, 99-100), all-fetch-failed
(121-122), aggregate=False (133), skip fetch_success=False (172), transform
exception (180-181), _fallback_result (185), invalid limit (200, 202-204),
invalid max_cities (211-213), _resolve_region_scope (237, 240), and
_validate_query / _require_* helpers (244, 246, 248, 253, 259).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
from src.application.use_cases.use_case_result import ResultStatus
from src.data.enums import AnalyticsMetric
from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.services.analytics_transform_service import (
    AnalyticsTransformService,
)
from src.domain.analytics.services.region_resolver import RegionResolverService
from src.domain.entities.weather import CityWeatherResult
from src.domain.ports import CityRepositoryPort

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

QUERY_TYPES: dict[str, dict[str, Any]] = {
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb szél {region}ban?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    }
}

REGIONS: dict[str, dict[str, Any]] = {
    "Hungary": {
        "name": "Magyarország",
        "country_codes": ["HU"],
        "max_cities": 5,
        "batch_size": 2,
        "rate_limit_delay": 0.0,
    },
    "Global": {
        "name": "Világ",
        "country_codes": [],
        "max_cities": 10,
        "batch_size": 5,
        "rate_limit_delay": 0.0,
    },
}

HUNGARIAN_MAPPING: dict[str, list[str]] = {"Budapest": ["Budapest"]}


# ---------------------------------------------------------------------------
# Lightweight fake dependencies
# ---------------------------------------------------------------------------


class FakeCityRepository(CityRepositoryPort):
    """In-memory city repository for tests."""

    def __init__(self, cities: list[dict[str, Any]] | None = None) -> None:
        self.cities: list[dict[str, Any]] = cities or []
        self.last_limit: int | None = None

    def validate_paths(self) -> None:
        return None

    def get_cities_for_region(
        self,
        mapped_region: str,
        original_region: str,
        country_codes: list[str],
        limit: int,
        hungarian_mapping: dict[str, list[str]],
    ) -> list[dict[str, object]]:
        self.last_limit = limit
        return self.cities

    def get_cities_by_names(self, city_names: list[str]) -> list[dict[str, object]]:
        return self.cities


class FakeWeatherFetchService:
    """Returns pre-seeded weather data."""

    def __init__(self, weather_data: list[CityWeatherData]) -> None:
        self.weather_data = weather_data

    def fetch_weather_data_dual_api_batch(
        self,
        cities: list[dict[str, Any]],
        date: str,
        region_config: dict[str, Any],
        **kwargs: Any,
    ) -> list[CityWeatherData]:
        return self.weather_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _city(
    name: str,
    windspeed: float,
    fetch_success: bool = True,
) -> CityWeatherData:
    """Create a CityWeatherData instance for testing."""
    return CityWeatherData(
        city=name,
        country="X",
        country_code="XX",
        lat=0.0,
        lon=0.0,
        population=1,
        date="2024-01-01",
        windspeed_10m_max=windspeed,
        fetch_success=fetch_success,
    )


def _make_use_case(
    repo: FakeCityRepository | None = None,
    weather_data: list[CityWeatherData] | None = None,
    query_types: dict[str, dict[str, Any]] | None = None,
    regions: dict[str, dict[str, Any]] | None = None,
    transform_service: AnalyticsTransformService | None = None,
    *,
    _allow_empty_query_types: bool = False,
    _allow_empty_regions: bool = False,
) -> AnalyzeMultiCityUseCase:
    """Build an AnalyzeMultiCityUseCase with sensible defaults.

    The _allow_empty_* flags let constructor-validation tests pass empty
    dicts without the helper overriding them with defaults.
    """
    effective_qt = (
        query_types
        if (query_types is not None and (query_types or _allow_empty_query_types))
        else QUERY_TYPES
    )
    effective_regions = (
        regions if (regions is not None and (regions or _allow_empty_regions)) else REGIONS
    )
    resolver = RegionResolverService()
    ts = transform_service or AnalyticsTransformService(effective_qt)
    city_repo = repo or FakeCityRepository(
        [
            {"city": "A", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0},
            {"city": "B", "country": "X", "country_code": "XX", "lat": 1.0, "lon": 1.0},
        ]
    )
    weather_service = FakeWeatherFetchService(weather_data or [_city("A", 20.0), _city("B", 30.0)])
    return AnalyzeMultiCityUseCase(
        region_resolver=resolver,
        city_repository=city_repo,
        weather_fetch_service=weather_service,
        analytics_transform_service=ts,
        query_types=effective_qt,
        regions=effective_regions,
        hungarian_mapping=HUNGARIAN_MAPPING,
    )


def _query(**overrides: Any) -> MultiCityQuery:
    """Create a MultiCityQuery with defaults that can be overridden."""
    defaults: dict[str, Any] = {
        "query_type": "windiest_today",
        "region": "Hungary",
        "date": "2024-01-01",
        "limit": None,
        "max_cities": None,
    }
    defaults.update(overrides)
    return MultiCityQuery(**defaults)


# ===================================================================
# 1. Constructor validation — empty query_types (line 50)
# ===================================================================


def test_init_raises_on_empty_query_types() -> None:
    """ValueError when query_types mapping is empty."""
    with pytest.raises(ValueError, match="query_types mapping is required"):
        _make_use_case(query_types={}, _allow_empty_query_types=True)


# ===================================================================
# 2. Constructor validation — empty regions (line 52)
# ===================================================================


def test_init_raises_on_empty_regions() -> None:
    """ValueError when regions mapping is empty."""
    with pytest.raises(ValueError, match="regions mapping is required"):
        _make_use_case(regions={}, _allow_empty_regions=True)


# ===================================================================
# 3. No cities found via explicit city names (lines 89, 99-100)
# ===================================================================


def test_execute_no_cities_found_with_explicit_names_returns_error() -> None:
    """When query.cities is set but repo returns no matches, result is ERROR."""
    repo = FakeCityRepository(cities=[])
    use_case = _make_use_case(repo=repo)
    query = _query(cities=["NonExistent"])

    result = use_case.execute(query)

    assert result.status == ResultStatus.ERROR
    assert result.error_message == "Nincsenek városok a lekérdezéshez"
    assert result.data is not None


# ===================================================================
# 4. All fetches failed — all CityWeatherData have fetch_success=False
#    (lines 121-122)
# ===================================================================


def test_execute_all_fetches_failed_returns_error() -> None:
    """When every CityWeatherData has fetch_success=False, result is ERROR."""
    repo = FakeCityRepository(
        [{"city": "A", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0}]
    )
    weather = [_city("A", 0.0, fetch_success=False)]
    use_case = _make_use_case(repo=repo, weather_data=weather)
    query = _query()

    result = use_case.execute(query)

    assert result.status == ResultStatus.ERROR
    assert "sikeres" in result.error_message


# ===================================================================
# 5. aggregate=False path — result_limit should be None (line 133)
# ===================================================================


def test_execute_aggregate_false_returns_all_records() -> None:
    """With aggregate=False, result_limit is None so all daily records are kept."""
    repo = FakeCityRepository(
        [
            {"city": "A", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0},
            {"city": "B", "country": "X", "country_code": "XX", "lat": 1.0, "lon": 1.0},
        ]
    )
    weather = [_city("A", 10.0), _city("B", 20.0)]
    use_case = _make_use_case(repo=repo, weather_data=weather)
    query = _query(limit=1)

    result = use_case.execute(query, aggregate=False)

    assert result.is_success
    # aggregate=False => result_limit=None => no slicing, both cities returned
    assert len(result.data.city_results) == 2


# ===================================================================
# 6. Skip city with fetch_success=False during transformation (line 172)
# ===================================================================


def test_transform_results_skips_fetch_failure() -> None:
    """Cities with fetch_success=False are skipped in _transform_results."""
    repo = FakeCityRepository(
        [
            {"city": "A", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0},
            {"city": "B", "country": "X", "country_code": "XX", "lat": 1.0, "lon": 1.0},
        ]
    )
    weather = [
        _city("A", 10.0, fetch_success=False),
        _city("B", 20.0, fetch_success=True),
    ]
    use_case = _make_use_case(repo=repo, weather_data=weather)
    query = _query()

    result = use_case.execute(query)

    assert result.is_success
    # Only city B should appear; A was skipped due to fetch_success=False
    assert len(result.data.city_results) == 1
    assert result.data.city_results[0].city_name == "B"


# ===================================================================
# 7. Exception during transform (lines 180-181)
# ===================================================================


def test_transform_results_handles_exception_during_transform() -> None:
    """Exception in transform_to_city_weather_result is caught, city skipped."""
    ts = MagicMock(spec=AnalyticsTransformService)
    ts.process_weather_results.return_value = [_city("A", 10.0)]
    ts.transform_to_city_weather_result.side_effect = RuntimeError("boom")
    ts.calculate_statistics_for_results_none_safe.return_value = {}
    ts.get_provider_stats.return_value = {}

    use_case = _make_use_case(transform_service=ts)
    query = _query()

    # transform raises for every city => transformed_results is empty => ERROR
    result = use_case.execute(query)

    assert result.status == ResultStatus.ERROR
    assert "sikeres" in result.error_message


# ===================================================================
# 8. _fallback_result method (line 185)
# ===================================================================


def test_fallback_result_creates_empty_analytics_result() -> None:
    """_fallback_result delegates to analytics_transform_service.create_empty_analytics_result."""
    ts = MagicMock(spec=AnalyticsTransformService)
    ts.create_empty_analytics_result.return_value = MagicMock()
    ts.process_weather_results.return_value = []
    ts.calculate_statistics_for_results_none_safe.return_value = {}
    ts.get_provider_stats.return_value = {}

    use_case = _make_use_case(transform_service=ts)
    query = _query()

    result = use_case.execute(query)

    # No cities at all => fallback result should have been created
    assert result.status == ResultStatus.ERROR
    ts.create_empty_analytics_result.assert_called_once()


# ===================================================================
# 9a. Invalid limit handling — limit <= 0 returns all (line 200)
# ===================================================================


def test_apply_result_limit_returns_all_when_limit_is_zero() -> None:
    """A limit of 0 is treated as invalid and all results are returned."""
    use_case = _make_use_case()
    dummy_results = [
        CityWeatherResult(
            city_name="A",
            country="X",
            country_code="XX",
            latitude=0.0,
            longitude=0.0,
            value=1.0,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date="2024-01-01",
            rank=1,
        ),
        CityWeatherResult(
            city_name="B",
            country="X",
            country_code="XX",
            latitude=1.0,
            longitude=1.0,
            value=2.0,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date="2024-01-01",
            rank=2,
        ),
    ]

    actual = use_case._apply_result_limit(dummy_results, 0)

    assert len(actual) == 2


# ===================================================================
# 9b. Invalid limit handling — non-int limit returns all
#     (lines 202-204)
# ===================================================================


def test_apply_result_limit_returns_all_when_limit_is_not_int() -> None:
    """A non-int limit triggers TypeError/ValueError and all results are returned."""
    use_case = _make_use_case()
    dummy_results = [
        CityWeatherResult(
            city_name="A",
            country="X",
            country_code="XX",
            latitude=0.0,
            longitude=0.0,
            value=1.0,
            metric=AnalyticsMetric.WINDSPEED_10M_MAX,
            date="2024-01-01",
            rank=1,
        ),
    ]

    actual = use_case._apply_result_limit(dummy_results, "bad")

    assert len(actual) == 1


# ===================================================================
# 10a. Invalid max_cities — None falls back to region config
#      (line 210, confirmed via last_limit)
# ===================================================================


def test_resolve_city_limit_returns_region_default_when_max_cities_none() -> None:
    """When max_cities is None, the region default is used."""
    use_case = _make_use_case()
    query = _query(max_cities=None)

    limit = use_case._resolve_city_limit(query, REGIONS["Hungary"])

    assert limit == 5


# ===================================================================
# 10b. Invalid max_cities — bad value falls back to region config
#      (lines 212-213)
# ===================================================================


def test_resolve_city_limit_returns_region_default_on_invalid_max_cities() -> None:
    """A non-numeric max_cities triggers TypeError/ValueError and falls back to region config."""
    use_case = _make_use_case()
    query = _query(max_cities="not_a_number")  # type: ignore[arg-type]

    limit = use_case._resolve_city_limit(query, REGIONS["Hungary"])

    assert limit == 5


# ===================================================================
# 10c. Negative max_cities falls back to region config (line 210)
# ===================================================================


def test_resolve_city_limit_returns_region_default_on_negative_max_cities() -> None:
    """A negative max_cities falls back to the region default."""
    use_case = _make_use_case()
    query = _query(max_cities=-3)

    limit = use_case._resolve_city_limit(query, REGIONS["Hungary"])

    assert limit == 5


# ===================================================================
# 11. _resolve_region_scope("Global") returns GLOBAL (line 237)
# ===================================================================


def test_resolve_region_scope_global() -> None:
    """Mapped region 'Global' maps to RegionScope.GLOBAL."""
    from src.domain.value_objects.enums import RegionScope  # noqa: PLC0415

    use_case = _make_use_case()

    scope = use_case._resolve_region_scope("Global")

    assert scope == RegionScope.GLOBAL


# ===================================================================
# 11b. _resolve_region_scope fallback for non-Hungary, non-Global (line 240)
# ===================================================================


def test_resolve_region_scope_continent_fallback() -> None:
    """Any region other than 'Global' or 'Hungary' maps to RegionScope.CONTINENT."""
    from src.domain.value_objects.enums import RegionScope  # noqa: PLC0415

    use_case = _make_use_case()

    scope = use_case._resolve_region_scope("Europe")

    assert scope == RegionScope.CONTINENT


# ===================================================================
# 12. Missing query_type raises ValueError (line 244)
# ===================================================================


def test_validate_query_raises_on_empty_query_type() -> None:
    """Empty query_type triggers ValueError."""
    use_case = _make_use_case()
    query = _query(query_type="")

    with pytest.raises(ValueError, match="query_type hiányzik"):
        use_case._validate_query(query)


# ===================================================================
# 13. Missing region raises ValueError (line 246)
# ===================================================================


def test_validate_query_raises_on_empty_region() -> None:
    """Empty region triggers ValueError."""
    use_case = _make_use_case()
    query = _query(region="")

    with pytest.raises(ValueError, match="region hiányzik"):
        use_case._validate_query(query)


# ===================================================================
# 14. Missing date raises ValueError (line 248)
# ===================================================================


def test_validate_query_raises_on_empty_date() -> None:
    """Empty date triggers ValueError."""
    use_case = _make_use_case()
    query = _query(date="")

    with pytest.raises(ValueError, match="date hiányzik"):
        use_case._validate_query(query)


# ===================================================================
# 15. Unknown query_type raises ValueError (line 253)
# ===================================================================


def test_require_query_config_raises_on_unknown_query_type() -> None:
    """An unregistered query_type triggers ValueError."""
    use_case = _make_use_case()

    with pytest.raises(ValueError, match="Ismeretlen lekérdezés típus"):
        use_case._require_query_config("nonexistent_type")


# ===================================================================
# 16. Unknown region raises ValueError (line 259)
# ===================================================================


def test_require_region_config_raises_on_unknown_region() -> None:
    """An unregistered mapped region triggers ValueError."""
    use_case = _make_use_case()

    with pytest.raises(ValueError, match="Ismeretlen régió"):
        use_case._require_region_config("Antarctica")
