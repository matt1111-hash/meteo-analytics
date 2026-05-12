# meteo-analytics — Optimalizáció & Kódminőség Audit
Dátum: 2026-05-12 | Model: GPT-5 Codex

## Executive summary

Az audit statikus kódelemzésen, a Prompt 0 és Prompt 1 eredményein, lokális bundle-méret ellenőrzésen, SQLite query plan vizsgálaton és import/inicializációs időmérésen alapul. Runtime profiler nem futott, ezért ahol a hatás csak terhelés alatt igazolható, ott külön jelöltem: `[HIPOTÉZIS – profilozással ellenőrzendő]`.

A fő teljesítménykockázat nem mikroszintű Python optimalizáció, hanem az időjárás-lekérési orchestration, a per-request dependency construction, az indexet nem használó keresések, a frontend nagy kezdő bundle-je és a többszörös API round-trip minták.

Megerősített, gyorsan támadható pontok:

- Az API teljes importja lokálisan kb. 3,0 s volt; az `src.api.main` eager router importjai behúzzák a trend analitika pandas/scipy/sklearn láncát.
- A frontend build egyetlen nagy, kb. 5,4 MB-os JS chunkot tartalmaz (`frontend/build/assets/index-CaT7_9j1.js`), miközben a route-ok és nagy chart/map könyvtárak statikusan importálódnak.
- A város autocomplete SQL query planje teljes scan jellegű: `LOWER(...) LIKE '%query%'` és population szerinti rendezés miatt nem használ névindexet.
- A multi-city időjárás pipeline minden city-day rekordot memóriában gyűjt, és a `limit` csak az adatlekérés és transzformáció után érvényesül.
- A trend use case-ben a `WeatherClient.get_weather_data` hívás rossz kulcsszóparamétereket használ (`lat`/`lon` a `latitude`/`longitude` helyett), majd a hibát elnyeli, ami funkcionális hibát és felesleges háttérmunkát okozhat.
- A React multi-year nézet évszámonként külön API hívásokat indít, default 3, maximum 8 párhuzamos kéréssel.

## 1. Algoritmikus komplexitás

#### Város autocomplete indexet kerülő keresése
- **Kategória:** Algoritmikus / I/O
- **Severity:** MAGAS
- **Érintett fájlok:** `src/infrastructure/repositories/city_repository_queries.py:147`, `src/infrastructure/repositories/city_repository_queries.py:158`, `src/infrastructure/repositories/city_repository_queries.py:180`, `frontend/src/components/common/CityAutocomplete.tsx:53`, `frontend/src/components/common/CityAutocomplete.tsx:65`
- **Mi a probléma:** Az autocomplete query `LOWER(city) LIKE ?` és `LOWER(name) LIKE ?` mintát használ `%query%` kereséssel, majd `population DESC` szerint rendez. Lokális `EXPLAIN QUERY PLAN` alapján a 44 658 soros `cities` táblán és a 3 178 soros magyar település táblán scan jellegű végrehajtás történik, ez pedig minden debounce-olt billentyűzésnél lefut.
- **Várható hatás:** API latency és SQLite CPU nő a keresési forgalommal; kis adatmennyiségnél még elfogadható, de interaktív inputnál közvetlenül felhasználói késleltetésként jelentkezik.
- **Javítási irány:** Normalizált keresőoszlopot, expression indexet vagy SQLite FTS5 táblát érdemes bevezetni. Ha a termékélmény megengedi, prefix keresés és népszerű találatok cache-elése tovább csökkenti a scan mennyiséget.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### `get_cities_by_names` korrelált subquery és névindex hiány
- **Kategória:** Algoritmikus / I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/infrastructure/repositories/city_repository_queries.py:19`, `src/infrastructure/repositories/city_repository_queries.py:32`, `src/infrastructure/repositories/city_repository_queries.py:36`
- **Mi a probléma:** A név szerinti városkeresés `LOWER(city) IN (...)` feltételt és `MAX(population)` korrelált subquery-t használ. A lokális query plan `SCAN cities USING INDEX idx_population` és `CORRELATED SCALAR SUBQUERY` mintát mutatott.
- **Várható hatás:** Több városnév egyidejű lekérésekor a DB többször dolgozza fel ugyanazt a táblát; multi-city indításnál ez latency-t ad az amúgy is hálózatvezérelt flow elejéhez.
- **Javítási irány:** Precomputed canonical city rekord, normalizált névindex, vagy ablakfüggvényes/group-by alapú egy lekérdezés csökkentené a szükséges scaneket. A population szerinti deduplikációt célszerű explicit adatmodell döntéssé tenni.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Detailed city metrikák négyszer dolgozzák fel ugyanazt az idősor-listát
- **Kategória:** Algoritmikus
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/application/use_cases/detailed_city_use_case.py:80`, `src/application/use_cases/detailed_city_use_case.py:85`, `src/application/use_cases/detailed_city_use_case.py:98`, `src/application/use_cases/detailed_city_use_case.py:122`, `src/domain/analytics/services/analytics_transform_service.py:230`, `src/domain/analytics/services/analytics_transform_service.py:270`
- **Mi a probléma:** A részletes város nézet ugyan egyszer fetch-el, de négy metrikára külön hívja a `process_weather_results(..., aggregate=False)` feldolgozást. Ez ismételt szűrést, rendezést és dict-transzformációt jelent ugyanazon daily rekordokon.
- **Várható hatás:** CPU és memóriaallokáció négyszereződik a metrika-extrakcióban, főleg hosszabb dátumtartományoknál.
- **Javítási irány:** A daily rekordokat egyszer kellene validálni, rendezni és normalizált belső reprezentációba tenni, majd abból projektálni a metrikasorozatokat. Ez a jelenlegi API-választ nem feltétlenül érinti.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

