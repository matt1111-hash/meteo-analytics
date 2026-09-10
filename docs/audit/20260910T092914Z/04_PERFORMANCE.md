# 04_PERFORMANCE — Teljesítmény és kódminőség audit

**RUN_ID:** `20260910T092914Z`
**Mód:** read-only elemzés + izolált lokális mérés (nincs kódmódosítás, optimalizálás, hálózat, production adat)
**Bemenet:** `01_MAP.md`, `02_LOGIC.md`, a repó forrása
**Repo gyökér:** `/home/tibor/PythonProjects/meteo-analytics`
**Snapshot (ellenőrizve):** HEAD `c4793cdc9ef6161d2bcaf91d994bae2348426d78`, branch `main`; a `git status --porcelain` a térkép §1.2 listájával **azonos** (+ a `docs/` untracked audit-mappa) → nincs snapshot-eltérés, nem BLOKKOLT.
**Mérési ablak:** 2026-09-10 kb. 10:10–11:05 UTC

Minden átvett állítást (térkép, logika-audit, feltáró ügynökök) a kódban újra ellenőriztem; ahol mérhető volt, mértem. Státuszok: `MÉRT` / `STATIKUSAN IGAZOLT` / `HIPOTÉZIS` / `BLOKKOLT`.

---

## 1. Terhelési utak és mérési környezet

### 1.1 Valós terhelési utak (belépő → adathatár)

| # | Flow | Belépő | Gyakoriság / inputméret | Forrás |
|---|------|--------|------------------------|--------|
| T1 | Trend | `POST /api/analytics/trend` (`src/api/routes/analytics.py:18-39`, `run_in_threadpool`) → `CalculateTrendUseCase` → 4 szálas év-batch → `OpenMeteoProvider` 90 napos batchek → `TrendCalculator` | SPA trend-oldal alapértelmezett kérése: `time_periods=[5,10,25,55]` (`frontend/src/services/trendService.ts:113`) → **55 év, ~20 076 napi rekord**. Gyakoriság: felhasználói kattintás, **ismeretlen** | kód + mérés |
| T2 | Single-city / detailed / anomália / multi-city | `POST /api/weather/*` → `AnalyzeMultiCityUseCase` / `DetailedCityUseCase` → `WeatherFetchService` (8 worker) → `WeatherClient` → provider | max ~5 év (`MAX_DATE_RANGE_DAYS`), max `MAX_CITIES_PER_REQUEST` város; **1 827 rekord/város** 5 évre. Gyakoriság **ismeretlen** | kód |
| T3 | Multi-year batch | `POST /api/weather/multi-year-batch` → 4 szálas év-fan-out, évenként teljes T2 | ≤ 20 év (`multi_year_request.py` `max_length=20`) | kód |
| T4 | Város-keresés | `GET /api/cities/search` → `autocomplete_city_name` | billentyűleütésenként; `cities` 44 658 sor, `hungarian_settlements` 3 178 sor | kód + DB-számlálás |
| T5 | GUI trend | `trend_data_processor/fetcher.py:40-63` szekvenciális évenkénti fetch → GUI `calculator.py` | 55 év, felhasználói kattintás, GUI nem futott | kód |
| T6 | GUI chart tooltip | `tooltip_mixin/event_handlers.py` `motion_notify_event` → `point_finder.py:56-64` | minden egérmozgás a diagram felett | kód + mérés |
| T7 | Tesztsuite | `pytest tests/` 1 743 teszt | minden CI/pre-commit futás | mérés |

**Nincs** scheduler, consumer, cron vagy háttér-worker a repóban (térkép §5.4), tehát a terhelés kizárólag felhasználó-vezérelt; a fenti flow-k gyakorisága **nem mért, nem becsült**.

### 1.2 Mérési környezet

| Tétel | Érték |
|-------|-------|
| Gép | 13th Gen Intel Core i5-13400, 16 logikai CPU, 31 GB RAM, Linux 7.0.0-31-generic |
| Interpreter | `venv/bin/python` CPython 3.12.3; sqlite 3.45.1; pandas 3.0.1, numpy 2.3.1, scipy 1.17.1, matplotlib 3.10.5 |
| Bemenetek | **szintetikus** (véletlen, seed-elt) napi rekordok; a valós `data/*.db` fájlok **read-only** (`mode=ro` URI) vagy memóriabeli `backup()` másolaton; HTTP **mockolva** (nincs hálózat), a kód `time.sleep` hívásai **valósak** |
| Ismétlés | ahol `n=` szerepel, annyi futás; **medián** + min/max, ms |
| Repó-eszközök | a repóban **nincs** benchmark-, profiler- vagy timing-eszköz (Makefile, pyproject, CI, scripts átnézve) → saját inline `time.perf_counter` mérések |
| Izoláció | a pytest futás előtt/után `md5sum data/*.db` **azonos**; `git status --porcelain` változatlan; `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider` |

---

## 2. Mért baseline-ok

| ID | Mérés | Eredmény |
|----|-------|----------|
| B1 | `import src.api.main` (3 futás) | **232 / 253 / 257 ms**; nehéz könyvtár (pandas/numpy/scipy/matplotlib/geopandas/plotly/PySide6) **nem** töltődik importkor (`sys.modules` ellenőrzés: üres lista) |
| B2 | `build_service_registry()` (lifespan) | ügynök mérése **0,62 s** (2× `SELECT COUNT(*)`); nem ismételtem, tájékoztató |
| B3 | Open-Meteo, 1 város × 5 év, HTTP mockolva | **21 HTTP-hívás, 1 827 rekord, 12,0 s fal-idő** (tisztán `time.sleep`) |
| B4 | Trend UC `_fetch_weather_data`, 55 év, HTTP mockolva, 4 szál | **55 év-batch, 274 HTTP-hívás, 20 076 rekord, 35,2 s fal-idő** |
| B5 | `TrendCalculator.calculate_multiple_periods([5,10,25,55])` 20 076 rekordon | **4 905 ms medián** (4 815–5 043, n=5) — tiszta CPU |
| B6 | `TrendDataProcessor.prepare_dataframe` 20 076 rekordon | **2 715 ms** (soronkénti `pd.to_datetime`); vektorizált ekvivalens **6,2 ms** |
| B7 | `aggregate_monthly` 20 076 rekordon | 3 ms |
| B8 | periódus-szűrő list-comprehension ×4 (`trend_calculator.py:154-158`) | inline `strftime`: **44,0 ms**; kiemelve: **2,6 ms** (n=10) |
| B9 | `OpenMeteoProvider._process_response` 90 nap × 15 mező | 0,06 ms (×224 batch ≈ 14 ms / 55 év) |
| B10 | `WindRoseCalculator.calculate` | 365 rekord 0,4 ms; 1 827 rekord **2,0 ms**; 20 076 rekord 20,8 ms |
| B11 | Detailed-city 4 metrika kinyerése 1 827 rekordon (`process_weather_results` + transform + `to_dict`) | **20 ms** összesen (~5 ms/metrika) |
| B12 | Autocomplete `LOWER(city) LIKE '%q%'` 44 658 soron (memória-másolat) | `%bu%` 0,18 ms; `%buda%` **12,9 ms**; `%zz%` 6,0 ms (n=30); plan: `SCAN cities USING INDEX idx_population` |
| B13 | `get_cities_by_names` korrelált al-lekérdezés | 1 név **11,0 ms**; 5 név 13,3 ms; 5 gyakori név (pl. „springfield” 12 sor) **25,1 ms** |
| B14 | `sqlite3.connect` + `PRAGMA table_info` fájlról | 0,093 ms; connect + autocomplete hidegen 0,28 ms |
| B15 | `CityManagerStats.find_city_by_name` valós DB-n | találat („Budapest”, „Kecske”, „Buda”) **0,2 ms**; nincs találat („Zzzqq”) **10,6 ms** (max 13,3; n=20); `get_city_manager_port()` 26 ms |
| B16 | Rate-limiter `_is_limited` 100 / 10 000 / 10 001 követett klienssel | medián **1 µs** mind; max 67 µs / 1 871 µs / 1 767 µs (n=200) |
| B17 | GUI tooltip pontonkénti `transData.transform` (Agg backend) | 1 827 pont: 8 ms/sorozat → **25 ms/egérmozgás 3 sorozattal**; 20 076 pont: 87 ms → **262 ms/egérmozgás**; vektorizált: 0,04 / 0,24 ms |
| B18 | Teljes pytest (1 743 teszt, cache/bytecode/cov nélkül) | **26,92 s, 1743 passed**; a 4 leglassabb teszt **14,4 s** (6,00 + 3,00 + 3,00 + 2,40 s) |
| B19 | Frontend build-artefakt (`frontend/build/`, **2026-07-25**, nem ennek a snapshotnak a buildje) | `plotly-*.js` 4 598 KB, `recharts` 375 KB, `vendor` 179 KB, `leaflet` 165 KB + 15 KB css, `index` 96 KB |

