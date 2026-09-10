# 06_REPAIR_PLAN — Végrehajtható javítási terv

**RUN_ID:** `20260910T092914Z`
**Mód:** read-only tervezés (nincs kódmódosítás, patch, javítás, telepítés, hálózat, production, valós credential)
**Bemenet:** `docs/audit/20260910T092914Z/05_VERIFICATION.md` + a P2–P4 findingek + a repó forrása
**Tervező session:** 2026-09-10, friss session (nem a P5 szerzője)

A P5 címkéje önmagában nem volt elég: minden tételt a kódból és futtatott parancsokból újraigazoltam. Az elvárt viselkedés forrása csak már létező artefaktum (séma, meglévő teszt, API-/kliensszerződés, dokumentált invariáns, biztonsági követelmény, mért performance-cél). A reproducer bizonyíték, nem specifikáció.

**Összegzés:** `READY_TO_FIX` = **3**; `NEEDS_EVIDENCE` = **1**; `SPEC_AMBIGUITY` = **12** (+ HN-1); `REJECTED` = hipotézisek + cáfolt / nem elérhető tételek. A karbantarthatósági tételek **külön fejezetben** vannak, nem a javítási sorban. A nulla `READY_TO_FIX` érvényes lett volna; itt három tétel teljesíti a küszöböt.

---

## 1. Snapshot- és scope-ellenőrzés

| Ellenőrzés | Eredmény | Parancs |
|---|---|---|
| HEAD | `c4793cdc9ef6161d2bcaf91d994bae2348426d78` | `git rev-parse HEAD` |
| Branch | `main` | `git rev-parse --abbrev-ref HEAD` |
| P1–P5 HEAD | **egyezik** | mind az öt riport fejléce ugyanezt a SHA-t rögzíti |
| `git diff --stat` | 8 fájl, **3 beszúrás / 823 törlés** | egyezik P1/P5 |
| Worktree porcelain | lásd §9 (záró status) | bit-pontosan a P1 §1.2 + `?? docs/` (audit-kimenet) + a P1-ben is szereplő untracked tool-mappák |
| Módosított termékfájlok mtime | `2026-08-21 17:18:21 +0200` (`src/api/main.py`, `src/config/api_config.py`, `.env.example`, `.secrets.baseline`) | `stat -c '%y'` — az audit-futás (2026-09-10) **előtti**; P5 óta a termékfájlok nem változtak |
| `05_VERIFICATION.md` mtime | `2026-09-10 15:26:43 +0200` | a P5 kimenete; P6 csak ezt a tervfájlt adja hozzá |

**Verdikt: ÉRVÉNYES.** Nincs snapshot-eltérés, nincs `BLOKKOLT`. A piszkos worktree a run része (auth-törlés a worktree-ben, nem a HEAD-en) — a P3/P5 ezt helyesen azonosította. A P6 nem módosított termékkódot, tesztet, sémát, lockot, configot.

**Scope:** a P5 által `VALID`-nak, illetve `RÉSZBEN_VALID`-nak (szűkített állítás) minősített findingek, plusz a P5 saját sweepjéből származó, bizonyított HN-1. Hipotézisek, `NEM_ELLENŐRIZHETŐ` tételek és a P5 által nem igazolt új jelöltek nem kerültek a javítási sorba.

---

## 2. Feldolgozott bemenet és a kihagyottak

### 2.1 Feldolgozott (újraigazolva)

| Forrás | ID-k | P5 verdikt | P6 újraigazolás |
|---|---|---|---|
| P2 | L-01…L-12 | VALID | a hivatkozott hely és a jelenség **áll** |
| P2 | L-13 | RÉSZBEN_VALID | **csak** a P5 szűkítése: `CityRepositoryPaths.validate_paths()` (közvetve/közvetlenül) nincs invoke-olva induláskor/kérésnél |
| P3 | S-01, S-02, S-03 | VALID | a hivatkozott hely **áll** |
| P4 | P-01…P-05, Q-01…Q-11 | VALID | a hivatkozott hely **áll** |
| P5 saját sweep | HN-1 | bizonyított kihagyott hiba | a RMW-út **áll** (`provider_config.py:175-190`) |

### 2.2 Kihagyottak → `REJECTED` (rövid indok a §6-ban)

| Kategória | ID-k | Indok |
|---|---|---|
| HIPOTÉZIS (P2) | H1, H2, H3 | a P6 utasítás szerint a hipotézis nem javítási tétel; H1 reprodukálva, de nincs termékbekötés |
| HIPOTÉZIS (P4) | H-P1…H-P7 | mérés/hálózat/GUI/`vite build` nélkül; P4/P5 helyesen tartotta őket a listán kívül |
| NEM_ELLENŐRIZHETŐ | H2, H3, H-P* | a P5 verdiktje |
| ÚJ_JELÖLT | — | P6 nem nyitott új findinget |
| P5 J1–J4, J6–J9 | — | P5 szerint nem FN (már P2–P4-ben megvannak vagy indokoltan elvetettek) |

A P4 §7 / P2 §7 elvetett jelölteket nem dolgoztam fel (nincs P5 VALID).

---

## 3. `READY_TO_FIX` tételek — végrehajtási sorrend

