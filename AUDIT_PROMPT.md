> ⚠️ AGENT INSTRUKCIÓ: Olvasd el ezt a teljes fájlt mielőtt bármit teszel.
> Ne kezdj semmilyen műveletet amíg el nem jutottál az utolsó sorig.
> Fázisonként dolgozz és adj összefoglalót mielőtt továbblépnél.
# AUDIT_PROMPT.md — Projekt kódbázis audit
<!-- Stack: FASTAPI -->
<!-- Projekt: meteo-analytics -->
<!-- Generálva: 2026-03-30 -->

---

## AGENT COMPLIANCE CONTRACT

Mielőtt bármit csinálsz:
1. Olvasd el ezt a teljes fájlt
2. Ne kezdj el semmilyen módosítást a PHASE 1 befejezése előtt
3. Minden fázis végén adj összefoglaló jelentést, mielőtt továbblépnél
4. Ha bizonytalan vagy egy döntésben → kérdezz, ne feltételezz
5. Soha ne töröld vagy módosítsd a `.git/` könyvtárat
6. A scope: **csak ez a projekt gyökérkönyvtára**, nem más projektek

---

## PHASE 0 — Függőség tisztítás (KÖTELEZŐ ELSŐ LÉPÉS)

A legtöbb projektben a requirements.txt `pip freeze` kimenet az egész
rendszerkörnyezetből — nem a projekt valódi függősége. Ezt kell először
rendbe tenni.

### 0.1 Valódi függőségek feltárása
```bash
cd <PROJEKT_GYÖKÉR>
pip install pipreqs
pipreqs . --force --ignore .venv,.venv_audit,venv,tests
```
Az így kapott `requirements.txt` csak a ténylegesen importált csomagokat
tartalmazza. Hasonlítsd össze a régivel — dokumentáld a különbséget.

### 0.2 Virtuális környezet ellenőrzés
- Van-e `.venv/` vagy `venv/` a projektben?
- Role a `.gitignore`-ban: benne van-e a venv könyvtár?
- Ha nincs venv: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

### 0.3 Verzió rögzítés
A pipreqs által generált requirements.txt-ben nincsenek verziók.
Rögzítsd őket:
```bash
pip install -r requirements.txt
pip freeze | grep -Ff requirements.txt > requirements.lock
```
Kimenet: `requirements.txt` (minimális, emberi), `requirements.lock` (pontos, reprodukálható)

### 0.4 Döntés
Ha a régi requirements.txt >2x annyi csomagot tartalmaz mint a pipreqs
kimenete: a régi FELÜLÍRANDÓ. Dokumentáld mit távolítottál el és miért.

## PHASE 1 — Kódbázis térkép & Hívásgráf

### 1.1 Projekt struktúra feltárás
```
Futtasd le:
- find . -type f -name "*.py" | sort
- cat requirements*.txt 2>/dev/null || cat pyproject.toml 2>/dev/null
- Azonosítsd: entry point(ok), config fájlok, .env fájlok, test könyvtárak
```

Készíts egy **könyvtárfa áttekintést** magyarázattal: mi micsoda, mi a szerepe.

### 1.2 Dependency térkép
- Listázd az összes külső függőséget verzióval
- Jelöld meg a **kiadatlan/elavult** csomagokat (pip list --outdated mintájára)
- Azonosítsd a **közvetlen vs. tranzitív** függőségeket

### 1.3 Belső hívásgráf
Térképezd fel a belső modulok közötti függőséget:
- Melyik modul hív melyiket (import gráf)
- Körkörös importok azonosítása
- God module-ok (minden mást importáló modulok)
- Entry pointtól a legmélyebb hívásig: írd le a főbb végrehajtási útvonalakat

**Kimenet:** Szöveges gráf vagy ASCII ábrázolás a híváslánc főbb ágaival.

### 1.4 Dead code előszűrés
```
Keress manuálisan:
- Soha nem importált modulok
- Soha nem hívott top-level funkciók
- Kommentált kódblokkokat (# TODO, # FIXME, # HACK jelölések listája)
```

---

## PHASE 2 — Biztonsági audit

### 2.1 Secrets & credentials
Keress minden fájlban (beleértve .env, config, YAML, TOML):
- Hardcoded API kulcsok, tokenek, jelszavak
- Mintázatok: `sk-`, `Bearer `, `password =`, `secret =`, `token =`
- Base64-kódolt stringek amelyek credential-nek néznek ki
- .gitignore-ból HIÁNYZÓ .env fájlok (ellenőrizd: van-e .env a .gitignore-ban?)

**Kimenet:** Táblázat — Fájl | Sor | Típus | Súlyosság (KRITIKUS/MAGAS/KÖZEPES)

### 2.2 Injection pontok
- SQL injection: nyers string konkatenáció query-kben (f-string + SQL)
- Command injection: `subprocess`, `os.system`, `eval()`, `exec()` nem sanitizált inputtal
- Path traversal: `open()` felhasználói inputtal kombinálva
- SSRF: külső URL-ek validálás nélkül

### 2.3 Autentikáció & authorizáció
- Van-e auth middleware? Ha igen, lefed-e minden végpontot?
- Session kezelés: token expiry, refresh logika
- Admin/privilegizált végpontok védelem nélkül?
- CORS konfiguráció: `*` allow-origin?

### 2.4 Dependency vulnerabilities
```bash
pip audit 2>/dev/null || safety check 2>/dev/null || echo "Nincs audit tool telepítve"
```
Ha egyik sem elérhető: listázd a függőségeket és jelöld a known-vulnerable verziókat.

