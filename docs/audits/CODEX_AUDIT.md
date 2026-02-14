# PROJECT AUDIT REPORT
**Model:** CODEX | **Date:** 2026-02-10 | **Prompt:** v4.2

## §1 EXECUTIVE SUMMARY
A `src/` fókuszú audit alapján a projektben jelentős Clean Architecture és kódminőségi eltérések vannak, különösen a `presentation` réteg mérete/komplexitása és a rétegfüggőségek miatt. A kötelező teljes `pytest tests/ --cov=src --cov-branch` futás timeouttal leállt, ezért coverage verdikt teljes bizonyossággal nem adható. **Risk:** 🔴 | **Confidence:** MEDIUM

## §2 PROJECT STRUCTURE
`src/` (scope: minden fájl): 635 fájl; Python fájlok: 502; Python LOC: 59,745.
Teljes repo (scope: auto-exclude után): 52,195 fájl; Python fájlok: 562; Python LOC: 76,226.
Stack (evidence alapján): Python + FastAPI + PySide6 + pandas/numpy/scipy/scikit-learn + pytest/ruff/mypy.
Architektúra minta: részben Clean Architecture jelleg (`domain/application/infrastructure/presentation`), de a függőségi szabályok sérülnek.

Parancs + scope + releváns kimenet:
- `find src -type f | wc -l` | scope: `src/` összes fájl | stdout: `635`
- `find src -type f -name '*.py' | wc -l` | scope: `src/` Python fájlok | stdout: `502`
- `find src -type f -name '*.py' -print0 | xargs -0 wc -l | tail -n 1` | scope: `src/` Python LOC | stdout: `59745 total`
- `find . ... -type f -print | wc -l` | scope: teljes repo (auto-exclude) | stdout: `52195`
- `find . ... -type f -name '*.py' -print | wc -l` | scope: teljes repo Python fájlok | stdout: `562`
- `find . ... -type f -name '*.py' -print0 | xargs -0 wc -l | tail -n 1` | scope: teljes repo Python LOC | stdout: `76226 total`
- `rg -n "from fastapi import|import fastapi" src` | scope: `src/` | stdout példa: `src/api/main.py:6:from fastapi import FastAPI`
- `rg -n "from PySide6|import PySide6" src` | scope: `src/` | stdout példa: `src/presentation/gui/map_view/core.py:19:from PySide6.QtCore import Signal`
- `rg -n "numpy|pandas|scipy|scikit|pytest|ruff|mypy" requirements.txt requirements-dev.txt` | scope: root config | stdout példa: `requirements.txt:58:pandas==2.3.1`

Gyökérszintű (legacy/mixed) fájlok említése, részletes analízis nélkül (fájlnév + LOC):
- `meteo_gui_starter.py` (324)
- `ultimate_project_analyzer.py` (1530)
- `quality_gate.sh` (488)
- `pyproject.toml` (176)
- `README.md` (129)
- `baseline_report.txt` (13396)
- `coverage.xml` (26003)
- `uvicorn_new.log` (19765)
- `sqlite3` (61453)
- `MASTER_PLAN.md` (215)

Root könyvtárak a promptban megadott listából:
- `plugins/`: not present
- `data_fetchers/`: not present
- `utils/`: exists
- `models/`: not present

## §3 CLEAN ARCHITECTURE COMPLIANCE
**Verdict:** ❌

Layer állapot (mért importok alapján):
- `domain`: sérül (`src/domain/ports/__init__.py:366` -> `src.infrastructure...`; több external import)
- `application`: közvetlen tiltott (`infrastructure/presentation`) importot a futtatott ellenőrzés nem talált
- `infrastructure`: tiltott `presentation` importot a futtatott ellenőrzés nem talált
- `presentation`: tömeges tiltott `domain` import (31 összesített violation jelentős része)

Főbb violations (`file:line`):
- `src/domain/ports/__init__.py:366` (`domain -> infrastructure`)
- `src/domain/entities/location.py:6` (`domain -> src.data...`)
- `src/presentation/gui/control_panel/core.py:37` (`presentation -> domain`)
- `src/presentation/gui/hungarian_map_tab/core.py:17` (`presentation -> domain`)
- `src/presentation/gui/panel_widgets/location_widget/core.py:13` (`presentation -> domain`)
- `src/presentation/gui/weather_data_bridge/core.py:6` (`presentation -> domain`)

TYPE_CHECKING import szabály:
- Futtatott ellenőrzésben tiltott `TYPE_CHECKING` import **not present** (0 találat).

Körkörös import:
- `src.domain.value_objects.enum_utils -> src.domain.value_objects.enums` (1 cikluscsoport).

`# noqa` megjegyzések:
- Tudatos suppresszió jelen van (pl. `src/presentation/gui/map/map_visualizer/core.py:35`), ez a prompt szabály szerint nem mentesít.

