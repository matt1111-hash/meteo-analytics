# 02_LOGIC — Logika, architektúra és megbízhatóság audit

**RUN_ID:** `20260910T092914Z`
**Mód:** read-only elemzés (nincs javítás, refaktor, telepítés, hálózat, production adatbázis)
**Bemenet:** `docs/audit/20260910T092914Z/01_MAP.md` + a repó tényleges forrása
**Repo gyökér:** `/home/tibor/PythonProjects/meteo-analytics`
**Snapshot (ellenőrizve):** HEAD `c4793cdc9ef6161d2bcaf91d994bae2348426d78`, branch `main`, worktree piszkos — a porcelain **egyezik** a térkép §1.2 listájával (nincs snapshot-eltérés)
**Mérési ablak:** 2026-09-10 09:52–09:57 UTC

A térkép navigáció volt, nem bizonyíték: minden itteni állítás a kód és a futtatott parancsok alapján készült. Ahol a térkép állítását cáfoltam, az a §7-ben szerepel.

---

## 1. Vizsgált flow-k és lefedettség

Az API a kanonikus szerveroldali belépő (`src/api/main.py:52` → `lifespan` `src/api/main.py:30-49` → `build_service_registry()` `src/api/dependencies.py:29-58`), a GUI a `meteo_gui_starter.py` → `MainWindow` út.

| # | Flow | Belépő → side effect | Lefedettség | Mi maradt ki |
|---|------|----------------------|-------------|--------------|
| F1 | Health | `GET /health` (`main.py:88-91`) → statikus dict | **TELJES** | — |
| F2 | Multi-city analitika | `POST /api/weather/multi-city` (`routes/weather.py:19-43`) → adapter (`adapters/weather_adapter.py:27-48`) → `AnalyzeMultiCityUseCase.execute` (`use_cases/analyze_multi_city.py:64-158`) → `CityRepository` → `WeatherFetchService` → `WeatherClient` → provider → `AnalyticsResult.to_dict()` | **TELJES** (hibaágakkal) | — |
| F3 | Single-city idősor | `POST /api/weather/single-city` (`routes/single_city.py:57-96`) → query_type átírás → ugyanaz az UC `aggregate=False` | **TELJES** | — |
| F4 | Detailed single-city | `POST /api/weather/single-city-detailed` (`routes/detailed_city.py:36-62`) → `DetailedCityUseCase.execute` (`use_cases/detailed_city_use_case.py:60-119`) → 4 metrika ugyanabból a fetchből | **TELJES** | — |
| F5 | Trend | `POST /api/analytics/trend` (`routes/analytics.py:18-51`) → `CalculateTrendUseCase.execute` (`use_cases/calculate_trend.py:42-205`) → `CityManager` + `WeatherClient` (éves batchek) → `TrendCalculator` | **TELJES** | maga a regresszió-számítás (`infrastructure/analytics/trend_calculator.py`) nem |
| F6 | Anomáliák | `POST /api/weather/anomalies` (`routes/anomalies.py:121-170`) → fetch a multi-city UC-n keresztül → `DetectAnomaliesUseCase.execute` (`use_cases/detect_anomalies.py:25-59`) → `AnomalyDetectorService` | **TELJES** | a küszöb-döntési logika (`domain/services/anomaly_detector.py` küszöb-összevetései) részben |
| F7 | Multi-year batch | `POST /api/weather/multi-year-batch` (`routes/multi_year.py:56-89`) → 4 szálas évenkénti fan-out ugyanarra az UC-ra | **TELJES** | — |
| F8 | Wind rose | `POST /api/weather/wind-rose` (`routes/wind_rose.py` → `wind_rose_part3.py:133-154`) → `CityManager.find_city_by_name` + `WeatherClient.get_weather_data` | **RÉSZLEGES** | `_process_wind_rose_data` (`wind_rose_part2.py`) és a sávozási logika |
| F9 | Katalógus/olvasó végpontok | `GET /api/cities/search` (`routes/cities.py:16-57`), `wind_rose`-on kívül: `metadata.py`, `hungary.py` | **RÉSZLEGES** | `routes/hungary.py`, `routes/metadata.py` tartalma nem lett végigolvasva (kizárólag statikus/olvasó végpontok) |
| F10 | Provider-kezelés | `GET /api/providers/{list,status,{id}/status,{id}/usage,selected}`, `POST /api/providers/{id}/select` (`routes/providers.py:41-224`) → `UserPreferences` + `ProviderUsageService` | **TELJES** | — |
| F11 | GUI mentés | város kiválasztás (`controller/geocoding_handler.py:239-274`) → `DatabaseManager.save_city_to_database` (`controller/database_manager.py:159-191`); időjárás (`controller/weather_data_handler/core.py:51-112`) → `save_weather_to_database` (`database_manager.py:193-272`) | **TELJES** (írási út) | a worker/QThread életciklus |
| F12 | GUI indulás/leállás | `meteo_gui_starter.py` → `MainWindow` | **BLOKKOLT** | GUI nem indult (headless); csak statikus olvasás |
| F13 | Frontend → API szerződés | `frontend/src/services/apiClient.ts:72-130` + a 11 SPA route | **RÉSZLEGES** | a page-komponensek hibakezelése; Playwright e2e nem futott |

**Kritikus hibaágak, amiket külön végigkövettem:** validációs hiba (400), provider-kiesés/retry-kimerülés, „nincs város”, „nincs adat”, üres bemenet, hiányzó DB-fájl, retry- és fallback-lánc, leállás (`lifespan` shutdown).

---

## 2. Architektúra — a tényleges rétegek és a bizonyított eltérések

**Rétegek (import-linter contract PASS, térkép §3.2):** `src/domain` ← `src/application` ← `src/infrastructure` / `src/analytics` / `src/api` / `src/presentation`. A `lint-imports` 3 contractja KEPT, a domain tiltott importjai (fastapi/httpx/requests…) nincsenek meg.

**Composition rootok (tényleges):**

| Root | Mit épít | Ki használja |
|------|----------|--------------|
| `src/infrastructure/container/composition_root.py:10-52` | `AnalyzeMultiCityUseCase`, `DetailedCityUseCase` | API `dependencies.build_service_registry` |
| `src/infrastructure/container/factories.py:30-127` | port-implementációk (nincs cache) | API + GUI + composition root |
| `src/api/dependencies.py:29-58` | `ServiceRegistry` (`app.state.services`) — **és helyben épít egy use case-t**: `CalculateTrendUseCase(...)` a 50-54. sorban | API route-ok |
| `src/presentation/gui/gui_composition_root.py:28-56` | `GuiServices` | GUI |

**Bizonyított architekturális eltérések:**

