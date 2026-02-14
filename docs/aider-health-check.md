# 🏥 Aider Projekt Health Check - Lépésről Lépésre

## 📋 Alapelv
**Ne egyszerre kérj mindent!** Az Aider túlterhelődik → progresszíven haladj.

---

## ⚡ FASE 1: Gyors Diagnosztika (2-5 perc)

### 1️⃣ Első parancs (MINDIG ezt indítsd)
```bash
aider --no-git
```

Majd **pontosan ezt** írd be:

```
Kérlek végezz egy gyors projekt health check-et. Add meg:

1. **Projekt típusa és technológiai stack** (nyelvek, framework-ök, függőségek)
2. **Fájlstruktúra minősége** (van-e logikus szervezés, patterns)
3. **Top 3 kritikus probléma** amit azonnal látó (ha van)
4. **Projekt érettségi szintje** (prototype/development/production-ready)

NE csinálj semmit, csak elemezz és írj egy rövid összefoglalót!
```

### 🎯 Mit vársz el:
- ✅ Gyors áttekintés (30-90 másodperc)
- ✅ Azonosítja a tech stack-et
- ✅ Kiemeli a nyilvánvaló problémákat
- ❌ NEM javít semmit (csak felméri)

---

## 🔍 FASE 2: Statikus Elemzés (5-10 perc)

### 2️⃣ Második parancs

```
Most futtasd le ezeket a parancsokat és értékeld az eredményeket:

**Python projekt:**
- `ruff check . --statistics`
- `mypy . --ignore-missing-imports`

**JavaScript/TypeScript:**
- `npm run lint` vagy `eslint .`
- `tsc --noEmit` (ha TypeScript)

**Általános:**
- `find . -name "*.py" | xargs wc -l` (vagy .js/.ts)
- `git log --oneline -10` (ha van git history)

Írd meg egy táblázatban:
1. Hibák száma típusonként (kritikus/magas/közepes/alacsony)
2. Leggyakoribb hibaminták
3. Kódbázis mérete (sorok, fájlok)
4. Ajánlott javítási prioritások
```

### 🎯 Mit vársz el:
- ✅ Konkrét számok (pl. "247 hiba: 12 kritikus, 89 magas...")
- ✅ Összesítés táblázatban
- ✅ Prioritási lista
- ❌ Még mindig NEM javít!

---

## 🏗️ FASE 3: Architektúra Audit (10-15 perc)

### 3️⃣ Harmadik parancs

```
Elemezd a projekt architektúráját:

1. **Design patterns** - milyen mintákat használ? (MVC, Repository, Service Layer, stb.)
2. **Separation of concerns** - tisztán elkülönülnek a rétegek?
3. **Dependency injection** - van-e? Jól használt?
4. **Error handling** - konzisztens? Van központi exception kezelés?
5. **Testing** - van test coverage? Mennyire?
6. **Configuration** - környezeti változók, config fájlok kezelése?

Add meg egy **pontozással (1-5)** minden kategóriára és 2-3 mondatos indoklással.
```

### 🎯 Mit vársz el:
- ✅ Strukturált értékelés
- ✅ Konkrét javítási javaslatok
- ✅ Gyenge pontok azonosítása

---

## 🚀 FASE 4: Action Plan (5 perc)

### 4️⃣ Negyedik parancs

```
Most készíts egy **priorizált javítási tervet** 3 kategóriában:

**🔴 KRITIKUS (azonnal javítandó):**
- Blokkoló hibák
- Biztonsági rések
- Működést gátló problémák

**🟡 MAGAS (1-2 héten belül):**
- Kód minőség javítások
- Refactoring feladatok
- Tech debt csökkentés

**🟢 ALACSONY (nice-to-have):**
- Stílus finomhangolás
- Dokumentáció bővítés
- Performance optimalizálás

Minden feladathoz add meg:
- Becsült időigény (óra)
- Nehézségi szint (1-5)
- Függőségek (ha van)
```