Parancs + scope + releváns kimenet:
- Egyedi AST ellenőrző script (layer rules) | scope: `src/` | stdout: `layer_violations=31`, `plugin_violations=0`
- Egyedi AST ellenőrző script (domain import policy) | scope: `src/domain/` | stdout: `domain_import_violations=14`
- Egyedi AST script (`TYPE_CHECKING`) | scope: `src/` | stdout: `type_checking_layer_violations=0`
- Egyedi AST graph script (circular) | scope: `src/` | stdout: `circular_groups=1`
- `rg -n "# noqa" src` | scope: `src/` | stdout példa: `src/presentation/gui/map/map_visualizer/core.py:35:    import folium  # noqa: F401`

## §4 CODE QUALITY
God class / túl nagy fájl (`>250 LOC`, prompt threshold): 40 fájl a `src/` alatt.
- CRITICAL példák: `src/presentation/gui/windows/main_window.py:1` (443 LOC), `src/api/routes/providers.py:1` (396 LOC), `src/presentation/gui/controller/app_controller.py:1` (389 LOC).

Cyclomatic complexity:
- `complexity >5`: 266 függvény.
- CRITICAL példa (`>15`): `src/api/routes/wind_rose.py:63` (`_process_wind_rose_data`, complexity 38).
- HIGH példák (`9-15`): `src/presentation/gui/workers/weather_data_worker/executor.py:27` (15), `src/domain/analytics/wind_analysis_service.py:20` (15).

Function length:
- `>50 sor`: 144 függvény.
- HIGH példák (`>80`): `src/presentation/gui/demos/map_tab_demo.py:25` (200), `src/presentation/gui/trend_analytics/trend_data_processor/calculator.py:11` (158), `src/api/routes/wind_rose.py:63` (131).

Nesting depth:
- `>3`: 98 függvény.
- HIGH példák (`>4`): `src/presentation/gui/results_panel/extreme/text_generators.py:120` (7), `src/presentation/gui/data_widgets/table_model.py:61` (7), `src/presentation/gui/map/map_constants.py:125` (7).

Type hint coverage:
- `1860/2306` teljesen típusozott függvény (`~80.7%`).

Duplicate logic:
- **insufficient evidence** (nem futott dedikált klón-detektor eszköz).

Parancs + scope + releváns kimenet:
- Egyedi AST metrika script | scope: `src/` | stdout: `functions_total=2306`, `functions_fully_typed=1860`, `files_over_250=40`, `long_functions_over_50=144`, `complexity_over_5=266`, `nesting_over_3=98`
- Ugyanebből a scriptből konkrét sorok: `FILELOC|src/presentation/gui/windows/main_window.py|443`, `COMP|src/api/routes/wind_rose.py|63|_process_wind_rose_data|38`, `LONG|src/presentation/gui/demos/map_tab_demo.py|25|demo_hungarian_map_tab|200`, `NEST|src/presentation/gui/results_panel/extreme/text_generators.py|120|_generate_wind_text|7`

## §5 TEST ANALYSIS
Kötelező teljes futás (`tests/` teljes suite, `src/` teljes coverage scope) nem adott lezárt coverage riportot.

Futtatott parancsok + scope + releváns stdout/stderr:
- `pytest tests/ --cov=src --cov-report=term-missing -q` | scope: teljes `tests/`, teljes `src/` | stderr: `ModuleNotFoundError: No module named 'src'`
- `PYTHONPATH=. pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q` | scope: teljes `tests/`, teljes `src/`, line+branch cél | futás elindult (`collected 1004 items`), nem adott záró coverage summary-t
- `PYTHONPATH=. timeout 20 pytest tests/ --cov=src --cov-branch --cov-report=term-missing -q; echo "PYTEST_EXIT=$?"` | scope: teljes `tests/`, teljes `src/`, line+branch cél | stdout: `collected 1004 items ... PYTEST_EXIT=124`

Coverage eredmény:
- Line coverage: **insufficient evidence** (nincs lezárt coverage summary).
- Branch coverage: **insufficient evidence** (nincs lezárt coverage summary).
- `<70%` fájllista: **insufficient evidence** (coverage report hiányzik).

Kiegészítő teszt-metrikák:
- `find src -name '*.py' | wc -l` => `502`
- `find tests -name '*.py' | wc -l` => `53`
- Forrás-teszt arány: 502:53 (kb. 9.47:1)
- `grep -Rnl --include='*.py' -E '^\s*def test_' tests | xargs -r grep -L 'assert'` => `tests/test_smoke.py`

Untested critical paths (kockázati rangsor, coverage evidence hiányában):
- 1) `src/api/routes/wind_rose.py:63` (complexity 38, hosszú függvény) — **HIGH**
- 2) `src/presentation/gui/results_panel/utils/dataframe_extractor.py:33` (complexity 29) — **HIGH**
- 3) `src/presentation/gui/data_widgets/table_model.py:61` (complexity 29, nesting 7) — **HIGH**

