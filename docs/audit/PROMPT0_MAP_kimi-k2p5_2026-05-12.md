# meteo-analytics — Struktúratérkép & Audit-előkészítés

Dátum: 2026-05-12 | Model: Kimi K2 Pro

---

## 1. Technológiai leltár

### Programnyelvek és verziók
| Réteg | Nyelv | Verzió |
|---|---|---|
| Backend | Python | 3.12+ (`requires-python = ">=3.12"`) |
| Frontend | TypeScript | 4.9.5 (⚠️ **elavult** — a React 19-hez TypeScript 5.x illene) |

### Runtime és build rendszer
| Eszköz | Backend | Frontend |
|---|---|---|
| Build | `make` (Makefile) + `pip` | `vite` (8.0.10) |
| Package manager | pip (requirements.txt/lock) | npm |
| Task runner | Makefile target-ek | npm scripts |

### Frameworkök és könyvtárak szerepkör szerint

**Backend — Web/API réteg:**
- `fastapi==0.135.1` — REST API framework
- `uvicorn==0.41.0` — ASGI szerver
- `starlette==1.0.0` — ⚠️ extrém alacsony verziószám, a FastAPI 0.135-hez nem illik (valószínűleg placeholder vagy hibás pin)
- `httpx==0.28.1` — async HTTP kliens (időjárás API-hoz)
- `pydantic==2.11.7` — adatvalidáció, DTO-k

**Backend — Adatkezelés / Tudományos:**
- `pandas==3.0.1` — adatmanipuláció
- `numpy==2.4.4` — numerikus számítások
- `geopandas==1.1.2` + `shapely==2.1.2` + `pyogrio==0.12.1` — GIS/mappa adatok
- `matplotlib==3.10.5` + `plotly==5.24.1` — vizualizáció
- `scikit-learn==1.8.0` + `scipy==1.17.1` — statisztikai elemzés

**Backend — GUI (desktop):**
- `PySide6==6.9.1` — Qt alapú desktop alkalmazás
- `PyQtDarkTheme2==2.1.2` — dark theme támogatás

**Backend — Tesztelés:**
- `pytest>=8.0.0`, `pytest-asyncio>=1.1.0`, `pytest-cov>=4.1.0`, `pytest-qt>=4.5.0`, `pytest-timeout>=2.3.1`
- `mutmut>=2.4` — mutation testing

**Backend — Linting / Formázás / CI/CD:**
- `ruff>=0.8.0`, `mypy>=1.8.0`, `pre-commit>=3.7`
- `radon>=5.0`, `xenon>=0.9`, `wily>=1.25` — komplexitás és trendek
- `import-linter>=2.0` — architektúra-ellenőrzés
- `vulture>=2.11`, `bandit>=1.7.7`, `detect-secrets>=1.4`, `pip-audit>=2.6`

**Frontend:**
- `react==19.2.0` + `react-dom==19.2.0` — UI framework
- `react-router-dom==7.9.6` — routing
- `react-leaflet==5.0.0` + `leaflet==1.9.4` — térképes megjelenítés
- `recharts==3.4.1` + `plotly.js-dist-min==3.3.1` — chartok
- `vitest==4.1.5` — teszt runner
- `typescript==4.9.5` — ⚠️ elavult a React 19-hez
- `eslint==9.24.0` + `prettier==3.8.3`

**Infrastruktúra jelei:**
- Docker file nincs a repóban
- `.desktop` fájlok (`meteo_analytics_fullstack.desktop`, `meteo_analytics_frontend.desktop`) — Linux desktop integráció
- GitHub Actions: `ci.yml`, `health-check.yml`, `pre-commit.yml`, `e2e-tests.yml`
- `.env` alapú config kezelés (API kulcsok environment variable-ban)

### Konfiguráció és environment kezelés
- `.env` — aktuális config (API kulcsokat tartalmaz, de placeholder értékekkel)
- `.env.example` — sablon
- `src/config/` moduláris config package (api_config, paths_config, provider_config, usage_config, config_settings, config_validation)
- `src/config.py` — ⚠️ legacy re-export wrapper
- `pyproject.toml` — tool config-ek (ruff, mypy, pytest, coverage, bandit, vulture, mutmut)

---

## 2. Struktúratérkép (annotált könyvtárfa)

