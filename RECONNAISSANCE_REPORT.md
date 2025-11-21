# 🔍 RECONNAISSANCE REPORT - Anomaly Detection Refactor

**Dátum:** 2025-11-21  
**Cél:** Clean Architecture pilot - Anomaly detection audit  
**Audit eszközök:** ultimate_project_analyzer, grep, manual code review  

---

## 📊 EXECUTIVE SUMMARY

**FELFEDEZÉS:** Az eredeti PILOT_REFACTOR_PLAN **téves feltételezéseken** alapult!

| **PILOT TERV állítása** | **VALÓSÁG** | **Impact** |
|-------------------------|-------------|------------|
| `anomaly_profile_manager.py` 635 sor GOD CLASS | 385 sor, CSAK config menedzser | ✅ Kisebb refactor! |
| "Anomaly detection algorithm + DB keveredés" | Detection logic **GUI-ban** van! | ❌ Más a probléma! |
| "Tesztelhetetlen DB dependency" | Csak JSON + numpy számítás | ✅ Könnyebb lesz! |
| SQLite repository szükséges | **NEM** kell DB layer! | ✅ Egyszerűbb! |

---

## 🗂️ JELENLEGI KÓD STRUKTÚRA

### **1. CONFIG LAYER** ✅ (Jó helyen van!)

**Fájl:** `src/data/anomaly_profile_manager.py` (385 sor)

```python
@dataclass
class AnomalyProfileSettings:
    """Anomaly profilok beállításai."""
    # Hőmérséklet küszöbök
    temp_hot: float = 35.0
    temp_cold: float = -10.0
    
    # Csapadék küszöbök
    precip_high: float = 100.0
    precip_low: float = 5.0
    
    # Szél küszöbök
    wind_normal: float = 50.0
    wind_strong: float = 70.0
    wind_extreme: float = 100.0
    wind_hurricane: float = 120.0
    
    # Metaadatok
    profile_name: str = "default"
    created_at: str = ""
    modified_at: str = ""
    description: str = ""

class AnomalyProfileManager:
    """
    Profil menedzsment - JSON alapú persistence.
    
    FELELŐSSÉG:
    ✅ Profilok CRUD (create, read, update, delete)
    ✅ JSON file mentés/betöltés
    ✅ Predefined profilok (default, tropical, arctic, continental, mediterranean)
    ✅ Aktív profil tracking
    ✅ Thread-safe file operations
    
    NINCS BENNE:
    ❌ Anomaly detection logic!
    ❌ Database operations!
    ❌ Weather data processing!
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("data/user_preferences")
        self.profiles_file = self.config_dir / "anomaly_profiles.json"
        ...
    
    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Profil betöltése JSON-ból."""
        ...
    
    def save_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool:
        """Profil mentése JSON-ba."""
        ...
    
    def get_available_profiles(self) -> List[str]:
        """Elérhető profil nevek listája."""
        ...
    
    def set_active_profile(self, profile_name: str) -> bool:
        """Aktív profil beállítása."""
        ...
```

**ÉRTÉKELÉS:**
- ✅ Jól strukturált (dataclass + manager)
- ✅ Thread-safe
- ✅ Clean separation (config management ONLY)
- ⚠️ De a domain logic máshol van!

**FÜGGÉSEK:**
```
Ca (Afferent): 2 modul ⬅️ használja
Ce (Efferent): 0 modul ➡️ nem függ senkitől
Instability: 0.00 (Maximálisan stabil!)
```

---

### **2. DETECTION LOGIC** ❌ (ROSSZ HELYEN!)

**Fájl:** `src/gui/results_panel/anomaly_detector.py` (549 sor)

