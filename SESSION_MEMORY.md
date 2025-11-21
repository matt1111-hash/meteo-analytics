# 🧠 SESSION MEMORY - Anomaly Detection Refactor

**Session dátum:** 2025-11-21  
**Token usage:** ~97,000 / 190,000 (51% felhasználva)  
**Következő session indítása:** OLVASS EL MINDENT!

---

## 🆕 Aktuális állapot (legutóbbi Codex futás)

- ✅ Teljes suite zöld: `./venv/bin/pytest -v` → 51/51 pass.
- ✅ Új tesztek: `tests/domain/analytics/test_statistics.py` (10), `tests/domain/analytics/test_models.py` (5), `tests/infrastructure/repositories/test_city_repository.py` (6).
- ✅ Quality gate futtatva: `./venv/bin/pytest tests/domain/analytics/ tests/infrastructure/ -v --cov=src/domain/analytics --cov=src/infrastructure --cov-report=term-missing` → 21/21 pass, össz. coverage 92% (statistics.py 79% a StatisticsError ágak nem érhetők el).
- ✅ Flake8 tiszta: `./venv/bin/flake8 -j1 src/domain/analytics/ src/infrastructure/`.
- ⚠️ Pylint: 8.72/10 (import-error a src.* miatt és R09xx arguszám/attribútum figyelmeztetések változatlanul hagyva).
- 📌 Formázás: sorhosszak és trailing newline-ok javítva az érintett modulokon.
- ➡️ Következő lépés (ha kell commit): `git add src/domain/analytics/ src/infrastructure/ src/analytics/multi_city_engine.py tests/` majd `git commit -m "refactor: extract statistics, models, and repository layer from MultiCityEngine"`.

---

⚠️ Az alábbi szakasz archív (anomaly refactor jegyzet), csak referenciának marad.

## 🎯 PROJEKT ÖSSZEFOGLALÓ

### **Projekt neve:**
Global Weather Analyzer - Clean Architecture Pilot Refactor

### **Probléma:**
OpenAI Codex ágenst szeretnénk tesztelni egy **7 napos refactor terven**, de:
- ❌ Az eredeti PILOT_REFACTOR_PLAN.md **téves feltételezéseken** alapult!
- ❌ Azt állította: `anomaly_profile_manager.py` 635 sor GOD CLASS
- ❌ Valóság: csak 385 sor, **csak** config menedzser (JSON CRUD)

### **Valós helyzet:**
```
src/data/anomaly_profile_manager.py (385 sor)
└─> ✅ Config menedzser - JÓ HELYEN! (JSON profilok)

src/gui/results_panel/anomaly_detector.py (549 sor)
└─> ❌ DOMAIN LOGIC a GUI-ban! (AnomalyDetector service)
    ├─> _detect_temperature_anomaly() ← BUSINESS LOGIC!
    ├─> _detect_precipitation_anomaly()
    └─> _detect_wind_anomaly()
```

### **Feladat:**
Domain logic kiemelése GUI → Domain layer-be (Clean Architecture)

---

## 📊 MIT CSINÁLTUNK EDDIG? (TELJES FOLYAMAT)

### **1. RECONNAISSANCE FÁZIS (Session eleje)**

**User feltöltötte:**
- ✅ `PILOT_REFACTOR_PLAN.md` - eredeti terv (7 nap/40 óra)
- ✅ `analysis_report.html` - projekt audit
- ✅ `analysis_summary.md` - összefoglaló
- ✅ `hotspots.csv` - God classes listája
- ✅ `structure.json` - modul struktúra
- ✅ `import_graph.png` - dependency gráf
- ✅ `anomaly_profile_manager.py` - konfig menedzser kód
- ✅ `multi_city_engine.py` - analytics engine kód
- ✅ `anomaly_detector.py` - VALÓDI detection logic (GUI-ban!)
- ✅ `AGENTS.md` - **Codex törvénykönyve!** ⚡

