# meteo-analytics — Security Audit

Dátum: 2026-05-12 | Model: DeepSeek V4 (deepseek-tui 0.8.31)

## Executive summary (top kritikus finding-ek)

A kódbázis biztonsági szempontból **rendezett, de nem hibátlan**. Nincs találat KRITIKUS besorolással (nincs hardcoded credential, nincs `eval`/`exec`, nincs SQL injection, nincs kikapcsolt TLS verifikáció). Az alábbi MAGAS prioritású problémákat azonosítottam:

1. **Hibaválasz információszivárgás** — a `/api/analytics/trend` endpoint és a `uc_result.error_message` visszaadása a kliensnek belső implementációs részleteket, akár upstream API hibákat szivárogtathat.
2. **Fejlesztői függőségek production build-ben** — a frontend `package.json`-ben `@testing-library/*`, `vite-node`, `esbuild`, `typescript` tévesen `dependencies`-ben vannak `devDependencies` helyett.

A KÖZEPES kategóriába tartozik a rate limiter memóriaszivárgása, a megengedő CORS beállítások, valamint az API key rotáció hiánya.

---

## 1. Input validáció és injection

### 1.1 SQL Injection — MEGERŐSÍTETT: BIZTONSÁGOS

Az összes SQLite lekérdezés paraméterezett placeholder-eket (`?`) használ a `cursor.execute(query, params)` híváson keresztül. A dinamikus `IN (...)` klauzákban az f-string kizárólag a `?` placeholder-ek számát határozza meg, nem tartalmaz felhasználói inputot.

- **Érintett fájlok:** `src/infrastructure/repositories/city_repository_queries.py` 32, 54, 119, 138. sor
- **Bizonyosság:** MEGERŐSÍTETT (biztonságos)

### 1.2 Path Traversal — MEGERŐSÍTETT: VÉDETT

`CityRepositoryPaths._validate_path()` (`src/infrastructure/repositories/city_repository_paths.py` 23-32. sor) explicit ellenőrzi, hogy a feloldott útvonal egy megbízható alapkönyvtár alatt van-e (`_TRUSTED_BASES`). A `resolve(strict=False)` + `relative_to()` kombináció véd a `../` támadások ellen.

- **Megjegyzés:** Explicit `db_path` paraméter esetén (factory, tesztek) a validáció kihagyásra kerül (66-67. sor). Ez tesztkontextusban elfogadható, de production kódban a `get_city_repository_port()` mindig a default útvonalat használja, ami validált.
- **Bizonyosság:** MEGERŐSÍTETT (védett)

### 1.3 Command Injection — MEGERŐSÍTETT: NINCS

- Nincs `subprocess.call(shell=True)`, `os.system()`, vagy hasonló hívás a `src/` alatt.
- A `scripts/` shell szkriptek (`dev.sh`, `launch_meteo_analytics_fullstack.sh`) nem fogadnak tetszőleges felhasználói inputot — csak környezeti változókból dolgoznak.

### 1.4 Eval / Dinamikus kódvégrehajtás — MEGERŐSÍTETT: NINCS

- Nincs `eval()`, `exec()` (Python), `Function()` (JS) a kódbázisban.
- A PySide6 `app.exec()` és `dialog.exec()` hívások a Qt eseményhurok indítására szolgálnak, nem kódinterpretációra.
- **Bizonyosság:** MEGERŐSÍTETT (biztonságos)

### 1.5 Deserialization — MEGERŐSÍTETT: BIZTONSÁGOS

- Kizárólag `json.dumps`/`json.loads` használatos (`src/config/atomic_io.py` 13. sor, `src/config/usage_config.py`).
- Nincs `pickle`, `yaml.load` (unsafe), vagy `bincode`.
- **Bizonyosság:** MEGERŐSÍTETT (biztonságos)

### 1.6 Template Injection — MEGERŐSÍTETT: NINCS

- Nincs szerver-oldali template engine (Jinja2, Mako, stb.).
- Frontend: React JSX használ, amely alapértelmezetten escape-el. Nincs `dangerouslySetInnerHTML` a frontend kódban.
- **Bizonyosság:** MEGERŐSÍTETT (biztonságos)

