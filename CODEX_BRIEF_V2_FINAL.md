# 🚀 CODEX VIZSGA - Anomaly Detection Refactor

**Projekt:** Global Weather Analyzer  
**Feladat:** Domain logic kiemelése GUI-ból  
**Időkeret:** 2 nap (SPIKE)  
**Munkakönyvtár:** `~/PythonProjects/Jules/global_weather_analyzer/`

⚠️ **KRITIKUS:** Codex szabályok 100% érvényesek! AGENTS.md az alapdokumentum!

---

## 🎯 CÉL

**BEFORE (most):**
```
src/gui/results_panel/anomaly_detector.py (549 sor)
└─> AnomalyDetector ← 🔥 DOMAIN SERVICE a GUI-ban! ❌
```

**AFTER (cél):**
```
src/domain/services/anomaly_detector.py
└─> AnomalyDetectorService ← ✅ PURE domain logic!
```

**MIÉRT?**
- ❌ GUI-ban van business logic → Clean Arch sértés
- ❌ AI nem találja a domain logicot
- ❌ Nehéz unit tesztelni

**CÉL:**
- ✅ Domain logic PURE (ZERO numpy, csak stdlib!)
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ Max 250 sor/fájl

---

## 🔧 CODEX WORKFLOW

### Session Start:
```bash
cd ~/PythonProjects/Jules/global_weather_analyzer
git checkout -b spike/anomaly-domain-extraction

# 1. STATUS.md
cat > STATUS.md << 'EOF'
# SPIKE STATUS - Anomaly Refactor

## Current:
- Session: Day 1
- Task: Domain entities + value objects
- Blocked: None

## Files Created:
- [ ] src/domain/entities/climate_anomaly.py
- [ ] src/domain/value_objects/anomaly_threshold.py
- [ ] tests/domain/test_climate_anomaly.py
- [ ] tests/domain/test_anomaly_threshold.py

## Quality:
- Tests: Pending
- Coverage: Pending (target >85%)
- Pylint: Pending (target >8.0)
EOF

# 2. PLAN.md
cat > PLAN.md << 'EOF'
# DAY 1 PLAN

## Goal:
Domain entities + value objects

## Files to Create:
1. climate_anomaly.py (~150 sor)
2. anomaly_threshold.py (~200 sor)
3. test_climate_anomaly.py (~150 sor)
4. test_anomaly_threshold.py (~150 sor)

## Dependencies:
- stdlib: dataclass, datetime, typing
- test: pytest

## Validation:
- pytest >85% coverage
- pylint >8.0
- flake8 0 errors
EOF
```

### File Creation (Codex style):
```
# ✅ CORRECT - file-based, minimal output
Creating src/domain/entities/climate_anomaly.py...
✓ climate_anomaly.py complete (148 lines)

Creating tests/domain/test_climate_anomaly.py...
✓ test_climate_anomaly.py complete (156 lines)

# ❌ WRONG - verbose stdout
"Most létrehozom a ClimateAnomaly osztályt, amely..."
```

### Session End:
```bash
# Quality checks
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing
pylint src/domain/ --fail-under=8.0
flake8 src/domain/

# Git commit
git add src/domain/ tests/domain/ STATUS.md PLAN.md
git commit -m "feat(domain): Add ClimateAnomaly entity + AnomalyThresholdSet"

# Optional: REVIEW.md
```

---

## 📁 JELENLEGI KÓD (NE NYÚLJ HOZZÁ!)

### Config Layer (Jó helyen van!)
```
src/data/anomaly_profile_manager.py (385 sor)
└─> JSON config menedzser (temp_hot, precip_high, stb.)
    ✅ Ez MARAD ahogy van!
```

### Detection Logic (ROSSZ HELYEN!)
```
src/gui/results_panel/anomaly_detector.py (549 sor)
├─> AnomalyResult (dataclass) ← DOMAIN ENTITY!
├─> AnomalySettingsProvider ← Settings DI
└─> AnomalyDetector ← DOMAIN SERVICE!
    ├─> _detect_temperature_anomaly() ← BUSINESS LOGIC!
    ├─> _detect_precipitation_anomaly()
    └─> _detect_wind_anomaly()
```

**ENNEK a logikáját** emelj ki domain layer-be!

---

## 🎯 DAY 1 FELADAT (4-6 óra)

