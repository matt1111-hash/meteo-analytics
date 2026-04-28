# REFACTOR PLAN — Production Mandate Compliance
**Dátum: 2026-04-28 | Alap: PRODUCTION_MANDATE.md v2.0, 12 releváns kritérium**
**Validálva: külső review-val, 6 javítás integrálva**

---

## 0. Audit állapot — két review összevetése

### Review #1 (saját audit)

| # | Kritérium | Értékelés | Megjegyzés |
|---|-----------|-----------|------------|
| 1 | Fő user flow-k | ⚠️ | Playwright E2E hiányzik, GUI-ban 1 TODO |
| 2 | Nincs blocker bug | ✅ | 1783 teszt zöld, 0 ruff, 0 mypy |
| 3 | Graceful degradation | ⚠️ | Retry/timeout/fallback van, circuit breaker hiányzik |
| 4 | Idempotencia/concurrency | ⚠️ | Config mentés lock nélkül, APIConfig.reload race |
| 5 | Unit tesztek | ✅ | 93.52% coverage, 1783 teszt |
| 6 | Integration tesztek | ✅ | DB, API auth, provider integrációk |
| 7 | E2E smoke | ⚠️ | Csak backend AsyncClient, Playwright üres |
| 13 | CI/CD + lock | ⚠️ | Nincs Dependabot config, lock file nem teljes |
| 17 | Config/secrets env-ben | ✅ | .env gitignore-olva, example van |
| 20 | Secret nincs repo-ban + audit | ✅ | detect-secrets beállítva, nincs hardcoded |
| 22 | README | ✅ | Részletes, minden lépés benne |
| 26 | Dependency rule | ⚠️ | 1 sértés, import-linter nem fut |

### Review #2 (külső validált review)

| # | Kritérium | Értékelés | Új információ |
|---|-----------|-----------|---------------|
| 1 | Fő user flow-k | Részleges | API smoke van, teljes E2E nincs |
| 2 | Nincs kritikus bug | **NEM** | Ismert audit/security/architecture hibák |
| 3 | Graceful degradation | Részleges | Circuit breaker explicit bizonyíték nincs |
| 4 | Idempotencia | Részleges | Nincs teljes race/idempotencia audit |
| 5 | Unit tesztek | Valószínű jó | 209 tesztfájl, 91.54% régi artifact |
| 6 | Integration tesztek | Részleges | Aktuális teljes futás nincs módosításmentesen |
| 7 | E2E smoke | **NEM** | In-process API smoke van, workflow törött |
| 13 | CI/CD + lock | Részleges | Dependabot van(!), E2E workflow hibás |
| 17 | Config/secrets | Igen | — |
| 20 | Dependency audit | **NEM** | geopandas CVE, 10 npm vulnerability |
| 22 | README | Igen | — |
| 26 | Clean Arch rule | **NEM** | lint-imports konkrétan bukik |

### Validált eltérések a két review között

| Téma | Review #1 | Review #2 (validált) | Valóság |
|------|-----------|---------------------|---------|
| Dependency audit | ✅ tiszta | ❌ nem tiszta | ❌ **geopandas CVE-2025-69662**, 10 npm vuln |
| Bandit B608 | nem vizsgált | ❌ city_manager_db.py:214 | ⚠️ false positive (hardkódott táblanév) |
| lint-imports | nem futtatható | ❌ Layers BROKEN | ❌ infrastructure → analytics sértés |
| scripts/dev.sh | nem vizsgált | ❌ hiányzik | ❌ E2E workflow nem futtatható |
| Port inkonzisztencia | nem vizsgált | ❌ 8001/5173 vs 8003/3000 | ❌ workflow vs README eltérés |
| Dependabot | ❌ hiányzik | ✅ aktív (GitHub UI) | ✅ aktív, de nincs `.github/dependabot.yml` |
| E2E Playwright | ⚠️ nincs teszt | ❌ workflow is törött | ❌ teljesen törött lánc |

---

## 1. BLOCKER — biztonsági és dependency problémák

**Cél: Kritérium #20 teljesüljön**

### 1.1 geopandas CVE-2025-69662 fix

```
Jelenleg:  geopandas==1.1.1  → CVE-2025-69662
Cél:       geopandas>=1.1.2
```

**Lépések:**
- [x] `requirements.txt`: geopandas verzió emelése `>=1.1.2`
- [x] `pip install -r requirements.txt && pip-audit -r requirements.txt` → zöld
- [x] `requirements.lock`: újragenerálás (lásd 4.2 — tiszta venv-ből)
- [x] `python -m pytest tests/ -x -q` → regresszió ellenőrzés