```
meteo-analytics/
├── src/                          # Python backend — Clean Architecture
│   ├── domain/                   # [50 fájl, ~5273 LOC] Entitások, portok, value objectek, services
│   │   ├── analytics/            #   Analitikai modellek, repository protokollok, wind services
│   │   ├── constants/            #   Query típusok, régió definíciók
│   │   ├── entities/             #   Domain entitások (City, Location, Weather, AnalyticsResult)
│   │   ├── ports/                #   Abstract interfészek (Clean Architecture boundary)
│   │   ├── services/             #   Domain service-ek (anomaly, trend, wind)
│   │   └── value_objects/        #   Value objectek (enums, threshold-ök)
│   ├── application/              # [15 fájl, ~1232 LOC] Use case-ek, DTO-k, application services
│   │   ├── commands/             #   Trend parancsok
│   │   ├── dto/                  #   Analytics és location DTO-k
│   │   ├── use_cases/            #   Multi-city analízis, trend, anomaly, detailed city
│   │   └── services/             #   Wind analysis service (application szint)
│   ├── infrastructure/           # [9 fájl, ~728 LOC] Külső adapterek, DI container
│   │   ├── adapters/             #   City adapter (weather API illesztés)
│   │   ├── container/            #   Composition root, factory függvények
│   │   └── repositories/         #   City repository implementációk
│   ├── data/                     # [34 fájl, ~4432 LOC] ⚠️ Nem oda való — adatréteg, nem infrastructure
│   │   ├── anomaly_profile/      #   Anomália profil kezelés
│   │   ├── city_manager*.py      #   ⚠️ Több fájl (manager, db, search, stats, demo)
│   │   ├── weather_client*.py    #   Időjárás API kliens + extensions
│   │   ├── *provider*.py         #   Meteostat és OpenMeteo providerek
│   │   ├── geo_utils*.py         #   Földrajzi segédfüggvények
│   │   ├── distance_calculator*.py # Távolság számítás
│   │   └── circuit_breaker.py    #   Resilience pattern
│   ├── config/                   # [9 fájl, ~1381 LOC] Konfigurációs modul (moduláris)
│   │   ├── api_config.py         #   API config (env var-ok, CORS, auth)
│   │   ├── paths_config.py       #   Elérési utak
│   │   ├── provider_config.py    #   Provider selector + user prefs
│   │   ├── usage_config.py       #   Használat követés
│   │   ├── config_settings.py    #   GUI/Hardware/MultiCity/AppInfo
│   │   └── config_validation.py  #   Validáció
│   ├── config.py                 # ⚠️ Legacy re-export wrapper (minden configot innen exportál)
│   ├── api/                      # [25 fájl, ~2290 LOC] FastAPI REST API réteg
│   │   ├── main.py               #   API belépési pont (middleware, auth, route regisztráció)
│   │   ├── routes/               #   Route-ok (weather, cities, analytics, anomalies, providers, wind_rose, hungary, metadata, single_city, detailed_city)
│   │   ├── services/             #   ⚠️ API service (provider_usage_service — singleton)
│   │   ├── middleware/           #   Rate limiting
│   │   ├── dto/                  #   Request/Response DTO-k
│   │   └── adapters/             #   Weather adapter (DTO → domain konverzió)
│   ├── analytics/                # [13 fájl, ~947 LOC] Multi-city analitikai modul
│   │   ├── multi_city_engine*.py #   ⚠️ Több változat: core, legacy, query_types, region_ops, result_factory
│   │   └── ports/                #   Analytics portok
│   └── presentation/             # [460 fájl, ~49198 LOC] ⚠️ MASSZÍV — GUI + API presentation
│       ├── gui/                  #   PySide6 desktop alkalmazás
│       │   ├── windows/          #     MainWindow és kiegészítők
│       │   ├── controller/       #     AppController, database_manager, geocoding_handler
│       │   ├── charts/           #     Base, comparison, heatmap, precipitation, temperature, wind, wind_rose, windy_days chartok
│       │   ├── analytics/        #     Analytics view, statistics, tabs, widgets
│       │   ├── panels/           #     Eredmény panelek (quick_overview, extreme, windy_days, data_table, tab_manager)
│       │   ├── dialogs/          #     Anomaly settings, calculation
│       │   ├── hungarian_city_selector/   #   Magyar település választó
│       │   ├── hungarian_location_selector/#  Magyar helyválasztó
│       │   ├── hungarian_map_tab/         #   Magyar térkép tab
│       │   ├── universal_location_selector/#  Univerzális helyválasztó
│       │   ├── trend_analytics/           #   Trend analitika
│       │   ├── map/                       #   Folium térkép rendering
│       │   ├── map_view/                  #   Térkép nézet
│       │   ├── color_palette/             #   Színpaletta kezelés (14 fájl! ⚠️)
│       │   ├── theme_manager/             #   Téma kezelés
│       │   ├── workers/                   #   Background worker-ek
│       │   ├── panel_widgets/             #   Vezérlő widgetek
│       │   ├── utils/                     #   Segédfüggvények
│       │   ├── weather_data_bridge/       #   Adat híd GUI és backend között
│       │   ├── data_widgets/              #   Adat megjelenítő widgetek
│       │   ├── chart_container/           #   Chart konténer
│       │   ├── cleanup_manager.py         #   Erőforrás tisztítás
│       │   └── signal_manager.py          #   Qt signal kezelés
│       └── api/                           # ⚠️ Üres init — API presentation itt lenne, de az api/ alatt van
│
├── frontend/                     # React + TypeScript + Vite frontend
│   ├── src/                      # [88 TS/TSX fájl, ~18378 LOC]
│   │   ├── components/           #   UI komponensek (analytics, charts, common, maps, panels)
│   │   ├── pages/                #   Oldal nézetek (11 oldal)
│   │   ├── hooks/                #   Custom React hook-ok
│   │   ├── services/             #   API kliens, Hungary, provider, trend service-ek
│   │   ├── config/               #   Frontend config
│   │   ├── contexts/             #   Theme context
│   │   ├── constants/            #   Hungary és wind konstanok
│   │   ├── types/                #   TypeScript típusok
│   │   └── utils/                #   Extreme calculator, logger
│   ├── package.json              #   NPM függőségek
│   ├── vite.config.ts            #   Vite konfiguráció
│   ├── vitest.config.ts          #   Vitest konfiguráció
│   ├── tsconfig.json             #   TypeScript konfiguráció
│   └── eslint.config.js          #   ESLint konfiguráció
│
├── tests/                        # Python tesztek (~238 fájl)
│   ├── analytics/                #   Analytics tesztek
│   ├── api/                      #   API route, middleware, auth tesztek
│   ├── application/              #   Use case, service, DTO tesztek
│   ├── config/                   #   Config modul tesztek
│   ├── domain/                   #   Domain entity, service, port tesztek
│   ├── gui/                      #   GUI tesztek (⚠️ CI-ban ignored)
│   ├── infrastructure/           #   Infrastructure/container tesztek
│   ├── data/                     #   ⚠️ Nincs data/ teszt könyvtár — data layer teszteletlen
│   └── test_*.py                 #   Top-level tesztek (config, city, provider, weather, stb.)
│
├── data/                         # Adatbázisok és statikus adatok
│   ├── meteo_data.db             #   Időjárási adatbázis (SQLite)
│   ├── hungarian_settlements.db  #   Magyar települések adatbázis
│   ├── cities.db                 #   Város adatbázis
│   ├── geojson/                  #   GeoJSON fájlok (counties, postal_codes)
│   └── user_preferences/         #   Felhasználói preferenciák (JSON)
│
├── scripts/                      # Helper scriptek
│   ├── dev.sh                    #   Fejlesztői indító
│   ├── launch_meteo_analytics_*.sh # GUI és fullstack indítók
│   ├── install_hooks.sh          #   Git hook telepítő
│   ├── gui_audit.py              #   GUI audit script
│   ├── test_*.py                 #   Flow tesztek
│   └── ultimate_project_analyzer.py # Projekt elemző
│
├── .github/workflows/            # CI/CD
│   ├── ci.yml                    #   Alap CI (lint, test, coverage)
│   ├── health-check.yml          #   Teljes health check (multi-python, security, coverage)
│   ├── pre-commit.yml            #   Pre-commit hook CI-ban
│   └── e2e-tests.yml             #   E2E tesztek
│
├── pyproject.toml                # Python projekt konfiguráció
├── Makefile                      # Build/quality automation
├── quality_gate.sh               # Minőségi kapu script (backend + frontend)
├── requirements.txt              # Production függőségek
├── requirements-dev.txt          # Fejlesztői függőségek
├── requirements.lock             # ⚠️ Lock file — de nincs pip-tools vagy uv használva a Makefile-ban
├── .env / .env.example           # Environment konfiguráció
├── .pre-commit-config.yaml       # Pre-commit hookok
├── .importlinter                 # Import architektúra szabályok
├── .pylintrc / .mypy.ini         # ⚠️ MyPy config felülírhatja a pyproject.toml-t
├── .secrets.baseline             # Secrets scan baseline
├── .ruff_cache/                  # Ruff cache
├── .mypy_cache/                  # MyPy cache
├── .pytest_cache/                # Pytest cache
├── .coverage / coverage.xml      # Coverage riportok
├── meteo_gui_starter.py          # ⚠️ Top-level GUI belépési pont (deprecated?)
├── README.md                     # Projekt dokumentáció
├── PRODUCTION_MANDATE.md         # Production követelmények
├── REFACTOR_PLAN.md              # Refaktor terv
├── AGENTS.md                     # AI agent utasítások
└── .codex/                       # Codex config
```