---

## 2. Autentikáció és authorizáció

### 2.1 Hardcoded Credentials — MEGERŐSÍTETT: NINCS

- `METEOSTAT_API_KEY` és `API_KEY` kizárólag környezeti változóból (`os.getenv`) olvasva.
- `.env` placeholder értékeket tartalmaz (`your_rapidapi_key_here`, üres string), valós credential nélkül.
- `.env` szerepel a `.gitignore`-ban.
- `.secrets.baseline` csak tesztfájlokban lévő teszt API kulcs placeholder-eket jelöl.
- **Bizonyosság:** MEGERŐSÍTETT (nincs hardcoded credential)

#### [API Kulcs placeholder-ek tesztfájlokban]
- **Severity:** ALACSONY
- **CWE:** CWE-798 (Use of Hard-coded Credentials)
- **Érintett fájlok:** `tests/api/test_api_auth_middleware.py` (86, 110), `tests/api/test_api_auth_verify_key.py` (38, 52, 55), `tests/data/test_meteostat_provider_part1.py` (41), `tests/data/test_meteostat_provider_support.py` (58)
- **Mi a probléma:** A `.secrets.baseline` detektálta a teszt API kulcsokat. Ezek valószínűleg placeholder értékek teszteléshez, de ha valaha éles kulcs kerülne ide, a baseline elavulttá válhat.
- **Kihasználhatóság:** Jelenleg nem kihasználható (placeholder értékek). Ha éles kulcs kerülne tesztfájlba, a `.secrets.baseline` kivétele alapján a CI nem jelezné.
- **Hatás:** Alacsony — jelenlegi állapotban nincs éles credential kompromittálva.
- **Javítási irány:** Rendszeresen frissíteni a `.secrets.baseline`-t. A teszt kulcsokat érdemes egyértelműen placeholder formátumban tartani (pl. `test_api_key_placeholder_123`).
- **Bizonyosság:** MEGERŐSÍTETT (placeholder-ek, nem éles credential-ök)

### 2.2 API Key Authentikáció — MEGERŐSÍTETT: MEGFELELŐ

- `secrets.compare_digest()` használata a timing attack ellen (`src/api/main.py` 97, 144. sor).
- Production startup ellenőrzés: `_enforce_production_security()` blokkolja az indulást ha `APP_ENV=production` és `API_KEY` nincs beállítva (54. sor).
- Public/private endpoint szétválasztás: `/health` mindig publikus, `/docs` csak development-ben publikus (117-121. sor).
- Auth middleware minden nem-publikus endpointra érvényes (129-155. sor).
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

#### [API Key rotáció hiánya]
- **Severity:** KÖZEPES
- **CWE:** CWE-287 (Improper Authentication)
- **Érintett fájlok:** `src/api/main.py` 27-28, `src/config/api_config.py` 27-28
- **Mi a probléma:** Az API key statikus bearer token, nincs lejárati idő, nincs rotációs mechanizmus. Ha a kulcs kompromittálódik, nincs automatikus érvénytelenítés.
- **Kihasználhatóság:** Ellopott API key korlátlan ideig használható marad.
- **Hatás:** Adathozzáférés, API abuse.
- **Javítási irány:** JWT vagy időalapú token bevezetése, vagy minimum egy key revocation lista támogatása.
- **Bizonyosság:** MEGERŐSÍTETT

#### [Brute force védelem hiánya auth endpoint-on]
- **Severity:** ALACSONY
- **CWE:** CWE-307 (Improper Restriction of Excessive Authentication Attempts)
- **Érintett fájlok:** `src/api/main.py` 129-155
- **Mi a probléma:** A `/auth/status` endpoint (és implicit módon minden védett endpoint) ugyanazt az IP-alapú rate limitet használja mint a többi endpoint (60 req/60s production, 10000/60s development). Nincs specifikus brute force védelem az auth hibákra.
- **Kihasználhatóság:** Elosztott brute force támadás (több IP-ről) megkerülheti az IP-alapú rate limitet.
- **Hatás:** API key kitalálása brute force-szal (bár a `secrets.token_urlsafe(32)` erős kulcsot generál).
- **Javítási irány:** Sikertelen auth próbálkozások számlálása és exponenciális backoff.
- **Bizonyosság:** MEGERŐSÍTETT

