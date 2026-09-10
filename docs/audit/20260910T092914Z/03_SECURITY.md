# 03_SECURITY — AppSec audit (támadói nézőpont, read-only)

**RUN_ID:** `20260910T092914Z`
**Mód:** read-only (kód, teszt, config, lock **nem** módosult; exploit nem futott; telepítés/hálózat nem történt)
**Bemenet:** `docs/audit/20260910T092914Z/01_MAP.md`, `02_LOGIC.md` + a repó tényleges forrása
**Repo gyökér:** `/home/tibor/PythonProjects/meteo-analytics`
**Snapshot (ellenőrizve):** HEAD `c4793cdc9ef6161d2bcaf91d994bae2348426d78`, branch `main`; a `git status --porcelain` **egyezik** a térkép §1.2 listájával, az egyetlen többlet a `?? docs/` (az audit saját kimenete) → **nincs snapshot-eltérés, nincs `BLOKKOLT`**
**Mérési ablak:** 2026-09-10 10:01–10:06 UTC

> **Futáskorlát-figyelmeztetés (őszinte lefedettség).** A feltáró fázist a host költségvetés-korlátja
> lezárta, mielőtt minden kategória sweepje befejeződött volna. Ezért a **negatív („nincs finding”)
> állítások nem teljesek**: ahol a sweep nem fejeződött be, ott a lefedettség `RÉSZLEGES`, illetve
> `BLOKKOLT`, és **nem** állítom, hogy az adott kategória biztonságos. A `01_MAP` és a `02_LOGIC` által
> már megmért tényeket átvettem (jelölés: „02_LOGIC-ból átvéve”), de **nem** kezelem őket saját
> mérésként. Ahol egy korábbi állításomat pontosítani kellett, az a §7-ben és a lábjegyzetekben látszik.

---

## 1. Deployment- és threat-kontextus

| Dimenzió | Mért állapot | Bizonyíték |
|----------|--------------|------------|
| Deployment | **asztali (PySide6 GUI) + helyi uvicorn API + helyi Vite dev SPA**; nincs konténer/orchestrator | `01_MAP` §1.4 (`Dockerfile/compose/k8s/helm/terraform` → nincs), §5.4 |
| Hálózati kitettség (dokumentált indítás) | **loopback**: `--host 127.0.0.1` mindkét launcherben; a README uvicorn-parancsa host nélkül (uvicorn default = `127.0.0.1`) | `scripts/dev.sh:35-36,62`, `scripts/launch_meteo_analytics_fullstack.sh:121`, `README.md:36` |
| Reverse proxy / TLS | nincs a repóban (nincs nginx/traefik config, nincs TLS-terminálás) | `01_MAP` §1.4 |
| Tenancy | **single-user / single-tenant**; nincs felhasználó-fogalom, nincs session/cookie/login | `src/api/main.py` teljes olvasás; `rg 'APIKeyHeader\|X-API-Key\|API_KEY\|verify_api_key\|auth_middleware' src/` → csak `METEOSTAT_API_KEY` találatok |
| Bemenet jellege | **anonim** (nincs hitelesítés a worktree állapotában), szerkezetileg kötött: városnév, évszám-lista, query_type enum, régió-kulcs | `01_MAP` §5.2 (22 handler), §7 (Pydantic DTO-k) |
| Kezelt adatok érzékenysége | **alacsony**: nyilvános időjárás-adat; `data/user_preferences/*.json` felhasználói preferenciák (nem PII-minőség); `data/*.db` helyi katalógusok | `01_MAP` §5.5 |
| Secret-ek | egy harmadik fél kulcsa: `METEOSTAT_API_KEY` (RapidAPI, **fizetős kvóta**: `METEOSTAT_MONTHLY_LIMIT = 10000`, havi) | `src/config/api_config.py:42`, `01_MAP` §5.5 |
| `APP_ENV=production` | **létező, dokumentált mód** (a CORS-wildcard fail-fast erre épül) — a „production” feltételezés nem légből kapott | `src/api/main.py:33-39`, `01_MAP` §5.5 (`APP_ENV` env) |

**Kalibrált severity-modell.** Internetes, multi-tenant, privilegizált felülettel rendelkező rendszer **nincs**: a dokumentált futás loopback-only, egyfelhasználós, alacsony adatérzékenységgel. Ezért:

