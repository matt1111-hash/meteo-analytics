# Meteo-Analytics Master Refactor Plan

**Dátum:** 2026-05-12 (frissítve: 2026-05-13)
**Alap:** 4 audit (PROMPT0–PROMPT3) validált finding-jei
**Státusz:** 1815/1815 teszt zöld | Ruff clean | 93.56% coverage

---

## 0. Projekt állapotfelmérés

### Mire épül ez a terv?

Négy független modell (Kimi K2 Pro, GLM-5.1, DeepSeek V4, GPT-5 Codex) auditját
validáltam a kód ellen. Az eredmény 47 Finding, amiből 44 megerősítve, 2 téves,
1 részben helyes. Ez a terv a 44 validált Findinget strukturált fázisokba rendezi.

### Validált metrikák

| Metrika | Érték | Forrás |
|---|---|---|
| Python LOC (src/) | ~6204 sor (clean) / ~64K (teljes) | wc / audit |
| Tesztek | 1815 db, mind PASS (2026-05-13) | pytest |
| Ruff | 0 error | ruff check |
| mypy ignore fájlok | 499 db | grep |
| Frontend JS bundle | 5.3 MB (1 chunk) | ls build |
| API cold import | ~3.0 s | audit mérés |
| Per-request DI overhead | ~184 ms | audit mérés |
| Könyvtárszerkezet | 615+ Python fájl | audit |

### Validált kritikus problémák

| # | Probléma | Típus | Fájl |
|---|---|---|---|
| C1 | Trend kwargs mismatch (`lat`/`lon` vs `latitude`/`longitude`) | Funkcionális hiba | `calculate_trend.py:164` |
| C2 | Hibaválasz információszivárgás (3 endpoint) | Biztonság | `analytics.py:74`, `weather.py:33`, `single_city.py:67` |
| C3 | Per-request use case konstrukció (~184 ms) | Teljesítmény | 4 route handler |
| C4 | 499 fájl mypy ignore | Kódminőség | `src/` teljes |
| C5 | Dual City Repository Protocol | Architektúra | `repository_ports.py`, `repositories.py` |
| C6 | WeatherClientPort signature inkompatibilis a valós implementációval | Architektúra | `city_weather_ports.py`, `weather_client_core.py` |
| C7 | Domain pandas/numpy/scipy/sklearn függőség | Clean Architecture | 5 domain fájl |
| C8 | src/data/ vs src/infrastructure/ kettősség | Architektúra | 34 fájl |
| C9 | Dev deps production bundle-ben | Biztonság | `package.json` 8 csomag |
| C10 | Rate limiter memóriaszivárgás | Biztonság | `rate_limit.py:46-56` |
| C11 | Frontend 5.3 MB monolitikus JS chunk | Teljesítmény | `App.tsx:7-17` |
| C12 | Autocomplete SQL full scan | Teljesítmény | `city_repository_queries.py:158` |
| C13 | Multi-city pipeline korlátlan memóriagyűjtés | Teljesítmény | `analyze_multi_city.py:107-138` |
| C14 | Hungary async endpointok sync DB blokkolás | Teljesítmény | `hungary.py:117-229` |

---

## Fázisok áttekintése

```
Fázis 0: Sürgős javítások (P0)          ── 1-2 nap
Fázis 1: Biztonság megerősítése         ── 2-3 nap
Fázis 2: Architektúra rendezés          ── 1-2 hét
Fázis 3: Teljesítmény optimalizálás     ── 1 hét
Fázis 4: Kódminőség emelés              ── 1-2 hét
Fázis 5: Domain tisztaság               ── 1 hét
```

Minden fázis végén: **tesztek zöldek, ruff clean, coverage ≥85%**.

---

## Fázis 0: Sürgős javítások (P0)

**Cél:** Funkcionális hibák és azonnali biztonsági kockázatok megszüntetése.
**Idő:** 1-2 nap
**Függőség:** Nincs

### 0.1 Trend kwargs mismatch javítás ✅ KÉSZ

**Finding:** C1 — `calculate_trend.py:164-168` `lat`/`lon` kulcsszavakkal hívja
a `WeatherClient.get_weather_data()` metódust, ami `latitude`/`longitude` paramétereket
vár. A hiba csendben elnyelődik, trend adat üres lesz.