#### Trend periódusok ismételt teljes lista-szűrése és dataframe építése
- **Kategória:** Algoritmikus / Memória
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/domain/analytics/services/trend_calculator.py:133`, `src/domain/analytics/services/trend_calculator.py:151`, `src/domain/analytics/services/trend_calculator.py:164`, `src/domain/analytics/services/trend_data_processor.py:19`, `src/domain/analytics/services/trend_data_processor.py:76`
- **Mi a probléma:** A trend számítás előbb rendezi az összes weather adatot, majd minden periódushoz újra végigszűri a teljes listát, és minden periódushoz új dataframe/monthly aggregation készül. A periódusok száma kicsi, de a weather lista a dátumtartománnyal nő.
- **Várható hatás:** CPU és memória O(k*n) irányba nő, ahol `k` a kért periódusok száma. A default periódusoknál ez még kezelhető, de 55 évnyi napi adatnál már mérhető.
- **Javítási irány:** Egyszeri monthly aggregate vagy dátumindexelt sorozat után periódusonként csak szeletelni kellene. A regressziós számítás maradhat periódusonként, de az input-előkészítés ne ismétlődjön.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Wind rose irányonként újraszkenneli az observation listát
- **Kategória:** Algoritmikus
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/domain/analytics/services/wind_rose_calculator.py:135`, `src/domain/analytics/services/wind_rose_calculator.py:153`, `src/domain/analytics/services/wind_rose_calculator.py:165`
- **Mi a probléma:** A 16 iránybin mindegyike külön list comprehensionnel szűri a `paired_data` listát, majd speed bucket számítást futtat. Ez konstans 16 miatt nem klasszikus O(n²), de nagy idősornál felesleges 16 teljes bejárás és listaallokáció.
- **Várható hatás:** Alacsony-közepes CPU/allokációs overhead a wind rose endpointnál; a hatás date range növekedéssel arányos.
- **Javítási irány:** Egyetlen passzban lehetne direction indexet és speed bucketet számolni, majd egy 16 x bucket mátrixot tölteni. Ez egyszerűsíti a hot loopot és csökkenti az átmeneti listákat.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

## 2. Memória és erőforrás-kezelés

#### Multi-city időjárás pipeline teljes city-day datasetet tart memóriában
- **Kategória:** Memória / I/O
- **Severity:** MAGAS
- **Érintett fájlok:** `src/domain/analytics/services/weather_fetch_service.py:94`, `src/domain/analytics/services/weather_fetch_service.py:105`, `src/domain/analytics/services/weather_fetch_service_support.py:76`, `src/domain/analytics/services/weather_fetch_service_support.py:87`, `src/application/use_cases/analyze_multi_city.py:107`, `src/application/use_cases/analyze_multi_city.py:139`
- **Mi a probléma:** A batch fetch minden város napi rekordjait `all_city_weather_data` listába gyűjti, majd a transform új listát épít. A `query.limit` csak az adatlekérés és transzformáció után vágja a választ, ezért nem védi a hálózati és memória oldalt.
- **Várható hatás:** Memóriahasználat O(városok * napok) szerint nő; nagy régió és hosszú dátumtartomány esetén MB-tól több tíz MB-ig terjedő átmeneti objektumtömeg keletkezhet.
- **Javítási irány:** A limitet és aggregációs igényt a fetch előtt kellene érvényesíteni, ahol az üzleti logika engedi. Hosszabb távon streaming/generator alapú feldolgozás vagy batchenkénti aggregálás csökkentené az átmeneti memóriaigényt.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### `requests.Session` életciklus nincs lezárva, miközben kliensek per-request jönnek létre
- **Kategória:** Memória / I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/data/weather_provider_base.py:31`, `src/data/weather_client_core.py:43`, `src/data/weather_client_core.py:46`, `src/infrastructure/container/factories.py:41`, `src/infrastructure/container/factories.py:50`, `src/api/routes/wind_rose_part3.py:23`, `src/api/routes/wind_rose_part3.py:29`
- **Mi a probléma:** A provider base `requests.Session()` objektumot hoz létre, de a provider/client oldalon nem látszik `close()` vagy context manager életciklus. Több route és factory per kérés hoz létre `WeatherClient` példányt.
- **Várható hatás:** Hosszú életű API folyamatban connection pool churn és socket/handle felhalmozódási kockázat. A pontos mérték forgalom- és GC-függő.
- **Javítási irány:** Lifespan-managed singleton vagy request-scoped client pool szükséges explicit lezárással. A provider Session objektumokhoz érdemes `close()` metódust és FastAPI lifespan cleanupot kötni.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### `split_batches` teljes nested batch listát épít előre
- **Kategória:** Memória
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/domain/analytics/services/weather_fetch_service_support.py:12`, `src/domain/analytics/services/weather_fetch_service_support.py:14`, `src/domain/analytics/services/weather_fetch_service.py:71`
- **Mi a probléma:** A batch splitter előre materializálja az összes batch listát, miközben a hívó szekvenciálisan dolgozza fel őket. Nagy city listánál ez kis, de felesleges plusz memória.
- **Várható hatás:** Alacsony MB-hatás, inkább tisztasági és skálázódási jellegű.
- **Javítási irány:** Iterator/generator alapú batchelés elegendő lenne, mert a pipeline egyszerre csak egy batch-et dolgoz fel.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

