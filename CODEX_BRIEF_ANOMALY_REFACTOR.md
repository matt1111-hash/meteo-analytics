# 🚀 CODEX VIZSGA - Anomaly Detection Refactor

## 📊 PROJEKT KONTEXTUS

**Projekt:** Global Weather Analyzer  
**Feladat:** Clean Architecture pilot - Anomaly detection refactor  
**Időkeret:** 2-3 nap (SPIKE módszer)  
**Környezet:** Izolált teszt sandbox (NEM az éles projekt!)

---

## 🎯 CÉL

**Domain logic kiemelése GUI rétegből:**

```
src/gui/results_panel/anomaly_detector.py (549 sor)
   ⬇️ ÁTHELYEZÉS ⬇️
src/domain/services/anomaly_detector.py
```

**MIÉRT?**
- ❌ GUI-ban van a business logic (Clean Arch sértés!)
- ❌ AI nem találja a domain logicot
- ❌ Nehéz unit tesztelni (GUI dependency)

**AFTER STATE:**
- ✅ Domain logic PURE (ZERO external deps)
- ✅ AI TUDJA: `src/domain/services/anomaly_detector.py`
- ✅ Unit test KÖNNYŰ (no GUI!)

---

## 📁 JELENLEGI KÓDSTRUKTÚRA

### **1. CONFIG LAYER (Jó helyen van!)**
```
src/data/anomaly_profile_manager.py (385 sor)
├── AnomalyProfileSettings (dataclass)
│   └── temp_hot, temp_cold, precip_high, wind_extreme, ...
└── AnomalyProfileManager
    └── JSON CRUD: save/load profilok
```

### **2. GUI LAYER (❌ Itt van a probléma!)**
```
src/gui/results_panel/anomaly_detector.py (549 sor)
├── AnomalyResult (dataclass) ← 🔥 DOMAIN ENTITY!
├── AnomalySettingsProvider ← Settings injector
└── AnomalyDetector ← 🔥 DOMAIN SERVICE!
    ├── detect_all_anomalies()
    ├── _detect_temperature_anomaly()
    ├── _detect_precipitation_anomaly()
    └── _detect_wind_anomaly()
```

### **3. CONSTANTS**
```
src/gui/utils.py
└── AnomalyConstants
    ├── TEMP_HOT_THRESHOLD = 35.0
    ├── WIND_EXTREME_THRESHOLD = 100.0
    └── ...
```

---

## 🎯 FELADAT - DAY 1-2 SPIKE

### **DAY 1: Domain Entities + Value Objects (4-6 óra)**

#### 1.1 Folder Structure
```bash
mkdir -p src/domain/entities
mkdir -p src/domain/value_objects
mkdir -p src/domain/services
mkdir -p tests/domain

touch src/domain/__init__.py
touch src/domain/entities/__init__.py
touch src/domain/value_objects/__init__.py
touch src/domain/services/__init__.py
```

#### 1.2 Domain Entity: ClimateAnomaly
**Fájl:** `src/domain/entities/climate_anomaly.py`

```python
"""
Domain Entity - Climate Anomaly
Represents a detected weather anomaly.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)  # Immutable!
class ClimateAnomaly:
    """
    Domain Entity: Észlelt időjárási anomália.
    
    Business Rules:
    - category must be valid ("temperature", "precipitation", "wind")
    - severity must be valid ("success", "warning", "error")
    - measured_value must be non-negative for precipitation/wind
    """
    location_name: str
    date: date
    parameter: str  # "temperature", "precipitation", "wind"
    measured_value: float
    category: str  # "hot", "cold", "heavy_rain", "drought", "strong_wind", etc.
    severity: str  # "success", "warning", "error"
    message: str
    threshold: Optional[float] = None
    details: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules."""
        valid_parameters = ["temperature", "precipitation", "wind"]
        if self.parameter not in valid_parameters:
            raise ValueError(f"Invalid parameter: {self.parameter}")
        
        valid_severities = ["success", "warning", "error", "disabled"]
        if self.severity not in valid_severities:
            raise ValueError(f"Invalid severity: {self.severity}")
        
        # Precipitation és wind nem lehet negatív
        if self.parameter in ["precipitation", "wind"] and self.measured_value < 0:
            raise ValueError(f"Negative value not allowed for {self.parameter}")
    
    @property
    def is_extreme(self) -> bool:
        """Business Rule: Extreme anomaly = error severity."""
        return self.severity == "error"
    
    @property
    def is_normal(self) -> bool:
        """Business Rule: Normal condition = success severity."""
        return self.severity == "success"
    
    def __str__(self) -> str:
        return f"{self.location_name} {self.date}: {self.message}"
```