### ⚠️ "Nem oda való" tartalmú könyvtárak

| Könyvtár | Probléma |
|---|---|
| `src/data/` | Clean Architecture szerint ez az `infrastructure` layer lenne. 34 fájl, 4432 LOC — jelentős réteg, ami nincs a nevében jelölve. Az import-linter config-ban `data | infrastructure` együtt van kezelve, de ez architektúrális inkonzisztencia. |
| `src/config.py` | Legacy re-export wrapper, ami shadow-olja a `src/config/` package-t. |
| `src/presentation/` | 460 fájl, ~49K LOC — a teljes projekt ~75%-a itt van. Ez egy GUI rétegnek aránytalanul nagy. |
| `src/analytics/` | Párhuzamos multi-city engine létezik itt (`multi_city_engine*.py`) ÉS az `application/use_cases/`-ben is — ⚠️ duplikáció vagy átmeneti állapot. |
| `src/api/services/provider_usage_service.py` | Singleton service az API layerben — a service-eknek az application vagy domain layerben kellene lenniük. |
| `frontend/src/components/analytics/*Heatmap.tsx` | 6 hőérkélet chart komponens külön — lehetne egyesíteni. |

### Projekt méret becslés

| Metrika | Érték |
|---|---|
| Python forrásfájlok (src/) | ~615 fájl |
| Python LOC (src/) | ~64 482 LOC |
| TypeScript forrásfájlok (frontend/) | ~88 fájl |
| TypeScript LOC (frontend/) | ~18 378 LOC |
| Tesztfájlok | ~238 fájl |
| Test/Forrás arány | ~238/615 = **~0.39** (alacsony — a presentation layer-hez nagyon kevés teszt látható) |
| Összes LOC (kód) | ~83 000+ |
| Összes fájl (kód + config) | ~941+ |

