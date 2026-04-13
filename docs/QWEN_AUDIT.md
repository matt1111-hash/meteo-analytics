# 🏗️ METEO-ANALYTICS — Full Repository Architecture Analysis

**Dátum:** 2026-04-07
**Eszköz:** Qwen Code
**Repó:** `/home/tibor/PythonProjects/meteo-analytics`
**Előző audit:** 2026-03-15 (CODEX, Overall Risk: 🟡 MEDIUM)

---

## 1. STRUKTÚRATÉRKÉP

### 1.1 Annotált könyvtárfa

```
meteo-analytics/
│
├── src/                              # Python backend (~685 .py fájl)
│   ├── api/                          # FastAPI REST API szerver
│   │   ├── main.py                   # ⚡ BELÉPÉSI PONT #1 (uvicorn src.api.main:app)
│   │   ├── routes/                   # 11 route modul (weather, analytics, cities, hungary, stb.)
│   │   ├── dto/                      # Request/Response DTO-k (trend, weather, provider)
│   │   ├── adapters/                 # Weather API adapter
│   │   └── services/                 # Provider usage tracking service
│   │
│   ├── domain/                       # Clean Architecture — Domain réteg
│   │   ├── entities/                 # Analytics, anomaly, location, weather data modellek
│   │   ├── ports/                    # Repository/service interface-ek (no I/O!)
│   │   ├── services/                 # Anomaly detector, trend calculator
│   │   ├── value_objects/            # CityInfo, enum-ök
│   │   └── analytics/                # Domain-level analytics (region resolver, wind analysis)
│   │
│   ├── application/                  # Clean Architecture — Application réteg
│   │   ├── dto/                      # Analytics, location DTO-k
│   │   ├── services/                 # Wind analysis service
│   │   └── use_cases/                # Multi-city analysis, trend calculation, anomaly detection
│   │
│   ├── infrastructure/               # Clean Architecture — Infrastructure réteg
│   │   ├── adapters/                 # DI container, city adapter
│   │   ├── container/                # Dependency injection (factories, core)
│   │   └── repositories/             # City repository (SQLite)
│   │
│   ├── presentation/                 # Clean Architecture — Presentation réteg
│   │   └── gui/                      # ⚠️ PySide6 desktop GUI (~520+ .py fájl!)
│   │       ├── windows/              # Main window, toolbar, menu, actions
│   │       ├── controllers/          # App controller, data handlers
│   │       ├── charts/               # 8+ chart típus (wind, heatmap, temperature, stb.)
│   │       ├── results_panel/        # Eredmény megjelenítés (overview, extreme, windy days)
│   │       ├── trend_analytics/      # Trend analytics tab
│   │       ├── workers/              # Thread workers (analysis, weather data, worker manager)
│   │       ├── control_panel/        # Dátum, keresés, provider vezérlők
│   │       ├── hungarian_*/          # Hungary-specifikus selector/map/map tab
│   │       ├── dialogs/              # Anomaly settings dialog
│   │       ├── theme_manager/        # Tema/színkezelés
│   │       └── utils/                # Formatters, validators, constants, export helpers
│   │
│   ├── analytics/                    # ⚠️ Párhuzamos legacy csomag (multi-city engine)
│   │   ├── multi_city_engine_*.py    # 8+ fájlra szétvágott engine
│   │   ├── ports/                    # Multi-city port interface-ek
│   │   └── wind_analysis.py          # Szél elemzés
│   │
│   ├── data/                         # ⚠️ Párhuzamos legacy csomag (providers, city mgmt)
│   │   ├── weather_client*.py        # 3 részre szedett weather client
│   │   ├── city_manager*.py          # 5 részre szedett city manager
│   │   ├── anomaly_profile/          # Anomaly profile management
│   │   ├── geo_utils/                # Geo utilities (core, region)
│   │   └── city_types/, geo_types/   # Type definitions
│   │
│   └── config/                       # ⚠️ Párhuzamos legacy csomag (konfigurációk)
│       ├── api_config.py             # API config (key, host, port)
│       ├── provider_config*.py       # 3 részre szedett provider config
│       ├── usage_config*.py          # 3 részre szedett usage config
│       └── config_*.py               # Settings, validation, paths
│
├── frontend/                         # React 19 + TypeScript frontend (84 .ts/.tsx fájl)
│   ├── src/
│   │   ├── App.tsx                   # ⚡ Routing root (11 route)
│   │   ├── index.tsx                 # ⚡ BELÉPÉSI PONT #2 (React entry)
│   │   ├── pages/                    # 11 page component
│   │   ├── components/               # ~40 reusable component
│   │   ├── services/                 # 3 API service (hungary, provider, trend)
│   │   ├── hooks/                    # 5 custom hook
│   │   └── constants/                # Hungary geo + wind constants (+ tesztekkel)
│   └── build/                        # Lefordított production build
│
├── tests/                            # Python tesztek (211 .py fájl)
│   ├── api/, domain/, application/, infrastructure/  # Clean Arch réteg tesztek
│   ├── data/, analytics/             # Legacy csomag tesztek
│   └── integration/                  # Integrációs tesztek
│
├── scripts/                          # Launch scriptek + utilityk
│   ├── launch_meteo_analytics_frontend.sh    # ⚡ BELÉPÉSI PONT #3 (React dev)
│   ├── launch_meteo_analytics_fullstack.sh   # ⚡ BELÉPÉSI PONT #4 (Full-stack)
│   └── ...
│
├── data/                             # Runtime adatok (nem verziózott)
│   ├── *.db                          # SQLite adatbázisok (cities, meteo_data, hungarian_settlements)
│   ├── geojson/                      # GeoJSON fájlok (counties, postal codes)
│   └── user_preferences/             # Felhasználói preferenciák (JSON)
│
├── docs/, exports/, logs/            # Üres könyvtárak (előre lefoglalva)
│
├── meteo_gui_starter.py              # ⚡ BELÉPÉSI PONT #5 (PySide6 desktop indító)
├── meteo_analytics_*.desktop         # Desktop launcher fájlok
│
├── pyproject.toml                    # Ruff, mypy, pytest, coverage konfiguráció
├── quality_gate.sh                   # Quality gate script (v3.2)
├── .quality_gate.conf                # Threshold-ök (coverage=85, max_lines=300)
├── .importlinter                     # Clean Architecture import contracts
├── .pre-commit-config.yaml           # Pre-commit hook konfiguráció
├── .github/workflows/ci.yml          # GitHub Actions CI pipeline
├── Makefile                          # Make target-ek (check, test, ci, strict)
├── mypy.ini                          # Mypy konfiguráció
├── .pylintrc                         # Pylint (minimal: jobs=1)
├── .coveragerc                       # Coverage konfiguráció
├── requirements.txt                  # Prod függőségek
├── requirements-dev.txt              # Dev függőségek
├── README.md                         # Code Health Toolkit dokumentáció
├── AGENTS.md                         # AI Coding Rules (v2.4)
├── PRODUCTION_MANDATE.md             # Production-ready mandate
├── AUDIT.md                          # Előző audit (2026-03-15, RISK: MEDIUM)
└── AUDIT_PROMPT.md                   # Audit procedure template
```