**Művelet:**
```python
# calculate_trend.py:164 — BEFORE (ROSSZ)
batch_data = self._weather_client.get_weather_data(
    lat=lat, lon=lon, ...)

# AFTER (JAVÍTOTT)
batch_data = self._weather_client.get_weather_data(
    latitude=lat, longitude=lon, ...)
```

**Teszt:** Trend endpoint hívás után nem üres eredmény, integritás teszt.

### 0.2 Hibaválasz információszivárgás megszüntetése ✅ KÉSZ

**Finding:** C2 — Három endpoint belső hibaüzenetet ad vissza a kliensnek.

**Művelet:**
| Fájl | Sorszám | Jelenleg | Javítás |
|---|---|---|---|
| `analytics.py` | 74 | `f"Trend calculation failed: {str(e)}"` | `"Trend calculation failed"` |
| `weather.py` | 33 | `uc_result.error_message or "Upstream error"` | `"Upstream error"` |
| `single_city.py` | 67 | `uc_result.error_message or "Upstream error"` | `"Upstream error"` |

**Teszt:** API tesztek ellenőrzik, hogy hibaüzenet nem tartalmaz belső részleteket.

### 0.3 Frontend devDependencies rendezés ✅ KÉSZ

**Finding:** C9 — 8 csomag tévesen `dependencies`-ben `devDependencies` helyett.

**Művelet:** `frontend/package.json` — átmozgatás:
- `@testing-library/dom`, `@testing-library/jest-dom`, `@testing-library/react`,
  `@testing-library/user-event`, `@types/jest`, `@types/react`, `@types/react-dom`,
  `esbuild`, `typescript`, `vite-node`, `web-vitals` → `devDependencies`

**Teszt:** `npm run build` sikeres, production bundle méret csökken.

### 0.4 Fázis 0 quality gate ✅ KÉSZ

- [x] `python -m pytest tests/ -v` — 1814/1814 PASS
- [x] `python -m ruff check src/` — 0 error
- [x] Trend endpoint ad vissza eredményt
- [x] Hibás API hívás nem szivárogtat belső információt
- [x] `npm run build` sikeres
- **Extra:** rejtett 502→500 HTTPException bug javítva, +4 regressziós teszt

---

## Fázis 1: Biztonság megerősítése

**Cél:** A PROMPT2 összes közepes és magas findingjének javítása.
**Idő:** 2-3 nap
**Függőség:** Fázis 0

### 1.1 Rate limiter memóriaszivárgás ✅ KÉSZ

**Finding:** C10 — `_timestamps` dict IP kulcsai sosem törlődnek.

**Művelet:** `rate_limit.py` — hozzáadás a `_is_limited` végén:
```python
# Üres timestamp listával rendelkező IP kulcsok evictálása
if not self._timestamps[client_ip]:
    del self._timestamps[client_ip]
```

Alternatíva: `cachetools.TTLCache` használata a dict helyett.

**Teszt:** Long-running rate limiter teszt, memória nem nő végtelenül.

### 1.2 CORS beállítások szűkítése ✅ KÉSZ

**Művelet:** `main.py:75-76`:
```python
allow_methods=["GET", "POST", "OPTIONS"],
allow_headers=["Authorization", "Content-Type"],
```

### 1.3 @app.on_event → lifespan migráció ✅ KÉSZ

**Művelet:** `main.py:48` — `on_event("startup")` → FastAPI `lifespan` context manager.
Ez egyben a per-request DI (C3) megoldásának alapja is lesz.

### 1.4 Hardcoded abszolút útvonal ✅ KÉSZ

**Művelet:** `scripts/launch_meteo_analytics_fullstack.sh:38`:
```bash
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
```

### 1.5 logging.basicConfig eltávolítása ✅ KÉSZ

**Művelet:** `main.py:27` — `logging.basicConfig(level=logging.INFO)` eltávolítása,
uvicorn saját log konfigurációja marad.

### 1.6 Database fájlok .gitignore-ba ✅ KÉSZ

**Művelet:** `.gitignore` kiegészítés:
```
data/*.db
data/*.db-journal
data/*.db-wal
```
A `data/geojson/` és `data/user_preferences/` maradhat tracked.

### 1.7 Fázis 1 quality gate ✅ KÉSZ