### 1. Folder Setup (5 perc)
```bash
mkdir -p src/domain/{entities,value_objects,services}
mkdir -p tests/domain
touch src/domain/__init__.py
touch src/domain/entities/__init__.py
touch src/domain/value_objects/__init__.py
touch src/domain/services/__init__.py
```

### 2. ClimateAnomaly Entity (~150 sor)

**Fájl:** `src/domain/entities/climate_anomaly.py`

**Követelmények:**
- ✅ `from __future__ import annotations` (első sor!)
- ✅ `@dataclass(frozen=True)` - immutable!
- ✅ Type hints MINDENÜTT
- ✅ Business rule validáció `__post_init__`-ben
- ✅ Property methods: `is_extreme`, `is_normal`
- ✅ Module docstring (1-2 sor)
- ✅ Max 150 sor

**Kód (teljes!):**

```python
"""Domain Entity - Climate Anomaly."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class ClimateAnomaly:
    """
    Domain Entity: Észlelt időjárási anomália.
    
    Business Rules:
    - parameter must be valid ("temperature", "precipitation", "wind")
    - severity must be valid ("success", "warning", "error")
    - measured_value nem lehet negatív precipitation/wind esetén
    """
    
    location_name: str
    date: date
    parameter: str  # "temperature", "precipitation", "wind"
    measured_value: float
    category: str  # "hot", "cold", "heavy_rain", "drought", "hurricane", etc.
    severity: str  # "success", "warning", "error", "disabled"
    message: str
    threshold: Optional[float] = None
    details: Optional[str] = None
    
    def __post_init__(self) -> None:
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
        """Business Rule: Normal = success severity."""
        return self.severity == "success"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.location_name} {self.date}: {self.message}"
```

**Git commit:**
```bash
git add src/domain/entities/climate_anomaly.py
git commit -m "feat(domain): Add ClimateAnomaly entity"
```

---

### 3. AnomalyThresholdSet Value Object (~200 sor)

**Fájl:** `src/domain/value_objects/anomaly_threshold.py`

**Követelmények:**
- ✅ `from __future__ import annotations`
- ✅ `@dataclass(frozen=True)` - immutable!
- ✅ Business rule validáció
- ✅ Class methods: `default()`, `tropical()`, `arctic()`
- ✅ `from_dict()` / `to_dict()` factory
- ✅ Max 200 sor

**Kód (teljes!):**

```python
"""Domain Value Object - Anomaly Thresholds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnomalyThresholdSet:
    """
    Value Object: Anomaly Detection küszöbértékek.
    
    Business Rules:
    - temp_hot > temp_cold
    - precip_high > precip_low
    - wind thresholds: normal < strong < extreme < hurricane
    """
    
    # Temperature (°C)
    temp_hot: float = 35.0
    temp_cold: float = -10.0
    
    # Precipitation (mm/day)
    precip_high: float = 100.0
    precip_low: float = 5.0
    
    # Wind (km/h)
    wind_normal: float = 50.0
    wind_strong: float = 70.0
    wind_extreme: float = 100.0
    wind_hurricane: float = 120.0
    
    def __post_init__(self) -> None:
        """Validate business rules."""
        # Temperature
        if self.temp_hot <= self.temp_cold:
            raise ValueError(
                f"temp_hot ({self.temp_hot}) must be > temp_cold ({self.temp_cold})"
            )
        
        if not (-50.0 <= self.temp_hot <= 60.0):
            raise ValueError(f"temp_hot must be in [-50, 60]°C")
        
        if not (-50.0 <= self.temp_cold <= 40.0):
            raise ValueError(f"temp_cold must be in [-50, 40]°C")
        
        # Precipitation
        if self.precip_high <= self.precip_low:
            raise ValueError(
                f"precip_high ({self.precip_high}) must be > precip_low ({self.precip_low})"
            )
        
        if not (0.0 <= self.precip_low <= 50.0):
            raise ValueError(f"precip_low must be in [0, 50]mm")
        
        if not (10.0 <= self.precip_high <= 500.0):
            raise ValueError(f"precip_high must be in [10, 500]mm")
        
        # Wind (ascending order)
        wind_values = [
            self.wind_normal,
            self.wind_strong,
            self.wind_extreme,
            self.wind_hurricane
        ]
        if wind_values != sorted(wind_values):
            raise ValueError("Wind thresholds must be in ascending order")
        
        for wind_val in wind_values:
            if not (10.0 <= wind_val <= 300.0):
                raise ValueError(f"Wind threshold must be in [10, 300]km/h")
    
    @classmethod
    def default(cls) -> AnomalyThresholdSet:
        """Default threshold set (continental climate)."""
        return cls()
    
    @classmethod
    def tropical(cls) -> AnomalyThresholdSet:
        """Tropical climate thresholds."""
        return cls(
            temp_hot=40.0,
            temp_cold=10.0,
            precip_high=200.0,
            precip_low=2.0,
            wind_hurricane=150.0
        )
    
    @classmethod
    def arctic(cls) -> AnomalyThresholdSet:
        """Arctic climate thresholds."""
        return cls(
            temp_hot=25.0,
            temp_cold=-30.0,
            precip_high=50.0,
            precip_low=1.0,
            wind_extreme=80.0,
            wind_hurricane=100.0
        )
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyThresholdSet:
        """Create from dictionary (JSON config)."""
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
    
    def to_dict(self) -> dict[str, float]:
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

**Git commit:**
```bash
git add src/domain/value_objects/anomaly_threshold.py
git commit -m "feat(domain): Add AnomalyThresholdSet value object"
```

---

### 4. Unit Tests (~300 sor összesen)

**Fájl:** `tests/domain/test_climate_anomaly.py`

```python
"""Tests for ClimateAnomaly entity."""
from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities.climate_anomaly import ClimateAnomaly