### 1.2 Belépési pontok (Entry Points)

| # | Név | Útvonal | Típus | Indítás |
|---|-----|---------|-------|---------|
| 1 | FastAPI API | `src/api/main.py` | Backend REST API | `uvicorn src.api.main:app --port 8003` |
| 2 | React Frontend | `frontend/src/index.tsx` → `App.tsx` | Web UI | `npm start` (port 3000) |
| 3 | PySide6 Desktop | `meteo_gui_starter.py` | Desktop GUI | `python3 meteo_gui_starter.py` |
| 4 | Frontend-only launcher | `scripts/launch_meteo_analytics_frontend.sh` | Shell script | `.desktop` fájl |
| 5 | Full-stack launcher | `scripts/launch_meteo_analytics_fullstack.sh` | Shell script | `.desktop` fájl |

### 1.3 Modul/Csomag határok

A projekt **két párhuzamos struktúrát** futtat:

```
┌─────────────────────────────────────────────────────┐
│  CLEAN ARCHITECTURE (formális rétegek)              │
│                                                     │
│  src/domain/    ← Entities, Ports, Value Objects    │
│       ↑                                             │
│  src/application/ ← Use Cases, DTOs, Services       │
│       ↑                                             │
│  src/infrastructure/ ← Repositories, DI Container   │
│       ↑                                             │
│  src/presentation/gui/ ← PySide6 UI                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  PÁRHUZAMOS LEGACY CSOMAGOK (nem réteg-alapú)       │
│                                                     │
│  src/analytics/   ← Multi-city engine (8+ fájl)     │
│  src/data/        ← Weather client, city manager    │
│  src/config/      ← API, provider, usage config     │
│  src/api/         ← FastAPI routes, DTOs, services  │
└─────────────────────────────────────────────────────┘
```

