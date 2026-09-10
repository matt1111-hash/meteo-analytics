# 01_MAP — Projektfeltérképezés és mért alapállapot

**RUN_ID:** `20260910T092914Z`
**Mód:** read-only térkép (nincs logikai / security / teljesítmény-audit)
**Repo gyökér:** `/home/tibor/PythonProjects/meteo-analytics`
**Időbélyeg (UTC, mérés indítása):** `20260910T092914Z`

A `RUN_ID` környezeti változó a sessionben **UNSET** volt; az azonosító a mérés UTC időbélyege.

---

## 1. Snapshot és scope

### 1.1 Git snapshot

| Mező | Érték | Parancs |
|------|--------|---------|
| Commit SHA | `c4793cdc9ef6161d2bcaf91d994bae2348426d78` | `git rev-parse HEAD` |
| Branch | `main` (up to date with `origin/main`) | `git branch --show-current` |
| NOGIT? | nem | `.git` létezik |

A térkép a **worktree** tartalmát méri (nem csak a HEAD blobjait). A HEAD-hez képest a worktree a mérés elején **piszkos** volt; ez a snapshot része, nem ennek a futásnak a mellékhatása.

### 1.2 Induló worktree (`git status --porcelain`, mérés eleje)

```
 M .env.example
 D .qwen/settings.json
 M .secrets.baseline
 D "200 | sort -rn | head -20"
 D ARCHITECTURE.md
 D FINAL_VERIFY.md
 M src/api/main.py
 M src/config/api_config.py
?? .deepseek/
?? .reasonix/
?? .repowise/
?? reasonix.toml
```

`git diff --stat` (HEAD → worktree, mérés közben, titkot nem idézve): 8 fájl, **3 beszúrás / 823 törlés**. A termékérintett módosítások: `src/api/main.py` (98 sor nettó törlés), `src/config/api_config.py` (6 sor törlés).

### 1.3 Scope — mi számít bele

**Source-rootok (termékkód):**

| Root | Szerep |
|------|--------|
| `src/` | Python backend + PySide6 GUI (Clean Architecture rétegek) |
| `frontend/src/` | React 19 + TypeScript + Vite SPA |
| `meteo_gui_starter.py` | kanonikus desktop GUI belépő a repo gyökerében |

**Test-rootok:**

| Root | Szerep |
|------|--------|
| `tests/` | pytest (Python) |
| `frontend/src/**/*.test.{ts,tsx}` | Vitest (jsdom) |
| `tests/e2e/` | Playwright (`smoke.spec.ts`) + pytest ASGI smoke (`test_smoke.py`) |

**Önálló alprojektek (saját manifest + lock):**