- `KRITIKUS`-ra csak akkor lenne alap, ha a worktree-t `APP_ENV=production`-nal, nem-loopback binddal (LAN/proxy/internet) futtatnák — ez **nem** a dokumentált indítás, de a kód ezt engedi, és a védelmet (fail-fast) épp eltávolította.
- A reális, bizonyított hatás így: **hitelesítés nélküli hozzáférés a helyi API-hoz** (bármely lokális folyamat, illetve böngészőből engedélyezett originról induló kérés), **fizetős provider-kvóta égetése**, és a meglévő **erőforrás-igényes lánc** (02_LOGIC L-06: városonként akár ~190–380 s) DoS-jellegű terhelése — a jelen kontextusban `MAGAS`, nem `KRITIKUS`.

---

## 2. Attack surface és trust boundary

Bemenetek a `01_MAP` §5.2 listája szerint (**átvéve**; saját újraszámlálás nem történt): **22 HTTP handler**, ebből 1 public health, 21 funkcionális (6 POST + 15 GET). Külső integráció: Open-Meteo + Meteostat (kimenő). Nincs upload, nincs webhook, nincs admin végpont, nincs CLI-bemenet a szerveren, nincs worker-queue.

| Bemenet | AuthN | AuthZ / tenant-guard | Validáció | Elért érzékeny sink | Bizonyíték |
|---------|-------|----------------------|-----------|---------------------|------------|
| `GET /health` | nincs (szándékolt) | n/a | nincs (statikus) | — | `src/api/main.py:88-91` |
| `POST /api/weather/{multi-city, single-city, single-city-detailed, anomalies, multi-year-batch, wind-rose}` | **nincs** | nincs (nincs szerep) | Pydantic DTO (+ route-szintű ellenőrzés) | kimenő provider-hívás (fizetős kvóta), `data/*.db` olvasás | `src/api/main.py` (nincs auth middleware), `01_MAP` §5.2/§7 |
| `POST /api/analytics/trend` | **nincs** | nincs | `trend_request.py` `{5,10,25,55}` halmaz-szűrés (02_LOGIC §7) | több év-batch provider-hívás | ugyanaz |
| `GET /api/cities/search`, `/api/hungary/*` | **nincs** | nincs | query param, LIKE-escape | `data/cities.db`, `data/hungarian_settlements.db` olvasás | `01_MAP` §5.2 |
| `GET/POST /api/providers/*` | **nincs** | nincs | `{provider_id}` path param | **állapotmódosítás**: `data/user_preferences/*.json` írás (`set_selected_provider`) | `02_LOGIC` L-02; `01_MAP` §5.5 |
| Interfész `/docs`, `/openapi.json`, `/redoc` | **nincs** | nincs | — | séma-kinyerés | FastAPI default + a HEAD-beli `PUBLIC_PATHS` logika eltávolítása (`git diff src/api/main.py`) |
| CORS | nem auth-kontroll | — | origin allowlist (`CORS_ORIGINS`) | — | `src/api/main.py:70-77` |
| Rate limit | nem auth | — | 60/60 s (production) / **10000/60 s (dev)** | — | `src/api/main.py:79-85` |

**Trust boundary:** loopback → lokális folyamatok (és az engedélyezett originról futó böngésző-JS). A CORS **kizárólag** böngésző-oldali korlát: szerveroldali klienst (curl, script) nem gátol. A kimenő irány (Open-Meteo/Meteostat) a trust boundary másik éle: a kulcs és a fizetős kvóta védelme a támadói cél.

---

## 3. Kategóriánkénti lefedettség