1. **Párhuzamos példányok (mért).** Egy `build_service_registry()` hívás **3 `WeatherClientExtensions`, 3 `CityRepository`, 2 `WeatherFetchService`** példányt hoz létre (mérés: `gc.get_objects()` számolás, ld. §9). A registry `weather_client`-je **nem** azonos a multi-city/detailed fetch-klienssel (mért: `is` → `False`), és a circuit breaker objektumok is különböznek (mért: `is` → `False`). Részletek: L-05.
2. **Composition bypass az API rétegben.** A `CalculateTrendUseCase` az API `dependencies.py:50-54`-ben épül, nem a composition rootban; a `DetectAnomaliesUseCase` pedig route-modul szintű globális (`routes/anomalies.py:57`). → L-09.
3. **Két városfeloldó implementáció** (`CityRepository` vs `CityManagerStats`) eltérő illesztési szemantikával, két külön végpontcsoportban használva. → L-07.
4. **Nincs perzisztencia-port a GUI DB-írás mögött:** a `WeatherRepositoryPort` (`domain/ports/city_weather_ports.py:131-155`) deklarált, de **nincs implementációja**; a `data/meteo_data.db`-t közvetlen `sqlite3` hívásokkal a presentation írja. → L-10.
5. **Kettős adatmodell ugyanabban az API-ban:** a multi-city/detailed/anomália/multi-year út `CityWeatherData` dataclass-t használ, a wind-rose és a trend nyers `list[dict]`-et (`wind_rose_part3.py:37-48`, `calculate_trend.py:177-185`). Nem önmagában finding — a konzekvenciája az L-03 (eltérő hibaábrázolás) és a kétféle városfeloldás (L-07).

**Megfigyelés — piszkos worktree (security-hatókör, itt csak a szerződés-tény):** a worktree eltávolítja az API-kulcs réteget: `src/config/api_config.py` HEAD 46-48/84-86 (`API_KEY`, `API_KEY_ENABLED`), `src/api/main.py` HEAD 33-38 (production startup guard), 96-176 (`verify_api_key`, `PUBLIC_PATHS`, `auth_middleware`), 178-192 (`/auth/status`). Mért következmény: a repo **más része nem hivatkozik** a mechanizmusra (`rg 'X-API-Key|API_KEY|auth/status' frontend/src tests/api/api_auth_support.py` → 0 találat), tehát nincs törött kliens-szerződés; a production indulás viszont már nem fail-fastel API-kulcs nélkül. A kockázati besorolás a security-audit (PROMPT 3) feladata.

---

## 3. Meglévő jó megoldások (bekötve, olvasott kóddal igazolva)

| Megoldás | Hely | Mit bizonyít |
|----------|------|--------------|
| Paraméterezett SQL + LIKE-escape | `infrastructure/repositories/city_repository_queries.py:20-60,148-218`, `infrastructure/db/like_utils.py` | nincs string-beégetett felhasználói input; a `?` placeholderek és az `ESCAPE '\'` konzisztensen használt |
| Útvonal-traversal védelem | `city_repository_paths.py:21-35` | a DB-útvonal canonicalizálás után trusted base alá kell essen |
| Retry + fallback + circuit breaker | `weather_client_core.py:112-157,215-236`, `resilience/circuit_breaker.py` | thread-safe (lockolt) CB, CLOSED→OPEN→HALF_OPEN szemantika, provider-fallback lánc |
| HTTP-szintű timeout minden provider-hívásban | `openmeteo_provider.py:169-170`, `meteostat_provider.py:141` (`timeout=APIConfig.REQUEST_TIMEOUT` = 30 s) | nincs végtelen blokkolás egy provider-hívásban |
| `UseCaseResult` + hibakategória → HTTP mapping | `application/use_cases/use_case_result.py`, `api/error_handling.py:10-38` | VALIDATION→400, PROVIDER→502, INTERNAL→500, a belső üzenet nem szivárog ki (erre teszt is van: `tests/api/test_weather_route.py:122-142`) |
| Bemenet-validáció a szélen | `api/dto/weather_request.py:26-110` | ISO dátum + span ≤ `MAX_DATE_RANGE_DAYS` (~5 év) + `MAX_CITIES_PER_REQUEST` cap, és az adapter újra csonkol (`weather_adapter.py:30-34`) |
| Rate limiter hardening | `api/middleware/rate_limit.py:36-92` | FIX-01 (XFF csak trusted proxy mögött), FIX-02 (bounded kliens-tár + eviction) |
| Atomikus JSON írás | `config/atomic_io.py` (temp + replace), `UserPreferences.save_provider_preferences` | nincs félig írt prefs-fájl |
| Production fail-fast | `api/main.py:33-39` | `APP_ENV=production` + `*` CORS → `RuntimeError` induláskor |
| GUI provider-választó fallback jele | `workers/weather_data_worker/provider_selector.py:39-61` | elérhetetlen választott provider esetén `provider_validation_failed` + auto fallback (a fetch-kliens ezt **nem** teszi meg — L-03, illetve §6 H1) |
| Frontend rugalmasság | `frontend/src/services/apiClient.ts:72-130` | 30 s timeout, hálózati hibára 3 lépéses exponenciális retry, 5xx-re 1 retry |
| Teszt-bázis | lásd §5 | 1743 passed, CI-ekvivalens coverage 92,70 %, vitest 342 passed |

---

## 4. Megerősített / részleges findingek

Formátum: `[ID] [SEVERITY] [STÁTUSZ] Cím` — hely; megfigyelés; hívási út/feltétel; védelem és cáfolat; bizonyított hatás; javítási irány.

### [L-01] [MAGAS] [MEGERŐSÍTETT] GUI: a város újramentése elszakítja a mentett időjárás-előzményt (`INSERT OR REPLACE` + `name UNIQUE` + kikapcsolt FK)

- **Hely:** `src/presentation/gui/controller/database_manager.py:159-191` (`INSERT OR REPLACE INTO cities` a 171-183. sorban), séma: `data/meteo_data.db` → `cities.name TEXT UNIQUE`, `weather_data.city_id → cities.id` (FK deklarált).
- **Megfigyelés:** az `INSERT OR REPLACE` a SQLite REPLACE-algoritmusa szerint **törli** az ütköző sort és **új** `id`-vel szúrja be ugyanazt a várost; a korábbi `weather_data` sorok a régi `city_id`-ra mutatnak tovább.
- **Hívási út/feltétel:** GUI városkiválasztás → `geocoding_handler.py:254` → `_save_city_to_database` (266-274) → `save_city_to_database`; feltétel: ugyanazon város **bármely** ismételt kiválasztása (nincs dedup, nincs „csak ha új” ág).
- **Meglévő védelem és cáfolat:** `PRAGMA foreign_keys` a teljes `src/`-ben **nincs** (ellenőrizve `rg 'foreign_keys|PRAGMA'`-mal: csak `table_info` pragmák), `ON DELETE CASCADE` nincs → az FK-sértés csendben elmarad; cáfolni nem tudtam, ellenben **megmértem** a hatást.
- **Bizonyított hatás (mért):** `data/meteo_data.db` (mode=ro): `cities` = 60 sor, id-tartomány 1..452 (48 sor később újra beszúrva), `weather_data` = 79 824 sor **148** különböző `city_id`-val, ebből **62 957 sor (78,9 %) olyan `city_id`-ra mutat, amely már nem létezik a `cities` táblában**. Ma nincs olvasó útvonal (lásd L-10), ezért a látható UI-hatás korlátozott; bármely jövőbeli előzmény-olvasó viszont a sorok ~79 %-át elveszíti, és a mentés ciklusonként tovább romlik.
- **Javítási irány:** `INSERT ... ON CONFLICT(name) DO UPDATE SET latitude=..., longitude=...` (id megőrzés), vagy explicit „létezik már? → UPDATE” ág; emellett `PRAGMA foreign_keys=ON` a kapcsolatnyitáskor.