def test_create_valid_temperature_anomaly() -> None:
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


def test_invalid_parameter_rejected() -> None:
    """Business Rule: Only valid parameters allowed."""
    with pytest.raises(ValueError, match="Invalid parameter"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="invalid_param",
            measured_value=42.5,
            category="hot",
            severity="error",
            message="Test"
        )


def test_invalid_severity_rejected() -> None:
    """Business Rule: Only valid severities allowed."""
    with pytest.raises(ValueError, match="Invalid severity"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="temperature",
            measured_value=42.5,
            category="hot",
            severity="invalid",
            message="Test"
        )


def test_negative_precipitation_rejected() -> None:
    """Business Rule: Precipitation cannot be negative."""
    with pytest.raises(ValueError, match="Negative value not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="precipitation",
            measured_value=-10.0,
            category="drought",
            severity="warning",
            message="Test"
        )


def test_negative_wind_rejected() -> None:
    """Business Rule: Wind cannot be negative."""
    with pytest.raises(ValueError, match="Negative value not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date.today(),
            parameter="wind",
            measured_value=-50.0,
            category="calm",
            severity="success",
            message="Test"
        )


def test_normal_temperature_is_not_extreme() -> None:
    """Test normal temperature (success severity)."""
    anomaly = ClimateAnomaly(
        location_name="Szeged",
        date=date(2024, 5, 15),
        parameter="temperature",
        measured_value=24.0,
        category="normal",
        severity="success",
        message="🌡️ Normális: 24.0°C",
    )
    
    assert not anomaly.is_extreme
    assert anomaly.is_normal
```

**Fájl:** `tests/domain/test_anomaly_threshold.py`

```python
"""Tests for AnomalyThresholdSet value object."""
from __future__ import annotations

import pytest

from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet


def test_create_default_thresholds() -> None:
    """Test default threshold creation."""
    thresholds = AnomalyThresholdSet.default()
    
    assert thresholds.temp_hot == 35.0
    assert thresholds.temp_cold == -10.0
    assert thresholds.precip_high == 100.0
    assert thresholds.wind_hurricane == 120.0


def test_tropical_thresholds() -> None:
    """Test tropical climate thresholds."""
    thresholds = AnomalyThresholdSet.tropical()
    
    assert thresholds.temp_hot == 40.0
    assert thresholds.temp_cold == 10.0
    assert thresholds.precip_high == 200.0
    assert thresholds.wind_hurricane == 150.0


def test_arctic_thresholds() -> None:
    """Test arctic climate thresholds."""
    thresholds = AnomalyThresholdSet.arctic()
    
    assert thresholds.temp_hot == 25.0
    assert thresholds.temp_cold == -30.0
    assert thresholds.precip_high == 50.0
    assert thresholds.wind_hurricane == 100.0


def test_invalid_temperature_order_rejected() -> None:
    """Business Rule: temp_hot must be > temp_cold."""
    with pytest.raises(ValueError, match="temp_hot .* must be > temp_cold"):
        AnomalyThresholdSet(temp_hot=10.0, temp_cold=20.0)


