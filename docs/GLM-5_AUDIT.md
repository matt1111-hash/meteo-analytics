# PROJECT AUDIT REPORT
**Model:** GLM-5 | **Date:** 2026-03-07 | **Prompt:** v4.2

## §1 EXECUTIVE SUMMARY

A meteo-analytics projekt egy időjárás-elemző platform Clean Architecture mintát követve, PySide6 GUI-val. A domain réteg tisztán implementált, de az application réteg több Clean Architecture szabálysértést tartalmaz (infrastructure importok). A teszt lefedettség kritikusan alacsony (18.32%), ami a legnagyobb kockázat. A kód minőség megfelelő (91.8% type hint coverage, ruff clean), de több god class található a presentation rétegben.

**Risk:** 🔴 | **Confidence:** HIGH

---

## §2 PROJECT STRUCTURE

| Metrika | src/ | Teljes repo |
|---------|------|-------------|
| Python fájlok | 515 | 13790 |
| LOC | 64083 | 4979442 |
| Teszt fájlok | — | 82 |

**Stack:** Python 3.10+, PySide6 (Qt GUI), SQLite, Open-Meteo API, Clean Architecture

**Architektúra minta:** Clean Architecture (domain/application/infrastructure/presentation)

**Gyökérszintű könyvtárak (említés):**
- `data/` - adatbázis fájlok
- `frontend/` - frontend komponensek
- `scripts/` - segédszkriptek
- `utils/` - segédprogramok

---

## §3 CLEAN ARCHITECTURE COMPLIANCE

**Verdict:** ⚠️ Részleges megfelelés

### Layer struktúra:
| Layer | Állapot | Megjegyzés |
|-------|---------|------------|
| domain | ✅ | Tiszt, nincs külső függőség |
| application | ❌ | Importol infrastructure-ből |
| infrastructure | ✅ | Helyes függőségi irány |
| presentation | ✅ | Helyes függőségi irány |

### Violations:

**Application → Infrastructure (❌ TILTOTT):**
- `src/application/use_cases/calculate_trend.py:16` — `from src.infrastructure.container import get_weather_client_port`
- `src/application/use_cases/calculate_trend.py:92` — `from src.infrastructure.container import get_city_manager_port`
- `src/application/services/port_provider.py:17` — `from src.infrastructure.container import (...)`

**TYPE_CHECKING importok domain rétegben (❌ VIOLATION — compile-time coupling):**
- `src/domain/entities/analysis_factories.py:6-7` — `if TYPE_CHECKING: from src.domain.entities.universal_query import UniversalQuery`
- `src/domain/entities/location.py:6-7` — `if TYPE_CHECKING: from src.domain.value_objects.city_info import CityInfo`

**Import-linter státusz:**
```
Parancs: lint-imports
Eredmény: "Missing layer in container 'src': module src.adapters does not exist."
```
A `.importlinter` konfiguráció `adapters` réteget vár, ami nem létezik — konfigurációs hiba.

---

## §4 CODE QUALITY

### God Classes (>250 LOC a prompt threshold szerint):

| Fájl | LOC | Severity |
|------|-----|----------|
| `src/presentation/gui/windows/main_window.py` | 483 | 🚨 CRITICAL |
| `src/presentation/gui/controller/app_controller.py` | 419 | 🚨 CRITICAL |
| `src/presentation/gui/analytics/analytics_tabs.py` | 411 | 🚨 CRITICAL |
| `src/presentation/gui/charts/comparison_chart.py` | 380 | 🔴 HIGH |
| `src/presentation/gui/results_panel/extreme/category_calculators.py` | 373 | 🔴 HIGH |
| `src/analytics/multi_city_engine_core.py` | 372 | 🔴 HIGH |
| `src/domain/ports/__init__.py` | 361 | 🔴 HIGH |
| `src/api/routes/wind_rose.py` | 361 | 🔴 HIGH |
| `src/presentation/gui/results_panel/extreme_events_tab.py` | 360 | 🔴 HIGH |
| `src/presentation/gui/analytics/analytics_view/core.py` | 357 | 🔴 HIGH |
| `src/presentation/gui/results_panel/utils/dataframe_extractor.py` | 351 | 🔴 HIGH |
| `src/presentation/gui/weather_data_bridge/core.py` | 334 | 🔴 HIGH |
| `src/presentation/gui/charts/precipitation_chart/tooltip.py` | 330 | 🔴 HIGH |
| `src/presentation/gui/charts/temperature_chart/tooltip_handler.py` | 324 | 🔴 HIGH |
| `src/presentation/gui/theme_manager/core.py` | 318 | ⚠️ WARN |
| `src/presentation/gui/utils/theme_helpers.py` | 317 | ⚠️ WARN |