#### Rate limiter listát szűr és újraallokál minden requestnél
- **Kategória:** Memória / Algoritmikus
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/api/middleware/rate_limit.py:35`, `src/api/middleware/rate_limit.py:49`, `src/api/middleware/rate_limit.py:56`, `src/api/main.py:80`, `src/api/main.py:84`
- **Mi a probléma:** A limiter kliensenként timestamp listát tart, és minden kérésnél list comprehensionnel kiszűri a lejárt elemeket. Production limitnél ez kicsi, de dev módban a limit 10 000 request/minute.
- **Várható hatás:** Magas request rate mellett O(requests_in_window) munka és listaallokáció történik requestenként.
- **Javítási irány:** `deque` alapú sliding window és bal oldali pop csökkentené az allokációt és a per-request munkát.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

## 3. I/O és hálózat

#### Per-request composition root és provider inicializáció
- **Kategória:** I/O / Build
- **Severity:** MAGAS
- **Érintett fájlok:** `src/api/routes/weather.py:29`, `src/api/routes/weather.py:31`, `src/api/routes/single_city.py:50`, `src/api/routes/single_city.py:64`, `src/api/routes/detailed_city.py:30`, `src/api/routes/detailed_city.py:32`, `src/api/routes/analytics.py:49`, `src/api/routes/analytics.py:53`, `src/infrastructure/container/composition_root.py:24`, `src/infrastructure/container/composition_root.py:38`, `src/infrastructure/container/factories.py:41`, `src/infrastructure/container/factories.py:50`
- **Mi a probléma:** Több route minden kéréshez új use case-t, repositoryt, provider chain-t és `WeatherClient`-et épít. Lokális mérés alapján `build_analyze_multi_city_use_case()` egyszeri hívása kb. 183,8 ms volt, és ebben nincs külső API round-trip.
- **Várható hatás:** Kérésenként ms nagyságrendű overhead, felesleges Session/circuit breaker/provider stats újrainicializálás, cache és állapotvesztés.
- **Javítási irány:** A FastAPI lifespan alatt épített, explicit lezárható szolgáltatásokat érdemes használni. Ami állapotot tart, annak ownershipje legyen egyértelmű, a request-specifikus adat pedig maradjon use case paraméter.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Multi-year frontend N darab backend kérést indít évszámonként
- **Kategória:** I/O / Hálózat
- **Severity:** KÖZEPES
- **Érintett fájlok:** `frontend/src/hooks/useMultiYearWeather.ts:40`, `frontend/src/hooks/useMultiYearWeather.ts:61`, `frontend/src/pages/MultiYearView.tsx:146`, `frontend/src/pages/MultiYearView.tsx:152`
- **Mi a probléma:** A multi-year hook minden kiválasztott évre külön `/api/weather/single-city` requestet indít `Promise.all`-lal. A UI default 3 évet választ, de 2018-2025 között akár 8 párhuzamos backend fetch is történhet.
- **Várható hatás:** Felesleges round-trip és backend provider terhelés; lassú hálózatnál vagy provider throttlingnál közvetlenül rontja a válaszidőt.
- **Javítási irány:** Egy date range alapú backend batch endpoint vagy meglévő endpoint kiterjesztése csökkentené a round-trip számot. A kliens oldali havi aggregálás helyett a backend is visszaadhatna év-hónap aggregátumot.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Hungary stations flow N+1 county query mintát használ
- **Kategória:** I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/api/routes/hungary.py:101`, `src/api/routes/hungary.py:108`, `src/api/routes/hungary.py:203`, `src/api/routes/hungary.py:229`
- **Mi a probléma:** A station candidate fetch county listán iterál, és minden megyére külön settlement query-t hív, amíg elég jelölt nincs. Ez N+1 jellegű DB round-trip ahelyett, hogy egy bulk query adná vissza a szükséges településeket.
- **Várható hatás:** Közepes DB latency és connection churn, főleg ha a limit magasabb vagy a népességi feltételek kevés találatot adnak.
- **Javítási irány:** Egyetlen SQL query vagy repository metódus kérje le a szükséges jelölteket county filterrel és rendezéssel. A limitet a DB-ben célszerű érvényesíteni.
- **Effort:** kicsi-közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### CityAutocomplete nem törli az elavult kéréseket
- **Kategória:** I/O / Kódminőség
- **Severity:** KÖZEPES
- **Érintett fájlok:** `frontend/src/components/common/CityAutocomplete.tsx:53`, `frontend/src/components/common/CityAutocomplete.tsx:83`, `frontend/src/components/common/CityAutocomplete.tsx:85`, `frontend/src/components/common/CityAutocomplete.tsx:97`
- **Mi a probléma:** A komponens debounce-ol, de nincs `AbortController` vagy sequence guard. Lassabb korábbi request később visszaérve felülírhatja az aktuális query suggestion listáját.
- **Várható hatás:** Stale UI találatok és felesleges backend munka gyors gépelésnél; performance és UX probléma egyszerre.
- **Javítási irány:** Minden új query előtt az előző requestet abortálni kell, vagy monoton request id alapján csak a legfrissebb választ szabad elfogadni.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