1. **Python app** (repo gyökér) — `requirements.txt` / `requirements.lock` / `pyproject.toml`
2. **frontend/** — `package.json` + `package-lock.json` (npm lockfileVersion 3)
3. **tests/e2e/** — `package.json` + `package-lock.json` (`@playwright/test`)

**Nyelvek / runtimeok:**

| Runtime | Deklarált | Lokálisan elérhető | Megjegyzés |
|---------|-----------|-------------------|------------|
| Python | `requires-python = ">=3.12"` (`pyproject.toml`); CI `3.12`; health-check mátrix `3.12` és `3.13` | `/usr/bin/python3` = CPython **3.12.3**; `venv/bin/python` = CPython **3.12.3** | Nincs exact pin → **KONFLIKTUS (nincs pin)**. `python3.13` a PATH-on **nincs** (`command -v python3.13` → üres). |
| Node | `frontend/package.json` **nincs** `engines` / `packageManager` mező; e2e CI `node-version: "22"` | `/usr/local/bin/node` = **v24.19.0**; npm **12.0.2** | **KONFLIKTUS (nincs pin + CI 22 vs local 24)**. |

**Frameworkök (tartalom + manifest, nem README):**

- Backend HTTP: FastAPI `0.135.1` + Starlette `0.52.1` + Uvicorn `0.41.0` (lock/venv)
- GUI: PySide6 `6.9.1` + PyQtDarkTheme2 (`import qdarktheme`)
- Frontend: React `19.2.6`, react-router-dom `7.15.1`, Vite `8.0.10`, Vitest `4.1.5`
- Adat: pandas, geopandas, numpy, scipy, matplotlib, plotly, folium; SQLite fájlok `data/*.db`
- HTTP kliens: `requests` (provider), `httpx` (tesztek / ASGI)

**Build / csomagkezelő:**

- Python: pip + `requirements.lock`; venv a gyökérben (`venv/`)
- Frontend: npm (`package-lock.json`); `frontend/node_modules` jelen van
- Make: `Makefile` (BE+FE wrapper a `quality_gate.sh` köré)
- Quality: `quality_gate.sh`, `.quality_gate.conf`, Ruff, Mypy, pytest, import-linter, pre-commit

### 1.4 Manifesztek, lockfile-ok, sémák, migrációk, CI, container, deploy

**Manifesztek / lockok (olvasva):**

| Fájl | Szerep |
|------|--------|
| `pyproject.toml` | Tool config (ruff/mypy/pytest/coverage). `[project] name = "my-project"`, `dependencies = []` — **nem** a runtime manifest |
| `requirements.txt` | 16 **pinnelt** runtime csomag (`==`) |
| `requirements-dev.txt` | teszt/lint; `-r requirements.txt`; ruff/mypy **exact** pin, több más `>=` |
| `requirements.lock` | 189 pinnelt sor (`==`) |
| `frontend/package.json` + `frontend/package-lock.json` | npm, lockfileVersion 3, 401 `packages` kulcs |
| `tests/e2e/package.json` + `tests/e2e/package-lock.json` | Playwright; lockfileVersion 3, 5 packages; `@playwright/test` lock **1.59.1** vs manifest `^1.52.0` |

**Sémák / migrációk:**

| Tétel | Eredmény | Két módszer |
|-------|----------|-------------|
| Alembic / Prisma / Django migrations | **nincs** | (1) `find` név/glob; (2) `git ls-files \| grep -iE 'docker\|alembic\|prisma\|...'` → `GIT_NO_DOCKER_MATCH` |
| SQL dump | `src/scripts/hungarian_settlements_dump.sql` — **adatdump**, nem migrációs runner | `find` + path létezik |
| Élő SQLite sémák (read-only `mode=ro`) | lásd §4 | `sqlite3` `sqlite_master` |

**CI / hooks / deploy:**

| Fájl | Szerep |
|------|--------|
| `.github/workflows/ci.yml` | push/PR `main`: pip lock, `ruff check src/`, `mypy src`, pytest+cov `--ignore=tests/gui` |
| `.github/workflows/health-check.yml` | Python 3.12+3.13, ruff `src tests`, mypy `src`, pytest+cov, bandit |
| `.github/workflows/pre-commit.yml` | `pre-commit/action@v3.0.1` |
| `.github/workflows/e2e-tests.yml` | Node 22, `npm ci` frontend, Playwright chromium/firefox, `scripts/dev.sh` |
| `.github/dependabot.yml` | pip `/`, npm `/frontend`, github-actions |
| `.pre-commit-config.yaml` | ruff **v0.15.10**, mypy, import-linter, radon, pytest, detect-secrets |
| `.githooks/commit-msg` | helyi hook |
| `scripts/install_hooks.sh` | hook telepítő |
| Dockerfile / compose / k8s / helm / terraform | **nincs** (find + `git ls-files` grep) |
| `*.desktop` + `scripts/launch_meteo_analytics_*.sh` | Linux desktop indítók (nem konténer-deploy) |

**CI hivatkozás, de fájl nincs:** `.coveragerc` — `ls` → nincs; `git ls-files --error-unmatch .coveragerc` → pathspec error. A coverage konfig a `pyproject.toml` `[tool.coverage.*]` alatt van. `ci.yml` / `health-check.yml` mégis `--cov-config=.coveragerc`-et ad át.

**Launcher hivatkozás, de fájl nincs:** `meteo_gui_starter.py` `requirements-base.txt`-t említ; `ls` + `git ls-files` → **nincs**.

### 1.5 Kizárások (a leltár és a kapuk scope-jából)

Minden kizárás, amit a számlálás / AST / kapuk **nem** vettek termékforrásként:

| Kizárás | Indok |
|---------|--------|
| `.git/` | VCS |
| `docs/audit/` | audit-output |
| `venv/` | virtuális környezet |
| `frontend/node_modules/` | vendor |
| `tests/e2e/node_modules/` | vendor |
| `frontend/build/` | build kimenet |
| `__pycache__/`, `*.pyc` | bytecode |
| `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.grimp_cache/`, `.import_linter_cache/` | tool cache |
| `data/cache/`, `data/climate_cache/` | runtime cache |
| `htmlcov/`, `.coverage`, `coverage.xml` | generált coverage (más futás) |
| `tests/e2e/playwright-report/`, `tests/e2e/test-results/` | generált e2e kimenet |
| `.repowise/`, `.reasonix/`, `.deepseek/` | tool index / session (generált) |
| `dist/` (ha lenne) | build |

További, a **forrás/teszt LOC-leltárból** kihagyott, de a fában meglévő tételek: `src/scripts/*.{csv,xlsx,sql}` (adat), `data/*.db`, `data/geojson/`, IDE (`.vscode`, `.claude`, `.agents`), `learnings.md` / README (navigáció, nem bizonyíték).

---

## 2. Mért leltár

### 2.1 Számlálási kritériumok (minden darabszámhoz)

**Python source fájl:** `src/**/*.py` **vagy** `meteo_gui_starter.py`; `__pycache__` kizárva.
**Python test fájl:** `tests/**/*.py`, `node_modules` / `__pycache__` / playwright-report / test-results kizárva.
**Frontend source:** `frontend/src/**/*.{ts,tsx,css,svg}` **kivéve** `*.test.*` / `*.spec.*`.
**Frontend test:** `frontend/src/**/*.{test,spec}.{ts,tsx}`.
**E2E TS:** `tests/e2e/*.{ts,tsx}` a fenti prune után.
**Fizikai LOC:** bájt-szintű `\n` szám + 1, ha a fájl nem `\n`-nel végződik. A `wc -l` a záró newline nélküli utolsó sort is számolja — eltérés csak trailing-newline esetén.

**Második fájlszám-módszer:** `find` (ugyanazok a prune-ok) vs Python `os.walk`; Python forrás/teszt esetén harmadik ellenőrzés: `git ls-files <dir> \| grep '\.py$'`.

### 2.2 Fájlszámok

| Halmaz | Módszer 1 (`os.walk` / inventory) | Módszer 2 (`find`) | Módszer 3 (`git ls-files … \| grep '\.py$'`) | Verdikt |
|--------|-----------------------------------|--------------------|-----------------------------------------------|---------|
| `src/**/*.py` | 622 (inventory lista starter nélkül) | 622 | 622 | **EGYEZIK** |
| `meteo_gui_starter.py` | 1 | 1 (`ls`) | tracked | **EGYEZIK** |
| Python source összesen (src+starter) | **623** | 622+1 | 622+1 | **EGYEZIK** |
| `tests/**/*.py` | 236 | 236 | 236 | **EGYEZIK** |
| Frontend source (ts/tsx/css/svg, teszt nélkül) | **127** (lista) | 127 | — | **EGYEZIK** |
| Frontend test | 9 | 9 | — | **EGYEZIK** |
| E2E TS | 2 | 2 | — | **EGYEZIK** |
| `scripts/*.py` | 5 (3 script + 2 `test_*.py`) | 5 | — | **EGYEZIK** |
| Walked fájlok a prune után | 1078 | 1078 (`find_all_files.txt`) | tracked 1074 (más kritérium: csak git) | walk/find **EGYEZIK**; git tracked nem ugyanaz a halmaz |

**Nem KONFLIKTUS, más kritérium:** `files_by_bucket['frontend_source']=126`, mert a számláló csak akkor növelte a bucketet, ha a LOC-ot számolta, és a `frontend/src/logo.svg` kiesett. A fájllista 127 elemű (benne az svg). Jelentett source-szám: **127** (svg bent), kód-nyelvű: **126**.

`git ls-files 'src/**/*.py'` **621**-et adott: a git glob **nem** illeszkedik a `src/__init__.py` közvetlen gyerekre. Ez glob-csapda, nem hiányzó fájl; a `git ls-files src \| grep '\.py$'` a helyes második git-módszer.

### 2.3 Fizikai LOC nyelvenként

| Halmaz | Inventory (newline-count) | `wc -l` | Verdikt |
|--------|---------------------------|---------|---------|
| `src/**/*.py` | 65305 | 65305 | **EGYEZIK** |
| `meteo_gui_starter.py` | 327 | 327 | **EGYEZIK** |
| Python source összesen | **65632** | 65632 | **EGYEZIK** |
| Python tests | **27026** | 27026 | **EGYEZIK** |
| `scripts/*.py` | 2265 (1916 script + 349 script_test) | 2265 (2592 starterrel − 327) | **EGYEZIK** |
| FE ts source (nem teszt) | — | 3626 / 25 fájl | |
| FE tsx source | — | 11123 / 54 fájl | |
| FE css | 10392 | 10392 / 47 fájl | **EGYEZIK** |
| FE tests (ts+tsx) | 3606 | 3606 / 9 fájl | **EGYEZIK** |
| E2E ts | 69 | 69 | **EGYEZIK** |
| TS összesen (fe src ts + teszt ts + e2e) | 4672 | 3626+977+69=4672 | **EGYEZIK** |
| TSX összesen (src+teszt) | 13752 | 11123+2629=13752 | **EGYEZIK** |