| Kategória | Lefedettség | Mit jelent pontosan |
|-----------|-------------|---------------------|
| Attack surface / trust boundary | **TELJES** (a 22 handler listjére, `01_MAP` §5.2 alapján) | `src/api/main.py` teljes olvasás + auth-szimbólum grep a `src/`-en |
| AuthN (hitelesítés megléte/hiánya) | **TELJES** a kulcs-alapú mechanizmusra | main.py teljes olvasás + `rg 'APIKeyHeader\|X-API-Key\|API_KEY\|verify_api_key\|auth_middleware' src/` → 0 auth-találat |
| AuthZ / IDOR / tenant-izoláció | **NEM RELEVÁNS** (nincs szerep, nincs user, nincs tenant); a state-módosító `providers/select` végpont jogosultság nélkül hívható (S-01) | nincs user-modell a kódban |
| Session/token életciklus, jelszó-hash, CSRF | **NEM RELEVÁNS** (nincs session/cookie/login) | grep + main.py olvasás |
| Injection (SQL / command / template / expression) | **RÉSZLEGES** — lásd §6 és §7 | `rg` minták: `execute(f"`, `.format(`, `% (`, `eval/exec/os.system/subprocess/shell=True` |
| Unsafe deserialization / YAML / XML | **RÉSZLEGES** | grep `pickle.load`, `yaml.load`, `tarfile`, `zipfile`, `extractall` a `src/`-en → 0 találat; `01_MAP` §4.1: `yaml`/`PIL` import nincs |
| XSS / unsafe HTML (frontend) | **RÉSZLEGES** | `rg 'dangerouslySetInnerHTML\|innerHTML\|document.write\|new Function\|eval\('` `frontend/src` → 0 találat (page-szintű komponensek nem lettek végigolvasva) |
| SSRF / unsafe redirect | **RÉSZLEGES** | a 22 handler egyike sem fogad URL-t (`01_MAP` §5.2 + DTO-k); a provider base URL env/config, nem kérés-paraméter → elvetett jelölt, de nem teljes sweep |
| Path traversal / upload / archívum | **RÉSZLEGES** (traversal), **NEM RELEVÁNS** (upload/archívum) | traversal: `02_LOGIC` L-11 (átvéve) + `city_repository_paths.resolve/relative_to`; upload/archívum: nincs ilyen végpont/handler |
| Secrets (jelenlegi tree) | **RÉSZBEN** | `.env` untracked + `.gitignore` fedi; `.env.example` tisztítás mérve |
| Secrets (Git history) | **BLOKKOLT** | history-scan nem futott (futáskorlát) → `SZKEN BLOKKOLT` |
| Logolás / hibaszivárgás | **RÉSZLEGES** | `FastAPI(...)` `debug=True` nélkül (main.py:52); provider-logolás mintavétel; a route-ok `exc_info=True`-t használnak (02_LOGIC §5) |
| CORS / security headerek / rate limit / debug-expozíció | **TELJES** a `src/api/main.py`-ra | teljes fájlolvasás |
| TLS-verifikáció | **RÉSZLEGES** | `rg 'verify\s*=\s*False' src/ frontend/src scripts/` → 0 találat |
| Supply chain / CVE | **BLOKKOLT** → `CVE-ELLENŐRZÉS BLOKKOLT` | `pip-audit` / `npm audit` nem futott (futáskorlát); a manifest/lock elemzés a `01_MAP` §1.4/§3.6-ból **átvéve** |
| TOCTOU / permission race / shared state | **RÉSZLEGES** | saját mérés: nincs; `02_LOGIC` L-05/L-11 + `atomic_io` (átvéve) |

---

## 4. Meglévő védelmek (bekötve)

| Védelem | Hely | Állapot |
|---------|------|---------|
| API-kulcs auth (`X-API-Key`, `secrets.compare_digest`, production fail-fast, `/auth/status`) | HEAD `src/api/main.py:33-38, 96-176, 178-192` | **a worktree-ből eltávolítva** → S-01 |
| Security headerek (`nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`; production: HSTS + `CSP: default-src 'self'`) | `src/api/main.py:55-67` | aktív |
| CORS allowlist + production wildcard fail-fast | `src/api/main.py:33-38, 70-77` | aktív |
| Rate limit middleware (60/60 s production) | `src/api/main.py:79-85` + `src/api/middleware/rate_limit.py` | aktív; XFF csak `TRUSTED_PROXIES`-ból (01_MAP §7) |
| Pydantic request-DTO validáció | `src/api/dto/*` | aktív (01_MAP §7) |
| Hibakód-leképezés (`UseCaseResult` → 400/502/500) | `src/api/error_handling.py` | aktív (01_MAP §7) |
| `debug` mód kikapcsolva (nincs stack-trace a válaszban) | `src/api/main.py:52` | aktív (saját olvasás) |
| SQL paraméterezés + LIKE-escape | `city_repository_queries.py`, `like_utils.escape_like` | aktív (01_MAP §7) |
| Atomic JSON írás | `src/config/atomic_io.py` | aktív (01_MAP §7) |
| Titok-tárolás: `.env` untracked, `.gitignore` fedi; `detect-secrets` pre-commit + baseline | `.gitignore:42-44`, `.pre-commit-config.yaml` | aktív, de ellentmondásos baseline-kezeléssel (S-03) |
| Rétegszerződés (domain tilos: fastapi/httpx/requests/…), CI: ruff+mypy+pytest+cov, bandit | `.importlinter`, `.github/workflows/*` | aktív (01_MAP §3.2, §7) |
| API réteg nem ír adatbázist | 02_LOGIC §9 parancsnapló (`INSERT INTO\|UPDATE\|DELETE\|commit` a GUI nélkül → 0) | **átvéve**, nem saját mérés |