---

## 3. Meglévő optimalizációk (bekötve, kóddal igazolva)

| Megoldás | Hely | Mit ad |
|----------|------|--------|
| Város-szintű párhuzamosság | `weather_fetch_service.py:114-127` `ThreadPoolExecutor(max_workers=8)` + `as_completed` | több város egyszerre |
| Év-szintű párhuzamosság | `calculate_trend.py:142` (4 szál), `routes/multi_year.py:70` (4 szál) | évek egyszerre |
| `run_in_threadpool` a blokkoló use case-ek köré | `analytics.py:29`, `weather.py`, `multi_year.py:77`, `anomalies.py:138,145`, `wind_rose_part3.py:141`, `cities.py:32` | az event loop nem blokkol a fetch alatt |
| `requests.Session` (connection pooling) | `weather_provider_base.py:30` | TCP-újrahasználat providerenként |
| HTTP-timeout minden provider-hívásban | `openmeteo_provider.py:169-170`, `meteostat_provider.py:141` (30 s) | nincs végtelen blokkolás |
| Circuit breaker (lockolt) | `resilience/circuit_breaker.py`, `weather_client_core.py:41-48` | provider-kiesésnél gyors fail |
| Regresszió havi aggregátumon | `trend_statistics.py:33` `scipy.stats.linregress` ~660 ponton, nem 20 076-on | vektorizált statisztika |
| `list.extend` merge (nincs `pd.concat` ciklusban, nincs `deepcopy`) | `weather_fetch_service.py:96,127`, `calculate_trend.py:149`, `openmeteo_provider.py:132` | O(n) összefűzés |
| Bounded rate-limit tár + eviction | `rate_limit.py:36-92` | memória korlátos, mért költség 1 µs |
| Lazy pandas/numpy import az API-n | factories függvény-szintű importjai; B1 | 250 ms cold import |
| Frontend route-szintű `React.lazy` + `manualChunks` | `App.tsx:8-18`, `vite.config.ts` | a 4,6 MB plotly csak a `WindyDaysView` chunkkal jön (build-artefakt: az `index` chunk statikusan csak `leaflet`, `vendor`, `rolldown-runtime` importál) |
| Frontend 30 s timeout + retry | `apiClient.ts:74,119-126` | kliens nem lóg végtelenül |
| SQLite indexek | `cities`: `idx_population`, `idx_country_code`, `idx_coordinates`… (8 db); `hungarian_settlements`: `idx_name`, `idx_megye`, `idx_jaras`, `idx_population`; `weather_data`: `(city_id,date)` | a `LIMIT`-es keresések az `idx_population` mentén korán megállnak (B12 `%bu%` 0,18 ms) |
| Megyelista memoizálása | `city_manager_hungarian.py:77-90` | egyszeri lekérdezés |
| De-N+1 tömeges lekérés | `city_manager_stats.py:197-230` `get_settlements_bulk` ← `hungary.py:102` | egy query a stations végponton |

**Nincs:** válasz-cache a provider-hívásokra (`data/cache/`, `data/climate_cache/` üres, csak a `paths_config.py` hozza létre; `grep cache|lru_cache|memo` a weather/use_case/analytics fákon: 0 találat), kérés-szintű cancellation, teljes kérés-deadline (02_LOGIC L-06).

---

## 4. Aktív performance findingek

### [P-01] [MAGAS] [MÉRT] Az alapértelmezett trend-lekérés hálózat nélkül is 35 s: 90 napos Open-Meteo batchek + 0,6 s fix alvás batchenként, cache nélkül — a SPA 30 s-os timeoutja fölött

- **Hely:** `src/infrastructure/weather/openmeteo_provider.py:41-42` (`max_days_per_request = 90`, `batch_delay = 0.6`), `:104-143` (szekvenciális batch-ciklus, `time.sleep(self.batch_delay)` a 136. sorban), `:166` + `weather_provider_base.py:63-70` (`_rate_limit_check`, 0,1 s); `src/application/use_cases/calculate_trend.py:62-66` (55 év default), `:142-149` (4 szál), `:160-168` (366 napos év-batchek); `frontend/src/services/trendService.ts:113` (`TIME_PERIODS = [5,10,25,55]`), `frontend/src/services/apiClient.ts:74` (`timeout: 30_000`).
- **Elérhető flow:** T1 — a SPA `/trend-analytics` oldal alapértelmezett kérése; T2 (5 éves single/detailed/anomália), T3 (multi-year), T5 (GUI trend) ugyanazon a provider-batchelésen mennek át.
- **Mérés (B3, B4, HTTP mockolva, alvások valósak):** 1 város × 5 év → **21 HTTP-hívás, 12,0 s**; trend 55 év → **274 HTTP-hívás, 35,2 s** 4 szálon. Levezetés: 366 napos év-batch / 90 nap = 5 HTTP + 4×0,6 s alvás + 5×0,1 s min-intervallum ≈ 2,4 s alvás/év; 55 év ≈ 132 s alvás / 4 szál ≈ 33 s + a nem lockolt `_rate_limit_check` ütközései → mért 35,2 s. Ehhez jön a P-02 CPU-ideje (4,9 s) → **≈ 40 s** kérésenként **nulla** hálózati késleltetés mellett.
- **Aktiváló feltétel:** bármely 90 napnál hosszabb dátumtartomány; a trend-oldalon **minden** alapértelmezett kérés.
- **Meglévő optimalizáció / cáfolat:** a 4 szálas év-fan-out és a fetch-szintű 8 worker **létezik**, de a batch-ciklus egy városon belül szekvenciális, és az alvás konstans, nem adaptív (nincs 429-visszajelzés-alapú throttling). Cache nincs (§3). Cáfolatkísérlet: a `time_periods` validátor a `{5,10,25,55}` halmazra szűr, tehát a max 55 év nem csökkenthető kliensről; a `start_date` megadásával rövidíthető, de a SPA nem adja meg. A frontend csak 5xx-re retry-zik, timeoutra nem (`apiClient.ts:119-126`), és a szerver a kliens lemondása után is végigdolgozza a kérést (nincs cancellation).
- **Bizonyított hatás:** a trend végpont alapértelmezett bemenetre determinisztikusan a kliens-timeout fölött válaszol (35,2 s alvás-padló > 30 s), tehát a SPA trend-oldala hálózati késleltetés nélkül sem tud sikeres választ kapni; a 5 éves single-city út 12 s alvás-padlóval indul. **Nem bizonyított:** a valós Open-Meteo válaszidő és az, hogy az Open-Meteo API elfogad-e 90 napnál hosszabb tartományt egy kérésben (hálózat nélkül nem ellenőrizhető → §6 H-P6); a 90 nap / 0,6 s értékek forrása a kódban nincs dokumentálva.
- **Effort / irány:** közepes. (1) A batch-méret és az alvás forrásának tisztázása (H-P6), nagyobb batch vagy alvás nélküli, 429-re reagáló throttling; (2) év-batch szintű válasz-cache (a történelmi adat immutábilis; a `data/climate_cache` erre van előkészítve); (3) a trend-oldal fokozatos betöltése (először 5 év) vagy a kliens-timeout összehangolása a szerver-oldali felső korláttal + cancellation (02_LOGIC L-06 javítási irányával együtt).