def test_invalid_precipitation_order_rejected() -> None:
    """Business Rule: precip_high must be > precip_low."""
    with pytest.raises(ValueError, match="precip_high .* must be > precip_low"):
        AnomalyThresholdSet(precip_high=10.0, precip_low=50.0)


def test_invalid_wind_order_rejected() -> None:
    """Business Rule: Wind thresholds must be ascending."""
    with pytest.raises(ValueError, match="Wind thresholds must be in ascending order"):
        AnomalyThresholdSet(
            wind_normal=100.0,
            wind_strong=50.0,
            wind_extreme=120.0
        )


def test_from_dict_conversion() -> None:
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


def test_to_dict_conversion() -> None:
    """Test converting thresholds to dictionary."""
    thresholds = AnomalyThresholdSet(temp_hot=40.0, precip_high=150.0)
    data = thresholds.to_dict()
    
    assert data["temp_hot"] == 40.0
    assert data["precip_high"] == 150.0
    assert data["wind_hurricane"] == 120.0
```

**Git commit:**
```bash
git add tests/domain/
git commit -m "test(domain): Add unit tests for entity + value object"
```

---

### 5. Quality Check (KÖTELEZŐ!)

```bash
# Coverage check
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing

# Expected:
# tests/domain/test_climate_anomaly.py ......             [ 50%]
# tests/domain/test_anomaly_threshold.py .........        [100%]
# 
# ----------- coverage: platform linux, python 3.10.x -----------
# Name                                          Stmts   Miss  Cover   Missing
# ---------------------------------------------------------------------------
# src/domain/entities/climate_anomaly.py          25      0   100%
# src/domain/value_objects/anomaly_threshold.py   45      0   100%
# ---------------------------------------------------------------------------
# TOTAL                                            70      0   100%

# Pylint check
pylint src/domain/ --fail-under=8.0

# Expected:
# ------------------------------------
# Your code has been rated at 9.2/10

# Flake8 check
flake8 src/domain/

# Expected:
# (no output = success)
```

**SIKERKRITÉRIUM - DAY 1:**
- ✅ Coverage ≥85% (cél: 100%)
- ✅ Pylint ≥8.0 (cél: >9.0)
- ✅ Flake8 = 0 errors
- ✅ Minden teszt ZÖLD
- ✅ Max 250 sor/fájl
- ✅ Git history: 3 clean commit

**DAY 1 END** ✓

---

## 🎯 DAY 2 FELADAT (4-6 óra)

### 1. AnomalyDetectorService (~250 sor)

**Fájl:** `src/domain/services/anomaly_detector.py`

**Követelmények:**
- ✅ PURE business logic
- ✅ ZERO numpy! (használj `sum() / len()` helyette)
- ✅ ZERO external deps (csak stdlib!)
- ✅ Type hints MINDENÜTT
- ✅ Max 250 sor (Codex limit!)

**Kód (teljes!):**

```python
"""Domain Service - Anomaly Detector."""
from __future__ import annotations

from datetime import date
from typing import Optional

from ..entities.climate_anomaly import ClimateAnomaly
from ..value_objects.anomaly_threshold import AnomalyThresholdSet