### [L-02] [KÖZEPES] [MEGERŐSÍTETT] A `POST /api/providers/{id}/select` nem hat a tényleges adatlekérésre — két külön igazságforrás

- **Hely:** `src/api/routes/providers.py:159-196` → `UserPreferences.set_selected_provider` (`config/provider_config.py:174-190`, fájl: `data/user_preferences/*.json`); a fetch-oldali választás: `infrastructure/weather/weather_client_core.py:169-199` → `get_optimal_data_source("single_city", prefer_free=True)` (`config/config_validation.py:102-127`).
- **Megfigyelés:** a kiválasztás fájlba kerül, a fetch viszont kizárólag a `DataConstants.USE_CASE_SOURCE_MAPPING` + `prefer_free` szerint dönt; a `preferred_provider` a termékben mindig `"auto"` (a `get_weather_client_port()` a `WeatherClientExtensions()`-t alapértelmezéssel építi, `factories.py:42-53`).
- **Hívási út/feltétel:** `POST /api/providers/meteostat/select` → bármely `POST /api/weather/*` vagy `/api/analytics/trend`; feltétel: a felhasználó a defaulttól eltérő providert választ.
- **Meglévő védelem és cáfolat:** nincs: `WeatherFetchService` 4 argumentummal hív (`weather_fetch_service.py:151-153`, `user_override_provider` default `None`), a route-ok nem adnak át override-ot. Cáfolatkeresés: `rg 'get_selected_provider|set_selected_provider'` → termékkódban csak `api/routes/providers.py` (76, 113, 181, 182, 212) és `presentation/gui/controller/provider_routing.py` olvassa; a fetch-lánc egyik pontján sem jelenik meg.
- **Bizonyított hatás:** `GET /api/providers/selected` „meteostat”-ot jelent, miközben a multi-city/detailed/anomália/trend lekérdezés open-meteo-t használ; a felhasználói döntés az API-n keresztül hatástalan, miközben a GUI worker-szintű választója (`provider_selector.py:53-61`) tiszteletben tartja — vagyis ugyanaz a beállítás GUI-ban és API-ban mást jelent.
- **Javítási irány:** a composition root olvassa a `UserPreferences.get_selected_provider()`-t és adja át `preferred_provider`-ként a fetch-kliensnek (vagy adjon a registry egy override-portot); a prefs-olvasás legyen egyetlen helyen.

### [L-03] [KÖZEPES] [MEGERŐSÍTETT] Ugyanaz a provider-kiesés végpontonként eltérő választ ad (502 vs. 200-üres vs. 200-null)

- **Hely:** multi-city: `routes/weather.py:34` + `api/error_handling.py:29-33` (502); detailed: `routes/detailed_city.py:42-62` (nincs `UseCaseResult`-mapping, a 200-as válasz üres listákkal jön); trend: `use_cases/calculate_trend.py:76-78` + `190-205` (`_empty_result`) → `routes/analytics.py:40` (200); anomáliák: `routes/anomalies.py:90-99` + `121-162` (a 404-ág **elérhetetlen**, ld. lent) → 200 három `null` anomáliával; multi-year: `routes/multi_year.py:51-53` (sikertelen év → `{"year": y, "data": []}`).
- **Megfigyelés:** a hibaábrázolás végpontonként eltér, és három úton a hiba **megkülönböztethetetlen** a „nincs adat” esettől.
- **Hívási út/feltétel:** provider-kiesés vagy retry-kimerülés (mindkét provider hibázik). A fetch service ilyenkor **nem** üres listát ad, hanem egy eleműt: `weather_fetch_service.py:179` → `create_empty_city_data` (`domain/analytics/services/weather_fetch_service_support.py:89-103`, `fetch_success=False`, minden metrika `None`).
- **Meglévő védelem és cáfolat:** részleges: `UseCaseResult` + `raise_for_use_case_result` a multi-city/single-city úton; a detailed/trend/anomália/multi-year úton nincs ekvivalens. Cáfolatkísérlet az anomália 404-ágra: `routes/anomalies.py:97` `if raw_weather_data:` — mivel a hibás fetch is **1 elemű listát** ad, a feltétel igaz, a 404 nem keletkezik; az anomália-detektor pedig a `None` értékeket kiszűri (`domain/services/anomaly_detector.py:26-29,201-208`), így `{temperature: null, precipitation: null, wind: null}` a válasz.
- **Bizonyított hatás:** a kliens nem tudja megkülönböztetni a „nincs adat”-ot a „szolgáltató halott”-tól; a frontend csak 5xx-re retry-zik (`frontend/src/services/apiClient.ts:119-126`), a 200-üres válaszra nem, tehát a felhasználó csendben üres grafikonokat lát.
- **Javítási irány:** egységes hibapolitika: a detailed/trend/anomália/multi-year úton is `UseCaseResult`/`ErrorCategory.PROVIDER` (502), vagy explicit `partial`/`data_source: "error"` mező a válaszban; a `fetch_success=False` rekordokat a route-oknak hibaként kell értelmezniük.

### [L-04] [KÖZEPES] [MEGERŐSÍTETT] A `/api/providers/*` usage/status felület strukturálisan nullákat ad (nincs író), és a circuit breaker állapot egyáltalán nem jut ki az API-ba