⚠️ **A két struktúra párhuzamosan létezik** — a Clean Architecture rétegek mellett a `src/analytics/`, `src/data/`, `src/config/`, `src/api/` top-level csomagok is aktívan használtak, ami **kettős felelősséget** és **import-útvonalbeli zavart** okoz.

---

## 2. FÜGGŐSÉGTÉRKÉP

### 2.1 Külső függőségek (verzióval)

**Production (`requirements.txt`):**

| Függőség | Verzió | Cél |
|----------|--------|-----|
| geopandas | 1.1.1 | Geo-spatial adatkezelés |
| pandas | 3.0.1 | Adatmanipuláció |
| plotly | 5.24.1 | Interaktív vizualizáció |
| scikit-learn | 1.8.0 | ML/anomaly detection |
| scipy | 1.17.1 | Statisztikai számítások |
| PyQtDarkTheme2 | >=2.1.2 | GUI téma |
| fastapi | (közvetett) | REST API keretrendszer |
| pydantic | (közvetett) | Validáció, DTO-k |
| uvicorn | (közvetett) | ASGI szerver |
| PySide6 | (közvetett) | Desktop GUI |
| PyQt6 | (közvetett) | GUI alap |

**Development (`requirements-dev.txt`):**

| Függőség | Verzió | Cél |
|----------|--------|-----|
| ruff | >=0.8.0 | Linting + formatting |
| mypy | >=1.8.0 | Type checking |
| pytest | >=8.0.0 | Unit testing |
| pytest-cov | >=4.1.0 | Coverage measurement |
| pytest-timeout | >=2.3.1 | Test timeout |
| mutmut | >=2.4 | Mutation testing |
| radon | >=5.0,<6 | Cyclomatic complexity |
| xenon | >=0.9 | Complexity threshold |
| wily | >=1.25 | Code health metrics |
| import-linter | >=2.0 | Architecture enforcement |
| vulture | >=2.11 | Dead code detection |
| bandit | >=1.7.7 | Security scanning |
| detect-secrets | >=1.4 | Secret detection |
| pre-commit | >=3.7 | Git hook management |

**Frontend (`package.json`):**

| Függőség | Verzió | Cél |
|----------|--------|-----|
| react | 19.2.0 | UI framework |
| react-dom | 19.2.0 | DOM renderer |
| react-scripts | 5.0.1 | CRA build tool |
| typescript | 4.9.5 | Type system |
| axios | 1.13.2 | HTTP client |
| react-router-dom | 7.9.6 | Routing |
| recharts | 3.4.1 | Chart library |
| plotly.js-dist-min | 3.3.1 | Chart library |
| leaflet | 1.9.4 | Map library |
| react-leaflet | 5.0.0 | React map wrapper |

### 2.2 Belső modul-függőségek (ki hív kit)

```
                      ┌──────────────────┐
                      │   src/api/main   │  FastAPI entrypoint
                      │   (routes 11db)  │
                      └────┬─────┬───────┘
                           │     │
              ┌────────────┘     └────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│ src/analytics/          │     │ src/infrastructure/         │
│  multi_city_engine_core │     │  container/factories        │
│  multi_city_types       │     │  repositories/city_repo     │
└────────┬────────────────┘     └──────┬──────┬──────────────┘
         │                             │      │
         │              ┌──────────────┘      └──────────┐
         │              ▼                                ▼
         │   ┌──────────────────┐          ┌──────────────────────┐
         │   │ src/data/        │          │ src/config/          │
         │   │  weather_client  │          │  api_config          │
         │   │  city_manager    │          │  provider_config     │
         │   └──────┬───────────┘          └──────────┬───────────┘
         │          │                                  │
         │          ▼                                  │
         │   ┌──────────────────┐                      │
         └──►│ src/domain/      │◄─────────────────────┘
             │  entities        │
             │  ports           │
             │  services        │
             │  value_objects   │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ src/application/ │
             │  use_cases       │
             │  dto             │
             │  services        │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ src/presentation │
             │  gui/ (520+ fájl)│
             └──────────────────┘

             ║ FRONTEND (React) ║
             ║  pages/ (11 db)  ║  ──HTTP──►  /api/*  ──►  src/api/routes/*
             ║  services/ (3db) ║     (port 8003 proxy)
             ║  hooks/ (5 db)   ║
```

