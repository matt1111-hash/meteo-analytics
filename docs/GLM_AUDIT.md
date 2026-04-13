# Meteo Analytics — Architekturális Áttekintés

> **Dátum**: 2026-04-07
> **Elemző**: GLM-5-Turbo architekturális audit
> **Scope**: Teljes repó átfogó vizsgálata

---

## 1. Struktúratérkép

### Könyvtárfa

```
meteo-analytics/
├── data/                          # Futásidejű adatok (cache, GeoJSON, user prefs)
│   ├── cache/                     # API válasz cache (httpx alapú)
│   ├── climate_cache/             # Klímaadat cache
│   ├── geojson/                   # Megye + irányítószám GeoJSON (⚠️ 11MB gitben)
│   ├── user_preferences/          # Felhasználói beállítások JSON + backups/
│   ├── cities.db                  # Városadatbázis (9.8MB ⚠️)
│   ├── meteo_data.db              # Meteorológiai adatok (12MB ⚠️)
│   └── hungarian_settlements.db   # Településadatbázis (772KB)
├── docs/                          # Dokumentáció
├── exports/                       # Exportált jelentések (üres)
├── frontend/                      # React/TypeScript SPA
│   ├── public/                    # Statikus asszettek
│   └── src/
│       ├── components/            # 45 TSX komponens (UI réteg)
│       │   ├── analytics/         # Hőmérséklet/Szél/Csapadék tab-ok és hőtérképek
│       │   └── common/            # Megosztott widgetek (CityAutocomplete stb.)
│       ├── config/                # Frontend konfig
│       ├── constants/             # Alkalmazás konstansok
│       ├── contexts/              # React context-ek
│       ├── hooks/                 # Egyedi React hook-ok (useCityWeather stb.)
│       ├── pages/                 # Oldal komponensek
│       ├── services/              # API hívó szolgáltatások (axios)
│       ├── styles/                # CSS fájlok
│       ├── types/                 # TypeScript típusdefiníciók
│       └── utils/                 # Segédfüggvények
├── logs/                          # Alkalmazás naplók
├── scripts/                       # Segédszkriptek
│   └── ultimate_project_analyzer.py  # ⚠️ 1583 soros monolitikus script
├── src/                           # Python backend (Clean Architecture)
│   ├── domain/                    # Domain réteg (tiszta, keretrendszer-független)
│   │   ├── entities/              # Entitások (weather, analytics_models, universal_location)
│   │   ├── value_objects/         # Értékobjektumok
│   │   ├── ports/                 # Port interfészek (szerződések)
│   │   └── services/              # Domain szolgáltatások
│   ├── application/               # Alkalmazás réteg (use case-ek)
│   │   ├── dto/                   # Data Transfer Objects
│   │   ├── services/              # Alkalmazás szolgáltatások
│   │   └── use_cases/             # Üzleti use case-ek (analyze_multi_city stb.)
│   ├── infrastructure/            # Infrastruktúra réteg
│   │   ├── adapters/              # Keretrendszer adapterek
│   │   └── repositories/          # Adatelérés implementációk (SQLite)
│   ├── presentation/              # Prezentáció réteg
│   │   ├── api/                   # FastAPI routes + DTO + middleware
│   │   └── gui/                   # PySide6 GUI (MVC)
│   │       ├── analytics/         # Analytics panel widgetek
│   │       ├── charts/            # Diagram komponensek
│   │       ├── controller/        # MVC kontrollerek
│   │       ├── results_panel/     # Eredmény panel
│   │       ├── weather_data_bridge/  # ⚠️ Szoros csatolás bridge
│   │       └── windows/           # Főablak + dialógusok
│   ├── analytics/                 # Analytics feldolgozás (multi-city engine, wind)
│   ├── config/                    # Konfiguráció (API, provider, paths, usage)
│   └── data/                      # Adatkezelés (city_manager, weather_fetch, anomaly)
├── tests/                         # Teszt suite (211 fájl)
│   ├── domain/                    # Domain unit tesztek
│   ├── application/               # Application unit tesztek
│   ├── infrastructure/            # Infra tesztek
│   ├── api/                       # API integrációs tesztek
│   ├── analytics/                 # Analytics feature tesztek
│   └── integration/               # E2E integrációs tesztek
├── meteo_gui_starter.py           # 🖥️ Desktop belépési pont (PySide6)
├── .importlinter                  # Clean Architecture szabályok
├── .pre-commit-config.yaml        # Pre-commit hookok
├── quality_gate.sh                # Minőségi kapu script
├── Makefile                       # Build automatizáció
├── pyproject.toml                 # Python projekt konfig
└── requirements.txt               # Futásidejű függőségek
```