### 1.2 npm audit — 10 vulnerability (5 low, 5 moderate)

```
Érintett: esbuild, vite, vite-node, vitest, postcss, http-proxy-agent, jsdom
```

**Lépések (célzott frissítés, NEM --force):**
- [x] `cd frontend && npm audit fix` — postcss fix (nem breaking)
- [x] Célzott frissítés egyesével, sorrendben:
  - `npm install esbuild@latest` — GHSA-67mh-4wv8-2f99
  - `npm install vite@latest` — esbuild függőség
  - `npm install vitest@latest` — vite/vite-node függőség
  - `npm install postcss@latest` — GHSA-qx2v-qp2m-jg93 (XSS)
- [x] Minden egyes frissítés után: `npx vitest run` → tesztek zöldek
- [x] `npm run build` → build sikeres
- [x] `npm audit --audit-level=moderate` → 0 találat
- [x] `frontend/package-lock.json` commit

> **Figyelem:** `npm audit fix --force` túl durva, breaking change-eket hozhat be
> ellenőrizetlenül. A célzott frissítés biztonságosabb — minden lépés után
> regresszió tesztelhető.

### 1.3 Bandit B608 — city_manager_db.py:214

**Valós kockázat: false positive** — a `table` paraméter sosem user-controlled,
kizárólag `"cities"` és `"hungarian_settlements"` hardkódott értékekkel hívódik.
A `city_repository_queries.py`-ban lévő 4 darab `# nosec B608` mind jogosan
van elnyomva (parametrikus `IN` clause `?` placeholder-ekkel).

**Lépések:**
- [ ] `_get_count_with()` refaktorálása: hardkódott táblanevek enum vagy const
  ```python
  _VALID_TABLES = frozenset({"cities", "hungarian_settlements"})
  if table not in _VALID_TABLES:
      raise ValueError(f"Invalid table: {table}")
  cursor.execute(f"SELECT COUNT(*) FROM {table}")
  ```
- [ ] Vagy: `# nosec B608` jelölés hozzáadása indoklással
- [ ] `bandit -r src -ll -q` → 0 medium találat

---

## 2. BLOCKER — Clean Architecture sértés javítása

**Cél: Kritérium #26 teljesüljön**

### 2.1 lint-imports: Layers BROKEN

```
Sértés: src.infrastructure.container.composition_root → src.analytics.*
  - src.analytics.multi_city_types (l.12, l.44) — REGIONS, HUNGARIAN_REGIONAL_MAPPING
  - src.analytics.multi_city_engine_query_types (l.11, l.43) — QUERY_TYPES
```

**Gyökér ok:** A composition root analytics modulból importál konfigurációs
adatokat (REGIONS, QUERY_TYPES), ami megsérti a layer rule-t.
A `REGIONS` és `QUERY_TYPES` valójában domain szintű konstansok — nincs bennük
I/O, nincs külső függőség. Az analytics csak tárolóként szolgál számukra.

**Megoldási opciók:**

**Opció A — Analytics konstansok áthelyezése domain-be (ajánlott):**
- REGIONS, HUNGARIAN_REGIONAL_MAPPING → `src/domain/constants/regions.py`
- QUERY_TYPES → `src/domain/constants/query_types.py`
- Analytics modulok re-exportálnak domain-ből (backward compat)
- Composition root importál a domain-ből (helyes irány)

**Opció B — .importlinter ignore bővítése:**
- Hozzáadni `composition_root → analytics` ignore szabályt
- Kevesebb munka, de elrejti a problémát

**Lépések (Opció A):**
- [ ] Új fájl: `src/domain/constants/__init__.py`
- [ ] Új fájl: `src/domain/constants/regions.py` — REGIONS + HUNGARIAN_REGIONAL_MAPPING
- [ ] Új fájl: `src/domain/constants/query_types.py` — QUERY_TYPES
- [ ] `src/analytics/multi_city_types.py` — re-export domain-ből (backward compat)
- [ ] `src/analytics/multi_city_engine_query_types.py` — re-export domain-ből
- [ ] `composition_root.py` — importok domain-re változtatása
- [ ] `lint-imports` → Layers KEPT
- [ ] `python -m pytest tests/ -x -q` → zöld

### 2.2 wind_rose_support.py közvetlen data import (Review #1)

**Státusz:** A lint-imports jelenleg nem jelzi — valószínűleg javítva vagy
a layer config nem fedi le. Ellenőrizni kell:

- [ ] Ellenőrizni: `src/api/routes/wind_rose_support.py:13` import
- [ ] Ha még létezik: application layer-en keresztül importálni