---

## 3. Belépési pont leltár

### CLI entrypointok

| Fájl | Szerep | Flow-k | Kanonikus? |
|---|---|---|---|
| `meteo_gui_starter.py` | PySide6 desktop app bootstrap | GUI indítás, config ellenőrzés, MainWindow létrehozás | ⚠️ Legacy — a `meteo_analytics_gui.desktop` hivatkozik rá, de a fő app itt van |
| `scripts/launch_meteo_analytics_fullstack.sh` | Fullstack indító (API + GUI) | Backend API + Desktop GUI együttes indítása | ⚠️ Nem kanonikus — script wrapper |
| `scripts/launch_meteo_analytics_frontend.sh` | Frontend indító | Vite dev szerver indítása | ⚠️ Nem kanonikus — script wrapper |
| `scripts/dev.sh` | Fejlesztői indító | Fejlesztői környezet setup | ⚠️ Nem kanonikus |

### API / Web entrypointok

| Fájl | Szerep | Route-ok | Kanonikus? |
|---|---|---|---|
| `src/api/main.py` | FastAPI alkalmazás | Összes route regisztrálása, middleware-ek, auth | ✅ Kanonikus |
| `src/api/routes/weather.py` | Időjárás analízis API | POST `/api/weather/multi-city` | ✅ |
| `src/api/routes/analytics.py` | Analitikai route-ok | GET/POST analitika endpointok | ✅ |
| `src/api/routes/anomalies.py` | Anomália detektálás | GET/POST anomaly endpointok | ✅ |
| `src/api/routes/cities.py` | Város kezelés | GET/POST város endpointok | ✅ |
| `src/api/routes/detailed_city.py` | Részletes város adatok | GET detailed city | ✅ |
| `src/api/routes/hungary.py` | Magyar települések | GET Hungary endpointok | ✅ |
| `src/api/routes/metadata.py` | Metaadat endpointok | GET metadata | ✅ |
| `src/api/routes/providers.py` | Provider kezelés | GET/POST provider endpointok | ✅ |
| `src/api/routes/single_city.py` | Egyvárosos analízis | POST single city | ✅ |
| `src/api/routes/wind_rose.py` | Szélrózsa analízis | GET wind rose (3 részre bontva) | ⚠️ Part1/2/3 fájlokra bontva |
| `src/api/routes/wind_rose_part1.py` | Szélrózsa support | Support functions | ⚠️ Nem önálló entrypoint |
| `src/api/routes/wind_rose_part2.py` | Szélrózsa support | Support functions | ⚠️ Nem önálló entrypoint |
| `src/api/routes/wind_rose_part3.py` | Szélrózsa support | Support functions | ⚠️ Nem önálló entrypoint |

### Frontend (React) entrypoint

| Fájl | Szerep | Kanonikus? |
|---|---|---|
| `frontend/src/index.tsx` | React app bootstrap (ReactDOM.createRoot) | ✅ |
| `frontend/src/App.tsx` | Router + layout koordináció | ✅ |

### Background job / Worker entrypointok