Egyszerre **egy** tétel adható a javítónak. Sorrend: (1) izolált, séma/adat nélküli API-500; (2) MAGAS adatsérülés a további íráson; (3) ugyanazon GUI-fájl bool-szerződése.

Közös regressziós parancsok (a javító **nem** módosíthatja őket):

```bash
./venv/bin/ruff check src tests
./venv/bin/ruff format --check src tests
./venv/bin/mypy src --ignore-missing-imports
./venv/bin/lint-imports
# izolált másolatban, hogy data/*.db ne íródjon:
#   rsync -a --exclude venv --exclude frontend/node_modules --exclude .git \
#     ./ /tmp/meteo-repair-<ID>/ && cd /tmp/meteo-repair-<ID>
./venv/bin/python -m pytest tests/ -q --timeout=10 --ignore=tests/gui -p no:cacheprovider
cd frontend && ./node_modules/.bin/tsc --noEmit && ./node_modules/.bin/vitest run
```

`./quality_gate.sh --quick` / `--full` **tilos** ebben a tervben: autofixelhet, illetve coverage-fájlt ír.

---

### RT-1 — Q-04 — `GET /api/hungary/settlements` megye nélkül `AttributeError` → HTTP 500

**Státusz:** `READY_TO_FIX`
**P5:** VALID (Q-04)

1. **Kanonikus hibaleírás.** A `GET /api/hungary/settlements` megye nélküli ága a registry-be kötött `CityManagerStats` nem létező `get_cities_for_region` metódusát hívja, ezért a kérés HTTP 500-at ad.
2. **Hely és érintett végrehajtási út.**
   `GET /api/hungary/settlements` (`src/api/routes/hungary.py:147-166`) → `_fetch_settlements` (`:68-72`) `county is None` ág → `city_manager.get_cities_for_region("Hungary", limit=limit)` → bound példány `CityManagerStats` (`src/infrastructure/city_manager/city_manager_stats.py`, a `ServiceRegistry.city_manager`) → `AttributeError` → `hungary.py:164-166` általános kivételkezelő → HTTP 500 `"Failed to get Hungarian settlements"`.
   A megyés ág (`get_cities_for_hungarian_county`) élő: Pest, limit=3 → 50 elem (a limitet a hívó a fetch után vágja, `:161`).
3. **Az elvárt viselkedés forrása.**
   - API-szerződés: `hungary.py:148-156` — `county` opcionális query param, a docstring „optional filtering”.
   - Kliensszerződés: `frontend/src/services/hungaryService.ts:89-111` — `county?` opcionális; a válasz `SettlementsResponse`.
   - Meglévő teszt: `tests/api/test_hungary_route.py::test_get_hungarian_settlements_uses_region_lookup_without_county` (`:102-128`) — `GET /api/hungary/settlements?limit=3` → **200**, és `get_cities_for_region("Hungary", limit=3)` hívás.
   - Port-szerződés: `src/domain/ports/city_weather_ports.py:36-41` (`CityManagerPort.get_cities_for_region`); a kötött osztály saját kommentje `city_manager_stats.py:182` „PORT IMPLEMENTATION (CityManagerPort)”.
   - Alak: a no-county stations-út már `get_settlements_bulk`-ot hív (`hungary.py:95-102` + `:197-230`); a bulk kulcskészlete (`city`, `megye`, `lat`, `lon`, `population`, `region_priority`, `settlement_type`) megegyezik `_serialize_settlement` mezőivel (`hungary.py:43-52`).
4. **Baseline bizonyíték.**
   Futtatva: `hasattr(CityManagerStats, "get_cities_for_region")` → `False`; élő `cm.get_cities_for_region("Hungary", limit=5)` → `AttributeError: 'CityManagerStats' object has no attribute 'get_cities_for_region'`; `_fetch_settlements(cm, None, 3)` → ugyanaz az `AttributeError`.
   `cm.get_settlements_bulk(limit=3)` → 3 elem, működik.
   A route-teszt **zöld**, mert `MagicMock`-olja a portot (`test_hungary_route.py:105,123,226`) — ez a vakfolt, nem a spec.
5. **A legkisebb szükséges módosítás hatóköre.**
   - **Érintett:** csak `src/infrastructure/city_manager/city_manager_stats.py` — új `get_cities_for_region(self, region: str, limit: int | None = None, max_cities: int | None = None) -> list[dict[str, Any]]`, amely `region == "Hungary"` esetén a már létező `get_settlements_bulk(limit=cap)`-ra delegál (`cap = limit or max_cities or 200`).
   - **Nem érinthető:** `hungary.py` (a meglévő teszt `get_cities_for_region.assert_called_once_with("Hungary", limit=3)`-at vár); tesztfájlok; séma; a port többi, szintén hiányzó metódusa (`get_cities_for_hungarian_region`, `find_cities_by_name`, … — ezeknek nincs hívási útja ezen a végponton; teljes port-kitöltés refaktor, lásd §7). Más `region` értékre ne találjunk ki feloldót: a termék csak `"Hungary"`-t ad át.
