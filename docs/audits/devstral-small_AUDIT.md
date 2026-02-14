# PROJECT AUDIT REPORT
**Model:** devstral-small | **Date:** 2025-02-11 | **Prompt:** v4.2

## §1 EXECUTIVE SUMMARY

A meteo-analytics projekt egy komplex időjárás-analitikai rendszer, amely Clean Architecture elveket követ. A projekt jól szervezett, de jelentős minőségi és tesztfedés problémákkal rendelkezik. A tesztfedés csak 15.77%, ami kritikusan alacsony a 85% célhoz képest. A kódminőségben jelentős ruff és mypy hibák vannak, valamint több nagy fájl (443-300 soros) is található. A Clean Architecture alapvetően helyes, de a presentation réteg közvetlen domain importokkal rendelkezik, ami megszegi az architekturális elveket.

**Risk:** 🔴 | **Confidence:** HIGH

## §2 PROJECT STRUCTURE

- **src/ fájlszám:** 502 Python fájl
- **src/ LOC:** 119,490 sor
- **Teljes repo fájlszám:** 13,581 fájl
- **Teljes repo LOC:** 9,831,096 sor
- **Stack:** Python 3.10+, PySide6, FastAPI, SQLite, pandas, numpy
- **Architektúra minta:** Clean Architecture (domain/application/infrastructure/presentation)

**Legacy/root fájlok:**
- `config.py` (2209 LOC)
- `analyze_coverage.py`
- `quality_gate.sh` (13524 bájt)
- `.quality_gate.conf`
- `.pre-commit-config.yaml`
- `pyproject.toml`

## §3 CLEAN ARCHITECTURE COMPLIANCE

**Verdict:** ⚠️

### Layer tábla:

| Layer | Engedélyezett | Tiltott | Status |
|-------|---------------|---------|--------|
| domain | stdlib, typing, dataclasses, abc | BÁRMILYEN external | ✅ (de pandas/numpy importokkal) |
| application | domain, stdlib | infrastructure, presentation | ✅ |
| infrastructure | domain, application, external libs | presentation | ✅ |
| presentation | application, infrastructure, UI libs | domain (közvetlen) | ❌ (direct domain imports) |

### Violations:

1. **Domain layer violations:**
   - `src/domain/analytics/wind_statistics.py` - pandas import (external library)
   - `src/domain/analytics/wind_extractors.py` - pandas import
   - `src/domain/analytics/services/trend_statistics.py` - numpy import
   - `src/domain/analytics/services/trend_data_processor.py` - pandas import

2. **Presentation layer violations:**
   - `src/presentation/gui/hungarian_map_tab/map_widget.py` - direct domain.entities import
   - `src/presentation/gui/hungarian_map_tab/core.py` - direct domain.entities import
   - `src/presentation/gui/results_panel/windy_days_tab/core.py` - direct domain.analytics import
   - `src/presentation/gui/results_panel/windy_days_tab/data_processor.py` - direct domain.analytics import
   - `src/presentation/gui/results_panel/windy_days_tab/handlers.py` - direct domain.analytics import
   - `src/presentation/gui/panel_widgets/location_widget/core.py` - direct domain.entities import
   - `src/presentation/gui/panel_widgets/location_widget/signal_handlers.py` - direct domain.entities import
   - `src/presentation/gui/weather_data_bridge/core.py` - direct domain.entities import

3. **TYPE_CHECKING violations:**
   - 103 fájl használ TYPE_CHECKING importokat, ami compile-time couplingot okoz
   - Ezek a presentation rétegben találhatók, de nem domain importok

4. **Circular imports:**
   - Nincs nyilvánvaló circular import problémák

## §4 CODE QUALITY