| Fájl | Szerep | Flow-k | Kanonikus? |
|---|---|---|---|
| `src/presentation/gui/workers/analysis_worker/core.py` | GUI analysis worker | Aszinkron analízis futtatás Qt threadben | ⚠️ GUI specifikus |
| `src/presentation/gui/workers/base_worker.py` | Alap worker osztály | Worker életciklus kezelés | ⚠️ GUI specifikus |
| `src/presentation/gui/workers/weather_data_worker/api_builder.py` | Időjárás API worker | API request építés és futtatás | ⚠️ GUI specifikus |
| `src/presentation/gui/workers/geocoding_worker.py` | Geokódoló worker | Cím → koordináta konverzió | ⚠️ GUI specifikus |
| `src/presentation/gui/workers/sql_query_worker.py` | SQL query worker | Adatbázis lekérdezések | ⚠️ GUI specifikus |

### Use case entrypointok

| Fájl | Szerep | Flow-k | Kanonikus? |
|---|---|---|---|
| `src/application/use_cases/analyze_multi_city.py` | Multi-city analízis | Városok batch időjárás elemzése | ✅ Kompozíciós gyökér: `infrastructure/container/composition_root.py` |
| `src/application/use_cases/calculate_trend.py` | Trend számítás | Idősor trend analízis | ✅ |
| `src/application/use_cases/detailed_city_use_case.py` | Részletes város analízis | Egy város mélyreható elemzése | ✅ |
| `src/application/use_cases/detect_anomalies.py` | Anomália detektálás | Kiugró értékek azonosítása | ✅ |
| `src/application/commands/trend_command.py` | Trend parancs | CLI trend számítás | ✅ |

### Script entrypointok

| Fájl | Szerep | Flow-k | Kanonikus? |
|---|---|---|---|
| `scripts/test_fetch_flow.py` | Teszt fetch flow | API tesztelés | ⚠️ Nem kanonikus |
| `scripts/test_city_name_flow.py` | Teszt város név flow | Város név feloldás teszt | ⚠️ Nem kanonikus |
| `scripts/gui_audit.py` | GUI audit | GUI állapotfelmérés | ⚠️ Nem kanonikus |
| `scripts/ultimate_project_analyzer.py` | Projekt elemzés | Kódelemzés | ⚠️ Nem kanonikus |
| `run_health_check.sh` | Health check | CI health pipeline | ✅ |

### Kvázi-entrypointok (tesztekből hívva)

| Fájl | Szerep | Megjegyzés |
|---|---|---|
| `src/analytics/multi_city_engine.py` | Multi-city engine (eredeti) | ⚠️ Párhuzamosan létezik az `application/use_cases/analyze_multi_city.py`-val |
| `src/analytics/multi_city_engine_core.py` | Multi-city engine (core) | ⚠️ Szintén párhuzamos implementáció |
| `src/analytics/multi_city_legacy.py` | Legacy multi-city | ⚠️ Explicit legacy jelölés, de még mindig importálható |

---

## 4. Belső függőségtérkép

### Fő hívási irányok

```
presentation/gui (PySide6 desktop app)
    ↓ hívja
application/use_cases (MultiCity, Trend, Anomaly, DetailedCity)
    ↓ hívja
domain/services (AnalyticsTransform, RegionResolver, WeatherFetch, WindAnalysis)
    ↓ hívja
infrastructure/container/factories (port implementációk gyártása)
    ↓ hívja
data/* (CityManager, WeatherClient, AnomalyProfile, MeteostatProvider, OpenMeteoProvider)

api/main.py (FastAPI)
    ↓ regisztrálja
api/routes/* (weather, cities, analytics, anomalies, providers, hungary, wind_rose)
    ↓ hívja
application/use_cases (compose-on keresztül)
    ↓ hívja
domain/services → data/* (ugyanaz a lánc mint fent)

frontend/src (React SPA)
    ↓ HTTP hívások
api/routes/* (FastAPI backend)
```

### ⚠️ Gyanús cirkuláris függőségek

1. **`src/config.py` → `src/config/*` → `src/config.py`**: A gyökér `config.py` re-exportálja a `config/` package tartalmát, de a `config/` almodulok is importálhatnak egymáson keresztül a gyökérből. ⚠️

2. **`src/analytics/multi_city_engine.py` ↔ `src/application/use_cases/analyze_multi_city.py`**: Két párhuzamos multi-city implementáció létezik. Az egyik használhatja a másikat, ami cirkuláris hívási láncot eredményezhet. ⚠️

3. **`src/presentation/gui/*` → `src/data/*`**: A presentation layer közvetlenül hívja a data layert, megkerülve az application és domain rétegeket. Ez Clean Architecture szabályzatot sért. ⚠️