- **Hely:** `src/api/services/provider_usage_service.py:35-51` (`_create_default_usage_data`), `202-208` (modul-szintű singleton), `routes/providers.py:72-156`.
- **Megfigyelés:** a `ProviderUsageService._usage_data`-t **egyetlen termékkód sem módosítja** — nincs `record_request`/inkrementáló API. A `requests_total`, `requests_this_month`, `errors_total`, `last_used`, `average_response_time_ms`, `estimated_cost_usd` mindig a default (0/None).
- **Hívási út/feltétel:** `GET /api/providers/status`, `GET /api/providers/{id}/usage` bármikor.
- **Meglévő védelem és cáfolat:** cáfolatkeresés `rg '_usage_service|usage_service\.|record_request|requests_total'` → termékkódban csak olvasás (`routes/providers.py:75,112,147`); a `_usage_data`-t kizárólag tesztek írják monkeypatch-csel (`tests/api/test_providers_route_part1.py:134`, `part3.py:66`) — vagyis a teszt épp azt az állapotot injektálja, amit a termék nem állít elő. A `WeatherClient.provider_usage_stats`/`circuit_breakers` értékei (`weather_client_core.py:34,41-48`) **egyetlen route-ból sem olvashatók** (`rg 'circuit_breakers' src/` → csak a core fájl).
- **Bizonyított hatás:** a provider-limitek/usage/cost felület mindig „0 / elérhető küszöb alatt”; a valós hibaállapot (CB nyitva, fallback történt, provider-hívások száma) sehol nem jelenik meg sem az API-ban, sem a GUI státusz-sávban.
- **Javítási irány:** a usage-t a tényleges fetch úthoz kell kötni (a `WeatherClient` számlálóinak publikálása a registry-n át), és a CB állapotát (`state`, `failure_count`) ki kell adni a provider-státusz DTO-ban.

### [L-05] [KÖZEPES] [MEGERŐSÍTETT] Párhuzamos példányok: 3 weather-kliens / 3 city-repo / 2 fetch-service indításonként, külön circuit breaker állapottal

- **Hely:** `src/api/dependencies.py:43-58`, `src/infrastructure/container/factories.py:30-115` (egyetlen factory sem cache-el), `src/infrastructure/container/composition_root.py:24-52`.
- **Megfigyelés (mért):** egy `build_service_registry()` → **3 `WeatherClientExtensions`, 3 `CityRepository`, 2 `WeatherFetchService`**; `r.weather_client is mc.weather_fetch_service.weather_client` → `False`; a CB objektumok különbözőek (`is` → `False`); `r.city_repository is mc.city_repository` → `False`.
- **Hívási út/feltétel:** minden API-indítás (lifespan) — nincs különleges feltétel.
- **Meglévő védelem és cáfolat:** a `WeatherFetchService` a saját kliensét használja, tehát **nincs funkcionális hiba** egyetlen úton sem; a CB viszont példányonként 5 hibát számol, így a „küszöb” összesítve 3×5 hiba egy provider kiesésénél, és a registry kliense (amit a `/api/providers/*` elvileg képviselhetne) nem az, amelyik a fő adatutakat kiszolgálja.
- **Bizonyított hatás:** a provider-/CB-állapot nem reprezentálja a rendszert (L-04-gyel együtt), a `city_manager` pedig csak a trend/wind-rose úton él; a provider-választás (L-02) és a usage (L-04) ugyanabból a szétszórtságból ered.
- **Javítási irány:** cache-elt port-példányok (pl. `functools.lru_cache`/container-szintű életciklus), és a `CalculateTrendUseCase` is a composition rootból épüljön (`dependencies.py:50-54` helyett).

### [L-06] [KÖZEPES] [RÉSZBEN] Retry-szorzódás: nincs teljes kérés-deadline, a fetch-szintű timeout hatástalan, a kliens 30 s után elvágja

- **Hely:** `weather_client_core.py:215-236` (3 próba + lineáris delay), `weather_fetch_service.py:149-179` (2 próba + 3 s), `config/config_settings.py:18-21` (`max_workers=8`, `request_timeout=90`, `max_retries=2`, `retry_delay=3.0`), `config/api_config.py:56-57` (`REQUEST_TIMEOUT=30`, `MAX_RETRIES=3`), kliens: `frontend/src/services/apiClient.ts:74` (`timeout: 30_000`).
- **Megfigyelés:** a `future.result(timeout=self.request_timeout)` (`weather_fetch_service.py:125`) az `as_completed` után **no-op** (a future már befejeződött), ezért a 90 s-os „fetch timeout” nem korlátoz; egy város worst case ideje ≈ 2 provider × 3 próba × 30 s + delay ≈ 190 s, amit a fetch-szintű 2 próba megismétel → ≈ 380 s+; a trend úton ehhez év-batchenkénti 30 s-os timeoutok jönnek (`calculate_trend.py:142-149`, timeout nélküli `future.result()`).
- **Hívási út/feltétel:** lassú/hibázó provider (30 s-os requests-timeout vagy többszöri hibaválasz); aktiváló config: a fenti env-ek defaultjai.
- **Meglévő védelem és cáfolat:** **van** HTTP-szintű védelem (`timeout=APIConfig.REQUEST_TIMEOUT`, `openmeteo_provider.py:169-170`, `meteostat_provider.py:141`), tehát egy hívás nem blokkol végtelenségig; a frontend 30 s-os timeoutja viszont rövidebb, mint a szerveroldali lehetséges válaszidő — és a kliens lemondása után a szerver tovább dolgozik (cancellation nincs).
- **Bizonyított hatás:** a konfigurációból számított lánc bizonyított (olvasott kód + defaultok); a **tényleges gyakoriságot nem mértem** (nincs hálózat ebben a futásban) → RÉSZBEN. Reális következmény: a 30 s-nál hosszabb, egyébként sikeres kérések kliens-oldalon elhalnak, a szerver threadpoolja (anyio ~40) hosszan foglalt.
- **Javítási irány:** teljes kérés-deadline a fetch-service-ben (`as_completed(futures, timeout=…)` + `future.cancel()`), a retry-szorzódás csökkentése (egy rétegben retry), és a kliens timeout összehangolása a szerveroldali felső korláttal.

### [L-07] [KÖZEPES] [MEGERŐSÍTETT] Két különböző városfeloldás: ugyanaz a név végpontonként más országba/településbe esik