### [P-02] [MAGAS] [MÉRT] Soronkénti `pd.to_datetime` a trend DataFrame-építésben: 2,7 s / 20 076 rekord, periódusonként újraépítve → 4,9 s CPU kérésenként (440× a vektorizált költség)

- **Hely:** `src/infrastructure/analytics/trend_data_processor.py:19-43` (`prepare_dataframe`: `for record in weather_data: … pd.to_datetime(record["date"])`), hívó: `trend_calculator.py:75` minden periódusra (`:150-163` ciklus); a loop-invariáns `calculated_end.strftime()` a `:154-158` comprehensionben. **Ugyanez a minta a GUI másolatban:** `src/presentation/gui/trend_analytics/trend_data_processor/calculator.py:13`.
- **Elérhető flow:** T1 (API trend, `run_in_threadpool` → anyio worker szál), T5 (GUI trend worker).
- **Mérés (B5, B6, B8):** `prepare_dataframe` 20 076 rekordon **2 715 ms**, vektorizált ekvivalens (`pd.to_datetime(series)`) **6,2 ms**; a teljes `calculate_multiple_periods([5,10,25,55])` **4 905 ms** (a 4 periódus összesen ≈ 34 700 rekordot dolgoz fel újra: 1 826 + 3 652 + 9 131 + 20 076); a `strftime`-os szűrő 44 ms vs 2,6 ms kiemelve.
- **Aktiváló feltétel:** az alapértelmezett 55 éves trend; a költség lineáris a rekordszámmal és a periódusok számával (O(P·N), P=4).
- **Meglévő optimalizáció / cáfolat:** a regresszió maga a havi aggregátumon fut (~660 pont, 3 ms), tehát a statisztika nem a szűk keresztmetszet; kizárólag a per-rekord Python-szintű pandas-hívás az. Nincs memoizáció a periódusok között (a 55 éves DataFrame tartalmazza a többit).
- **Bizonyított hatás:** kérésenként ~4,9 s CPU egy anyio worker szálon (default 40 szál) + a P-01 fal-idejéhez adódik. **Nem bizonyított:** a GUI másolat futásideje (GUI nem futott; a kód azonos minta).
- **Effort / irány:** alacsony. Egyszeri `pd.DataFrame(weather_data)` + vektorizált `pd.to_datetime` + periódusonként `DatetimeIndex` szeletelés; a `strftime` kiemelése a comprehensionből (1 sor). A GUI másolattal együtt javítandó (Q-01).

### [P-03] [KÖZEPES] [MÉRT] GUI tooltip: pontonkénti matplotlib `transData.transform` és `print()` minden egérmozgásra — 25 ms (5 év) … 262 ms (55 év) mozgásonként

- **Hely:** `src/presentation/gui/charts/tooltip_mixin/point_finder.py:56-64` (`for index, (x_val, y_val) in enumerate(zip(...)): self._mixin.ax.transData.transform((x_val, y_val))`), `charts/temperature_chart/tooltip_handler_part1.py:33-45` (azonos minta); hívó: `tooltip_mixin/event_handlers.py:57` (`motion_notify_event`), `:60` és `:65` `print(f"🎯 DEBUG: …")` minden találatnál.
- **Elérhető flow:** T6 — GUI hőmérséklet-diagram, egérmozgás a diagram felett; 3 sorozat (`temp_mean/max/min`).
- **Mérés (B17, Agg backend, ugyanaz a transzformációs matek):** 1 827 pont × 3 sorozat ≈ **25 ms**; 20 076 × 3 ≈ **262 ms** egérmozgásonként; a vektorizált `transform((N,2))` 0,04 / 0,24 ms.
- **Aktiváló feltétel:** többéves adat a diagramon; az egérmozgás-esemény frekvenciája (tipikusan több tíz/s) → 55 évnél a UI-szál telítődik.
- **Meglévő optimalizáció / cáfolat:** a `_last_tooltip_point` csak a **megjelenítést** deduplikálja, a keresés minden mozgásra lefut; nincs throttling/debounce a handlerben. A Qt-backend költségét (repaint) nem mértem — a fenti szám alsó korlát.
- **Bizonyított hatás:** a GUI-szálon egérmozgásonként 25–262 ms tiszta Python-munka. **Nem bizonyított:** a felhasználói észlelés (GUI nem futott).
- **Effort / irány:** alacsony. Egy vektorizált `transform` + `np.argmin`; a `print()` hívások eltávolítása (stdout írás a hot pathon); opcionális esemény-throttling.

### [P-04] [ALACSONY] [MÉRT] Blokkoló SQLite-hívások az event loopon két route-ban (11–25 ms / kérés)

- **Hely:** `src/api/routes/anomalies.py:137` (`cities = _get_city_or_404(...)` → `get_cities_by_names`, nincs `run_in_threadpool`), `src/api/routes/wind_rose_part3.py:140` (`_resolve_city_coordinates` → `find_city_by_name`), `:144-145` (`_extract_daily_data` + `_process_wind_rose_data`); `src/api/routes/providers.py:76,113,181,212` (`UserPreferences` JSON-olvasás, `:182` atomikus írás az event loopon).
- **Elérhető flow:** T2 anomália, wind-rose, provider végpontok.
- **Mérés:** `get_cities_by_names` **11,0–25,1 ms** (B13); `find_city_by_name` 0,2 ms találatnál, **10,6 ms** hiánynál (B15); szélrózsa-számítás 2,0 ms 5 évre (B10).
- **Aktiváló feltétel:** minden kérés ezeken a végpontokon; a blokkolás időtartama alatt az event loop más kérést nem szolgál ki.
- **Meglévő optimalizáció / cáfolat:** ugyanezek a route-ok a fetch-részt már `run_in_threadpool`-ba teszik; a városfeloldás kimaradt. A költség korlátos (≤ 25 ms), ezért ALACSONY; egyetlen uvicorn-folyamat + alacsony forgalom mellett nem mérhető felhasználói hatás.
- **Bizonyított hatás:** 11–25 ms event-loop blokkolás kérésenként. **Nem bizonyított:** konkurens kérések alatti latencia-növekedés (nem mértem terhelés alatt).
- **Effort / irány:** alacsony — a városfeloldást és a JSON I/O-t is a threadpoolba tenni, a wind-rose adatkinyerést a fetch-tel egy `run_in_threadpool`-ba vonni.

### [P-05] [ALACSONY] [MÉRT] Tesztsuite: 4 teszt 14,4 s-ot valós `time.sleep`-pel tölt (a 26,9 s-os suite 53 %-a), mert a retry-késleltetés nem injektálható

