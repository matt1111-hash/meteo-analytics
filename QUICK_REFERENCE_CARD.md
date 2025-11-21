# 🚀 QUICK REFERENCE CARD - Anomaly Detection Refactor

## 📁 FÁJLOK HELYE (Sandbox)

```
~/PythonProjects/Jules/global_weather_analyzer/  ← TESZT SANDBOX!

LÉTEZŐ FÁJLOK (NE NYÚLJ HOZZÁ!):
├── src/data/anomaly_profile_manager.py (385 sor) ← Config menedzser
├── src/gui/results_panel/anomaly_detector.py (549 sor) ← ROSSZ HELYEN!
└── src/gui/utils.py ← AnomalyConstants

LÉTREHOZANDÓ FÁJLOK (Te csinálod!):
└── src/domain/
    ├── entities/
    │   └── climate_anomaly.py ← Day 1
    ├── value_objects/
    │   └── anomaly_threshold.py ← Day 1
    └── services/
        └── anomaly_detector.py ← Day 2
```

---

## 🎯 FELADAT - 2 NAPOS SPIKE

### **Day 1 (4-6 óra):**
1. Folder structure setup
2. `climate_anomaly.py` ← Domain Entity
3. `anomaly_threshold.py` ← Value Object
4. Unit tesztek >90%
5. Git commit

### **Day 2 (4-6 óra):**
1. `anomaly_detector.py` ← Domain Service
2. PURE logic (ZERO numpy!)
3. Unit tesztek >85%
4. Git commit

---

## 🚫 TILALMAK

❌ **NE HASZNÁLJ:**
- numpy / pandas / external deps a domain-ben
- Mock / demo adatokat
- `...` a kódban (TELJES fájlok!)

❌ **NE NYÚLJ:**
- GUI fájlokhoz (Day 3-ig)
- Éles projekthez
- Meglévő tesztekhez (ne törj el semmit!)

✅ **CSAK EZEKET HASZNÁLD:**
- Python stdlib (sum, min, max, len, sorted)
- datetime, dataclass, typing
- Domain objects (ClimateAnomaly, AnomalyThresholdSet)

---

## 📋 CHECKLIST - DAY 1

```bash
# 1. Git branch
git checkout -b spike/anomaly-domain-extraction

# 2. Folder structure
mkdir -p src/domain/entities
mkdir -p src/domain/value_objects
mkdir -p src/domain/services
mkdir -p tests/domain

touch src/domain/__init__.py
touch src/domain/entities/__init__.py
touch src/domain/value_objects/__init__.py
touch src/domain/services/__init__.py

# 3. Create files
# climate_anomaly.py (~150 sor)
# anomaly_threshold.py (~200 sor)

# 4. Create tests
# tests/domain/test_climate_anomaly.py
# tests/domain/test_anomaly_threshold.py

# 5. Run tests
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing

# 6. Git commit
git add src/domain/ tests/domain/
git commit -m "feat(domain): Add ClimateAnomaly entity and AnomalyThresholdSet value object"
```

---

## 📋 CHECKLIST - DAY 2

```bash
# 1. Create domain service
# src/domain/services/anomaly_detector.py (~300 sor)

# 2. Create tests
# tests/domain/test_anomaly_detector_service.py

# 3. Run tests
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing

# 4. Check coverage
# MINIMUM: 85%

# 5. Git commit
git add src/domain/services/ tests/domain/
git commit -m "feat(domain): Add AnomalyDetectorService with pure business logic"
```

---

## 🔍 BUSINESS LOGIC ÁTMÁSOLÁS

**FORRÁS (régi):** `src/gui/results_panel/anomaly_detector.py`

**CÉL (új):** `src/domain/services/anomaly_detector.py`

### **Hőmérséklet anomália:**
```python
# RÉGI (numpy-s):
avg_temp = np.mean(max_temp_values)

# ÚJ (stdlib):
avg_temp = sum(max_temp_values) / len(max_temp_values)
```

### **Csapadék anomália:**
```python
# RÉGI:
avg_precip = np.mean(precip_values)

# ÚJ:
avg_precip = sum(precip_values) / len(precip_values)
```

### **Szél anomália:**
```python
# RÉGI:
avg_wind = np.mean(wind_values)

# ÚJ:
avg_wind = sum(wind_values) / len(wind_values)
```

---

## 🧪 TESZTELÉSI TEMPLATE

```python
def test_detect_extreme_heat():
    """Test extreme heat detection."""
    thresholds = AnomalyThresholdSet(temp_hot=35.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Budapest",
        analysis_date=date(2024, 7, 15),
        max_temps=[42.5, 38.2, 45.1],
        min_temps=[25.0, 22.0, 28.0]
    )
    
    assert result is not None
    assert result.category == "hot"
    assert result.severity == "error"
    assert result.measured_value == 45.1
    assert result.is_extreme
```

---

## ✅ SUCCESS METRICS

### **SPIKE SIKERES:**
- [ ] `climate_anomaly.py` létrehozva + tesztek
- [ ] `anomaly_threshold.py` létrehozva + tesztek
- [ ] `anomaly_detector.py` létrehozva + tesztek
- [ ] Coverage >85%
- [ ] MINDEN teszt ZÖLD
- [ ] Git history: 2-3 clean commit

### **SPIKE FAIL:**
- [ ] Tesztek nem futnak
- [ ] Coverage <70%
- [ ] numpy/pandas dependency
- [ ] Félbehagyott fájlok

---

## 🆘 HA ELAKADTÁL

1. **Nézd meg a CODEX_BRIEF.md-t** - teljes code példák!
2. **Nézd meg a RECONNAISSANCE_REPORT.md-t** - jelenlegi kód audit!
3. **Kérdezz Claude-ot** (mentor)!
4. **Check git status** - commitoltad-e az eddigi munkát?

---

## 📊 ELVÁRÁSOK

**Időkeret:**
- Day 1: 4-6 óra
- Day 2: 4-6 óra
- **ÖSSZESEN: 8-12 óra**

**Kód minőség:**
- Type hints MINDENÜTT
- Docstringek MINDENÜTT
- Business rules DOKUMENTÁLVA
- Error handling ROBUSZTUS

**Tesztelés:**
- Happy path ✅
- Edge cases ✅
- Invalid input ✅
- None handling ✅

---

## 🎓 FILOZÓFIA

> **"Működő spike, nem perfekt architektúra!"**

- SPIKE = gyors proof-of-concept
- NEM kell perfekt kód
- NEM kell minden edge case lefedni
- NEM kell dokumentáció (csak docstring)

**Cél:** Bebizonyítani, hogy a domain extraction működik!

---

## 🚀 START COMMANDS

```bash
# 1. Navigálj a projektbe
cd ~/PythonProjects/Jules/global_weather_analyzer

# 2. Git branch
git checkout -b spike/anomaly-domain-extraction

# 3. Kezdjünk!
mkdir -p src/domain/entities src/domain/value_objects src/domain/services tests/domain
touch src/domain/__init__.py src/domain/entities/__init__.py

# 4. HAJRÁ! 🚀
```

---

**Spike indítás dátuma:** [____-__-__]  
**Várható befejezés:** [____-__-__]  

**Codex, hajrá! Te tudod! 💪**