### 2.3 Cirkuláris függőség gyanús helyek ⚠️

| # | Helyszín | Típus | Indoklás |
|---|----------|-------|----------|
| 1 | ⚠️ `src/application/use_cases/calculate_trend.py:13` → `src.api.dto.trend_request` | **Application → API rétegsértés** | Az application réteg importál az API rétegből (`TrendAnalysisRequest`), ami Clean Architecture rétegsértés — a DTO-nak application/domain szintűnek kellene lennie |
| 2 | ⚠️ `src/data/weather_client.py` | **Ön-referencia / re-export labirintus** | A `weather_client.py` saját magát re-exportálja: `from src.data.weather_client_extensions import WeatherClientExtensions as WeatherClient`, miközben a `weather_client_extensions` is importálhatja a core-ot — potenciális circular import ha a sorrend változik |
| 3 | ⚠️ `src/data/city_manager.py` | **Ön-referencia / re-export labirintus** | Hasonló pattern: `from .city_manager_stats import CityManagerStats as CityManager` — a legacy fájl csak re-export, de 5+ almodulra hivatkozik |
| 4 | ⚠️ `src/analytics/multi_city_engine_core.py` → `src.infrastructure.container` | **Párhuzamos csomag → Infrastructure bypass** | A `src/analytics/` (nem Clean Arch réteg) közvetlenül az infrastructure container-t hívja, bypass-olva az application réteget |
| 5 | ⚠️ `src/data/geo_utils.py` | **Ön-referencia** | `from src.data.geo_utils import GeoUtils, DistanceCalculator` — a fájl saját magát importálja! (valószínűleg re-export de nagyon zavaró) |
| 6 | ⚠️ `src/data/models.py` | **Ön-referencia** | `from src.data.models import AnalyticsResult` — önmagát importálja, circular import risk |

---

## 3. TECHNOLÓGIAI LELTÁR

### 3.1 Nyelvek, Frameworkök, Infrastruktúra

| Kategória | Technológia | Verzió | Megjegyzés |
|-----------|-------------|--------|------------|
| **Backend nyelv** | Python | 3.12 (runtime), >=3.10 (requirement) | ⚠️ Eltérés a pyproject.toml-ban |
| **API keretrendszer** | FastAPI | (közvetett) | REST API, CORS-mal |
| **GUI framework** | PySide6 / PyQt6 | (közvetett) | Desktop alkalmazás, 520+ fájl |
| **Frontend nyelv** | TypeScript | 4.9.5 | ⚠️ React 19-hez képest elavult |
| **Frontend framework** | React | 19.2.0 | Create React App (react-scripts 5.0.1) |
| **Chart libs** | Recharts 3, Plotly.js 3 | — | Két chart library párhuzamosan |
| **Map lib** | Leaflet 1.9 + react-leaflet 5 | — | Geo-megjelenítés |
| **Adatbázis** | SQLite | (beépített) | 3 DB fájl (cities, meteo_data, settlements) |
| **Data science** | pandas 3.0, scipy 1.17, sklearn 1.8 | — | Analitika, anomaly detection |
| **Geo** | geopandas 1.1 | — | GeoJSON feldolgozás |
| **CI/CD** | GitHub Actions | — | push/PR/dispatch trigger |
| **Pre-commit** | pre-commit 3.7 | — | 14 hook |
| **Quality** | Ruff, Mypy, Xenon, Vulture, Bandit, Import-linter | — | Comprehensive toolchain |

### 3.2 Konfig fájlok és céljuk

| Fájl | Cél | Kulcsfontosságú beállítás |
|------|-----|--------------------------|
| `pyproject.toml` | Projekt meta, Ruff, pytest, coverage | Ruff: E/W/F/I/B/UP/SIM/RUF/C90/C4/ARG/PTH/ERA/PERF/PL/D |
| `mypy.ini` | Type checking | `warn_return_any=True`, pandas/scipy/sklearn ignored |
| `.importlinter` | Clean Architecture enforcement | 3 contract: layers, domain purity, app isolation |
| `.coveragerc` | Coverage config | `fail_under=85`, **GUI excluded!** |
| `.pylintrc` | Pylint (minimális) | `jobs=1` |
| `.pre-commit-config.yaml` | Git hook-ok | ruff, mypy, import-linter, bandit, detect-secrets, pytest |
| `.quality_gate.conf` | Quality gate threshold-ök | coverage=85, max_lines=300 |
| `quality_gate.sh` | Quality gate runner (v3.2) | 8 checkpoint: ruff→mypy→xenon→vulture→import-linter→size→bandit→pytest |
| `Makefile` | Build automation | check, test, ci, strict, coverage, lint, format, typecheck |
| `.github/workflows/ci.yml` | CI pipeline | ruff + mypy + pytest/coverage |
| `tsconfig.json` | TypeScript config | target: es5 ⚠️, skipLibCheck: true ⚠️ |
| `frontend/package.json` | Frontend deps + proxy | proxy → `http://localhost:8003` |
| `.env.example` | Környezeti változók sablon | API kulcs, backend URL |