---

## 5. Aktív sérülékenységek

### [S-01] [MAGAS] [MEGERŐSÍTETT] A worktree eltávolítja a teljes API-hitelesítést, és ezzel a production fail-fast védelmet is — CWE-306 / CWE-1188

- **Hely:** `git diff src/api/main.py` (HEAD 33-38, 96-176, 178-192 eltávolítva), `git diff src/config/api_config.py` (HEAD 46-48, 84-86), `git diff .env.example` (4 sor: `API_KEY` sor + generálási útmutató).
- **source → guard → sink:**
  - **source:** bármely HTTP kliens a 21 nem-public handlerre (`01_MAP` §5.2), illetve `GET /docs|/openapi.json|/redoc`; lokálisan bármely folyamat, hálózaton bárki, ha a bind nem loopback.
  - **guard:** **nincs.** `verify_api_key`, `auth_middleware`, `PUBLIC_PATHS`/`_DOCS_PATHS`, `/auth/status` és a `API_KEY_ENABLED` flag mind hiányzik a worktree-ből; `rg 'APIKeyHeader|X-API-Key|API_KEY|verify_api_key|auth_middleware' src/` → **0** auth-találat (csak `METEOSTAT_API_KEY` kulcs-hivatkozások). A CORS **nem** szerveroldali kontroll, a rate limit pedig nem auth.
  - **sink:** use case-végrehajtás → (a) **fizetős** Meteostat/Open-Meteo hívások (`APIConfig.METEOSTAT_MONTHLY_LIMIT = 10000`), (b) `POST /api/providers/{id}/select` → `data/user_preferences/*.json` **írás**, (c) `data/*.db` olvasás (város-, település-katalógus), (d) `/docs` séma-kinyerés.
- **Elkülönítés (`KIHASZNÁLHATÓ` / `FELTÉTELES`):**
  - **FELTÉTELES** a dokumentált, loopback-only asztali futásban (§1): a hatás lokális, de a védelem akkor is elveszett — bármely lokális folyamat/skript korlátlanul hívhatja az API-t, és a havi 10 000-es fizetős kvóta védtelen.
  - **KIHASZNÁLHATÓ** `APP_ENV=production` alatt nem-loopback binddal (LAN, proxy, tunnel): a startup **nem** fail-fastel API-kulcs hiányában (a guardot eltávolították), így a rendszer **hitelesítés nélkül** indul és szolgál ki. Az `APP_ENV=production` nem hipotetikus mód: a kód erre építi a CORS- és a header-politikát.