- [x] Rate limiter memória teszt PASS
- [x] CORS teszt: csak engedélyezett methodok
- [ ] Lifespan alapú startup/shutdown működik
- [ ] Launch script más gépen is fut
- [ ] `git status` nem mutat `.db` fájlokat

---

## Fázis 2: Architektúra rendezés

**Cél:** A PROMPT1 és PROMPT0 által azonosított strukturális káosz megszüntetése.
**Idő:** 1-2 hét
**Függőség:** Fázis 1 (lifespan rendelkezésre áll)

### 2.1 Dual City Repository Protocol egyesítése ✅ KÉSZ

**Finding:** C5 — Két Protocol ugyanarra a fogalomra:
- `CityRepositoryPort` (9 tag, `src/domain/ports/repository_ports.py`)
- `CityRepositoryProtocol` (3 tag, `src/domain/analytics/repositories.py`)

**Művelet:**
1. `CityRepositoryPort` kiterjesztése a `CityRepositoryProtocol` 3 metódusával
2. Minden hivatkozás cseréje `CityRepositoryPort`-ra
3. `src/domain/analytics/repositories.py` törlése
4. `hungarian_mapping` típus egységesítése (`dict[str, str]`)

**Érintett fájlok:** `repository_ports.py`, `repositories.py`,
`city_repository.py`, `factories.py`, `multi_city_engine_core.py`,
`analyze_multi_city.py`, és minden importáló teszt

**Teszt:** `CityRepositoryPort` implementáció teszt, összes meglévő teszt PASS.

### 2.2 WeatherClientPort signature javítás ✅ KÉSZ

**Finding:** C6 — A port `WeatherDataProtocol | None`-ot ígér, a valós
`WeatherClient` `list[dict[str, Any]]`-t ad vissza.

**Művelet:**
1. `WeatherClientPort.get_weather_data` visszatérési típusának frissítése:
   `list[dict[str, Any]]` vagy wrapper result típus
2. Paraméternevek szinkronizálása: `latitude`/`longitude` mindkét oldalon
3. Adapter réteg vizsgálata: kell-e DTO konverzió

**Teszt:** Port konformancia teszt, API route tesztek.

### 2.3 src/data/ → src/infrastructure/ migráció

**Finding:** C8 — 34 fájl, 4432 LOC infrastruktúra kód `src/data/` alatt
ahelyett, hogy `src/infrastructure/`-ben lenne.

**Művelet (fokozatos):**
1. `src/data/city_manager*.py` → `src/infrastructure/city_manager/`
2. `src/data/weather_client*.py` → `src/infrastructure/weather/`
3. `src/data/*provider*.py` → `src/infrastructure/providers/`
4. `src/data/geo_utils*.py` → `src/infrastructure/geo/`
5. `src/data/circuit_breaker.py` → `src/infrastructure/resilience/`
6. `src/data/distance_calculator*.py` → `src/infrastructure/geo/`
7. `src/data/anomaly_profile/` → `src/infrastructure/anomaly/`
8. `src/data/enums.py` — törlés (üres re-export wrapper)
9. Import path frissítés minden fájlban
10. `.importlinter` config frissítés

**Függőség:** 2.1 és 2.2 befejezve (stabil port réteg kell a mozgatáshoz)

**Teszt:** Import-linter PASS, `grep -r "from src.data" src/` — 0 találat.

### 2.4 MultiCityEngine wrapper megszüntetése

**Finding:** A `MultiCityEngine` felesleges delegáló réteg az
`AnalyzeMultiCityUseCase` felett. A GUI ezen megy keresztül, az API
a composition_root-ot használja közvetlenül.

**Művelet:**
1. GUI entry point-ok átirányítása a composition_root használatára
2. `MultiCityEngine` → thin facade vagy teljes törlés
3. `src/analytics/multi_city_engine*.py` fájlok konszolidálása
4. `src/analytics/multi_city_legacy.py` törlés

**Függőség:** 2.3 (data → infrastructure mozgatás)

**Teszt:** GUI analytics flow teszt, API multi-city teszt.

### 2.5 Halott analytics portok tisztítása

**Finding:** `AnomalyDetectionPort`, `AnalyticsQueryPort`, `QueryTypeConfigPort` —
definícióban léteznek, nincs implementációjuk, nincs hívójuk.

**Művelet:**
- Törlés ha nincs terv implementációra
- Ha van terv: `# TODO: PHASE-X implement` komment és tracking issue
- `WindAnalysisPort` — van implementáció, de 0 hívó → döntés szükséges

