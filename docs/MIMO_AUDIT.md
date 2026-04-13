# Meteo Analytics — Architektúra Audit Előkészítő Elemzés

**Készült:** 2026-04-07
**Modell:** MIMO-v2-pro
**Scope:** Teljes repo feltérképezése, struktúra/függőség/technológia/audit előkészítés

---

## 1. Struktúratérkép

### Könyvtárfa annotálva

```
meteo-analytics/
├── src/                          # Fő forráskód (685 .py fájl, ~67k sor)
│   ├── domain/                   # 🏛️ Domain layer (51 fájl, 4903 sor)
│   │   ├── entities/             #   Entitások: CityInfo, Location, Weather, Analysis
│   │   ├── value_objects/        #   Enum-ok, AnomalyThreshold
│   │   ├── analytics/            #   Wind analysis, trend calculator, statistics
│   │   ├── services/             #   Anomaly detector
│   │   └── ports/                #   Abstract port interfaces (Clean Arch)
│   │
│   ├── application/              # 📋 Application layer (13 fájl, 1025 sor)
│   │   ├── use_cases/            #   AnalyzeMultiCity, CalculateTrend, DetectAnomalies
│   │   ├── dto/                  #   AnalyticsDTO, LocationDTO
│   │   └── services/             #   WindAnalysisService
│   │
│   ├── api/                      # 🌐 FastAPI backend (25 fájl, 2608 sor)
│   │   ├── main.py               #   ★ BELÉPÉSI PONT: FastAPI app, CORS, API key auth
│   │   ├── routes/               #   10+ router (weather, analytics, anomalies, cities, etc.)
│   │   ├── dto/                  #   Request/Response DTO-k
│   │   ├── adapters/             #   Weather adapter
│   │   └── services/             #   ProviderUsageService
│   │
│   ├── data/                     # 💾 Data layer (39 fájl, 4522 sor)
│   │   ├── city_manager*.py      #   City search, stats, geo utils
│   │   ├── weather_client*.py    #   HTTP client, caching, provider abstraction
│   │   ├── openmeteo_provider/   #   Open-Meteo API adapter (FREE)
│   │   ├── meteostat_provider/   #   Meteostat API adapter (PAID/RapidAPI)
│   │   ├── anomaly_profile/      #   Anomaly settings persistence
│   │   └── user_preferences/     #   User prefs persistence
│   │
│   ├── infrastructure/           # 🔧 Infrastructure (8 fájl, 633 sor)
│   │   ├── container/            #   DI factory functions (get_*_port())
│   │   ├── adapters/             #   CityAdapter
│   │   └── repositories/         #   CityRepository (DB queries)
│   │
│   ├── config/                   # ⚙️ Configuration (13 fájl, 1375 sor)
│   │   ├── api_config.py         #   API endpoints, keys, rate limits
│   │   ├── paths_config.py       #   Directory paths, DB paths
│   │   ├── provider_config.py    #   Provider selection, user prefs
│   │   ├── usage_config.py       #   API usage tracking
│   │   └── config_settings.py    #   GUIConfig, HardwareConfig, AppInfo
│   │
│   ├── analytics/                # 📊 Multi-city analytics engine (13 fájl, 1100 sor)
│   │   ├── multi_city_engine*.py #   Multi-city comparison engine
│   │   └── ports/                #   Analysis port interfaces
│   │
│   └── presentation/             # 🖥️ GUI - PySide6 (522 fájl, 51319 sor) ⚠️
│       ├── gui/
│       │   ├── windows/          #   MainWindow
│       │   ├── controller/       #   AppController, handlers
│       │   ├── charts/           #   8 chart típus (temp, precip, wind, heatmap, etc.)
│       │   ├── control_panel/    #   Input controls
│       │   ├── results_panel/    #   Results display tabs
│       │   ├── dialogs/          #   AnomalySettings, ExtremeWeather
│       │   ├── map/              #   Map visualization
│       │   ├── widgets/          #   Panel widgets
│       │   └── workers/          #   QThread workers
│       └── api/                  #   (üres vagy minimal)
│
├── frontend/                     # ⚛️ React frontend (84 fájl, 17875 sor)
│   └── src/
│       ├── components/           #   React komponensek (Heatmap, Charts, Forms)
│       ├── hooks/                #   useCityWeather custom hook
│       ├── constants/            #   Magyar megyék, szél konstansok
│       └── services/             #   API service layer
│
├── tests/                        # 🧪 Backend tesztek (211 .py fájl, 24484 sor)
├── data/                         # 📁 Adatbázisok + GeoJSON (22MB+)
├── scripts/                      # 🔨 Segédscriptek
├── meteo_gui_starter.py          # ★ BELÉPÉSI PONT: PySide6 GUI indító
└── [config fájlok]               #   Makefile, pyproject.toml, requirements*.txt
```