6. **Ellenőrzések.**
   - Célzott: a fenti `_fetch_settlements(CityManagerStats(), None, 3)` ne dobjon; lista, elemek `_serialize_settlement`-kompatibilis kulcsokkal; `pytest tests/api/test_hungary_route.py -q`.
   - Teljes: a közös regressziós parancsok fent.
7. **Kockázat és visszaállítás.**
   A no-county settlements eddig 500-at adott, tehát a 200-as válasz **új megfigyelhető viselkedés** a SPA HierarchicalSelectorán kívül (az mindig `county`-t küld, `HierarchicalSelector.tsx:146-159`). Túl nagy `limit` a bulk-on (max 500 a query-n) terhelheti a JSON-választ — a route `:161`-ben még egyszer vág. Rollback: `git revert` az egyetlen commithoz; a metódus törlése visszaállítja a 500-at.
8. **Függőségek és sorrend.** Nincs előfeltétel. Elsőnek futtatandó (nincs séma-/adatérintés).

---

### RT-2 — L-01 — Város újramentése elszakítja a `weather_data` előzményt

**Státusz:** `READY_TO_FIX`
**P5:** VALID (L-01)

1. **Kanonikus hibaleírás.** A GUI `INSERT OR REPLACE INTO cities` a `name UNIQUE` ütközéskor új `id`-t ad a városnak, a meglévő `weather_data` sorok a régi `city_id`-on maradnak, és árva rekordokká válnak.
2. **Hely és érintett végrehajtási út.**
   GUI városkiválasztás → `geocoding_handler.py:254` → `_save_city_to_database` (`:266-274`) → `DatabaseManager.save_city_to_database` (`database_manager.py:159-191`), SQL `:171-183` `INSERT OR REPLACE INTO cities (name, latitude, longitude, country, region)`.
   Séma (`data/meteo_data.db`, `mode=ro`): `cities.name TEXT UNIQUE`; `weather_data.city_id` → `FOREIGN KEY (city_id) REFERENCES cities (id)`; `UNIQUE(city_id, date)`.
   `PRAGMA foreign_keys` a kapcsolatnyitáskor **0**; a `src/`-ben nincs `PRAGMA foreign_keys=ON` (csak `src/scripts/hungarian_settlements_dump.sql` `OFF`).
3. **Az elvárt viselkedés forrása.**
   Élő séma-constraint: `FOREIGN KEY (city_id) REFERENCES cities (id)` + `cities.name TEXT UNIQUE` (`sqlite_master`, futtatva). A UNIQUE a városnevet egy sorhoz köti; az FK a `weather_data.city_id`-t létező `cities.id`-hoz. Az `INSERT OR REPLACE` SQLite-algoritmusa a UNIQUE ütközéskor **törli** a régi sort és **új id**-vel szúr be — ez az FK-invariánst sérti, ha az enforcement ki van kapcsolva.
4. **Baseline bizonyíték.**
   (a) Élő DB, `mode=ro`: `cities` = 60 sor, `id` 1..452; `weather_data` = 79 824 sor, 148 distinct `city_id`; **árva 62 957 (78,9 %)**; duplikált `(city_id, date)` csoport = 0; `PRAGMA foreign_keys` = 0.
   (b) In-memory reproducer (futtatva): egy város + egy weather-sor → `INSERT OR REPLACE` ugyanarra a névre → `cities.id` 1→2, weather `city_id=1` árva. Ugyanez `ON CONFLICT(name) DO UPDATE` mellett: `id` marad 1, árva 0.
   Reprodukció: a (b) snippet; a (a) számlálók `sqlite3 mode=ro` a `data/meteo_data.db`-n.
5. **A legkisebb szükséges módosítás hatóköre.**
   - **Érintett:** csak `save_city_to_database` SQL-je `database_manager.py:171-183`: `INSERT INTO cities (...) VALUES (...) ON CONFLICT(name) DO UPDATE SET latitude=excluded.latitude, longitude=excluded.longitude, country=excluded.country, region=excluded.region` (az `id` megmarad).
   - **Nem érinthető:** a `weather_data` `INSERT OR REPLACE` (`:244-251` — ott a `UNIQUE(city_id, date)` helyes upsert); séma / migráció / `PRAGMA foreign_keys=ON` (az élő 62 957 árva mellett az FK bekapcsolása a következő city-REPLACE-t `NO ACTION` miatt elhasaltatná); a 62 957 árva **visszamenőleges javítása** (az adatmigráció külön emberi döntés, lásd SA-1); tesztharnesz; GUI signalok.
6. **Ellenőrzések.**
   - Célzott: az in-memory (b) snippet az új SQL-lel (árva=0, id stabil); a `data/*.db` fájlokat **ne** írja a javító.
   - Teljes: közös regressziós parancsok. A GUI-út a CI `--ignore=tests/gui` miatt a suite-ban nincs fedve — a reproducer a baseline, nem egy most írt teszt a spec.
7. **Kockázat és visszaállítás.**
   Az `ON CONFLICT(name)` a UNIQUE-ra támaszkodik (a sémában megvan). Ha egy másolatban nincs UNIQUE, az SQL hibát ad — a mért `meteo_data.db`-n van. A már árva 62 957 sor **nem** javul; az előzmény-olvasó továbbra is hiányzik (L-10). Rollback: revert az egyetlen commithoz.