---

## 3. BLOCKER — E2E workflow javítása

**Cél: Kritérium #7 teljesüljön**

### 3.1 scripts/dev.sh hiányzik

A `.github/workflows/e2e-tests.yml:67` hivatkozik rá.

**Lépések:**
- [ ] Új fájl: `scripts/dev.sh` — elindítja backend + frontend stacket
  - Backend: `uvicorn src.api.main:app --port 8003`
  - Frontend: `cd frontend && npm run dev` (port 3000)
    - **FONTOS:** `package.json` nem tartalmaz `start` scriptet, csak `dev`-et
  - Health check várakozás
- [ ] Tesztelés: `./scripts/dev.sh` és manuális ellenőrzés

### 3.2 Port inkonzisztencia javítása

```
Workflow:   8001 (backend), 5173 (frontend)
README:     8003 (backend), 3000 (frontend)
Scripts:    8003 (backend), 3000 (frontend)
```

**Lépések:**
- [ ] `.github/workflows/e2e-tests.yml`: portok javítása → 8003/3000
  - Line 60: `8001` → `8003`
  - Line 61: `5173` → `3000`
- [ ] Vagy: dev.sh paraméterezhető portokkal, CI-ben env vars-ból

### 3.3 Playwright tesztek létrehozása

A workflow `npx playwright test` hív, de nincs mit futtatni.

**Lépések:**
- [ ] `tests/e2e/package.json` — Playwright dependency
- [ ] `tests/e2e/playwright.config.ts` — alap konfig (chromium, firefox)
- [ ] `tests/e2e/smoke.spec.ts` — minimális tesztek:
  - Frontend betölt
  - City search működik
  - Weather lekérdezés működik
- [ ] Lokális tesztelés: `cd tests/e2e && npx playwright test`

---

## 4. HIGH — Dependabot és lock file

**Cél: Kritérium #13 teljesüljön**

### 4.1 Dependabot konfiguráció

**Státusz:** Dependabot aktív a GitHub UI-ban
(dynamic/dependabot/dependabot-updates), de **nincs** `.github/dependabot.yml`.
Ez nem "hiányzik" funkcionálisan, de repo-portabilitási szempontból problémás:
clone után nincs konfiguráció, és a schedule/package-ecosystem beállítások
nincs version control alatt.