Python (src+tests+scripts+starter) fizikai LOC: **94923**.

Frontend kód (src ts/tsx/css + tesztek, svg nélkül): 3626+11123+10392+3606 = **28747**.

### 2.4 Fájlméret (src)

Kritérium: fizikai LOC / `src/**/*.py`.
**0** fájl > 300 sor; **28** fájl > 250 sor; max = **300** (`src/presentation/gui/hungarian_city_selector/ui_builder.py`).
Tesztek: **5** fájl > 300 sor, max **808** (`tests/domain/entities/test_analytics_models_coverage.py`).

### 2.5 Parser

Minden scoped `.py` AST-parse: **0** `SyntaxError` (inventory `parse_failures: []`).
`compileall` (venv 3.12.3 és `/usr/bin/python3.12`): exit 0. (Bytecode-ot ír `__pycache__`-be; gitignored.)

---

## 3. Kapueredmények

Jelmagyarázat: **PASS** / **WARN** / **FAIL** / **BLOKKOLT**. A PATH vs pin eltérés **KONFLIKTUS**.

### 3.1 Eszközpin vs PATH

| Eszköz | Pin (repo) | venv bináris | PATH bináris | Kapu |
|--------|------------|--------------|--------------|------|
| ruff | `requirements-dev.txt` / lock / pre-commit **0.15.10** | `/home/tibor/PythonProjects/meteo-analytics/venv/bin/ruff` **0.15.10** | `/home/tibor/.local/bin/ruff` **0.16.2** | **KONFLIKTUS** — a PATH ruff a gate-et elbukja |
| mypy | lock / requirements-dev **1.17.0** | `venv/bin/mypy` **1.17.0** | `/home/tibor/.local/bin/mypy` **2.3.0** | verzió **KONFLIKTUS**; `src` eredmény azonos PASS |
| pytest | lock **9.0.3** (`requirements-dev` `>=8.0.0`) | `venv/bin/pytest` **9.0.3** | `/home/tibor/.local/bin/pytest` **9.1.1** | verzió **KONFLIKTUS**; collect **1743** mindkettőn |
| import-linter | lock **2.11** | `venv/bin/lint-imports` **2.11** | `/home/tibor/.local/bin/lint-imports` **2.13** | verzió **KONFLIKTUS**; mindkettő 3/3 KEPT |
| uvicorn | `requirements.txt` / lock **0.41.0** | venv **0.41.0** | PATH **0.52.1** | **KONFLIKTUS** (CLI, ebben a futásban nem indítottunk szervert) |
| tsc / eslint / vitest / vite | lock: tsc **5.8.3**, eslint **9.39.4**, vitest **4.1.5**, vite **8.0.10**; `package.json` caret (`^`) | `frontend/node_modules/.bin/*` | PATH-on **nincs** `tsc`/`eslint`/`vitest` | **KONFLIKTUS (nincs exact pin a package.json-ban + nincs PATH bináris)** |
| Python | `>=3.12`, nincs patch-pin | 3.12.3 | 3.12.3 | **KONFLIKTUS (nincs pin)**; a két bináris verziója egyezik |
| Node | nincs `engines` | — | v24.19.0; CI e2e Node **22** | **KONFLIKTUS (nincs pin)** |

`quality_gate.sh --full` **BLOKKOLT:** tesztet futtat (`check_tests`), coverage-t ír, és a teljes suite izoláltsága nem bizonyított (lásd §3.7). A check-only ekvivalenseket külön futtattuk (`ruff check` fix nélkül, `ruff format --check`, `mypy`, collect).

`npm run build` / `vite build` **BLOKKOLT:** `frontend/build/`-be ír.

### 3.2 Python kapuk

| Kapu | Parancs | Eszköz | Eredmény |
|------|---------|--------|----------|
| compileall | `python -m compileall -q -x 'venv\|node_modules\|__pycache__' src tests scripts meteo_gui_starter.py` | venv 3.12.3 **és** `/usr/bin/python3.12` | **PASS** / **PASS** |
| ruff check `src tests scripts meteo_gui_starter.py` | `ruff check … --output-format=concise` | venv 0.15.10 | **PASS** (`All checks passed!`) |
| ruff check (ugyanaz) | ugyanaz | PATH 0.16.2 | **FAIL** — **29** error: 28× `PLR0917`, 1× `RUF036` (új szabály a pinnelt ruffhoz képest). **KONFLIKTUS**, a függő kapu: **ruff check**. |
| ruff format --check | `ruff format --check src tests scripts meteo_gui_starter.py` | venv 0.15.10 **és** PATH 0.16.2 | **PASS** / **PASS** („863 files already formatted”). Elvárt fájlszám 622+236+5+1=**864** → **KONFLIKTUS** a riportolt 863 vs 864 között (eredmény PASS marad). |
| mypy `src` | `python -m mypy src --ignore-missing-imports` | venv 1.17.0 **és** PATH 2.3.0 | **PASS** / **PASS** — „Success: no issues found in **611** source files” |
| mypy `tests` | `python -m mypy tests --ignore-missing-imports` | venv **és** PATH | **FAIL** / **FAIL** — **268** error **56** fájlban (236 checked). CI ezt a kaput **nem** futtatja. |
| import-linter | `lint-imports` | 2.11 és 2.13 | **PASS** / **PASS** — 3 contract KEPT; „Analyzed **632** files, **2190** dependencies” |
| pytest collect | lásd §3.3 | 9.0.3 és 9.1.1 | **PASS** collect **1743** |

**mypy 611 vs find 622:** 11 fájl–mappa ütközés (§4.3). `622 − 11 = 611`. A mypy egy modulnéven egy fájlt lát; a shadowolt `.py` **nem** typecheckelt. Ez mért vakfolt, nem mypy PASS cáfolata.

**import-linter 632 vs find 622:** 10 fájl eltérés. A tool belső fájllistája nem lett második, független dump-pal visszafejtve → **nem** emeljük bizonyított hiányzó/többlet fájllá; lásd Ismert korlátok.

### 3.3 Pytest collection

Kritérium: `pytest tests/ --collect-only -q -o addopts=` (a pyproject `-v` addopts felülírva), nodeid-ek `tests/…::…`.