### Kódméret eloszlás (rétegenként)

| Réteg | Fájlok | Sorok | Arány |
|-------|--------|-------|-------|
| `presentation/gui/` | 522 | 51,319 | **76.1%** |
| `domain/` | 51 | 4,903 | 7.3% |
| `data/` | 39 | 4,522 | 6.7% |
| `api/` | 25 | 2,608 | 3.9% |
| `config/` | 13 | 1,375 | 2.0% |
| `analytics/` | 13 | 1,100 | 1.6% |
| `application/` | 13 | 1,025 | 1.5% |
| `infrastructure/` | 8 | 633 | 0.9% |

### Belépési pontok

| Pont | Fájl | Cél |
|------|------|-----|
| **FastAPI backend** | `src/api/main.py` | HTTP API szerver (port 8003) |
| **PySide6 GUI** | `meteo_gui_starter.py` | Asztali alkalmazás |
| **React frontend** | `frontend/` (CRA) | Web UI (port 3000, proxy → 8003) |
| **CLI scripts** | `scripts/`, `src/scripts/` | Ad-hoc elemzések |

### Modul határok

A `src/` rétegek Clean Architecture irányt követnek:

```
presentation → infrastructure → application → domain
     ↓                ↓              ↓
     api ──────→ application ──→ domain
     ↓
  analytics ──→ domain
```

A `data` réteg mint külső adapter szolgál (port implementációk), az `infrastructure/container/` DI factory-kel köti össze.

⚠️ **A `presentation/` réteg a teljes kód 76%-át teszi ki**, ami jelentős kiegyensúlyozatlanság.

---

## 2. Függőségtérkép

### Külső függőségek

#### Backend — Runtime (requirements.txt)

| Csomag | Verzió | Cél |
|--------|--------|-----|
| `geopandas` | 1.1.1 | Térképi adatok, GeoJSON |
| `pandas` | 3.0.1 | Adatfeldolgozás |
| `plotly` | 5.24.1 | Interaktív chartok |
| `scikit-learn` | 1.8.0 | ML (anomália detekció) |
| `scipy` | 1.17.1 | Statisztikai számítások |
| `PyQtDarkTheme2` | >=2.1.2 | GUI dark theme |

#### Backend — Nem listázott runtime függőségek ⚠️

A `requirements.txt` nem teljes. A kód importálja de nem listázza:
- `PySide6` (Qt6 GUI framework)
- `httpx` (HTTP client)
- `matplotlib` (chartok)
- `fastapi` (web framework)
- `uvicorn` (ASGI server)

#### Backend — Dev tooling (requirements-dev.txt / pyproject.toml)

| Csomag | Cél |
|--------|-----|
| `ruff >=0.8.0` | Linting + formatting |
| `mypy >=1.8.0` | Type checking |
| `pytest >=8.0.0` | Test runner |
| `pytest-cov >=4.1.0` | Coverage |
| `pytest-timeout >=2.3.1` | Test timeout |
| `mutmut >=2.4` | Mutation testing |
| `radon >=5.0,<6` | Complexity analysis |
| `xenon >=0.9` | Complexity gate |
| `wily >=1.25` | Historical trends |
| `import-linter >=2.0` | Clean Architecture enforcement |
| `vulture >=2.11` | Dead code detection |
| `bandit >=1.7.7` | Security scanning |
| `detect-secrets >=1.4` | Secrets detection |
| `pre-commit >=3.7` | Git hooks |