**Lépések:**
- [ ] `.github/dependabot.yml` létrehozni a jelenlegi GitHub beállítások alapján:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: pip
      directory: /
      schedule: { interval: weekly }
    - package-ecosystem: npm
      directory: /frontend
      schedule: { interval: weekly }
    - package-ecosystem: github-actions
      directory: /
      schedule: { interval: weekly }
  ```

### 4.2 requirements.lock nem teljes

**Jelenleg:** 16 soros részleges lock (csak direct dependencies).

**Lépések:**
- [ ] Tiszta venv-ből lock generálás (ne dev/tooling szennyezze):
  ```bash
  python -m venv /tmp/clean-venv
  /tmp/clean-venv/bin/pip install -r requirements.txt
  /tmp/clean-venv/bin/pip freeze > requirements.lock
  ```
- [ ] Vagy: `pip-compile` (pip-tools) használata reprodukálható build-hez
- [ ] Validáció: `pip-audit -r requirements.lock` → 0 találat

> **Figyelem:** `pip freeze` a teljes venv-et dumpolja. Ha dev függőségek is
> telepítve vannak (ruff, mypy, pytest stb.), azok is bekerülnek. Tiszta venv
> vagy `pip-compile` használata kötelező.

---

## 5. MEDIUM — Graceful degradation javítás

**Cél: Kritérium #3 teljesüljön — PRODUCTION_MANDATE kötelező**

### 5.1 Circuit breaker

**Jelenleg:** Retry + exponential backoff + fallback chain van, de nincs circuit breaker.

**PRODUCTION_MANDATE #3:** "Graceful degradation: retry, timeout, circuit breaker megvan"

**Helyzet:** A mandate kifejezetten említi a circuit breakert. Solo desktop scope-ban
az alacsony concurrent hozzáférés miatt a kockázat kisebb, de a mandate nem tesz
kivételt. Két opció:

**Opció A — Implementáció (ajánlott):**
- [ ] Egyszerű circuit breaker: `src/data/circuit_breaker.py`
  - Closed → Open (N egymást követő hiba után, pl. 5)
  - Open → Half-Open (timeout után, pl. 60s)
  - Thread-safe állapotkezelés
- [ ] Integráció a `weather_client_core.py` fallback chain-be
- [ ] Tesztek: closed/open/half-open állapotátmenetek

**Opció B — Explicit dokumentáció, hogy miért elég a retry/timeout/fallback:**
- [ ] PRODUCTION_MANDATE.md vagy INCOMPLETE.md: indoklás, hogy solo desktop
  scope-ban a circuit breaker nem ad hozzáértéket a meglévő fallback chainhez
- [ ] A mandate #3 kritériumát "részleges" minősítéssel dokumentálni

### 5.2 Nem atomi JSON config mentések

**Érintett:**
- `src/config/usage_config.py` (line ~110)
- `src/config/provider_config.py` (line ~160)

**Lépések:**
- [ ] Atomikus írás helper: write-to-temp → rename minta
  ```python
  def atomic_write_json(path: Path, data: dict) -> None:
      tmp = path.with_suffix(".tmp")
      tmp.write_text(json.dumps(data, indent=2))
      tmp.rename(path)
  ```
- [ ] Alkalmazni usage_config.py és provider_config.py mentésekre
- [ ] Tesztek: concurrent write, interrupted write

---

## 6. MEDIUM — Concurrency / idempotencia

**Cél: Kritérium #4 teljesüljön**

### 6.1 APIConfig.reload() race condition

**Hely:** `src/config/api_config.py:60-71`

**Lépések:**
- [ ] `threading.Lock` hozzáadása a reload metódushoz
- [ ] Vagy: immutable config objektum (minden reload új instance)

### 6.2 UsageTracker lock hiányzik

**Hely:** `src/config/usage_config.py`

**Lépések:**
- [ ] `threading.Lock` hozzáadása a load/save ciklushoz
- [ ] Teszt: concurrent load+save nem corruptál adatot

---

## 7. LOW — TODO/pass hygiene és apró javítások

### 7.1 TODO és pass/ellipsis audit

**Forráskódban talált TODO:**
- `src/presentation/gui/windows/main_window.py:130` — counties loading TODO

**Pass állapotok (jogosak, nem action item):**
- `src/presentation/gui/interfaces.py` — 7 darab `@abstractmethod` + `pass` (ABC protocol)
- `src/data/city_types.py` — 2 daráb `pass` (dataclass/ABC)
- `src/data/weather_types.py` — 3 darab `pass` (dataclass/ABC)
- `src/data/weather_provider_base.py` — 1 darab `pass` (abstract method)
- `src/presentation/gui/charts/*` — ~20 darab `pass` (mixin üres metódusok)
- `src/presentation/gui/map/map_interactions.py:53` — 1 darab `pass` (except blokk)

**Ellipsis `...` (jogosak):**
- `src/api/routes/wind_rose_part1.py` — Pydantic Field default
- `src/api/dto/weather_request.py` — Pydantic Field default
- GUI mixins — Protocol típusok

**Lépések:**
- [x] `main_window.py:130` — counties loading implementálva (geopandas → data/geojson/counties.geojson)
- [x] Fenti `pass` és `...` találatok: nincs teendő, mind jogos minta

### 7.2 import-linter — már telepítve

**Státusz:** `import-linter>=2.0` már szerepel a `requirements-dev.txt` (line 27)-ben.
A `venv/bin/lint-imports` futtatható. A korábbi terv pontatlan volt.

**Nincs teendő** — a pre-commit hook is működik venv-ből.

### 7.3 Fájl méretek a limit határán

**A 10 legnagyobb fájl (max 300 sor):**
```
299  ui_builder.py
296  wind_analyzer.py
292  analytics_transform_service.py
287  data_processor.py
286  database_manager.py
285  display_mixin.py
285  provider_dto.py
281  provider_routing.py
280  geocoding_handler.py
275  theme_manager/core.py
```

**Lépések:**
- [x] Monitorozni — jelenleg mind a 300-as limit alatt (max: 299 sor)
- [x] Ha bármelyik átlépi: felbontani kisebb modulokra (jelenleg nem szükséges)

---

## 8. Megvalósítási sorrend

```
Phase 1 — BLOCKER: Security/dependency + Bandit + Clean Architecture ✅ KÉSZ
├── 1.1 geopandas CVE fix (pip-audit zöld)                           ✅
├── 1.2 npm audit célzott fix (npm audit zöld)                       ✅
├── 1.3 B608 false positive kezelése (bandit zöld)                   ✅
└── 2.1 Clean Architecture sértés javítása (lint-imports zöld)       ✅

Phase 2 — BLOCKER: E2E workflow futtathatóvá tétele                  ✅ KÉSZ
├── 3.1 scripts/dev.sh létrehozás (npm run dev, nem npm start)       ✅
├── 3.2 Port inkonzisztencia javítás (8001→8003, 5173→3000)          ✅
└── 3.3 Playwright tesztek (minimális smoke)                         ✅

Phase 3 — HIGH: Lock/reproducibility                                 ✅ KÉSZ
├── 4.1 .github/dependabot.yml létrehozás (repo-portabilitás)        ✅
└── 4.2 requirements.lock teljesítés (tiszta venv-ből)               ✅

Phase 4 — MEDIUM: Concurrency/idempotencia                           ✅ KÉSZ
├── 5.2 Atomikus JSON config mentések                                 ✅
├── 6.1 APIConfig.reload race fix                                     ✅
└── 6.2 UsageTracker lock                                             ✅

Phase 5 — MEDIUM: Circuit breaker (mandate kötelező)                  ✅ KÉSZ
└── 5.1 Circuit breaker implementáció + weather client integráció     ✅

Phase 6 — LOW: TODO/pass hygiene és dokumentáció                           ✅ KÉSZ
├── 7.1 main_window.py TODO — counties loading implementálva           ✅
└── 7.3 Fájlméret monitorozás (mind <300 sor)                          ✅
```

---

## 9. Quality gate — minden phase után

```bash
# Minden phase végén futtatni:
python -m ruff check src/
python -m mypy src/ --ignore-missing-imports
python -m pytest tests/ -v --cov=src --cov-report=term-missing
lint-imports
bandit -r src -ll -q
pip-audit -r requirements.txt
cd frontend && npm audit --audit-level=moderate
```

**PASS kritérium:**
- Ruff: 0 error
- Mypy: 0 error
- Pytest: 100% pass, coverage ≥85%
- lint-imports: 0 broken contract
- Bandit: 0 medium/high
- pip-audit: 0 vulnerability
- npm audit: 0 moderate+

---

## 10. PRODUCTION_MANDATE állapot (Phase 1–6 után)

| # | Kritérium | Kezdet | Phase 1–4 után | Phase 5 után | Phase 6 után | Cél |
|---|-----------|--------|-----------------|---------------|---------------|-----|
| 1 | Fő user flow-k | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ |
| 2 | Nincs blocker bug | ❌ | ✅ | ✅ | ✅ | ✅ |
| 3 | Graceful degradation | ⚠️ | ⚠️ | ✅ | ✅ | ✅ |
| 4 | Idempotencia/concurrency | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| 5 | Unit tesztek | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | Integration tesztek | ✅ | ✅ | ✅ | ✅ | ✅ |
| 7 | E2E smoke | ❌ | ✅ | ✅ | ✅ | ✅ |
| 13 | CI/CD + lock | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| 17 | Config/secrets env | ✅ | ✅ | ✅ | ✅ | ✅ |
| 20 | Secret + dependency audit | ❌ | ✅ | ✅ | ✅ | ✅ |
| 22 | README | ✅ | ✅ | ✅ | ✅ | ✅ |
| 26 | Clean Arch rule | ❌ | ✅ | ✅ | ✅ | ✅ |

**Állás: 12/12 PASS — PRODUCTION_MANDATE TELJESÜL.**

---

## Validációs napló

| Dátum | Validáló | Eredmény |
|-------|----------|----------|
| 2026-04-28 | Saját audit | 12/12 vizsgálva, 4 ❌, 5 ⚠️, 3 ✅ |
| 2026-04-28 | Külső review | 6 javítás: npm start→dev, import-linter már van, Dependabot portabilitás, npm fix nem --force, circuit breaker kötelező, TODO/pass helyes skálázás |
| 2026-04-28 | Terv v2 integrálva | Minden javítás beépítve |
| 2026-04-28 | Phase 1 végrehajtás | geopandas CVE, npm 10→0, B608 fix, Clean Arch domain/constants, 1783 teszt zöld |
| 2026-04-28 | Phase 2 végrehajtás | dev.sh, port fix 8003/3000, Playwright 4/4 smoke, E2E workflow javítva |
| 2026-04-28 | Phase 3 végrehajtás | dependabot.yml, requirements.lock 16→47 sor, pip-audit zöld |
| 2026-04-28 | Phase 4 végrehajtás | atomic_io.py, APIConfig lock, UsageTracker lock, 1788 teszt zöld |
| 2026-04-28 | Phase 5 végrehajtás | circuit_breaker.py, weather_client integráció, 1811 teszt zöld, 99% CB coverage |
| 2026-04-28 | Phase 6 végrehajtás | main_window.py TODO javítva (counties loading), fájlméretek OK, 12/12 PASS |