| Eszköz | Collected | Exit |
|--------|-----------|------|
| venv pytest 9.0.3 (CI-szerű plugin lista) | 1743 | 0 |
| venv pytest 9.0.3 (default pluginok) | 1743 | 0 |
| PATH pytest 9.1.1 | 1743 | 0 |

**194** modul, **356** class, **1743** function/coroutine.

CI `--ignore=tests/gui`: a könyvtár **nincs** (`ls` + `git ls-files tests/gui` = 0). A flag no-op.

### 3.4 Frontend kapuk

| Kapu | Bináris | Eredmény |
|------|---------|----------|
| `tsc --noEmit` (`tsconfig` `include: ["src"]`) | `frontend/node_modules/typescript/bin/tsc` 5.8.3 | **PASS** (üres kimenet, exit 0) |
| `eslint src` (fix nélkül) | `frontend/node_modules/eslint/bin/eslint.js` 9.39.4 | **FAIL** — **13** error / 0 warning, **10** fájl. Többség `react-hooks/set-state-in-effect`; `HierarchicalSelector.tsx` „Cannot create components during render”. |
| `npm run lint` | a script **`tsc --noEmit`**, nem eslint | tsc **PASS**; az eslint **nem** a kanonikus npm lint |
| vitest list | vitest 4.1.5, node v24.19.0 | **PASS** — **342** tesztnév, **9** fájl |
| vitest run (jsdom, lokális) | ugyanaz | **PASS** — `Test Files 9 passed (9); Tests 342 passed (342); Duration 1.41s` |
| Playwright `--list` | `tests/e2e/node_modules/.bin/playwright` | **PASS** collect — **8** teszt / 1 fájl (`smoke.spec.ts`) × chromium+firefox |
| Playwright futtatás | — | **BLOKKOLT** — élő stack (`scripts/dev.sh`, :8003/:5174) + browser install; nem izolált |

PATH tsc/eslint/vitest: **nincs** — csak a lock/node_modules bináris futott.

### 3.5 Build

| Kapu | Eredmény |
|------|----------|
| Python package build (`python -m build`) | **BLOKKOLT** — nem kértük, dist-et írna; nincs setuptools csomag-entrypoint a pyproject `[project]` üres dependencies mellett |
| `frontend` `tsc && vite build` | **BLOKKOLT** — `frontend/build/`-be ír |

### 3.6 `requirements.txt` vs lock vs venv (runtime pin)

| Csomag | `requirements.txt` | `requirements.lock` | venv `importlib.metadata` | Verdikt |
|--------|--------------------|---------------------|---------------------------|---------|
| pandas | 3.0.2 | 3.0.1 | 3.0.1 | **KONFLIKTUS** |
| anyio | 4.13.0 | 4.9.0 | 4.9.0 | **KONFLIKTUS** |
| matplotlib | 3.10.9 | 3.10.5 | 3.10.5 | **KONFLIKTUS** |
| többi 13 rt pin | egyezik a lockkal | — | — | egyezik |

A venv a **lockot** követi, nem a `requirements.txt` újabb pinjeit.

### 3.7 Teljes Python tesztsuite

**BLOKKOLT.** Indok (nem becslés):

1. A provider-tesztek `import requests`-et használnak a valós kliensmodulokra (`src/infrastructure/weather/{openmeteo,meteostat,weather_provider_base}.py` is `import requests`). Az összes teszt mockoltsága collect-onlyból **nem** bizonyított.
2. City/DB tesztek a helyi `data/*.db` fájlokhoz kötődnek; a suite futtatása a worktree adatfájljait módosíthatná.
3. A Playwright e2e (külön suite) élő HTTP-t igényel; a pytest `tests/e2e/test_smoke.py` ASGI+mock, de ez csak 11 teszt a 1743-ból.

Coverage **ebben a futásban nincs mérve**. A meglévő `.coverage` (szept 9) / `coverage.xml` (ápr 18) **más futás** artifactja — nem közöljük számként.

---

## 4. Import / dependency / ciklus

### 4.1 Statikus import feloldás

Kritérium: AST `Import`/`ImportFrom` (level=0) minden scoped `.py`-n; top-name `importlib.util.find_spec` a **venv** interpreterrel.

- Belső `src.*` / `tests.*`: **0** unresolved (két eljárás: modulnév-halmaz walk + `find_spec` nem kellett belsőre).
- Third-party top-level (bármely import, nested/try is):
  `PySide6, pytest, pandas, fastapi, matplotlib, httpx, numpy, starlette, folium, pydantic, requests, geopandas, qdarktheme, scipy, anyio, plotly`
  Mindegyikre `find_spec` a venvben **sikerült**; `missing_find_spec: []`.
- Importnév ≠ dist: `qdarktheme` ↔ `PyQtDarkTheme2` (lock + `requirements.txt`). `PIL`/`yaml` **nincs** import (két módszer: AST top-lista + `rg import PIL|from yaml`).

**Opcionális (top-level `try` + ImportError/ModuleNotFoundError):** 26 rekord. Tartalom szerint: `meteo_gui_starter.py` PySide6/projekt import; GUI térkép: `folium`, `geopandas`; néhány GUI try a `src.config` / relatív modulokra.

**Nested (függvénytörzs / nem modul-top) import:** **678**. Vakfolt a top-level ciklusgráfnak.

**Dinamikus hívás (`import_module` / `__import__`):** **7** (köztük `scripts/test_fetch_flow.py` `__import__` nem konstans arg; `src/presentation/gui/results_panel/__init__.py` `import_module`).

**TYPE_CHECKING import:** 82.

### 4.2 Manifest vs kód

**Használt, lockban megvan, de nincs a `requirements.txt` közvetlen listájában** (venv+lock igen; `find_spec` OK):

| Import | Hol | Megjegyzés |
|--------|-----|------------|
| `requests` | `src/infrastructure/weather/{openmeteo,meteostat,weather_provider_base}.py` + 3 teszt | **közvetlen runtime import**, nincs `requirements.txt`-ben |
| `folium` | `src/presentation/gui/map/**` (9 fájl, try) | GUI runtime, nincs `requirements.txt`-ben |
| `numpy` | infra trend + GUI chartok + teszt | nincs `requirements.txt`-ben (tranzitív lock `numpy==2.3.1`) |
| `starlette` | `src/api/middleware/rate_limit.py` + route-ok + tesztek | FastAPI függőség, de **közvetlen import** |

**`uvicorn`:** nincs `import uvicorn`; CLI (`python -m uvicorn src.api.main:app`) a `scripts/dev.sh`, `scripts/launch_meteo_analytics_fullstack.sh`, README, frontend hibaüzenet. **Bekötött CLI-dep**, helyesen a `requirements.txt`-ben.