- **Feltételek:** (a) a worktree állapotában futó szerver; (b) remote forgatókönyvhöz nem-loopback bind + elérhető port.
- **Meglévő védelem és cáfolatkísérletek:** (1) *„talán másutt van auth”* → grep a `src/`-en minden auth-szimbólumra: 0 találat; a GUI és a frontend felől sincs token (`02_LOGIC` §2: `rg 'X-API-Key|API_KEY|auth/status' frontend/src tests/api/api_auth_support.py` → 0). (2) *„a CORS véd”* → cáfolva: böngésző-oldali korlát, szerveroldali klienst nem érint. (3) *„a rate limit véd”* → cáfolva: 60 kérés/perc csak lassítja a visszaélést, `APP_ENV` nélkül **10000/60 s** (`src/api/main.py:79-85`). (4) *„a hálózat nem éri el”* → csak a dokumentált launcherre igaz (loopback).
- **Bizonyított hatás:** a hitelesítés és a hozzá tartozó üzemeltetési biztosíték („nem indul el kulcs nélkül”) egyaránt megszűnt a worktree-ben; a kísérő fájlok (`.env.example`, `.secrets.baseline`) konzisztensen lettek tisztítva — vagyis ez **nem véletlen drift, hanem tudatos eltávolítás** (a hozzá tartozó teszt-fájlok már a HEAD-on sincsenek meg: `ls tests/api | grep -i auth` → csak az árva `api_auth_support.py`, amire a `01_MAP` §6.1 szerint 0 teszt gyűlik).
- **Javítási irány (max. 2 mondat):** vagy állítsd vissza a HEAD-beli auth réteget (middleware + production fail-fast + `API_KEY` env), vagy — ha a hitelesítés szándékosan nem kell — dokumentáld és kényszerítsd a loopback-only invariánst (bind-check a launcherben, és `APP_ENV=production` alatt továbbra is fail-fast, explicit „insecure” opt-in nélkül).
- **HITL-döntés:** a jelentés nem dönti el, hogy a törlés kívánt állapot-e; a worktree szándékosnak tűnő változását **nem** módosítottam.

### [S-02] [ALACSONY] [MEGERŐSÍTETT] A dev profilban a rate limit gyakorlatilag ki van kapcsolva, miközben a hitelesítés is hiányzik — CWE-770

- **Hely:** `src/api/main.py:79-85`; `src/api/middleware/rate_limit.py`.
- **source → guard → sink:** bármely (lokális vagy engedélyezett originról érkező) kliens → a guard a `max_requests=10000/60 s` nem-production ág → sink: a provider-hívásokat indító use case-ek, városonként a 02_LOGIC L-06 szerinti lassú lánccal.
- **Elkülönítés:** `DEFENSE_IN_DEPTH` (loopback-kontextusban lokális erőforrás-kimerülés; a produkciós ág 60/60 s-ot ad).
- **Meglévő védelem és cáfolat:** van production ág és `TRUSTED_PROXIES`-hoz kötött XFF (01_MAP §7) — a mechanizmus helyes, a default profil engedékeny; önmagában **nem** sérülékenység, az S-01-gyel együtt viszont a dev futásban nincs visszatartó kontroll.
- **Javítási irány:** a nem-production ág is kapjon érdemi (pl. 300–600/60 s) limitet, vagy a teszt-igényt teszt-konfigurációval oldd meg env helyett.

### [S-03] [ALACSONY] [RÉSZBEN] Secret-baseline és ignore ellentmondás: a `.secrets.baseline` egyszerre gitignore-olt és verziókövetett — CWE-693 (defense in depth)

- **Hely:** `.gitignore:42-44` (`.secrets.baseline`, `.env`), `git status` → ` M .secrets.baseline`, `git ls-files | grep -F env` → a `.env` **nincs** trackelve (csak a `.env.example`-ek).
- **Mért változás:** a diffstat szerint 66 érintett sor (túlnyomórészt törlés); a vizsgált részben **7 eltávolított `Secret Keyword` bejegyzés** (a diffet `head -40`-ig olvastam, tehát a lista alsó korlát): 5 db a `tests/api/test_api_auth_middleware.py` és `tests/api/test_api_auth_verify_key.py` fájlokra — **amelyek nem léteznek** (`ls tests/api | grep -i auth` → csak `api_auth_support.py`) —, továbbá **2 db** a `tests/data/test_meteostat_provider_part1.py` és `tests/data/test_meteostat_provider_support.py` fájlokra, amelyek viszont léteznek.
- **Fontos pontosítás (korábbi tévesztés javítva):** az eltávolított bejegyzések **nem** kizárólag nem létező fájlokra vonatkoznak. A baseline-ból való törlés önmagában **nem rejt el** találatot (a kivétellistáról levétellel a detect-secrets inkább újra jelezni fog) — a kockázat a kontroll **konzisztenciájában** van: mivel a fájl ignore-olt, a baseline bármely módosítása **review-ban láthatatlan**, és a meteostat-tesztekhez tartozó 2 bejegyzés eltávolítása azt jelenti, hogy a `data` tesztekben lévő `Secret Keyword` minták (vélhetően teszt-kulcsok) review nélkül kikerültek a „known/approved” halmazból. Azt **nem** mértem meg, hogy ezek a sorok valódi secretet tartalmaznak-e (a tesztek tartalmát nem olvastam) → `RÉSZBEN`.
- **Elkülönítés:** `DEFENSE_IN_DEPTH`.
- **Cáfolatkísérlet:** „talán a baseline-ban valódi secret volt” → csak `filename`/`line_number`/`type` mezőket olvastam, `hashed_secret`-et nem; a worktree-beli `.env` (194 B, `-rw-rw-r--`) untracked és `.gitignore`-olt → **a jelenlegi tree-ben nincs commitolt secret** a `.env`-re.
- **Javítási irány:** vedd ki a `.secrets.baseline`-t a `.gitignore`-ból (a tracked baseline a normális minta), generálj új baseline-t a jelenlegi tree-re, és a különbséget review-zd; a `.env` maradjon ignore-olt + untracked.