### 2.3 Authorization (IDOR, privilege escalation) — MEGERŐSÍTETT: NINCS

- Az API nem használ felhasználói szerepköröket — egyetlen API key védi az összes endpointot.
- Nincs user-specifikus erőforrás, így IDOR nem releváns.
- Provider selection endpoint (`/api/providers/{provider_id}/select`) validálja a `provider_id`-t és nem enged tetszőleges értéket.
- **Bizonyosság:** MEGERŐSÍTETT (jelenlegi scope-ban nem releváns)

---

## 3. Érzékeny adatkezelés

#### [Hibaválasz információszivárgás — analytics endpoint]
- **Severity:** MAGAS
- **CWE:** CWE-209 (Generation of Error Message Containing Sensitive Information)
- **CVSS becslés:** 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
- **Érintett fájlok:** `src/api/routes/analytics.py` 72-75. sor
- **Mi a probléma:** Az általános kivételkezelő visszaadja a kliensnek a teljes hibaüzenetet: `detail=f"Trend calculation failed: {str(e)}"`. Ez tartalmazhat belső implementációs részleteket, library verziókat, fájlrendszer útvonalakat.
- **Kihasználhatóság:** Támadó szándékosan hibát provokálva információt szerezhet a belső rendszerről.
- **Hatás:** Információszivárgás — rendszerarchitektúra, library verziók, esetleg fájlrendszer útvonalak.
- **Javítási irány:** A 74. sort cserélni erre: `detail="Trend calculation failed"`. A teljes hibaüzenetet csak loggolni.
- **Bizonyosság:** MEGERŐSÍTETT

#### [Hibaválasz információszivárgás — upstream error_message]
- **Severity:** MAGAS
- **CWE:** CWE-209 (Generation of Error Message Containing Sensitive Information)
- **CVSS becslés:** 5.3
- **Érintett fájlok:** `src/api/routes/weather.py` 33. sor, `src/api/routes/single_city.py` 67. sor
- **Mi a probléma:** A use case `error_message` attribútuma közvetlenül visszakerül a kliensnek: `detail=uc_result.error_message or "Upstream error"`. Az upstream API-k (Open-Meteo, Meteostat) hibaüzenetei kerülhetnek ki, amelyek tartalmazhatnak API endpoint URL-eket, paramétereket.
- **Kihasználhatóság:** Támadó hibás kéréssel kicsikarhatja az upstream API belső hibaüzeneteit.
- **Hatás:** Upstream API implementációs részletek, endpoint-ok kiszivárgása.
- **Javítási irány:** Mindig a generikus `"Upstream error"` üzenetet visszaadni. Az `error_message` csak loggolásra.
- **Bizonyosság:** MEGERŐSÍTETT

