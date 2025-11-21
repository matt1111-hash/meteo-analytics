# 🚀 PILOT REFACTOR PLAN - Clean Architecture Bevezetés
**Global Weather Analyzer - 1 hetes pilot projekt**

---

## 🎯 CÉL

**Bebizonyítani**, hogy Clean Architecture:
1. ✅ **Működik** a projektben
2. ✅ **AI jobban tudja használni** (Codex, Claude Code)
3. ✅ **Nem töri el** a meglévő funkciókat
4. ✅ **Értéket ad** (gyorsabb development)

**IDŐ:** 5-7 munkanap (~40 óra)

**SCOPE:** CSAK az **anomaly detection** funkció refaktorálása!

---

## 📊 JELENLEGI ÁLLAPOT (BEFORE)

```
src/
  data/
    anomaly_profile_manager.py    # 635 sor GOD CLASS! ❌
      - Anomaly detection algorithm (Domain)
      - Database persistence (Infrastructure)
      - VEGYES felelősségek!
  
  analytics/
    multi_city_engine.py          # 1197 sor - használja!
      - Hívja az AnomalyProfileManager-t
```

**PROBLÉMA:**
- AI nem tudja, hol van a CORE anomaly logic
- Tesztelhetetlen (DB dependency)
- Nehéz módosítani

---

## 🎯 CÉLÁLLAPOT (AFTER)

```
src/
  domain/                          # ✅ ÚJ!
    entities/
      climate_anomaly.py           # ✅ Entity
    value_objects/
      anomaly_threshold.py         # ✅ Value Object
    services/
      anomaly_detector.py          # ✅ PURE business logic!
  
  application/                     # ✅ ÚJ!
    use_cases/
      detect_anomalies_use_case.py # ✅ Orchestration
  
  infrastructure/                  # ✅ ÚJ!
    repositories/
      anomaly_repository.py        # ✅ DB access
  
  data/
    anomaly_profile_manager.py     # ⚠️ DEPRECATED (backward compat)
```

**EREDMÉNY:**
- ✅ AI TUDJA, hol van a Domain logic (`src/domain/services/anomaly_detector.py`)
- ✅ Unit tesztelhető (NO DB dependency)
- ✅ Könnyen módosítható

---

## 📅 NAPRÓL NAPRA TERV

### **DAY 1: Struktura + Domain Entities (8 óra)**

#### 1.1 Mappaszerkezet létrehozása (30 perc)

```bash
cd ~/PythonProjects/Jules/global_weather_analyzer

# Új mappák
mkdir -p src/domain/entities
mkdir -p src/domain/value_objects
mkdir -p src/domain/services
mkdir -p src/domain/repositories
mkdir -p src/application/use_cases
mkdir -p src/infrastructure/repositories

# __init__.py fájlok
touch src/domain/__init__.py
touch src/domain/entities/__init__.py
touch src/domain/value_objects/__init__.py
touch src/domain/services/__init__.py
touch src/domain/repositories/__init__.py
touch src/application/__init__.py
touch src/application/use_cases/__init__.py
touch src/infrastructure/__init__.py
touch src/infrastructure/repositories/__init__.py

# Git commit
git add src/domain src/application src/infrastructure
git commit -m "feat: Add Clean Architecture folder structure"
```

#### 1.2 Domain Entity: ClimateAnomaly (2 óra)

**Fájl:** `src/domain/entities/climate_anomaly.py`