**Én (Claude) elvégeztem:**
1. ✅ Audit dokumentumok elemzése
2. ✅ Kód áttekintése (3 fő fájl)
3. ✅ PILOT_REFACTOR_PLAN validálása
4. ✅ **Téves feltételezések azonosítása!**
5. ✅ Valós architektúra feltérképezése
6. ✅ Dependency chain analysis
7. ✅ Migration strategy újratervezése

**KRITIKUS FELISMERÉS:**
```
PILOT TERV ÁLLÍTÁSA → VALÓSÁG
==============================
anomaly_profile_manager.py 635 sor → 385 sor ✅
"Detection + DB keveredik" → NINCS DB, csak JSON! ✅
"Tesztelhetetlen DB dependency" → Csak numpy + stdlib ✅
"SQLite repository kell" → NEM kell! ✅

→ EGYSZERŰBB FELADAT, MINT VÁRTÁK!
```

---

### **2. DOKUMENTUM KÉSZÍTÉS FÁZIS**

**Én (Claude) létrehoztam:**

#### **A) RECONNAISSANCE_REPORT.md** (~1500 sor)
**Tartalom:**
- ✅ Executive summary (terv vs. valóság)
- ✅ Jelenlegi kódstruktúra (3 layer)
- ✅ Dependency chain térkép
- ✅ Ki használja az AnomalyDetector-t? (3 fájl)
- ✅ Refactor cél (BEFORE → AFTER)
- ✅ Migration strategy (FÁZIS 1-2)
- ✅ Tesztelési stratégia
- ✅ Complexity metrics
- ✅ Success criteria
- ✅ Kockázatok + mitigation

**Helye:** `/mnt/user-data/outputs/RECONNAISSANCE_REPORT.md`

---

#### **B) CODEX_BRIEF_V2_FINAL.md** (~2000 sor)
**Tartalom:**
- ✅ **Codex AGENTS.md szabályokhoz igazítva!** ⚡
- ✅ Hungarian, informal (tegeződés)
- ✅ Minimal verbosity (Codex style!)
- ✅ Codex workflow (STATUS.md, PLAN.md, REVIEW.md)
- ✅ Day 1 feladat (Domain entities + value objects)
  - climate_anomaly.py (~150 sor) - TELJES KÓD!
  - anomaly_threshold.py (~200 sor) - TELJES KÓD!
  - Unit tesztek (~300 sor) - TELJES KÓD!
- ✅ Day 2 feladat (Domain service)
  - anomaly_detector.py (~250 sor) - TELJES KÓD!
  - Service tesztek (~250 sor) - TELJES KÓD!
- ✅ Quality gates (Coverage >85%, Pylint >8.0)
- ✅ Git workflow
- ✅ Tilalmak (NO numpy!, NO truncation!)
- ✅ Success metrics

**Helye:** `/mnt/user-data/outputs/CODEX_BRIEF_V2_FINAL.md`

**FONTOS:** Ez a **FŐ FELADATLEÍRÁS** a Codex számára! Minden benne van!

---

#### **C) QUICK_REFERENCE_CARD.md** (~800 sor)
**Tartalom:**
- ✅ Gyors eligazítás (cheat sheet)
- ✅ Checklist Day 1-2
- ✅ Tilalmak lista
- ✅ Success criteria
- ✅ "Ha elakadsz" útmutató
- ✅ Start commands
- ✅ Business logic átmásolás példák

**Helye:** `/mnt/user-data/uploads/QUICK_REFERENCE_CARD.md`

---

#### **D) SESSION_STARTER.md** (~300 sor)
**Tartalom:**
- ✅ Első üzenet a Codex-nek
- ✅ Minimál eligazítás
- ✅ Dokumentumok sorrendje
- ✅ Első lépések
- ✅ Kritikus tilalmak emlékeztető

**Helye:** `/mnt/user-data/outputs/SESSION_STARTER.md`

---