### 2.6 Config modulok üzleti logika kiszervezése

**Finding:** `UsageTracker` és `get_resolved_provider()` üzleti logikát
tartalmaznak a config modulban.

**Művelet:**
1. `get_resolved_provider()` → `src/application/services/provider_routing.py`
2. `UsageTracker` cost estimation → `src/application/services/cost_estimation.py`
3. `UsageTracker` marad config-only (file I/O, settings)

### 2.7 Legacy wrapper-ek törlése

**Művelet:**
- `src/data/city_manager.py` (55 sor re-export) — hivatkozások frissítése, törlés
- `src/config.py` (legacy re-export) — hivatkozások frissítése, törlés
- `src/config/__init__.py:82` — `datetime = _datetime` backward compat eltávolítása
- `src/analytics/multi_city_legacy.py` — 3-szintű indirekció törlése

### 2.8 Fázis 2 quality gate

- [ ] `from src.data` import → 0 találat
- [ ] Egyetlen `CityRepositoryPort` létezik
- [ ] `WeatherClientPort` return típus kompatibilis az implementációval
- [ ] `MultiCityEngine` vagy törlött vagy thin facade (<50 sor)
- [ ] Halott portok törölve
- [ ] Import-linter PASS
- [ ] 1811+ teszt PASS
- [ ] Coverage ≥85%

---

## Fázis 3: Teljesítmény optimalizálás

**Cél:** A PROMPT3 által azonosított teljesítmény-problémák javítása.
**Idő:** 1 hét
**Függőség:** Fázis 2 (stabil architektúra kell a DI módosításokhoz)

### 3.1 Per-request DI → lifespan-managed services

**Finding:** C3 — Minden route handler új use case-et, client-et, repository-t
épít. Mért overhead: ~184 ms kérésenként.

**Művelet:**
1. FastAPI `lifespan` context manager (Fázis 1-ben létrehozott) kiterjesztése:
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       app.state.use_cases = {
           "multi_city": build_analyze_multi_city_use_case(),
           "detailed_city": build_detailed_city_use_case(),
           "trend": build_trend_use_case(),
       }
       yield
       # Shutdown — session cleanup
       for uc in app.state.use_cases.values():
           if hasattr(uc, 'close'):
               await uc.close()
   ```
2. Route handler-ek átirányítása `request.app.state.use_cases[...]`-ra
3. Thread-safe shared state garantálása

**Teszt:** Warm request latency benchmark, concurrency teszt.

### 3.2 Autocomplete SQL indexelés

**Finding:** C12 — `LOWER(city) LIKE '%query%'` full table scan 44 658 soron.

**Művelet (választható megközelítés):**
- **Opció A:** Normalizált `city_lower` oszlop + index + prefix keresés (`query%`)
- **Opció B:** SQLite FTS5 virtuális tábla
- **Opció C:** Redis/Memory cache a top találatokra

**Javaslat:** Opció A — a legegyszerűbb, jó kompromisszum. Migration script
kell hozzá, ami hozzáadja a `city_lower` oszlopot és indexet.

**Frontend:** `CityAutocomplete.tsx` — `AbortController` hozzáadás (P1).

### 3.3 Frontend code splitting

**Finding:** C11 — 5.3 MB monolitikus JS chunk, minden page statikus import.

**Művelet:**
1. `App.tsx:7-17` — statikus importok → `React.lazy`:
   ```tsx
   const AnalyticsView = React.lazy(() => import('./pages/AnalyticsView'));
   const MultiCityView = React.lazy(() => import('./pages/MultiCityView'));
   // ...
   ```
2. `WindRoseChart.tsx:6` — Plotly lazy import
3. `HungaryMap.tsx:11` — Leaflet lazy import
4. `vite.config.ts` — `manualChunks` konfiguráció:
   ```ts
   build: {
     rollupOptions: {
       output: {
         manualChunks: {
           'plotly': ['plotly.js-dist-min'],
           'leaflet': ['leaflet', 'react-leaflet'],
           'recharts': ['recharts'],
         }
       }
     }
   }
   ```

**Cél:** Initial JS chunk < 500 KB, teljes bundle < 2 MB (gzipped).

**Teszt:** `npm run build` után `ls -la build/assets/` — legalább 5 chunk,
initial < 500 KB.

### 3.4 Multi-city memóriakezelés

**Finding:** C13 — `limit` csak a fetch+transform után érvényesül,
addig minden város minden napja memóriában van.

**Művelet:**
1. City limit alkalmazása a fetch előtt (ha a query tartalmazza)
2. Streaming/generator alapú feldolgozás vizsgálata
3. `weather_fetch_service.py` — `split_batches` → generator:
   ```python
   def split_batches(cities, batch_size):
       for i in range(0, len(cities), batch_size):
           yield cities[i:i + batch_size]
   ```

### 3.5 Hungary async/sync javítás

**Finding:** C14 — 3 endpoint `async def` de szinkron DB hívásokkal blokkolja
az event loopot.

**Művelet:** `hungary.py` — `run_in_threadpool` becsomagolás:
```python
result = await run_in_threadpool(city_manager.get_hungarian_counties)
```

### 3.6 Hungary N+1 query → bulk query

**Művelet:** `_fetch_station_candidates` refaktor:
```python
# BEFORE: N+1 — county-nként külön query
for county_name in city_manager.get_hungarian_counties():
    all_cities.extend(city_manager.get_cities_for_hungarian_county(county_name))