4. **`src/data/weather_client.py` → `src/config.py`**: A data layer importálja a configot, ami rendben van, DE a config importálhat data-s dolgokat (backward compatibility), ami cirkuláris lehet. ⚠️

### Implicit globális állapotok / singleton-ok

| Hely | Típus | Kockázat |
|---|---|---|
| `src/api/services/provider_usage_service.py:203` | `_usage_service = ProviderUsageService()` | Globális singleton instance, thread-safety kérdéses |
| `src/config.py:101` | `ensure_directories()` hívás import időben | Side-effect import közben — fájlok létrejöttek importkor |
| `src/config/__init__.py:82` | `datetime = _datetime` | Modul szintű változó felülírás backward compatibility miatt |
| `src/presentation/gui/theme_manager/core.py` | Singleton téma kezelés | Globális UI állapot |
| `src/presentation/gui/charts/tooltip_mixin/__init__.py` | Singleton tooltip | Globális tooltip instance |
| `src/data/city_manager.py` | Globális város menedzser | ⚠️ Nem egyértelmű, hogy singleton-e |

### Shared util-on át rejtett coupling

| Util | Hol használják | Coupling jelleg |
|---|---|---|
| `src/presentation/gui/utils/initialization.py` | Számos GUI modul | Közös inicializációs logika — ha változik, sok helyen érint |
| `src/presentation/gui/utils/validation/constants_validators.py` | GUI validációk | Közös validációs logika |
| `src/presentation/gui/utils/formatting/formatters.py` | GUI megjelenítés | Közös formázás |
| `src/presentation/gui/signal_manager.py` | Qt signal kezelés | Minden GUI komponens ezt használja |
| `src/config/api_config.py` | Minden API és config hívás | Központi config — változás minden réteget érint |

---

## 5. Külső függőségek

### Direkt production függőségek (requirements.txt)

| Csomag | Verzió | Szerep | Megjegyzés |
|---|---|---|---|
| `fastapi` | 0.135.1 | Web API framework | ✅ Aktív |
| `uvicorn` | 0.41.0 | ASGI szerver | ✅ Aktív |
| `starlette` | 1.0.0 | ASGI toolkit | ⚠️ Gyanúsan alacsony verzió — FastAPI 0.135-hez starlette 0.45+ illene |
| `httpx` | 0.28.1 | Async HTTP kliens | ✅ Aktív |
| `pydantic` | 2.11.7 | Adatvalidáció | ✅ Aktív |
| `pandas` | 3.0.1 | Adatmanipuláció | ✅ Új major verzió |
| `numpy` | 2.4.4 | Numerikus | ✅ Aktív |
| `scipy` | 1.17.1 | Tudományos számítás | ✅ |
| `scikit-learn` | 1.8.0 | ML | ✅ |
| `matplotlib` | 3.10.5 | Vizualizáció | ✅ |
| `plotly` | 5.24.1 | Interaktív chartok | ✅ |
| `geopandas` | 1.1.2 | GIS | ✅ |
| `shapely` | 2.1.2 | Geometriai műveletek | ✅ |
| `pyogrio` | 0.12.1 | Geo IO | ✅ |
| `pyproj` | 3.7.2 | Vetületi transzformáció | ✅ |
| `PySide6` | 6.9.1 | Qt GUI framework | ✅ |
| `darkdetect` | 0.7.1 | Rendszer téma érzékelés | ✅ |
| `tenacity` | 9.1.4 | Retry decorator | ✅ |
| `PyQtDarkTheme2` | 2.1.2 | Dark theme | ✅ |

### Dev-only / build-time függőségek

| Csomag | Verzió | Megjegyzés |
|---|---|---|
| `pytest` | >=8.0.0 | ✅ |
| `pytest-asyncio` | >=1.1.0 | ✅ |
| `pytest-cov` | >=4.1.0 | ✅ |
| `pytest-qt` | >=4.5.0 | ✅ Qt GUI tesztekhez |
| `pytest-timeout` | >=2.3.1 | ✅ |
| `mutmut` | >=2.4 | ✅ Mutation testing |
| `ruff` | >=0.8.0 | ✅ |
| `mypy` | >=1.8.0 | ✅ |
| `radon` | >=5.0,<6 | ✅ |
| `xenon` | >=0.9 | ✅ |
| `wily` | >=1.25 | ✅ |
| `import-linter` | >=2.0 | ✅ |
| `vulture` | >=2.11 | ✅ |
| `bandit` | >=1.7.7 | ✅ |
| `detect-secrets` | >=1.4 | ✅ |
| `pip-audit` | >=2.6 | ✅ |
| `pre-commit` | >=3.7 | ✅ |
| `types-requests` | >=2.31.0 | ✅ |