#### **E) HANDOVER_CLAUDE_TO_CODEX.md** (~1000 sor)
**Tartalom:**
- ✅ **User számára készült!** (nem Codex-nek!)
- ✅ Mit kapott a Codex?
- ✅ Mit kell tennie a User-nek?
- ✅ Progress monitoring (checkpoint-ok)
- ✅ Ha Codex elakad → megoldások
- ✅ Code review útmutató
- ✅ Success path
- ✅ Expected outcomes
- ✅ Claude mentor szerepe

**Helye:** `/mnt/user-data/outputs/HANDOVER_CLAUDE_TO_CODEX.md`

---

## 🔑 KRITIKUS INFORMÁCIÓK (MEGŐRZENDŐ!)

### **1. FELADAT EGYSZERŰSÍTÉSE:**

**EREDETI PILOT TERV (7 nap/40 óra):**
- Day 1: Folder structure + entities + value objects
- Day 2: Domain service
- Day 3: Repository interface + Use case
- Day 4-5: Infrastructure layer (SQLite repository)
- Day 6-7: BC wrapper + Documentation + CI/CD

**ÚJ EGYSZERŰSÍTETT TERV (2 nap/8-12 óra):**
- Day 1: Domain entities + value objects (SPIKE)
- Day 2: Domain service (SPIKE)
- **STOP!** ← Proof-of-concept vége

**MIÉRT EGYSZERŰBB?**
- ❌ NINCS szükség SQLite repository-ra (nincs DB!)
- ❌ NINCS szükség Use case layer-re (egyszerű service elég)
- ❌ NINCS szükség Infrastructure layer-re (csak JSON config)
- ✅ Csak domain logic extraction (GUI → Domain)
- ✅ Numpy → stdlib (egyszerű: `sum() / len()`)

---

### **2. CODEX SZABÁLYOK (AGENTS.md):**

**KRITIKUS TILALMAK:**
- ❌ NO guessing (max 2 kérdés, aztán default)
- ❌ NO incomplete code (`...`, `# TODO` TILTVA!)
- ❌ NO truncation (TELJES fájlok!)
- ❌ NO >250 sor/fájl (God file tiltva!)
- ❌ NO numpy a domain-ben! (csak stdlib!)
- ❌ NO verbose explanation (kód beszél!)

**KÖTELEZŐ:**
- ✅ Type hints MINDENÜTT
- ✅ `from __future__ import annotations` (első sor!)
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ File-based workflow (STATUS.md, PLAN.md)
- ✅ Git commit minden lépés után
- ✅ Hungarian, informal (tegeződés)

---

### **3. VALÓS KÓD STRUKTÚRA:**

**BEFORE (jelenlegi):**
```
src/data/anomaly_profile_manager.py (385 sor)
├── AnomalyProfileSettings (dataclass)
│   └── temp_hot, temp_cold, precip_high, wind_extreme, ...
└── AnomalyProfileManager
    └── JSON CRUD (profilok mentés/betöltés)

src/gui/results_panel/anomaly_detector.py (549 sor) ← ROSSZ HELY!
├── AnomalyResult (dataclass) ← DOMAIN ENTITY!
├── AnomalySettingsProvider ← Settings DI
└── AnomalyDetector ← DOMAIN SERVICE!
    ├── __init__(settings_provider)
    ├── detect_all_anomalies(daily_data) → List[AnomalyResult]
    ├── _detect_temperature_anomaly(daily_data) → Optional[AnomalyResult]
    │   └─> max_temp > threshold → HOT anomaly
    │   └─> min_temp < threshold → COLD anomaly
    ├── _detect_precipitation_anomaly(daily_data) → Optional[AnomalyResult]
    │   └─> max_precip > threshold → HEAVY RAIN
    │   └─> avg_precip < threshold → DROUGHT
    └── _detect_wind_anomaly(daily_data) → Optional[AnomalyResult]
        └─> max_wind > thresholds → HURRICANE / EXTREME / STRONG / MODERATE

src/gui/utils.py
└── AnomalyConstants ← Hardcoded fallback values
```