```python
"""
Domain Entity - Climate Anomaly
================================
Represents a detected climate anomaly at a specific location and time.

Business Rules:
- deviation must be significant (> threshold)
- severity calculated from standard deviations
- date cannot be in the future
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from ..value_objects.temperature import Temperature

@dataclass(frozen=True)  # Immutable!
class ClimateAnomaly:
    """
    Domain Entity: Climate Anomaly
    
    Represents a detected deviation from historical climate norms.
    """
    location_name: str
    date: date
    parameter: str  # "temperature", "precipitation", etc.
    measured_value: float
    historical_mean: float
    historical_std: float
    deviation_sigma: float  # How many σ from mean
    
    def __post_init__(self):
        """Validate business rules."""
        from datetime import date as date_class
        if self.date > date_class.today():
            raise ValueError(f"Future date not allowed: {self.date}")
        
        if abs(self.deviation_sigma) < 1.0:
            raise ValueError(f"Anomaly too weak: {self.deviation_sigma}σ")
    
    @property
    def severity(self) -> str:
        """
        Business Rule: Anomaly severity classification.
        
        - LOW: 1-2 sigma
        - MODERATE: 2-2.5 sigma
        - HIGH: 2.5-3 sigma
        - EXTREME: 3+ sigma
        """
        abs_sigma = abs(self.deviation_sigma)
        
        if abs_sigma < 2.0:
            return "LOW"
        elif abs_sigma < 2.5:
            return "MODERATE"
        elif abs_sigma < 3.0:
            return "HIGH"
        else:
            return "EXTREME"
    
    @property
    def is_extreme(self) -> bool:
        """Business Rule: Extreme anomaly = 3+ sigma."""
        return abs(self.deviation_sigma) >= 3.0
    
    @property
    def is_positive_anomaly(self) -> bool:
        """Positive deviation (warmer, wetter, etc.)."""
        return self.measured_value > self.historical_mean
    
    def __str__(self) -> str:
        direction = "+" if self.is_positive_anomaly else "-"
        return (f"{self.location_name} {self.date}: "
                f"{self.parameter} anomaly {direction}{abs(self.deviation_sigma):.1f}σ "
                f"({self.severity})")
```

**Git commit:**
```bash
git add src/domain/entities/climate_anomaly.py
git commit -m "feat(domain): Add ClimateAnomaly entity with business rules"
```

#### 1.3 Value Object: AnomalyThreshold (2 óra)

**Fájl:** `src/domain/value_objects/anomaly_threshold.py`

```python
"""
Domain Value Object - Anomaly Threshold
========================================
Self-validating threshold for anomaly detection.

Business Rule: Threshold must be between 1.0 and 5.0 standard deviations.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class AnomalyThreshold:
    """
    Value Object: Anomaly Detection Threshold
    
    Represents how many standard deviations constitute an anomaly.
    Typical values: 2.0 (95% confidence), 3.0 (99.7% confidence)
    """
    sigma: float
    
    def __post_init__(self):
        """Validate business rule."""
        if not (1.0 <= self.sigma <= 5.0):
            raise ValueError(
                f"Invalid threshold: {self.sigma}σ. "
                f"Must be between 1.0 and 5.0 standard deviations."
            )
    
    @classmethod
    def default(cls) -> 'AnomalyThreshold':
        """Default threshold: 2.0σ (95% confidence)."""
        return cls(sigma=2.0)
    
    @classmethod
    def conservative(cls) -> 'AnomalyThreshold':
        """Conservative threshold: 3.0σ (99.7% confidence)."""
        return cls(sigma=3.0)
    
    @classmethod
    def aggressive(cls) -> 'AnomalyThreshold':
        """Aggressive threshold: 1.5σ (86% confidence)."""
        return cls(sigma=1.5)
    
    def is_anomaly(self, deviation_sigma: float) -> bool:
        """Check if deviation exceeds threshold."""
        return abs(deviation_sigma) >= self.sigma
    
    def __str__(self) -> str:
        return f"{self.sigma}σ"
```

**Git commit:**
```bash
git add src/domain/value_objects/anomaly_threshold.py
git commit -m "feat(domain): Add AnomalyThreshold value object"
```

#### 1.4 Tesztek (3 óra)

**Fájl:** `tests/domain/test_climate_anomaly.py`

```python
"""Unit tests for ClimateAnomaly entity."""
import pytest
from datetime import date, timedelta
from src.domain.entities.climate_anomaly import ClimateAnomaly

def test_create_climate_anomaly():
    """Test basic anomaly creation."""
    anomaly = ClimateAnomaly(
        location_name="Budapest",
        date=date(2024, 7, 15),
        parameter="temperature",
        measured_value=38.5,
        historical_mean=28.0,
        historical_std=3.5,
        deviation_sigma=3.0
    )
    
    assert anomaly.severity == "EXTREME"
    assert anomaly.is_extreme
    assert anomaly.is_positive_anomaly

def test_future_date_rejected():
    """Business Rule: Future dates not allowed."""
    future_date = date.today() + timedelta(days=1)
    
    with pytest.raises(ValueError, match="Future date not allowed"):
        ClimateAnomaly(
            location_name="Budapest",
            date=future_date,
            parameter="temperature",
            measured_value=38.5,
            historical_mean=28.0,
            historical_std=3.5,
            deviation_sigma=3.0
        )

def test_weak_anomaly_rejected():
    """Business Rule: Anomaly must be significant (>1σ)."""
    with pytest.raises(ValueError, match="Anomaly too weak"):
        ClimateAnomaly(
            location_name="Budapest",
            date=date(2024, 7, 15),
            parameter="temperature",
            measured_value=28.5,
            historical_mean=28.0,
            historical_std=3.5,
            deviation_sigma=0.14  # Too weak!
        )

def test_severity_classification():
    """Test anomaly severity classification."""
    # LOW (1-2σ)
    low = ClimateAnomaly(
        location_name="Test",
        date=date(2024, 1, 1),
        parameter="temp",
        measured_value=30.0,
        historical_mean=25.0,
        historical_std=2.5,
        deviation_sigma=1.8
    )
    assert low.severity == "LOW"
    
    # EXTREME (3+σ)
    extreme = ClimateAnomaly(
        location_name="Test",
        date=date(2024, 1, 1),
        parameter="temp",
        measured_value=30.0,
        historical_mean=20.0,
        historical_std=3.0,
        deviation_sigma=3.3
    )
    assert extreme.severity == "EXTREME"
    assert extreme.is_extreme
```

