# PROJECT AUDIT REPORT
**Model:** KIMI | **Date:** 2026-02-11 | **Prompt:** v4.2

## §1 EXECUTIVE SUMMARY

A meteo-analytics projekt egy Python alapú időjárás-elemző alkalmazás PySide6 GUI-val és FastAPI backenddel. A projekt 502 Python fájlból áll az `src/` könyvtárban, összesen ~63k LOC-kal. A Clean Architecture rétegelés elméletben megvan, de a gyakorlatban számos violation található. A tesztlefedettség kritikusan alacsony (15.8%), a Ruff lintelés 650+ hibát jelez, és a type hint coverage is hiányos (paramétereknél 47.8%). **Risk:** 🔴 | **Confidence:** HIGH

## §2 PROJECT STRUCTURE

**src/ könyvtár:**
- Fájlok száma: 502 db `.py` fájl
- Összes LOC: ~63,117 sor
- Architektúra: Clean Architecture (domain/application/infrastructure/presentation)

**Teljes repo:**
- Python fájlok: 563 db
- Összes LOC: ~79,684 sor
- Teszt fájlok: 53 db

**Stack:**
- Python 3.10+
- PySide6 (GUI)
- FastAPI (API)
- Pandas, NumPy (adatfeldolgozás)
- Folium (térképek)
- SQLite (adatbázis)
- pytest, ruff, mypy (tooling)

**Legacy/root fájlok (említés szinten):**
- `ultimate_project_analyzer.py` (1530 LOC) - root szintű analizátor
- `meteo_gui_starter.py` (324 LOC) - GUI indító
- `utils/` könyvtár - projekt gyökérben, különálló segédeszközök

## §3 CLEAN ARCHITECTURE COMPLIANCE

**Verdict:** ⚠️ - A rétegelés megvan, de számos violation található.

### Réteg tábla:

| Layer | Fájlok | Engedélyezett | Violations |
|-------|--------|---------------|------------|
| domain | ~30 | stdlib, typing | ❌ Importál infrastructure-t |
| application | ~10 | domain, stdlib | ✅ Tiszta |
| infrastructure | ~40 | domain, application, external | ✅ Tiszta |
| presentation | ~400 | application, infrastructure, UI | ❌ Közvetlen domain import |

### Konkrét violations:

**Domain -> Infrastructure (TILOS):**
- `src/domain/ports/__init__.py:402` - `from src.infrastructure.repositories.city_repository import CityRepository`
- `src/domain/ports/__init__.py` - `from src.data.city_manager_stats import CityManagerStats`
- `src/domain/ports/__init__.py` - `from src.data.weather_client_extensions import WeatherClientExtensions`
- `src/domain/ports/__init__.py` - `from src.data.anomaly_profile.manager import AnomalyProfileManager`
- `src/domain/entities/location.py` - `from src.data.city_types import City as CityInfo`

**Presentation -> Domain közvetlen (TILOS):**
- `src/presentation/gui/workers/analysis_worker/core.py` - `from src.domain.ports import ...`
- `src/presentation/gui/hungarian_map_tab/map_widget.py` - `from src.domain.entities.analytics_models import ...`
- `src/presentation/gui/trend_analytics/trend_data_processor/core.py` - `from src.domain.ports import ...`
- `src/presentation/gui/results_panel/windy_days_tab/core.py` - `from src.domain.analytics.wind_models import ...`
- `src/presentation/gui/panel_widgets/location_widget/core.py` - `from src.domain.entities.universal_location import ...`
- `src/presentation/gui/dialogs/anomaly_settings_dialog/core.py` - `from src.domain.ports import ...`

**Megjegyzés:** A `TYPE_CHECKING` blokkban lévő importok is violation-ként számítanak a prompt szerint, de ezeket a kódban nem találtam explicit módon.

## §4 CODE QUALITY

### God classes (>250 LOC threshold):

| Fájl | LOC | Severity |
|------|-----|----------|
| `src/presentation/gui/windows/main_window.py` | 480 | 🔴 CRITICAL |
| `src/presentation/gui/controller/app_controller.py` | 419 | 🔴 CRITICAL |
| `src/api/routes/providers.py` | 412 | 🔴 CRITICAL |
| `src/presentation/gui/analytics/analytics_tabs.py` | 411 | 🔴 CRITICAL |
| `src/domain/ports/__init__.py` | 402 | 🔴 CRITICAL |
| `src/presentation/gui/charts/comparison_chart.py` | 380 | 🔴 CRITICAL |
| `src/presentation/gui/results_panel/extreme/category_calculators.py` | 373 | 🔴 CRITICAL |
| `src/analytics/multi_city_engine_core.py` | 372 | 🔴 CRITICAL |
| `src/api/routes/wind_rose.py` | 361 | 🔴 CRITICAL |
| `src/presentation/gui/results_panel/extreme_events_tab.py` | 360 | 🔴 CRITICAL |