#### Open-Meteo chunk fetch szekvenciális késleltetést használ hosszú tartományokon
- **Kategória:** I/O / Concurrency
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/data/openmeteo_provider.py:104`, `src/data/openmeteo_provider.py:147`, `src/data/openmeteo_provider.py:134`, `src/data/openmeteo_provider.py:135`
- **Mi a probléma:** A hosszabb date range chunkokra osztódik, és chunkonként szekvenciális sleep történik. Ez lehet tudatos rate-limit védelem, de hosszú tartományoknál lineárisan növeli a wall-clock időt.
- **Várható hatás:** Trend és hosszú history lekérések lassulhatnak, ha a provider API limitje megengedné az okosabb batch/paralell stratégiát.
- **Javítási irány:** Provider limit dokumentáció alapján érdemes eldönteni, hogy lehet-e adaptív concurrency vagy nagyobb chunk. Ha nem lehet, a késleltetés legyen konfigurált és mérhető metrika.
- **Effort:** közepes
- **Bizonyosság:** HIPOTÉZIS – profilozással ellenőrzendő

## 4. Párhuzamosíthatóság

#### Közös `WeatherClient` és `requests.Session` használat threadpoolból
- **Kategória:** Concurrency / I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/domain/analytics/services/weather_fetch_service.py:107`, `src/domain/analytics/services/weather_fetch_service.py:129`, `src/data/weather_client_core.py:149`, `src/data/weather_client_core.py:151`, `src/data/weather_provider_base.py:31`
- **Mi a probléma:** A batch fetch egy közös `WeatherClient` példányt használ több worker threadből, miközben a client provider usage statot mutál és a providerek `requests.Session` objektumot tartanak. A thread-safety szerződés nem látszik a kódban.
- **Várható hatás:** Ritka race condition, pontatlan provider stat, Session állapotprobléma vagy flaky hiba terhelés alatt.
- **Javítási irány:** Terheléses teszttel kell igazolni a viselkedést. Ha reprodukálható, thread-local client, lockolt stat-kezelés vagy thread-safe HTTP kliens/pool szükséges.
- **Effort:** közepes
- **Bizonyosság:** HIPOTÉZIS – profilozással ellenőrzendő