**Futtatás:**
```bash
pytest tests/domain/test_climate_anomaly.py -v
# Elvárt: 4/4 PASSED ✅
```

---

### **DAY 2: Domain Service - Anomaly Detector (8 óra)**

#### 2.1 Tiszta Domain Service (4 óra)

**Fájl:** `src/domain/services/anomaly_detector.py`

```python
"""
Domain Service - Anomaly Detector
==================================
PURE business logic for climate anomaly detection.

NO DEPENDENCIES on Infrastructure!
- No database access
- No API calls
- No file I/O

Just pure Python + statistics!
"""
from typing import List, Optional
from datetime import date
from ..entities.climate_anomaly import ClimateAnomaly
from ..value_objects.anomaly_threshold import AnomalyThreshold
import statistics

class AnomalyDetector:
    """
    Domain Service: Climate Anomaly Detection
    
    Implements the statistical algorithm for detecting climate anomalies
    based on historical data and standard deviation analysis.
    
    Business Rules:
    1. Baseline period must be at least 30 years (climatological standard)
    2. Anomaly = deviation > threshold * std_dev
    3. Historical mean/std calculated from baseline period only
    """
    
    def __init__(self, threshold: Optional[AnomalyThreshold] = None):
        """
        Initialize detector with threshold.
        
        Args:
            threshold: Anomaly detection threshold (default: 2.0σ)
        """
        self.threshold = threshold or AnomalyThreshold.default()
    
    def detect_temperature_anomalies(
        self,
        location_name: str,
        observations: List[tuple],  # (date, temperature)
        baseline_start: date,
        baseline_end: date
    ) -> List[ClimateAnomaly]:
        """
        Detect temperature anomalies using historical baseline.
        
        Business Logic:
        1. Calculate historical mean/std from baseline period
        2. For each observation, calculate deviation in σ
        3. If |deviation| > threshold → anomaly
        
        Args:
            location_name: Location identifier
            observations: List of (date, temperature) tuples
            baseline_start: Start of baseline period (e.g., 1970-01-01)
            baseline_end: End of baseline period (e.g., 2000-12-31)
        
        Returns:
            List of detected anomalies
        """
        # Step 1: Extract baseline observations
        baseline_temps = [
            temp for obs_date, temp in observations
            if baseline_start <= obs_date <= baseline_end and temp is not None
        ]
        
        if len(baseline_temps) < 365:  # At least 1 year of data
            raise ValueError(
                f"Insufficient baseline data: {len(baseline_temps)} observations. "
                f"Need at least 365 (1 year)."
            )
        
        # Step 2: Calculate baseline statistics
        historical_mean = statistics.mean(baseline_temps)
        historical_std = statistics.stdev(baseline_temps)
        
        if historical_std == 0:
            raise ValueError("Historical std deviation is 0 (no variation in baseline)")
        
        # Step 3: Detect anomalies
        anomalies = []
        
        for obs_date, temp in observations:
            if temp is None:
                continue
            
            # Calculate deviation in σ
            deviation_sigma = (temp - historical_mean) / historical_std
            
            # Check if anomaly
            if self.threshold.is_anomaly(deviation_sigma):
                try:
                    anomaly = ClimateAnomaly(
                        location_name=location_name,
                        date=obs_date,
                        parameter="temperature",
                        measured_value=temp,
                        historical_mean=historical_mean,
                        historical_std=historical_std,
                        deviation_sigma=deviation_sigma
                    )
                    anomalies.append(anomaly)
                except ValueError:
                    # Future date or weak anomaly - skip
                    continue
        
        return anomalies
    
    def detect_precipitation_anomalies(
        self,
        location_name: str,
        observations: List[tuple],  # (date, precipitation_mm)
        baseline_start: date,
        baseline_end: date
    ) -> List[ClimateAnomaly]:
        """
        Detect precipitation anomalies.
        
        Similar to temperature, but handles 0 values differently.
        """
        # Similar implementation...
        # (Rövidség kedvéért csak vázlat)
        pass
    
    def calculate_baseline_statistics(
        self,
        observations: List[tuple],
        baseline_start: date,
        baseline_end: date
    ) -> tuple:
        """
        Helper: Calculate baseline mean and std dev.
        
        Returns:
            (mean, std_dev)
        """
        baseline_values = [
            value for obs_date, value in observations
            if baseline_start <= obs_date <= baseline_end and value is not None
        ]
        
        if not baseline_values:
            raise ValueError("No baseline data available")
        
        return statistics.mean(baseline_values), statistics.stdev(baseline_values)
```