#### 1.3 Value Object: AnomalyThresholdSet
**Fájl:** `src/domain/value_objects/anomaly_threshold.py`

```python
"""
Domain Value Object - Anomaly Thresholds
Self-validating threshold configuration.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class AnomalyThresholdSet:
    """
    Value Object: Anomaly Detection Küszöbértékek.
    
    Business Rules:
    - temp_hot > temp_cold
    - precip_high > precip_low
    - wind thresholds: normal < strong < extreme < hurricane
    """
    # Temperature thresholds (°C)
    temp_hot: float = 35.0
    temp_cold: float = -10.0
    
    # Precipitation thresholds (mm/day)
    precip_high: float = 100.0
    precip_low: float = 5.0
    
    # Wind thresholds (km/h)
    wind_normal: float = 50.0
    wind_strong: float = 70.0
    wind_extreme: float = 100.0
    wind_hurricane: float = 120.0
    
    def __post_init__(self):
        """Validate business rules."""
        # Temperature validation
        if self.temp_hot <= self.temp_cold:
            raise ValueError(
                f"temp_hot ({self.temp_hot}) must be > temp_cold ({self.temp_cold})"
            )
        
        if not (-50.0 <= self.temp_hot <= 60.0):
            raise ValueError(f"temp_hot must be in range [-50, 60]°C")
        
        if not (-50.0 <= self.temp_cold <= 40.0):
            raise ValueError(f"temp_cold must be in range [-50, 40]°C")
        
        # Precipitation validation
        if self.precip_high <= self.precip_low:
            raise ValueError(
                f"precip_high ({self.precip_high}) must be > precip_low ({self.precip_low})"
            )
        
        if not (0.0 <= self.precip_low <= 50.0):
            raise ValueError(f"precip_low must be in range [0, 50]mm")
        
        if not (10.0 <= self.precip_high <= 500.0):
            raise ValueError(f"precip_high must be in range [10, 500]mm")
        
        # Wind validation (ascending order)
        wind_values = [self.wind_normal, self.wind_strong, self.wind_extreme, self.wind_hurricane]
        if wind_values != sorted(wind_values):
            raise ValueError("Wind thresholds must be in ascending order")
        
        for wind_val in wind_values:
            if not (10.0 <= wind_val <= 300.0):
                raise ValueError(f"Wind threshold must be in range [10, 300]km/h")
    
    @classmethod
    def default(cls) -> 'AnomalyThresholdSet':
        """Default threshold set (continental climate)."""
        return cls()
    
    @classmethod
    def tropical(cls) -> 'AnomalyThresholdSet':
        """Tropical climate threshold set."""
        return cls(
            temp_hot=40.0,
            temp_cold=10.0,
            precip_high=200.0,
            precip_low=2.0,
            wind_hurricane=150.0
        )
    
    @classmethod
    def arctic(cls) -> 'AnomalyThresholdSet':
        """Arctic climate threshold set."""
        return cls(
            temp_hot=25.0,
            temp_cold=-30.0,
            precip_high=50.0,
            precip_low=1.0,
            wind_extreme=80.0,
            wind_hurricane=100.0
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnomalyThresholdSet':
        """Create from dictionary (e.g. from JSON config)."""
        return cls(
            temp_hot=data.get("temp_hot", 35.0),
            temp_cold=data.get("temp_cold", -10.0),
            precip_high=data.get("precip_high", 100.0),
            precip_low=data.get("precip_low", 5.0),
            wind_normal=data.get("wind_normal", 50.0),
            wind_strong=data.get("wind_strong", 70.0),
            wind_extreme=data.get("wind_extreme", 100.0),
            wind_hurricane=data.get("wind_hurricane", 120.0)
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "temp_hot": self.temp_hot,
            "temp_cold": self.temp_cold,
            "precip_high": self.precip_high,
            "precip_low": self.precip_low,
            "wind_normal": self.wind_normal,
            "wind_strong": self.wind_strong,
            "wind_extreme": self.wind_extreme,
            "wind_hurricane": self.wind_hurricane
        }
```

