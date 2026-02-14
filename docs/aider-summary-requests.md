# 📋 Aider Összefoglaló Kérések - Context Management

## 🎯 Alapelv

**NE TE emlékeztesd mindig az AI-t!** Kérj tőle rendszeres összefoglalókat, így:
- ✅ Te kontrolláltad a folyamatot
- ✅ Az AI felfrissíti a saját context-ét
- ✅ Követhető a progress
- ✅ Könnyebb újraindítani sessionöket

---

## 1️⃣ Egyszerű Checkpoint (Gyors - 30 másodperc)

### Prompt sablon:

```
CHECKPOINT! Készíts egy gyors összefoglalót:

✅ MIT CSINÁLTUNK EDDIG? (commitok listája)
⏳ MIN DOLGOZUNK MOST?
📋 MI VAN HÁTRA? (todo lista)
```

### Példa válasz:

```
✅ ELKÉSZÜLT:
- fix(db): F821 hibák javítva memory_blood_pressure_repository.py-ban
- fix(charts): BLE001 hibák javítva base_chart.py-ban
- fix(charts): E501 túl hosszú sorok base_chart.py-ban

⏳ MOST:
- E501 hibák javítása blood_pressure_chart.py-ban (3/7 sor kész)

📋 HÁTRALEVŐ:
- E501 hibák: 4 fájl
- ANN hibák: src/charts/* (később)
- PLR2004: mágikus számok (alacsony prioritás)
```

### Mikor használd:
- ⏱️ 20-30 percenként
- 🔄 Munka közben gyors refresh
- 🤔 Ha elvesztetted a fonalat

---

## 2️⃣ Részletes Session Report (Alapos - 2-3 perc)

### Prompt sablon:

```
Készíts egy PROGRESS.md fájlt a következő struktúrával:

# Session Progress Report
Date: [mai dátum]
Duration: [mennyi ideje dolgozunk]

## Completed Tasks
- [minden commit üzenettel és fájlnévvel]

## Current Task
- File: [melyik fájlon]
- Issue: [mit javítunk]
- Progress: [hol tartunk]

## Remaining Tasks (prioritized)
### 🔴 High Priority
- [ ] ...
### 🟡 Medium Priority  
- [ ] ...
### 🟢 Low Priority
- [ ] ...

## Blockers / Issues
[ha van valami probléma]

## Next Steps
1. [következő 3 lépés]
```

### Példa eredmény:

```markdown
# Session Progress Report
Date: 2025-10-25
Duration: 1.5 óra

## Completed Tasks
- fix(db): F821 undefined names in memory_blood_pressure_repository.py
- fix(db): F821 undefined names in memory_sleep_cycle_repository.py
- fix(charts): BLE001 blind except in base_chart.py
- fix(charts): E501 line length in base_chart.py
- refactor(charts): PLR2004 magic values to constants in base_chart.py

## Current Task
- File: src/charts/blood_pressure_chart.py
- Issue: E501 - Line too long (5 locations)
- Progress: 3/5 lines refactored

## Remaining Tasks (prioritized)
### 🔴 High Priority
- [ ] E501 errors in blood_pressure_chart.py (2 remaining)
- [ ] E501 errors in sleep_quality_chart.py
- [ ] E501 errors in weather_correlation.py

### 🟡 Medium Priority  
- [ ] ANN type annotations (all chart modules)
- [ ] PLR2004 magic values in other modules

### 🟢 Low Priority
- [ ] Finalize docstrings
- [ ] Add type hints to lambda functions

## Blockers / Issues
None currently.

## Next Steps
1. Complete E501 fixes in blood_pressure_chart.py
2. Run full ruff check to verify
3. Move to sleep_quality_chart.py
```

### Mikor használd:
- 🕐 Hosszabb session vége (1+ óra után)
- 💾 Session mentése (később folytatod)
- 📊 Team reportinghoz
- 🔄 Context túl nagy lett (refresh kell)

---

## 3️⃣ Quick Status (Ultra Gyors - 10 másodperc)

### Prompt sablon:

```
1 mondatban: most min dolgozol és mi a következő lépés?
```

### Példa válasz:

```
Most az E501 hibákat javítom a blood_pressure_chart.py-ban (142. sor),
következő: ugyanez a sleep_quality_chart.py-ban.
```