**Git commit:**
```bash
git add src/domain/services/anomaly_detector.py
git commit -m "feat(domain): Add pure AnomalyDetector service"
```

#### 2.2 Domain Service Unit Tests (4 óra)

**Fájl:** `tests/domain/test_anomaly_detector.py`

```python
"""Unit tests for AnomalyDetector service."""
import pytest
from datetime import date
from src.domain.services.anomaly_detector import AnomalyDetector
from src.domain.value_objects.anomaly_threshold import AnomalyThreshold

def test_detect_temperature_anomalies_simple():
    """Test basic anomaly detection."""
    detector = AnomalyDetector(threshold=AnomalyThreshold(sigma=2.0))
    
    # Baseline: normal temperatures (20-30°C, mean≈25°C, std≈3°C)
    observations = [
        (date(1990, 1, i), 25.0 + (i % 6) - 3)  # 22-28°C range
        for i in range(1, 366)  # 365 days
    ]
    
    # Add anomaly: 38°C (way above normal!)
    observations.append((date(1991, 7, 15), 38.0))
    
    anomalies = detector.detect_temperature_anomalies(
        location_name="Test City",
        observations=observations,
        baseline_start=date(1990, 1, 1),
        baseline_end=date(1990, 12, 31)
    )
    
    assert len(anomalies) >= 1
    assert any(a.date == date(1991, 7, 15) for a in anomalies)
    
    anomaly_38c = next(a for a in anomalies if a.date == date(1991, 7, 15))
    assert anomaly_38c.measured_value == 38.0
    assert anomaly_38c.is_positive_anomaly
    assert anomaly_38c.deviation_sigma > 2.0

def test_insufficient_baseline_data():
    """Business Rule: At least 365 observations required."""
    detector = AnomalyDetector()
    
    # Only 100 observations (not enough!)
    observations = [(date(1990, 1, i), 25.0) for i in range(1, 101)]
    
    with pytest.raises(ValueError, match="Insufficient baseline data"):
        detector.detect_temperature_anomalies(
            location_name="Test",
            observations=observations,
            baseline_start=date(1990, 1, 1),
            baseline_end=date(1990, 12, 31)
        )

def test_no_anomalies_in_normal_data():
    """Normal data should produce no anomalies."""
    detector = AnomalyDetector(threshold=AnomalyThreshold(sigma=2.0))
    
    # All normal temps (20-30°C)
    observations = [
        (date(1990, 1, i), 25.0 + (i % 6) - 3)
        for i in range(1, 366)
    ]
    
    anomalies = detector.detect_temperature_anomalies(
        location_name="Normal City",
        observations=observations,
        baseline_start=date(1990, 1, 1),
        baseline_end=date(1990, 12, 31)
    )
    
    assert len(anomalies) == 0  # No anomalies!
```

**Futtatás:**
```bash
pytest tests/domain/test_anomaly_detector.py -v
# Elvárt: PASSED ✅
```

---

### **DAY 3: Application Layer - Use Case (8 óra)**

#### 3.1 Repository Interface (Domain) (2 óra)

**Fájl:** `src/domain/repositories/weather_repository.py`