**pyproject.toml `[project].dependencies = []`:** a pip-installálható projektmeta **üres**; a valós runtime manifest a `requirements.txt`. **KONFLIKTUS** a két deklaráció között.

**Lockban van, kódban nincs import (AST top-lista üres + `rg import/from` = 0 fájl `src/tests/scripts/meteo_gui_starter.py`):**
`openai`, `redis`, `textual`, `reportlab`, `seaborn`, `schedule`, `PIL`/`pillow`, `yaml`, `bs4`/`beautifulsoup4`, `geopy`, `openpyxl`, `black`, `ipython`, `shapely`, `fiona`.
Ezek **tranzitív vagy tool** lock-sorok lehetnek; CLI/plugin-használatot Makefile / quality_gate / pre-commit blobban **nem** találtunk a fenti nevekre (kivéve a quality toolokat: ruff, mypy, pytest, xenon, radon, vulture, bandit, import-linter, mutmut, pre-commit, pip-audit, detect-secrets — azok **tooling**, nem runtime import).

**`python-dotenv==1.2.2` a lockban:**

1. AST `import dotenv` / `from dotenv` a `src/`-ben: **[]**
2. `rg load_dotenv` a `src/ tests/ scripts/ meteo_gui_starter.py` körön: **0** (a találatok `learnings.md` / `reasonix.toml` navigációs szöveg, nem termékkód)

Következtetés a térkép szintjén: a csomag **nincs bekötve** a product entrypointokba. (A `.env` betöltésének viselkedése security/logic audit tárgya.)

**Indokolatlanul nyitott tartományok:** `requirements-dev.txt` több `>=`; `pyproject.toml` optional-deps `>=`; frontend `package.json` minden verzió `^`. A lockok zárnak, a manifesztek nem.

**Frontend:**

| Csomag | package.json | Használat |
|--------|--------------|-----------|
| axios, leaflet, plotly.js-dist-min, react, react-dom, react-leaflet, react-router-dom, recharts | `dependencies` | `frontend/src` import — **bekötve** |
| `@types/leaflet` | `dependencies` (nem dev) | típus; **scope gyanús** |
| `web-vitals` | **devDependencies** | `frontend/src/reportWebVitals.ts` dinamikus `import('web-vitals')` — **rossz scope** (app runtime a devDeps-ben) |
| vitest, testing-library, eslint, typescript, vite | devDependencies | teszt/tool — **bekötve** |

### 4.3 Fájl–mappa ütközés (ugyanazon a pathon `.py` és könyvtár)

11 ütközés (inventory walk; mindegyik `Path.is_dir()` a `.py` stemjén):

1. `src/presentation/gui/weather_data_bridge.py` ↔ `weather_data_bridge/`
2. `src/presentation/gui/charts/wind_rose_chart.py` ↔ `wind_rose_chart/`
3. `src/presentation/gui/charts/base_chart.py` ↔ `base_chart/`
4. `src/presentation/gui/dialogs/anomaly_settings_dialog/ui_builder.py` ↔ `ui_builder/`
5. `src/presentation/gui/trend_analytics/trend_data_processor.py` ↔ `trend_data_processor/`
6. `src/presentation/gui/trend_analytics/trend_analytics_tab/ui_builder.py` ↔ `ui_builder/`
7. `src/presentation/gui/windows/main_window_actions.py` ↔ `main_window_actions/`
8. `src/presentation/gui/controller/weather_data_handler.py` ↔ `weather_data_handler/`
9. `src/presentation/gui/results_panel/windy_days_tab.py` ↔ `windy_days_tab/`
10. `src/presentation/gui/results_panel/quick_overview_tab.py` ↔ `quick_overview_tab/`
11. `src/presentation/gui/results_panel/tab_manager.py` ↔ `tab_manager/`

Tartalom-ellenőrzés (`weather_data_bridge.py`): a `.py` **re-export** a csomagból (`from src.presentation.gui.weather_data_bridge import …`). Pythonban a csomag és a modul azonos néven ütközik; a mypy 611-es fájlszáma ezzel esik egybe.

**Stdlib shadow:** `src/` közvetlen gyerek neve nem esik egybe `sys.stdlib_module_names`-szel (`shadow: []`). A `tests/` alatti `types` csomagnevet nem minősítettük stdlib-shadownak, mert a tesztcsomag `tests.` prefixszel töltődik.

### 4.4 Belső importgráf és ciklusok

Kritérium: **csak top-level statikus** `src.* → src.*` élek (TYPE_CHECKING / nested / try kimarad). DFS back-edge, kanonizált ciklus.

| Metrika | Érték |
|---------|-------|
| Gráf csúcs | 381 |
| Gráf él | 933 |
| Ciklus | **8** |

**8 statikus ciklus (tartalommal ellenőrizve):**

1. `src.domain.value_objects.enum_utils` → `enums` → `enum_utils`
   `enum_utils.py` top import az enumsból; `enums.py:207` késői `from src.domain.value_objects.enum_utils import` (`noqa: E402`).
2. `src.infrastructure.anomaly.anomaly_demo` → `anomaly_profile_manager` → `anomaly_demo`
   `anomaly_demo.py` importálja a managert; `anomaly_profile_manager.py:27` importálja `demo_anomaly_profile_manager`-t.
3–8. **Ön-él** a fájl–mappa ütköző neveken: a `.py` a saját csomagját importálja (`weather_data_bridge`, `wind_rose_chart`, `tab_manager`, `ui_builder` ×2, `main_window_actions`).

A nested 678 import **vakfolt**: a GUI-ban további ciklusok lehetnek függvényen belüli importtal (az első, nem szűrt gráf 60 ciklust látott, benne TYPE_CHECKING + nested). Azokat itt **nem** állítjuk bizonyított top-level ciklusnak.

`lint-imports` layer contract **PASS** (presentation → … → domain); a fenti ciklusok **rétegen belül** vannak, ezért a contract nem töri őket.

---

## 5. Annotált struktúra és entrypointok

### 5.1 Könyvtárfa (tartalom alapján, prune után)