### Frontend függőségek (package.json)

| Csomag | Verzió | Megjegyzés |
|---|---|---|
| `react` | 19.2.0 | ✅ Legújabb |
| `react-dom` | 19.2.0 | ✅ |
| `react-router-dom` | 7.9.6 | ✅ |
| `typescript` | 4.9.5 | ⚠️ Elavult — React 19 + Vite 8 mellett TS 5.x kellene |
| `vite` | 8.0.10 | ✅ |
| `vitest` | 4.1.5 | ✅ |
| `recharts` | 3.4.1 | ✅ Új major |
| `leaflet` | 1.9.4 | ✅ |
| `react-leaflet` | 5.0.0 | ✅ |
| `axios` | 1.13.2 | ⚠️ Lehetne fetch API (modernebb) |
| `plotly.js-dist-min` | 3.3.1 | ✅ |

### ⚠️ Meglepő / kockázatos függőségek

| Csomag | Miért? |
|---|---|
| `starlette==1.0.0` | A FastAPI 0.135.1-hez ez a verzió inkonzisztensnek tűnik. A FastAPI a Starlette-en alapul, és ez az alverzió nem létezik a valóságban (starlette latest ~0.45). ⚠️ **Kritikus** — valószínűleg hibás pin vagy custom build. |
| `typescript==4.9.5` | React 19-hez TypeScript 5.0+ szükséges. A 4.9.5 nem támogatja a React 19 típusait. ⚠️ |
| `axios==1.13.2` | Modern böngészőkben a `fetch` API elérhető, az axios redundáns lehet. |
| `pandas==3.0.1` | ⚠️ Nagyon új major verzió — előfordulhatnak breaking change-ek a kódbázisban. |
| `pydantic==2.11.7` + `pydantic_core==2.33.2` | Pydantic v2 új, a v1-ről migrált kódban maradhatnak v1-es pattern-ek. |

---

## 6. Test coverage becslés

### Tesztfájlok száma és típusa

| Kategória | Fájlok száma | Típus |
|---|---|---|
| Backend tesztek | ~238 | Unit + integrációs |
| Frontend tesztek | ~10 (becsült a komponens alapú `.test.tsx` fájlokból) | Unit |
| **Összesen** | **~248** | |

### Teszt típusok láthatósága

| Típus | Van? | Megjegyzés |
|---|---|---|
| Unit tesztek | ✅ | `test_*.py` fájlok, `*.test.tsx` fájlok |
| Integrációs tesztek | ✅ | `test_*_integration.py`, API route tesztek |
| E2E tesztek | ⚠️ | `.github/workflows/e2e-tests.yml` létezik, de nem láthatóak a tényleges E2E tesztfájlok |
| Mutation tesztek | ✅ | `mutmut` konfigurálva, de nem automatikus |
| GUI tesztek | ⚠️ | `pytest-qt` jelen van, de a CI-ban `--ignore=tests/gui` — a GUI tesztek **nincsenek futtatva CI-ban**! |

### ⚠️ Teszeletlen területek

| Terület | Miért teszeletlen? | Kockázat |
|---|---|---|
| `src/presentation/gui/` (~49K LOC) | CI-ban `--ignore=tests/gui` flag. 460 fájlból csak ~238 tesztfájl van, és azok nagy része nem GUI. | **Magas** — a kód ~75%-a teszeletlen CI-ban |
| `src/data/` (34 fájl) | Nincs külön `tests/data/` könyvtár. A data layer funkciói a domain és application teszteken keresztül vannak érintve, de közvetlen tesztek nincsenek. | **Közepes** |
| `src/analytics/multi_city_legacy.py` | Legacy modul — valószínűleg deprecated, de nem lett eltávolítva. | **Alacsony** (ha tényleg legacy) |
| `scripts/*.py` | Helper scriptek — egyikre sincs teszt. | **Alacsony** |
| `src/config.py` (legacy re-export) | A re-export wrapper-re nincs külön teszt. | **Alacsony** |
| Frontend services | `apiClient.ts`, `hungaryService.ts`, `providerService.ts`, `trendService.ts` — nincs direkt tesztjük. | **Közepes** |
| Frontend hooks | `useCityWeather.ts`, `useModal.ts`, `useMultiYearWeather.ts`, `useProviderManagement.ts`, `useTrendAnalytics.ts` — hook tesztek nincsenek. | **Közepes** |

### Coverage arány becslés