#### [ValueError: detail=str(exc) — input validáció, elfogadható]
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/api/routes/weather.py` 36, `src/api/routes/single_city.py` 76, `src/api/routes/anomalies.py` 154, `src/api/routes/wind_rose_part3.py` 158, `src/api/routes/analytics.py` 68
- **Mi a probléma:** A `ValueError` ágak visszaadják a `str(exc)` értéket. Ezek jellemzően validációs hibák (pl. érvénytelen dátumformátum), ami elfogadható, de ha valamelyik `ValueError` véletlenül belső adatokat tartalmaz, az kiszivároghat.
- **Hatás:** Alacsony — validációs hibák esetén segíti a klienst. Figyelmet igényel, hogy a `ValueError`-t mindig csak validációs kontextusban használják.
- **Javítási irány:** Explicit validációs hibaosztály bevezetése (pl. `ValidationError`), és csak annak üzenetét visszaadni.
- **Bizonyosság:** MEGERŐSÍTETT (jelenleg alacsony kockázat)

### 3.2 Logolás — MEGERŐSÍTETT: MEGFELELŐ

- A `logger.error()` hívások tartalmazzák az `exc_info=True` paramétert, ami teljes traceback-et loggol. Ez a szerver oldalon rendben van, de a log fájlokat védeni kell.
- Nincs credential, API key, vagy PII a log üzenetekben.
- `logging.basicConfig(level=logging.INFO)` a modul szintjén (`src/api/main.py` 27. sor) — ez felülírhatja a hívó fél log konfigurációját. [ALACSONY]
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő, kivéve a basicConfig felülírást)

### 3.3 Titkosítás és átvitel — MEGERŐSÍTETT: MEGFELELŐ

- `requests.Session()` alapértelmezett `verify=True` beállítással (nincs `verify=False` a kódbázisban).
- Open-Meteo és Meteostat API hívások HTTPS-en keresztül történnek (`https://api.open-meteo.com`, `https://meteostat.p.rapidapi.com`).
- Nincs érzékeny adat titkosítatlanul tárolva fájlban (a használati statisztikák és provider preferenciák JSON fájlokban vannak, de nem tartalmaznak PII-t).
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 3.4 Adatbázis biztonság — MEGERŐSÍTETT: FIGYELMET IGÉNYEL

- Az SQLite adatbázisok a `data/` könyvtárban vannak, amely git által követett.
- A `data/` könyvtár nincs a `.gitignore`-ban. Ha az adatbázisok érzékeny adatokat tartalmaznának (pl. felhasználói preferenciák), azok verziókezelőbe kerülhetnek.
- **Hatás:** Alacsony — a jelenlegi adatbázisok publikus városadatokat tartalmaznak.
- **Javítási irány:** Runtime adatbázisok áthelyezése a `data/` alól, vagy a `*.db` fájlok hozzáadása a `.gitignore`-hoz.

---

## 4. Függőség-biztonság

#### [Fejlesztői függőségek production függőségként]
- **Severity:** KÖZEPES
- **CWE:** CWE-1104 (Use of Unmaintained Third Party Components)
- **Érintett fájlok:** `frontend/package.json` 7-16, 22. sor
- **Mi a probléma:** Az alábbi csomagok `dependencies`-ben vannak, pedig `devDependencies`-be kellene kerülniük:
  - `@testing-library/dom`, `@testing-library/jest-dom`, `@testing-library/react`, `@testing-library/user-event`
  - `@types/jest`, `@types/react`, `@types/react-dom`
  - `esbuild`, `vite-node`, `typescript`
  - `web-vitals`
- **Kihasználhatóság:** A production build-ben feleslegesen szerepelnek tesztelési keretrendszerek és típusdefiníciók, növelve a támadási felületet és a bundle méretét.
- **Hatás:** Nagyobb attack surface, potenciálisan ismert sérülékenységekkel rendelkező dev tool-ok production környezetben.
- **Javítási irány:** A felsorolt csomagok áthelyezése a `devDependencies` szekcióba.
- **Bizonyosság:** MEGERŐSÍTETT

#### [Verziókezelés — MEGERŐSÍTETT: RÉSZBEN MEGFELELŐ]
- **Python:** `requirements.lock` létezik, rögzített verziókkal. A `requirements.txt` és `requirements-dev.txt` minimum verziókat ad meg. Ez elfogadható.
- **Frontend:** A `package.json`-ben a verziók caret (`^`) prefix-szel vannak megadva, ami engedi a minor és patch frissítéseket. Ez szokványos, de a `package-lock.json` pontos verziókat rögzít.
- **Bizonyosság:** MEGERŐSÍTETT (részben megfelelő)

#### [Ismert CVE-k — HIPOTÉZIS – manuális ellenőrzés szükséges]
- **Severity:** KÖZEPES
- **Érintett fájlok:** `requirements.lock`, `frontend/package.json`
- **Mi a probléma:** Az audit időpontjában nem áll rendelkezésre valós idejű CVE adatbázis. A `pip-audit` és `bandit` konfigurálva van a projektben, de nem tudom ellenőrizni, hogy mikor futottak utoljára.
- **Javítási irány:** `pip-audit` és `npm audit` futtatása, eredmények integrálása a CI pipeline-ba.
- **Bizonyosság:** HIPOTÉZIS – manuális ellenőrzés szükséges