8. **Függőségek és sorrend.** RT-1 után. SA-1 (árva-visszamenés) **csak** ezután, és csak emberi döntéssel. L-08 ugyanazt a fájlt érinti, de másik metódust — RT-2 után, külön commitban.

---

### RT-3 — L-08 — A GUI időjárás-mentés 0 mentett sornál is sikert jelez

**Státusz:** `READY_TO_FIX`
**P5:** VALID (L-08)

1. **Kanonikus hibaleírás.** A `save_weather_to_database` a soronkénti hibákat elnyeli, majd `saved_count == 0` esetén is `True`-t ad vissza, és a UI „sikeres mentés” jelet kap.
2. **Hely és érintett végrehajtási út.**
   GUI időjárás-mentés → `weather_data_handler/core.py:103-112` → `DatabaseManager.save_weather_to_database` (`database_manager.py:193-272`): belső `except Exception: continue` (`:258-260`), egy `commit()` (`:262`), `return True` (`:268`). Hívó: `weather_saved_to_db.emit(success)` (`core.py:109`); a controller `Signal(bool)` (`app_controller.py:68`). A „nincs város” / „város nem található” ágak már `False`-t adnak (`:209`, `:231`).
3. **Az elvárt viselkedés forrása.**
   - Metódus-dokumentáció: `database_manager.py:203-204` — `Returns: bool: Sikeres volt-e a mentés`.
   - Signal-invariáns: `app_controller.py:68` — `weather_saved_to_db = Signal(bool)  # bool - sikeres mentés`.
   A „nincs mit menteni / a város hiányzik” ágak ugyanezt a bool-t `False`-ként értelmezik (`:209`, `:231`) — a zéró sikeres sor nem lehet „sikeres mentés”.
4. **Baseline bizonyíték.** Statikus `source → sink`: a `:241-260` ciklus `saved_count`-ot csak sikerre növeli, a `:268` `return True` a számlálótól független. Reprodukció (izolált, in-memory, a javító futtatja, a `data/*.db`-t nem írja): séma + city sor + `daily.time` nemüres, a sorépítés/INSERT kivételt dob (pl. hiányzó `temperature_2m_max` kulcs) → jelenleg `True`.
5. **A legkisebb szükséges módosítás hatóköre.**
   - **Érintett:** `database_manager.py:268` — `return saved_count > 0` (a `:265-267` log maradhat a számlálóval).
   - **Nem érinthető:** a `Signal(bool)` szignatúra (darabszámos signal = nagyobb szerződés-változás, SA-2); a soronkénti `continue` (részleges commit-szemantika külön döntés); RT-2 SQL-je; séma; teszt-harnesz.
6. **Ellenőrzések.**
   - Célzott: az in-memory reproducer a módosítás után `False`-t ad 0 mentett sornál, és `True`-t legalább egy sikeres sornál.
   - Teljes: közös regressziós parancsok. Nincs meglévő teszt erre a metódusra (`rg save_weather_to_database tests/` → 0).
7. **Kockázat és visszaállítás.** A UI eddig tévesen „mentve” jelet adhatott üres/hibás mentésnél; a `False` hibajelzést kapcsolhat be. Részleges mentés (`saved_count > 0` hibás sorok mellett) továbbra is `True` — ez szándékosan kint hagyott SA-2. Rollback: revert.
8. **Függőségek és sorrend.** RT-2 után (ugyanaz a fájl, másik metódus; külön commit, hogy az L-01 revertje ne vigye magával).

---

## 4. `NEEDS_EVIDENCE` tételek

### NE-1 — L-06 — Fetch-szintű `future.result(timeout=…)` no-op; a kliens 30 s-nál elvágja

**P5:** VALID (a kódsor igaz; a gyakoriság nem mérhető hálózat nélkül — P2 RÉSZBEN).

- A `weather_fetch_service.py:122-125` `as_completed` **után** hívja `future.result(timeout=self.request_timeout)`-ot — a future ekkor már kész, a 90 s-os `METEO_FETCH_TIMEOUT` (`config_settings.py:19`) nem korlátoz. HTTP-szintű 30 s timeout van (`APIConfig.REQUEST_TIMEOUT`, provider-hívások). A SPA timeout 30 000 ms (`apiClient.ts:74`).
- **Hiányzó bizonyíték:** (1) egyetlen kanonikus kérés-deadline szám, amelyhez a javítás igazodhat — 30 s (kliens / HTTP) vs 90 s (fetch-config) vs a P-01 55 éves alvás-padló; (2) hálózat nélküli gyakoriság: mennyi kérés esik a 30 s fölé élő providernél. Amíg ez a kettő nincs, a „legkisebb módosítás” nem egyértelmű (`as_completed(..., timeout=)`, retry-réteg összevonása, vagy kliens-timeout emelés — utóbbi P-01/SA-3).
- **Mi kell:** dokumentált vagy mért E2E-deadline (lásd SA-3), majd egy izolált, mock-HTTP + valós/`patch`-elt sleep mérés, hogy a no-op timeout tényleg a padló fölé visz-e. Addig ne javítsuk.

---

## 5. `SPEC_AMBIGUITY` tételek — emberi döntés kell