```python
"""
Domain Repository Interface - Weather Repository
=================================================
Port (interface) for weather data access.

This is a DOMAIN interface (no implementation details!)
Infrastructure layer will implement this.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from ..entities.climate_anomaly import ClimateAnomaly

class WeatherRepository(ABC):
    """
    Port: Weather data repository interface.
    
    Domain defines WHAT it needs.
    Infrastructure defines HOW to get it.
    """
    
    @abstractmethod
    def get_temperature_observations(
        self,
        location_name: str,
        start_date: date,
        end_date: date
    ) -> List[tuple]:
        """
        Get temperature observations for a location and period.
        
        Args:
            location_name: Location identifier
            start_date: Start of period
            end_date: End of period
        
        Returns:
            List of (date, temperature) tuples
        """
        pass
    
    @abstractmethod
    def save_anomalies(self, anomalies: List[ClimateAnomaly]) -> None:
        """
        Save detected anomalies.
        
        Args:
            anomalies: List of anomalies to save
        """
        pass
```

#### 3.2 Use Case (4 óra)

**Fájl:** `src/application/use_cases/detect_anomalies_use_case.py`

```python
"""
Application Use Case - Detect Anomalies
========================================
Orchestrates anomaly detection workflow.

Responsibilities:
1. Fetch data (via repository)
2. Apply domain service (AnomalyDetector)
3. Save results (via repository)
4. Report progress
"""
from typing import List, Optional, Callable
from datetime import date
from ...domain.services.anomaly_detector import AnomalyDetector
from ...domain.repositories.weather_repository import WeatherRepository
from ...domain.entities.climate_anomaly import ClimateAnomaly
from ...domain.value_objects.anomaly_threshold import AnomalyThreshold

class DetectAnomaliesUseCase:
    """
    Use Case: Detect Climate Anomalies
    
    Coordinates anomaly detection process:
    - Fetches weather data
    - Applies detection algorithm
    - Saves results
    """
    
    def __init__(
        self,
        weather_repository: WeatherRepository,
        anomaly_detector: Optional[AnomalyDetector] = None
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            weather_repository: Repository for weather data access
            anomaly_detector: Domain service (optional, creates default)
        """
        self.weather_repo = weather_repository
        self.detector = anomaly_detector or AnomalyDetector()
    
    def execute(
        self,
        location_name: str,
        analysis_start: date,
        analysis_end: date,
        baseline_start: date,
        baseline_end: date,
        threshold: Optional[AnomalyThreshold] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[ClimateAnomaly]:
        """
        Execute anomaly detection use case.
        
        Args:
            location_name: Location to analyze
            analysis_start: Start of analysis period
            analysis_end: End of analysis period
            baseline_start: Start of baseline period (e.g., 1970)
            baseline_end: End of baseline period (e.g., 2000)
            threshold: Detection threshold (optional)
            progress_callback: Progress reporting function (optional)
        
        Returns:
            List of detected anomalies
        """
        # Step 1: Fetch weather data (Infrastructure)
        if progress_callback:
            progress_callback(0.0)
        
        observations = self.weather_repo.get_temperature_observations(
            location_name=location_name,
            start_date=baseline_start,  # Need baseline + analysis data!
            end_date=analysis_end
        )
        
        if progress_callback:
            progress_callback(0.5)  # 50% - data fetched
        
        # Step 2: Apply domain service (Domain)
        if threshold:
            self.detector.threshold = threshold
        
        anomalies = self.detector.detect_temperature_anomalies(
            location_name=location_name,
            observations=observations,
            baseline_start=baseline_start,
            baseline_end=baseline_end
        )
        
        if progress_callback:
            progress_callback(0.8)  # 80% - detection complete
        
        # Step 3: Save results (Infrastructure)
        self.weather_repo.save_anomalies(anomalies)
        
        if progress_callback:
            progress_callback(1.0)  # 100% - done!
        
        return anomalies
```

**Git commit:**
```bash
git add src/application/use_cases/detect_anomalies_use_case.py
git commit -m "feat(application): Add DetectAnomaliesUseCase"
```

---

### **DAY 4-5: Infrastructure Layer (16 óra)**

#### 4.1 Repository Implementation (8 óra)

**Fájl:** `src/infrastructure/repositories/sqlite_weather_repository.py`