#### Hungary async endpointok szinkron DB munkát futtatnak event loop-ban
- **Kategória:** Concurrency / I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/api/routes/hungary.py:116`, `src/api/routes/hungary.py:137`, `src/api/routes/hungary.py:173`, `src/api/routes/hungary.py:196`, `src/api/routes/hungary.py:203`, `src/api/routes/hungary.py:229`
- **Mi a probléma:** Az endpointok `async def` függvények, de közvetlenül hívnak szinkron SQLite repository/city manager műveleteket. Más route-oknál a projekt használ `run_in_threadpool` mintát, itt ez hiányzik.
- **Várható hatás:** DB művelet közben az event loop blokkolódhat, ami párhuzamos API forgalomnál tail latency növekedést okoz.
- **Javítási irány:** A meglévő `run_in_threadpool` mintát vagy async DB adaptert kell alkalmazni. Bulk query-vel kombinálva egyszerre javulna a concurrency és az I/O költség.
- **Effort:** kicsi-közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### ThreadPoolExecutor batchenként újra létrejön
- **Kategória:** Concurrency
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/domain/analytics/services/weather_fetch_service.py:107`, `src/domain/analytics/services/weather_fetch_service.py:116`, `src/domain/analytics/services/weather_fetch_service.py:138`
- **Mi a probléma:** Minden batch külön `ThreadPoolExecutor` példányt hoz létre, majd lezárja. Kis batch countnál ez nem gond, de nagy régióknál felesleges executor lifecycle overhead.
- **Várható hatás:** Alacsony ms overhead batchenként; a hálózati latency mellett ritkán domináns, de egyszerűen mérhető.
- **Javítási irány:** Egy request-scope executor vagy hosszabb életű service-scope executor csökkentheti az overheadet, de csak a thread-safety kérdés rendezése után érdemes hozzányúlni.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

## 5. Kódminőség és maintainability

#### Trend use case rossz `WeatherClient` kulcsszóparamétereket használ, a hibát elnyeli
- **Kategória:** Kódminőség / I/O
- **Severity:** MAGAS
- **Érintett fájlok:** `src/application/use_cases/calculate_trend.py:164`, `src/application/use_cases/calculate_trend.py:169`, `src/application/use_cases/calculate_trend.py:173`, `src/application/use_cases/calculate_trend.py:175`, `src/data/weather_client_core.py:73`, `src/data/weather_client_core.py:80`
- **Mi a probléma:** A trend batch fetch `lat=` és `lon=` kulcsszavakkal hívja a weather clientet, miközben a valós signature `latitude=` és `longitude=`. A batch kivételt elkapja és üres listát ad vissza, így a hiba csendben trend-adathiányként jelenhet meg.
- **Várható hatás:** Funkcionális correctness hiba, felesleges threadpool munka, félrevezető üres trend válaszok.
- **Javítási irány:** A port és az implementáció signature-jét egységesíteni kell, majd a batch exception handlinget úgy módosítani, hogy contract mismatch ne tűnhessen el normál adat-hiányként.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

#### Mypy és Ruff suppressziók tömegesen fedik el a kockázatot
- **Kategória:** Kódminőség
- **Severity:** MAGAS
- **Érintett fájlok:** `src/application/use_cases/analyze_multi_city.py:1`, `src/data/weather_client_core.py:1`, `src/api/main.py:1`, `src/api/routes/wind_rose.py:1`, `src/api/routes/wind_rose.py:2`
- **Mi a probléma:** Lokális `rg` számlálás alapján 499 `# mypy: ignore-errors` fájl és 96 `ruff: noqa` érintett fájl található a `src/` alatt. Ez a trend signature mismatchhez hasonló hibákat is könnyen elfedhet.
- **Várható hatás:** Karbantarthatósági kockázat, gyenge refaktor-biztonság, típushibák késői és runtime felfedezése.
- **Javítási irány:** Modulonkénti, prioritásalapú visszavezetés szükséges: először hot path portok, use case-ek és API DTO-k. A suppressziók eltávolítása ne egyszerre, hanem mérhető quality gate lépcsőkkel történjen.
- **Effort:** nagy
- **Bizonyosság:** MEGERŐSÍTETT