- **Hely:** repository-út: `infrastructure/repositories/city_repository_queries.py:20-60` (`WHERE LOWER(city) IN (...)` + max-populáció, **globális DB először**, a magyar DB csak fallback); city-manager út: `infrastructure/city_manager/city_manager_search.py:77-103` (magyar **prioritás**, exact-match majd best-match) és `:147-169` (`city LIKE '%term%'` — részleges egyezés).
- **Hívási út:** repository: `/api/weather/single-city`, `/single-city-detailed`, `/multi-city`, `/anomalies`, `/multi-year-batch`; city-manager: `/api/analytics/trend` (`calculate_trend.py:104-114`) és `/api/weather/wind-rose` (`wind_rose_part3.py:17-22`).
- **Megfigyelés/mérés (mode=ro lekérdezésekkel):** `term="Buda"` → repository: **Buda, US (14 348)**; city-manager: **Budapest, HU (2 997 958)**; `term="Kecske"` → repository: nincs találat (a hívó 400/„nincs város”), city-manager: **Kecskemét**; `term="Győr"` → repository a `cities` sorát adja (populáció 246 159), city-manager a `hungarian_settlements` sorát (130 191).
- **Meglévő védelem és cáfolat:** nincs közös feloldó; a `data_quality_score` mezőt a repository a magyar DB esetén **`region_priority`-ból** tölti fel (`city_repository_queries.py:53`), azaz a mező szemantikája is eltér a két úton. Cáfolat: nem név-pár-hiba — a két illesztési szabály bizonyítottan más, és a fenti három minta közvetlenül mérhető eltérést mutat.
- **Bizonyított hatás:** ugyanaz a felhasználói input más helyszínt/más adatminőséget jelent a „Trend” és a „Multi-city” fülön; részleges nevek némelyik végponton működnek, máshol nem.
- **Javítási irány:** egyetlen városfeloldó port (a `CityManagerPort` és a `CityRepositoryPort` közös szemantikával), a végpontok ugyanazt hívják; a fuzzy/exact szabályt explicit módon dokumentálni és egységesíteni.

### [L-08] [KÖZEPES] [MEGERŐSÍTETT] Részleges írás sikeresként jelentve a GUI mentésben

- **Hely:** `database_manager.py:240-272` (soronkénti `try/except … continue`, egyetlen `commit()` a 262. sorban, `return True` a 268. sorban), hívó: `weather_data_handler/core.py:103-112`.
- **Megfigyelés:** soronkénti hiba esetén a ciklus továbbmegy, `saved_count` nő csak a sikereseknél, de a visszatérés **`True`**, ha a külső try nem kapott kivételt — akkor is, ha `saved_count == 0`. A hívó ezt `weather_saved_to_db.emit(True)`-ként továbbítja.
- **Hívási út/feltétel:** `save_weather_to_database` bármely sorszintű hibája (típus-eltérés, constraint, disk) a kivétel forrása nélkül.
- **Meglévő védelem és cáfolat:** a logolás megvan (`_logger.warning`), a commit tranzakciós (nincs félig commitolt állapot); a **visszatérési érték** viszont nem hordozza a részlegességet, és `save_city_to_database` egyáltalán nem ad vissza értéket (`None`, `:159-191`), a hibát csak logolja (`:190-191`).
- **Bizonyított hatás:** a UI „mentve” visszajelzést adhat 0 mentett sor mellett; a felhasználó azt hiszi, van helyi előzménye.
- **Javítási irány:** adjon vissza `(saved, failed)` számlálót vagy `bool`-t a tényleges siker szerint, és a hívó a részleges eredményt is jelezze (a `weather_saved_to_db` szignál kapjon darabszámot).

### [L-09] [ALACSONY] [MEGERŐSÍTETT] Route-szintű globális singleton és holt kód az anomália-úton

- **Hely:** `routes/anomalies.py:57` (`anomaly_use_case = DetectAnomaliesUseCase()` import-időben), felhasználás `:145-151`; holt kód: `:133-136` (`WeatherAnalysisRequest(...)` létrehozva és eldobva).
- **Megfigyelés:** a 3. use case nem a `ServiceRegistry`-ből jön (szemben a multi-city/detailed/trend úttal), így a kompozíció és a teszt-cserélhetőség szempontja eltér; a 133-136. sor validációs szándéka hatástalan (az eredmény nem kerül sehova, a kérés DTO-ja már validált).
- **Hívási út/feltétel:** `POST /api/weather/anomalies` minden hívása.
- **Meglévő védelem és cáfolat:** nincs (a globális objektum stateless, ezért nincs adatverseny); a duplikált validáció miatt funkcionális hiba nincs.
- **Bizonyított hatás:** a registry nem az egyetlen kompozíciós pont (L-05 család); a holt sor félrevezeti a karbantartót.
- **Javítási irány:** a `DetectAnomaliesUseCase` kerüljön a `ServiceRegistry`-be, a felesleges `WeatherAnalysisRequest` példányosítás törlendő.

### [L-10] [ALACSONY] [MEGERŐSÍTETT] Implementálatlan repository-port + közvetlen `sqlite3` a presentation rétegben; nincs retenció

- **Hely:** `domain/ports/city_weather_ports.py:131-155` (`WeatherRepositoryPort`, benne `delete_old_weather_data`), egyetlen implementáció sincs (`rg 'delete_old_weather_data'` → csak a deklaráció); az írás a `presentation/gui/controller/database_manager.py`-ban közvetlen `sqlite3`-vel történik.
- **Megfigyelés:** a `data/meteo_data.db`-be **nincs** domain-port mögötti adapter; a `weather_data` táblához tartozó egyetlen Python-hivatkozás az írás (`INSERT OR REPLACE`, `database_manager.py:244-251`) — olvasó (`SELECT … FROM weather_data`) nincs a `src/`-ben (`rg 'FROM weather_data'` → 0 találat).
- **Hívási út/feltétel:** GUI mentések; a retenció soha nem fut.
- **Meglévő védelem és cáfolat:** nincs; ellenben a séma konzisztens (`weather_data(city_id,date)` UNIQUE — mért: 0 duplikált csoport), tehát az `INSERT OR REPLACE` ott helyes upsert.
- **Bizonyított hatás:** 79 824 sor gyűlt fel, amelyhez nincs olvasó útvonal és nincs tisztító mechanizmus; a port-deklaráció félrevezeti a réteg-modellt (a DB-írás tesztelhető varrat nélkül maradt — ezért az L-01 osztályú hiba láthatatlan).
- **Javítási irány:** vagy implementáld a `WeatherRepositoryPort`-ot és a `DatabaseManager` azt használja, vagy töröld a portot; + retenció (`delete_old_weather_data`) bekötése.

### [L-11] [ALACSONY] [MEGERŐSÍTETT] Rejtett, futásidőben bővülő globális állapot a repository-path kezelésben

- **Hely:** `city_repository_paths.py:12-15` (`_TRUSTED_BASES` modul-szintű lista) + `:44-55` (`_TRUSTED_BASES.append(resolved_env)`).
- **Megfigyelés:** egy instance-metódus globális listát módosít, amely minden további példány viselkedését befolyásolja (a `WEATHER_ANALYZER_DATA_DIR` első használata után az env-mappa örökre „trusted” lesz a folyamatban).
- **Hívási út/feltétel:** fallback-ág (`_resolve_fallback_path`) akkor, ha az alap DB-útvonal nem létezik és az env-változó be van állítva.
- **Meglévő védelem és cáfolat:** a `resolve`-oltatás és a `relative_to` ellenőrzés megmarad, tehát a bejárat továbbra is canonicalizált; a lista csak bővít, szűkít nem → nincs azonnali traversal-rés, ezért ALACSONY.
- **Bizonyított hatás:** a trust-döntés nem determinisztikus a folyamaton belül (sorrendfüggő), és nem izolált tesztenként.
- **Javítási irány:** a trusted base-ek legyenek példányszintűek (konstruktorban átadva) vagy a bővítés legyen explicit, dokumentált API.