```python
"""
Infrastructure Adapter - SQLite Weather Repository
==================================================
Implements WeatherRepository interface using SQLite.
"""
import sqlite3
from typing import List
from datetime import date
from ...domain.repositories.weather_repository import WeatherRepository
from ...domain.entities.climate_anomaly import ClimateAnomaly

class SQLiteWeatherRepository(WeatherRepository):
    """SQLite implementation of WeatherRepository."""
    
    def __init__(self, db_path: str):
        """
        Initialize repository with database path.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def get_temperature_observations(
        self,
        location_name: str,
        start_date: date,
        end_date: date
    ) -> List[tuple]:
        """Fetch temperature data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT date, temperature_2m_max
            FROM weather_observations
            WHERE location = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """
        
        cursor.execute(query, (location_name, start_date, end_date))
        results = cursor.fetchall()
        conn.close()
        
        # Convert to (date, float) tuples
        observations = [
            (date.fromisoformat(row[0]), float(row[1]))
            for row in results if row[1] is not None
        ]
        
        return observations
    
    def save_anomalies(self, anomalies: List[ClimateAnomaly]) -> None:
        """Save anomalies to database."""
        if not anomalies:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS climate_anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                parameter TEXT NOT NULL,
                measured_value REAL NOT NULL,
                historical_mean REAL NOT NULL,
                historical_std REAL NOT NULL,
                deviation_sigma REAL NOT NULL,
                severity TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert anomalies
        for anomaly in anomalies:
            cursor.execute("""
                INSERT INTO climate_anomalies 
                (location, date, parameter, measured_value, historical_mean, 
                 historical_std, deviation_sigma, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                anomaly.location_name,
                anomaly.date.isoformat(),
                anomaly.parameter,
                anomaly.measured_value,
                anomaly.historical_mean,
                anomaly.historical_std,
                anomaly.deviation_sigma,
                anomaly.severity
            ))
        
        conn.commit()
        conn.close()
```

#### 4.2 Integration Tests (8 óra)

**Fájl:** `tests/integration/test_detect_anomalies_integration.py`

```python
"""Integration test: Full anomaly detection flow."""
import pytest
import tempfile
import sqlite3
from datetime import date
from src.domain.services.anomaly_detector import AnomalyDetector
from src.application.use_cases.detect_anomalies_use_case import DetectAnomaliesUseCase
from src.infrastructure.repositories.sqlite_weather_repository import SQLiteWeatherRepository

@pytest.fixture
def temp_db():
    """Create temporary database with test data."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_file.name
    temp_file.close()
    
    # Create schema and insert test data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE weather_observations (
            location TEXT,
            date TEXT,
            temperature_2m_max REAL
        )
    """)
    
    # Insert baseline data (1990: normal temps)
    for i in range(1, 366):
        cursor.execute("""
            INSERT INTO weather_observations VALUES ('Budapest', ?, ?)
        """, (f"1990-{i:03d}", 25.0 + (i % 6) - 3))
    
    # Insert anomaly (1991: 38°C heatwave!)
    cursor.execute("""
        INSERT INTO weather_observations VALUES ('Budapest', '1991-07-15', 38.0)
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    import os
    os.unlink(db_path)

def test_full_anomaly_detection_flow(temp_db):
    """Test complete flow: Repository → Use Case → Domain Service."""
    # Arrange
    repository = SQLiteWeatherRepository(db_path=temp_db)
    detector = AnomalyDetector()
    use_case = DetectAnomaliesUseCase(
        weather_repository=repository,
        anomaly_detector=detector
    )
    
    # Act
    anomalies = use_case.execute(
        location_name="Budapest",
        analysis_start=date(1991, 1, 1),
        analysis_end=date(1991, 12, 31),
        baseline_start=date(1990, 1, 1),
        baseline_end=date(1990, 12, 31)
    )
    
    # Assert
    assert len(anomalies) >= 1
    assert any(a.date == date(1991, 7, 15) for a in anomalies)
    
    # Verify saved to database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM climate_anomalies")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count >= 1  # Saved successfully!
```

---

### **DAY 6-7: Integration + Deprecation (16 óra)**

#### 6.1 Backward Compatibility Wrapper (4 óra)

**Fájl:** `src/data/anomaly_profile_manager.py` (MÓDOSÍTÁS!)

