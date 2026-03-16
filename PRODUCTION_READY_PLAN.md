# Production Ready Plan

## Goal

Bring `meteo-analytics` to a state where `./quality_gate.sh --ci` passes without changing protected config files or weakening tests.

## Current Status

Completed:
- Full API stabilization is done.
- Split-test compatibility fixes are in place for:
  - providers API tests
  - auth/openapi fixtures
  - wind rose route tests
  - anomaly storage/profile tests
  - city manager tests
  - geo utils tests
  - provider/weather client tests
- Test package/import compatibility fixes are in place for duplicate basename cases
- Coverage expansion is done for the latest non-GUI domain/entity targets
- Full test suite passes:
  - `venv/bin/python -m pytest tests/ -q --tb=no`
  - Result: `1582 passed`

Current CI blockers:
- `./quality_gate.sh --ci` still fails on:
  - xenon complexity gate

Latest measured CI facts:
- Tests: PASS
- Ruff lint: PASS
- Ruff format: PASS
- Mypy: PASS
- Architecture/import-linter: PASS
- File size gate: PASS
- Security/bandit: PASS
- Coverage: PASS
  - Total coverage: `90.41%`
  - CI minimum: `90%`
- Complexity: FAIL
  - Remaining blocking `C/D` ranked blocks are still numerous
  - Most are in `src/presentation/gui/...`
  - A smaller non-GUI set remains in `src/domain/...`, `src/data/...`, and `src/api/...`

## What Was Already Fixed

- Pydantic forward-ref and schema rebuild issues in provider DTO and wind rose API chain
- Missing `app` and `anyio_backend` fixtures for API tests
- Missing imports in split tests (`patch`, `status`, support exports)
- Wrapper/split-module compatibility regressions in:
  - `src/api/routes/wind_rose.py`
  - `src/api/routes/wind_rose_part3.py`
  - `src/api/dto/provider_dto_part2.py`
- Support-module export gaps across split test families
- Targeted xenon reductions already applied to:
  - `src/api/routes/wind_rose_part3.py`
  - `src/data/city_manager_search.py`
  - `src/infrastructure/repositories/city_repository_paths.py`
- New coverage tests added for:
  - `tests/api/test_weather_adapter.py`
  - `tests/application/services/test_wind_analysis_service.py`
  - `tests/infrastructure/repositories/test_city_repository_queries.py`
  - `tests/domain/test_location_entities.py`
  - `tests/domain/test_time_and_query_entities.py`
  - `tests/domain/test_trend_and_enum_utils.py`
- `CityManagerSearch.search_unified()` compatibility restored for `global_limit_ratio`
- `src/data/city_manager_search.py` reduced below the CI file-size threshold
- Duplicate test module collection issue resolved with missing package markers in:
  - `tests/application/services/`
  - `tests/application/use_cases/`
  - `tests/domain/analytics/`

## Remaining Work

### Phase 1: Raise Coverage To 90%+

Status: completed.

Result:
- Repository coverage is now `90.41%`
- `./quality_gate.sh --ci` confirms coverage is above the CI threshold

Note:
- There is still a domain contract inconsistency worth revisiting later:
  - `src/domain/entities/location.py::from_city_info()`
  - expects attributes not guaranteed by `src/domain/value_objects/city_info.py`
  - This is not currently blocking CI, but it is a real architecture mismatch.

### Phase 2: Reduce Xenon Complexity

Objective: eliminate enough `C/D` blocks so xenon passes with the current CI threshold.

Current shape of the remaining problem:
- Most remaining xenon failures are in `src/presentation/gui/...`
- A smaller set remains in non-GUI modules across:
  - `src/domain/...`
  - `src/data/...`
  - `src/api/...`

Execution strategy:
- Continue from smallest, least-coupled non-GUI blocks first.
- Then work through GUI mixins/helpers in descending simplification value.
- Favor extraction of pure helper functions and smaller branch units.
- Keep files below the existing file-size gate while reducing branch complexity.

Suggested next non-GUI xenon targets:
- `src/domain/analytics/services/analytics_transform_service_part2.py`
- `src/domain/analytics/services/weather_fetch_service.py`
- `src/data/distance_calculator_part2.py`
- `src/data/geo_utils_region.py`
- `src/api/routes/anomalies.py`

Suggested verification:
- Run xenon on the touched files first.
- Then rerun:
  - `./quality_gate.sh --ci`

Exit criteria:
- Xenon no longer reports blocking `C/D` failures for the repo.

### Phase 3: Final CI Validation

Objective: confirm the repository is actually CI-ready.

Run in order:
- `venv/bin/python -m pytest tests/ -q --tb=no`
- `./quality_gate.sh --ci`

Exit criteria:
- Full test suite passes
- Coverage passes
- Xenon passes
- Entire `quality_gate.sh --ci` passes

## Next Session Start Point

Start with these actions:
1. Re-run `./quality_gate.sh --ci` once to refresh the current xenon and coverage list.
2. Ignore coverage work unless a xenon refactor accidentally changes behavior and needs compensating tests.
3. Start xenon reduction on the next smallest non-GUI blockers first:
   - `src/domain/analytics/services/analytics_transform_service_part2.py`
   - `src/domain/analytics/services/weather_fetch_service.py`
   - `src/data/distance_calculator_part2.py`
   - `src/api/routes/anomalies.py`
4. Only move into `src/presentation/gui/...` after the remaining non-GUI xenon wins are exhausted.

## Working Rules For Execution

- Preserve unrelated user changes already present in the worktree.
- Do not modify:
  - `.quality_gate.conf`
  - `quality_gate.sh`
  - `pyproject.toml`
- Do not weaken tests or reduce gate strictness.
- After every fix batch, run the narrowest possible verification command immediately.
- Only commit after the full suite and `./quality_gate.sh --ci` are green.

## Definition Of Done

The project is production ready for this task only when all of the following are true:
- Full `tests/` suite is green
- `./quality_gate.sh --ci` is green
- Coverage is at or above CI threshold
- Xenon complexity passes
- The repo remains within the architecture and file-size constraints
- A clean, reviewable commit can be created without reverting unrelated user work