Ezek a jelenségek **igazoltak**, de az elvárt viselkedésnek nincs egyetlen, a allowlistán lévő forrása. A javító **nem** kaphatja meg őket, amíg a döntés nincs rögzítve.

| ID | Igazolt jelenség | Döntési kérdés | Miért nem READY |
|---|---|---|---|
| **SA-1** (L-01 adat) | 62 957 árva `weather_data` sor (78,9 %) a mért DB-ben | Visszamenőlegesen újraidézzük-e a sorokat a jelenlegi `cities.id`-hez, archiváljuk, vagy hagyjuk? | Adatmigráció; nincs retenciós/olvasó spec (L-10). Csak RT-2 után értelmes. |
| **SA-2** (L-08 részleges) | Részleges mentés (`0 < saved_count < N`) ma `True` | A részleges írás siker, hiba, vagy `(saved, failed)`? | A bool-szerződés a zéró esetet lefedi (RT-3); a részlegest nem. |
| **SA-3** (P-01 / L-02-szomszéd) | 5 év = 21 batch, **12,0 s** alvás-padló; 55 év = 224 batch, **133,8 s** alvás / 4 szál ≈ **33,5 s** > `apiClient` 30 000 ms. `TIME_PERIODS=[5,10,25,55]` (`trendService.ts:113`); a DTO `{5,10,25,55}`-re szűr (`trend_request.py:43-52`); `batch_delay=0.6`, `max_days_per_request=90`. A P4 35,2 s-os fal-időt **nem** futtattam újra; a 33,5 s alvás-padló a konstansokból adódik. | A 30 s a kliens-szerződés (szerver gyorsuljon / cache / kisebb default periódus), vagy a szerver a forrás (kliens-timeout emelendő), vagy az Open-Meteo 90 nap/0,6 s H-P6 szerint fölösleges? | Három, egymást kizáró „legkisebb” javítás. Nincs mért/dokumentált E2E-SLO a 30 s-on kívül, és az is kliens-oldali. |
| **SA-4** (L-02) | `POST /api/providers/{id}/select` fájlba ír (`providers.py:159-188`, OpenAPI: „active provider”); a fetch `DataConstants.USE_CASE_SOURCE_MAPPING` + `prefer_free` szerint dönt; `get_weather_client_port()` `preferred_provider="auto"`. A GUI `provider_routing.py` a prefs-et használja. | Az API-fetch a kiválasztott providert használja, vagy a use-case mapping a forrás, és a select csak megjelenítés? | Két dokumentált igazság. Ha a prefs-et a `WeatherClient`-be kötik, **H1** (`RecursionError` `preferred_provider="meteostat"` + `_select_provider(None)`, futtatva) azonnal élő 500-at ad — a bekötés nem atomi a rekurzió nélkül. |
| **SA-5** (L-03 / Q-06) | Provider-kiesés: multi-city/single-city `UseCaseResult` → 502 (`error_handling.py:29-33`, teszt: `test_error_handling.py::test_provider_error_returns_502`, `test_weather_route.py` 502); detailed 200 üres listákkal (`detailed_city.py:36-56`); trend `_empty_result` 200; anomáliák 200 null mezőkkel, a 404-ág elérhetetlen, mert a fetch 1 elemű `fetch_success=False` listát ad (`weather_fetch_service.py:179`). | Minden végpont 502-t adjon `ErrorCategory.PROVIDER`-re, vagy a 200+explicit hiba mező a szerződés? | A 502-mapping csak a `raise_for_use_case_result`-ot használó két route-ra spec (teszt). A többi végpont viselkedése nincs rögzítve. |
| **SA-6** (L-04) | `ProviderUsageService._usage_data`-t termék nem írja; a GET usage/status default nullák. Közben a GUI `UsageTracker` (`usage_config.py`) perzisztál. | Az API a `UsageTracker`-t tegye közzé, a weather-kliens számlálóit, vagy a usage végpont maradjon placeholder? | Két párhuzamos usage-rendszer; a GET mezői nem ígérik, hogy nem nullák. |
| **SA-7** (L-07) | Élő feloldás: `"Buda"` repo → Buda, US, pop. 14 348; manager → koordináta (47.4978, 19.0402) (Budapest). `"Kecske"` repo → `[]`; manager → (46.9074, 19.6917). `"Győr"` repo pop. 246 159 vs manager (47.6876, 17.6347) / HU settlements pop. 130 191. | Globális exact-IN vagy magyar prioritás+LIKE a kanonikus feloldás minden végponton? | Nincs közös városfeloldó-spec. A két DB és a két hívó (weather vs trend/wind-rose) szándékos variáns is lehet. |
| **SA-8** (L-10 / L-13 szűkítés) | Nincs `FROM weather_data` a `src/`-ben; `delete_old_weather_data` csak port-deklaráció. `/health` statikus `{"status":"ok"}` (`main.py:88-91`). `CityRepositoryPaths.validate_paths()` termékhívás: csak a delegáló `city_repository.py:51-53` teste, lifespan/route nem hívja. | Kell-e olvasó/retenció? A `/health` liveness maradjon (a teszt ezt kéri), vagy legyen readiness? | `tests/e2e/test_smoke.py:26-34`: „must be reachable without auth”, `status == "ok"`. `PRODUCTION_MANDATE.md` crit 15 Health check **N/A** solo desktop. A P5 szűkített L-13 állítás igaz, de nem ír elő readiness-t. |
| **SA-9** (S-01) | A worktree eltávolítja a HEAD-beli API-kulcs auth-ot: `verify_api_key`, `auth_middleware`, `PUBLIC_PATHS`, `/auth/status`, production fail-fast, `APIConfig.API_KEY` / `API_KEY_ENABLED`, `.env.example` `API_KEY` sor. `rg` auth-szimbólumokra a worktree `src/`-ben: 0 (csak `METEOSTAT_API_KEY`). | Visszaállítjuk a HEAD auth+fail-fast réteget, vagy a törlés szándékos, és loopback-only invariánst kényszerítünk? | P3 HITL. `PRODUCTION_MANDATE.md` crit 18 Auth **N/A** solo desktop. A frontend nem küld `X-API-Key`-t. A worktree konzisztens tisztítás (nem drift). |
| **SA-10** (S-03) | `.gitignore:43` tartalmazza a `.secrets.baseline`-t, a fájl **tracked** (`git ls-files`). A worktree-diff **7** eltávolított `Secret Keyword` bejegyzés, fájlok: 2× `test_api_auth_middleware.py`, 3× `test_api_auth_verify_key.py` (ezek **nincsenek** a fában), 1× `test_meteostat_provider_part1.py`, 1× `test_meteostat_provider_support.py` (ezek megvannak). A pre-commit hook a baseline meglétekor futtat (` .pre-commit-config.yaml:156-175`). | A baseline legyen tracked és review-zott (vegyük ki a gitignore-ból), vagy maradjon helyi, ignore-olt fájl? | Mindkettő érvényes secret-scan politika. Crit 20 a scan meglétét kéri, a gitignore-ellentmondást nem dönti el. A hashed_secret értékeket nem olvastam. |
| **SA-11** (HN-1) | `set_selected_provider`: load JSON → mezőcsere → `save_provider_preferences` (`provider_config.py:175-190`). `atomic_write_json` (`atomic_io.py:11-16`) a **fájlírást** védi crash ellen, a load→save ablakot nem. Két konkurens `POST /select` last-write-wins. | Kell-e folyamat-szintű lock/merge a prefs-re? | Nincs konkurens-írási spec. Asztali, egyfelhasználós kontextus. |
| **SA-12** (P-02) | Soronkénti `pd.to_datetime` (`trend_data_processor.py:19-43`). Nincs dokumentált CPU-SLO. | Van-e trend-CPU költségvetés, ami a vektorizálást kötelezővé teszi? | Helyes eredmény lassan is specifikáció-kompatibilis, amíg SA-3 nem rögzít padlót. A vektorizálás §7. |