class AnomalyDetectorService:
    """
    Domain Service: Időjárási anomáliák detektálása.
    
    PURE BUSINESS LOGIC:
    - ZERO external dependencies (csak stdlib!)
    - Deterministic
    - Testable
    
    Business Rules:
    - Temperature anomaly: max > temp_hot OR min < temp_cold
    - Precipitation anomaly: max > precip_high OR avg < precip_low
    - Wind anomaly: max > wind thresholds
    """
    
    def __init__(self, thresholds: AnomalyThresholdSet) -> None:
        """Initialize detector with thresholds."""
        self.thresholds = thresholds
    
    def detect_temperature_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        max_temps: list[float],
        min_temps: list[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect temperature anomaly.
        
        Business Logic:
        - max_temp > threshold → HOT anomaly (error)
        - min_temp < threshold → COLD anomaly (error)
        - Otherwise → NORMAL (success)
        """
        if not max_temps or not min_temps:
            return None
        
        # Remove None values
        valid_max = [t for t in max_temps if t is not None]
        valid_min = [t for t in min_temps if t is not None]
        
        if not valid_max or not valid_min:
            return None
        
        max_temp = max(valid_max)
        min_temp = min(valid_min)
        avg_temp = sum(valid_max) / len(valid_max)  # PURE stdlib!
        
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
                details=f"Max hőmérséklet > {self.thresholds.temp_hot}°C"
            )
        
        # COLD anomaly
        if min_temp < self.thresholds.temp_cold:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="temperature",
                measured_value=min_temp,
                category="cold",
                severity="error",
                message=f"❄️ Extrém hideg: {min_temp:.1f}°C",
                threshold=self.thresholds.temp_cold,
                details=f"Min hőmérséklet < {self.thresholds.temp_cold}°C"
            )
        
        # NORMAL
        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="temperature",
            measured_value=avg_temp,
            category="normal",
            severity="success",
            message=f"🌡️ Normális: {avg_temp:.1f}°C átlag",
            details="Hőmérséklet normál tartományban"
        )
    
    def detect_precipitation_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        precipitation_values: list[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect precipitation anomaly.
        
        Business Logic:
        - max_precip > threshold → HEAVY RAIN (error)
        - avg_precip < threshold → DROUGHT (warning)
        - Otherwise → NORMAL (success)
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
                details=f"Max csapadék > {self.thresholds.precip_high}mm"
            )
        
        # DROUGHT
        if avg_precip < self.thresholds.precip_low:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="precipitation",
                measured_value=avg_precip,
                category="drought",
                severity="warning",
                message=f"🏜️ Száraz: {avg_precip:.1f}mm/nap átlag",
                threshold=self.thresholds.precip_low,
                details=f"Átlag csapadék < {self.thresholds.precip_low}mm"
            )
        
        # NORMAL
        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="precipitation",
            measured_value=avg_precip,
            category="normal",
            severity="success",
            message=f"🌧️ Normális: {avg_precip:.1f}mm/nap",
            details="Csapadék normál tartományban"
        )
    
    def detect_wind_anomaly(
        self,
        location_name: str,
        analysis_date: date,
        wind_speeds: list[float]
    ) -> Optional[ClimateAnomaly]:
        """
        Detect wind anomaly.
        
        Business Logic:
        - max_wind > hurricane → HURRICANE (error)
        - max_wind > extreme → EXTREME WIND (error)
        - max_wind > strong → STRONG WIND (warning)
        - max_wind > normal → MODERATE WIND (warning)
        - Otherwise → CALM (success)
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
                details=f"Szél > {self.thresholds.wind_hurricane}km/h"
            )
        
        # EXTREME WIND
        if max_wind > self.thresholds.wind_extreme:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="extreme_wind",
                severity="error",
                message=f"🌪️ Extrém szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_extreme,
                details=f"Szél > {self.thresholds.wind_extreme}km/h"
            )
        
        # STRONG WIND
        if max_wind > self.thresholds.wind_strong:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="strong_wind",
                severity="warning",
                message=f"🌬️ Erős szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_strong,
                details=f"Szél > {self.thresholds.wind_strong}km/h"
            )
        
        # MODERATE WIND
        if max_wind > self.thresholds.wind_normal:
            return ClimateAnomaly(
                location_name=location_name,
                date=analysis_date,
                parameter="wind",
                measured_value=max_wind,
                category="moderate_wind",
                severity="warning",
                message=f"💨 Mérsékelt szél: {max_wind:.1f}km/h",
                threshold=self.thresholds.wind_normal,
                details=f"Szél > {self.thresholds.wind_normal}km/h"
            )
        
        # CALM
        return ClimateAnomaly(
            location_name=location_name,
            date=analysis_date,
            parameter="wind",
            measured_value=avg_wind,
            category="calm",
            severity="success",
            message=f"🌿 Csendes: {avg_wind:.1f}km/h",
            details="Szél normál tartományban"
        )
```

**Git commit:**
```bash
git add src/domain/services/anomaly_detector.py
git commit -m "feat(domain): Add AnomalyDetectorService with pure logic"
```

---

### 2. Service Tests (~250 sor)

**Fájl:** `tests/domain/test_anomaly_detector_service.py`

```python
"""Tests for AnomalyDetectorService."""
from __future__ import annotations

from datetime import date

from src.domain.services.anomaly_detector import AnomalyDetectorService
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet


def test_detect_extreme_heat() -> None:
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


def test_detect_extreme_cold() -> None:
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
    assert result.measured_value == -18.2


def test_detect_normal_temperature() -> None:
    """Test normal temperature."""
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


def test_detect_heavy_rain() -> None:
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


def test_detect_drought() -> None:
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
    assert result.measured_value < 5.0