#### 1.4 Unit Tests (KÖTELEZŐ!)
**Fájl:** `tests/domain/test_climate_anomaly.py`

```python
"""Unit tests for ClimateAnomaly entity."""
import pytest
from datetime import date
from src.domain.entities.climate_anomaly import ClimateAnomaly

def test_create_valid_temperature_anomaly():
    """Test valid temperature anomaly creation."""
    anomaly = ClimateAnomaly(
        location_name="Budapest",
        date=date(2024, 7, 15),
        parameter="temperature",
        measured_value=42.5,
        category="hot",
        severity="error",
        message="🔥 Extrém hőség: 42.5°C",
        threshold=35.0,
        details="Maximum hőmérséklet meghaladja a 35°C küszöböt"
    )
    
    assert anomaly.is_extreme
    assert not anomaly.is_normal
    assert str(anomaly) == "Budapest 2024-07-15: 🔥 Extrém hőség: 42.5°C"

def test_invalid_parameter_rejected():
    """Business Rule: Only valid parameters allowed."""
    with pytest.raises(ValueError, match="Invalid parameter"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="invalid_param",  # ❌ Invalid!
            measured_value=42.5,
            category="hot",
            severity="error",
            message="Test"
        )

def test_negative_precipitation_rejected():
    """Business Rule: Precipitation cannot be negative."""
    with pytest.raises(ValueError, match="Negative value not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="precipitation",
            measured_value=-10.0,  # ❌ Negative!
            category="drought",
            severity="warning",
            message="Test"
        )

# ... More tests ...
```

**Fájl:** `tests/domain/test_anomaly_threshold.py`

```python
"""Unit tests for AnomalyThresholdSet value object."""
import pytest
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet

def test_create_default_thresholds():
    """Test default threshold creation."""
    thresholds = AnomalyThresholdSet.default()
    
    assert thresholds.temp_hot == 35.0
    assert thresholds.temp_cold == -10.0
    assert thresholds.precip_high == 100.0
    assert thresholds.wind_hurricane == 120.0

def test_invalid_temperature_order_rejected():
    """Business Rule: temp_hot must be > temp_cold."""
    with pytest.raises(ValueError, match="temp_hot .* must be > temp_cold"):
        AnomalyThresholdSet(temp_hot=10.0, temp_cold=20.0)

def test_invalid_wind_order_rejected():
    """Business Rule: Wind thresholds must be ascending."""
    with pytest.raises(ValueError, match="Wind thresholds must be in ascending order"):
        AnomalyThresholdSet(
            wind_normal=100.0,
            wind_strong=50.0,  # ❌ Wrong order!
            wind_extreme=120.0
        )

def test_from_dict_conversion():
    """Test creating thresholds from dictionary."""
    data = {
        "temp_hot": 40.0,
        "temp_cold": 5.0,
        "precip_high": 150.0
    }
    
    thresholds = AnomalyThresholdSet.from_dict(data)
    
    assert thresholds.temp_hot == 40.0
    assert thresholds.temp_cold == 5.0
    assert thresholds.precip_high == 150.0
    # Defaults for missing values
    assert thresholds.wind_normal == 50.0

# ... More tests ...
```

#### 1.5 Git Commit
```bash
git add src/domain/ tests/domain/
git commit -m "feat(domain): Add ClimateAnomaly entity and AnomalyThresholdSet value object with tests"
```

**SIKERKRITÉRIUM - DAY 1:**
- [ ] Domain entities létrehozva
- [ ] Value objects létrehozva
- [ ] Unit tesztek >90% coverage
- [ ] Minden teszt ZÖLD
- [ ] Git commit done

---

### **DAY 2: Domain Service (4-6 óra)**

#### 2.1 Domain Service: AnomalyDetectorService
**Fájl:** `src/domain/services/anomaly_detector.py`