- **Hely:** `src/infrastructure/weather/weather_client_core.py:51` (`self.retry_delay = 1.0` hardcode), `:224-234` (lineáris backoff `1 s + 2 s` provider-enként); `openmeteo_provider.py:42,136` (`batch_delay = 0.6`); tesztek: `tests/data/test_weather_client_core_new_part3.py` (nincs `sleep`-patch), `tests/data/test_openmeteo_provider_part2.py::test_get_weather_data_batched_handles_365_day_period`.
- **Mérés (B18):** `--durations`: 6,00 s (mindkét provider hibázik: 2×3 s), 3,00 s, 3,00 s (fallback: 1 provider retry-lánca), 2,40 s (365 nap = 5 batch × 0,6 s − 1); összesen **14,4 s** a 26,92 s-ból.
- **Aktiváló feltétel:** minden teljes suite-futás (CI `ci.yml`, `health-check.yml`, pre-commit pytest hook).
- **Meglévő optimalizáció / cáfolat:** a `WeatherFetchConfig` (`config_settings.py:15-21`) env-ből állítható `retry_delay`-t ad a fetch-service-nek, de a **kliens-szintű** `retry_delay` és a provider `batch_delay` nem ezen az úton jön; a tesztek ezért csak `time.sleep` monkeypatch-csel gyorsulnának, amit a 4 lassú teszt nem tesz.
- **Bizonyított hatás:** +14,4 s minden CI/pre-commit futáson. Ez karbantarthatósági/CI-költség, **nem** runtime-hatás.
- **Effort / irány:** alacsony — a késleltetés injektálható (konstruktor-paraméter vagy `sleep` callable), a tesztekben 0-ra állítva. Tesztet nem szabad módosítani a spec-ellen; itt a termékkód tesztelhetősége hiányzik.

---

## 5. Kódminőségi findingek (a sebességtől külön)

### [Q-01] [MAGAS] [STATIKUSAN IGAZOLT] A trend-statisztika két független implementációban él (API vs GUI), azonos copy-paste kommentekkel, eltérő küszöb-reprezentációval; a GUI-másolat tesztelhetetlen és teszteletlen

- **Hely:** A: `src/infrastructure/analytics/trend_statistics.py:18-91` + `trend_data_processor.py:19-75` + `trend_calculator.py:40-41` (nevesített konstansok `MIN_DAILY_RECORDS=30`, `MIN_MONTHLY_POINTS=6`, `MIN_DAYS_PER_MONTH=5`); B: `src/presentation/gui/trend_analytics/trend_data_processor/calculator.py:9-118` (ugyanaz a `pd.to_datetime` soronként a 13. sorban, `< 30` / `>= 5` / `< 6` inline literálok `# noqa: PLR2004`-gyel a 23/44/45. sorban, `stats.linregress` a 66. sorban, a `# r_squared via SS — sklearn r2_score convention` komment szó szerint azonos a `trend_statistics.py:44`-gyel).
- **Hívók:** A ← `factories.py` → `CalculateTrendUseCase` → API; tesztelve (`tests/domain/analytics/test_trend_*`). B ← `trend_data_processor/core.py` → `trend_worker.py` → GUI tab; a `pyproject.toml` coverage-omitja a `src/presentation/gui/*`-ot, a `tests/` nem hivatkozik rá.
- **Szándékos variáns kizárása:** a CI-visszatérési alak eltér (A szimmetrikus tuple, B teljes alsó/felső sáv a rajzoláshoz) — ez szándékos; a matematika, a fallback (`np.std(y) * 0.5` mindkettőben, naplózás nélkül), a p-küszöbök (0,001/0,01/0,05) és a `slope*12*10` évtized-konverzió azonos, de két helyen. A szignifikancia-címkék eltérnek (A angol, B magyar).
- **Konkrét kockázat:** egy küszöb- vagy regressziós javítás az egyik helyen (pl. a P-02 javítása) a másikban nem érvényesül; az API és a desktop GUI ugyanarra a bemenetre eltérő trendet adhat, és a GUI-oldal hibája teszt nélkül marad.
- **Effort / irány:** közepes — a GUI a domain/infrastructure `TrendCalculator`-t használja (port már létezik: `TrendCalculatorPort`), a rajzoláshoz külön adapter adja a sávot.

### [Q-02] [KÖZEPES] [STATIKUSAN IGAZOLT] `analyze_wind_patterns`: két élő implementáció — a GUI az egyiket futtatja, a tesztek a másikat

- **Hely:** A: `src/application/services/wind_pattern_analyzer.py:63`; B: `src/infrastructure/analytics/wind_analysis_service.py:68` (saját docstringje: „compatibility implementation keeps historical patch points … while the application layer owns the same orchestration logic”), B importálja A privát segédfüggvényeit, de a fő függvényt újraírja; eltérő naplózás (A: induló log; B: sebességtartomány + befejezés log).
- **Hívók:** A ← `application/services/wind_analysis_service.py` ← `presentation/gui/results_panel/windy_days_tab/handlers.py` (termék). B ← `src/analytics/wind_analysis.py` ← csak tesztek (`tests/analytics/test_wind_analysis.py`, `tests/domain/analytics/test_wind_analysis_service.py`, `test_wind_analysis_coverage.py`, `tests/test_wind_analysis.py`). Termékkódból a `src/analytics/wind_analysis.py`-t **semmi** nem importálja.
- **Kockázat:** a szállított út (A) lefedettsége a B-re írt tesztekből nem következik; a két törzs már drifted.
- **Effort / irány:** alacsony — B törlése vagy tiszta re-exportra cserélése, a tesztek átirányítása A-ra (a tesztfájlok módosítása spec-döntés, nem ennek az auditnak a dolga).

### [Q-03] [KÖZEPES] [STATIKUSAN IGAZOLT] 11 árnyékolt `.py` modul: a csomag mindig nyer, a fájlok elérhetetlenek, `# mypy: ignore-errors`-szal statikus vakfoltot képeznek

- **Hely:** a térkép §4.3 11 ütközése (`weather_data_bridge.py`, `charts/wind_rose_chart.py`, `charts/base_chart.py`, `trend_analytics/trend_data_processor.py`, `windows/main_window_actions.py`, `controller/weather_data_handler.py`, `results_panel/{windy_days_tab,quick_overview_tab,tab_manager}.py`, 2× `ui_builder.py`). `importlib.util.find_spec` mind a 10 feloldhatóra a **csomag** `__init__.py`-t adja (a 11. körkörös importba fut — szintén a csomagot tölti). Tartalmuk 5–9 soros re-export, több önmagára hivatkozó importtal (`weather_data_bridge.py:4` a saját modulútját importálja).
- **Hívók:** `tests/` 0 hivatkozás a modulutakra; a `results_panel/__init__.py` `import_module(".tab_manager")` is a csomagot kapja.
- **Kockázat:** a mypy 611 vs 622 fájl (térkép §3.2) ebből ered; egy jövőbeli szerkesztés ezekben a fájlokban **semmire nem hat**, a 8 statikus „ön-él” ciklus (térkép §4.4) is innen jön.
- **Effort / irány:** triviális — a 11 fájl törlése (0 runtime-hatás).

### [Q-04] [KÖZEPES] [STATIKUSAN IGAZOLT] A route-teszt mockolt portja elrejti, hogy `GET /api/hungary/settlements` (megye nélkül) egy nem implementált metódust hív → 500

- **Hely:** `src/api/routes/hungary.py:72` `city_manager.get_cities_for_region("Hungary", limit=limit)`; a `CityManagerPort` deklarálja (`domain/ports/city_weather_ports.py:36`), de a registry-be kötött `CityManagerStats` **nem** implementálja (`hasattr(CityManagerStats, "get_cities_for_region") → False`, futtatva). A teszt `tests/api/test_hungary_route.py:105,123,226` a portot `MagicMock`-olja, ezért zöld.
- **Kockázat:** ez a 02_LOGIC L-12 (mockolt registry) konkrét következménye: egy éles végpont-ág `AttributeError` → a `hungary.py:164` általános kivételkezelője → HTTP 500. **Logikai hiba**, itt a tesztelhetőségi vakfolt miatt szerepel; a severity-t a logika-audit kategóriájában külön kell megítélni.
- **Effort / irány:** alacsony — a metódus implementálása a `CityManagerStats`-ban vagy a route átirányítása a meglévő `query_hungarian_all`-ra; legalább egy valós-registry szerződésteszt.