### Mikor használd:
- ❓ Gyors kérdés a státuszról
- ☕ Visszajöttél egy szünetből
- 🔍 Ellenőrzés hogy jó irányban halad-e

---

## 4️⃣ Git-based Summary (Objektív)

### Prompt sablon:

```
Futtasd: git log --oneline -10

Majd csoportosítsd kategóriánként mit csináltunk:
- Bugfixes: ...
- Refactoring: ...
- Documentation: ...
- Testing: ...

És mondd meg mi maradt hátra az eredeti tervből.
```

### Példa válasz:

```
GIT HISTORY ALAPJÁN:

Bugfixes (5 commit):
- fix(db): F821 undefined names (2 fájl)
- fix(charts): BLE001 blind except (1 fájl)
- fix(charts): E501 line too long (2 fájl)

Refactoring (2 commit):
- refactor(charts): PLR2004 magic values
- refactor(db): improve error messages

Documentation (0 commit):
- Nincs még

Testing (0 commit):
- Nincs még

EREDETI TERVBŐL HÁTRA:
- E501 hibák: 3 fájl (70% kész)
- ANN type annotations: 8 fájl (0% kész)
- PLR2004 magic values: 5 fájl (20% kész)
```

### Előnye:
- ✅ Git history = objektív igazság
- ✅ Nem az AI memóriájára támaszkodik
- ✅ Ellenőrizhető

### Mikor használd:
- 🔍 Bizonytalan vagy hogy mit csinált az AI
- 📊 Pontos riport kell
- 🐛 Debugging (mi változott?)

---

## 5️⃣ Proaktív Auto-Checkpoint

### Prompt sablon (Session elején add meg):

```
SZABÁLY: Minden 3. feladat után automatikusan írj egy 
CHECKPOINT összefoglalót commit nélkül. Formátum:

═══════════════════════════════════════════
📊 CHECKPOINT #[sorszám]
═══════════════════════════════════════════
✅ Utolsó 3 commit:
1. [...]
2. [...]  
3. [...]

⏳ Jelenlegi scope: [...]
📋 Következő 3 feladat:
1. [...]
2. [...]
3. [...]
═══════════════════════════════════════════

Folytatjuk? (Y/n)
```

### Hogyan működik:

1. **Session elején:** Megadod a szabályt
2. **AI automatikusan:** 3 feladat után checkpoint-ot ír
3. **Te döntesz:** folytatod vagy módosítasz

### Példa használat:

```
Te: [megadod a szabályt]

AI: [csinál 3 feladatot]

AI: 
═══════════════════════════════════════════
📊 CHECKPOINT #1
═══════════════════════════════════════════
✅ Utolsó 3 commit:
1. fix(db): F821 in memory_blood_pressure_repository.py
2. fix(db): F821 in memory_sleep_cycle_repository.py
3. fix(charts): BLE001 in base_chart.py

⏳ Jelenlegi scope: src/charts/blood_pressure_chart.py

📋 Következő 3 feladat:
1. E501 fixes in blood_pressure_chart.py
2. E501 fixes in sleep_quality_chart.py
3. E501 fixes in weather_correlation.py
═══════════════════════════════════════════

Folytatjuk? (Y/n)

Te: Y [vagy változtatsz irányt]
```

### Előnye:
- ✅ **Automatikus** context refresh
- ✅ Te nem felejted el kérni
- ✅ Rendszeres megállási pontok
- ✅ Kontroll megmarad (Y/n)

---

## 6️⃣ Context Refresh Workflow (Amikor ELVESZTED a fonalat)

### 3 lépéses folyamat:

#### Lépés 1: Kérj összefoglalót

```
STOP! Összefoglaló kérés:
- Mit csináltunk az utolsó 5 commitban?
- Mit ígértél hogy csinálsz most?
- Van valami amit elkezdtél de nem fejezted be?
```

#### Lépés 2: Validálj (te magad)

```bash
git log --oneline -5
git status
git diff
```

#### Lépés 3: Korrigálj (ha kell)

```
Kicsit összezavarodtál. Az IGAZ helyzet:

GIT LOG:
[másold be a git log kimenetét]

GIT STATUS:
[másold be a git status kimenetét]

Szóval a következő feladat valójában: [...]

Megerősíted hogy érted?
```