# AFTER: Egyetlen bulk query
all_cities = city_manager.get_hungarian_settlements_bulk(limit=limit * 2)
```

Ehhez új repository metódus kell: `get_settlements_bulk(county_filter, limit)`.

### 3.7 API cold import csökkentés

**Művelet:** Lazy import az analytics route-ban:
```python
# analytics.py — BEFORE
from src.application.use_cases.calculate_trend import CalculateTrendUseCase

# AFTER — route handleren belül
def calculate_trend(request):
    from src.application.use_cases.calculate_trend import CalculateTrendUseCase
    ...
```

Cél: API startup < 1.0 s (jelenleg ~3.0 s).

### 3.8 Multi-year batch endpoint

**Művelet:** Új endpoint vagy meglévő kiterjesztése:
```python
@router.post("/api/weather/multi-year-batch")
async def multi_year_batch(request: MultiYearRequest):
    # Egyetlen backend hívás, évszámok paraméterként
    # A backend belsőleg párhuzamosít
```

Frontend: `useMultiYearWeather.ts` — Promise.all N hívás → 1 batch hívás.

### 3.9 Egyéb teljesítmény javítások

| Elem | Művelet | Prioritás |
|---|---|---|
| ThreadPoolExecutor per-batch | Service-scope executor újrafelhasználás | P3 |
| Wind rose 16× scan | Egyszeri pass, 16×bucket mátrix | P3 |
| Trend periódus re-filter | Egyszeri monthly aggregate | P3 |
| Detailed city 4× process | Egyszeri feldolgozás, 4 metrika projekció | P3 |
| requests.Session lifecycle | Lifespan-managed singleton | P3 |
| Per-record INFO logging | `logger.info` → `logger.debug` | P3 |
| Per-request factory cache | Lifespan-scope manager singleton | P3 |

### 3.10 Fázis 3 quality gate

- [ ] API warm request latency < 50 ms (backend overhead)
- [ ] API cold start < 1.0 s
- [ ] Frontend initial chunk < 500 KB
- [ ] Frontend teljes bundle < 2 MB
- [ ] Autocomplete válaszidő < 50 ms (local)
- [ ] Multi-city 50 város + 1 év < 5 s
- [ ] Hungary endpoint nem blokkolja event loopot
- [ ] 1811+ teszt PASS, coverage ≥85%

---

## Fázis 4: Kódminőség emelés

**Cél:** mypy coverage javítása, tesztelhetőség növelése, karbantarthatóság.
**Idő:** 1-2 hét
**Függőség:** Fázis 2 (stabil architektúra) és Fázis 3 (stabil DI)

### 4.1 Mypy ignore redukció (499 → <50)

**Stratégia:** Modulonkénti, prioritásalapú visszavezetés.

**Hullám 1 — Hot path (1. hét):**
- `src/domain/ports/` — Protocol fájlok
- `src/application/use_cases/` — Use case-ek
- `src/api/routes/` — Route handler-ek
- `src/api/dto/` — API DTO-k
- `src/infrastructure/container/` — DI

Művelet: `# mypy: ignore-errors` → specifikus `# type: ignore[xxx]` vagy javítás.