---

## 6. `REJECTED` tételek — cáfolat

| ID | Cáfolat |
|---|---|
| **H1** | HIPOTÉZIS. Reprodukálva: `WeatherClientExtensions(preferred_provider="meteostat"); _select_provider(None)` → `RecursionError`. Termékkód `preferred_provider="auto"` (futtatva: `"open-meteo"`). Nincs javítási tétel, amíg SA-4 nem köti be. |
| **H2, H3** | NEM_ELLENŐRIZHETŐ / HIPOTÉZIS (nincs reprodukció / kulcsértéket nem olvasunk). |
| **H-P1…H-P7** | HIPOTÉZIS; P4/P5 a prioritási listán kívül tartotta. H-P6 SA-3 döntési inputja, nem önálló tétel. |
| **S-02** | A nem-production 10 000/60 s **dokumentált szándék**: `main.py:79` „production: strict; development: generous for tests”. `PRODUCTION_MANDATE.md` crit 21 Rate limiting **N/A** solo desktop. Nem hiba. |
| **Q-11** | `get_statistics_summary` `statistics.mean(values)` szűrés nélkül (`analytics_models.py:147-164`). Termékkódbeli hívó: **0** (`rg get_statistics_summary src/` csak a definíció). A meglévő tesztek numerikus értékeket fednek, `None`-t nem. Nincs elérhető termékhiba. |
| **L-12 mint termékhiba** | 9 fájl / **63** sormatch a P2 mintájára (futtatva; az előfordulás-szám 81, a P5 a sormatchet mérte). Ez teszt-vakfolt, nem runtime defekt. A javító a harneszt/ellenőrző parancsokat nem módosíthatja; új szerződés-teszt spec-döntés (SA-5). |
| **P5 J4** | `ThreadPoolExecutor` per-request: P4 mért indokkal elvetette; P5 egyetért. Nem tétel. |

A VALID-nak minősített, de **karbantartási** jellegű tételek (L-05, L-09, L-11, P-03…P-05, Q-01…Q-10 kivéve Q-04) nem REJECTED-ek: a §7-be kerültek, hogy ne keveredjenek a hibajavítási sorral.

---

## 7. Karbantarthatósági és refaktorálási javaslatok