---

## 5. Konfiguráció és infrastruktúra

### 5.1 CORS — MEGERŐSÍTETT: FUNKCIONÁLIS, DE MEGENGEDŐ

- `allow_origins` környezeti változóból konfigurálható (`CORS_ORIGINS`), production-ben validált (nincs `*`).
- `allow_methods=["*"]` — minden HTTP metódus engedélyezett. [ALACSONY]
- `allow_headers=["*"]` — minden header engedélyezett. [ALACSONY]
- `allow_credentials=True` — szükséges a Vite proxy miatt, de wildcard origin-nel kombinálva veszélyes lenne (a production check ezt blokkolja).
- **Bizonyosság:** MEGERŐSÍTETT (production-ben biztonságos, development-ben megengedő)

### 5.2 Rate Limiting — MEGERŐSÍTETT: MEGFELELŐ, DE MEMÓRIASZIVÁRGÁS VESZÉLY

#### [Rate limiter memóriaszivárgás]
- **Severity:** KÖZEPES
- **CWE:** CWE-400 (Uncontrolled Resource Consumption)
- **Érintett fájlok:** `src/api/middleware/rate_limit.py` 55-66
- **Mi a probléma:** A `_timestamps` dictionary-ben az IP címek és timestamp-ek soha nem törlődnek — a sliding window csak a régi timestamp-eket szűri, de az IP kulcsok örökre megmaradnak. Hosszú üzemidő vagy elosztott támadás esetén a memóriahasználat növekszik.
- **Kihasználhatóság:** Támadó sok különböző (hamisított) IP címről indított kéréssel kimerítheti a szerver memóriáját.
- **Hatás:** Denial of Service — memória kimerülés.
- **Javítási irány:** Rendszeres cleanup: üres timestamp listával rendelkező IP kulcsok törlése, vagy TTL-alapú cache (pl. `cachetools.TTLCache`).
- **Bizonyosság:** MEGERŐSÍTETT

### 5.3 Security Headerek — MEGERŐSÍTETT: MEGFELELŐ

- `X-Content-Type-Options: nosniff` — minden válaszban.
- `X-Frame-Options: DENY` — minden válaszban.
- `X-XSS-Protection: 1; mode=block` — minden válaszban.
- `Strict-Transport-Security` — csak production-ben.
- `Content-Security-Policy: default-src 'self'` — csak production-ben.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 5.4 Deprecated API — ALACSONY

- `@app.on_event("startup")` (`src/api/main.py` 49. sor) — FastAPI deprecálta az `on_event`-et a `lifespan` context manager javára. Ez technikai adósság, nem közvetlen biztonsági rés, de a jövőbeli FastAPI verziókban megszűnhet a támogatás.
- **Bizonyosság:** MEGERŐSÍTETT

### 5.5 Hardcoded Abszolút Útvonal — ALACSONY

- `scripts/launch_meteo_analytics_fullstack.sh` 43. sor: `PROJECT_ROOT="/home/tibor/PythonProjects/meteo-analytics"` — hardcoded abszolút útvonal.
- **Hatás:** A script nem hordozható más gépekre/felhasználókra. Ha a fájl jogosultsága nem megfelelő, más felhasználó is tudja használni ugyanazt a környezetet (bár ez valószínűtlen desktop környezetben).
- **Bizonyosság:** MEGERŐSÍTETT

---

## 6. Trust boundary elemzés

### 6.1 API Boundary — MEGERŐSÍTETT: MEGFELELŐ

- Minden API request Pydantic model-be kerül validálásra a feldolgozás előtt.
- A DTO → domain transzformáció adapter rétegen keresztül történik (`src/api/adapters/`).
- Nincs `**kwargs` spreading vagy mass assignment az API rétegben.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 6.2 Input folyam — MEGERŐSÍTETT: TISZTA ARCHITEKTÚRA