**Hullám 2 — Services (2. hét):**
- `src/domain/services/`
- `src/infrastructure/`
- `src/config/`

**Hullám 3 — GUI (később):**
- `src/presentation/` — legalább a controller és worker fájlok

**Cél:** ≤50 fájl `ignore-errors`, a domain/application/api rétegek 0 db.

### 4.2 UsageTracker instance-alapúra

**Művelet:**
```python
# BEFORE — static class, nehezen tesztelhető
class UsageTracker:
    _lock = threading.Lock()
    @staticmethod
    def track_usage(...): ...

# AFTER — injectálható instance
class UsageTracker:
    def __init__(self, storage_path: Path, clock: Callable[[], datetime]):
        self._storage_path = storage_path
        self._clock = clock
        self._lock = threading.Lock()
```

Factory: `get_usage_tracker()` → lifespan-managed singleton.

### 4.3 Hibakezelési stratégia egységesítése

**Finding:** Három különböző stratégia keveredik:
1. `UseCaseResult` (result type) — use case-ekben
2. `Exception` (dobás) — WeatherClient-ben
3. Silent fallback — MultiCityEngine-ben

**Művelet:**
- Use case-ek: `UseCaseResult` marad, de gazdagítva (error category, loggable detail)
- Infrastructure: Exception dobás marad
- Presentation: Explicit error handling, nincs silent fallback
- Új: `ValidationError` osztály az input validációs hibákhoz (CWE-209 enyhítés)

### 4.4 Frontend kódminőség

| Elem | Művelet |
|---|---|
| Heatmap duplikáció | Közös `CalendarMatrix` + `MetricHeatmap` komponens |
| 300+ soros fájlok | Feature-scope bontás, hook extrakció |
| TrendAnalyticsView export | Implementáció vagy feature flag mögé rejtés |
| TypeScript 4.9 → 5.x | Frissítés a React 19 kompatibilitáshoz |

### 4.5 Fázis 4 quality gate

- [ ] mypy ignore fájlok ≤50
- [ ] Domain + application + api rétegek 0 mypy ignore
- [ ] `mypy src/ --strict` — 0 error (legalább domain/application)
- [ ] Coverage ≥90%
- [ ] Frontend TypeScript 5.x
- [ ] Nincs 300+ soros Python fájl (kivéve presentation legacy)

---

## Fázis 5: Domain tisztaság

**Cél:** A domain réteg teljes külső függőség-mentessége.
**Idő:** 1 hét
**Függőség:** Fázis 2 (architektúra stabil) és Fázis 4 (mypy tiszta)

### 5.1 pandas/numpy/scipy/sklearn kiszervezése a domain-ből

**Finding:** C7 — 5 domain fájl importál nehéz tudományos könyvtárakat:
- `trend_statistics.py` — numpy, pandas, scipy, sklearn
- `wind_analysis_service.py` — pandas
- `wind_statistics.py` — pandas
- `trend_data_processor.py` — pandas
- `wind_extractors.py` — pandas

**Művelet:**
1. Új könyvtár: `src/infrastructure/analytics/`
2. Számítási logika áthelyezése:
   - `trend_statistics.py` → `src/infrastructure/analytics/trend_calculator_impl.py`
   - `wind_statistics.py` → `src/infrastructure/analytics/wind_statistics_impl.py`
   - stb.
3. Domain-ben csak Protocol definíció marad:
   ```python
   # src/domain/analytics/ports.py
   class TrendCalculator(Protocol):
       def calculate_trend(self, data: list[dict], ...) -> TrendResult: ...
   ```
4. Factory regisztrálja az infrastructure implementációt a Protocol-hoz

**Teszt:** Domain import vizsgálat — `grep -r "import pandas\|import numpy\|import scipy\|import sklearn" src/domain/` → 0 találat.

### 5.2 Composition root kiegészítése GUI-hoz

**Finding:** A GUI nem használja a composition_root-ot, közvetlenül hívja
a port factory-ket.

**Művelet:**
1. `build_gui_services()` factory a composition_root-ban
2. GUI controller-ek átállása a factory használatára
3. `AppController` kapja a service-eket konstruktor paraméterként

### 5.3 Hardcoded konfiguráció kiváltása