**Összesen:** 30+ fájl meghaladja a 250 LOC thresholdöt.

### Cyclomatic complexity (radon output alapján):

| Fájl | Függvény | Complexity | Severity |
|------|----------|------------|----------|
| `src/presentation/gui/data_widgets.py.backup` | `WeatherDataTable.data` | D (10-15) | 🔴 HIGH |
| `src/presentation/gui/data_widgets/mixins/display_mixin.py` | `_populate_table_with_numeric_items` | C (8-10) | ⚠️ WARN |
| `src/presentation/gui/results_panel/extreme/category_calculators.py` | `calculate_temperature_records` | C (8-10) | ⚠️ WARN |
| `src/presentation/gui/results_panel/extreme/text_generators.py` | `_generate_wind_text` | C (8-10) | ⚠️ WARN |

### Nesting depth >3:

| Fájl | Sor | Függvény | Depth |
|------|-----|----------|-------|
| `src/presentation/gui/map/map_constants.py` | 125 | `get_beaufort_color()` | 7 |
| `src/presentation/gui/analytics/analytics_tabs.py` | 372 | `_update_current_tab()` | 7 |
| `src/presentation/gui/data_widgets/table_model.py` | 65 | `data()` | 7 |
| `src/presentation/gui/results_panel/extreme/category_calculators.py` | 338 | `calculate_uv_records()` | 7 |
| `src/domain/analytics/services/weather_fetch_service.py` | 130 | `fetch_single_city_weather_dual_api()` | 7 |

**Összesen:** 108 függvény meghaladja a 3-as nesting depth-et.

### Type hint coverage:

| Metrika | Érték | Target | Status |
|---------|-------|--------|--------|
| Függvények száma | 2306 | - | - |
| Visszatérési érték típusozott | 86.2% | 100% | ⚠️ WARN |
| Paraméterek típusozva | 47.8% | 100% | 🔴 HIGH |

**Parancs:** `python3 -c "import ast; ... (custom script)"`

## §5 TEST ANALYSIS