```python
"""
DEPRECATED: AnomalyProfileManager
==================================
⚠️ This class is DEPRECATED and kept only for backward compatibility!

NEW CODE should use:
- src/domain/services/anomaly_detector.py (Domain)
- src/application/use_cases/detect_anomalies_use_case.py (Application)
- src/infrastructure/repositories/sqlite_weather_repository.py (Infrastructure)

This wrapper delegates to the new Clean Architecture implementation.
"""
import warnings
from datetime import date
from typing import List
from ..domain.services.anomaly_detector import AnomalyDetector
from ..domain.value_objects.anomaly_threshold import AnomalyThreshold
from ..application.use_cases.detect_anomalies_use_case import DetectAnomaliesUseCase
from ..infrastructure.repositories.sqlite_weather_repository import SQLiteWeatherRepository

class AnomalyProfileManager:
    """
    DEPRECATED: Use DetectAnomaliesUseCase instead!
    
    This is a compatibility wrapper for old code.
    """
    
    def __init__(self, db_path: str):
        warnings.warn(
            "AnomalyProfileManager is deprecated. "
            "Use DetectAnomaliesUseCase instead!",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Delegate to new implementation
        repository = SQLiteWeatherRepository(db_path)
        detector = AnomalyDetector()
        self.use_case = DetectAnomaliesUseCase(repository, detector)
    
    def detect_anomalies(
        self,
        location: str,
        start_date: date,
        end_date: date
    ) -> List:
        """DEPRECATED: Use use_case.execute() instead!"""
        # Delegate to new use case
        return self.use_case.execute(
            location_name=location,
            analysis_start=start_date,
            analysis_end=end_date,
            baseline_start=date(1970, 1, 1),  # Default baseline
            baseline_end=date(2000, 12, 31)
        )
```

#### 6.2 Documentation (4 óra)

**Fájl:** `docs/CLEAN_ARCHITECTURE_MIGRATION.md`

```markdown
# Clean Architecture Migration Guide

## ✅ PILOT PROJECT: Anomaly Detection (DONE!)

### What Changed?

**BEFORE:**
```python
# OLD CODE (DEPRECATED):
from src.data.anomaly_profile_manager import AnomalyProfileManager

manager = AnomalyProfileManager(db_path="weather.db")
anomalies = manager.detect_anomalies("Budapest", start, end)
```

**AFTER:**
```python
# NEW CODE (Clean Architecture):
from src.domain.services.anomaly_detector import AnomalyDetector
from src.domain.value_objects.anomaly_threshold import AnomalyThreshold
from src.application.use_cases.detect_anomalies_use_case import DetectAnomaliesUseCase
from src.infrastructure.repositories.sqlite_weather_repository import SQLiteWeatherRepository

# Setup (usually done in DI container)
repository = SQLiteWeatherRepository(db_path="weather.db")
detector = AnomalyDetector(threshold=AnomalyThreshold.default())
use_case = DetectAnomaliesUseCase(repository, detector)

# Execute
anomalies = use_case.execute(
    location_name="Budapest",
    analysis_start=date(2024, 1, 1),
    analysis_end=date(2024, 12, 31),
    baseline_start=date(1970, 1, 1),
    baseline_end=date(2000, 12, 31)
)
```

### Why Better?

1. ✅ **AI-friendly**: Domain logic in `src/domain/services/anomaly_detector.py`
2. ✅ **Testable**: No DB dependency in Domain layer
3. ✅ **Flexible**: Easy to swap SQLite → PostgreSQL
4. ✅ **Clear**: Each layer has one responsibility

### Migration Path

1. **Phase 1 (Week 1)**: New code uses new structure ✅ DONE!
2. **Phase 2 (Week 2-4)**: Migrate existing code gradually
3. **Phase 3 (Week 5+)**: Remove deprecated wrappers

### For AI Assistants (Codex, Claude Code)

When working on anomaly detection:
- **Domain logic**: `src/domain/services/anomaly_detector.py`
- **Use cases**: `src/application/use_cases/detect_anomalies_use_case.py`
- **DB access**: `src/infrastructure/repositories/sqlite_weather_repository.py`

**DON'T** touch `src/data/anomaly_profile_manager.py` (deprecated!)
```

#### 6.3 CI/CD Pipeline (4 óra)

**.github/workflows/test.yml**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run Domain Tests
      run: |
        pytest tests/domain/ -v --cov=src/domain
    
    - name: Run Application Tests
      run: |
        pytest tests/application/ -v --cov=src/application
    
    - name: Run Integration Tests
      run: |
        pytest tests/integration/ -v
    
    - name: Check Coverage
      run: |
        pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

#### 6.4 Final Testing + Demo (4 óra)

**Manual Testing Script:**

