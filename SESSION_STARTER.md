# 🚀 CODEX SESSION STARTER

**Helló, Codex!** 

Ez egy **VIZSGA feladat**. Clean Architecture pilot - anomaly detection refactor.

---

## 📋 GYORS ELIGAZÍTÁS

### 1. DOKUMENTUMOK (olvasd el sorrendben):
1. **RECONNAISSANCE_REPORT.md** ← Jelenlegi kód audit
2. **CODEX_BRIEF_V2_FINAL.md** ← Feladatleírás (TELJES)
3. **QUICK_REFERENCE_CARD.md** ← Gyors referencia

### 2. SZABÁLYOK:
- ✅ **AGENTS.md** = szent irat, 100% követendő!
- ✅ Terminal workflow - file-based munka
- ✅ Hungarian, informal - tegeződés
- ✅ Minimal verbosity - kód beszél!
- ✅ Max 250 sor/fájl
- ✅ Coverage >85%, Pylint >8.0

### 3. FELADAT (2 nap):
**Day 1 (4-6 óra):**
- Domain entities + value objects
- Unit tesztek >90%

**Day 2 (4-6 óra):**
- Domain service (PURE logic, ZERO numpy!)
- Unit tesztek >85%

---

## 🎯 ELSŐ LÉPÉS

Kezdd ezzel:

```bash
cd ~/PythonProjects/Jules/global_weather_analyzer
git checkout -b spike/anomaly-domain-extraction

# STATUS.md és PLAN.md létrehozása
# (lásd CODEX_BRIEF_V2_FINAL.md "CODEX WORKFLOW" szekció)
```

Aztán:
1. Olvasd el a dokumentumokat
2. Kérdezz, ha bármi nem világos! (max 2 kérdés)
3. Kezdj neki!

---

## ⚡ GYORS EMLÉKEZTETŐ

**BEFORE (most):**
```
src/gui/results_panel/anomaly_detector.py (549 sor)
└─> Domain logic a GUI-ban! ❌
```

**AFTER (cél - Day 1-2):**
```
src/domain/entities/climate_anomaly.py (150 sor)
src/domain/value_objects/anomaly_threshold.py (200 sor)
src/domain/services/anomaly_detector.py (250 sor)
└─> PURE domain logic! ✅
```

---

## 🚫 KRITIKUS TILALMAK

❌ NO numpy a domain-ben! (használj `sum() / len()`)  
❌ NO truncation! (TELJES fájlok!)  
❌ NO `...` vagy `# TODO`!  
❌ NO >250 sor/fájl!

---

## ✅ SUCCESS CRITERIA

**SPIKE SIKERES:**
- ✅ 3 domain fájl + 3 test fájl
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ Minden teszt ZÖLD
- ✅ Git: 5-6 clean commit

---

**Kérdésed van? Kérdezz! Aztán hajrá! 🚀**