```
.
├── src/                          # Python termékcsomag (importálható `src.*`)
│   ├── domain/                   # entitások, value object, portok, anomaly_detector; framework-mentesnek szánt
│   ├── application/              # use case-ek, DTO, wind_* service, trend command
│   ├── infrastructure/           # SQLite repo, weather provider (requests), CB, factories, composition_root
│   ├── analytics/                # MultiCityEngine — application/infra feletti orkestráció
│   ├── api/                      # FastAPI: main, routes, dto, middleware, dependencies
│   ├── config/                   # APIConfig, paths, provider/usage, atomic_io
│   ├── presentation/gui/         # PySide6 MVC (charts, map, workers, dialogs, …) — a kód nagy része itt van
│   ├── presentation/api/         # csak docstringes __init__.py — NINCS bekötve
│   └── scripts/                  # CSV/XLSX/SQL adatdump, NEM Python modulok
├── tests/                        # pytest tükör + root tesztfájlok + e2e
├── frontend/                     # Vite+React SPA
├── scripts/                      # launcherek, dev.sh, ad-hoc analyzer/test_*.py
├── data/                         # SQLite DB + geojson + user_preferences JSON
├── meteo_gui_starter.py          # GUI belépő
├── quality_gate.sh / Makefile    # kapu
└── requirements*.txt / lock / pyproject.toml
```

### 5.2 HTTP API — kanonikus

**Composition / app objektum:** `src.api.main:app` (`FastAPI`, `lifespan` → `build_service_registry()` → `app.state.services`).

**Router-bekötés:** 11× `app.include_router(...)` a `main.py` 94–104. sorában. Prefix a route-modulok `APIRouter(prefix=...)` hívásán (olvasva).

**Endpoint-számítási kritérium:** `@app.get|post` vagy `@router.get|post` a `src/api/main.py` + `src/api/routes/*.py` fájlokban, a dekorátor pathja + a router prefix. AST + `rg "@(router|app)\.(get|post"` egyezik: **22** HTTP handler.

| Módszer | Path |
|---------|------|
| GET | `/health` |
| GET | `/api/cities/search` |
| POST | `/api/weather/single-city-detailed` |
| GET | `/api/weather/metrics` |
| GET | `/api/weather/regions` |
| GET | `/api/weather/query-types` |
| GET | `/api/hungary/counties` |
| GET | `/api/hungary/regions` |
| GET | `/api/hungary/settlements` |
| GET | `/api/hungary/stations` |
| POST | `/api/analytics/trend` |
| POST | `/api/weather/anomalies` |
| POST | `/api/weather/multi-year-batch` |
| POST | `/api/weather/multi-city` |
| GET | `/api/providers/list` |
| GET | `/api/providers/status` |
| GET | `/api/providers/{provider_id}/status` |
| GET | `/api/providers/{provider_id}/usage` |
| POST | `/api/providers/{provider_id}/select` |
| GET | `/api/providers/selected` |
| POST | `/api/weather/single-city` |
| POST | `/api/weather/wind-rose` |

**Router darab:** 11 `APIRouter(` a `src/api/routes/` alatt (wind_rose_support prefix `/api/weather`). `wind_rose.py` **nem** definiál saját `APIRouter`-t; `from .wind_rose_support import *` + kompatibilitási wrapper.

**Legacy / be nem kötött:**

- `src/api/routes/wind_rose.py::get_wind_rose` — újrafogalmazott wrapper; a `@router.post("/wind-rose")` a `wind_rose_part3.py`-ben kötődik a **dekoráláskor** a part3 függvényhez. A wrapper **nem** a router handler.
- `tests/api/api_auth_support.py` — „API Authentication middleware” fixture, **0** collected teszt erről a modulról; a worktree `main.py` diffje auth-törlést mutat.
- `src/presentation/api/` — üres csomag, nincs import-gráf él rá a kanonikus API-ból.

### 5.3 Frontend SPA

Kritérium: `frontend/src/App.tsx` `<Route path=…>` (regex + fájlolvasás). **11** route:

`/`, `/analytics`, `/multi-city`, `/single-city`, `/multi-year`, `/anomalies`, `/heatmap`, `/extreme-events`, `/windy-days`, `/data-table`, `/trend-analytics`.

Belépő: `frontend/src/index.tsx` → `App`. Dev szerver: Vite **5174**, proxy `/api` → `localhost:8003` (`vite.config.ts`, olvasva). Env sablon: `frontend/.env.example` → `VITE_API_BASE_URL`.

### 5.4 CLI / GUI / worker / scheduler / admin / migráció

| Típus | Út | Státusz |
|-------|----|---------|
| GUI kanonikus | `meteo_gui_starter.py` → `MainWindow`; `if __name__ == "__main__"` | **kanonikus** |
| GUI launcher | `scripts/launch_meteo_analytics_gui.sh`, `meteo_analytics_*.desktop` | **kanonikus** (shell) |
| API kanonikus | `python -m uvicorn src.api.main:app --port 8003` | **kanonikus** |
| Fullstack | `scripts/dev.sh`, `scripts/launch_meteo_analytics_fullstack.sh` | **kanonikus** |
| Frontend only | `scripts/launch_meteo_analytics_frontend.sh`, `cd frontend && npm run dev` | **kanonikus** |
| GUI composition | `src/presentation/gui/gui_composition_root.py::build_gui_services` | **kanonikus** GUI DI |
| API composition | `src/infrastructure/container/{composition_root,factories}.py` + `src/api/dependencies.py` | **kanonikus** |
| GUI workers | `src/presentation/gui/workers/**` (QThread, nem Celery) | **kanonikus** a GUI-hoz |
| `__main__` demók | `src/presentation/gui/**/demo.py`, `city_manager_demo.py`, `anomaly_profile_manager.py`, stb. (14 dunder-main összesen) | **jelen van**; nem a desktop launcher hívja |
| Ad-hoc scriptek | `scripts/{gui_audit,ultimate_project_analyzer,add_city_name_index,test_city_name_flow,test_fetch_flow}.py` | **nincs** pytest-gyűjtés; kézi |
| Scheduler | `schedule` csomag a lockban, **0** import | **nincs bekötve** |
| Admin UI / Django admin | nincs route/modul | **nincs** (rg + route lista) |
| Migrációs runner | nincs | **nincs** |

### 5.5 Composition, globális állapot, env, külső szolgáltatás

**Registry / singleton (olvasott kód):**

- `app.state.services: ServiceRegistry` (lifespan, `src/api/dependencies.py`)
- `ProviderUsageService` modul-szintű `_usage_service` + `get_usage_service()` (`src/api/services/provider_usage_service.py:202-208`)
- `ProfessionalThemeManager._instance` (`src/presentation/gui/theme_manager/core.py`)
- `APIConfig` class-level mezők + `_reload_lock`

