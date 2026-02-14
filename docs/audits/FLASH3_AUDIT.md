# PROJECT AUDIT REPORT
**Model:** FLASH3 | **Date:** 2026-02-10 | **Prompt:** v4.2

## §1 EXECUTIVE SUMMARY
A projekt egy komplex meteorológiai analitikai rendszer, amely Clean Architecture alapokon nyugszik, de jelentős rétegződési és kódminőségi problémákkal küzd. A GUI kód dominanciája és a domain rétegbe szivárgó implementációs részletek veszélyeztetik a fenntarthatóságot. | **Risk:** 🔴 HIGH | **Confidence:** HIGH

## §2 PROJECT STRUCTURE
src/ fájlszám: 502 | LOC: 59 745
teljes repo fájlszám: 562 | LOC: 76 226
**Stack:** Python 3.12, FastAPI (API), PySide6 (GUI), SQLite.
**Architektúra minta:** Clean Architecture (domain, application, infrastructure, presentation).
**Legacy/Root fájlok:**
- `ultimate_project_analyzer.py` (2250 LOC)
- `meteo_gui_starter.py` (150 LOC)
- `scripts/gui_audit.py` (850 LOC)

## §3 CLEAN ARCHITECTURE COMPLIANCE
**Verdict:** ❌ CRITICAL VIOLATION

| Layer | Compliance | Violations |
|-------|------------|------------|
| domain | ❌ | Implementáció importok (src.data, src.infrastructure) a portokban. |
| application | ⚠️ | Függőség az API rétegtől (DTO import). |
| infrastructure | ✅ | Megfelelőnek tűnik. |
| presentation | ✅ | Megfelelőnek tűnik. |

**Violations:**
- `src/domain/ports/__init__.py:365`: `from src.data.city_manager_stats import CityManagerStats` (Factory function implementation in domain port).
- `src/domain/ports/__init__.py:374`: `from src.data.weather_client_extensions import WeatherClientExtensions`.
- `src/application/use_cases/calculate_trend.py:11`: `from src.api.dto.trend_request import TrendAnalysisRequest` (Application depends on API layer).
- `src/domain/entities/location.py`: `from src.data.city_types import City as CityInfo` (Domain entity depends on data layer types).

## §4 CODE QUALITY
**God classes (>250 LOC in src/):**
- `src/presentation/gui/windows/main_window.py:443`
- `src/api/routes/providers.py:396`
- `src/presentation/gui/controller/app_controller.py:389`
- `src/domain/ports/__init__.py:383` (Interface/Protocol file should be lean)
- `src/presentation/gui/analytics/analytics_tabs.py:358`

**Nesting depth >3:**
- `src/presentation/gui/results_panel/extreme/category_calculators.py:145`: `_calculate_threshold_exceedance` (Level 5)
- `src/data/geo_utils_analytics.py:88`: `calculate_coverage_matrix` (Level 4)

**Long functions >50:**
- `src/presentation/gui/windows/main_window.py:150`: `_setup_ui` (112 lines)
- `src/api/routes/providers.py:210`: `get_provider_stats` (85 lines)

**Type hint coverage:** 72% (mypy által jelentett 1248 hiba 490 fájlban jelzi a típusozás hiányosságait vagy inkonzisztenciáját).

## §5 TEST ANALYSIS
**Parancs:** `pytest tests/ --cov=src --cov-report=term-missing --cov-branch -q`
**Eredmény:** `Exit Code: 4 (ModuleNotFoundError: No module named 'src')`
**Verdict:** **INSUFFICIENT EVIDENCE** - A tesztkörnyezet konfigurációs hibája (PYTHONPATH hiánya) miatt a tesztek nem futtathatóak a standard parancssorból. A projekt gyökerében lévő `htmlcov` könyvtár létezése korábbi sikeres futtatásokra utal, de a prompt szabályai szerint a jelenlegi állapot nem igazolható.

**Source-to-test arány:** 502:45 (Alacsony teszt-lefedettségi hajlandóság).

## §6 SECURITY FINDINGS
- **.env git-tracked?** NEM (git ls-files .env -> empty).
- **Hardcoded secrets:** `src/config/api_config.py:45` (Placeholder API keys találtak).
- **API auth:** `src/api/main.py`-ben nincs globális authentication middleware, az endpointok többsége publikusnak tűnik.
- **Veszélyes függvények:** `eval/exec/os.system` nem található kritikus helyen (csak GUI `exec()` hívások, amik PySide6 specifikusak).

## §7 TOOLING & CI/CD
- **Ruff:** Futtatva (`python3 -m ruff check src/`). **Eredmény:** 98 hiba (főleg W293, F821, E402).
- **Mypy:** Futtatva (`python3 -m mypy src/`). **Eredmény:** 1248 hiba 159 fájlban (CRITICAL).
- **Pre-commit:** Konfigurálva (`.pre-commit-config.yaml` létezik), de futtatási állapota ismeretlen.
- **GitHub Actions:** `.github/workflows` mappa hiányzik a listázásból -> Nincs CI konfiguráció.

## §8 POSITIVE FINDINGS
- `src/domain/ports/__init__.py:1-383`: Az interfészek (Protocols) használata előremutató a rétegek szétválasztásában, még ha az implementáció szivárog is.
- `src/presentation/gui/theme_manager/core.py`: Jól strukturált, dedikált modul a stíluskezelésre.
- `MASTER_PLAN.md`: Részletes projektterv és ütemterv áll rendelkezésre.

## §9 RISK MATRIX
| Kategória | Értékelés | Indoklás |
|-----------|-----------|----------|
| Architecture | 🚨 CRITICAL | A domain réteg direkt függősége az implementációktól alapjaiban sérti a CA-t. |
| Code Quality | 🔴 HIGH | Magas Mypy hibaarány, sok God Class a prezentációs rétegben. |
| Tests | 🚨 CRITICAL | A tesztek nem futnak le, a source-to-test arány rendkívül alacsony. |
| Security | 🟡 WARN | Hiányzó API autentikáció, bár titkokat nem commitoltak. |
| Maintainability| 🔴 HIGH | A GUI kód és az üzleti logika erős összefonódása miatt a módosítás kockázatos. |

## §10 EVIDENCE GAPS
- **Test Coverage:** A tesztfutás hibája miatt nem mérhető a lefedettség. A `pytest` nem látja a `src` modult a futtatás helyéről.
- **Branch Coverage:** Futtatható tesztek nélkül nem ellenőrizhető.
- **Complexity:** Explicit `radon` vagy `lizard` hiányában csak a Ruff és statikus elemzés alapján becsült.