| Réteg | Becsült coverage | Megjegyzés |
|---|---|---|
| domain | ~85%+ | Jól tesztelt, port-alapú |
| application | ~80%+ | Use case-ek tesztelve |
| infrastructure | ~70%+ | Container factory-k tesztelve |
| data | ~40-60% | ⚠️ Közvetlen tesztek nélkül |
| config | ~70%+ | Config validation tesztelve |
| api | ~75%+ | Route-ok tesztelve |
| presentation/gui | ~10-20% | ⚠️ CI-ban teljesen figyelmen kívül hagyva |
| analytics | ~60%+ | Multi-city engine részben tesztelve |
| frontend | ~50-60% | Komponens tesztek vannak, de nem teljes |

---

## 7. Audit-előkészítő összefoglaló

### Top 3 logikai / architekturális kockázat (Prompt 1 számára)

| # | Cím | Magyarázat | Érintett fájlok |
|---|---|---|---|
| 1 | **Duplikált multi-city engine** | Két külön implementáció létezik: `src/analytics/multi_city_engine*.py` és `src/application/use_cases/analyze_multi_city.py`. Ez inkonzisztens viselkedést, karbantartási duplázást és nehézkes bug-keresést eredményez. | `src/analytics/multi_city_engine.py`, `src/analytics/multi_city_engine_core.py`, `src/analytics/multi_city_legacy.py`, `src/application/use_cases/analyze_multi_city.py` |
| 2 | **Presentation layer túlméretezett** | `src/presentation/` 460 fájl, ~49K LOC — a teljes backend kód ~75%-a. A GUI réteg tartalmaz üzleti logikát (pl. `analysis_handler`, `weather_data_handler`, `trend_data_processor`), ami a domain/application layerben kellene legyen. | `src/presentation/gui/controller/`, `src/presentation/gui/analytics/`, `src/presentation/gui/trend_analytics/` |
| 3 | **Data layer nincs Clean Architecture-ban** | `src/data/` 34 fájlos könyvtár, ami infrastructure funkcionalitást lát el, de külön könyvtárban van. Az import-linter workaround-olja (`data | infrastructure` együtt), de a presentation layer közvetlenül importálja a data-t, megkerülve az application réteget. | `src/data/`, `src/presentation/gui/workers/weather_data_worker/`, `src/presentation/gui/controller/provider_routing.py` |

### Top 3 biztonsági kockázat (Prompt 2 számára)

| # | Cím | Magyarázat | Érintett fájlok |
|---|---|---|---|
| 1 | **API key middleware nem átfogó** | Az auth middleware csak a nem-public path-ekre fut, de a `/docs` és `/openapi.json` endpointok development módban nyilvánosak. A middleware-ben van egy korai visszatérés `OPTIONS` requestekre is, ami CSRF sebezhetőséget okozhat. | `src/api/main.py:126-161`, `src/api/main.py:118-123` |
| 2 | **Globális singleton provider usage service thread-safety kérdése** | A `ProviderUsageService` singleton `_usage_data` dict-je nincs szinkronizálva, miközben a FastAPI async környezetben fut. Párhuzamos requestek esetén race condition léphet fel. | `src/api/services/provider_usage_service.py:35-37,203` |
| 3 | **`.env` fájl a repóban van** | A `.env` fájl nem került fel a `.gitignore`-ra (vagy mégis, de a CI-ban nem védett). Placeholder értékek vannak benne, de a struktúra itself information disclosure. | `.env`, `.gitignore` |

### Top 3 teljesítmény-bottleneck jelölt (Prompt 3 számára)

| # | Cím | Magyarázat | Érintett fájlok |
|---|---|---|---|
| 1 | **Multi-city fetch szinkron threadpool-ban** | A `WeatherFetchService` 8 worker-rel fut, de a fetch művelet szinkron (`run_in_threadpool`-ba csomagolva). Nagy városlisták esetén ez memory és CPU bottleneck lehet. | `src/infrastructure/container/composition_root.py:27-32`, `src/domain/analytics/services/weather_fetch_service.py` |
| 2 | **Presentation layer modul felosztások (`_part1`, `_part2`)** | Számos fájl van `_part1`, `_part2` jelöléssel (pl. `wind_rose_part1.py`, `analytics_tabs_part1.py`, `tooltip_part1.py`). Ez azt jelzi, hogy az eredeti fájlok túl nagyok voltak, de a szétbontás nem csökkenti a betöltési időt — sőt, a modulok közti import overhead növelheti. | `src/api/routes/wind_rose_part*.py`, `src/presentation/gui/analytics/analytics_tabs_part*.py`, `src/presentation/gui/charts/precipitation_chart/tooltip_part*.py` |
| 3 | **GeoJSON és térkép adatok betöltése** | A `hungaryCounties.geojson.ts` beágyazott GeoJSON adat a frontend bundle-ban van, nem externalizálva. Ez növeli a JS bundle méretét és lassítja az első betöltést. | `frontend/src/components/maps/hungaryCounties.geojson.ts` |