#### Frontend (package.json)

| Csomag | Verzió | Cél |
|--------|--------|-----|
| `react` | 19.2.0 | UI framework |
| `react-dom` | 19.2.0 | DOM rendering |
| `typescript` | 4.9.5 | Type system |
| `axios` | 1.13.2 | HTTP client |
| `leaflet` + `react-leaflet` | 1.9.4 / 5.0.0 | Térkép |
| `recharts` | 3.4.1 | Chart komponensek |
| `plotly.js-dist-min` | 3.3.1 | Interaktív chartok |
| `react-router-dom` | 7.9.6 | Routing |
| `react-scripts` | 5.0.1 | CRA build |

### Belső modul-függőségek (rétegszinten)

```
                    ┌─────────────┐
                    │ presentation │
                    └──┬───┬───┬──┘
                       │   │   │
          ┌────────────┘   │   └────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌───────────┐    ┌───────────┐
    │   api    │    │analytics  │    │infrastruc.│
    └──┬───┬───┘    └─────┬─────┘    └─────┬─────┘
       │   │              │                │
       ▼   ▼              ▼                ▼
┌──────────┐ ┌────────────┐          ┌──────────┐
│application│ │  domain    │◄─────────│   data   │
└─────┬─────┘ └────▲───────┘          └──────────┘
      │            │
      └────────────┘
```

Import irányok (fájl-szintű):
- `api` → `application`, `config`, `data`, `domain`, `infrastructure`, `analytics`
- `presentation` → `infrastructure`, `application`, `config`, `domain`, `analytics`
- `analytics` → `application`, `domain`, `infrastructure`
- `data` → `config`, `domain`
- `infrastructure` → `data`, `domain`
- `domain` → **(saját magán belül)**
- `application` → `domain`, `api` ⚠️

### ⚠️ Cirkuláris / Irány-sértő függőségek

1. **`api` ↔ `application`** ⚠️⚠️
   - `api/routes/*.py` importálja `application/use_cases/`-t ✓
   - `application/use_cases/calculate_trend.py` importálja `src.api.dto.trend_request`-et ✗
   - Ez megsérti a Clean Architecture rétegsorrendet.

2. **`data` ↔ `domain`** ⚠️
   - `data/models.py` importál `domain.entities`-t ✓ (adattár a domain entitásokat használja)
   - `data/enums.py` re-exportálja `domain.value_objects.enums`-t — a domain réteg tisztaságát sérti, mert a re-export miatt két helyről is elérhetők az enum-ok.

3. **`src/config.py` ↔ `src/config/`** ⚠️
   - Van egy `src/config.py` (legacy re-export wrapper) ÉS egy `src/config/` package.
   - A Python a package-t részesíti előnyben, de a `config.py` `from src.config import`-et tartalmaz, ami a saját package-jét importálja vissza. Nem végtelen ciklus, de kétértelmű és karbantartási kockázat.

4. **`analytics` → `infrastructure`** ⚠️
   - `analytics/multi_city_engine_core.py` importálja `src.infrastructure.container`-t.
   - Az analytics réteg az application/domain között kellene legyen, nem az infrastructure alatt.

---

## 3. Technológiai leltár

### Nyelvek, framework-ök

| Réteg | Nyelv | Framework | Verzió |
|-------|-------|-----------|--------|
| Backend API | Python | FastAPI | — |
| Backend GUI | Python | PySide6 (Qt6) | — |
| Frontend | TypeScript | React 19 (CRA) | TS 4.9 |
| Adatbázis | SQL | SQLite | beépített |
| Térkép (backend) | Python | geopandas | 1.1.1 |
| Térkép (frontend) | JS | Leaflet + react-leaflet | 1.9.4 / 5.0.0 |

### Konfig fájlok