### 🎯 Mit vársz el:
- ✅ Konkrét, végrehajtható terv
- ✅ Időbecslésekkel
- ✅ Priorizálva

---

## 💊 FASE 5: Automatizált Javítás (Iteratív)

### 5️⃣ Ötödik parancs (CSAK EZUTÁN javítasz!)

```
Kezdjük el a javításokat! Először a KRITIKUS kategóriából:

1. Javítsd az [első kritikus probléma neve] hibát
2. Commit-old "fix: [rövid leírás]" üzenettel
3. Futtass ellenőrzést (ruff check / eslint)
4. Ha sikeres, jelezd és kérd a következő feladatot
```

### 🎯 Iteratív folyamat:
```
Javítás → Ellenőrzés → Commit → Következő feladat
```

**FONTOS:** Egyszerre max 1-2 fájlt javíts! Ha sok a hiba:
```
Javítsd az összes F821 hibát a src/infrastructure/ mappában, 
és commitold "fix(infrastructure): resolve undefined name errors"
üzenettel. Aztán várj további instrukciókra!
```

---

## 📊 BONUS: Mérőszámok Követése

### Ha CI/CD-d van:

```yaml
# .github/workflows/health-check.yml
name: Project Health
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint Check
        run: ruff check . --statistics --output-format=json > metrics.json
      - name: Complexity
        run: radon cc . -a -nb
      - name: Security
        run: bandit -r . -f json -o security.json
```

### Követendő metrikák:
- **Hibák száma** (trend: csökken?)
- **Complexity** (McCabe score < 10)
- **Test coverage** (> 80%)
- **Dependency security** (0 kritikus CVE)

---

## 🎯 TL;DR - Copy-Paste Starter

```bash
# 1. Projekt gyökerébe navigálj
cd /path/to/project

# 2. Indítsd Aidert
aider --no-git

# 3. Másold be:
```

**FASE 1 - Gyors Overview:**
```
Végezz gyors health check-et: projekt típus, stack, top 3 probléma, érettségi szint. NE javíts semmit!
```

**FASE 2 - Statikus Elemzés:**
```
Futtasd: ruff check . --statistics
Értékeld táblázatban: hibaszámok típusonként, gyakori minták, prioritások.
```

**FASE 3 - Architektúra:**
```
Elemezd az architektúrát: design patterns, separation of concerns, DI, error handling, testing, config. Pontozz 1-5-ig minden kategóriára.
```

**FASE 4 - Action Plan:**
```
Készíts priorizált javítási tervet: KRITIKUS/MAGAS/ALACSONY kategóriákban, időbecslésekkel és függőségekkel.
```

**FASE 5 - Javítás (CSAK EZUTÁN!):**
```
Javítsd az első kritikus hibát, commitold, ellenőrizd. Egy feladat = egy üzenet!
```

---

## 🛡️ Pro Tippek

### ✅ DO:
- Progresszívan haladj (ne ugorj azonnal javításba)
- Egy commit = egy logikai változás
- Kérj összefoglalót minden fase után
- Mentsd a health check eredményeket (`HEALTH_REPORT.md`)

### ❌ DON'T:
- Ne kérj mindent egyszerre (túlterheli az AI-t)
- Ne javíttasd az ÖSSZES hibát egyben (100+ fájl = context overflow)
- Ne felejtsd el ellenőrizni a változásokat (`git diff`)
- Ne commitolj tesztelés nélkül

---

## 📈 Siker Mérése

**Előtte:**
```
❌ 247 ruff hiba
❌ Nincs type annotation
❌ Kevert architektúra
❌ 0% test coverage
```

**Utána:**
```
✅ 3 alacsony prioritású hiba
✅ 95%+ type coverage
✅ Clean architecture
✅ 60%+ test coverage
```

---

**Következő lépés:** Próbáld ki egy test projekten, és figyeld milyen eredményt ad! 🚀