### [L-12] [KÖZEPES] [MEGERŐSÍTETT] Tesztintegritás: az API-route tesztek 100 %-ban mockolt registry-vel futnak, és a valós hibamódok nincsenek lefedve

- **Hely:** `tests/api/conftest.py:19-31` (`MagicMock(spec=ServiceRegistry)`), `tests/api/test_weather_route.py:15-38` (a use case `MagicMock`, tetszőleges `UseCaseResult`-tal), `tests/api/test_anomalies_route.py:113-131`.
- **Megfigyelés:** `rg -c 'MagicMock\(spec=ServiceRegistry\)|mock_services' tests/api/*.py` → 9 fájl, összesen 63 előfordulás; az anomália-teszt a fetch service-t **üres listával** állítja be, ami a valós fetch-service kimeneteleként nem áll elő (hiba esetén 1 elemű, `fetch_success=False` lista jön — `weather_fetch_service.py:179`), tehát egy **elérhetetlen ágat** assertál, míg az L-03 valós hibamódja teszt nélkül marad. A trend úton `_empty_result` (`calculate_trend.py:190-205`) szintén nem szerepel egyetlen tesztben sem (`rg 'periods|empty|data_quality' tests/api/test_analytics_route.py` → 0).
- **Hívási út/feltétel:** a teljes `tests/api/` suite; a valós registry-t csak 2 hely használja (`tests/api/test_integration_cities_weather.py:28-36`, `tests/e2e/conftest.py:18-26`) — provider-kiesés szcenárió egyikükben sincs.
- **Meglévő védelem és cáfolat:** a suite **nem** gyengített: 1743 teszt zöld, nincs feltétel nélküli skip (a `pytest.skip` hívások könyvtár-hiányt őriznek: `tests/integration/test_clean_architecture_*.py`), és van valós integrációs mag (`test_integration_cities_weather.py`). A mockolás itt nem hiba, hanem **lefedettségi vakfolt**.
- **Bizonyított hatás:** az L-02…L-05 és L-07 osztályú hibák zöld suite mellett is láthatatlanok; a suite „igazsága” a mockolt DTO transzformációra korlátozódik.
- **Javítási irány:** legalább egy valós-registry, stub-providerrel futó szerződésteszt per kritikus flow (provider-kiesés → 502/partial), és az anomália 404-ág helyett a tényleges hibamód assertálása.

### [L-13] [ALACSONY] [MEGERŐSÍTETT] `/health` konstans és nincs readiness: a DB-hiány és a provider-kiesés nem detektálható

- **Hely:** `api/main.py:88-91` (statikus `{"status": "ok"}`), `lifespan` (`:30-49`) csak a CORS-wildcardot ellenőrzi; a `CityRepositoryPaths.validate_paths` (`:103-113`) **termékkódban sehol nem hívott** (`rg 'validate_paths'` → csak `tests/test_paths_config_validate_paths.py`, ami egy másik függvényt tesztel).
- **Megfigyelés:** hiányzó `data/cities.db` és `data/hungarian_settlements.db` esetén az app elindul, a `/health` 200-at ad, a keresés viszont üres listát/„nincs város” 400-at eredményez; a provider-kiesés (L-03) szintén nem jelenik meg sehol.
- **Hívási út/feltétel:** deploy/indítás hiányos adatkönyvtárral.
- **Meglévő védelem és cáfolat:** a `CityRepositoryPaths._validate_path` és a fallback-lánc (cwd/env) részben kompenzál, és a `CityRepository` fallbacket ad a magyar DB-re; ezért nem KRITIKUS/„indulás blokkolt”, hanem néma degradáció.
- **Bizonyított hatás:** nincs olyan jel, amely megkülönböztetné a „rendben fut” és a „nem tud adatot szolgáltatni” állapotot (a health-check CI is ezt a végpontot hívja).
- **Javítási irány:** `/health` maradjon liveness, mellé `/ready` a DB-elérhetőség + a registry megléte alapján (induláskor hívd a `validate_paths`-ot, fail-fast vagy `degraded` státusz).

---

## 5. Teszteredmények (ebben a futásban mérve)

| Futtatás | Parancs (rövidítve) | Eredmény |
|----------|---------------------|----------|
| Teljes pytest (izolált másolat) | `venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (`/tmp/meteo-audit-20260910T092914Z/repo`) | **1743 passed, 2 warnings in 29.00s** — 0 failed, 0 skipped, 0 error |
| CI-ekvivalens pytest + coverage | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 … pytest tests/ -p pytest_cov.plugin -p pytest_timeout -p anyio.pytest_plugin -p pytest_asyncio.plugin --cov=src --cov-config=.coveragerc -q --timeout=10 --ignore=tests/gui` | **1743 passed**, **TOTAL coverage 92.70 %** (fail-under 85 % teljesült), 63 fájl 100 %-os |
| Vitest | `cd frontend && npx vitest run` | **9 fájl / 342 teszt passed**, 1.41 s |
| Playwright | — | **BLOKKOLT** (élő stack + böngésző kell; nem izolált) |
| Izoláció igazolása | `md5sum -c db-before.md5` (futás előtti/utáni `data/*.db`), `git status --porcelain` | mindhárom DB **változatlan**, a worktree a futás előtti állapottal azonos |

**Tesztek minősége (a fentiek kontextusában):** a suite zöld és bő (1743 teszt, 92,7 % coverage), a domain/application/data rétegek valóban teszteltek; a hiányzó rész a **valós, hibás provider-szcénáriók** lefedése az API szinten (L-12). A `tests/api/api_auth_support.py` a worktree-beli auth-eltávolítás után **árva** (a `rg` szerint semmi nem hivatkozik rá, és a térkép is 0 collected tesztet mért rá).

**Observability:** nincs metrics/readiness végpont, a provider-usage/CB állapot nem jut ki (L-04), a hibák `logger.*`-ban jelennek meg (`exc_info=True` a legtöbb route-on — ez jó), de a „részleges siker” (L-08) és a csendes degradáció (L-03) nem hagy nyomot a válaszban.

---

## 6. Hipotézisek és blokkolt területek