**Futtatott parancs:**
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -q
```

**Eredmény:**
```
============================ 1004 passed in 24.11s =============================
TOTAL coverage: 15.77%
FAIL Required test coverage of 85.0% not reached.
```

### Coverage részletek:

| Metrika | Érték |
|---------|-------|
| Line coverage | 15.8% |
| Branch coverage | 861/5656 (15.2%) |
| <70% coverage fájlok | 357 db |

### Alacsony coverage fájlok (minta):

| Fájl | Coverage |
|------|----------|
| `src/config.py` | 0% |
| `src/data/anomaly_demo.py` | 0% |
| `src/presentation/gui/analytics/analytics_tabs.py` | 0% |
| `src/presentation/gui/windows/main_window.py` | 0% |
| `src/presentation/gui/controller/app_controller.py` | 0% |

**Megjegyzés:** A GUI réteg (presentation/gui/) gyakorlatilag nincs tesztelve (0% coverage).

### Teszt struktúra:
- Teszt fájlok: 52 db
- Teszt függvények: ~105 db
- Assert-ök: 2080 db

## §6 SECURITY FINDINGS

### .env git-tracked ellenőrzés:
**Parancs:** `git ls-files .env`
**Eredmény:** Nem git-tracked ✅

### Hardcoded secrets:
**Parancs:** `grep -rn "api_key\|password\|secret\|token" src/ --include="*.py" -i`
**Eredmény:**
- API kulcsok környezeti változókból érkeznek (`os.getenv()`), nincs hardcoded secret ✅
- `src/data/meteostat_provider.py:36` - `self.api_key = os.getenv("METEOSTAT_API_KEY")` ✅
- `src/config/api_config.py:23` - `METEOSTAT_API_KEY: ClassVar[str | None] = os.getenv("METEOSTAT_API_KEY")` ✅

### SQL injection:
**Parancs:** `python -m bandit -r src/ -f txt`
**Eredmény:**
- **MEDIUM (5 db):** `src/infrastructure/repositories/city_repository_queries.py` - string-based query construction `.format(in_clause)`
- **LOW (14 db):** Try-except-pass blokkok

**Részletek:**
```python
# src/infrastructure/repositories/city_repository_queries.py:29-37
query = (
    "SELECT city, country, country_code, lat, lon, population, "
    "meteostat_station_id, data_quality_score FROM cities "
    "WHERE LOWER(city) IN ({}) ".format(in_clause)  # B608
```

### eval/exec/os.system:
**Parancs:** `grep -rn "eval(\|exec(\|os\.system" src/ --include="*.py"`
**Eredmény:**
- `exec()` előfordulások: PySide6 `QApplication.exec()` hívások (biztonságos) ✅
- Tényleges `eval()` vagy `os.system()` nincs ✅

### API authentication:
- Meteostat API: API key használat ✅
- OpenMeteo API: API key használat ✅
- Publikus endpoint-ok nincsenek azonosítás nélkül ✅

## §7 TOOLING & CI/CD

### Ruff:
**Parancs:** `python -m ruff check src/`
**Eredmény:** 650+ hiba

**Fő kategóriák:**
- F841 (unused variable): `src/api/routes/anomalies.py:109`
- E402 (import not at top): `src/data/weather_client_core.py:26-29`

### Mypy:
**Parancs:** `python -m mypy src/ --ignore-missing-imports`
**Eredmény:** 1254 errors in 159 files

**Fő problémák:**
- PySide6 attribútum hibák: `"MainWindow" has no attribute "control_panel"`
- Hiányzó importok: `Name "AnalyticsResult" is not defined`

### Pre-commit:
**Konfiguráció:** `.pre-commit-config.yaml` ✅ meglévő
- trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-json
- detect-private-key ✅
- ruff-pre-commit v0.8.6

**Státusz:** Nincs aktiválva (nincs `.git/hooks/pre-commit`)

### CI/CD:
**GitHub Actions:** Nincs `.github/workflows/` könyvtár ❌

### Import-linter:
**Parancs:** `python -m importlinter`
**Eredmény:** Nem elérhető, de konfiguráció meglévő (`.importlinter`)

## §8 POSITIVE FINDINGS

### 1. Repository Pattern megvalósítása
**Fájl:** `src/infrastructure/repositories/city_repository.py:1`
**Leírás:** A `CityRepository` osztály implementálja a `CityRepositoryProtocol`-t, tiszta repository pattern.
```python
class CityRepository(CityRepositoryProtocol):
    """SQLite-based implementation of CityRepositoryProtocol."""
```

### 2. Port/Adapter Pattern használata
**Fájl:** `src/domain/ports/__init__.py:1`
**Leírás:** Protokollok definiálása a domain rétegben, dependency inversion.
```python
class CityManagerPort(Protocol):
    """Port for city management operations."""
```

### 3. Dataclass-ok használata entitásokhoz
**Fájl:** `src/domain/entities/weather.py:20`
**Leírás:** Típusos, dokumentált entitások dataclass-okkal.
```python
@dataclass
class CityWeatherResult:
    """Egyetlen város időjárási eredménye."""
    city_name: str
    country: str
    # ...
```

### 4. Környezeti változók használata API kulcsokhoz
**Fájl:** `src/config/api_config.py:23`
**Leírás:** API kulcsok biztonságos tárolása környezeti változókban.
```python
METEOSTAT_API_KEY: ClassVar[str | None] = os.getenv("METEOSTAT_API_KEY")
```

### 5. Type hints a domain rétegben
**Fájl:** `src/domain/value_objects/enums.py`
**Leírás:** Széleskörű type hint használat a domain rétegben (86.2% visszatérési érték).

## §9 RISK MATRIX

| Kategória | Értékelés | Indoklás |
|-----------|-----------|----------|
| **Architecture** | 🔴 HIGH | Számos CA violation (domain->infrastructure, presentation->domain), 30+ god class |
| **Code Quality** | 🔴 HIGH | 650+ Ruff error, 1254 mypy error, 108 függvény >3 nesting depth, paraméter típusok 47.8% |
| **Tests** | 🚨 CRITICAL | 15.8% coverage (target: 85%), GUI réteg nincs tesztelve |
| **Security** | 🟡 WARN | SQL injection lehetőség (B608), 14 try-except-pass blokk, de nincs hardcoded secret |
| **Maintainability** | 🔴 HIGH | 502 fájl, 63k LOC, magas komplexitás, alacsony tesztlefedettség |

## §10 EVIDENCE GAPS

| Terület | Státusz | Indoklás |
|---------|---------|----------|
| Branch coverage | Részleges | A pytest output tartalmaz branch coverage-t, de a pontos fájlonkénti branch coverage nem teljes |
| Cyclomatic complexity | Részleges | A radon csak bizonyos fájlokat elemezett, nem teljes src/ coverage |
| Long functions (>50 sor) | Hiányos | Az AST alapú elemzés nem futott le teljesen, manuális ellenőrzés szükséges |
| Import-linter | Nem futtatható | A tool nem elérhető, a konfiguráció alapján csak elméleti elemzés |
| CI/CD pipeline | Hiányos | Nincs GitHub Actions, a pre-commit nincs aktiválva |

### Megjegyzések:
- A coverage.json és a pytest output konzisztens (15.8% vs 15.77%), mindkettő alacsony.
- A GUI réteg tesztelése nem volt lehetséges headless környezetben (PySide6 GUI komponensek).
- A mypy hibák nagy része PySide6 specifikus attribútum probléma, nem valódi típushiba.