```python
@dataclass
class AnomalyResult:
    """
    Anomály detektálás eredménye.
    🔥 Ez egy DOMAIN ENTITY! DE a GUI rétegben van! ❌
    """
    category: str  # "temperature", "precipitation", "wind"
    message: str  # "🔥 Extrém hőség: 42.5°C"
    status: str  # 'success', 'warning', 'error', 'disabled'
    value: Optional[float] = None
    threshold: Optional[float] = None
    details: Optional[str] = None

class AnomalySettingsProvider:
    """
    Settings provider - DEPENDENCY INJECTION pattern.
    ✅ Jó design! DE a GUI rétegben van! ❌
    """
    
    def __init__(self, initial_settings: Optional[Dict[str, Any]] = None):
        self._settings = initial_settings or self._get_default_settings()
        self._validate_settings()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """Real-time settings frissítés."""
        ...
    
    def get_temp_hot_threshold(self) -> float:
        """Meleg hőmérséklet küszöb."""
        return float(self._settings.get("temp_hot", AnomalyConstants.TEMP_HOT_THRESHOLD))
    
    # ... további getter methodok

class AnomalyDetector:
    """
    🔥 VALÓDI DETECTION LOGIC - DOMAIN SERVICE!
    DE a GUI rétegben van! ❌ Clean Architecture sértés!
    """
    
    def __init__(self, settings_provider: Optional[AnomalySettingsProvider] = None):
        self.settings_provider = settings_provider or AnomalySettingsProvider()
    
    def detect_all_anomalies(self, daily_data: Dict[str, List]) -> List[AnomalyResult]:
        """
        Összes anomália detektálása.
        
        Args:
            daily_data: {
                'temperature_2m_max': [42.5, 38.2, ...],
                'temperature_2m_min': [25.1, 22.3, ...],
                'precipitation_sum': [0.0, 125.5, ...],
                'wind_speed_10m_max': [15.2, 85.3, ...]
            }
        
        Returns:
            List[AnomalyResult]
        """
        results = []
        
        # Hőmérséklet anomáliák
        temp_anomaly = self._detect_temperature_anomaly(daily_data)
        if temp_anomaly:
            results.append(temp_anomaly)
        
        # Csapadék anomáliák
        precip_anomaly = self._detect_precipitation_anomaly(daily_data)
        if precip_anomaly:
            results.append(precip_anomaly)
        
        # Szél anomáliák
        wind_anomaly = self._detect_wind_anomaly(daily_data)
        if wind_anomaly:
            results.append(wind_anomaly)
        
        return results
    
    def _detect_temperature_anomaly(self, daily_data: Dict[str, List]) -> Optional[AnomalyResult]:
        """
        Hőmérséklet anomália detektálás - PURE BUSINESS LOGIC!
        
        Business Rules:
        - max_temp > temp_hot_threshold → HOT anomaly (error)
        - min_temp < temp_cold_threshold → COLD anomaly (error)
        - Otherwise → NORMAL (success)
        """
        try:
            hot_threshold = self.settings_provider.get_temp_hot_threshold()
            cold_threshold = self.settings_provider.get_temp_cold_threshold()
            
            # Max temps
            max_temps = daily_data.get('temperature_2m_max', [])
            max_temp_values = [float(t) for t in max_temps if t is not None]
            
            # Min temps
            min_temps = daily_data.get('temperature_2m_min', [])
            min_temp_values = [float(t) for t in min_temps if t is not None]
            
            if not max_temp_values or not min_temp_values:
                return None
            
            max_temp = max(max_temp_values)
            min_temp = min(min_temp_values)
            avg_temp = np.mean(max_temp_values)  # ⚠️ numpy dependency!
            
            # HOT anomaly
            if max_temp > hot_threshold:
                return AnomalyResult(
                    category="temperature",
                    message=f"🔥 Extrém hőség: {max_temp:.1f}°C",
                    status="error",
                    value=max_temp,
                    threshold=hot_threshold,
                    details=f"Maximum hőmérséklet meghaladja a {hot_threshold}°C küszöböt"
                )
            
            # COLD anomaly
            elif min_temp < cold_threshold:
                return AnomalyResult(
                    category="temperature",
                    message=f"❄️ Extrém hideg: {min_temp:.1f}°C",
                    status="error",
                    value=min_temp,
                    threshold=cold_threshold,
                    details=f"Minimum hőmérséklet alatta a {cold_threshold}°C küszöbnek"
                )
            
            # NORMAL
            else:
                return AnomalyResult(
                    category="temperature",
                    message=f"🌡️ Normális: {avg_temp:.1f}°C átlag",
                    status="success",
                    value=avg_temp,
                    details=f"Hőmérséklet a normál tartományban"
                )
        
        except Exception as e:
            logger.error(f"🌡️ Hőmérséklet anomália detektálási hiba: {e}")
            return None
    
    def _detect_precipitation_anomaly(self, daily_data: Dict[str, List]) -> Optional[AnomalyResult]:
        """
        Csapadék anomália detektálás.
        
        Business Rules:
        - max_precip > precip_high_threshold → HEAVY RAIN (error)
        - avg_precip < precip_low_threshold → DROUGHT (warning)
        - Otherwise → NORMAL (success)
        """
        # ... hasonló logika
    
    def _detect_wind_anomaly(self, daily_data: Dict[str, List]) -> Optional[AnomalyResult]:
        """
        Szél anomália detektálás.
        
        Business Rules:
        - max_wind > hurricane_threshold → HURRICANE (error)
        - max_wind > extreme_threshold → EXTREME WIND (error)
        - max_wind > strong_threshold → STRONG WIND (warning)
        - max_wind > normal_threshold → MODERATE WIND (warning)
        - Otherwise → CALM (success)
        """
        # ... hasonló logika
```

