# 🎯 Aider Context Management - Prompt Minták GLM-4.6-hoz

## 🚨 A Probléma GLM-4.6-tal

**Túl proaktív viselkedés:**
- ❌ Átírja az EGÉSZ fájlt amikor csak 1 sort kértél
- ❌ "Segít" azzal amit nem kértél (pl. refactor közben újraformáz)
- ❌ Elveszíti a fókuszt multi-turn beszélgetésben
- ❌ Összekeveri az előző feladatokat

---

## ✅ Megoldás: Explicit Context Control

### Pattern #1: Scope Limiter (Hatókör Korlátozás)

```
FONTOS: CSAK a következőket tedd:
1. Javítsd a memory_blood_pressure_repository.py fájlban az F821 hibákat
2. NE változtass semmit más fájlban
3. NE refaktorálj, NE formázz
4. Commit üzenet: "fix(repo): resolve undefined name errors"

Kész? Jelezd amikor befejezted!
```

**Miért működik:**
- ✅ Explicit scope ("CSAK")
- ✅ Enumerált lépések (1-4)
- ✅ Negatív utasítások ("NE")
- ✅ Visszajelzési pont ("Kész?")

---

### Pattern #2: Context Reset (Kontextus Nullázás)

```
STOP! Felejts el mindent amit eddig beszéltünk.

ÚJ FELADAT:
Most CSAK arra fókuszálj hogy elemezd a src/charts/ mappát.
Mit kérek: lista a fájlokról és egy 1 mondatos leírás mindegyikről.
Mit NEM kérek: javítások, refaktorálás, részletes elemzés.

Válasz formátuma:
- base_chart.py: [1 mondat]
- blood_pressure_chart.py: [1 mondat]
...

SEMMI MÁS!
```

**Használd amikor:**
- Új feladatra váltasz
- Az AI elkezdett "túlsegíteni"
- Összezavarodott az előző context miatt

---

### Pattern #3: Chunked Work (Darabolt Munka)

**❌ ROSSZ (túl nagy scope):**
```
Javítsd az összes ruff hibát a projektben
```

**✅ JÓ (explicit chunk):**
```
CHUNK 1/5: F821 hibák a src/infrastructure/db/ mappában

FELADAT:
1. Futtasd: ruff check src/infrastructure/db/ | grep F821
2. Javítsd CSAK ezeket a hibákat
3. Commitold: "fix(db): resolve F821 errors in repositories"
4. Jelezd hogy kész vagy

KÖVETKEZŐ CHUNK: Majd én kérem a következő lépést!
```

**Miért működik:**
- ✅ Tiszta határok (1/5)
- ✅ Véges feladat
- ✅ Visszajelzési pont
- ✅ Nincs "automatikus folytatás"

---

### Pattern #4: State Reminder (Állapot Emlékeztető)

Ha hosszabb session van, rendszeresen emlékeztess:

```
Állj! Összefoglalás check:

AMIT EDDIG CSINÁLTUNK:
1. ✅ F821 hibák javítva (src/infrastructure/)
2. ✅ BLE001 hibák javítva (src/charts/)
3. ⏳ MOST: E501 hibák (túl hosszú sorok)

AMIT MÉG NEM CSINÁLTUNK:
- ANN (type annotations) - KÉSŐBB
- PLR2004 (magic values) - KÉSŐBB

MOST A KÖVETKEZŐ LÉPÉS:
Javítsd az E501 hibákat CSAK a src/charts/base_chart.py fájlban.
NE menj tovább más fájlokra!

Érted? Megerősítsd mielőtt kezded!
```

---

### Pattern #5: File Lock (Fájl Zárolás)

```
/add src/charts/base_chart.py

LOCKED FILE MODE:
- CSAK ezt az 1 fájlt módosítsd: base_chart.py
- Feladat: Törj át 3 hosszú sort (87. sor, 142. sor, 198. sor)
- Minden más fájl OFF LIMITS!

Jelezd sorról-sorra mit változtatsz, mielőtt írsz!
```

**Aider parancsok ehhez:**
```bash
/drop src/charts/*.py              # Mindent levesz
/add src/charts/base_chart.py      # Csak ezt adja hozzá
```

---

## 🎛️ Session Management Tippek

### Új Task = Új Prompt Pattern

```
═══════════════════════════════════════════
  ÚJ FELADAT - ELŐZŐ CONTEXT IRRELEVÁNS
═══════════════════════════════════════════

Task ID: HEALTH-CHECK-002
Scope: src/infrastructure/db/
Goal: [konkrét cél]
Out of scope: [mit NE csináljon]

LÉPÉSEK:
1. [...]
2. [...]

AMIKOR KÉSZ, ÁLLJ MEG ÉS VÁRJ!
```

---

### Mid-Session Context Check

```
GYORS CHECK (válaszolj 1 mondatban):

1. Milyen feladaton dolgozol MOST?
2. Melyik fájl(ok) van(nak) a scope-ban?
3. Mi a KÖVETKEZŐ lépés?

Ha bármelyikre nem tudod a választ → STOP és kérdezz!
```

---