| Fájl | Cél | Megjegyzés |
|------|------|------------|
| `pyproject.toml` | Ruff, mypy, pytest, coverage, bandit, vulture, mutmut beállítások | Fő konfig |
| `requirements.txt` | Runtime függőségek (6 csomag) | ⚠️ Nem teljes |
| `requirements-dev.txt` | Dev tooling (14 csomag) | |
| `Makefile` | Build/quality/test parancsok | ⚠️ `BE_DIR=backend` de nincs `backend/` dir |
| `.importlinter` | Clean Architecture rétegellenőrzés | 4 kontraktus definiálva |
| `.coveragerc` | Coverage konfig (85% min) | ⚠️ `src/presentation/gui/*` kihagyva |
| `ruff.toml` | Linter config | ⚠️ `py311` target vs `pyproject.toml` `py312` |
| `mypy.ini` | Type checking overrides | ⚠️ Redundáns a pyproject.toml-lal |
| `quality_gate.sh` | Minőségi kapu script | 324 soros bash script |
| `.env` / `.env.example` | API kulcsok (Meteostat, API auth) | `.env` nincs `.gitignore`-ban |
| `frontend/.env.example` | Frontend API URL + key | |
| `frontend/package.json` | React CRA, proxy → localhost:8003 | |

### Test coverage becslés

| Terület | Fájlok | Sorok | Megjegyzés |
|---------|--------|-------|------------|
| Backend tests | 211 | 24,484 | Jó lefedettség, domain+config+data rétegek |
| Frontend tests | 9 | ~500 | Minimális (9 komponens teszt) |
| GUI (PySide6) tests | **0** | **0** | `.coveragerc` explicit kihagyja |

**Backend coverage target:** 85% (de csak a `src/` rétegre, a `presentation/gui/*` ki van zárva)

⚠️ **A GUI réteg (51k sor, a kód 76%-a) teljesen teszteletlen.**

---

## 4. Audit előkészítő összefoglaló

### Top 3 logikai/architekturális probléma

1. **⚠️ Kiegyensúlyozatlan rétegméret — `presentation` uralja a kódbázist**
   - A `presentation/gui/` 51,319 sor (76%).
   - A domain layer csak 4,903 sor (7%).
   - Ez az "anemic domain model" antipattern — az üzleti logika a GUI-ban van, nem a domain/application rétegekben. A GUI komponensek (charts, controllers, workers) üzleti logikát is tartalmaznak.
   - **Hatás:** Nehezen tesztelhető, nehezen újrahasznosítható, GUI-csere esetén a logika elveszik.

2. **⚠️ 96 db `_part*.py` + 51 db `_support*.py` — mesterséges fájlszétvágás**
   - A fájlokat mechanikusan vágták 250 soros darabokra (valószínűleg linterek miatt).
   - Néhány fájl duplán is szét van vágva: `extreme_events_tab_part2_part1.py`, `extreme_events_tab_part2_part2.py`, `theme_helpers_part1_part1.py`, `theme_helpers_part1_part2.py`.
   - 147 mesterségesen szétvágott fájl egy olyan kódbázisban, ami már rétegekre van bontva — ez a strukturálás látszatát kelti, de valójában karbathatatlan.

3. **⚠️ Cirkuláris importok a rétegek között + Makefile eltérés a valós struktúrától**
   - `application` importál `api`-ból (calculate_trend.py → api.dto.trend_request).
   - `analytics` importál `infrastructure`-ból.
   - A Makefile `BE_DIR=backend`-et vár, de a backend kód közvetlenül a `src/` gyökérben van — a `make` parancsok nem működnek a jelenlegi struktúrával.
   - A `ruff.toml` `py311`-et céloz, a `pyproject.toml` `py312`-t — ellentmondás.

### Top 3 security kockázat

1. **⚠️ Dupla auth ellenőrzés az API-ban + opcionális teljes kikapcsolás**
   - `api/main.py`-ban két helyen történik auth: middleware (74-108. sor) + `Depends(verify_api_key)` (44-67. sor). A middleware redundáns a dependency injection mellett.
   - `API_KEY_ENABLED=False` esetén az **egész API nyitott** — nincs semmilyen auth. Ez a default állapot (az `.env`-ben nincs API_KEY beállítva).