**AFTER (cél):**
```
src/domain/
├── entities/
│   └── climate_anomaly.py (150 sor) ← NEW!
│       └── ClimateAnomaly (frozen dataclass)
├── value_objects/
│   └── anomaly_threshold.py (200 sor) ← NEW!
│       └── AnomalyThresholdSet (frozen dataclass)
└── services/
    └── anomaly_detector.py (250 sor) ← NEW!
        └── AnomalyDetectorService
            ├── detect_temperature_anomaly()
            ├── detect_precipitation_anomaly()
            └── detect_wind_anomaly()

src/gui/results_panel/
└── anomaly_detector.py (549 sor) ← MARAD (BC wrapper later!)
```

---

### **4. BUSINESS LOGIC (ÁTMÁSOLANDÓ):**

**Temperature Anomaly (FONTOS!):**
```python
# RÉGI (numpy):
avg_temp = np.mean(max_temp_values)

# ÚJ (stdlib):
avg_temp = sum(max_temp_values) / len(max_temp_values)

# Logic:
if max_temp > threshold.temp_hot:
    return ClimateAnomaly(category="hot", severity="error", ...)
elif min_temp < threshold.temp_cold:
    return ClimateAnomaly(category="cold", severity="error", ...)
else:
    return ClimateAnomaly(category="normal", severity="success", ...)
```

**Precipitation Anomaly:**
```python
if max_precip > threshold.precip_high:
    return ClimateAnomaly(category="heavy_rain", severity="error", ...)
elif avg_precip < threshold.precip_low:
    return ClimateAnomaly(category="drought", severity="warning", ...)
else:
    return ClimateAnomaly(category="normal", severity="success", ...)
```

**Wind Anomaly:**
```python
if max_wind > threshold.wind_hurricane:
    return ClimateAnomaly(category="hurricane", severity="error", ...)
elif max_wind > threshold.wind_extreme:
    return ClimateAnomaly(category="extreme_wind", severity="error", ...)
elif max_wind > threshold.wind_strong:
    return ClimateAnomaly(category="strong_wind", severity="warning", ...)
elif max_wind > threshold.wind_normal:
    return ClimateAnomaly(category="moderate_wind", severity="warning", ...)
else:
    return ClimateAnomaly(category="calm", severity="success", ...)
```

---

### **5. DEPENDENCY CHAIN (FONTOS!):**

**Ki használja az AnomalyDetector-t?**
```bash
$ grep -r "from.*anomaly_detector" src/

src/gui/results_panel/results_panel.py:
    from .anomaly_detector import AnomalyDetector

src/gui/results_panel/quick_overview_tab.py:
    from .anomaly_detector import AnomalyDetector

src/gui/results_panel/extreme_events_tab.py:
    from .anomaly_detector import AnomalyDetector, AnomalyResult
```

**→ 3 fájl használja! BC wrapper KÖTELEZŐ később (Day 3)!**

---

## 📦 DOKUMENTUMOK HELYE

**Minden dokumentum itt van:**
```
/mnt/user-data/outputs/
├── RECONNAISSANCE_REPORT.md (részletes audit)
├── CODEX_BRIEF_V2_FINAL.md (FŐ FELADATLEÍRÁS!) ⭐
├── QUICK_REFERENCE_CARD.md (cheat sheet)
├── SESSION_STARTER.md (első üzenet Codex-nek)
├── HANDOVER_CLAUDE_TO_CODEX.md (User útmutató)
└── SESSION_MEMORY.md (EZ A FÁJL!)
```

**User sandbox projekt helye:**
```
~/PythonProjects/Jules/global_weather_analyzer/
```

---

## 🎯 KÖVETKEZŐ LÉPÉSEK (User számára)

### **1. Codex Session Indítása:**