### God classes (>250 LOC):
- `src/presentation/gui/windows/main_window.py` (443 LOC)
- `src/api/routes/providers.py` (396 LOC)
- `src/presentation/gui/controller/app_controller.py` (389 LOC)
- `src/domain/ports/__init__.py` (383 LOC)
- `src/presentation/gui/analytics/analytics_tabs.py` (358 LOC)
- `src/presentation/gui/results_panel/extreme/category_calculators.py` (344 LOC)
- `src/presentation/gui/charts/precipitation_chart/tooltip.py` (325 LOC)
- `src/presentation/gui/analytics/analytics_view/core.py` (316 LOC)
- `src/presentation/gui/weather_data_bridge/core.py` (315 LOC)
- `src/presentation/gui/results_panel/extreme_events_tab.py` (315 LOC)

### Complex functions (>50 sor):
- `src/presentation/gui/utils/formatting/statistics.py:17:calculate_statistics`
- `src/presentation/gui/hungarian_map_tab/initialization.py:129:_initialize_step_4`
- `src/presentation/gui/map/map_visualizer/debug.py:66:get_http_debug_info`
- `src/presentation/gui/trend_analytics/trend_data_processor/calculator.py:11:calculate_trend_statistics`
- `src/presentation/gui/results_panel/results_panel/signal_handlers.py:133:_on_windy_days_export_requested`
- `src/presentation/gui/color_palette/presets.py:89:is_valid_preset`
- `src/presentation/gui/panel_widgets/provider_widget/provider_data.py:80:get_default_warning_thresholds`
- `src/presentation/gui/charts/wind_rose_chart/data_handler.py:7:extract_wind_data`
- `src/presentation/gui/controller/analysis_handler/provider_integration.py:79:_extract_coordinates_from_request`
- `src/domain/analytics/statistics.py:22:safe_median`

### Type hint coverage:
- **1966/2285 függvények típusozottak** (86%)
- Jó típusozottság, de még 319 függvény nincs típusozva

### Ruff hibák:
- **1091 hiba** a teljes src/ könyvtárban
- Főbb problémák: F841 (unused variables), E402 (import not at top), F401 (unused imports)

### Mypy hibák:
- **1453 hiba** a teljes src/ könyvtárban
- Főbb problémák: attribute-defined errors, type annotation issues

### Nesting depth:
- Nincs nyilvánvaló >4 szintű nesting problémák
- A majority of functions have ≤3 nesting levels

### Cyclomatic complexity (Radon):
- **Average complexity:** A (2.83105981112277)
- **Complexity C:** 1044 block (36.5%)
- **Complexity D:** 365 block (12.8%)
- **Total blocks analyzed:** 2859
- **14.3% of blocks have C/D complexity**

### Dead code (Vulture):
- **19 dead code issue** (min-confidence 80%)
- Főbb problémák: unused variables, unreachable code
- Minőségi problémák, nem kritikusak

## §5 TEST ANALYSIS