```python
"""
Domain Service - Anomaly Detector
PURE business logic, ZERO external dependencies!
"""
from typing import List, Optional
from datetime import date
from ..entities.climate_anomaly import ClimateAnomaly
from ..value_objects.anomaly_threshold import AnomalyThresholdSet

class AnomalyDetectorService:
    """
    Domain Service: Időjárási anomáliák detektálása.
    
    🎯 PURE BUSINESS LOGIC:
    - ZERO external dependencies (no numpy, no GUI, no DB!)
    - Only Python stdlib + domain objects
    - Deterministic, testable, predictable
    
    Business Rules:
    - Temperature anomaly: max > temp_hot OR min < temp_cold
    - Precipitation anomaly: max > precip_high OR avg < precip_low
    - Wind anomaly: max > wind thresholds
    """
    
    def __init__(self, thresholds: AnomalyThresholdSet):
        """
        Initialize detector with threshold configuration.
        
        Args:
            thresholds: Anomaly threshold set (value object)
        """
        self.thresholds = thresholds
    
    def detect_temperature_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        max_temps: List[float],
        min_temps: List[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect temperature anomaly.
        
        Business Logic:
        - If max temp > threshold → HOT anomaly
        - If min temp < threshold → COLD anomaly
        - Otherwise → NORMAL
        
        Args:
            location_name: Location name
            analysis_date: Analysis date
            max_temps: Daily maximum temperatures
            min_temps: Daily minimum temperatures
            
        Returns:
            ClimateAnomaly or None if no valid data
        """
        if not max_temps or not min_temps:
            return None
        
        # Remove None values
        valid_max_temps = [t for t in max_temps if t is not None]
        valid_min_temps = [t for t in min_temps if t is not None]
        
        if not valid_max_temps or not valid_min_temps:
            return None
        
        max_temp = max(valid_max_temps)
        min_temp = min(valid_min_temps)
        avg_temp = sum(valid_max_temps) / len(valid_max_temps)
        
        # HOT anomaly
        if max_temp > self.thresholds.temp_hot:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=max_temp,
                category="hot",
                severity="error",
                message=f"🔥 Extrém hőség: {max_temp:.1f}°C",
                threshold=self.thresholds.temp_hot,
                details=f"Maximum hőmérséklet meghaladja a {self.thresholds.temp_hot}°C küszöböt"
            )
        
        # COLD anomaly
        elif min_temp < self.thresholds.temp_cold:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=min_temp,
                category="cold",
                severity="error",
                message=f"❄️ Extrém hideg: {min_temp:.1f}°C",
                threshold=self.thresholds.temp_cold,
                details=f"Minimum hőmérséklet alatta a {self.thresholds.temp_cold}°C küszöbnek"
            )
        
        # NORMAL
        else:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=avg_temp,
                category="normal",
                severity="success",
                message=f"🌡️ Normális: {avg_temp:.1f}°C átlag",
                details=f"Hőmérséklet a normál tartományban"
            )
    
    def detect_precipitation_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        precipitation_values: List[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect precipitation anomaly.
        
        Business Logic:
        - If max precip > high_threshold → HEAVY RAIN
        - If avg precip < low_threshold → DROUGHT
        - Otherwise → NORMAL
        
        Args:
            location_name: Location name
            analysis_date: Analysis date
            precipitation_values: Daily precipitation sums (mm)
            
        Returns:
            ClimateAnomaly or None
        """
        if not precipitation_values:
            return None
        
        valid_precip = [p for p in precipitation_values if p is not None and p >= 0]
        
        if not valid_precip:
            return None
        
        max_precip = max(valid_precip)
        avg_precip = sum(valid_precip) / len(valid_precip)
        
        # HEAVY RAIN
        if max_precip > self.thresholds.precip_high:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=max_precip,
                category="heavy_rain",
                severity="error",
                message=f"🌊 Esős időszak: {max_precip:.1f}mm/nap",
                threshold=self.thresholds.precip_high,
                details=f"Maximum napi csapadék meghaladja a {self.thresholds.precip_high}mm küszöböt"
            )
        
        # DROUGHT
        elif avg_precip < self.thresholds.precip_low:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=avg_precip,
                category="drought",
                severity="warning",
                message=f"🏜️ Száraz időszak: {avg_precip:.1f}mm/nap átlag",
                threshold=self.thresholds.precip_low,
                details=f"Átlagos csapadék alatta a {self.thresholds.precip_low}mm küszöbnek"
            )
        
        # NORMAL
        else:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=avg_precip,
                category="normal",
                severity="success",
                message=f"🌧️ Normális: {avg_precip:.1f}mm/nap",
                details=f"Csapadék a normál tartományban"
            )
    
    def detect_wind_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        wind_speeds: List[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect wind anomaly.
        
        Business Logic:
        - If max wind > hurricane → HURRICANE
        - If max wind > extreme → EXTREME WIND
        - If max wind > strong → STRONG WIND
        - If max wind > normal → MODERATE WIND
        - Otherwise → CALM
        
        Args:
            location_name: Location name
            analysis_date: Analysis date
            wind_speeds: Wind speeds (km/h)
            
        Returns:
            ClimateAnomaly or None
        """
        if not wind_speeds:
            return None
        
        valid_winds = [w for w in wind_speeds if w is not None and w >= 0]
        
        if not valid_winds:
            return None
        
        max_wind = max(valid_winds)
        avg_wind = sum(valid_winds) / len(valid_winds)
        
        # HURRICANE
        if max_wind > self.thresholds.wind_hurricane:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="hurricane",
                severity="error",
                message=f"🌀 Orkán: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_hurricane,
                details=f"Szélsebesség orkán szinten ({self.thresholds.wind_hurricane}+ km/h)"
            )
        
        # EXTREME WIND
        elif max_wind > self.thresholds.wind_extreme:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="extreme_wind",
                severity="error",
                message=f"🌪️ Extrém szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_extreme,
                details=f"Szélsebesség extrém szinten"
            )
        
        # STRONG WIND
        elif max_wind > self.thresholds.wind_strong:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="strong_wind",
                severity="warning",
                message=f"🌬️ Erős szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_strong,
                details=f"Szélsebesség erős szinten"
            )
        
        # MODERATE WIND
        elif max_wind > self.thresholds.wind_normal:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="moderate_wind",
                severity="warning",
                message=f"💨 Mérsékelt szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_normal,
                details=f"Szélsebesség mérsékelt szinten"
            )
        
        # CALM
        else:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=avg_wind,
                category="calm",
                severity="success",
                message=f"🌿 Csendes: {avg_wind:.1f}km/h",
                details=f"Szélsebesség normál tartományban"
            )
```