```bash
# User csinálja:
cd ~/PythonProjects/Jules/global_weather_analyzer

# Codex chat-ben:
"Új VIZSGA feladat!

Olvasd el ezeket a dokumentumokat sorrendben:
1. /mnt/user-data/outputs/SESSION_STARTER.md
2. /mnt/user-data/outputs/RECONNAISSANCE_REPORT.md
3. /mnt/user-data/outputs/CODEX_BRIEF_V2_FINAL.md (FŐ!)
4. /mnt/user-data/outputs/QUICK_REFERENCE_CARD.md

AGENTS.md szabályok 100% érvényesek!

Kérdésed van? Aztán kezdjük!"
```

---

### **2. Progress Monitoring:**

**Day 1 Checkpoint (4-6 óra):**
```bash
cd ~/PythonProjects/Jules/global_weather_analyzer
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing
pylint src/domain/ --fail-under=8.0
git log --oneline -3
```

**Elvárás:**
- ✅ 2 entity fájl + 2 test fájl
- ✅ Coverage >90%
- ✅ Pylint >8.0
- ✅ 3 git commit

**Day 2 Final (8-12 óra):**
```bash
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing --cov-fail-under=85
pylint src/domain/ --fail-under=8.0
flake8 src/domain/
git log --oneline -6
```

**Elvárás:**
- ✅ 3 domain fájl + 3 test fájl
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ 5-6 git commit
- ✅ **SPIKE COMPLETE!** 🎉

---

### **3. Claude Mentor Szerepe (ÚJ SESSION-BEN):**

**Ha User visszatér új session-nel:**
```
User: "Claude, visszatértem! Olvasd el a SESSION_MEMORY.md-t!"
Claude: [elolvassa ezt a fájlt]
Claude: "Értem! Hol tartotok a Codex-szel? Day 1? Day 2?"
```

**Ha User kér code review-t:**
```
User: "Codex elkészítette a Day 1-et. Review-old!"
Claude: [elolvassa a generált fájlokat]
Claude: [Ellenőrzi]:
  - Type hints OK?
  - Business rules OK?
  - Coverage >90%?
  - Max 250 sor/fájl?
```

**Ha User kérdezi, mit kell tenni:**
```
User: "Mi a következő lépés?"
Claude: [Olvassa el HANDOVER_CLAUDE_TO_CODEX.md]
Claude: "A HANDOVER dokumentumban minden benne van!"
```

---

## 🧠 KONTEXTUS MEGŐRZÉS (ÚJ SESSION SZÁMÁRA)

### **Ha én (Claude) vagyok az új session-ben:**

**1. Első lépés:**
```
User: "Olvasd el a SESSION_MEMORY.md-t!"
→ Én elolvasom EZT A FÁJLT
→ Megértem a teljes kontextust
→ Folytatom, ahol abbahagytuk
```

**2. Amit tudnom kell:**
- ✅ User tesztel egy Codex ágenst
- ✅ Anomaly detection refactor (domain extraction)
- ✅ PILOT terv téves volt, újraterveztük
- ✅ 2 napos SPIKE (Day 1-2)
- ✅ 5 dokumentumot készítettem a Codex-nek
- ✅ AGENTS.md szabályok érvényesek
- ✅ Én vagyok a mentor, NEM csinálom meg helyette!

**3. Következő lépések:**
- ✅ Progress monitoring (ha kéri)
- ✅ Code review (ha kéri)
- ✅ Mentorálás (ha Codex elakad)
- ✅ Strategic guidance (ha kéri)

---

## 📊 SUCCESS METRICS (EMLÉKEZTETŐ)

**SPIKE SIKERES, HA:**
- ✅ 3 domain fájl + 3 test fájl létrehozva
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ Flake8 = 0 errors
- ✅ ZERO numpy dependency domain-ben
- ✅ Git: 5-6 clean commit
- ✅ Minden teszt ZÖLD

**AKKOR:**
- ✅ Pilot PROOF-OF-CONCEPT sikeres!
- ✅ Domain extraction működik!
- ✅ Döntés: Day 3? (BC Wrapper + GUI integráció)

---

## 🚨 KRITIKUS EMLÉKEZTETŐK