## §6 SECURITY FINDINGS
`.env` git-tracked ellenőrzés:
- `git ls-files .env` | scope: git index | stdout: *(üres)* -> `.env` **nem tracked**.
- Prompt szabály szerinti automatikus CRITICAL feltétel (`.env` tracked) ezért **not present**.

Hardcoded secrets:
- `.env:1` `OPENMETEO_API_KEY=...`
- `.env:2` `METEOSTAT_API_KEY=...`
- `.env:3` `METEOSOURCE_API_KEY=...`

Unsafe kódminták (`eval/exec/os.system`, unsafe deserialization, MD5/SHA1):
- `rg -nP "(?<!\.)\beval\(|(?<!\.)\bexec\(|\bos\.system\(|pickle\.loads\(|yaml\.load\(|hashlib\.md5\(|hashlib\.sha1\(" src` | scope: `src/` | stdout: *(nincs találat)*
- Megjegyzés: `.exec()` GUI metódushívások vannak, de ez nem Python `exec()` builtin.

SQL injection minta:
- `rg -n "execute\(f[\"']|executemany\(f[\"']|cursor\.execute\(f[\"']" src` | scope: `src/` | stdout: *(nincs találat)*

API authentication:
- `rg -n "APIRouter|Depends\(|HTTPBearer|OAuth2|Security\(" src/api src/presentation/api` | scope: API rétegek | releváns stdout: route-ok és `APIRouter` találatok vannak, auth dependency (`Depends/HTTPBearer/OAuth2/Security`) találat **not present**.

## §7 TOOLING & CI/CD
Ruff:
- Konfiguráció: jelen van (`pyproject.toml`, `.pre-commit-config.yaml`).
- Futtatás: `ruff check src/` | scope: `src/` | stdout: `Found 98 errors.`

Mypy:
- Konfiguráció: jelen van (`pyproject.toml`, `mypy.ini`, `.pre-commit-config.yaml`).
- Futtatás: `mypy src/` | scope: `src/` | stdout: `Found 1313 errors in 193 files (checked 490 source files)`

Pytest:
- Futtatás: teljes suite indult, de timeout (`PYTEST_EXIT=124`) a kötelező coverage záró riport nélkül.

pre-commit:
- `rg -n "repos:|ruff|mypy|pytest" .pre-commit-config.yaml` | scope: root | stdout: `repos:`, `ruff`, `mypy`, `pytest` hookok jelen vannak.

GitHub Actions / CI:
- `find .github -maxdepth 3 -type f` | scope: root | stdout: *(üres)* -> workflow fájl **not present**.

## §8 POSITIVE FINDINGS
- `src/infrastructure/repositories/city_repository_queries.py:202` paraméterezett SQL futtatás (`cursor.execute(query, params)`), ami SQL injection ellen védettebb.
- `src/api/dto/trend_request.py:35` és `src/api/dto/trend_request.py:53` Pydantic validátorokkal bemeneti szűrés (helynév, időszak, dátumformátum).
- `src/application/use_cases/analyze_multi_city.py:65` és `src/application/use_cases/analyze_multi_city.py:208` use-case szintű input validáció és kontrollált fallback eredmény.
- `src/domain/ports/__init__.py:36` és `src/domain/ports/__init__.py:114` Protocol-alapú port interfészek (absztrakciós szándék látható).

## §9 RISK MATRIX
| Kategória | Értékelés | Indoklás |
|---|---|---|
| Architecture | 🔴 | 31 layer violation, domain external/internal tiltott importok, 1 circular import csoport. |
| Code Quality | 🚨 | 40 db `>250 LOC` fájl, 266 db complexity `>5`, 144 db `>50` soros függvény, 98 db mély nesting. |
| Tests | 🔴 | Kötelező teljes pytest+coverage futás timeouttal zárt, nincs lezárt line/branch coverage bizonyíték. |
| Security | 🔴 | `.env` nem tracked, de élő API kulcsok plain textben; API auth mechanizmus jele `not present`; unsafe builtin-ekre nincs találat. |
| Maintainability | 🚨 | `ruff` 98 hiba, `mypy` 1313 hiba/193 fájl, prezentációs réteg dominancia (390 Python fájl). |

## §10 EVIDENCE GAPS
- Teljes line+branch coverage százalék és fájlszintű `<70%` lista: **insufficient evidence**, mert a kötelező teljes futás timeouttal (`PYTEST_EXIT=124`) zárt, záró coverage riport nélkül.
- Duplicate logic (kódklón) mértéke: **insufficient evidence**, dedikált klón-detektor nem futott.
- API authentication runtime enforcement (pl. tokenellenőrzés tényleges működése): **insufficient evidence**, statikus keresés alapján auth dependency jel `not present`, de runtime konfiguráció nem volt végrehajtható ebben az auditban.