### Context Save Point (Mentési Pont)

Hosszabb session esetén:

```
CHECKPOINT - Mentsd el a session állapotát!

Készíts egy PROGRESS.md fájlt:
- Amit ELVÉGEZTÜNK (commitok listája)
- Amit MOST CSINÁLUNK (jelenlegi feladat)
- Amit MÉG HÁTRAVAN (todo lista)

Ez lesz az új kontextusunk!
```

---

## 🔧 Config Optimalizálás GLM-4.6-hoz

```yaml
# .aider.conf.yml
model: openrouter/zhipuai/glm-4-flash
map-tokens: 2048                    # Ne legyen túl nagy!
map-refresh: always
editor: none
auto-commits: false                 # FONTOS! Ne commitoljon automatikusan
dirty-commits: false                # Ne engedje dirty commit-ot
show-diffs: true                    # Mindig mutassa mit változtat

# Explicit model behavior (ha támogatja)
edit-format: whole                  # Vagy: diff / udiff
max-chat-history-tokens: 4096       # Limitáld a history-t
```

---

## 🎯 Gyakorlati Példa: Multi-Step Refactor

### ❌ ROSSZ Megközelítés:

```
"Javítsd ki az összes hibát és refaktoráld a kódot"
```

**Eredmény:** Káosz, elveszített változások, nem követhető.

---

### ✅ JÓ Megközelítés:

**Step 1:**
```
PHASE 1/4: CSAK elemzés

Futtasd: ruff check . --statistics
Készíts egy táblázatot:
- Hibatípus | Darabszám | Prioritás

NE javíts semmit! STOP amikor kész a táblázat.
```

**Step 2:**
```
PHASE 2/4: F821 hibák

Előző context: [másold be a táblázatot]

FELADAT:
- CSAK F821 (undefined names)
- CSAK src/infrastructure/db/
- 1 fájl per commit

/add src/infrastructure/db/memory_blood_pressure_repository.py

Kezdd ezzel a fájllal! Jelezd amikor kész.
```

**Step 3:**
```
PHASE 3/4: F821 folytatás

CONTEXT:
✅ memory_blood_pressure_repository.py - DONE
⏳ memory_sleep_cycle_repository.py - NEXT

/drop src/infrastructure/db/memory_blood_pressure_repository.py
/add src/infrastructure/db/memory_sleep_cycle_repository.py

Javítsd az F821 hibákat CSAK ebben a fájlban!
```

**Step 4:**
```
PHASE 4/4: Összefoglalás

STOP! Ne javíts már semmit.

Készíts egy CHANGELOG.md-t:
- Mit javítottunk (commit-ok)
- Mi maradt hátra (remaining issues)
- Következő lépések (action items)

VÉGE.
```

---

## 💡 Pro Tips

### 1. Használj Delimitert (Határolót)

```
════════════════════════════════════════════
  TASK BOUNDARY - CLEAR CONTEXT SWITCH
════════════════════════════════════════════
```

**Vizuálisan** is jelezd az AI-nak hogy új feladat jön!

---

### 2. Echo Pattern (Visszhang)

```
Te: "Javítsd a base_chart.py fájlban az E501 hibákat"

Kérés az AI-tól:
"Mielőtt kezdem, megerősítsd:
- Fájl: base_chart.py
- Feladat: E501 (line too long)
- Scope: CSAK ez az 1 fájl
Helyes?"
```

**→ Kényszerítsd az AI-t hogy megértse a feladatot!**

---

### 3. Micro-commits

```bash
# Config-ban:
auto-commits: false

# Promptban:
"Minden javítás után:
1. Mutasd a diff-et
2. Kérj jóváhagyást
3. CSAK AKKOR commitolj ha OK-t mondok"
```

---

### 4. Context Dump (ha elveszik)

```
EMERGENCY RESET!

1. /clear                          # Töröld a context-et
2. /add [csak a szükséges fájlok]
3. Kezdjük elölről a feladatot:

[újra leírod a feladatot tisztán]
```

---

## 🎓 Összefoglalás

**GLM-4.6 specifikus kihívások:**
- Túl proaktív → **Explicit scope korlátok**
- Elvész a kontextus → **Rendszeres state reminder**
- "Segít" amikor nem kell → **NE utasítások**
- Nagy változások → **Chunk-old kisebbre**

**Aranyszabály:**
> "Egy prompt = Egy fókusz = Egy fájl = Egy commit"

**Ha elveszíted a kontrollt:**
```
/clear
STOP! Új feladat, tiszta lap!
[explicit újrakezdés]
```

---

## 📊 Hatékonyság Mérése

**Előtte (rossz context management):**
- ⏱️ 10 perc alatt 50 fájlt módosított
- 😵 Nem követhető változások
- 💥 Breaking changes
- 🔙 3-4 undo szükséges

**Utána (jó context management):**
- ⏱️ 10 perc alatt 2-3 fájl célzottan
- ✅ Tiszta, követhető commit-ok
- 🎯 Pontosan azt csinálja amit kértél
- ✨ Első próbára működik

---

**Próbáld ki és mondd el milyen eredményt adsz!** 🚀