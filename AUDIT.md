# PROJECT AUDIT REPORT
**Model:** CODEX | **Date:** 2026-03-15 | **Project:** /home/tibor/PythonProjects/meteo-analytics
**Overall Risk:** 🟡 MEDIUM

---

## 1. EXECUTIVE SUMMARY

Ez egy nagy, többfelületű meteorológiai alkalmazás Python backenddel, FastAPI API-val, PySide6 GUI-val és külön React frontenddel. A tesztelési és tooling állapot erős, a teljes Python coverage 90.41%, a `ruff`, `mypy`, `pytest` és az import-linter futása zöld. A fő kockázatot nem a file-méret, hanem a komplexitás adja: a quality gate a complexity kapun elbukik, több `C` és több `D` szintű függvény található, főleg a `presentation/gui` és néhány domain service környékén.

## 2. PROJECT STRUCTURE

| Metrika | Érték |
|---------|-------|
| Python fájlok | 682 |
| TypeScript fájlok | 25 |
| Tesztfájlok | 188 |
| AGENTS.md | Van |
| Stack | Python 3.12 runtime / `requires-python >=3.10`, FastAPI, PySide6, React 19, TypeScript 4.9 |
| Architektúra | Clean Architecture + párhuzamos legacy/monolith csomagstruktúra |

## 3. CODE QUALITY

### Nagy fájlok (>300 LOC)
| Fájl | LOC | Severity |
|------|-----|----------|
| not present | 0 | ✅ OK |

Megjegyzés: a `src/` alatt a legnagyobb mért Python fájl 249 LOC volt, tehát a 300 soros határ alatt marad.

### Komplex függvények (CC > 8)
| Fájl | Függvény | CC | Severity |
|------|----------|----|----------|
| `src/presentation/gui/data_widgets/table_model.py:66` | `WeatherTableModel.data` | 29 | 🚨 CRITICAL |
| `src/domain/analytics/services/analytics_transform_service_part2.py:11` | `AnalyticsTransformServicePart2Mixin.process_weather_results` | 23 | 🚨 CRITICAL |
| `src/presentation/gui/analytics/analytics_statistics_part2.py:12` | `AnalyticsStatisticsPart2Mixin.calculate_records` | 21 | 🚨 CRITICAL |
| `src/presentation/gui/charts/comparison_chart_part2.py:11` | `_plot_multi_year_comparison` | 19 | 🔴 HIGH |
| `src/presentation/gui/cleanup_manager.py:106` | `CleanupManager._cleanup_all_workers` | 11 | 🔴 HIGH |

### Type hint lefedettség
**Becslés:** 81.6% (AST-alapú mérés alapján, `self/cls` kivételekkel, `src/` teljes állományon)

## 4. CLEAN ARCHITECTURE
**Verdict:** ⚠️ PARTIAL

| Réteg | Jelen | Tiszta | Problémák |
|-------|-------|--------|-----------|
| domain | ✅ | ✅ | A futtatott grep és import-linter alapján nincs bizonyított kifelé mutató tiltott import |
| application | ✅ | ✅ | Nem találtam bizonyított `presentation` importot |
| infrastructure | ✅ | ✅ | Import-linter PASS, további részletezéshez insufficient evidence |
| presentation | ✅ | ⚠️ | Nagyon nagy és komplex GUI felület, 520 Python fájl a `presentation` top-level alatt |

### Függőség-sértések
| Fájl | Sor | Sértés | Severity |
|------|-----|--------|----------|
| not present | - | A futtatott domain/application grep és az import-linter alapján bizonyított rétegsértés nem találtam | ✅ OK |

Megjegyzés: a rétegek jelen vannak és a formális architektúra-ellenőrzés átment, de a projektben párhuzamosan léteznek a `analytics`, `api`, `data`, `config` top-level csomagok is, ezért az összkép nem tisztán clean architecture.

## 5. TEST RESULTS

```text
=============================== warnings summary ===============================
venv/lib/python3.12/site-packages/_pytest/config/__init__.py:833
  PytestAssertRewriteWarning: Module already imported so cannot be rewritten

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================== 1582 passed, 2 warnings in 25.27s =======================
```

| Metrika | Érték | Cél | Státusz |
|---------|-------|-----|---------|
| Lefedettség | 90.41% | ≥85% | ✅ |