### [Q-05] [KÖZEPES] [STATIKUSAN IGAZOLT] Holt kód és teszt-által-életben-tartott kód

| Tétel | Hivatkozás-ellenőrzés (src/tests/scripts/Makefile/pyproject/.importlinter/.github/dinamikus import) | Verdikt |
|-------|------------------------------------------------------------------------------------------------------|---------|
| `src/presentation/api/` (csak 1 soros `__init__.py`) | 0 találat | **holt** |
| `tests/api/api_auth_support.py` | 0 találat; nem illeszkedik a `python_files` mintára | **holt** (a worktree auth-törlése után árva; térkép §5.2, 02_LOGIC §5) |
| `src/infrastructure/anomaly/anomaly_profile_manager.py` ↔ `anomaly_demo.py` | egymást importálják (statikus ciklus, térkép §4.4 #2), **más importőr nincs**; a termék az `anomaly_storage`/`anomaly_types`/`anomaly_profile/manager` modulokat közvetlenül használja | **holt pár** |
| `src/analytics/wind_analysis.py` (3 lépéses re-export lánc) | csak 3 tesztfájl | teszt-által-életben-tartott |
| `src/api/routes/wind_rose.py::get_wind_rose` wrapper (`:15-20`, dekorátor nélkül) | a regisztrált handler a `wind_rose_part3.py:133` (`@router.post`); a wrappert **csak** `tests/api/test_wind_rose_route_endpoints.py` (5 hívás) hívja | a tesztek egy olyan függvényt tesztelnek, amit a szerver sosem futtat |
| `src/infrastructure/city_manager/city_manager_demo.py` | csak `tests/test_city_manager_demo.py` (`is not None`, `callable`, `__all__` assertek) | coverage-párnázás |
| 4× `demo.py` (`gui/demos/map_tab_demo.py`, `map_view/demo.py`, `hungarian_location_selector/demo.py`, `trend_analytics_tab/demo.py`) | csak saját `__init__`/`__main__` | kézi QA-harness lehet (szándék nem dokumentált) → nem minősítem holtnak |
| `*_part1/2/3` fájlok (33 db) | mind bekötve sibling `__init__`/`_support` útján | **élő**; ára a `from … import *` + `# ruff: noqa: F401, F403` (pl. `wind_rose.py:1,12`), ami a statikus elemzést vakítja |

- **Effort / irány:** alacsony — a holt tételek törlése; a wind-rose wrapper-tesztek átirányítása a regisztrált handlerre.

### [Q-06] [KÖZEPES] [STATIKUSAN IGAZOLT] Hibakezelési aszimmetria: az `application` (10/10) és `infrastructure` (21/21) `except Exception` kivétel nélkül üres/alapértelmezett értékkel nyel, az `api` (17/17) mindig `HTTPException`-né alakít

- **Számok (grep, ellenőrizve):** domain 4, application 10, infrastructure 21, api 17, presentation 266 `except Exception`; bare `except:` 0.
- **Legkockázatosabb helyek (olvasva):**
  1. `trend_statistics.py:89-91` **naplózás nélkül** hamis konfidencia-intervallumot ad (`np.std(y)*0.5`) bármely hibára; ugyanez a GUI-másolatban `calculator.py:114-116` (Q-01).
  2. `calculate_trend.py:186-188` egy sikertelen év-batch `[]`-ként tér vissza → a trend hiányos adaton fut, jelzés nélkül (02_LOGIC L-03 család).
  3. `anomaly_storage.py:121-123` a backup-hiba `warning`, a végrehajtás **továbbmegy a felülírásba**.
  4. `wind_pattern_analyzer.py:107-109` és a duplikátum `wind_analysis_service.py:115-117`: a teljes elemzés hibája „0 szeles nap” eredménnyel azonos.
  5. `analyze_multi_city.py:180-182`, `detailed_city_use_case.py:117-119`: transform-hiba → a város csendben kimarad.
- **Kockázat:** a 200-üres és a hiba megkülönböztethetetlensége (02_LOGIC L-03) itt gyökerezik; a hibák tesztelhetősége is romlik (a teszt nem tud különbséget tenni).
- **Effort / irány:** közepes — hibapolitika rétegenként (Result-típus/kivétel-kategória felfelé), a CI-fallback naplózása vagy `None` visszaadása.

### [Q-07] [ALACSONY] [MÉRT + STATIKUSAN IGAZOLT] Autocomplete: az „indexelt” ág holt a szállított DB-kkel, az index-script indexét a planner nem is használná, és hívásonként 2 extra PRAGMA-kapcsolat nyílik

- **Hely:** `src/infrastructure/repositories/city_repository_queries.py:148-218` (`autocomplete_city_name`, docstring: „prefix match (indexed)”), `:155-156,185-187` (`_has_column` ×2 → `:220-241` új `sqlite3.connect` + `PRAGMA table_info` hívásonként), `scripts/add_city_name_index.py` (a `city_lower`/`name_lower` oszlop + index, **nem futott** a worktree DB-ken: `sqlite_master` szerint nincs ilyen oszlop/index).
- **Mérés:** a memóriabeli másolaton létrehozott `idx_city_lower` mellett a `city_lower LIKE 'bu%'` terve továbbra is `SCAN cities USING INDEX idx_population` (a LIKE-prefix optimalizáció BINARY collation + case-insensitive LIKE mellett nem alkalmazható; `PRAGMA case_sensitive_like=ON` mellett lesz csak `SEARCH … (city_lower>? AND city_lower<?)`); a `get_cities_by_names` indexelt változata 11 ms → ~0 ms. A jelenlegi költség kicsi (B12: 0,2–13 ms; B14: 0,09 ms/PRAGMA).
- **Kockázat:** félrevezető docstring + soha nem futó ág + egy migrációs script, ami az ígért gyorsítást a jelen lekérdezés-alakkal nem hozná; a két PRAGMA-kapcsolat/keresés felesleges (a séma futásidőben nem változik).
- **Effort / irány:** alacsony — a séma-próba egyszeri (konstruktorban), a LIKE-ág `COLLATE NOCASE` vagy `case_sensitive_like`; a `get_cities_by_names` korrelált al-lekérdezése `GROUP BY`-ra cserélhető, ha a script indexe él.

### [Q-08] [ALACSONY] [STATIKUSAN IGAZOLT] Négy egymásnak ellentmondó szél-küszöbtábla ugyanarra a Beaufort-fogalomra

- **Hely:** `presentation/gui/charts/wind_chart/wind_categories.py:11-14` (43/61/90/119 km/h „Beaufort 6-7 / 8-9 / 10-11 / 12”), `presentation/gui/results_panel/utils/wind_constants.py:25-28` (50/70/100/120 „Beaufort 6-7 / 8 / 10 / 12”), `presentation/gui/map/map_constants.py:123` (`BEAUFORT_COLOR_STEPS` 6…62), `presentation/gui/utils/constants/anomaly_constants.py:37-42` (30…150); a domain `wind_rose_calculator.py:52` `SPEED_BINS` [0,25,50,70,100,120] ötödik, más célú sávozás. A `WINDY_DAY_THRESHOLD_KMH = 43.0` (`domain/analytics/wind_models.py:10`) és a `WINDY_THRESHOLD_GUSTS = 43.0` (`wind_constants.py:32-33`) egyezik, de két rétegben duplikált.
- **Kockázat:** ugyanaz a km/h a GUI különböző fülein más kategóriát/címkét kap; küszöb-módosításnál 4 helyet kell szinkronban tartani. Szándékos variáns (más UI-cél) részben magyarázza a színlépcsőt, de a „Beaufort 8 = 61 vs 70 km/h” ellentmondás nem szándékos.
- **Effort / irány:** alacsony — egy domain-szintű Beaufort-tábla, a GUI-k onnan származtatnak.

### [Q-09] [ALACSONY] [STATIKUSAN IGAZOLT] Erőforrás-lezárás hiányos helyek (korlátos, nem növekvő)

| Hely | Probléma |
|------|----------|
| `presentation/gui/controller/database_manager.py:167-188`, `:211-268`, `:93-98` | `sqlite3.connect` és `close()` a `try` belsejében; az `except` ág nem zár → hibánál nyitva marad (GUI, hibaút) |
| `presentation/gui/workers/sql_query_worker.py:70-99` | 4 szétszórt `close()`, egyik sincs `finally`-ban |
| `infrastructure/city_manager/city_manager_db.py:55-92`, `:252-265` | thread-local kapcsolatok szálanként; a `close()` csak a hívó szál párját zárja; a lifespan a registryt `del`-lel dobja, `close()`-t nem hív → legfeljebb 2 × (anyio 40 worker + loop) kapcsolat a folyamat élettartamára (**korlátos**, ezért nem perf-finding) |
| `infrastructure/weather/weather_provider_base.py:30` | `requests.Session` sosem záródik (`session.close` 0 találat); 3 kliens × 2 provider = 6 session a folyamat élettartamára (korlátos) |
| `presentation/gui/dialogs/anomaly_settings_dialog/core.py:48,120` | `preview_timer` indul, nincs `stop()`/cleanup-regisztráció |
| `presentation/gui/map/map_interactions.py:99` | `httpd.shutdown()` után nincs `server_close()` |

- **Meglévő védelem:** `presentation/gui/cleanup_manager.py:82-195` központi QThread/QTimer leállítás; `ThreadPoolExecutor` mind a 3 helyen `with`-blokkban; `open()` mindenhol `with`-tel.
- **Effort / irány:** alacsony — `try/finally` vagy `contextlib.closing`; a registry-shutdown hívja a `CityManager.close()`-t és a provider-session `close()`-t.

### [Q-10] [ALACSONY] [STATIKUSAN IGAZOLT] Konfiguráció és globális állapot: `APIConfig` lock csak írók között, `CORS_ORIGINS` mutálható lista, hardcode-olt késleltetések

- **Hely:** `src/config/api_config.py:47-51` (`CORS_ORIGINS: ClassVar[list[str]]` — mutálható, míg a többi konstans `MappingProxyType`/tuple), `:76-88` (`_reload_lock` csak a `reload()` íróit szerializálja; minden olvasó lock nélkül), `tests/test_api_config_app_env.py:23` közvetlen attribútum-írás a lock megkerülésével; `weather_client_core.py:51` `retry_delay = 1.0`, `openmeteo_provider.py:41-42` `90` / `0.6` — nem az `APIConfig`/`WeatherFetchConfig` része (P-01, P-05 gyökere); `api/routes/anomalies.py:57` import-idejű use case a registry helyett (02_LOGIC L-09); `api/services/provider_usage_service.py:203` modul-singleton (L-04).
- **Kockázat:** a viselkedést meghatározó számok (batch-méret, alvás, retry) szétszórtan, env-ből nem hangolhatók, tesztben nem injektálhatók; a `CORS_ORIGINS` futásidőben bővíthető.
- **Effort / irány:** alacsony — konstansok egy konfig-objektumba (env-override-dal), `CORS_ORIGINS` tuple.

### [Q-11] [ALACSONY] [STATIKUSAN IGAZOLT] Négy leíró-statisztika implementáció, ebből egy `None`-ra `TypeError`-t ad

- **Hely:** `domain/analytics/statistics.py:13-56` (`safe_*`, None-szűréssel), `domain/entities/analytics_models.py:147-164` (`get_statistics_summary`: `statistics.mean(values)` **szűrés nélkül**, függvény-szintű `import statistics`), `presentation/gui/utils/formatting/statistics.py:38-60`, `presentation/gui/results_panel/utils/wind_analyzer.py:14-33`; mind a `stdev if len > 1 else 0` mintát ismétli.
- **Kockázat:** a `CityWeatherResult.value` `None` esetén (hibás fetch, 02_LOGIC L-03) a `get_statistics_summary` kivételt dob, míg a `safe_mean` `None`-t ad — inkonzisztens viselkedés ugyanarra az adatra.
- **Effort / irány:** alacsony — a domain `safe_*` helperek használata mindenhol.

---

## 6. Hipotézisek (nem kerülnek a prioritási listára)

| ID | Állítás | Miért hipotézis | Szükséges mérés |
|----|---------|-----------------|-----------------|
| H-P1 | A `leaflet` chunk (165 KB js + 15 KB css) az entry `index.html`-ben `modulepreload`-dal minden oldalra betöltődik, holott csak lazy oldalak (`MultiCityView`, `SingleCityResults`) használják a `MapView`-t | a build-artefakt 2026-07-25-i, nem ennek a snapshotnak a buildje; `vite build` BLOKKOLT (ír a `frontend/build/`-be) | `vite build --outDir <scratch>` és az `index.html` preload-listája + `rollup-plugin-visualizer` |
| H-P2 | `requests.Session` megosztása 8 worker között (`pool_maxsize` default 10, 3 kliens × 2 provider) kapcsolat-eldobást/blokkolást okoz; a `_rate_limit_check` `last_request_time` lock nélküli osztott állapota alul-throttlingol → 429 | nincs konkurens reprodukció (02_LOGIC H2-vel azonos) | konkurens mock-teszt urllib3 pool-logolással; provider 429-számlálás |
| H-P3 | `routes/multi_year.py:52` a teljes `AnalyticsResult.to_dict()`-et materializálja, majd csak a `city_results`-t tartja meg; 20 év × 365 rekord × 4 reprezentáció (dataclass → dataclass → dict → JSON) | nem mértem a `to_dict` költségét; a detailed úton a hasonló transform 5 ms/metrika (B11) → valószínűleg kicsi | `AnalyticsResult` 365 rekorddal ×20 `to_dict` időzítés |
| H-P4 | A GUI trend-fetch szekvenciális (`fetcher.py:40-63`) → 55 év ≈ 55 × 2,4 s ≈ **132 s** alvás-padló a GUI workerben | a 2,4 s/év a B3-ból levezetett, a GUI nem futott | GUI headless futtatás mockolt HTTP-vel, worker-időmérés |
| H-P5 | Multi-city 5 évre `MAX_CITIES_PER_REQUEST` várossal: `ceil(N/8)` batch × (12 s + 0,5 s `rate_limit_delay`) > 30 s kliens-timeout már 9+ városnál | a régió `batch_size`/`max_cities` értékeit és a valós használati mintát (tipikusan 1 napos „hottest_today”) nem mértem | mock-HTTP futtatás 9 és 50 várossal, 5 éves tartománnyal |
| H-P6 | Az Open-Meteo archive API 90 napnál hosszabb tartományt is elfogad egy kérésben, tehát a 90 nap / 0,6 s önkorlát fölösleges | hálózat nélkül nem ellenőrizhető; a kódban nincs forráshivatkozás | dokumentáció + egy nem-production hívás 366 napos tartománnyal; ez dönti el P-01 javítási irányát |
| H-P7 | A `CityRepositoryQueries` kapcsolat-per-query mintája (B14: 0,09–0,28 ms) konkurencia alatt WAL/lock-várakozást okoz | egyszálú mérés csak | párhuzamos autocomplete-terhelés (pl. 20 szál) latencia-eloszlással |

---

## 7. Elvetett jelöltek (cáfolati napló)

| Jelölt | Cáfolat |
|--------|---------|
| API cold start / nehéz import | B1: 250 ms, nehéz könyvtár nem töltődik importkor; pandas/scipy csak a lifespanben a trend-kalkulátorral |
| Rate-limiter `sorted(...min())` eviction minden kérésen | csak `len > max_clients` esetén fut (`rate_limit.py:63`); B16: 1 µs medián, 1,9 ms max 10 000 kliensnél → nem bottleneck |
| Szélrózsa 16 lineáris scan + soronkénti sebesség-sáv keresés | B10: 2,0 ms 5 évre, 20,8 ms 55 évre — mikro-optimalizáció |
| Detailed-city 4× `process_weather_results` (4 sort, 4 dict-materializálás) | B11: 20 ms összesen 1 827 rekordon — a 12 s alvás-padló mellett elhanyagolható |
| Open-Meteo válasz oszlop→sor transzponálás (15 mező) | B9: 0,06 ms/batch, 14 ms/55 év |
| `get_cities_by_names` korrelált al-lekérdezés / autocomplete full scan | B12–B13: 0,2–25 ms 44 658 soron; lineáris a táblamérettel, de a tábla statikus → ALACSONY, a kódminőségi Q-07-be olvasztva |
| `city_manager` `LIKE '%term%'` két teljes scan | B15: 0,2 ms találat, 10,6 ms hiány → P-04-be olvasztva (event-loop), nem önálló |
| `_has_column` PRAGMA-kapcsolat hívásonként | B14: 0,09 ms → Q-07 |
| `CityManagerDB` thread-local kapcsolatok „szivárgása” | korlátos (≤ 2 × 41), nem nő kérésenként → Q-09 |
| `requests.Session` nem záródik | 6 példány a folyamat élettartamára, korlátos → Q-09 |
| `WeatherFetchService` új `ThreadPoolExecutor` batchenként | `with`-blokk, létrehozás µs-nagyságrend; nem mértem külön, a 12 s alvás mellett irreleváns |
| Nested pool (multi-year 4 × fetch 8 = 32 szál) | korlátos (4×8), single-city-nként 1 aktív provider-hívás; erőforrás-kimerülés nem bizonyított |
| Frontend `plotly` 4,6 MB | csak a `WindyDaysView` lazy chunk importálja (build-artefakt `grep`: `index` és `WindyDaysView` — az `index`-ben csak a chunk-név, statikus `from "./plotly…"` nincs) → nem eager |
| `pd.concat` ciklusban / `deepcopy` / `while True` / `@property` teljes-collection újraszámolás | grep: 0 találat mindegyikre a `src/`-ben |
| Domain `__post_init__` per rekord | `weather_types.py:44-54` két aritmetikai művelet; a string-építők (`city.py:69-81`) csak városonként futnak |
| Pydantic per-item validáció nagy listákon | `model_validate` 0 találat; a napi rekordok plain dict-ként mennek ki; a wind-rose `DirectionData` mindig 16 elem |
| Rekurzió memoizáció nélkül | egyetlen (`_select_preferred_provider` ↔ `_select_provider`), mélység ≤ 2 az elérhető úton (02_LOGIC H1 a nem elérhető végtelen esetre) |
| Tesztsuite összideje mint egész | 26,9 s / 1 743 teszt — az alvás nélküli rész (~12,5 s) rendben; csak a 4 sleep-es teszt (P-05) |

---

## 8. Blokkolt területek

| Terület | Indok |
|---------|-------|
| Valós provider-latencia, retry-időzítés, Open-Meteo tartomány-limit (H-P6) | nincs hálózat ebben a futásban |
| GUI futásidő (P-03 Qt-backend költsége, H-P4) | GUI nem indult (headless); Agg-backend és statikus levezetés |
| Frontend bundle mérése ezen a snapshoton (H-P1) | `vite build` a `frontend/build/`-be ír; a meglévő artefakt júliusi |
| Terhelés alatti mérés (konkurens kérések, event-loop blokkolás hatása, H-P2, H-P7) | csak egyszálú, izolált mérés történt; nincs load-generátor a repóban |
| Playwright e2e | élő stack + böngésző |
| `quality_gate.sh --full` | tesztet futtat + coverage-t ír; helyette izolált pytest (B18) |

---

## 9. Hatás × effort prioritási lista (csak MÉRT / STATIKUSAN IGAZOLT)

| Prioritás | ID | Severity | Státusz | Hatás | Effort | Egy soros indok |
|-----------|----|----------|---------|-------|--------|-----------------|
| 1 | P-01 | MAGAS | MÉRT | trend alapkérés 35 s alvás-padló > 30 s kliens-timeout; 5 év = 12 s/város | közepes | 90 napos batch + 0,6 s fix alvás + nincs cache |
| 2 | P-02 | MAGAS | MÉRT | 4,9 s CPU/trend-kérés, 440× a vektorizált költség | alacsony | soronkénti `pd.to_datetime` periódusonként újra |
| 3 | Q-01 | MAGAS | STATIKUSAN IGAZOLT | API és GUI trend eltérhet; GUI-másolat teszteletlen; P-02 kétszer javítandó | közepes | copy-paste regresszió + inline küszöbök |
| 4 | P-03 | KÖZEPES | MÉRT | 25–262 ms/egérmozgás a GUI-szálon | alacsony | pontonkénti `transform` + `print` a hot pathon |
| 5 | Q-04 | KÖZEPES | STATIKUSAN IGAZOLT | éles 500 egy végpont-ágon, zöld teszt mellett | alacsony | mockolt port elrejti a hiányzó implementációt |
| 6 | Q-06 | KÖZEPES | STATIKUSAN IGAZOLT | hiba ≡ üres eredmény két rétegben; naplózatlan hamis CI | közepes | 31/31 nyelő `except Exception` |
| 7 | Q-03 | KÖZEPES | STATIKUSAN IGAZOLT | mypy/ciklus vakfolt, 11 elérhetetlen fájl | triviális | csomag árnyékolja a modult |
| 8 | Q-02 | KÖZEPES | STATIKUSAN IGAZOLT | a tesztelt és a szállított szél-elemzés más függvény | alacsony | két `analyze_wind_patterns` |
| 9 | Q-05 | KÖZEPES | STATIKUSAN IGAZOLT | holt csomag, árva teszt-support, holt ciklus-pár, nem regisztrált wrapper tesztelve | alacsony | 0 hivatkozás |
| 10 | P-05 | ALACSONY | MÉRT | +14,4 s minden CI-futáson | alacsony | nem injektálható `sleep` |
| 11 | P-04 | ALACSONY | MÉRT | 11–25 ms event-loop blokkolás/kérés | alacsony | városfeloldás a threadpoolon kívül |
| 12 | Q-07 | ALACSONY | MÉRT | holt „indexelt” ág, hatástalan index-script, 2 extra kapcsolat | alacsony | planner-bizonyíték |
| 13 | Q-10 | ALACSONY | STATIKUSAN IGAZOLT | hangolhatatlan konstansok, mutálható CORS-lista | alacsony | konfig-szórás |
| 14 | Q-09 | ALACSONY | STATIKUSAN IGAZOLT | hibaúton nyitva maradó kapcsolatok, korlátos session/timer | alacsony | `finally` hiánya |
| 15 | Q-08 | ALACSONY | STATIKUSAN IGAZOLT | ellentmondó Beaufort-táblák | alacsony | 4 küszöbtábla |
| 16 | Q-11 | ALACSONY | STATIKUSAN IGAZOLT | `None` → `TypeError` egy statisztika-másolatban | alacsony | 4 implementáció |

**Nem került a listára:** H-P1…H-P7 (mérés nélkül).

---

## 10. Parancsnapló (ebben a futásban)

| Parancs (rövidítve) | Mit bizonyít | Eredmény |
|---------------------|--------------|----------|
| `git status --short`; `git rev-parse HEAD`; `ls docs/audit/` | snapshot-egyezés | HEAD `c4793cdc…`, porcelain azonos + `docs/`; RUN_ID mappa 3 korábbi jelentéssel |
| `grep -rniE 'benchmark\|profil\|timeit\|py-spy' Makefile pyproject.toml *.sh .github/*` ; `grep durations` | repó-eszközök | **nincs** benchmark/profiler/`--durations` |
| `venv/bin/python` + `sqlite3.connect("file:…?mode=ro", uri=True)` `sqlite_master` + `COUNT(*)` | sémák/indexek/sorszámok | `cities` 44 658 (8 index, **nincs** `city_lower`), `hungarian_settlements` 3 178, `weather_data` 79 824 |
| in-memory `backup()` + `EXPLAIN QUERY PLAN` + `perf_counter` (n=30) | B12, B13, B14, Q-07 planner | lásd §2; `INDEXED BY idx_city_lower` → SCAN; `case_sensitive_like=ON` → SEARCH |
| `python -X importtime -c "import src.api.main"`; 3× fal-idő; `sys.modules` szűrés | B1 | 232–257 ms, nehéz lib: `[]` |
| `ls -la frontend/build/assets`; `grep -o 'from"./…"' index-*.js`; `grep -l plotly-… *.js`; `grep -rn "React.lazy\|from 'leaflet'" frontend/src` | B19, H-P1, plotly-cáfolat | index statikus: leaflet/vendor/runtime; plotly csak WindyDaysView |
| `md5sum data/*.db` → `PYTHONDONTWRITEBYTECODE=1 pytest tests/ -q -p no:cacheprovider -o addopts= --durations=25` → `md5sum`; `git status --porcelain` | B18, izoláció | 1743 passed 26,92 s; top4 = 14,4 s; DB md5 **azonos**, porcelain változatlan |
| `grep -n sleep src/infrastructure/weather/*.py`; `sed` a retry/batch kódra; `grep RETRY_DELAY api_config.py` | P-01/P-05 forrás | `retry_delay=1.0` hardcode, `batch_delay=0.6`, `max_days_per_request=90`, `min_request_interval=0.1` |
| `sed` `calculate_trend.py`, `routes/multi_year.py`, `weather_fetch_service.py`, `openmeteo_provider.py`, `trend_request.py`, `analytics.py`, `anomalies.py`, `wind_rose_part3.py`, `cities.py`, `fetcher.py`, `detailed_city_use_case.py` | hívási láncok, threadpool-használat, event-loop blokkolás | §1.1, P-01, P-04, H-P4 |
| `venv/bin/python` mock `session.get` + valós `time.sleep`: `client.get_weather_data(5 év)`; `CalculateTrendUseCase._fetch_weather_data(55 év)` | B3, B4 | 21 hívás / 12,0 s; 274 hívás / 35,2 s |
| `venv/bin/python` `TrendCalculator.calculate_multiple_periods` 20 076 szintetikus rekordon (n=5); szűrő inline vs hoisted (n=10); `prepare_dataframe` vs vektorizált; `aggregate_monthly`; `_process_response` | B5–B9 | 4 905 ms; 44,0 vs 2,6 ms; 2 715 vs 6,2 ms; 3 ms; 0,06 ms |
| `MPLBACKEND=Agg venv/bin/python` pontonkénti vs vektorizált `transData.transform` 1 827 / 20 076 ponton | B17 | 8 / 87 ms sorozatonként vs 0,04 / 0,24 ms |
| `venv/bin/python` `WindRoseCalculator.calculate` 365/1 827/20 076 (n=10) | B10 | 0,4 / 2,0 / 20,8 ms |
| `venv/bin/python` `AnalyticsTransformService(QUERY_TYPES)` 4 metrika 1 827 rekordon (n=5) | B11 | 20 ms |
| `venv/bin/python` `RateLimitMiddleware._is_limited` 100/10 000/10 001 kliens (n=200) | B16 | 1 µs medián, ≤ 1,9 ms max |
| `venv/bin/python` `get_city_manager_port().find_city_by_name(...)` valós DB-n (n=20) | B15 | 0,2 ms / 10,6 ms |
| `venv/bin/python` `hasattr(CityManagerStats, "get_cities_for_region")`; `grep` port + route + teszt | Q-04 | `False`; port deklarálja; teszt mockolja |
| `grep -rn "def analyze_wind_patterns"`; `grep -rl analyze_wind_patterns src tests` | Q-02 | 2 definíció; GUI → application, tesztek → infrastructure |
| `grep -rl anomaly_profile_manager\|anomaly_demo\|analytics.wind_analysis\|presentation.api\|api_auth_support` (src/tests/scripts/Makefile/pyproject/.importlinter/.github) | Q-05 | csak egymás / csak teszt / 0 találat |
| `sed` `wind_rose.py:10-22`; `grep wind_rose.get_wind_rose tests/api` | Q-05 wrapper | dekorátor nélküli wrapper, 5 teszthívás |
| `grep -n to_datetime\|linregress\|sklearn calculator.py`; `grep MIN_* trend_*.py` | Q-01 | azonos komment, inline literálok vs konstansok |
| `grep -rn "except Exception" src/<layer> \| wc -l` (5 réteg); `sed` a 10 kiemelt helyre | Q-06 | 4/10/21/17/266 |
| `grep -n 43\|61\|90\|119 wind_categories.py`; `sed wind_constants.py:22-34` | Q-08 | 43/61/90/119 vs 50/70/100/120 azonos Beaufort-címkékkel |
| `sed database_manager.py:159-192`; `grep session.close src/infrastructure/weather` | Q-09 | close a try-ban; 0 `session.close` |
| `sed analytics_models.py:147-164` | Q-11 | `statistics.mean(values)` szűrés nélkül |
| `lscpu`, `free -m`, verziók | §1.2 | i5-13400, 31 GB, pandas 3.0.1 |
| `git status --porcelain` (zárás) | worktree | lásd §11 |

**Feltáró ügynökök:** 3 read-only Explore ügynök futott (API-utak, adatfeldolgozás, kódminőség); minden, a jelentésbe bekerült állításukat a fenti parancsokkal újraellenőriztem; a nem ellenőrzött vagy eltérő számaikat (pl. az ügynök 98,8 ms-os `strftime` mérése) nem vettem át, a saját mérés (44,0 ms) szerepel.

**Írás:** kizárólag ez a fájl (`docs/audit/20260910T092914Z/04_PERFORMANCE.md`). Termékkód, teszt, config, DB, lock nem módosult; `__pycache__`/bytecode írás `PYTHONDONTWRITEBYTECODE=1`-gyel tiltva, pytest cache `-p no:cacheprovider`-rel.

---

## 11. Záró `git status`

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

A lista **azonos** a futás eleji állapottal; az egyetlen új tétel a `docs/audit/20260910T092914Z/04_PERFORMANCE.md` (a `docs/` untracked mappán belül). `md5sum data/*.db` a zárásnál is a futás eleji értékeket adja (`aebe56a2…`, `87b3a7d6…`, `13ae4805…`). Termékkód, teszt, séma, config nem módosult.