### Mikor használd:
- 🤯 AI teljesen összezavarodott
- 🔄 Túl hosszú session (1.5+ óra)
- 🐛 Fura dolgokat csinál
- 📝 Nem azt írja amit kértél

---

## 7️⃣ Persistent Progress Tracking (PROGRESS.md)

### Session elején:

```
Ha van PROGRESS.md fájl, olvasd be és folytasd onnan.
Ha nincs, készíts egyet ezzel a struktúrával:

[ide jön a #2 sablon]
```

### Session végén:

```
Frissítsd a PROGRESS.md-t a mai munkával:
- Timestamp: [mai dátum + idő]
- Elvégzett feladatok listája
- Megmaradt feladatok
- Jegyzet (ha van valami fontos)
```

### Példa PROGRESS.md:

```markdown
# Project Health Improvement Progress

## 2025-10-25 14:30 - Session #1
### Completed
- ✅ Initial health check (ruff analysis)
- ✅ F821 errors fixed (src/infrastructure/db/)
- ✅ BLE001 errors fixed (src/charts/base_chart.py)

### In Progress
- ⏳ E501 errors (blood_pressure_chart.py - 50% done)

### Todo
- [ ] E501 errors (remaining 3 files)
- [ ] ANN type annotations
- [ ] PLR2004 magic values

### Notes
- Model: GLM-4.6 (proaktív, scope limitet kell!)
- Total commits: 5
- Estimated remaining: 2-3 hours

---

## 2025-10-26 09:00 - Session #2
### Completed
- ✅ E501 errors finished (all chart files)
- ✅ Started ANN type annotations (base_chart.py)

### In Progress
- ⏳ ANN type annotations (blood_pressure_chart.py - 30% done)

### Todo
- [ ] ANN type annotations (remaining 2 files)
- [ ] PLR2004 magic values
- [ ] Final ruff check + cleanup

### Notes
- Switched to Sonnet 4 for better type inference
- Found some edge cases in error handling
```

### Előnye:
- ✅ **Folytonos történet** session-ök között
- ✅ Commitolható (csapatmunka esetén)
- ✅ AI mindig be tudja tölteni
- ✅ Te is követni tudod

---

## 8️⃣ Emergency Hard Reset (Veszélyhelyzet)

### Jelek hogy kell:
- ❌ AI 3x megkérdezte ugyanazt
- ❌ Összekeveri a régi és új feladatokat
- ❌ Módosít fájlokat amikhez nem kéne nyúljon
- ❌ Context túl nagy (lassú válaszok)

### Hard Reset Protokoll:

```
EMERGENCY CONTEXT RESET!

LÉPÉSEK:
1. Commitolj mindent amit eddig csináltunk:
   git add .
   git commit -m "wip: checkpoint before context reset"

2. /clear (Aider context törlése)

3. Olvasd be a PROGRESS.md fájlt (ha van)

4. ÚJ SESSION INDÍTÁSA:
   Scope: [következő konkrét feladat - CSAK 1 dolog]
   Előzmény: [csak ami TÉNYLEG releváns]
   Cél: [egyetlen, mérhető eredmény]

Megerősíted hogy clean slate-tel kezdünk?
```

### Utána:

```
/add [csak a szükséges fájlok]

ÚJ FELADAT (minden más irreleváns):
[tisztán megfogalmazott feladat]
```

---

## 9️⃣ AI mint Scrum Master (Fordított Szerepjáték)

### Prompt (session elején):

```
SZEREPJÁTÉK: Te vagy a Scrum Master, én vagyok a developer.

TE FELELŐS VAGY:
- Sprint progress tracking
- Checkpoint-ok készítése (kéretlenül is, 30 percenként!)
- Figyelmeztetés ha off-scope megyek
- Session végén stand-up summary

ÉN FELELŐS VAGYOK:
- Feladatok végrehajtása
- Döntések a prioritásokról

SZABÁLY: Te proaktívan menedzseled a session-t!

Kezdjük! Mi a mai sprint goal?
```

### Mit várj:

Az AI **automatikusan** fogja:
- ✅ Rendszeresen checkpoint-ot írni
- ✅ Figyelmezteti ha elkanyarodsz
- ✅ Session végén összefoglalót ad
- ✅ Javaslatot tesz a következő lépésekre