### Teszteletlen kritikus modulok
| Modul | Kockázat |
|-------|----------|
| `src/application/dto/location_dto.py` | 66% coverage, application boundary DTO regressziók rejtve maradhatnak |
| `src/application/use_cases/analyze_multi_city_part2.py` | 68% coverage, use-case elágazások részben fedettek |
| `src/domain/analytics/services/analytics_transform_service_part2.py` | 73% coverage és CRITICAL komplexitás egy helyen koncentrálódik |
| `src/domain/entities/analytics_models_part2.py` | 56% coverage, domain modellágak hiányos teszteléssel |
| `src/infrastructure/repositories/city_repository.py` | 74% coverage, repository hibák részben észrevétlenek maradhatnak |

## 6. SECURITY

| Találat | Fájl | Sor | Severity |
|---------|------|-----|----------|
| not present | - | - | ✅ A futtatott `bandit`, `eval/exec/os.system`, `pickle.load`, `yaml.load`, SQL-string keresések alapján nem találtam bizonyított magas kockázatú mintát |

**Hardcoded secrets:** Nem találtam  
**SQL injection:** Nem találtam  
**Unsafe deserialization:** Nem találtam

## 7. TOOLING

| Eszköz | Konfigurált | Fut | Problémák |
|--------|-------------|-----|-----------|
| Ruff | ✅ | ✅ | `All checks passed!` |
| Mypy | ✅ | ✅ | `Success: no issues found in 670 source files`; egy `annotation-unchecked` note megjelent `src/data/geo_utils_region.py:34` sorra |
| Pytest | ✅ | ✅ | 1582 teszt PASS, 1-2 warning |
| Pre-commit | ✅ | insufficient evidence | `.pre-commit-config.yaml` jelen van, futtatás nem történt |
| Quality Gate | ✅ | ✅ | FAIL: `Complexity too high!`; dead code warning nem blokkoló |

## 8. CRITICAL ISSUES 🚨

| # | Probléma | Helyszín | Hatás |
|---|----------|----------|-------|
| 1 | CRITICAL komplexitású megjelenítési logika | `src/presentation/gui/data_widgets/table_model.py:66` | Magas regressziós és karbantarthatósági kockázat a GUI adattábla viselkedésében |
| 2 | CRITICAL komplexitású domain transzformáció | `src/domain/analytics/services/analytics_transform_service_part2.py:11` | A domain feldolgozás egyetlen eljárásban túl sok ágat kezel |
| 3 | CRITICAL komplexitású rekordszámítás | `src/presentation/gui/analytics/analytics_statistics_part2.py:12` | A rekordképzés hibáinak izolálása és verifikálása nehéz |

## 9. WARNINGS 🔴

| # | Probléma | Helyszín | Severity |
|---|----------|----------|----------|
| 1 | A quality gate complexity kapun elbukik, sok `C` és több `D` szintű egységgel | főleg `src/presentation/gui/**` | 🔴 HIGH |
| 2 | Hardcoded localhost API URL-ok a frontendben | `frontend/src/config/apiConfig.ts:17`, `frontend/src/components/panels/AnomalyPanel.tsx:5` | 🔴 HIGH |
| 3 | A projektstruktúra nem egységesen clean, mert a clean rétegek mellett párhuzamos top-level csomagok is élnek | `src/analytics`, `src/api`, `src/data`, `src/config` | ⚠️ WARNING |
| 4 | Több aktív modul coverage-e 70% alatt van, miközben nem demo-only szerepű | pl. `src/domain/entities/analytics_models_part2.py`, `src/application/use_cases/analyze_multi_city_part2.py` | 🔴 LOW |
| 5 | A quality gate vulture szintjén dead code warning jelent meg | pl. `src/analytics/ports/analysis_ports.py`, `src/data/city_manager_stats.py` | ⚠️ WARNING |

## 10. STRENGTHS ✅

- ✅ A teljes Python tesztcsomag stabil: 1582 teszt PASS.
- ✅ A teljes coverage 90.41%, ami a lokális quality gate küszöb fölött van.
- ✅ A `ruff`, `mypy`, `bandit` és az import-linter futási eredménye alapvetően tiszta.

## 11. RISK MATRIX

| Kategória | Kockázat | Indoklás |
|-----------|----------|----------|
| Architektúra | 🟡 | A clean rétegek jelen vannak és ellenőrzésen átmennek, de a teljes csomagstruktúra vegyes |
| Kódminőség | 🔴 | File-méret rendben van, de a complexity gate bukik és több CRITICAL függvény van |
| Tesztlefedettség | 🟢 | 90.41% összcoverage, nagy tesztmennyiség |
| Biztonság | 🟢 | A futtatott biztonsági ellenőrzések alapján bizonyított magas kockázatú minta nem találtam |
| Karbantarthatóság | 🟡 | Erős tooling mellett nagyon nagy GUI-felület és sok komplex elágazás látszik |