def test_detect_hurricane_wind() -> None:
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


def test_handle_none_values() -> None:
    """Test None value handling."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        max_temps=[None, 25.0, None, 30.0],
        min_temps=[10.0, None, 15.0, None]
    )
    
    assert result is not None
    assert result.category == "normal"


def test_empty_data_returns_none() -> None:
    """Test empty data returns None."""
    thresholds = AnomalyThresholdSet.default()
    service = AnomalyDetectorService(thresholds)
    
    result = service.detect_temperature_anomaly(
        location_name="Test",
        analysis_date=date.today(),
        max_temps=[],
        min_temps=[]
    )
    
    assert result is None
```

**Git commit:**
```bash
git add tests/domain/test_anomaly_detector_service.py
git commit -m "test(domain): Add AnomalyDetectorService tests"
```

---

### 3. Final Quality Check (KÖTELEZŐ!)

```bash
# Full domain test suite
pytest tests/domain/ -v --cov=src/domain --cov-report=term-missing --cov-fail-under=85

# Expected:
# tests/domain/test_climate_anomaly.py ......              [ 33%]
# tests/domain/test_anomaly_threshold.py .........         [ 66%]
# tests/domain/test_anomaly_detector_service.py .......    [100%]
# 
# ----------- coverage: platform linux, python 3.10.x -----------
# Name                                          Stmts   Miss  Cover
# -------------------------------------------------------------------
# src/domain/entities/climate_anomaly.py          25      0   100%
# src/domain/value_objects/anomaly_threshold.py   45      0   100%
# src/domain/services/anomaly_detector.py        120      5    96%
# -------------------------------------------------------------------
# TOTAL                                           190      5    97%
#
# ✓ Coverage: 97% (target: 85%)

# Pylint
pylint src/domain/ --fail-under=8.0

# Expected:
# ------------------------------------
# Your code has been rated at 9.5/10 
# ✓ Pylint: 9.5 (target: 8.0)

# Flake8
flake8 src/domain/

# Expected:
# (no output)
# ✓ Flake8: 0 errors
```

**SIKERKRITÉRIUM - DAY 2:**
- ✅ Coverage ≥85% (achieved: 97%)
- ✅ Pylint ≥8.0 (achieved: 9.5)
- ✅ Flake8 = 0 errors
- ✅ ZERO numpy/external deps
- ✅ Max 250 sor/fájl ✓
- ✅ Git history: 2 clean commit

**DAY 2 END** ✓

---

## 🚫 TILALMAK (AGENTS.md szerint!)

❌ **NO guessing** - ha bizonytalan, kérdezz!  
❌ **NO incomplete code** - SOHA `...` vagy `# TODO`!  
❌ **NO truncation** - TELJES fájlok MINDIG!  
❌ **NO numpy** - domain layer-ben CSAK stdlib!  
❌ **NO verbose output** - kód beszél, nem magyarázat!  
❌ **NO >250 sor/fájl** - God file TILTVA!

✅ **Type hints MINDENÜTT**  
✅ **`from __future__ import annotations`**  
✅ **Coverage >85%**  
✅ **Pylint >8.0**  
✅ **Git commit minden lépés után**

---

## 📊 SPIKE SUCCESS METRICS

**SPIKE SIKERES, HA:**
- ✅ `src/domain/entities/climate_anomaly.py` létrehozva
- ✅ `src/domain/value_objects/anomaly_threshold.py` létrehozva
- ✅ `src/domain/services/anomaly_detector.py` létrehozva
- ✅ Unit tesztek mind ZÖLDek
- ✅ Coverage >85%
- ✅ Pylint >8.0
- ✅ Flake8 = 0 errors
- ✅ ZERO numpy dependency
- ✅ Git history: 5-6 clean commit

**SPIKE FAIL, HA:**
- ❌ Tesztek nem futnak
- ❌ Coverage <80%
- ❌ numpy/external deps a domain-ben
- ❌ Félbehagyott fájlok (`...`, `TODO`)

---

## 🎓 MENTORÁLÁS

Ha elakadsz:
1. Olvasd el újra a RECONNAISSANCE_REPORT.md-t!
2. Nézd meg a QUICK_REFERENCE_CARD.md-t!
3. Kérdezz! (Max 2 kérdés)
4. Használj reasonable defaults!

**SIKER = Működő spike, NEM perfekt architektúra!**

---

**Hajrá! 🚀**