```python
# test_pilot_manual.py
"""Manual test script for pilot refactoring."""
from datetime import date
from src.domain.services.anomaly_detector import AnomalyDetector
from src.domain.value_objects.anomaly_threshold import AnomalyThreshold
from src.application.use_cases.detect_anomalies_use_case import DetectAnomaliesUseCase
from src.infrastructure.repositories.sqlite_weather_repository import SQLiteWeatherRepository

def main():
    print("🚀 PILOT REFACTOR - Manual Test")
    print("=" * 50)
    
    # Setup
    repository = SQLiteWeatherRepository(db_path="data/weather.db")
    detector = AnomalyDetector(threshold=AnomalyThreshold(sigma=2.5))
    use_case = DetectAnomaliesUseCase(repository, detector)
    
    # Execute
    print("🔍 Detecting anomalies for Budapest...")
    
    anomalies = use_case.execute(
        location_name="Budapest",
        analysis_start=date(2023, 1, 1),
        analysis_end=date(2023, 12, 31),
        baseline_start=date(1970, 1, 1),
        baseline_end=date(2000, 12, 31),
        progress_callback=lambda p: print(f"   Progress: {p*100:.0f}%")
    )
    
    print(f"\n✅ Found {len(anomalies)} anomalies!")
    
    if anomalies:
        print("\n📊 Top 5 Anomalies:")
        for anomaly in sorted(anomalies, key=lambda a: abs(a.deviation_sigma), reverse=True)[:5]:
            print(f"  - {anomaly}")
    
    print("\n🎉 Pilot refactoring SUCCESS!")

if __name__ == "__main__":
    main()
```

**Run:**
```bash
python test_pilot_manual.py
```

---

## 📊 SUCCESS METRICS

### **BEFORE Pilot (Baseline):**
- ❌ Anomaly logic in 635-sor God Class
- ❌ AI nem tudja, hol van a core logic
- ❌ Unit test lehetetlen (DB dependency)
- ❌ Test coverage: ~30%

### **AFTER Pilot (Expected):**
- ✅ Anomaly logic 150-sor pure Domain Service
- ✅ AI TUDJA: `src/domain/services/anomaly_detector.py`
- ✅ Unit test KÖNNYŰ (no DB!)
- ✅ Test coverage: ~90% (domain layer)

### **AI Promptok Javulása:**

**BEFORE:**
```
Prompt: "Add új anomaly threshold típust!"
AI: "Hol van az anomaly logic? anomaly_profile_manager.py? 
     635 sor... nem tudom hova írjak..."
Result: ❌ FAIL
```

**AFTER:**
```
Prompt: "Add új anomaly threshold típust!"
AI: "Aha! src/domain/value_objects/anomaly_threshold.py!
     Hozzáadok egy .lenient() class methodot!"
Result: ✅ SUCCESS!
```

---

## 🎯 KÖVETKEZŐ LÉPÉSEK (HA SIKER)

1. **Week 2-3**: `wind_analysis.py` refactor (már majdnem jó!)
2. **Week 4-6**: `MultiCityEngine` God Class szétszedés
3. **Week 7-12**: Teljes projekt refactor

**HA FAIL:**
- Visszaadjuk a pilot változtatásokat
- Status quo
- Tanulság levonás

---

## 📝 GIT WORKFLOW

```bash
# Create feature branch
git checkout -b pilot/clean-architecture-anomaly-detection

# Daily commits (napi 2-3 commit)
git add ...
git commit -m "feat(domain): Add ClimateAnomaly entity"

# End of week: merge
git checkout main
git merge pilot/clean-architecture-anomaly-detection
git push origin main
```

---

## ✅ CHECKLIST

### Day 1:
- [ ] Folder structure created
- [ ] ClimateAnomaly entity + tests
- [ ] AnomalyThreshold value object + tests
- [ ] Git commits: 3+

### Day 2:
- [ ] AnomalyDetector service
- [ ] Domain service unit tests
- [ ] Coverage >90% for domain layer
- [ ] Git commits: 2+

### Day 3:
- [ ] WeatherRepository interface
- [ ] DetectAnomaliesUseCase
- [ ] Use case tests
- [ ] Git commits: 2+

### Day 4-5:
- [ ] SQLiteWeatherRepository implementation
- [ ] Integration tests
- [ ] All tests passing
- [ ] Git commits: 4+

### Day 6-7:
- [ ] Backward compatibility wrapper
- [ ] Documentation
- [ ] CI/CD pipeline
- [ ] Manual testing + demo
- [ ] Git commits: 3+

### Final:
- [ ] All tests passing (domain + application + integration)
- [ ] Coverage >80%
- [ ] Documentation complete
- [ ] Demo successful
- [ ] PILOT SUCCESS! 🎉

---

**INDULÁS:** Kezdjük a Day 1-gyel! 🚀