### 3.3 Test Coverage becslés

| Metrika | Érték |
|---------|-------|
| **Összes Python forrás** | 685 fájl |
| **Összes teszt fájl** | 211 fájl (12 `__init__.py`, ~199 aktív teszt) |
| **Összes teszt eset** | 1582 passed (AUDIT.md szerint) |
| **Össz-coverage** | **90.41%** (≥85% threshold ✅) |
| **Frontend tesztek** | 9 teszt fájl (csak constants + common components) |
| **GUI coverage** | **KIZÁRVA** a `.coveragerc`-ből (`omit=src/presentation/gui/*`) |

**Teszt arányok becslése:**

| Src alcsomag | Becsült lefedettség | Megjegyzés |
|--------------|---------------------|------------|
| `src/domain/` | ~80-85% | Entities + services jól tesztelt, value_objects gyengébb |
| `src/application/` | ~75-80% | Use cases részben tesztelt |
| `src/infrastructure/` | ~74-80% | Repository 74% |
| `src/api/` | ~85-90% | Route-ok jól teszteltek |
| `src/data/` | ~85-90% | Core jól fedett |
| `src/analytics/` | ~80% | Multi-city engine részben |
| `src/presentation/gui/` | **NEM MÉRT** | Kizárva a coverage-ből! 520+ fájl teljesen tesztületlen |
| `src/config/` | ~70-80% | Config validation tesztelt |

---

## 4. AUDIT ELŐKÉSZÍTŐ ÖSSZEFOGLALÓ

### 4.1 Top 3 Architekturális Probléma

| # | Terület | Gyanús hely | Indoklás |
|---|---------|-------------|----------|
| 1 | **Dual Architecture / Párhuzamos csomagok** | ⚠️ `src/analytics/`, `src/data/`, `src/config/` vs Clean Arch rétegek | A projekt Clean Architecture-t hirdet, de a `src/analytics/` (multi-city engine), `src/data/` (weather client, city manager), `src/config/` (provider config) csomagok párhuzamosan léteznek a domain/application/infrastructure rétegekkel. Ugyanaz a felelősség kétszer is megjelenhet. A `MultiCityEngine` például a `src/analytics/`-ben van, de az API route-ok közvetlenül hívják, bypass-olva az application réteget. |
| 2 | **106 `_partN` fájl — Code Splitting Anti-pattern** | ⚠️ `src/` alatt 106 db `*_part*.py` fájl | A fájlok szétvágása `_part1.py`, `_part2.py` suffix-ekkel a 300 soros limit kényszerű megkerülése. Ezek nem önálló felelősségű modulok, hanem egyetlen osztály/függvény mesterséges darabolása (pl. `analytics_transform_service_part2.py`, `city_repository_part1.py`). Ez megnehezíti a navigációt, a comprehension-t és a refactoringot. |
| 3 | **Application réteg → API DTO import** | ⚠️ `src/application/use_cases/calculate_trend.py:13` | A CalculateTrendUseCase importálja a `TrendAnalysisRequest`-t az `src.api.dto`-ból. Ez **Clear Architecture rétegsértés**: az application réteg nem függethet az API rétegtől. A request DTO-nak az application vagy domain rétegben kellene lennie. |

### 4.2 Top 3 Security Kockázat