**H1 — Latens `RecursionError` a provider-választásban (reprodukálva, de termékkódból jelenleg nem elérhető).**
`weather_client_core.py:183-189`: ha `preferred_provider` érvényes kulcs, de a provider `validate_provider()`-je `False`, a metódus `self._select_provider(None)`-t hív, ami `preferred_provider != "auto"` miatt visszahívja `_select_preferred_provider`-t → végtelen rekurzió. **Reprodukció:** `WeatherClientExtensions(preferred_provider='meteostat')` (kulcs nélkül) → `_select_provider(None)` → `RecursionError: maximum recursion depth exceeded` (lefuttatva, hálózat nélkül). **Miért hipotézis:** nincs elérhető hívási út — a termékkód sehol nem állítja a `preferred_provider`-t `"auto"`-tól eltérőre (`rg 'set_preferred_provider'` → csak teszt; a GUI worker a saját `provider_selector.py`-ját használja fallbackkel). Ez a hiányzó bekötés egyben az L-02 oka: **ha valaki bekötné a prefs-választást a kliensbe, ez a defekt azonnal élesedne** (pl. meteostat kulcs nélkül → 500 a trend/wind-rose végponton). Az L-02 javításakor ez kötelezően együtt javítandó (fallback `_select_auto_provider`-ra, a GUI `provider_selector` mintájára).

**H2 — `requests.Session` megosztása több szálon.** A `WeatherProvider.__init__` egy `requests.Session`-t tart (`weather_provider_base.py:30`), a `WeatherFetchService` viszont `max_workers=8` szállal hívja ugyanazt a klienst (`weather_fetch_service.py:114-120`). A `Session` dokumentáltan nem teljesen thread-safe. **Nem finding:** nincs reprodukált interleaving/teszt, a gyakorlatban az urllib3 pool és a nem használt cookie-jar mellett nem sikerült hibát kimutatni → konkrét interleaving vagy reprodukció szükséges.

**H3 — `meteostat` kulcs nélküli állapot.** `validate_api_source_available` (`config_validation.py:143-161`) és a `MeteostatProvider` a `METEOSTAT_API_KEY` meglététől függ; a `.env.example` csak egy placeholdert tartalmaz, és `load_dotenv` nincs a termékkódban (térkép §4.2). Nem mértem, milyen állapotban indul a szerver kulcs nélkül (a kulcs értékét nem olvasom/naplózom) → security-audit téma.

**Blokkolt területek:** nincs hálózat (élő provider-válasz, valós retry-időzítés nem mérhető) · Playwright e2e nem futott · GUI nem indult (nincs X/headless trace, F12) · `quality_gate.sh --full` nem futott (tesztet futtat és coverage-t ír; helyette a check-ekvivalensek + a CI-pytest parancs futott izolált másolatban) · `routes/hungary.py`, `routes/metadata.py`, a trend-regresszió és a wind-rose sávozás nem lett végigolvasva.

---

## 7. Elvetett jelöltek (rövid cáfolati napló)

| Jelölt | Cáfolat |
|--------|---------|
| `time_periods` korlátlan → több ezer provider-hívás | `api/dto/trend_request.py:43-52` a `{5,10,25,55}` halmazra szűr, üres/érdemi nélküli listát elutasít |
| `region_config` hiányzó kulcs → KeyError a detailed úton | mérve: `REGIONS` mindhárom kulcsa (`Hungary`, `Europe`, `Global`) tartalmazza a `batch_size`/`rate_limit_delay`/`max_cities`/`country_codes` mezőket |
| Hiányzó `.coveragerc` miatt a CI coverage lefut | a CI-ekvivalens futtatás **PASS** (92,70 %), a `fail_under=85` a `pyproject.toml`-ból érvényesül; a hiányzó fájl nem fatális |
| A CI pytest parancs elhasal (`-p anyio.pytest_plugin` ütközés) | helyben reprodukáltam, de **csak** a `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` hiányában; a CI workflow beállítja (`ci.yml` env) → nem hiba |
| `future.result(timeout=90)` hatástalan → végtelen blokkolás | a state igaz, de **van** HTTP-szintű timeout (`timeout=30` a provider-hívásokban) → nem önálló finding, beolvasztva az L-06-ba (RÉSZBEN) |
| `with sqlite3.connect(...)` kapcsolat nem záródik (`city_repository_queries.py:233,248,273`) | CPython refcount a blokk végén felszabadítja a lokálist (a `with` a tranzakciót zárja, a `__del__` a kapcsolatot); nem mértem FD-növekedést → elvetve |
| `INSERT OR REPLACE` a `weather_data`-ba duplikál | a `UNIQUE(city_id,date)` miatt helyes upsert; mért duplikált csoport: **0** |
| `city_manager_db.py:219` f-string SQL (`# nosec B608`) | a `table` érték belső whitelist (`_get_count_with`), és a téma security-audit → itt nem finding |
| PATH `ruff 0.16.2` FAIL vs. pin 0.15.10 | eszköz-/CI-téma, a térkép §3.1 már dokumentálta; nem logika/architektúra |
| A rate limiter több workerrel szorzódik | a repóban nincs több-worker deploy (nincs Dockerfile/compose/k8s, `git ls-files` a térkép szerint), egyetlen uvicorn-folyamat a dokumentált indítás |
| `analyze_multi_city_support.py` holt modul | valójában re-export forrás (`from .analyze_multi_city_support import *`), a duplikált importlista kozmetikai; nem adtam findingot |

---

## 8. Prioritási lista (csak MEGERŐSÍTETT / RÉSZBEN)

| Prioritás | ID | Severity | Státusz | Egy soros indok |
|-----------|----|----------|---------|-----------------|
| 1 | L-01 | MAGAS | MEGERŐSÍTETT | a GUI városmentés 62 957 sort (78,9 %) tett árvává a mért DB-ben, minden ismételt kiválasztással tovább romlik |
| 2 | L-02 | KÖZEPES | MEGERŐSÍTETT | a provider-választás az API-n keresztül hatástalan a tényleges adatlekérésre (két igazságforrás) |
| 3 | L-03 | KÖZEPES | MEGERŐSÍTETT | ugyanaz a provider-kiesés végpontonként 502 / 200-üres / 200-null választ ad |
| 4 | L-07 | KÖZEPES | MEGERŐSÍTETT | két városfeloldó: „Buda” → Buda (US) vs. Budapest (HU) ugyanabban az appban |
| 5 | L-12 | KÖZEPES | MEGERŐSÍTETT | az API-tesztek mockolt registry-vel futnak, a valós provider-hibaágak teszt nélkül |
| 6 | L-05 | KÖZEPES | MEGERŐSÍTETT | 3 kliens / 3 repo / külön CB állapot indulásonként |
| 7 | L-04 | KÖZEPES | MEGERŐSÍTETT | a usage/status felület strukturálisan nulla, a CB állapot nem jut ki |
| 8 | L-06 | KÖZEPES | RÉSZBEN | retry-szorzódás + hatástalan fetch-timeout, a kliens 30 s-nál elvágja (gyakoriság nem mérve) |
| 9 | L-08 | KÖZEPES | MEGERŐSÍTETT | részleges DB-írás sikeresként jelentve a GUI-ban |
| 10 | L-09 | ALACSONY | MEGERŐSÍTETT | route-szintű globális use case + holt validációs sor |
| 11 | L-10 | ALACSONY | MEGERŐSÍTETT | implementálatlan repository-port, közvetlen sqlite3 a presentationben, nincs retenció (79 824 sor) |
| 12 | L-11 | ALACSONY | MEGERŐSÍTETT | futásidőben bővülő modul-szintű trusted-path lista |
| 13 | L-13 | ALACSONY | MEGERŐSÍTETT | `/health` konstans, nincs readiness, a DB-validáció termékkódban nem hívott |

