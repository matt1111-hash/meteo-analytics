# AGENTS.md — Universal Edition
**Version: 3.3 (2026-06-27) | Scope: minden repo | Lang: magyar**

> Stack-független szerződés az ember és az agent között. A magyar nyelvű
> természetes kommunikáció a fő interfész, nem a prompt engineering.
>
> **Hivatkozott fájlok:**
> - `GIT_WORKFLOW.md` — solo dev git szabályok
> - `PRODUCTION_MANDATE.md` — release döntés 26 kritériuma
> - `HANDOFF.md` — záró riport sablon (6 szekció, magyar)
>
> **Stack-specifikus parancsok:** lásd a [Stack Adapterek](#-stack-adapterek) szekciót.

---

## 🔴 HIERARCHIA — LEGFONTOSABB

| Szerep | Felelősség |
|--------|------------|
| **EMBER** | Megrendelő, döntéshozó. Magyarul beszél természetes szándékkal. |
| **AGENT** | Végrehajtó. Kódol, debuggol, ellenőriz, riportol. |

**AGENT KÖTELESSÉGEI:**
- Az EMBER **NEM DEBUGOL** — az agent dolga
- Az EMBER **NEM BÖNGÉSZIK** — kódelemzés az agent feladata
- Az EMBER **NEM CSELÉD** — ne kérj tőle futtatást amit te is tudsz
- Az EMBER **MAGYARUL** beszél természetes szándékkal — az agent fordítja le művelettervvé (lásd SZKEA módszer alább)

**AGENT TILOS:**
- Vezérelni az embert ("Act as a senior architect..." stílus tilos VICE VERSA is)
- Felesleges kérdezgetni (max 2 kérdés, csak ha tényleg blokkoló)
- "Lehetne refaktorálni" típusú scope expansion proaktívan

---

## 🚨 CRITICAL RULES (univerzális)

### ❌ TILOS

- **Találgatás** — ha valami nem világos, kérdezz (max 2 kérdés)
- **Befejezetlen kód** — vagy fejezd be, vagy `INCOMPLETE.md`-be dokumentáld
- **Placeholder kommentek** — `# TODO`, `// FIXME`, `pass`, `throw new Error("not implemented")`
- **Csonkolás** — SOHA `...`, `// rest unchanged`, `# existing code here`
- **Unsafe code** — `eval`, `exec`, `os.system`, shell injection, SQL string formatting
- **Tesztek gyengítése vagy törlése** — coverage vagy zöld státusz érdekében tilos. Viselkedésváltozásnál teszt frissítése kötelező is lehet, de az explicit, indokolt, és dokumentált.
- **Config manipuláció gate kikerülésére** — `.quality_gate.conf`, `pyproject.toml`, `package.json` quality szekciói nem módosíthatók a gate teljesítése érdekében
- **Scope creep** — csak a kért dolgot csináld, ne többet
- **Path guessing** — ha nem tudod biztosan, kérdezd meg, NE fabrikálj parancsokat
- **Vague reporting** — "looks fine", "probably OK", "should work" → tilos

### ✅ KÖTELEZŐ

- **Teljes, nem placeholder módosítás** — agent CLI-ben patch/diff normális; teljes fájl csak ha az ember kéri vagy új fájl. Chatben ne paszolj 500 soros fájlt ha 3 sort módosítottál.
- **Type hints / TypeScript types** — új vagy módosított publikus/nem triviális függvényeknél kötelező; meglévő vegyes stílusú kódbázisban ne legyen tömeges retrofit csak emiatt
- **Tesztek** — MANDATORY (ha a stack támogatja)
- **Repo struktúra követése** — kövesd a meglévő architektúrát. Clean Architecture (domain / application / infrastructure / presentation) kötelező ott, ahol a repo már ezt követi, vagy ahol nem triviális domain logika van. Vite játék, script, benchmark → ne erőltesd.
- **Fájlméret cél** — új fájl: ≤300 sor (CI: 250). Meglévő nagy fájl: célzott módosítás, nem kötelező egyből szétdarabolni.
- **Git status check** — minden új mappa után, session végén
- **HANDOFF.md formátum** a feladat végén
- **PRODUCTION_MANDATE.md ellenőrzőlista** production/release döntésnél, illetve ha az ember kifejezetten készültséget kér
- **Magyar nyelv** minden válaszban (kivéve kód és parancsok)

---

## 🗣️ KOMMUNIKÁCIÓ — SZKEA módszer

Az ember magyarul beszél, természetes szándékkal. Az agent ebből vezet le műveleti tervet a következő négy szempont mentén:

```
SZÁNDÉK → KORLÁT → ELLENŐRZÉS → ÁTADÁS
   S         Z          E           A
```

### 1. SZÁNDÉK (mit akar az ember?)

Példa magyar utasítások és az agent értelmezése:

| Magyar utasítás | Értelmezett szándék |
|-----------------|---------------------|
| "Nézd át ezt a repót minőségellenőrzési szempontból." | **Audit, read-only**, riport HANDOFF formátumban |
| "Keresd meg a hiba gyökerét." | **Root cause analysis**, nem tüneti javítás |
| "Egyszerűsítsd le ezt a részt." | **Refactor**, kisebb biztonságosabb megoldás |
| "Production szempontból vállalható-e?" | **PRODUCTION_MANDATE.md 26 kritérium** ellenőrzése |
| "Mi a baja?" | **Diagnosis**, ne javítson semmit |
| "Javítsd ki." | **Fix**, legkisebb biztonságos módosítás |
| "Tedd rendbe a worktree-t." | **Clean up dirty git state**, nem új feature |

### 2. KORLÁT (mihez NE nyúljon?)

Az ember explicit korlátokat ad. Az agent ezeket szigorúan tartja:

| Magyar korlát | Konkrét értelmezés |
|--------------|---------------------|
| "Ne írj át architektúrát." | Nincs új réteg, nincs új absztrakció |
| "Ne vezess be új dependency-t." | `package.json`, `pyproject.toml`, `pom.xml` változatlan |
| "Ne módosíts production configot." | `.env`, `config/prod.*` nem nyúl |
| "Ne commitolj." | Csak munkamódosítás, git művelet nem |
| "Csak elemezz." | Read-only mód, kód módosítás tilos |
| "Csak ezt az egy fájlt." | Diff csak a megnevezett fájlra korlátozódik |

### 3. ELLENŐRZÉS (hogyan bizonyítja az agent?)

Bizonyítani konkrét parancsokkal és konkrét output-tal kell:

- `pwd` és `git status` mindig
- Stack adapter szerinti quality gate (lásd lent)
- Explicit "nem futott" lista, indokkal
- Tilos: "tests are passing" → helyette pontos pytest/vitest/bun test output
- Tilos: feltételezni hogy egy parancs lefutott — futtasd és olvasd az output-ot

### 4. ÁTADÁS (mit ad vissza?)

**HANDOFF.md formátum**, 6 szekció, magyar nyelven:

1. Mit értettem
2. Mit találtam
3. Mit módosítottam
4. Ellenőrzés (lefuttatva / nem futott)
5. Kockázatok
6. Következő biztonságos lépés

Részletes formátum: `HANDOFF.md`.

### Tilos prompt stílusok

| ❌ Tilos | ✅ Helyette |
|----------|-------------|
| "Act as a senior DevOps architect performing a comprehensive CI/CD readiness assessment using a multi-stage validation rubric..." | "Nézd át a repót production szempontból." |
| "You are an expert Python engineer specialized in clean architecture..." | "Tedd rendbe a domain réteget." |
| "Ultra think about the optimal solution..." | "Mi a legkisebb biztonságos javítás?" |
| Túlterhelt mérnöki nyelv | Emberi magyar |
| Angol parancs magyar kontextusban | Magyar utasítás, az agent fordít műveletre |

**Az ember nem prompt engineer.** Az agent dolga megérteni az emberi szándékot.

---

## 🏗️ CLEAN ARCHITECTURE — ahol indokolt

Nem triviális domain logikát tartalmazó repóknál a dependency csak **BEFELÉ** mutathat.

```
┌─────────────────────────────────────────┐
│  presentation (CLI, GUI, HTTP, TUI)     │  ← legkülső
├─────────────────────────────────────────┤
│  infrastructure (DB, API, FS, cache)    │
├─────────────────────────────────────────┤
│  application (use cases, services)      │
├─────────────────────────────────────────┤
│  domain (entities, business rules)      │  ← legbelső, framework-agnosztikus
└─────────────────────────────────────────┘
        ↑ függőség iránya befelé
```

**Szabályok (ahol a repo ezt a struktúrát követi):**
- `domain` **soha** nem importál `infrastructure`-t vagy `presentation`-t
- `application` csak `domain`-t és **portokat** (interfészeket) lát
- ORM model ≠ domain entity (ne szivárogtass DB típust befelé)
- HTTP típusok (Request/Response) nem mennek `use case`-be
- Egy fájl = egy felelősség

**Mikor NEM kell:**
- Egyszerű script, benchmark, tool (`terms_bench`, `highlight`)
- Vite játék / demo (`blackjack`)
- Konfigurációs repó, dokumentáció
- Ha a repó meglévő struktúrája más és működik → kövesd azt

---

## 📊 CODE QUALITY CÉLÉRTÉKEK

Célértékek **új kódra**. Meglévő nagy fájlnál célzott módosítás OK, nem kell egyből refaktorálni.

| Metrika | Cél (új kód) | CI strict |
|---------|-------------|-----------|
| Sorok / függvény | ≤50 | ≤40 |
| Sorok / osztály | ≤200 | ≤200 |
| Sorok / fájl | ≤300 | ≤250 |
| Ciklomatikus komplexitás | <8 | <6 |
| Nesting depth | ≤3 | ≤3 |

A stack-specifikus tooling (Ruff, ESLint, Checkstyle) ezeket méri.

---

## 🔒 SECURITY (univerzális)

### Secret-ek
- ✅ Environment változókban
- ✅ `.env.example` a repóban, `.env` NEM
- ❌ SOHA hardcoded API kulcs, jelszó, token
- ❌ SOHA commitolva (gitleaks pre-commit hook, lásd GIT_WORKFLOW.md)

### Input validáció
- Külső input → validálj a presentation rétegben
- SQL → parametrizált queries (NEVER string formatting)
- Shell → sosem `eval`, `exec`, `os.system`, `child_process.exec` shell mode-ban

### SQL — univerzális minta

```python
# ✅ HELYES (Python parametrizált)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

```typescript
// ✅ HELYES (TypeScript parametrizált)
db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

```sql
-- ❌ TILOS (string formatting bármilyen nyelven)
"SELECT * FROM users WHERE id = " + userId
```

---

## 🧪 TESTING (univerzális)

- **Tesztek MANDATORY**, ha a stack támogatja
- **One test = one behavior**
- **Arrange-Act-Assert** pattern
- **Test file mirrors source**: `src/domain/foo.py` → `tests/domain/test_foo.py`
- **Tesztek gyengítése tilos** — coverage csökkentése, assertion eltávolítása, skip bevezetése zöldítés miatt tilos. Viselkedésváltozásnál teszt frissítése kötelező is lehet, de az explicit és indokolt.
- **Coverage target**: ≥85% local, ≥95% CI (stack adapter szerint)

---

## 📋 UNIVERZÁLIS WORKFLOW

### Session start

```bash
pwd                          # hol vagyok
git status                   # mi a worktree állapot
ls -la                       # mit látok
cat AGENTS.md                # szerződés (ez a fájl)
cat PRODUCTION_MANDATE.md    # release döntés
cat learnings.md 2>/dev/null || true   # korábbi session-ök tanulságai
```

### Munkafolyamat

1. **SZKEA**: Szándék → Korlát megértése magyar kérésből
2. **Repo intake**: mi van itt? milyen stack? milyen quality gate?
3. **Legkisebb biztonságos módosítás** (NEM "comprehensive refactor")
4. **Quality gate** — stack adapter szerint, ZÖLD KELL
5. **Git status check** → tiszta-e?
6. **HANDOFF.md formátum** szerint riport magyarul

### Befejezés előtt

```bash
git status                    # tiszta-e?
# Stack adapter quality gate (lásd lent)
git log --oneline -3          # mit csináltam
```

**Ha nem szándékos vagy nem dokumentált módosítás maradt a worktree-ben → NEM KÉSZ.**
Szándékos dirty (a feladat eredménye) elfogadható, ha a HANDOFF pontosan listázza a módosított fájlokat. Az ember commitol (lásd GIT_WORKFLOW.md).

### Session Close — learnings.md frissítés (KÖTELEZŐ):
A session NINCS LEZÁRVA amíg a `learnings.md` nincs frissítve. Agent-váltás / kontextusváltás ELŐTT mindig elvégzed ezt (különben az a session elveszik). Két lépés:

**1. Felülírod az `## AKTUÁLIS ÁLLAPOT` blokkot** (a fájl teteje — EZ a folytatási pointer a következő agentnek):
- **Aktív feladat:** mi fut most
- **Hol tartok most:** folytatási pont + érintett fájlok
- **Következő lépés:** pontosan mit csináljon a következő agent
- **Nyitott kérdések / fenntartások:** mire figyeljen
- **Blokkoló:** van-e ami megakasztja
- **Utolsó frissítés:** dátum | agent: profil

**2. Hozzáfűzöl egy bejegyzést az `## NAPLÓ` szekcióhoz** (történet, append a végéhez):
```markdown
### YYYY-MM-DD — [egy soros összefoglaló]
- **Feladat:** mi volt a cél
- **Eredmény:** mi készült el
- **Tanulság:** mi működött, mi nem, mit ne próbálj újra
- **Döntés:** milyen architekturális/technikai döntés született
```

Ha a `learnings.md` nem létezik, hozd létre a sablonnal (`AKTUÁLIS ÁLLAPOT` + `NAPLÓ` blokkok).
Ez NEM opcionális — kontextusváltás előtt KÖTELEZŐ.

### 🔍 PROJEKT INTEGRITÁS — AGENT FELELŐSSÉGE

- Az agent **MINDIG** végigköveti minden hívási láncot:
  presentation → application → domain → infrastructure
- **Tünet alapú debuggolás TILOS** — a gyökér okot kell megtalálni
- Az agent **MAGA** fedezi fel az architektúra inkonzisztenciákat (párhuzamos singletonok, dupla factory, stb.)
- Hibakeresés: **először a teljes dependency graph-ot** térképezi fel, AZTÁN javasol megoldást
- Az **EMBER SOHA nem mutat rá a hibára** — ez az agent dolga

---

## 📦 STACK ADAPTEREK

A fő szabályok mindenhol egyformák. Csak a parancskészlet más.

### 🐍 Python (Ruff + Pytest + Mypy)

**Detektálás:** `pyproject.toml` vagy `setup.py` / `requirements.txt` + `src/`, `app/`, vagy `lib/` mappa Python fájlokkal.

**Toolchain (2026 modern):**

Read-only validáció (audit, diagnózis):
```bash
python -m ruff check src/              # lint ellenőrzés
python -m ruff format --check src/     # format ellenőrzés (NEM formáz)
python -m mypy src/ --ignore-missing-imports
python -m pytest tests/ -v --cov=src --cov-branch \
    --cov-report=term-missing --cov-fail-under=85
./quality_gate.sh --help               # előbb ellenőrizd a módokat
# ./quality_gate.sh --full csak akkor, ha a --help vagy a script tartalma
# alapján bizonyítottan read-only; különben nem futtatod auditban
```

Módosító javítás (csak explicit fix feladatnál):
```bash
python -m ruff check --fix src/        # autofix
python -m ruff format src/             # formázás
./quality_gate.sh --quick              # FIGYELEM: ez autofix-elhet!
```

**Küszöbök:**

| Metrika | Local | CI |
|---------|-------|-----|
| Coverage | ≥85% | ≥95% |
| Max LOC/file | 300 | 250 |
| Ruff errors | 0 | 0 |
| Mypy | Warning | Strict |

**Clean Architecture struktúra** (ahol a repó ezt követi — nem minden Python projekt):

```
src/
├── domain/          # Entities, repository interfaces (no I/O!)
├── application/     # Use cases, services
├── infrastructure/  # SQLite, APIs, external services
└── presentation/    # CLI, GUI (PySide6 / CustomTkinter), HTTP (FastAPI)

tests/
└── test_*.py        # Tükrözi a src/ struktúrát
```

Egyszerű scriptek, benchmarkok → flat struktúra rendben van.

**Import sorrend:** stdlib → third-party → internal, alfabetikus.

---

### 🍞 Bun / TypeScript (dexter típusú projektek)

**Detektálás:** `bun.lockb` vagy `package.json` `bun run` scriptekkel.

**Read-only validáció:**

```bash
# Type check
bun run typecheck            # = tsc --noEmit

# Tests (Bun beépített)
bun test
bun test path/to/test.test.ts

# Lint (opcionális, ha biome / eslint van)
bun run lint
```

**Indítás (csak ha az ember kéri, vagy a feladat kifejezetten futtatást igényel):**

```bash
bun run start
bun run dev
```

**Küszöbök:**

| Metrika | Local | CI |
|---------|-------|-----|
| TS errors | 0 | 0 |
| Test failures | 0 | 0 |
| Lint warnings | warn | 0 |

**Struktúra (dexter példa):**

```
src/
├── domain/          # Entities, business rules
├── application/     # Use cases
├── infrastructure/  # External APIs, DB
├── tools/           # Agent tools (finance, search, etc.)
└── presentation/    # TUI (Ink), CLI
```

---

### 🌐 JS Web (Vite / Next.js / React)

**Detektálás:** `package.json` + `vite` / `next` / `react` dependency.

**Read-only validáció:**

```bash
# Lint
npm run lint                  # ESLint

# Type check
npx tsc --noEmit

# Unit tests (Vitest)
npm test                      # vagy npx vitest run
npx vitest run --coverage

# E2E (Playwright, ha van)
npx playwright test

# Build
npm run build
```

**Módosító javítás (csak explicit fix feladatnál):**

```bash
npx eslint src/ --fix
npx prettier --write .
```

**Indítás / preview (csak ha az ember kéri, vagy a feladat kifejezetten futtatást igényel):**

```bash
npm run preview               # production preview, tartós folyamat lehet
```

**Küszöbök:**

| Metrika | Local | CI |
|---------|-------|-----|
| TS errors | 0 | 0 |
| ESLint errors | 0 | 0 |
| Vitest failures | 0 | 0 |
| Coverage | ≥80% | ≥90% |
| Build | passes | passes |

**Struktúra (research-kb / blackjack példa):**

```
src/
├── components/      # React komponensek (presentation)
├── hooks/           # React hooks
├── lib/             # Pure logic (domain + application)
├── services/        # API hívások (infrastructure)
└── types/           # TS típusok

tests/ vagy src/**/__tests__/   # Vitest unit tests
e2e/                # Playwright (opcionális)
```

---

### ☕ JVM (Spring Boot / Maven)

**Detektálás:** `pom.xml` (Maven) vagy `build.gradle` (Gradle).

**Toolchain (Maven):**

```bash
# Tests
./mvnw test

# Verify (full quality)
./mvnw verify

# Coverage report (JaCoCo)
./mvnw jacoco:report
# → target/site/jacoco/index.html

# Static analysis (SpotBugs / Checkstyle, ha config)
./mvnw spotbugs:check
./mvnw checkstyle:check

# Build
./mvnw package
```

**Küszöbök:**

| Metrika | Local | CI |
|---------|-------|-----|
| Test failures | 0 | 0 |
| Coverage (JaCoCo) | ≥80% | ≥90% |
| Checkstyle | warn | 0 |
| SpotBugs | warn | 0 |

**Struktúra (Spring Boot):**

```
src/main/java/
└── tld/domain/app/
    ├── domain/      # Entities, value objects
    ├── application/ # Services, use cases
    ├── infrastructure/  # JPA, repositories, external clients
    └── presentation/    # Controllers, DTOs

src/test/java/      # JUnit tests
src/main/resources/ # application.yml, templates
```

---

### 🛠️ Új stack hozzáadása

Ha új stack jelenik meg (Go, Rust, PHP, .NET):

1. **Detektálás** (jellemző fájl és mappa)
2. **Toolchain** (lint, format, typecheck, test, build parancsok)
3. **Küszöbök** (mit jelent ZÖLD)
4. **Struktúra** (clean architecture leképezés)

Csak akkor adj hozzá ha tényleg van olyan repó. **Túlfejlesztés tilos.**

---

## 📋 SESSION WORKFLOW PÉLDA

### 1. Munkaszakasz indulása

```bash
pwd
# → /home/tibor/PythonProjects/trading-data-server
git status
# → On branch main; nothing to commit, working tree clean
ls -la
# → AGENTS.md, PRODUCTION_MANDATE.md, quality_gate.sh, src/, tests/, pyproject.toml
cat AGENTS.md     # ezt a fájlt
```

### 2. Magyar utasítás érkezik

> "Nézd át ezt a repót, és mondd meg, mi akadályozza hogy production-ready legyen."

### 3. SZKEA értelmezés

- **Szándék**: audit, production readiness check (PRODUCTION_MANDATE.md)
- **Korlát**: nincs említve módosítás → **read-only**
- **Ellenőrzés**: stack adapter (Python) szerint
- **Átadás**: HANDOFF.md formátum

### 4. Végrehajtás

```bash
# Stack detektálás
cat pyproject.toml
ls src/

# Quality gate: előbb módellenőrzés, mert repo-függő hogy mi read-only
./quality_gate.sh --help
# ./quality_gate.sh --full csak akkor, ha bizonyítottan nem módosít fájlokat

# Production mandate ellenőrzés (mentálisan a 26 kritérium)
# Solo desktop projekt → 1-7, 13, 17, 20, 22, 26 kötelező
```

### 5. HANDOFF riport

Magyar nyelven, 6 szekcióban (lásd HANDOFF.md).

---

## TL;DR

1. **Magyar nyelven beszélj** — SZKEA módszer, természetes szándék
2. **Teljes, nem placeholder módosítás** — nincs csonkolás, patch/diff OK
3. **Repo struktúra követése** — Clean Architecture ahol van, máshol ami a repóé
4. **Quality gate ZÖLD** — stack adapter szerint
5. **Tesztek kötelezők** — gyengítés tilos, frissítés explicit viselkedésváltozásnál OK
6. **Config manipulation tilos** — gate kikerülésére
7. **Debug az agent dolga** — soha ne delegáld emberre
8. **HANDOFF.md formátum** a végén
9. **GIT_WORKFLOW.md** szabályok mindig
10. **PRODUCTION_MANDATE.md** 26 kritérium release döntéshez
11. **📓 UPDATE learnings.md** — session végén KÖTELEZŐ

Code is written once, read many times. Git tracks everything — or it doesn't exist.