- Request → Pydantic validáció → adapter DTO → use case → domain service.
- A rétegek közötti határok explicit típuskonverzióval vannak jelölve.
- A `run_in_threadpool` használata biztosítja, hogy a blokkoló I/O műveletek ne blokkolják az async event loop-ot.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 6.3 Implicit Bizalom — MEGERŐSÍTETT: NINCS PROBLÉMA

- Nincs implicit bizalom a weather provider-ek válaszaiban — minden válasz ellenőrzött (`response.json()["daily"]` / `response.json()["data"]`), hibás válasz esetén `WeatherAPIError`.
- A `MeteostatProvider.validate_provider()` ellenőrzi az API kulcs hosszát használat előtt.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

---

## 7. Concurrency

### 7.1 Rate Limiter Lock — MEGERŐSÍTETT: MEGFELELŐ

- `RateLimitMiddleware._lock` (`threading.Lock`) védi a `_timestamps` dictionary konkurens módosítását.
- A lock scope-ja minimális — csak a timestamp lista módosítására terjed ki.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 7.2 APIConfig Thread Safety — MEGERŐSÍTETT: MEGFELELŐ

- `APIConfig.reload()` `threading.Lock`-ot használ (`_reload_lock`) az osztályváltozók atomi frissítésére.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

### 7.3 UsageTracker Thread Safety — MEGERŐSÍTETT: MEGFELELŐ

- `UsageTracker._lock` védi a konkurens hozzáférést a használati statisztikákhoz.
- **Bizonyosság:** MEGERŐSÍTETT (megfelelő)

---

## 8. Attack surface összefoglaló

| Felület | Expozíció | Kockázat |
|---------|-----------|----------|
| `/health` | Publikus | Alacsony |
| `/docs`, `/openapi.json`, `/redoc` | Publikus (dev) / Védett (prod) | Alacsony |
| `/api/cities/search` | Védett (ha API key beállítva) | Közepes (input van) |
| `/api/weather/*` (POST) | Védett | Közepes (komplex input) |
| `/api/analytics/trend` (POST) | Védett | MAGAS (hibaüzenet szivárgás) |
| `/api/hungary/*` (GET) | Védett | Alacsony (read-only) |
| `/api/providers/*` (GET/POST) | Védett | Alacsony |
| `/auth/status` (GET) | Védett | Alacsony |
| Open-Meteo API | Külső, HTTPS | Alacsony |
| Meteostat API (RapidAPI) | Külső, HTTPS, API key | Közepes |

---

## 9. Prioritizált javítási lista

| # | Finding | Severity | Effort | Prioritás |
|---|---------|----------|--------|-----------|
| 1 | Hibaválasz szivárgás — analytics route `str(e)` | MAGAS | 1 sor | AZONNAL |
| 2 | Hibaválasz szivárgás — `uc_result.error_message` | MAGAS | 2 sor | AZONNAL |
| 3 | Frontend dev deps áthelyezése devDependencies-be | KÖZEPES | 20 sor | MA |
| 4 | Rate limiter memóriaszivárgás javítása | KÖZEPES | 20 sor | MA |
| 5 | API key rotáció bevezetése | KÖZEPES | Architektúra | HÉT |
| 6 | pip-audit / npm audit futtatás és CI integráció | KÖZEPES | 5 perc | MA |
| 7 | CORS allow_methods/allow_headers szűkítése | ALACSONY | 5 sor | HÉT |
| 8 | `@app.on_event` → lifespan migráció | ALACSONY | 15 sor | HÉT |
| 9 | Launch script hardcoded path javítása | ALACSONY | 1 sor | HÉT |
| 10 | `logging.basicConfig` eltávolítás main.py-ból | ALACSONY | 1 sor | HÉT |
| 11 | Database fájlok .gitignore-ba | ALACSONY | 1 sor | HÉT |
| 12 | Explicit ValidationError osztály bevezetése | ALACSONY | 20 sor | HÉT |