**Env-vezérlés (os.getenv / os.environ, `src/`):**
`APP_ENV`, `CORS_ORIGINS`, `METEOSTAT_API_KEY`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`, `RATE_LIMIT_MAX_CLIENTS`, `TRUSTED_PROXIES`, `METEO_FETCH_MAX_WORKERS`, `METEO_FETCH_TIMEOUT`, `METEO_FETCH_RETRIES`, `METEO_FETCH_RETRY_DELAY`, `WEATHER_ANALYZER_DATA_DIR`, `QT_QPA_PLATFORM`, `DISPLAY`, `WAYLAND_DISPLAY`.

`.env.example` (worktree): `METEOSTAT_API_KEY=your_rapidapi_key_here`. Nincs `load_dotenv` a product kódban (§4.2).

**Külső HTTP:** Open-Meteo (`APIConfig.OPEN_METEO_*`), Meteostat RapidAPI (`METEOSTAT_BASE` + API key).
**Helyi I/O:** `data/cities.db`, `data/hungarian_settlements.db`, `data/meteo_data.db` (GUI `DATA_DIR / "meteo_data.db"`), `data/user_preferences/*.json`, `data/geojson/*.geojson`.

**SQLite sémák** (`sqlite3` URI `mode=ro`):

| DB | Táblák |
|----|--------|
| `data/cities.db` | `cities`, `generation_metadata`, `sqlite_sequence` |
| `data/hungarian_settlements.db` | `hungarian_settlements`, `sqlite_sequence` |
| `data/meteo_data.db` | `cities`, `weather_data` |

---

## 6. Tesztkép

### 6.1 Python (pytest collect = 1743)

Kritérium: nodeid path prefix. **Nem** futtatott viselkedés.

| Kosár | Collected teszt | Kritérium |
|-------|-----------------|-----------|
| `tests/data/` | 675 | path |
| `tests/` root `test_*.py` | 374 | path mélység = 2 |
| `tests/domain/` | 297 | path |
| `tests/api/` | 145 | path (route + DTO + middleware + ASGI) |
| `tests/analytics/` | 118 | path |
| `tests/application/` | 72 | path |
| `tests/infrastructure/` | 34 | path |
| `tests/integration/` | 12 | path (`test_clean_architecture_*`) |
| `tests/e2e/` | 11 | path; ASGITransport, mockolt provider — **in-process**, nem Playwright |
| `tests/presentation/` | 5 | path (GUI headless / map security / analytics import) |
| **Összesen** | **1743** | |

Típusba sorolás (könyvtár + tartalom, nem a fájlnév önmagában):

- **Unit-szerű:** `tests/domain`, `tests/application`, `tests/analytics` (engine unit), `tests/data` nagy része (provider mock + sqlite helper), root config tesztek.
- **Integrációs / API:** `tests/api/*` (httpx ASGI a FastAPI appra), `tests/integration/*`, `tests/test_*integration*`, `tests/e2e/test_smoke.py` (saját docstring: full stack ASGI, mockolt külső API).
- **GUI:** 5 teszt `tests/presentation/` — PySide6 import a három fájlban. `pytest-qt` a `requirements-dev.txt`-ben; collected nodeid-ekben `qtbot` használat **nem** lett külön megszámolva (Ismert korlát, ha kell pontos qtbot-szám).
- **E2E böngésző:** Playwright 8 teszt, **nem** a 1743 része.

**19** `tests/**/*.py` nincs collected teszt (support modulok + `api_auth_support.py`). `__init__.py` / `conftest.py` szándékosan nem teszt.

**Közvetlen tükör:** van `tests/{domain,application,api,infrastructure,analytics,data}/`.
**Hiányzó közvetlen teszt-tükör a kód tömegére:** `src/presentation/gui/` (több száz `.py`) ↔ 5 presentation teszt. A coverage omit a pyprojectban: `src/presentation/gui/*`.

### 6.2 Vitest

9 fájl, **342 teszt, 342 passed** (ez a futás mérte). Komponens/unit (jsdom): Modal, ProviderSelector, HierarchicalSelector, StatusBar, BeaufortLegend, WindChart, AnomalySettingsModal, hungary/wind constants.

Nincs page-level teszt a 11 SPA route-ra.

### 6.3 Playwright

8 teszt listázva (4 spec × 2 project). Futtatás BLOKKOLT.

---

## 7. Meglévő védelmek (bekötve, tartalom alapján)

Csak az olvasott / AST-vel látott, aktív wiring:

| Védelem | Hol | Megjegyzés |
|---------|-----|------------|
| Pydantic request DTO | `src/api/dto/*`, wind_rose_part1, anomalies/single_city/detailed_city route | input validáció a presentation/API szélen |
| UseCaseResult → HTTP | `src/api/error_handling.py` | VALIDATION 400, PROVIDER 502, INTERNAL 500 (részlet elrejtve) |
| Rate limit middleware | `src/api/middleware/rate_limit.py` + `main.py` add_middleware | production 60/60s, dev 10000/60s; XFF csak `TRUSTED_PROXIES` |
| Security headers | `main.py` middleware | nosniff, DENY frame, XSS; production HSTS + CSP |
| CORS | `CORSMiddleware` GET/POST/OPTIONS, credentials, origin `CORS_ORIGINS` | production: `*` origin → `RuntimeError` a lifespanben |
| Circuit breaker | `src/infrastructure/resilience/circuit_breaker.py` + weather client tesztek | lockolt állapot |
| Atomic JSON írás | `src/config/atomic_io.py` | temp + replace |
| SQL paraméterezés | `city_repository_queries.py` `cursor.execute(query, params)`; `like_utils.escape_like` | LIKE escape dokumentált mintával |
| Import-linter rétegszerződés | `.importlinter` 3 contract, gate PASS | domain tiltott: fastapi/httpx/redis/… |
| Pre-commit | ruff, mypy, import-linter, detect-secrets, pytest | local hooks |
| CI | ruff+mypy+pytest+cov; health-check bandit (nem fail-on) | |
| detect-secrets baseline | `.secrets.baseline` tracked/modified | |
| Headless GUI guard | `src/presentation/gui/runtime_environment.py` (`QT_QPA_PLATFORM`, DISPLAY) | |

**Ellenpélda a térképhez (nem security-finding, csak wiring):** `city_manager_db.py:219` `cursor.execute(f"SELECT COUNT(*) FROM {table}")` `# nosec B608` — string-formázott SQL, belső `table` név. Következő auditok témája.

---

## 8. Ismert korlátok

Ezek **nem** bizonyított megállapítások.

1. Teljes pytest suite és coverage **nem** futott (§3.7).
2. Playwright teszt **nem** futott.
3. `quality_gate.sh --full`, `vite build`, pip/npm install, hálózat, pip-audit/CVE **BLOKKOLT**.
4. Nested 678 import: cikluskeresés vakfoltja; a 60-as „minden él” lista nem top-level bizonyíték.
5. Dinamikus `import_module` nem-konstans argumentummal (`results_panel/__init__.py`, `test_fetch_flow.py`) — feloldás nem teljes.
6. import-linter „632 files” vs find 622 — a 10 fájl nem lett két független listával azonosítva.
7. ruff format „863 files” vs 864 scoped py — 1 fájl eltérés magyarázata nincs második dump-pal.
8. mypy `src` a 11 ütköző `.py` közül a csomagot typecheckeli, a shadowolt fájlt nem.
9. `find_spec` csak a **venv** site-packages-re vonatkozik, nem egy tiszta lock-installra. A PATH Python (rendszer) third-party készlete nincs végigmérve.
10. Lock 189 sorból a tranzitív vs közvetlen bontás a `pipdeptree` futtatása nélkül (az is I/O/env) nem teljes; a „használatlan lock-sor” lista tool/tranzitív csomagokra **túlbecsülhet**.
11. `qtbot` / pytest-qt tényleges fixture-használat nincs külön megszámolva.
12. Frontend `eslint` PATH bináris nincs; csak node_modules. Caret vs lock: a node_modules verzió a lockot követi ebben a worktree-ben.
13. Health-check CI Python 3.13-at kér; helyben nincs 3.13.
14. A worktree piszkos (`main.py`, `api_config.py`); a térkép a **piszkos** fájlokat olvasta, nem a HEAD blobot. A HEAD viselkedése eltérhet.
15. `rg load_dotenv` a `learnings.md` / `reasonix.toml` szövegében talál navigációs említést — ez **nem** product wiring.
16. SQLite `mode=ro` séma: táblanevek, nem oszlop-audit.
17. `compileall` `__pycache__`-t írt (gitignored); a porcelain ettől nem változott.
18. Egy-módszeres maradék: import-linter belső 2190 él nem lett AST-gráffal 1:1 összevetve (más éldefiníció).

---

## 9. Következő auditok számára a legfontosabb vizsgálati területek

1. **Piszkos `src/api/main.py` / `src/config/api_config.py`** (auth-törlés gyanúja a diffstat alapján) + `tests/api/api_auth_support.py` holttest — logic/security.
2. **11 fájl–mappa ütközés** + 8 statikus ciklus (domain enums, anomaly_demo, GUI re-export). Resolver/mypy vakfolt.
3. **`requests` / `folium` / `numpy` közvetlen import** `requirements.txt` nélkül; **pandas/anyio/matplotlib pin drift** txt vs lock vs venv.
4. **`python-dotenv` a lockban, `load_dotenv` nincs** — env/titok betöltés (security).
5. **PATH ruff 0.16.2 FAIL** vs pin 0.15.10 PASS — CI a lockot telepíti, a helyi PATH nem.
6. **GUI (`src/presentation/gui`) teszt/coverage omit** vs a kódtömeg.
7. **mypy tests: 268 error** — a CI csak `src`-et nézi.
8. **eslint 13 error**, miközben `npm run lint` = `tsc`.
9. **Node 24 helyi vs CI 22**, nincs `engines`.
10. **`.coveragerc` hiány** a CI `--cov-config=.coveragerc` mellett.
11. **SQL f-string** `city_manager_db.py`; LIKE vs paraméterezés konzisztencia.
12. **Duplikált wind/trend implementáció** `application/services` vs `infrastructure/analytics` vs `src/analytics`.
13. **Singleton usage service** vs `app.state` registry — két composition út.
14. **Nincs konténer/migrációs runner** — deploy-feltételezés: asztali + uvicorn.
15. **pyproject `name = "my-project"` + üres dependencies** — toolkit sablon maradék.

---

## 10. Parancsnapló

| Parancs | Mit bizonyít | Eredmény |
|---------|--------------|----------|
| `pwd`; `git rev-parse HEAD`; `git branch --show-current`; `git status --porcelain` | snapshot | SHA `c4793cdc…`, `main`, piszkos worktree (lista §1.2)  <!-- pragma: allowlist secret -->|
| `python3 --version`; `venv/bin/python --version`; `node --version` | runtime | 3.12.3 / 3.12.3 / v24.19.0 |
| `readlink -f` + `--version` ruff/mypy/pytest/lint-imports/uvicorn mindkét binárison | pin vs PATH | táblázat §3.1 |
| `find` prune + `os.walk` inventory | fájlszám 2 módszer | 622/236/127/9/1078 egyezés |
| `git ls-files src \| grep '\.py$'` (+ tests) | 3. módszer py | 622 / 236 |
| `wc -l` vs inventory newline-count | fizikai LOC | src 65305, tests 27026, starter 327, FE css 10392, stb. — egyezés |
| `python -m compileall` venv + system | parser | PASS / PASS |
| `venv/bin/ruff check src tests scripts meteo_gui_starter.py` | lint pin | PASS |
| `/home/tibor/.local/bin/ruff check …` | lint PATH | FAIL 29 |
| `ruff format --check` mindkettő | format | PASS / PASS, 863 fájl |
| `mypy src` venv+PATH | typecheck source | PASS, 611 files |
| `mypy tests` venv+PATH | typecheck tests | FAIL, 268/56 |
| `pytest tests/ --collect-only` venv CI-plugin, venv default, PATH | test collection | 1743 / 1743 / 1743 |
| `lint-imports` 2.11 és 2.13 | architecture contract | 3 KEPT / 3 KEPT, 632 files |
| `frontend/node_modules/.bin/tsc --noEmit` | FE typecheck | PASS |
| `frontend/node_modules/.bin/eslint src` | FE lint | FAIL 13/10 fájl |
| `vitest list`; `vitest run` | FE teszt collect + izolált futtatás | 342 list; 342 passed |
| `playwright test --list` | e2e collect | 8 teszt / 2 project |
| AST inventory + `analyze_deps.py` (venv) | import/ciklus/find_spec | 0 missing spec, 8 statikus ciklus, 11 collision |
| `rg` + AST `dotenv`/`load_dotenv` | dotenv bekötés | 0 product találat |
| `rg import openai\|redis\|…` + AST top-lista | használatlan lock-jelöltek | 0 fájl a felsorolt runtime-idegeneken |
| `sqlite3 file:data/*.db?mode=ro` | sémák | 3 DB, táblalisták §5.5 |
| `ls` + `git ls-files` `.coveragerc`, `tests/gui`, `requirements-base.txt`, Docker | negatív állítások 2 módszer | mind hiányzik |
| `git diff --stat` | worktree méret | 8 fájl, +3/−823 |
| `git status --porcelain` (zárás) | csak audit fájl új? | lásd a jelentés utáni záró futtatás |

---

*Ez a fájl a RUN_ID `20260910T092914Z` 01_MAP kimenete. Termékkód, teszt, lock és config nem módosult szándékosan; írás csak ide és `/tmp/meteo-audit-20260910T092914Z/` alá történt.*