### Type Hint Coverage:
```
Parancs: AST elemzés src/ könyvtáron
Eredmény: 2125/2316 függvény típusozott (91.8%)
```

### Mypy eredmény:
```
Parancs: python -m mypy src/ --ignore-missing-imports
Eredmény: 100+ attr-defined hiba a mixin osztályokban
Példák:
- src/presentation/gui/map_view/integration.py:65: "MapViewIntegrationMixin" has no attribute "focus_on_county"
- src/presentation/gui/control_panel/mixins/public_api.py:23: "PublicAPIMixin" has no attribute "analysis_type_widget"
```

### Ruff eredmény:
```
Parancs: python -m ruff check src/
Eredmény: All checks passed!
```

---

## §5 TEST ANALYSIS

### Futtatott parancs:
```bash
python -m pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q
```

### Eredmény:
```
1495 passed in 32.46s
TOTAL coverage: 18.32% (line), branch coverage elérhető
```

### Coverage kategóriák:
| Kategória | Szám |
|-----------|------|
| 🚨 CRITICAL (<70%) | Teljes projekt: 18.32% |
| ⚠️ WARN (70-84%) | 0 fájl |
| ✅ OK (≥95%) | 38 fájl (teljes coverage) |

### <70% coverage fájlok (kivonat):
- `src/presentation/gui/windows/main_window.py` — 0%
- `src/presentation/gui/controller/app_controller.py` — 0%
- `src/presentation/gui/analytics/analytics_tabs.py` — 0%
- `src/presentation/gui/results_panel/extreme_events_tab.py` — 0%
- `src/api/routes/wind_rose.py` — 0%

### Untested critical paths (risk rangsor):
1. 🔴 **CRITICAL:** `main_window.py` — GUI fő belépési pont, 0% coverage
2. 🔴 **CRITICAL:** `app_controller.py` — Alkalmazás vezérlő, 0% coverage
3. 🔴 **HIGH:** `multi_city_engine_core.py` — Üzleti logika motor, 0% coverage
4. 🔴 **HIGH:** `wind_rose.py` API endpoint — REST endpoint, 0% coverage

### No-assertion tesztek:
- `tests/test_smoke.py` — `def test_import_baseline():` nincs assert

### Source-to-test arány:
```
src/ Python fájlok: 515
tests/ Python fájlok: 82
Arány: 6.3:1 (src:test)
```

---

## §6 SECURITY FINDINGS

### .env git-tracking ellenőrzés:
```
Parancs: git check-ignore -v .env
Eredmény: .gitignore:44:.env → HELYESEN IGNORE-OLVA
Parancs: git log --oneline -n 5 -- .env
Eredmény: (üres) → SOHA NEM VOLT COMMITOLVA
```
**Verdict:** ✅ OK — A `.env` nincs verziókövetésben.

### .env tartalom:
```
OPENMETEO_API_KEY=cdd1997ffb98c0273066efa5d2d257d1
METEOSTAT_API_KEY=9b5e65efd7msh676934679d7ec95p11bf9cjsndcb3249f47d6
METEOSOURCE_API_KEY=5x9f7qt5mh083jyo1td0lf15idik9i8zohlxzr95
```
⚠️ **MEGJEGYZÉS:** Valós API kulcsok vannak a fájlban, de NEM vannak git-tracked.

### Hardcoded secrets:
```
Parancs: grep -rn "(password|secret|api_key|apikey|token)\s*=\s*[\"'][^\"']+[\"']" src/
Eredmény: Nincs találat
```

### SQL injection:
```
Parancs: grep -rn "\.execute\(.*format\(|\.execute\(.*%|\.execute\(.*\+|\.execute\(f\"" src/
Eredmény: Nincs találat
```