**Nem adtam findingot** a következő, a futásban látott jelöltekre: `allow_credentials=True` CORS (nem wildcard origin mellett helyes konfig, és a projektben nincs credential, amit védeni kellene), `X-XSS-Protection: 1; mode=block` (elavult, modern böngészőkben no-op — nem káros), a `/docs` nyilvános volta (az S-01 következménye, nem önálló hiba).

---

## 6. Negatív eredmények (részleges, a futáskorlát miatt)

> Ezek **nem** „biztonságos” verdiktek: a sweep a lent felsorolt parancsokra korlátozódott, és a
> `01_MAP` §4.1/§8 szerint is maradnak vakfoltok (678 nested import, dinamikus `import_module`).

| Állítás | Parancs | Eredmény |
|---------|---------|----------|
| Nincs `eval/exec/os.system/subprocess/shell=True` futtatás a `src/`-ben | `rg -n '\b(eval\|exec\|os\.system\|subprocess\|shell=True\|pickle\.loads?\|yaml\.load\|tarfile\|zipfile\|extractall)\b' src/ --glob '*.py'` | csak Qt `app.exec()` / `dialog.exec()` UI-hívások (10 találat, mind PySide6 event loop) |
| Nincs kikapcsolt TLS-verifikáció | `rg -n 'verify\s*=\s*False' src/ frontend/src scripts/` | 0 találat |
| Nincs HTML-injektáló sink a frontendben | `rg -n 'dangerouslySetInnerHTML\|innerHTML\|document\.write\|new Function\|eval\(' frontend/src --glob '*.ts*'` | 0 találat |
| Nincs auth-szimbólum a `src/`-ben | `rg -n 'APIKeyHeader\|X-API-Key\|API_KEY\|verify_api_key\|auth_middleware' src/ --glob '*.py'` | 0 auth-találat; 7 `METEOSTAT_API_KEY` találat |
| A provider-kulcs nem kerül logba a vizsgált mintában | `rg -n 'logger\.\|logging\.' src/infrastructure/weather/meteostat_provider.py` | 5 log-hívás (év-batch/évek/„batch error” szövegek), **kulcs nem szerepel** bennük |
| Nincs `*`-origin production indulás | `src/api/main.py:33-38` (teljes olvasás) | `RuntimeError` marad → fail-fast aktív |
| Nincs `debug=True` a FastAPI appon | `src/api/main.py:52` | `FastAPI(title=..., lifespan=lifespan)` |

**Részleges route-szintű enumerálás:** a `Depends(` összes előfordulása nem lett végigolvasva — a fenti grep az auth-szimbólumokra teljes, de egy ismeretlen nevű auth-dependency elméletileg kimaradhatna. Ez `RÉSZLEGES`; a `src/api/main.py` és `src/config/api_config.py` teljes olvasása/diffje alapján a kulcs-alapú mechanizmus eltávolítása bizonyított.

---

## 7. Elvetett jelöltek (cáfolati napló)