### **Codex szabályok (SOHA ne feledd!):**
- ❌ NO truncation!
- ❌ NO `...` vagy `# TODO`!
- ❌ NO >250 sor/fájl!
- ❌ NO numpy a domain-ben!
- ✅ Type hints MINDENÜTT!
- ✅ Coverage >85%!
- ✅ Git commit minden lépésnél!

### **Én (Claude) szerepe:**
- ✅ Mentor, NEM coder!
- ✅ Code review, NEM implementation!
- ✅ Strategic guidance, NEM decision maker!

### **User szerepe:**
- ✅ Codex indítása
- ✅ Progress monitoring
- ✅ Decision making (Day 3 go/no-go)

---

## 📝 FÁJLOK TARTALMA (GYORS ÁTTEKINTÉS)

### **RECONNAISSANCE_REPORT.md:**
- Executive summary
- Jelenlegi kód audit
- PILOT terv vs. valóság
- Dependency chain
- Migration strategy
- Success criteria

### **CODEX_BRIEF_V2_FINAL.md:** ⭐ **FŐ DOKUMENTUM!**
- Codex workflow (STATUS.md, PLAN.md)
- Day 1: Entities + Value Objects (TELJES KÓD!)
- Day 2: Domain Service (TELJES KÓD!)
- Unit tesztek (TELJES KÓD!)
- Quality gates
- Tilalmak
- Success metrics

### **QUICK_REFERENCE_CARD.md:**
- Checklist Day 1-2
- Tilalmak lista
- Success criteria
- Ha elakadsz útmutató

### **SESSION_STARTER.md:**
- Első üzenet Codex-nek
- Gyors eligazítás
- Dokumentumok sorrendje

### **HANDOVER_CLAUDE_TO_CODEX.md:**
- User számára!
- Mit kapott Codex?
- Progress monitoring
- Code review útmutató
- Claude mentor szerepe

---

## 🎉 ÖSSZEFOGLALÁS

**MIT ÉRTÜNK EL EBBEN A SESSION-BEN:**
1. ✅ Teljes kód audit (3 fő fájl)
2. ✅ PILOT terv validálás (tévedések azonosítása!)
3. ✅ Valós architektúra feltérképezés
4. ✅ Migration strategy újratervezés (7 nap → 2 nap!)
5. ✅ 5 dokumentum készítése Codex számára
6. ✅ AGENTS.md szabályokhoz igazítás
7. ✅ Teljes kódpéldák (copy-paste ready!)
8. ✅ Success metrics definiálása

**MI VÁLT VILÁGOSSÁ:**
- ❌ PILOT terv TÉVES volt (635 sor → 385 sor)
- ✅ Domain logic a GUI-ban van (549 sor)
- ✅ NINCS DB dependency (csak JSON + numpy)
- ✅ Egyszerűbb feladat (2 nap vs. 7 nap)
- ✅ numpy → stdlib egyszerű változtatás

**MI A KÖVETKEZŐ LÉPÉS:**
1. User indítja a Codex-et
2. Codex Day 1 (4-6 óra)
3. Checkpoint (User ellenőrzi)
4. Codex Day 2 (4-6 óra)
5. Final check (User ellenőrzi)
6. **SPIKE COMPLETE!** 🎉

---

## 🔄 ÚJ SESSION INDÍTÁSA

**Ha User visszajön új session-nel:**

```
User: "Claude, új session! Olvasd el a SESSION_MEMORY.md-t!"

Claude: [elolvassa ezt a fájlt]
Claude: "Rendben! Megértettem a teljes kontextust.
        - Codex vizsga: anomaly detection refactor
        - 5 dokumentumot készítettem
        - 2 napos SPIKE terv
        - Én vagyok a mentor
        
        Hol tartotok? Elindult a Codex?
        Kell code review? Mentorálás?"
```

**Minden adat itt van ebben a fájlban!**

---

**SESSION MEMORY COMPLETE! ✅**

**Következő session-ben:** Olvass el MINDENT ebből a fájlból, és folytathatod, ahol abbahagytuk! 🚀