#### Frontend heatmap komponensek duplikált calendar/matrix logikát tartalmaznak
- **Kategória:** Kódminőség
- **Severity:** KÖZEPES
- **Érintett fájlok:** `frontend/src/components/analytics/TemperatureHeatmap.tsx:91`, `frontend/src/components/analytics/TemperatureHeatmap.tsx:172`, `frontend/src/components/analytics/WindHeatmap.tsx:99`, `frontend/src/components/analytics/WindHeatmap.tsx:182`, `frontend/src/components/analytics/PrecipitationHeatmap.tsx:79`, `frontend/src/components/analytics/PrecipitationHeatmap.tsx:160`, `frontend/src/components/analytics/WindGustHeatmap.tsx:1`
- **Mi a probléma:** Több heatmap komponens saját `formatDate`, week number, calendar matrix, cell render és month label logikát tart. A fájlméretek több komponensnél 300 sor körül vagy felett vannak.
- **Várható hatás:** Hibajavítás és feature változtatás többszörözött munka; edge case eltérések valószínűsége nő.
- **Javítási irány:** Közös calendar matrix builder és metric config alapú komponens csökkentené a duplikációt. A vizuális eltérések maradhatnak konfigurációban, nem copy-paste komponensekben.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### MultiCityEngine wrapper duplikál és hibás delegáló metódust tartalmaz
- **Kategória:** Kódminőség
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/analytics/multi_city_engine_core.py:56`, `src/analytics/multi_city_engine_core.py:111`, `src/analytics/multi_city_engine_core.py:166`, `src/analytics/multi_city_engine_core.py:235`, `src/analytics/multi_city_engine_core.py:192`
- **Mi a probléma:** A `MultiCityEngine` konstruktorban infrastruktúrát és use case-eket épít, majd sok metódusa delegáló wrapper. A `_process_dual_api_batch` metódus két paraméterrel hívja a három paraméteres `process_dual_api_batch` targetet, ami latent runtime hiba.
- **Várható hatás:** Dupla composition root, nehezebb ownership, dead/legacy API felület és rejtett runtime hiba.
- **Javítási irány:** A wrapper szerepét dönteni kell: vagy kompatibilitási facade minimális kóddal, vagy megszűnik a composition root javára. A hibás delegációt előbb teszttel kell lefedni, utána lehet biztonságosan rendezni.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Több frontend fájl túllépi a 300 soros maintainability küszöböt
- **Kategória:** Kódminőség
- **Severity:** KÖZEPES
- **Érintett fájlok:** `frontend/src/components/maps/hungaryCounties.geojson.ts:602`, `frontend/src/constants/hungary.ts:440`, `frontend/src/components/analytics/AnomalySettingsModal.tsx:430`, `frontend/src/pages/WindyDaysView.tsx:368`, `frontend/src/components/maps/HungaryMap.tsx:350`, `frontend/src/components/WindChart.tsx:347`, `frontend/src/components/common/HierarchicalSelector.tsx:317`, `frontend/src/contexts/ThemeContext.tsx:315`
- **Mi a probléma:** Több UI komponens és konstans fájl jelentősen meghaladja a projektben megadott 300 soros limitet. Ez nem közvetlen performance bottleneck, de refaktor és hibakeresés során mérhető karbantartási költség.
- **Várható hatás:** Olvashatóság és módosíthatóság romlik, tesztelési felület túl nagyra nő.
- **Javítási irány:** Feature-scope bontás, adatfájlok külön assetként kezelése, hookok és presentational komponensek szétválasztása. A heatmap és map komponenseknél ez párhuzamosan csökkentheti a bundle optimalizációs kockázatot is.
- **Effort:** közepes-nagy
- **Bizonyosság:** MEGERŐSÍTETT

#### INFO szintű per-record logolás analytics hot path-ban
- **Kategória:** Kódminőség / I/O
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/domain/analytics/services/analytics_transform_service.py:91`, `src/domain/analytics/services/analytics_transform_service.py:106`, `src/domain/analytics/services/analytics_transform_service.py:183`, `src/domain/analytics/services/analytics_transform_service.py:197`
- **Mi a probléma:** A transform service input és filtered record adatokat INFO szinten logol ciklusokban. Multi-city vagy detailed city esetén ez nagyszámú log sort és string formázást okozhat.
- **Várható hatás:** Log I/O, CPU és zajos observability; production log aggregator mellett költségként is jelentkezhet.
- **Javítási irány:** Per-record részletek DEBUG szintre vagy mintavételezett trace logba kerüljenek, INFO szinten csak aggregált számlálók maradjanak.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

#### TrendAnalyticsView export funkció UI placeholderként maradt
- **Kategória:** Kódminőség
- **Severity:** ALACSONY
- **Érintett fájlok:** `frontend/src/pages/TrendAnalyticsView.tsx:97`, `frontend/src/pages/TrendAnalyticsView.tsx:104`
- **Mi a probléma:** A PNG export gomb felhasználói alerttel jelzi, hogy az export még nincs implementálva. Ez technikai adósság és UX minőségi probléma.
- **Várható hatás:** Felhasználói workflow megszakad, a feature státusza nem egyértelmű a kódból.
- **Javítási irány:** Vagy valódi export implementáció, vagy a vezérlő elrejtése feature flag mögé, amíg nincs kész.
- **Effort:** kicsi-közepes
- **Bizonyosság:** MEGERŐSÍTETT

## 6. Build és startup