**Ezek soha nem kerülhetnek ugyanabba a végrehajtási sorba, mint az RT-1…RT-3.** Nem `READY_TO_FIX` hibajavítások: vagy nincs funkcionális spec-sértés, vagy a javítás nagyobb átalakítás, mint a legkisebb szükséges módosítás.

| ID | Megfigyelés (újraigazolva) | Javaslat (nem utasítás) | Miért nem a javítási sor |
|---|---|---|---|
| L-05 | `build_service_registry()` → **+3** `WeatherClientExtensions`, **+3** `CityRepository`, **+2** `WeatherFetchService`; `is` False (futtatva) | Cache-elt portok a composition rootban | P2: nincs funkcionális hiba egy úton; CB-állapot szóródás SA-4/SA-6 nélkül nem spec |
| L-09 | `anomalies.py:57` modul-globális use case; `:133-136` holt `WeatherAnalysisRequest` | Registry-be tenni, holt sor törlése | P2: stateless, nincs funkcionális hiba |
| L-11 | `_TRUSTED_BASES.append` instance-metódusból (`city_repository_paths.py:50-53`) | Példányszintű trusted set | Nincs traversal-rés (canonical + `relative_to`); tesztizoláció |
| P-02 / Q-01 | Soronkénti `to_datetime`; API vs GUI duplikált regresszió, azonos `# r_squared via SS — sklearn r2_score convention` komment (`trend_statistics.py:44` / GUI `calculator.py`) | Vektorizálás + GUI → `TrendCalculatorPort` | Nincs CPU-SLO (SA-12); a GUI-másolat tesztelése coverage-omit mellett spec-döntés |
| P-03 | Pontonkénti `transData.transform` + `print` a tooltip hot pathon | Vektorizált `transform` + `argmin`; `print` le | Nincs GUI-latencia spec; GUI nem futott ebben a runban |
| P-04 | Anomália/wind-rose/providers SQLite/JSON az event loopon (11–25 ms B13/B15, P4) | `run_in_threadpool` a maradék I/O-ra | Nincs dokumentált non-blocking követelmény; ALACSONY, single-process |
| P-05 | `retry_delay = 1.0` hardcode (`weather_client_core.py:51`); 4 teszt valós sleep-pel. P4: 14,4 s / 26,9 s suite | Injektálható sleep a kliensben | CI-költség, nem runtime; a tesztek módosítása harnesz/spec határ |
| Q-02 | Két `analyze_wind_patterns`; GUI az application-utat futtatja, tesztek az infrastructure-t | Egy implementáció | Drift-kockázat; a teszt-átirányítás spec-döntés |
| Q-03 | **11** fájl+mappa ütközés (futtatva, lista a parancsnaplóban); a csomag nyer | A 11 árnyékolt `.py` törlése | 0 runtime-hatás, tisztítás |
| Q-05 | Holt: `src/presentation/api/`, `tests/api/api_auth_support.py` (0 hivatkozás), `anomaly_profile_manager`↔`anomaly_demo` pár; `wind_rose.py:15-20` wrapper dekorátor nélkül, csak teszt hívja | Törlés / teszt a regisztrált handlerre | Holt kód; a wrapper-teszt átírása harnesz |
| Q-06 | `except Exception` rétegenként **4 / 10 / 21 / 17 / 266** (futtatva, egyezik P4/P5) | Rétegenkénti hibapolitika | SA-5 nélkül politika-kitalálás |
| Q-07 | Autocomplete „indexelt” ág holt a szállított DB-n (`city_lower` nincs); `_has_column` PRAGMA kapcsolatonként | Séma-próba konstruktorban | Nincs perf-cél; a migrációs script hatása H-P/planner-függő |
| Q-08 | Beaufort-küszöb 43/61/90/119 vs 50/70/100/120 azonos címkékkel | Egy domain-tábla | Nincs rögzített Beaufort-forrás a repóban |
| Q-09 | `sqlite3.connect` + `close()` a `try`-ban; `session.close` a weather-infrában 0 | `try/finally` / `closing` | Korlátos leak; P4 nem perf-finding |
| Q-10 | `CORS_ORIGINS: ClassVar[list[str]]` mutálható; retry/batch konstansok szétszórva | Tuple + konfig-objektum | Hangolhatóság, nem viselkedési hiba (SA-3 döntéséig) |

---

## 8. Végrehajtási szerződés

1. A javító **egyszerre egy** `READY_TO_FIX` tételt kap (RT-1 → RT-2 → RT-3), a tétel teljes bizonyítékával és ellenőrzési tervével.
2. Tételenként **külön commit**. Commit üzenetben nincs secret, DSN, token.
3. Sikertelen célzott vagy teljes ellenőrzésnél: visszaállás az előző működő commitra (`git revert` / `git reset --hard` a tétel commitjára, a worktree piszkos auth-diffjét **ne** keverjük bele). A tétel ekkor `NEEDS_EVIDENCE`.
4. **Nincs „javítsd meg a javítást” hurok:** ugyanarra a tételre nem indul újabb automatikus javítási kör.
5. A javító **nem** módosíthatja: a tesztharnesst (`conftest.py`, pytest/vitest config, CI yaml), a specifikációt, a sémát / migrációt, az e dokumentumban rögzített ellenőrzési parancsokat.
6. A javító **nem** nyúl a §5–§7 tételeihez, és nem „mellesleg” refaktorál (L-05 cache, Q-03 törlés, P-02 vektorizálás, stb.).
7. A piszkos worktree auth-törlése (S-01 / SA-9) **nem** része egyik RT commitnak sem. A javító ne commitolja a `src/api/main.py` / `src/config/api_config.py` / `.env.example` worktree-diffjét az RT tételekkel.
8. `data/*.db` read-only marad minden ellenőrzésen (`mode=ro` vagy izolált másolat).
9. Secret: `.env` tartalmát, `hashed_secret` mezőket, API-kulcsokat a javító nem olvassa, nem naplózza, nem commitolja.