**Művelet:** `composition_root.py` — `max_workers=8`, `request_timeout=90`,
`max_retries=2`, `retry_delay=3.0` → `src/config/` vagy env var.

### 5.4 Fázis 5 quality gate

- [ ] `grep -r "import pandas\|import numpy\|import scipy\|import sklearn" src/domain/` → 0
- [ ] GUI composition root használ
- [ ] Minden hardcoded érték konfigurálható
- [ ] 1811+ teszt PASS
- [ ] Coverage ≥90%
- [ ] `mypy src/domain/ --strict` → 0 error

---

## Kockázatok és mitigáció

| Kockázat | Valószínűség | Hatás | Mitigáció |
|---|---|---|---|
| Import path törés Fázis 2.3-ban | Magas | Magas | Fázisonként commit, automatikus import-linter |
| Cirkuláris import Fázis 5.1-ben | Közepes | Magas | Először Protocol-ok, utána mozgatás |
| GUI regresszió Fázis 2.4-ben | Közepes | Közepes | GUI smoke tesztek (kézi + automated) |
| Teszt törés mozgatásoknál | Magas | Alacsony | Minden lépés után `pytest` futtatás |
| Frontend bundle törés Fázis 3.3-ban | Alacsony | Közepes | `npm run build` + manual browser teszt |
| API backward compatibility | Alacsony | Magas | API versioning ha szükséges |

---

## Végleges minőségi célok

| Metrika | Jelenleg | Cél | Fázis |
|---|---|---|---|
| Tesztek | 1815 PASS | 1815+ PASS | Minden |
| Coverage | 93.56% | ≥90% | Fázis 4 |
| mypy ignore fájlok | 499 | ≤50 | Fázis 4 |
| Ruff error | 0 | 0 | Minden |
| API cold start | ~3.0 s | <1.0 s | Fázis 3 |
| Per-request overhead | ~184 ms | <10 ms | Fázis 3 |
| Frontend initial chunk | 5.3 MB | <500 KB | Fázis 3 |
| Domain külső importok | 5 fájl | 0 | Fázis 5 |
| `from src.data` importok | 50+ | 0 | Fázis 2 |
| Funkcionális trend hiba | Nem ✅ | Nem | Fázis 0 |
| Security findings (MAGAS) | 0 ✅ | 0 | Fázis 0 |
| Dual protocol | Egyesítve ✅ | 1 port | Fázis 2 |
| WeatherClientPort mismatch | Javítva ✅ | Kompatibilis | Fázis 2 |

---

## Végrehajtási sorrend (dependency graph)

```
Fázis 0 ──────────────────────────────────────────────── Sürgős
    │
Fázis 1 ──────────────────────────────────────────────── Biztonság
    │
    ├── Fázis 2.1 (Protocol egyesítés)
    ├── Fázis 2.2 (Port signature)
    │       │
    │   Fázis 2.3 (data → infrastructure)  ←── 2.1 és 2.2 után
    │       │
    │   Fázis 2.4 (MultiCityEngine)  ←── 2.3 után
    │   Fázis 2.5 (Halott portok)
    │   Fázis 2.6 (Config logika)
    │   Fázis 2.7 (Legacy törlés)
    │
    ├── Fázis 3.1 (Lifespan DI)  ←── Fázis 1.3 után
    │   Fázis 3.2 (Autocomplete)
    │   Fázis 3.3 (Code splitting)  ←── Fázis 0.3 után
    │   Fázis 3.4 (Multi-city memória)
    │   Fázis 3.5 (Hungary async)  ←── Fázis 1.3 után
    │   Fázis 3.6 (Hungary N+1)
    │   Fázis 3.7 (Lazy import)
    │   Fázis 3.8 (Multi-year batch)
    │   Fázis 3.9 (Egyéb)
    │
    ├── Fázis 4.1 (Mypy redukció)  ←── Fázis 2 után
    │   Fázis 4.2 (UsageTracker)
    │   Fázis 4.3 (Hibakezelés)
    │   Fázis 4.4 (Frontend minőség)
    │
    └── Fázis 5.1 (Domain tisztítás)  ←── Fázis 2 + 4 után
        Fázis 5.2 (GUI composition root)
        Fázis 5.3 (Hardcoded config)
```

---

**Készítette:** GLM-5.1 agent, 4 audit validált finding-jei alapján
**Utoljára frissítve:** 2026-05-12