**Nem került a listára:** H1 (latens `RecursionError`) — reprodukált defekt, de jelenleg nincs elérhető hívási út; az L-02 javításával együtt kezelendő. H2 (Session thread-safety) — reprodukció nélkül hipotézis.

---

## 9. Parancsnapló (ebben a futásban)

| Parancs | Mit bizonyít | Eredmény |
|---------|--------------|----------|
| `git rev-parse HEAD`; `git status --porcelain`; `git diff --stat` | snapshot-egyezés a térképpel | SHA `c4793cdc…`, a porcelain azonos, `8 files, +3/−823` |
| `git diff src/config/api_config.py`; `git diff -U3 src/api/main.py` | worktree API-kulcs eltávolítás | 2 fájl, a auth-réteg teljes eltávolítása (HEAD 33-38, 96-176, 178-192) |
| `rg -n 'X-API-Key\|API_KEY\|auth/status' frontend/src tests/api/api_auth_support.py` | törött kliens-szerződés keresése | 0 találat → nincs hivatkozás |
| `rg -n 'get_selected_provider\|set_selected_provider' src/` | prefs-olvasók | csak `api/routes/providers.py` (5×) és `presentation/.../provider_routing.py` (5×) |
| `rg -n 'preferred_provider' src/` | fetch-oldali bekötés | a termékben mindig `"auto"`, `set_preferred_provider`-t csak teszt hív |
| `rg -n 'user_override_provider\|set_preferred_provider' src/ tests/` | override-átadás | a fetch-service 4 argumentummal hív, override nincs |
| `rg -n 'INSERT INTO\|UPDATE \|DELETE FROM\|\.commit()\|rollback' src/` (GUI kizárva) | írási pontok az API/infra rétegben | **0** — az API nem ír adatbázist |
| `python3 -c` + `sqlite3` `mode=ro` lekérdezések (`data/meteo_data.db`) | L-01 mérés | cities 60 sor (id 1..452), weather_data 79 824 sor, **62 957 árva** city_id, 148 distinct city_id, 0 duplikált (city_id,date) |
| `python3 -c` + `mode=ro` (`data/cities.db`, `data/hungarian_settlements.db`) | L-07 mérés | „Buda” → Buda(US) vs Budapest(HU); „Kecske” → nincs találat vs Kecskemét; „Győr” → 246 159 vs 130 191 fő |
| `venv/bin/python -c` (instance-számlálás `gc.get_objects()`-szel) | L-05 mérés | 3 × `WeatherClientExtensions`, 3 × `CityRepository`, 2 × `WeatherFetchService`; `is` összehasonlítások `False` |
| `venv/bin/python -c` (RecursionError reprodukció) | H1 | `RecursionError: maximum recursion depth exceeded` |
| `venv/bin/python -c` (`REGIONS` kulcsok) | elvetett jelölt | mindhárom régió tartalmazza a szükséges kulcsokat |
| `rg -n 'foreign_keys\|PRAGMA' src/` | L-01 védelem-keresés | csak `PRAGMA table_info` — FK-enforcement nincs |
| `rg -n 'circuit_breakers\|provider_usage_stats' src/` | L-04 | CB-t csak a `weather_client_core` olvassa; kifelé nem jut |
| `rg -n '_usage_service\|requests_total' src/ tests/` | L-04 író-keresés | termékkód csak olvas; a teszt monkeypatch-el |
| `rg -n 'FROM weather_data' src/` | L-10 | 0 olvasó útvonal |
| `rg -n 'delete_old_weather_data' src/ tests/` | L-10 | csak a port-deklaráció |
| `rg -n 'validate_paths' src/ tests/` | L-13 | termékkódban nincs hívás |
| `rg -c 'MagicMock\(spec=ServiceRegistry\)\|mock_services' tests/api/*.py` | L-12 | 9 fájl, 63 előfordulás |
| `rg -n 'pytest.mark.skip\|pytest.skip\|xfail' tests/` | tesztintegritás | csak könyvtár-őrző `pytest.skip`-ek (integration), nincs feltétel nélküli skip |
| `md5sum data/*.db` (futás előtt) + `md5sum -c` (után) | izoláció | mindhárom DB **változatlan** |
| `venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (izolált másolat, `/tmp/...`) | teszteredmény | **1743 passed, 2 warnings, 29.00 s** |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 … --cov=src --cov-config=.coveragerc -q --timeout=10 --ignore=tests/gui` | CI-ekvivalens kapu | **1743 passed**, **coverage 92,70 %** |
| `cd frontend && npx vitest run` | frontend tesztek | 9 fájl / **342 passed**, 1.41 s |
| `rg -n 'cov-config\|pytest\|coverage' .github/workflows/ci.yml` | CI-parancs | `--cov-config=.coveragerc`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` (a cáfolathoz) |
| `rg -n 'hottest_today' src/api` | duplikált metrika-térkép | 3 azonos másolat (`weather_adapter.py`, `single_city.py`, `multi_year.py`) — nem adtam rá findingot (jelenleg nincs drift) |
| `rg -n 'meteo_data' src/ tests/ scripts/ frontend/src` | DB-használat | írás: `gui_composition_root.py:40` + `database_manager.py`; olvasó Python-kód nincs |
| `git status --porcelain` (zárás) | worktree | csak a `docs/audit/…/02_LOGIC.md` az új fájl; minden más a futás előtti állapot |

**Környezet:** módosítás nem történt a repóban a `docs/audit/20260910T092914Z/` alá írt riporton kívül; a tesztfuttatás izolált másolatban (`/tmp/meteo-audit-20260910T092914Z/repo`) történt, a `frontend/node_modules/.vite` cache-en kívül (gitignore-olt) nem hagyott nyomot.

---

## 10. Záró `git status`

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
?? docs/
?? reasonix.toml
```

A fenti lista **azonos** a futás eleji állapottal; az egyetlen új tétel a `docs/audit/20260910T092914Z/02_LOGIC.md` (a `docs/` untracked mappa, amelyet a térkép futása hozott létre). Termékkód, teszt, séma, migráció és gépi config nem módosult.