### Belépési pontok

| Belépési pont | Típus | Fájl | Technológia |
|---|---|---|---|
| Desktop GUI | MVC applikáció | `meteo_gui_starter.py` | PySide6 |
| REST API | Szerver | `src/api/main.py` | FastAPI (port 8003) |
| Frontend SPA | Web kliens | `frontend/src/` | React 19 + TypeScript |
| Minőségi kapu | CLI | `quality_gate.sh` | Bash |

### Modul/csomag határok

A projekt **Clean Architecture** mintát követ:

```
Domain ← Application ← Infrastructure ← Presentation (API + GUI)
  ↑           ↑              ↑                  ↑
  tiszta    use case-ek    SQLite/HTTP       FastAPI/PySide6
```

- **Domain** (0 külső import): Entitások, port interfészek, domain szolgáltatások
- **Application**: Use case-ek, DTO-k, koordinálja a domain-infra interakciót
- **Infrastructure**: SQLite repository-k, HTTP adapterek
- **Presentation**: FastAPI routes + PySide6 GUI (MVC kontrollerek + view-k)

---

## 2. Függőségtérkép

### Külső függőségek

**Python (requirements.txt):**

| Csomag | Verzió | Cél |
|---|---|---|
| pandas | 3.0.1 | Adatmanipuláció |
| geopandas | 1.1.1 | Földrajzi adatfeldolgozás |
| plotly | 5.24.1 | Interaktív vizualizáció |
| scikit-learn | 1.8.0 | Gépi tanulás |
| scipy | 1.17.1 | Tudományos számítások |
| PyQtDarkTheme2 | >=2.1.2 | Dark téma támogatás |

**Python dev (pyproject.toml / requirements-dev.txt):**

| Csomag | Verzió | Cél |
|---|---|---|
| ruff | >=0.8.0 | Linting + formázás |
| mypy | >=1.8.0 | Típusellenőrzés |
| pytest | >=8.0.0 | Tesztelés |
| pytest-cov | >=4.1.0 | Coverage |
| bandit | >=1.7.7 | Biztonsági vizsgálat |
| import-linter | >=2.0 | Architektúra ellenőrzés |
| mutmut | >=2.4 | Mutációs tesztelés |
| vulture | – | Halott kód detektálás |
| radon/xenon | – | Komplexitás mérés |
| detect-secrets | >=1.4 | Titok szivárgás detektálás |

**Frontend (package.json):**

| Csomag | Verzió | Cél |
|---|---|---|
| react | 19.2.0 | UI keretrendszer |
| react-router-dom | 7.9.6 | Útválasztás |
| plotly.js-dist-min | 3.3.1 | Diagramok |
| recharts | 3.4.1 | Diagramok |
| leaflet / react-leaflet | 1.9.4 / 5.0.0 | Térképek |
| axios | 1.13.2 | HTTP kliens |
| typescript | 4.9.5 | Típusos JS |

### Belső modul-függőségek