| # | Terület | Gyanús hely | Indoklás |
|---|---------|-------------|----------|
| 1 | **API Key middleware kettősség** | ⚠️ `src/api/main.py:43-82` | Az API key ellenőrzés egyszerre van megvalósítva FastAPI `Depends()` alapú verify függvénnyel ÉS egy custom `@app.middleware("http")` middleware-ben. A middleware megkerüli a `verify_api_key` függvényt, és közvetlenül hasonlítja össze az API kulcsot. Bár `secrets.compare_digest` biztonságos, a kettős implementáció inkonzisztens hibakezeléshez vezethet (pl. a middleware nem hívja meg a `verify_api_key` logikát). |
| 2 | **Hardcoded API URL a frontendben** | ⚠️ `frontend/src/hooks/useCityWeather.ts:5`, `useMultiYearWeather.ts:5` | Két hook hardcoded `http://localhost:8003` URL-t használ a konfigurációs modul (`apiConfig.ts`) helyett. Ez production deployment-nél hibát okoz, és a kód-review során könnyen elsiklanak felette. |
| 3 | **GUI teljesen kivéve a security auditból** | ⚠️ `.coveragerc` + `quality_gate.sh` GUI exclusion | A `src/presentation/gui/` (520+ fájl) teljesen ki van véve a coverage mérésből. A PySide6 GUI közvetlenül SQLite adatbázishoz fér hozzá (`database_manager_part1.py`, `database_manager_part2.py`), és a `cursor.execute()` hívásoknál a paraméterezés ellenőrzése nem automatizált erre a rétegre. |

### 4.3 Top 3 Teljesítmény Bottleneck Jelölt

| # | Terület | Gyanús hely | Indoklás |
|---|---------|-------------|----------|
| 1 | **CRITICAL komplexitású GUI table model** | ⚠️ `src/presentation/gui/data_widgets/table_model.py:66` — `WeatherTableModel.data()`, **CC=29** | Egy single method 29 cyclomatic complexity-vel extrém nehéz tesztelni, optimalizálni és karbantartani. Ez a GUI adattábla core renderelő logikája, és minden adat-frissítésnél fut. |
| 2 | **Batch weather data fetching loop** | ⚠️ `src/application/use_cases/calculate_trend.py:109-132` | A `_fetch_weather_data()` yearly batch-ekben (365 napos ablakokkal) szinkron HTTP hívásokat végez egy while ciklusban. Több évtizedes trend analízisnél ez **tízszámos szekvenciális API hívás** lehet, időtúllépés és rate limit kockázattal. Nincs párhuzamosítás vagy cache. |
| 3 | **MultiCityEngine közvetlen használata API route-okban** | ⚠️ `src/api/routes/detailed_city.py`, `analytics.py`, `anomalies.py`, `weather.py`, `single_city.py` — mind importálják `MultiCityEngine`-t | Az `src/analytics/multi_city_engine_core.py` (236 LOC) minden API route-ban közvetlenül példányosítva vagy DI container-ből kérve van. Ha az engine belsőleg heavy adatbázis query-ket vagy komplex analitikát végez, akkor **nincs connection pooling, nincs cache, nincs rate limiting** az API réteg és az engine között. |

---

## 5. ÖSSZEGZÉS

| Kategória | Kockázati szint | Kulcsmegállapítás |
|-----------|----------------|-------------------|
| **Architektúra** | 🟡 MEDIUM | Clean Architecture formálisan megvan, de párhuzamos legacy csomagok gyengítik |
| **Kódminőség** | 🔴 HIGH | 106 `_part` fájl, complexity gate bukik, CC=29 a table model-ben |
| **Tesztlefedettség** | 🟡 MEDIUM | 90.41% összcoverage jó, de GUI (520+ fájl) teljesen exclusion alatt van |
| **Biztonság** | 🟢 LOW-MEDIUM | Nincs hardcoded secret, SQL injection nincs, de middleware kettősség aggasztó |
| **Karbantarthatóság** | 🔴 HIGH | 685 src fájl, 520 GUI fájl, dual structure, 106 split file |
| **Teljesítmény** | 🟡 MEDIUM | Szinkron batch fetching, nincs API cache, heavy table model |

### Fájl statisztikák

| Metrika | Érték |
|---------|-------|
| Python source fájlok (`src/`) | 685 |
| `_partN` split fájlok | 106 |
| Python teszt fájlok (`tests/`) | 211 |
| TypeScript/TSX fájlok (`frontend/`) | 84 |
| `__init__.py` fájlok (`src/`) | 91 |
| Összes projekt fájl | ~1,050 |
| Teszt esetek száma | 1,582 passed |

---

*Ez a jelentés a repó teljes statikus elemzésén alapul. Mélyebb audit futtatásához a `quality_gate.sh` és a teljes tesztcsomag futtatása javasolt.*