### Unsafe kód (eval/exec/os.system):
```
Parancs: grep -rn "eval\(|exec\(|os\.system\(|subprocess\.call\(" src/
Eredmény: Nincs találat (csak GUI exec() hívások Qt-hoz)
```

### API authentication:
- Open-Meteo API: Public endpoint (ingyenes, auth nélkül)
- Meteostat/Meteosource: API kulcs szükséges, .env-ből olvasva

---

## §7 TOOLING & CI/CD

### Ruff:
```
Parancs: python -m ruff check src/
Eredmény: All checks passed!
Konfiguráció: ruff.toml, pyproject.toml
```

### Mypy:
```
Parancs: python -m mypy src/ --ignore-missing-imports
Eredmény: 100+ hiba (főleg attr-defined mixin problémák)
Konfiguráció: mypy.ini
```

### Pre-commit:
```
Fájl: .pre-commit-config.yaml
Hookok: trailing-whitespace, end-of-file-fixer, ruff, mypy, import-linter, pytest, detect-secrets
```

### Pytest:
```
Konfiguráció: pyproject.toml
Parancs futtatva: ✅
```

### GitHub Actions:
```
Könyvtár: .github/ — NEM LÉTEZIK
Verdict: ❌ Nincs CI/CD pipeline konfigurálva
```

---

## §8 POSITIVE FINDINGS

1. **Domain réteg tisztasága:**
   - `src/domain/entities/universal_query.py:1-215` — Tiszta dataclass implementáció, teljes type hint, validáció
   - `src/domain/entities/weather.py:1-169` — Domain entity minta példa, nincs külső függőség

2. **Type hint coverage:**
   - 91.8% type hint coverage a src/ könyvtárban — kiemelkedő

3. **Ruff clean:**
   - Minden ruff ellenőrzés átmegy — nincs lint error

4. **Security:**
   - .env helyesen ignore-olva, soha nem volt commitolva
   - Nincs hardcoded secret a kódban
   - Nincs SQL injection vagy unsafe kód

5. **Pre-commit hooks:**
   - `.pre-commit-config.yaml:1-96` — Átfogó hook konfiguráció (ruff, mypy, import-linter, detect-secrets)

6. **AGENTS.md dokumentáció:**
   - `AGENTS.md:1-207` — Részletes fejlesztői guidelines, Clean Architecture szabályok

---

## §9 RISK MATRIX

| Kategória | Értékelés | Indoklás |
|-----------|-----------|----------|
| Architecture | 🟡 WARN | Application layer importál infrastructure-ből; TYPE_CHECKING coupling domain-ben; import-linter konfig hibás |
| Code Quality | 🟡 WARN | 16 god class (>250 LOC); mypy hibák; de 91.8% type hint coverage és ruff clean |
| Tests | 🚨 CRITICAL | 18.32% coverage — messze a 85% cél alatt; kritikus komponensek 0% coverage |
| Security | 🟢 OK | .env helyesen kezelve; nincs hardcoded secret; nincs SQL injection |
| Maintainability | 🟡 WARN | God classes nehezítik a karbantartást; de jó dokumentáció (AGENTS.md) és tooling |

---

## §10 EVIDENCE GAPS

1. **Cyclomatic complexity:** Nem futtattam radon-t vagy hasonló eszközt a komplexitás mérésére. A mypy attr-defined hibák és god class-ok alapján feltételezhető magas komplexitás, de nincs pontos mérés.

2. **Branch coverage részletek:** A pytest --cov-branch futott, de a részletes branch coverage report nem lett teljesen kigyűjtve fájl szinten.

3. **Nesting depth:** Nem végeztem automatizált mélység elemzést. A god class-okban valószínűleg mélyebb nesting van.

4. **CI/CD pipeline:** A `.github/` könyvtár hiánya miatt nincs GitHub Actions, de nem ellenőriztem más CI rendszereket (GitLab CI, Jenkins, stb.).

5. **Adapters layer:** Az import-linter hiányolja az adapters réteget — nem tisztázott hogy ez tervezett vagy hiányzó komponens.

---

**Audit befejezve.**