#### Frontend egyetlen 5,4 MB-os kezdő JS chunkot buildel
- **Kategória:** Build
- **Severity:** MAGAS
- **Érintett fájlok:** `frontend/src/App.tsx:7`, `frontend/src/App.tsx:17`, `frontend/src/App.tsx:120`, `frontend/src/App.tsx:131`, `frontend/src/components/charts/WindRoseChart.tsx:6`, `frontend/src/components/MapView.tsx:5`, `frontend/src/components/maps/HungaryMap.tsx:11`, `frontend/vite.config.ts:1`, `frontend/vite.config.ts:13`
- **Mi a probléma:** Az app minden oldalt statikusan importál, és a nagy chart/map könyvtárak is az induló bundle-be kerülnek. A lokális build asset ellenőrzés szerint a fő JS fájl kb. 5,4 MB.
- **Várható hatás:** Lassú első betöltés, parse/compile CPU overhead, mobilon és gyengébb gépen érzékelhető cold start.
- **Javítási irány:** Route-level `React.lazy`, dinamikus Plotly import, leaflet/map oldalak külön chunkba bontása és szükség esetén Vite `manualChunks`. A cél az, hogy az első viewport csak a kezdő route függőségeit töltse.
- **Effort:** kicsi-közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### API startup eager importálja a heavy analytics láncot
- **Kategória:** Build / Startup
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/api/main.py:14`, `src/api/main.py:24`, `src/api/routes/analytics.py:1`, `src/application/use_cases/calculate_trend.py:1`, `src/domain/analytics/services/trend_statistics.py:8`, `src/domain/analytics/services/trend_statistics.py:12`
- **Mi a probléma:** Az API main modul minden routert importál induláskor, az analytics route pedig behúzza a trend use case-et és a pandas/scipy/sklearn függőségeket. Lokális mérés: `import src.api.main` kb. 3017,9 ms; `-X importtime` szerint `src.api.main` kumulatív kb. 3,08 s, ebből `src.api.routes.analytics` kb. 2,59 s.
- **Várható hatás:** Lassabb cold start, fejlesztői feedback loop és container startup idő nő. Serverless vagy autoscaling környezetben közvetlen latency kockázat.
- **Javítási irány:** Heavy analytics importokat késleltetni lehet route handleren belül vagy service factory mögé, de csak tiszta dependency ownership mellett. Alternatív megoldás a trend szolgáltatás elkülönített lazy providerként való inicializálása.
- **Effort:** közepes
- **Bizonyosság:** MEGERŐSÍTETT

#### Per-request factory cache-ek nem hasznosulnak, mert új manager példányok jönnek létre
- **Kategória:** Build / Memória
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/infrastructure/container/factories.py:29`, `src/infrastructure/container/factories.py:38`, `src/api/routes/hungary.py:126`, `src/api/routes/hungary.py:192`, `src/api/routes/hungary.py:221`, `src/data/city_manager_hungarian.py:74`, `src/data/city_manager_hungarian.py:89`
- **Mi a probléma:** A Hungarian city manager tart instance cache-t, de a factory minden hívásra új `CityManagerStats()` példányt ad. Így requestek között a cache nem tud érdemben érvényesülni.
- **Várható hatás:** Felesleges DB lekérdezések és inicializáció; kis adatbázisnál nem kritikus, de interaktív endpointoknál könnyen mérhető.
- **Javítási irány:** Lifespan-scope manager vagy repository cache szükséges, explicit invalidációs modell nélkül csak read-only adatbázisokra.
- **Effort:** kicsi
- **Bizonyosság:** MEGERŐSÍTETT

## 7. Gyors nyerések — Top 5

1. **Autocomplete DB keresés indexelése és stale request védelem**
   - **Konkrét fájl + sorszám:** `src/infrastructure/repositories/city_repository_queries.py:147`, `frontend/src/components/common/CityAutocomplete.tsx:65`
   - **Jelenlegi megközelítés:** `%query%` jellegű `LOWER(...) LIKE` scan és debounce cancel nélkül.
   - **Javasolt megközelítés:** Normalizált keresőindex vagy FTS5, plusz frontend `AbortController` vagy request sequence guard.
   - **Várható hatás:** `[ms / olvashatóság]` gyorsabb autocomplete válaszidő, kevesebb DB CPU, kevesebb stale UI állapot.
   - **Effort becslés:** `[közepes 2-8h]`

2. **Per-request DI/provider inicializáció kiváltása lifespan-managed szolgáltatásokkal**
   - **Konkrét fájl + sorszám:** `src/infrastructure/container/composition_root.py:24`, `src/infrastructure/container/factories.py:41`, `src/api/routes/weather.py:29`
   - **Jelenlegi megközelítés:** Route handlerenként új use case, weather client és provider chain épül.
   - **Javasolt megközelítés:** FastAPI lifespan alatt épített, explicit `close()`-olható szolgáltatások, request paraméterekkel tisztán meghívott use case-ek.
   - **Várható hatás:** `[ms / MB / karbantarthatóság]` kb. 183,8 ms mért build overhead eltávolítható a hot request path-ból, kevesebb Session churn.
   - **Effort becslés:** `[közepes 2-8h]`