#### 2.2 Unit Tests
**Fájl:** `tests/domain/test_anomaly_detector_service.py`

```python
"""Unit tests for AnomalyDetectorService."""
import pytest
from datetime import date
from src.domain.services.anomaly_detector import AnomalyDetectorService
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet

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
    assert result.measured_value == 45.1  # Max of max_temps
    assert result.is_extreme

def test_detect_extreme_cold():
    """Test extreme cold detection."""
    thresholds = AnomalyThresholdSet(temp_cold=-10.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Miskolc",
        analysis_date=date(2024, 1, 15),
        max_temps=[5.0, 2.0, -3.0],
        min_temps=[-15.5, -12.0, -18.2]
    )
    
    assert result is not None
    assert result.category == "cold"
    assert result.severity == "error"
    assert result.measured_value == -18.2  # Min of min_temps

def test_detect_normal_temperature():
    """Test normal temperature (no anomaly)."""
    thresholds = AnomalyThresholdSet(temp_hot=35.0, temp_cold=-10.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Szeged",
        analysis_date=date(2024, 5, 15),
        max_temps=[22.0, 24.5, 26.0],
        min_temps=[12.0, 14.0, 15.5]
    )
    
    assert result is not None
    assert result.category == "normal"
    assert result.severity == "success"
    assert not result.is_extreme

def test_detect_heavy_rain():
    """Test heavy rain detection."""
    thresholds = AnomalyThresholdSet(precip_high=100.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_precipitation_anomaly(
        location_name="Debrecen",
        analysis_date=date(2024, 6, 15),
        precipitation_values=[125.5, 85.0, 20.0, 5.0]
    )
    
    assert result is not None
    assert result.category == "heavy_rain"
    assert result.severity == "error"
    assert result.measured_value == 125.5

def test_detect_drought():
    """Test drought detection."""
    thresholds = AnomalyThresholdSet(precip_low=5.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_precipitation_anomaly(
        location_name="Pécs",
        analysis_date=date(2024, 8, 15),
        precipitation_values=[0.5, 0.0, 1.2, 0.8]
    )
    
    assert result is not None
    assert result.category == "drought"
    assert result.severity == "warning"
    assert result.measured_value < 5.0  # Avg precip

def test_detect_hurricane_wind():
    """Test hurricane wind detection."""
    thresholds = AnomalyThresholdSet(wind_hurricane=120.0)
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_wind_anomaly(
        location_name="Balatonfüred",
        analysis_date=date(2024, 4, 15),
        wind_speeds=[135.5, 85.0, 25.0]
    )
    
    assert result is not None
    assert result.category == "hurricane"
    assert result.severity == "error"
    assert result.measured_value == 135.5

def test_handle_none_values():
    """Test handling of None values in data."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)
    
    # Data with None values
    result = service.detect_temperature_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        max_temps=[None, 25.0, None, 30.0],
        min_temps=[10.0, None, 15.0, None]
    )
    
    # Should still work by filtering None values
    assert result is not None
    assert result.category == "normal"

def test_empty_data_returns_none():
    """Test that empty data returns None."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        max_temps=[],
        min_temps=[]
    )
    
    assert result is None

# ... More tests ...
```