---

## PHASE 3 — Teljesítmény & optimalizáció

### 3.1 N+1 és adatbázis problémák
- ORM használatnál: lazy loading N+1 minták (ciklusban lekérdezés)
- Index nélküli WHERE feltételek (ha látható a schema)
- Kapcsolat pooling hiánya
- Tranzakciók helytelen kezelése

### 3.2 Memória problémák
- Nagy adathalmazok memóriába töltése (`.fetchall()`, list comprehension GB-os adaton)
- Generator helyett list ahol pazarló
- Globális state akkumuláció (class variable-ok amelyek nőnek)
- Nem zárt file handle-ok, DB kapcsolatok (`with` nélküli `open()`)

### 3.3 Lassú helyek
- Szinkron I/O ahol async indokolt lenne
- Ciklusban hálózati hívások
- Caching hiánya ismétlődő számításoknál
- Újrakompilált regex ciklusban (`re.compile()` hiánya)

### 3.4 Kód minőség
- Duplikált logika (copy-paste blokkok)
- Túl mély nesting (4+ szint)
- Funkciók amelyek >50 sort csinálnak egyszerre (SRP sértés)
- Type hints hiánya kritikus interfészeken

---

## PHASE 4 — Git állapot tisztítás

### 4.1 Branch állapot
```bash
git branch -a
git log --oneline --graph --all | head -30
```
- Orphan branch-ek (soha nem merge-elt, >30 napja inaktív)
- Stash-ek amelyek elfelejtődtek: `git stash list`

### 4.2 Commit history
- Nagy fájlok a historyben: `git rev-list --objects --all | sort -k2 | tail -20`
- Accidentálisan commitált .env vagy secrets (grep a historyben)
- "WIP", "test", "temp" commit üzenetek amelyek production branch-en landoltak

### 4.3 .gitignore audit
Ellenőrizd, hogy a következők mind szerepelnek:
```
.env
.env.*
*.pyc
__pycache__/
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
*.log
*.sqlite
*.db
```

### 4.4 Tracked fájlok amelyek nem kellene
```bash
git ls-files | grep -E "\.(env|log|db|sqlite|pyc)$"
```
Ha van találat: `git rm --cached <fájl>` és .gitignore frissítés.

### 4.5 README & dokumentáció állapot
- Van README.md? Aktuális?
- Dokumentált-e: hogyan kell futtatni, milyen env változók kellenek, mi a purpose?

---

## AUDIT ÖSSZEFOGLALÓ (töltsd ki minden fázis után)

| Terület | Kritikus | Magas | Közepes | Alacsony |
|---------|----------|-------|---------|---------|
| Secrets/Security | | | | |
| Injection | | | | |
| Auth | | | | |
| Teljesítmény | | | | |
| Git hygiene | | | | |

**Top 5 azonnali teendő:**
1.
2.
3.
4.
5.

**Becsült tisztítási idő:** [X óra]
**GitHub-ra kerülhet:** [ ] Igen / [ ] Nem — Okok: ...

---

## STACK-SPECIFIKUS KIEGÉSZÍTÉS

<!-- Illeszd be az alább megfelelő blokkot -->
<!-- FastAPI → STACK_FASTAPI.md -->
<!-- Flask → STACK_FLASK.md -->
<!-- Pure Python CLI/lib → STACK_PURE_PYTHON.md -->
# STACK_FASTAPI.md — FastAPI specifikus audit blokk
<!-- Illessze be az AUDIT_PROMPT.md végére -->

---

## FASTAPI SPECIFIKUS AUDIT

### F1 — Router struktúra
- APIRouter-ek logikusan szeparáltak-e? (auth, users, items stb.)
- Van-e prefix és tags minden router-en? (OpenAPI dokumentáció minőség)
- Response model-ek minden végponton definiáltak? (Pydantic output validation)

### F2 — Pydantic modellek
- Input validation szigorú? (`strict=True` ahol szükséges)
- Validators (`@validator`, `@field_validator`) nem bypassolhatók-e?
- Sensitive mezők (`password`, `token`) kizárva a response model-ből?
- ORM mode / `from_attributes` indokoltan van használva?

### F3 — Dependency Injection audit
- `Depends()` láncolat átlátható? Körkörös dependency?
- DB session dependency: minden kérés kap saját session-t és az le is záródik?
- Auth dependency: minden védett végponton ott van?
- Background tasks: hibakezelés megvan?

### F4 — Async helyesség
- `async def` endpoint-ok tényleg async I/O-t végeznek? (nem blokkoló sync hívás async-ben)
- `await` hiánya aszinkron hívás előtt
- `asyncio.sleep` vs `time.sleep` keveredés
- Async DB driver használt? (asyncpg, aiosqlite vs szinkron driver)

### F5 — Middleware & CORS
```python
# Keress ilyet — production-ban TILOS:
allow_origins=["*"]
allow_credentials=True  # + allow_origins=["*"] = biztonsági lyuk
```
- Rate limiting middleware van?
- Request logging / tracing middleware?
- Exception handler minden HTTP kivételre regisztrálva?

### F6 — OpenAPI / docs végpont
- `/docs` és `/redoc` production-ban le van tiltva? (információszivárgás)
```python
app = FastAPI(docs_url=None, redoc_url=None)  # production
```

### F7 — Alembic / migráció
- Minden model változás migrációban rögzítve?
- `alembic upgrade head` automatizált az indításkor? (vagy kézzel kell futtatni?)
- Down migration létezik minden up migrationhöz?