**ÉRTÉKELÉS:**
- ✅ Jó design (dependency injection, settings provider)
- ✅ Tiszta business logic
- ✅ Validációval ellátott
- ❌ **DE a GUI rétegben van!** Clean Architecture SÉRTÉS!
- ⚠️ numpy dependency (de könnyen lecserélhető Python stdlib-re)

**FÜGGÉSEK:**
```python
# Import chain
from ...utils import AnomalyConstants
# ↓
from src.gui.utils import AnomalyConstants
```

---

### **3. CONSTANTS LAYER**

**Fájl:** `src/gui/utils.py` (részlet)

```python
class AnomalyConstants:
    """
    Anomaly detection konstansok - HARDCODED fallback értékek.
    ⚠️ Ez is a GUI rétegben van!
    """
    # Temperature thresholds
    TEMP_HOT_THRESHOLD = 35.0  # °C
    TEMP_COLD_THRESHOLD = -10.0  # °C
    
    # Precipitation thresholds
    PRECIP_HIGH_THRESHOLD = 100.0  # mm/day
    PRECIP_LOW_THRESHOLD = 5.0  # mm/day
    
    # Wind thresholds
    WIND_HIGH_THRESHOLD = 70.0  # km/h
    WIND_EXTREME_THRESHOLD = 100.0  # km/h
    WIND_HURRICANE_THRESHOLD = 120.0  # km/h
```

---

## 🔗 DEPENDENCY CHAIN

```
GUI Layer
  └─> src/gui/results_panel/anomaly_detector.py (549 sor)
      ├─> AnomalyResult (dataclass) ← 🔥 DOMAIN ENTITY!
      ├─> AnomalySettingsProvider ← Settings DI
      └─> AnomalyDetector ← 🔥 DOMAIN SERVICE!
          └─> from ...utils import AnomalyConstants
              └─> src/gui/utils.py

Config Layer
  └─> src/data/anomaly_profile_manager.py (385 sor)
      ├─> AnomalyProfileSettings (dataclass)
      └─> AnomalyProfileManager
          └─> JSON file CRUD
```

**PROBLÉMA:**
- Domain logic (AnomalyDetector) a GUI rétegben van! ❌
- Domain entity (AnomalyResult) a GUI rétegben van! ❌
- Constants a GUI utils-ban! ❌

---

## 🎯 REFACTOR CÉL - TISZTÁZVA

### **BEFORE (Current):**
```
src/gui/results_panel/anomaly_detector.py
├── AnomalyResult ← DOMAIN ENTITY!
├── AnomalySettingsProvider ← Settings DI
└── AnomalyDetector ← DOMAIN SERVICE!
```

### **AFTER (Target):**
```
src/domain/
├── entities/
│   └── climate_anomaly.py ← ClimateAnomaly
├── value_objects/
│   └── anomaly_threshold.py ← AnomalyThresholdSet
└── services/
    └── anomaly_detector.py ← AnomalyDetectorService

src/gui/results_panel/
└── anomaly_detector.py ← DEPRECATED WRAPPER (BC)
```

---

## 📦 KI HASZNÁLJA AZ ANOMALY_DETECTOR-T?

**Grep eredmények:**

```bash
$ grep -r "from.*anomaly_detector" src/ --include="*.py"

src/gui/results_panel/results_panel.py:
    from .anomaly_detector import AnomalyDetector, create_anomaly_detector_with_settings

src/gui/results_panel/quick_overview_tab.py:
    from .anomaly_detector import AnomalyDetector

src/gui/results_panel/extreme_events_tab.py:
    from .anomaly_detector import AnomalyDetector, AnomalyResult
```

**KÖVETKEZMÉNY:**
- **3 fájl** használja közvetlenül!
- Backward compatibility wrapper KÖTELEZŐ!
- BC wrapper delegál az új domain service-re

---

## 🚧 MIGRATION STRATEGY

### **FÁZIS 1: SPIKE (2 nap) - PROOF OF CONCEPT**

**Cél:** Bebizonyítani, hogy a domain extraction működik!

```
Day 1: Domain entities + value objects
  ✅ src/domain/entities/climate_anomaly.py
  ✅ src/domain/value_objects/anomaly_threshold.py
  ✅ Unit tesztek >90%

Day 2: Domain service
  ✅ src/domain/services/anomaly_detector.py
  ✅ PURE logic (ZERO numpy!)
  ✅ Unit tesztek >85%
```

**STOP PONT:** Ha a spike sikeres → folytatás FÁZIS 2-re

---

### **FÁZIS 2: BC WRAPPER (1 nap) - HA SPIKE ✅**