```
┌──────────────────────────────────────────────────┐
│                  PRESENTATION                     │
│  ┌─────────────┐         ┌──────────────────┐    │
│  │  FastAPI     │         │  PySide6 GUI      │    │
│  │  routes/     │         │  controller/      │    │
│  │  dto/        │         │  windows/         │    │
│  └──────┬───────┘         └────────┬──────────┘    │
│         │                          │               │
│         │    ┌─────────────────────┘               │
│         │    │  ⚠️ GUI közvetlenül domain-hoz      │
│         ▼    ▼  (weather_data_bridge csatolás)     │
│  ┌──────────────────────────────────────────┐     │
│  │           APPLICATION                     │     │
│  │  use_cases/ ← services/ ← dto/           │     │
│  └──────────────────┬───────────────────────┘     │
│                     │                              │
│  ┌──────────────────▼───────────────────────┐     │
│  │         INFRASTRUCTURE                    │     │
│  │  adapters/ ← repositories/ ← container/  │     │
│  └──────────────────┬───────────────────────┘     │
│                     │                              │
│  ┌──────────────────▼───────────────────────┐     │
│  │            DOMAIN (tiszta)                │     │
│  │  entities/ ← value_objects/ ← ports/     │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### Cirkuláris függőség gyanús helyek ⚠️

| # | Gyanú | Indok |
|---|---|---|
| ⚠️ 1 | `presentation/gui/weather_data_bridge/` → `domain/entities/` | A GUI réteg 8 helyen importál közvetlenül domain entitásokat, megkerülve az Application réteget |
| ⚠️ 2 | `presentation/gui/panel_widgets/` → `domain/entities/` | A location_widget közvetlenül hivatkozik `universal_location` entitásra |
| ⚠️ 3 | `presentation/gui/dialogs/` → `domain/` | Beállítás dialógusok domain függőségekkel |
| ⚠️ 4 | Domain rétegben threading/Qt hivatkozások | Domain komponensek használnak Qt threading-et, ami megsérti a keretrendszer-függetlenséget |

> **Összesen 22 Clean Architecture sértés** a Presentation → Domain/Infrastructure irányban. A `.importlinter` konfig létezik, de a sértések jelenleg nincsenek kikényszerítve.

---

## 3. Technológiai leltár

### Nyelvek, framework-ök, infrastruktúra

| Réteg | Technológia | Verzió | Megjegyzés |
|---|---|---|---|
| Backend nyelv | Python | 3.12+ | Kötelező |
| Backend framework | FastAPI | – | Async REST API |
| Desktop framework | PySide6 | – | Qt6 alapú GUI |
| Frontend nyelv | TypeScript | 4.9.5 | Strict mode |
| Frontend framework | React | 19.2.0 | CRA alapú |
| Adatfeldolgozás | pandas | 3.0.1 | DataFrame-alapú |
| Geoadat | geopandas | 1.1.1 | Shapefile/GeoJSON |
| ML | scikit-learn | 1.8.0 | Anomália detektálás |
| Vizualizáció (Python) | plotly | 5.24.1 | Interaktív diagramok |
| Vizualizáció (React) | recharts + plotly.js | 3.4.1 / 3.3.1 | Kettős diagram lib |
| Térkép | Leaflet | 1.9.4 | OpenStreetMap |
| Adatbázis | SQLite | – | Több DB fájl (cities, meteo, settlements) |
| HTTP kliens | httpx / axios | – | Backend / Frontend |

### Infrastruktúra

- **Nincs Docker** — nincs docker-compose, Dockerfile
- **Nincs K8s** — nincs cloud deployment konfig
- **GitHub Actions** — `.github/workflows/ci.yml`
- **Lokális fejlesztés** — frontend proxy-z a `localhost:8003`-ra

### Konfig fájlok

| Fájl | Cél |
|---|---|
| `pyproject.toml` | Projekt meta, függőségek, ruff/mypy/pytest/bandit konfig |
| `requirements.txt` | Futásidejű Python függőségek |
| `requirements-dev.txt` | Dev függőségek (alternatíva a pyproject.toml-hoz) |
| `mypy.ini` | Típusellenőrzés konfig (pandas/scipy/sklearn ignore) |
| `.importlinter` | Clean Architecture réteg-szabályok |
| `.pre-commit-config.yaml` | Pre-commit hookok (ruff, mypy, bandit, detect-secrets) |
| `Makefile` | Build automatizáció (lint, test, coverage, quality gate) |
| `quality_gate.sh` | CI minőségi kapu (85% coverage, 300 sor limit, xenon, vulture) |
| `frontend/package.json` | React függőségek + scriptek |
| `frontend/tsconfig.json` | TypeScript konfig (ES5 target, strict) |
| `.env` / `.env.example` | MeteoStat API kulcs + opcionális API key |
| `.github/workflows/ci.yml` | CI pipeline |

### Tesztlefedettség becslés

| Réteg | Forrás fájlok | Teszt fájlok | Arány |
|---|---|---|---|
| Python backend | ~685 | ~211 | **30.8%** |
| React frontend | ~45 TSX | ~9 | **20%** |
| **Összesen** | **~730** | **~220** | **~30%** |

> A `pyproject.toml` **85%-os coverage** követelményt ír elő, de a fájl-szintű arány ezt nem támasztja alá. Valószínűleg a meglévő tesztek nagy vonalakban lefedik a kritikus utakat, de sok modulra lehet hiányos.

---

## 4. Audit előkészítő összefoglaló

### Top 3 logikai / architekturális probléma ⚠️

| # | Terület | Indok |
|---|---|---|
| ⚠️ **1** | **Presentation → Domain közvetlen csatolás** (22 sértés) | A GUI réteg megkerüli az Application réteget, közvetlenül importál domain entitásokat. Ez megsérti a Clean Architecture Dependency Rule-t, és megnehezíti a domain logika önálló tesztelését/refaktorálását. |
| ⚠️ **2** | **Domain réteg Qt/threading szennyeződés** | Domain komponensek használnak Qt threading-et és PySide6 típusokat, ami megsérti a keretrendszer-függetlenséget. A domain logika nem futtatható Qt nélkül. |
| ⚠️ **3** | `ultimate_project_analyzer.py` — **1583 soros God script** | Masszív monolitikus szkript, ami sérti a Single Responsibility elvet. Karbantarthatósági és tesztelhetőségi rémálom. |

### Top 3 security kockázat ⚠️

| # | Terület | Indok |
|---|---|---|
| ⚠️ **1** | **API auth letiltható** (`src/api/main.py:50-51`) | Ha `APIConfig.API_KEY` üres, a hitelesítés teljesen kikapcsol. Production-ben véletlenül nyitott API-t eredményezhet. |
| ⚠️ **2** | **CORS túl megengedő** (`src/api/main.py:32-38`) | `allow_methods=["*"]` és `allow_headers=["*"]` — bármilyen HTTP metódus és header engedélyezve van a localhost-ról. |
| ⚠️ **3** | **Nagy adatfájlok git-ben** (cities.db 9.8MB, meteo_data.db 12MB, GeoJSON 11MB) | Bináris adatbázisok a repoban növelik a klón méretét és potenciálisan tartalmazhatnak szenzitív adatokat. Nincs `.gitignore`-ozva. |

### Top 3 teljesítmény-bottleneck jelölt ⚠️

| # | Terület | Indok |
|---|---|---|
| ⚠️ **1** | **Hiányzó API pagináció** (`src/api/routes/cities.py`) | A város kereső endpoint nem korlátozza a visszaküldött találatok számát — széles keresés esetén több ezer rekord is visszajöhet. |
| ⚠️ **2** | **Multi-city fetch szekvenciális mintázat** (`analyze_multi_city_part1.py:66-72`) | ThreadPoolExecutor enyhíti, de az eredeti minta városonkénti fetch, ami skálázódási problémát jelent sok városnál. |
| ⚠️ **3** | **Kettős vizualizációs könyvtár** (recharts + plotly.js a frontend-ben) | Két teljes diagram-könyvtár bundle-ölve van a frontend-be, ami jelentősen növeli a JavaScript bundle méretet és a memória-használatot. |

---

> **Összegzés**: A projektnek szilárd az alapja — Clean Architecture minta, 85%-os coverage cél, átfogó quality gate, pre-commit hookok. A fő kockázatok a Presentation-Domain rétegcsatolásból, a domain Qt-függőségből és a git-ben tárolt nagy adatfájlokból fakadnak.