### Előnye:
- 🎯 **Proaktív** context management
- 🤖 AI önállóan figyeli a progresst
- 🧠 Te csak a fejlesztésre fókuszálsz
- ✨ Kevesebb mikromenedzsment

---

## 🎓 Best Practice Checklist

### ✅ Minden session:

```
START:
[ ] Betöltöd a PROGRESS.md-t (ha van)
[ ] Tisztázod a scope-ot

KÖZBEN:
[ ] 20-30 percenként: gyors checkpoint
[ ] Ha elveszik: summary → validálás → reset

END:
[ ] Frissíted a PROGRESS.md-t
[ ] NEXT_SESSION.md (mi jön holnap)
```

### ✅ Hosszú session (1.5+ óra):

```
[ ] 45 percenként: részletes összefoglaló
[ ] PROGRESS.md file-ba (nem csak chat)
[ ] Git commitok rendszeresek (10-15 perc)
[ ] Context refresh (ha túl nagy)
```

### ✅ Ha context problémás:

```
[ ] /clear parancs
[ ] Hard reset új prompttal
[ ] Csak releváns fájlok (/add)
[ ] Git validáció
```

---

## 📊 Real-world Session Példa

### 09:00 - Session Start

```
Te: Health check + statikus elemzés. 
    Commitold HEALTH_REPORT.md-be.
```

### 09:15 - Checkpoint #1

```
Te: Gyors státusz: mit csináltál, mi van hátra?

AI: "HEALTH_REPORT.md elkészült, 247 hiba azonosítva, 
     következő: F821 javítás src/infrastructure/ mappában"
```

### 09:45 - Checkpoint #2

```
Te: Hol tartunk az F821 javításokkal?

AI: "2/3 fájl kész (memory_blood_pressure_repository.py ✅, 
     memory_sleep_cycle_repository.py ✅), 
     hátra: memory_metrics_repository.py"
```

### 10:30 - Session End

```
Te: Session vége. Frissítsd a PROGRESS.md-t és 
    készíts NEXT_SESSION.md fájlt a holnapi folytatáshoz.

AI: [elkészíti mindkét fájlt]
```

---

## 🎯 Copy-Paste Quick Reference

### Gyors checkpoint (20 perc után):
```
CHECKPOINT! Mit csináltunk, min dolgozunk, mi van hátra?
```

### Részletes riport (session vége):
```
Készíts PROGRESS.md fájlt a session munkájáról.
```

### Quick refresh (bármikor):
```
1 mondatban: most min dolgozol?
```

### Context elveszett:
```
STOP! Mit csináltunk az utolsó 5 commitban? 
Mit ígértél hogy csinálsz? Van félbehagyott feladat?
```

### Hard reset (vészhelyzet):
```
/clear
EMERGENCY RESET! Commitolj mindent, töröld a context-et,
kezdjük újra tiszta lappal.
```

### Proaktív AI (session elején):
```
SZABÁLY: Minden 3. feladat után automatikus checkpoint!
```

### AI mint manager (session elején):
```
SZEREPJÁTÉK: Te vagy a Scrum Master, 
proaktívan menedzseld a session-t!
```

---

## 💡 Pro Tippek

1. **Ne várj vele!** Checkpoint-ot kérj **még mielőtt** elvesznél
2. **PROGRESS.md = single source of truth** (nem az AI memória!)
3. **Git commit > chat history** (objektív vs szubjektív)
4. **Hard reset nem vereség** (néha ez a leggyorsabb megoldás)
5. **Proaktív AI** beállítás jobb mint reaktív checkpoint-ok

---

## 🎬 Összefoglalás

**Arany szabály:**
> "Az AI-nak NINCS hosszútávú memóriája. 
> Rendszeres összefoglalók = artificiális memória."

**Gyakoriság:**
- ⚡ Quick status: **bármikor**
- 📋 Checkpoint: **20-30 percenként**
- 📊 Részletes riport: **session vége**
- 🔄 Hard reset: **ha context elveszett**

**Eszközök:**
- Git history (objektív igazság)
- PROGRESS.md (persistent memory)
- Checkpoint prompt-ok (frissítés)
- Proaktív AI (automatizmus)

**Eredmény:**
✅ Követhető munka
✅ Kontrollált AI
✅ Folytatható session-ök
✅ Kevesebb context-vesztés

---

**Most próbáld ki az első projekten és nézd meg mekkora különbség!** 🚀