---

## 9. Parancsnapló (P6)

| Parancs | Eredmény |
|---|---|
| `git rev-parse HEAD`; `git status --porcelain`; `git diff --stat` | `c4793cdc…`; porcelain = P1 §1.2 + `?? docs/`; +3/−823, 8 fájl |
| `stat -c '%y'` dirty termékfájlok | 2026-08-21 17:18:21 +0200 |
| `sqlite3 mode=ro` `data/meteo_data.db` séma + COUNT | FK deklarált; cities 60 (id 1..452); weather 79 824; árva **62 957 (78,9 %)**; dup 0; `PRAGMA foreign_keys` = 0 |
| in-memory `INSERT OR REPLACE` vs `ON CONFLICT DO UPDATE` | REPLACE: id 1→2, 1 árva; ON CONFLICT: id 1, 0 árva |
| `CityRepository.get_cities_by_names` / `CityManagerStats.find_city_by_name` | Buda US 14348 vs (47.4978, 19.0402); Kecske `[]` vs (46.9074, 19.6917); Győr 246159 vs (47.6876, 17.6347) |
| `hasattr` + élő hívás + `_fetch_settlements(..., None, 3)` | `False` / `AttributeError` / `AttributeError`; Pest-county ág él; `get_settlements_bulk(3)` él |
| `build_service_registry` `gc` delta | WC +3, CR +3, WF +2 |
| `WeatherClientExtensions(preferred_provider="meteostat")._select_provider(None)` | `RecursionError`; `"auto"` → `"open-meteo"` |
| `git show HEAD:src/api/main.py` auth-szimbólumok | `APIKeyHeader`, `verify_api_key`, `auth_middleware`, `PUBLIC_PATHS`, `/auth/status` **jelen** a HEAD-en, **hiányoznak** a worktree-ből |
| `git diff .env.example` (értékek maszkolva) | 3 komment + `API_KEY=` sor törölve |
| `git diff .secrets.baseline` filename/type only | 7 eltávolított `Secret Keyword`; hashed_secret nem olvasva |
| `git ls-files .secrets.baseline` | tracked; `.gitignore:43` a mintát tartalmazza |
| Open-Meteo batch-számítás (`max_days=90`, `batch_delay=0.6`) | 5 y / 1825 nap → **21 batch, 12,0 s** alvás; 55 y / 20075 nap → 224 batch, 133,8 s / 4 szál ≈ **33,5 s** |
| `rg -c 'MagicMock(spec=ServiceRegistry)\|mock_services' tests/api/*.py` | 9 fájl, **63** sormatch |
| `except Exception` rétegenként | 4 / 10 / 21 / 17 / 266 |
| fájl+mappa ütközés `src/**/*.py` vs azonos nevű dir | **11** (lista: `base_chart.py`, `wind_rose_chart.py`, `weather_data_handler.py`, `anomaly_settings_dialog/ui_builder.py`, `quick_overview_tab.py`, `tab_manager.py`, `windy_days_tab.py`, `trend_analytics_tab/ui_builder.py`, `trend_data_processor.py`, `weather_data_bridge.py`, `main_window_actions.py`) |
| `CityManagerPort` vs `CityManagerStats` hiányzó nevek | `get_cities_for_region` + 8 további (csak az előbbi a settlements no-county hívási út) |
| `rg get_statistics_summary src/` | csak a definíció |
| `rg FROM weather_data src/` | 0 |
| `rg foreign_keys src/` | csak dump `OFF` |
| P6 **nem** futtatta | teljes pytest, vitest, ruff/mypy, pip-audit, npm audit, GUI, hálózat, `quality_gate.sh` (írhat / autofix) |

---

## 10. Záró `git status`

```
 M .env.example
 D .qwen/settings.json
 M .secrets.baseline
 D "200 | sort -rn | head -20"
 D ARCHITECTURE.md
 D FINAL_VERIFY.md
 M learnings.md
 M src/api/main.py
 M src/config/api_config.py
?? .deepseek/
?? .reasonix/
?? .repowise/
?? docs/
?? reasonix.toml
```

A termék worktree **azonos** a P1–P5 snapshotjával (auth-diff és törölt docok változatlanok). E futás új artefaktumai: `docs/audit/20260910T092914Z/06_REPAIR_PLAN.md` (untracked `docs/` alatt) és a session-záró `learnings.md` AKTUÁLIS ÁLLAPOT + NAPLÓ frissítés (AGENTS.md kötelező checkpoint, nem termékváltozás). Termékkód, teszt, séma, lock, config nem módosult.