2. **⚠️ SQLite adatbázisok duplikálva, a `src/` alatt is**
   - `data/cities.db` (9.8MB) ≠ `src/data/cities.db` (12MB) — különböző hash-ek, különböző tartalom.
   - `data/hungarian_settlements.db` ≠ `src/data/hungarian_settlements.db` — szintén különböző.
   - `src/scripts/src/data/hungarian_settlements.db` — harmadik másolat.
   - Nem világos melyik az "igazi". Ha a rossz DB-t használja valamelyik komponens, adatinkonzisztencia léphet fel.

3. **⚠️ `.env` nem szerepel explicit a `.gitignore`-ban (de a `git status` szerint nem tracked)**
   - A `.env` létezik az `.env.example`-lel azonos placeholder tartalommal.
   - A `.gitignore` listázza a `.env`-t, de a biztonság nem garantált — ha valaki `git add .env`-et futtat, nincs pre-commit hook ami megállítaná (a `detect-secrets` csak `make install`-kor generál baseline-t).
   - A GeoJSON fájlok (counties, postal_codes) tracked-ek és nagyok — nem érzékeny adat, de a repo méretét növelik.

### Top 3 teljesítmény-bottleneck jelölt

1. **⚠️ Szinkron HTTP hívások a GUI thread potenciális blokkolása**
   - A `weather_client_core.py` szinkron `httpx` client-et használ (nem async).
   - A PySide6 QThread-ek (`workers/`) ezt kompenzálják, de sok közvetlen GUI komponens hívhat API-kat a main thread-ből (különösen a `controller/` és `control_panel/` rétegek).
   - Ha egy worker nem fut le, a GUI befagy.

2. **⚠️ Geopandas + nagy GeoJSON betöltés minden alkalommal**
   - A `counties.geojson` és `postal_codes.geojson` fájlok tracked-ek a repóban (a `git diff` mutatja hogy módosultak).
   - A `hungarian_location_selector` geopandas-t használ térkép renderelésre — ha nincs cache, minden alkalommal betölti és feldolgozza.

3. **⚠️ Hármas chart library (plotly + recharts + matplotlib)**
   - Backend: plotly (5.24.1) + matplotlib
   - Frontend: recharts (3.4.1) + plotly.js-dist-min (3.3.1)
   - A plotly.js ~3MB+ bundle. A tripla infrastruktúra növeli a bundle méretét, a telepítési időt és a karbantartási terhet.

---

## Melléklet: Fájl-szintű riasztások

### `src/config.py` vs `src/config/` konfliktus

```
src/config.py          ← legacy re-export wrapper (2205 soros fájl, de csak re-export)
src/config/__init__.py ← valódi package
```

A Python 3 import rendszer a package-t részesíti előnyben. A `config.py` `from src.config import ...`-et tartalmaz, ami a package-t importálja. Ez működik, de:
- A `src/config.py` fájlnév konfliktust okoz IDE-kban és import resolver-ekben.
- Ha valaki `import src.config`-et ír, mindig a package-t kapja, a fájlt soha.
- A fájl törlése nem törné meg a rendszert, mert minden import a package-ből történik.

### `_part*_part*` dupla szétvágás

```
extreme_events_tab_part2_part1.py
extreme_events_tab_part2_part2.py
theme_helpers_part1_part1.py
theme_helpers_part1_part2.py
```

Ezek azt jelzik, hogy először `part2`-re vágtak egy fájlt, majd a `part2`-t tovább vágták `part1`/`part2`-re. Ez a mintázat arra utal, hogy a fájlméret-limit túl szigorú (250 sor), és a split nem tervezett, hanem automatikus.

### Makefile `backend/` könyvtár eltérés

A Makefile `BE_DIR ?= backend`-et használ, de a backend kód közvetlenül a root `src/` könyvtárban van. A `make install-be`, `make check-be`, `make test-be` parancsok valószínűleg nem működnek a jelenlegi struktúrával, mert `cd backend && ...`-t próbálnak futtatni.