#### 2.3 Git Commit
```bash
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing
git add src/domain/services/ tests/domain/
git commit -m "feat(domain): Add AnomalyDetectorService with pure business logic"
```

**SIKERKRITÉRIUM - DAY 2:**
- [ ] Domain service létrehozva
- [ ] Unit tesztek >85% coverage
- [ ] PURE logic (ZERO external deps!)
- [ ] Minden teszt ZÖLD
- [ ] Git commit done

---

## 🚫 KRITIKUS TILALMAK

❌ **NE ÉRINTSD az éles projektet!**  
❌ **NE HASZNÁLJ numpy/pandas/external deps a domain layer-ben!**  
❌ **NE COMMITOLJ tesztlő kódot!**  
❌ **NE HAGYD félbe a munkát!**  
❌ **NE TÖRD EL a meglévő teszteket!**

✅ **CSAK Python stdlib + domain objects**  
✅ **CSAK unit tesztek (no integration yet)**  
✅ **TELJES fájlok, nincs `...`**  
✅ **Git commit minden lépés után**  

---

## 📊 SUCCESS METRICS

### **SPIKE SIKERES, HA:**
- ✅ Domain entities + value objects létrehozva
- ✅ Domain service PURE logic (ZERO deps!)
- ✅ Unit tesztek >85% coverage
- ✅ MINDEN teszt ZÖLD
- ✅ Git history CLEAN (3-4 commit)

### **SPIKE FAIL, HA:**
- ❌ Tesztek nem futnak
- ❌ Coverage <70%
- ❌ External dependencies a domain-ben
- ❌ Félbehagyott fájlok

---

## 📝 JEGYZETFÜZET - SESSION UTÁN

**A spike végén készíts egy `SPIKE_REPORT.md`-t:**

```markdown
# SPIKE REPORT - Anomaly Detection Refactor

## ✅ MEGVALÓSÍTVA
- [ ] Domain entities (ClimateAnomaly)
- [ ] Value objects (AnomalyThresholdSet)
- [ ] Domain service (AnomalyDetectorService)
- [ ] Unit tesztek (>85% coverage)

## 📊 TESZTELÉSI EREDMÉNYEK
```bash
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing
```

## 🐛 PROBLÉMÁK / AKADÁLYOK
- [Lista a problémákról]

## 🎯 KÖVETKEZŐ LÉPÉSEK
- Day 3: BC Wrapper + GUI integráció
- Day 4-5: Use case layer + infrastructure
```

---

## 🎓 MENTORÁLÁS

Ez egy **VIZSGA**, de én (Claude) itt vagyok mentorként:
- Kérdezz, ha elakadtál!
- Kérj code review-t commit előtt!
- Jelezd, ha a terv nem reális!

**SIKER = Működő spike, nem perfekt architektúra!**

---

Hajrá! 🚀