**Futtatott parancs:**
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -q --tb=no
```

**Eredmény:**
- **1004 teszt futott, mindegyik sikeres**
- **Tesztek futási ideje:** 23.68 másodperc
- **Coverage:** 15.77% (line coverage)
- **Branch coverage:** 87% (de line coverage kritikusan alacsony)

### Coverage részletek:
- **TOTAL:** 23,577 statements, 19,829 missed, 5,656 branches, 87 branch parts
- **Coverage:** 15.77%
- **33 fájl teljes coverage-sel (0% missed)**

### Untested critical paths (risk alapján rangsorolva):
1. **src/presentation/gui/** - 99% of files have 0% coverage (224 files)
2. **src/api/routes/** - 18-83% coverage, critical API endpoints missing
3. **src/application/use_cases/calculate_trend.py** - 23% coverage
4. **src/domain/analytics/services/trend_calculator.py** - 21% coverage
5. **src/domain/analytics/services/trend_statistics.py** - 32% coverage
6. **src/domain/analytics/wind_reporting.py** - 10% coverage
7. **src/data/city_manager_hungarian.py** - 18% coverage
8. **src/data/city_manager_search.py** - 8% coverage

### Source-to-test fájl arány:
- **src/:** 502 Python fájlok
- **tests/:** 1004 tesztfájlok (de a majority domain/data tesztek)
- **Presentation layer:** 0 tesztek
- **API layer:** 1 tesztfájl (providers)

### No-assertion tesztek:
- Nincs nyilvánvaló no-assertion tesztek
- Minden teszt használ assert-okat

## §6 SECURITY FINDINGS

### .env fájl:
- **Status:** ✅ NEM git-tracked
- `git ls-files .env` - üres kimenet
- A `.env` fájl tartalmaz API kulcsokat, de nem van gitben

### Hardcoded secrets:
- **Nincs** hardcoded API kulcs a forráskódban
- API kulcsok environment variables-ból betöltődnek
- `src/data/meteostat_provider.py` - `os.getenv("METEOSTAT_API_KEY")`
- `src/data/openmeteo_provider.py` - `os.getenv("OPENMETEO_API_KEY")`

### SQL injection:
- **⚠️ Parameterized queries** használva, de **5 SQL injection problémák** bandit által
- `src/data/city_manager_db.py` - `cursor.execute(sql, params)` ✅
- `src/infrastructure/repositories/city_repository_queries.py` - **5 B608 issues** (string-based query construction)
  - `src/infrastructure/repositories/city_repository_queries.py:29:12`
  - `src/infrastructure/repositories/city_repository_queries.py:32:14`
  - `src/infrastructure/repositories/city_repository_queries.py:48:16`
  - `src/infrastructure/repositories/city_repository_queries.py:115:12`
  - `src/infrastructure/repositories/city_repository_queries.py:137:12`

### Unsafe code (eval/exec):
- **✅ Nincs** `eval`, `exec`, `os.system`, `os.popen` használat
- Csak `cursor.execute` használat SQL queries-hez

### MD5/SHA1:
- **✅ Nincs** hashlib, md5, sha import
- Nincs gyenge kriptográfiai algoritmus használat

### API authentication:
- **✅ Valódi auth** használva
- Nem placeholder/public endpoint
- API kulcsok environment variables-ból betöltődnek

### Bandit security issues:
- **19 security issue** összesen
- **5 Medium severity:** SQL injection vectors (B608)
- **14 Low severity:** Try-except-pass (B110), random usage (B311)

## §7 TOOLING & CI/CD

### Ruff:
- **Konfigurálva:** ✅ (`pyproject.toml`)
- **Futtatás:** ✅ (`python -m ruff check src/`)
- **Eredmény:** 1091 hiba
- **Formatting:** ✅ (`python -m ruff format src/`)

### Mypy:
- **Konfigurálva:** ✅ (`pyproject.toml`)
- **Futtatás:** ✅ (`python -m mypy src/ --ignore-missing-imports`)
- **Eredmény:** 1453 hiba

### Pytest:
- **Konfigurálva:** ✅ (`pyproject.toml`)
- **Futtatás:** ✅ (`python -m pytest tests/`)
- **Eredmény:** 1004 teszt, mindegyik sikeres

### Pre-commit:
- **Konfigurálva:** ✅ (`.pre-commit-config.yaml`)
- **Hooks:** ruff, mypy, import-linter, complexity, pytest, detect-secrets
- **Futtatás:** ✅ (`pre-commit run --all-files`)

### Quality Gate:
- **Konfigurálva:** ✅ (`quality_gate.sh`)
- **Futtatás:** ✅ (`./quality_gate.sh --quick`)
- **Eredmény:** 61 ruff hiba, 103 fájl változtatás nélkül

### CI/CD:
- **GitHub Actions:** Nincs nyilvánvaló CI/CD konfig
- **Local CI:** ✅ (`quality_gate.sh --ci`)
- **Strict mode:** ✅ (`quality_gate.sh --strict`)

### Import-linter:
- **Konfigurálva:** ✅ (`.importlinter`)
- **Futtatás:** ✅ (`lint-imports`)
- **Eredmény:** "Missing layer in container 'src': module src.adapters does not exist."
- **Probléma:** A konfig nem illeszkedik a valós struktúrához

### Radon:
- **Futtatás:** ✅ (`radon cc src/ --total-average`)
- **Eredmény:** Average complexity: A (2.83105981112277)
- **Complexity C:** 1044 block (36.5%)
- **Complexity D:** 365 block (12.8%)

### Vulture:
- **Futtatás:** ✅ (`vulture src/ --min-confidence 80`)
- **Eredmény:** 19 dead code issue
- **Főbb problémák:** Unused variables, unreachable code

### Bandit:
- **Futtatás:** ✅ (`bandit -r src/ -f txt -o bandit_results.txt`)
- **Eredmény:** 19 security issue
- **Főbb problémák:** 5 Medium severity SQL injection, 14 Low severity issues

## §8 POSITIVE FINDINGS

1. **TYPE_CHECKING használata:** 103 fájl használ TYPE_CHECKING importokat compile-time coupling elkerülése érdekében
   - `src/presentation/gui/workers/weather_data_worker/api_executor.py`
   - `src/presentation/gui/workers/weather_data_worker/api_builder.py`
   - `src/presentation/gui/workers/weather_data_worker/provider_selector.py`
   - `src/presentation/gui/workers/analysis_worker/data_converter.py`
   - `src/presentation/gui/workers/analysis_worker/interrupt_handler.py`

2. **Jó típusozottság:** 86% type hint coverage (1966/2285 függvények)
   - `src/data/anomaly_profile/default_profiles.py` - 100% típusozottság
   - `src/data/anomaly_profile/manager.py` - 93% típusozottság
   - `src/data/anomaly_profile/profile_actions.py` - 80% típusozottság
   - `src/data/city_manager_db.py` - 88% típusozottság
   - `src/data/distance_calculator.py` - 86% típusozottság

3. **Parameterized SQL queries:** Mind a SQL queries parameterizáltak, SQL injection elleni védelmet biztosítva
   - `src/data/city_manager_db.py` - `cursor.execute(sql, params)`
   - `src/data/city_manager_search.py` - parameterized queries
   - `src/data/city_manager_hungarian.py` - parameterized queries

4. **Environment variables használata:** API kulcsok environment variables-ból betöltődnek, nem hardcoded
   - `src/data/meteostat_provider.py` - `os.getenv("METEOSTAT_API_KEY")`
   - `src/data/openmeteo_provider.py` - `os.getenv("OPENMETEO_API_KEY")`
   - `src/presentation/gui/utils/api_helpers/source_selector.py` - `os.getenv("METEOSTAT_API_KEY")`

5. **Komplex toolchain:** Modern toolchain használata (ruff, mypy, pytest, pre-commit, quality gate)
   - `.pre-commit-config.yaml` - 95 soros konfig
   - `pyproject.toml` - 176 soros konfig
   - `quality_gate.sh` - 13524 bájtos script
   - Támogatott: quick, full, ci, strict, trend, health módok

6. **Jó teszt struktúra:** 1004 teszt, mindegyik sikeres
   - `tests/api/test_providers_route.py` - 20 teszt
   - `tests/application/use_cases/test_analyze_multi_city.py` - 3 teszt
   - `tests/application/use_cases/test_detect_anomalies.py` - 7 teszt
   - `tests/data/anomaly_profile/test_manager.py` - 40 teszt
   - `tests/data/anomaly_profile/test_profile_actions.py` - 40 teszt

7. **Clean Architecture alapvetően helyes:**
   - Domain réteg jól elkülönítve
   - Application réteg csak domain-t importál
   - Infrastructure réteg csak domain-t és application-t importál
   - Csak presentation rétegben vannak kisebb problémák (direct domain imports)

8. **Jó cyclomatic complexity:** Average complexity: A (2.83105981112277)
   - Csak 14.3% of blocks have C/D complexity
   - A majority of functions have ≤3 nesting levels

## §9 RISK MATRIX

| Kategória | Értékelés | Indoklás |
|-----------|------------|-----------|
| **Architecture** | 🔴 | Domain layer external imports, presentation layer direct domain imports |
| **Code Quality** | 🔴 | 1091 ruff hiba, 1453 mypy hiba, 10+ god classes, 5 SQL injection problémák |
| **Tests** | 🚨 | 15.77% coverage (85% cél), 99% of presentation layer untested |
| **Security** | 🟡 | Parameterized SQL, environment variables, no hardcoded secrets, de 5 SQL injection problémák |
| **Maintainability** | 🔴 | Low coverage, high complexity, many ruff/mypy errors, 19 dead code issues |

**Összesített risk:** 🔴 CRITICAL

**Indoklás:**
- A 15.77% coverage kritikusan alacsony
- A presentation layer teljesen untested (0% coverage)
- 1091 ruff hiba és 1453 mypy hiba jelentősen csökkenti a kódminőséget
- A domain layer external imports (pandas/numpy) megszegik a Clean Architecture elveket
- A presentation layer direct domain imports további architekturális problémákat okoznak
- 5 SQL injection problémák a city_repository_queries.py fájlban

## §10 EVIDENCE GAPS

1. **CI/CD pipeline:** Nincs nyilvánvaló GitHub Actions konfig, csak local quality gate script
   - **Miért:** Nincs `.github/workflows/` könyvtár
   - **Hatása:** Nem tudom ellenőrizni, hogy a CI/CD pipeline működik-e

2. **Import-linter:** A `.importlinter` fájl létezik, de a konfig nem illeszkedik a valós struktúrához
   - **Miért:** A `.importlinter` fájl nem tartalmazza a valós rétegeket (domain/application/infrastructure/presentation)
   - **Hatása:** Nem tudom ellenőrizni az import-linter eredményét
   - **Futtatott parancs:** `lint-imports`
   - **Eredmény:** "Missing layer in container 'src': module src.adapters does not exist."

3. **Complexity metrics:** Radon complexity analysis eredmény
   - **Futtatott parancs:** `radon cc src/ --total-average`
   - **Eredmény:** Average complexity: A (2.83105981112277)
   - **Complexity C:** 1044 block (36.5%)
   - **Complexity D:** 365 block (12.8%)
   - **Hatása:** A complexity jó, de 14.3% of blocks have C/D complexity

4. **Mutation testing:** Nincs mutmut eredmény
   - **Miért:** Nincs futtatva mutmut
   - **Hatása:** Nem tudom ellenőrizni a mutation coverage-t

5. **Dead code detection:** Vulture eredmény
   - **Futtatott parancs:** `vulture src/ --min-confidence 80`
   - **Eredmény:** 19 dead code issue
   - **Főbb problémák:** Unused variables, unreachable code
   - **Hatása:** 19 dead code issue, de minőségi problémák, nem kritikusak

6. **Security scanning:** Bandit eredmény
   - **Futtatott parancs:** `bandit -r src/ -f txt -o bandit_results.txt`
   - **Eredmény:** 19 security issue
   - **Főbb problémák:**
     - 5 Medium severity: SQL injection vectors (B608)
     - 14 Low severity: Try-except-pass (B110), random usage (B311)
   - **Hatása:** 5 SQL injection problémák a city_repository_queries.py fájlban

7. **Trend analysis:** Nincs wily eredmény
   - **Miért:** Nincs futtatva wily
   - **Hatása:** Nem tudom ellenőrizni a historical trends-t

8. **Deep nesting analysis:** Radon complexity analysis eredmény
   - **Futtatott parancs:** `radon cc src/ --total-average`
   - **Eredmény:** Average complexity: A (2.83105981112277)
   - **Hatása:** A nesting depth jó, de 14.3% of blocks have C/D complexity

9. **Long function analysis:** Radon complexity analysis eredmény
   - **Futtatott parancs:** `radon cc src/ --total-average`
   - **Eredmény:** Average complexity: A (2.83105981112277)
   - **Hatása:** A function length jó, de 14.3% of blocks have C/D complexity

10. **Circular imports:** Nincs részletes circular import analysis
    - **Miért:** Nincs futtatva import-linter
    - **Hatása:** Nem tudom ellenőrizni, hogy van-e circular imports

**Megjegyzés:** Az evidence gaps jelentős hatással vannak az audit eredményére. A radon, vulture és bandit eredmények további problémákat mutattak ki, de a fő problémák (low coverage, ruff/mypy errors, Clean Architecture violations) megmaradnak.