| Jelölt | Cáfolat | Forrás |
|--------|---------|--------|
| `city_manager_db.py:219` f-string SQL (`SELECT COUNT(*) FROM {table}`, `# nosec B608`) | a `table` érték belső whitelistből (`_get_count_with`) jön, nem kérés-bemenetből; **nincs** source → sink út | átvéve: `02_LOGIC` §7 (nem saját mérés) |
| `city_repository_queries.py:235` `PRAGMA table_info({table_name})` | séma-név belső forrásból; a LIKE-ágak paraméterezettek (`params=[...]`), `like_utils.escape_like` a `%`/`_` metachereket kezeli | saját olvasás (`rg` + fájlrészletek) |
| CORS `allow_credentials=True` | `allow_origins` nem wildcard (env allowlist), productionben a `*` indulást a lifespan tiltja | saját olvasás: `src/api/main.py:33-38,70-77` |
| Rate limiter megkerülése XFF-fel | az XFF csak `TRUSTED_PROXIES` esetén számít | átvéve: `01_MAP` §7 |
| `/docs` és `/redoc` expozíciója | a HEAD-beli kód is csak nem-production módban tette elérhetővé; a worktree-ben viszont **minden** módban nyilvános → beolvasztva az S-01-be | saját diff-olvasás |
| SQLite írás a presentation rétegből (L-10) | biztonsági szempontból nincs kérés-vezérelt út hozzá (az API réteg nem ír DB-t) | átvéve: `02_LOGIC` §9 |
| `WEATHER_ANALYZER_DATA_DIR` futásidőben bővülő trusted-path lista (L-11) | a lista csak bővül, canonicalizálás + `relative_to` megmarad → nincs bizonyított traversal | átvéve: `02_LOGIC` L-11 |
| `requests.Session` megosztás több szálon (H2) | reprodukció nélkül hipotézis; nem security-finding | átvéve: `02_LOGIC` §6 |

---

## 8. Blokkolt ellenőrzések

| Ellenőrzés | Státusz | Ok |
|-----------|---------|-----|
| `pip-audit -r requirements.lock --no-deps --disable-pip -f json` (és `--path venv/.../site-packages`) | **`CVE-ELLENŐRZÉS BLOKKOLT`** | a futás a függőség-scan előtt zárult le; a hálózat egyébként is csak a sebezhetőségi DB lekérdezésére lehetett volna használható |
| `npm audit --offline` (`frontend/`, `tests/e2e/`) | **`CVE-ELLENŐRZÉS BLOKKOLT`** | ugyanaz |
| Git history secret-scan (teljes lokális history) | **`SZKEN BLOKKOLT`** | futáskorlát; a jelenlegi tree-re vonatkozó részleges mérés megvan (S-03) |
| `detect-secrets scan` / pre-commit futtatás | **BLOKKOLT** | nem read-only (baseline-t írna) |
| Teljes pytest-suite / CI-kapu ebben a futásban | **BLOKKOLT** | teszt- és coverage-artifactot ír; `01_MAP` §3.7 + `02_LOGIC` §5 mérései állnak rendelkezésre |
| Playwright e2e, GUI-futtatás, `frontend/src` page-komponensek XSS-sweepje | **BLOKKOLT / RÉSZLEGES** | élő stack + böngésző kell; futáskorlát |
| `src/scripts/*` (CSV/XLSX/SQL adatdumpok) tartalmi vizsgálata | **BLOKKOLT** | futáskorlát |

---

## 9. Prioritási lista

| # | ID | Severity | Státusz | Egy soros indok |
|---|----|----------|---------|-----------------|
| 1 | S-01 | MAGAS | MEGERŐSÍTETT | a hitelesítés és a production fail-fast eltűnt a worktree-ből; bármely lokális kliens (nem-loopback produkciós bind esetén bárki) korlátlanul égeti a fizetős provider-kvótát, és írhatja a preferencia-fájlokat |
| 2 | S-03 | ALACSONY | RÉSZBEN | a tracked `.secrets.baseline` ignore-olt → a baseline-változás review-ban láthatatlan; 2 meteostat-teszt bejegyzés indoklás nélkül került ki a „known” halmazból |
| 3 | S-02 | ALACSONY | MEGERŐSÍTETT | dev profilban 10 000/60 s a limit, miközben nincs hitelesítés → gyakorlatilag nulla visszatartó kontroll |
| 4 | — | — | BLOKKOLT | supply chain/CVE scan (pip-audit/npm audit) és a git-history secret-scan nem futott |

---

## 10. Parancsnapló