3. **Trend signature mismatch javítása és havi aggregátum egyszeri előállítása**
   - **Konkrét fájl + sorszám:** `src/application/use_cases/calculate_trend.py:164`, `src/domain/analytics/services/trend_calculator.py:151`, `src/domain/analytics/services/trend_data_processor.py:19`
   - **Jelenlegi megközelítés:** `lat`/`lon` kulcsszavak rossz contracttal, majd periódusonként ismételt lista-szűrés és dataframe építés.
   - **Javasolt megközelítés:** Port/implementáció signature egységesítése, majd egyszeri monthly aggregate és periódusonkénti slice.
   - **Várható hatás:** `[ms / karbantarthatóság]` correctness fix, kevesebb CPU hosszú trend lekéréseknél.
   - **Effort becslés:** `[kicsi <2h]` a signature fixre, `[közepes 2-8h]` az aggregációs optimalizációval együtt.

4. **Frontend route-level code splitting és Plotly lazy import**
   - **Konkrét fájl + sorszám:** `frontend/src/App.tsx:7`, `frontend/src/components/charts/WindRoseChart.tsx:6`, `frontend/vite.config.ts:1`
   - **Jelenlegi megközelítés:** Minden page és nagy chart/map függőség statikusan kerül a kezdő bundle-be.
   - **Javasolt megközelítés:** `React.lazy` route-ok, lazy WindRoseChart/Plotly, szükség esetén Vite manual chunkok.
   - **Várható hatás:** `[MB / ms]` 5,4 MB-os initial JS chunk jelentős csökkenése, jobb cold start.
   - **Effort becslés:** `[kicsi <2h]` alap route splitre, `[közepes 2-8h]` teljes chunk stratégia ellenőrzéssel.

5. **Heatmap calendar logika közösítése**
   - **Konkrét fájl + sorszám:** `frontend/src/components/analytics/TemperatureHeatmap.tsx:91`, `frontend/src/components/analytics/WindHeatmap.tsx:99`, `frontend/src/components/analytics/PrecipitationHeatmap.tsx:79`
   - **Jelenlegi megközelítés:** Több heatmap fájl külön implementálja ugyanazt a calendar matrix és cell render mintát.
   - **Javasolt megközelítés:** Közös calendar builder + metric config, külön stílus/threshold configgal.
   - **Várható hatás:** `[olvashatóság / karbantarthatóság]` kevesebb duplikáció, kisebb komponensek, alacsonyabb regressziós kockázat.
   - **Effort becslés:** `[közepes 2-8h]`

## 8. Prioritizált finding lista

| # | Finding | Hatás | Effort | Prioritás |
|---|---------|-------|--------|-----------|
| 1 | Trend use case rossz `WeatherClient` kulcsszóparamétereket használ, a hibát elnyeli | Correctness + felesleges háttérmunka | kicsi | P0 |
| 2 | Per-request composition root és provider inicializáció | Kérésenkénti ms overhead, Session churn | közepes | P0 |
| 3 | Város autocomplete indexet kerülő keresése | Interaktív API latency és DB CPU | közepes | P1 |
| 4 | Frontend egyetlen 5,4 MB-os kezdő JS chunkot buildel | Cold start MB és parse/compile idő | kicsi-közepes | P1 |
| 5 | Multi-city időjárás pipeline teljes city-day datasetet tart memóriában | O(városok * napok) memória | közepes | P1 |
| 6 | Multi-year frontend N darab backend kérést indít évszámonként | Round-trip és provider terhelés | közepes | P1 |
| 7 | API startup eager importálja a heavy analytics láncot | Kb. 3,0 s cold import | közepes | P2 |
| 8 | Hungary async endpointok szinkron DB munkát futtatnak event loop-ban | Tail latency concurrency alatt | kicsi-közepes | P2 |
| 9 | `get_cities_by_names` korrelált subquery és névindex hiány | Multi-city indítási DB overhead | közepes | P2 |
| 10 | Detailed city metrikák négyszer dolgozzák fel ugyanazt az idősor-listát | CPU/allokáció hosszabb range-nél | kicsi | P2 |
| 11 | `requests.Session` életciklus nincs lezárva | Socket/connection pool churn kockázat | közepes | P2 |
| 12 | Közös `WeatherClient` és `requests.Session` használat threadpoolból | Race/thread-safety kockázat | közepes | P2 |
| 13 | Mypy és Ruff suppressziók tömegesen fedik el a kockázatot | Refaktor-biztonság gyenge | nagy | P2 |
| 14 | Trend periódusok ismételt teljes lista-szűrése és dataframe építése | CPU/memória O(k*n) | közepes | P3 |
| 15 | Frontend heatmap komponensek duplikált calendar/matrix logikát tartalmaznak | Karbantarthatósági adósság | közepes | P3 |
| 16 | Rate limiter listát szűr és újraallokál minden requestnél | Magas request rate alatt overhead | kicsi | P3 |
| 17 | Wind rose irányonként újraszkenneli az observation listát | Alacsony CPU/allokáció overhead | kicsi | P3 |
| 18 | TrendAnalyticsView export funkció UI placeholderként maradt | UX és feature debt | kicsi-közepes | P4 |