```
Day 3: Backward compatibility
  ✅ src/gui/results_panel/anomaly_detector.py
      → DEPRECATED wrapper
      → Delegál az új domain service-re
      → Meglévő GUI kód VÁLTOZATLAN működik!
  
  ✅ Integration tesztek
  ✅ Regression testing
```

---

## 🧪 TESZTELÉSI STRATÉGIA

### **UNIT TESZTEK (Domain layer):**
```bash
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing

# Elvárás:
# - Coverage >85%
# - ZERO external dependencies
# - Determinisztikus eredmények
```

### **INTEGRATION TESZTEK (BC wrapper):**
```bash
pytest tests/integration/test_anomaly_bc_wrapper.py -v

# Elvárás:
# - Meglévő GUI kód működik
# - Deprecation warning látható
# - Eredmények azonosak az új + régi implementációval
```

---

## 📊 COMPLEXITY METRICS

### **JELENLEGI (BEFORE):**
```
anomaly_detector.py (549 sor):
├── AnomalyResult: 7 LOC
├── AnomalySettingsProvider: 78 LOC
└── AnomalyDetector: 327 LOC
    ├── __init__: 8 LOC
    ├── detect_all_anomalies: 31 LOC
    ├── _detect_temperature_anomaly: 98 LOC
    ├── _detect_precipitation_anomaly: 92 LOC
    └── _detect_wind_anomaly: 98 LOC

Ciklomatikus komplexitás: CC=1 (alacsony!)
Instability: N/A (GUI rétegben)
```

### **CÉLÁLLAPOT (AFTER):**
```
src/domain/entities/climate_anomaly.py (~150 sor):
└── ClimateAnomaly: 150 LOC, CC=1

src/domain/value_objects/anomaly_threshold.py (~200 sor):
└── AnomalyThresholdSet: 200 LOC, CC=1

src/domain/services/anomaly_detector.py (~300 sor):
└── AnomalyDetectorService: 300 LOC, CC=1
    ├── detect_temperature_anomaly: ~80 LOC
    ├── detect_precipitation_anomaly: ~80 LOC
    └── detect_wind_anomaly: ~80 LOC

Összesen: ~650 sor domain logic (tiszta, tesztelhető)
Instability: I=0.0 (stabil domain core!)
```

---

## 🎯 SUCCESS CRITERIA

### **SPIKE SIKERES, HA:**
- ✅ Domain entities + value objects létrehozva
- ✅ Domain service PURE logic (ZERO numpy!)
- ✅ Unit tesztek >85% coverage
- ✅ MINDEN unit teszt ZÖLD
- ✅ Git history CLEAN (3-4 commit)

### **BC WRAPPER SIKERES, HA:**
- ✅ Meglévő GUI kód VÁLTOZATLAN működik
- ✅ Deprecation warning megjelenik
- ✅ Integration tesztek ZÖLDek
- ✅ Regression: 0 broken feature

---

## 🚫 KOCKÁZATOK & MITIGATION

| **Kockázat** | **Valószínűség** | **Impact** | **Mitigation** |
|--------------|------------------|------------|----------------|
| numpy eltávolítása → eredmények eltérnek | Közepes | Nagy | Regression tesztek + tolerance check |
| BC wrapper hibás delegálás | Alacsony | Közepes | Integration tesztek teljes GUI flow-ra |
| GUI kód törik | Alacsony | Kritikus | Deprecation wrapper + zero GUI code change |

---

## 📝 KÖVETKEZŐ LÉPÉSEK

### **IMMEDIATE (SPIKE Start):**
1. Git branch létrehozása: `git checkout -b spike/anomaly-domain-extraction`
2. Folder structure setup
3. Day 1 végrehajtása (entities + value objects)
4. Day 2 végrehajtása (domain service)

### **POST-SPIKE (Ha sikeres):**
5. Day 3: BC wrapper implementation
6. Integration testing
7. Regression testing
8. Git merge to main

### **POST-PILOT (Ha minden OK):**
9. Week 2-3: További domain extraction (wind analysis, precipitation, stb.)
10. Week 4-6: MultiCityEngine refactor
11. Week 7-12: Full project refactor

---

## 🎓 MENTORÁLÁS NOTES

**Codex számára:**
- Ez egy **VIZSGA**, de mentor támogatással!
- Kérdezz, ha elakadtál!
- Code review bármikor kérhető!
- Jelezd, ha a terv nem reális!

**Scope control:**
- CSAK Domain layer (Day 1-2)!
- NE NYÚLJ a GUI kódhoz (Day 3-ig)!
- NE PRÓBÁLD az egész projektet refaktorálni!

**Success = Működő spike, NEM perfekt architektúra!**

---

**Recon befejezve. Hajrá, Codex! 🚀**