| Parancs | Mit bizonyít | Eredmény |
|---------|--------------|----------|
| `date -u`; `git rev-parse HEAD`; `git branch --show-current`; `git status --porcelain` | snapshot-egyezés | HEAD `c4793cdc…`, `main`; porcelain **azonos** a térkép §1.2-vel (+ `?? docs/`) |
| `git diff --stat` | worktree méret | 8 fájl, +3/−823 (egyezik a térképpel) |
| `git diff src/api/main.py` | auth-eltávolítás | `verify_api_key`, `auth_middleware`, `PUBLIC_PATHS`, `/auth/status`, production fail-fast, „auth disabled” warning **törölve** |
| `git diff src/config/api_config.py` | kulcs-config eltávolítás | `API_KEY`, `API_KEY_ENABLED` + a `_reload()` soraik törölve |
| `git diff .env.example` | secret-sablon tisztítás | 4 sor törölve (`API_KEY=` + generálási útmutató) |
| `git diff .secrets.baseline \| grep -E '^[-+].*"(filename\|type\|is_secret\|line_number)'` | baseline-tisztítás tartalma | 7 eltávolított `Secret Keyword` bejegyzés (5 nem létező auth-tesztfájlra, 2 létező meteostat-tesztfájlra) |
| `cat src/api/main.py` (teljes, 104 sor) | jelenlegi guard-készlet | nincs auth; CORS allowlist + `*` fail-fast; headerek; rate limit 60/10 000 |
| `rg -n 'APIKeyHeader\|X-API-Key\|API_KEY\|verify_api_key\|auth_middleware' src/ --glob '*.py'` | más auth-mechanizmus keresése | **0 auth-találat**; 7 `METEOSTAT_API_KEY` |
| `ls tests/api \| grep -i auth`; `rg -n 'from src.api.main\|import src.api.main\|verify_api_key\|auth_middleware' tests/` | teszt-oldali összefüggés | csak `api_auth_support.py` maradt (árva); a main-t importáló tesztek nem hivatkoznak auth-szimbólumra |
| `rg -n 'eval\|exec\|os.system\|subprocess\|shell=True\|pickle\|yaml.load\|tarfile\|zipfile\|extractall' src/` | veszélyes sinkek | csak Qt `.exec()` (10) |
| `rg -n 'verify\s*=\s*False' src/ frontend/src scripts/` | TLS-verifikáció | 0 |
| `rg -n 'execute\(f"\|\.format\(\|%\s*\(' src/infrastructure/{repositories,city_manager}/` | string-épített SQL | 2 hely (PRAGMA + whitelistelt COUNT), mindkettő cáfolva |
| `rg -n 'dangerouslySetInnerHTML\|innerHTML\|document.write\|new Function\|eval\(' frontend/src` | XSS-sinkek | 0 |
| `rg -n 'uvicorn\|--host\|0\.0\.0\.0\|127\.0\.0\.1' scripts/dev.sh scripts/launch_meteo_analytics_fullstack.sh README.md Makefile` | bind + kitettség | minden indítás `127.0.0.1` (README host nélkül = uvicorn default) |
| `git ls-files \| grep -F env`; `ls -la \| grep -i env`; `cat .gitignore` | secret-higiéné | `.env` **untracked** (csak `.env.example`-ek tracked), `194 B`, `-rw-rw-r--`; `.gitignore:42-44` fedi a `.env`-et |
| `rg -n 'logger\.\|logging\.' src/infrastructure/weather/meteostat_provider.py` | kulcs-logolás | 5 log-hívás, kulcs nem szerepel |

**Nem futott (szándékosan / korlát miatt):** exploit, telepítés, `quality_gate.sh`, pytest/vitest/build, `pip-audit`, `npm audit`, `detect-secrets`, Playwright, GUI-indítás. A `.env` **tartalmát nem olvastam és nem naplóztam** (titok-maszkolás); a `.secrets.baseline`-ból csak metaadat-mezőket idéztem.

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

Az egyetlen, e futás által létrehozott tétel: `docs/audit/20260910T092914Z/03_SECURITY.md` (a `docs/` már a térkép futásakor untracked lett). Termékkód, teszt, lock, séma és config **nem** módosult ebben a futásban; a worktree a futás előtti állapottal azonos.
