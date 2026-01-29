# Clean Architecture Refactor Plan (CA_REFAKTOR_PLAN)
**Verzió:** 4.0 | **Progress:** 0% | **Utolsó frissítés:** 2026-01-29
**Analízis forrás:** CA_ANALYSIS_ACCURATE.md (2026-01-29)

---

## 🎯 CÉL: Tiszta Clean Architecture Projekt

**Végső állapot:**
- Minden réteg csak a belső rétegeitől függhet
- Domain → Application → (Infrastructure/Data/Analytics/API) → Presentation
- Ports/Adapters pattern minden külső függőségnél
- Nincs "outer → inner" import

---

## 📊 JELENLEGI ÁLLAPOT (CA_ANALYSIS_ACCURATE.md alapján)

### Összefoglaló Violations

| Forrás Réteg | Cél Réteg | Darab | Státusz |
|--------------|-----------|-------|---------|
| Domain → outer | 0 | ✅ TISZTA |
| Application → data | 2 | ❌ JAVÍTANDÓ |
| API → analytics/infra/data | 12 | ❌ JAVÍTANDÓ |
| Presentation → data/analytics | 31 | ❌ JAVÍTANDÓ |
| Analytics → infra/data | 2 | ❌ JAVÍTANDÓ |
| **Összesen** | | **47** | |

---

## 🔍 DETAILS - MINDEN CA SÉRTÉS

### 1) APPLICATION → DATA (2 violations)

```
src/application/use_cases/analyze_multi_city.py:8-9
├── from src.data.enums import AnalyticsMetric, DataSource, QuestionType, RegionScope
├── from src.data.models import AnalyticsQuestion, AnalyticsResult, CityWeatherResult
```

**Probléma:** Application layer közvetlenül importál Data layerből

**Javítási stratégia:**
- Port interfészek létrehozása a Domain/Analytics rétegben
- Data layer implementálja ezeket az interfészeket
- Dependency injection through Application layer

---

### 2) API → ANALYTICS/INFRASTRUCTURE/DATA (12 violations)

```
src/api/routes/cities.py:8-9
src/api/routes/detailed_city.py:9,18
src/api/routes/single_city.py:9,18
src/api/routes/anomalies.py:11,19
src/api/routes/metadata.py:6-7
src/api/routes/weather.py:8,17
├── from src.analytics.multi_city_engine import MultiCityEngine
├── from src.infrastructure.repositories.city_repository import CityRepository
└── from src.data.enums import AnalyticsMetric
```

**Probléma:** API routes közvetlenül használják az analytics/infrastructure/data rétegeket

**Javítási stratégia:**
- Use Case-ek létrehozása az Application layerben
- API routes csak Application use case-eket hívnak
- Infrastructure/Data implementációk injectálva

---

### 3) PRESENTATION → DATA/ANALYTICS (31 violations)

#### 3.1) hungarian_map_tab (3 violations)

```
src/presentation/gui/hungarian_map_tab/map_widget.py:8
src/presentation/gui/hungarian_map_tab/initialization.py:20
src/presentation/gui/hungarian_map_tab/core.py:17-18
├── from src.data.models import AnalyticsResult
└── from src.analytics.multi_city_engine import MultiCityEngine
```

#### 3.2) weather_data_bridge (3 violations)

```
src/presentation/gui/weather_data_bridge/constants.py:2
src/presentation/gui/weather_data_bridge/core.py:6-7
├── from src.data.enums import AnalyticsMetric
└── from src.data.models import AnalyticsQuestion, AnalyticsResult, CityWeatherResult
```

#### 3.3) universal_location_selector (3 violations)

```
src/presentation/gui/universal_location_selector/search_handler.py:23
src/presentation/gui/universal_location_selector/core.py:27-28
src/presentation/gui/universal_location_selector/public_api.py:23
├── from src.data.city_manager import City, CityManager
└── from src.data.models import LocationType, UniversalLocation
```

#### 3.4) control_panel (1 violation)

```
src/presentation/gui/control_panel/core.py:37
├── from src.data.city_manager import CityManager
```

#### 3.5) workers/analysis_worker (3 violations)

```
src/presentation/gui/workers/analysis_worker/core.py:18-20
├── from src.analytics.multi_city_engine import MultiCityEngine
├── from src.data.enums import AnalysisType, DataProvider
└── from src.data.weather_client import WeatherClient
```

#### 3.6) analytics/analytics_view (1 violation)

```
src/presentation/gui/analytics/analytics_view/multi_city_handler.py:65
├── from src.data.enums import AnalyticsMetric
```

#### 3.7) trend_analytics/trend_data_processor (2 violations)

```
src/presentation/gui/trend_analytics/trend_data_processor/core.py:7-8
├── from src.data.city_manager import CityManager
└── from src.data.weather_client import WeatherClient
```

#### 3.8) results_panel/windy_days_tab (4 violations)

```
src/presentation/gui/results_panel/windy_days_tab/core.py:21
src/presentation/gui/results_panel/windy_days_tab/data_processor.py:19
src/presentation/gui/results_panel/windy_days_tab/ui_builder.py:31
src/presentation/gui/results_panel/windy_days_tab/handlers.py:20
└── from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH
```

#### 3.9) panel_widgets/location_widget (3 violations)

```
src/presentation/gui/panel_widgets/location_widget/core.py:13-14
src/presentation/gui/panel_widgets/location_widget/signal_handlers.py:10
├── from src.data.city_manager import CityManager
└── from src.data.models import UniversalLocation
```

#### 3.10) panel_widgets/multi_city_widget (1 violation)

```
src/presentation/gui/panel_widgets/multi_city_widget/core.py:23
└── from src.data.city_manager import CityManager
```

#### 3.11) dialogs/anomaly_settings_dialog (1 violation)

```
src/presentation/gui/dialogs/anomaly_settings_dialog/core.py:14
└── from src.data.anomaly_profile_manager import AnomalyProfileManager
```

#### 3.12) hungarian_location_selector (1 violation)

```
src/presentation/gui/hungarian_location_selector/mixins/signal_handlers.py:220
└── from src.data.models import Location
```

#### 3.13) windows/main_window_actions (1 violation)

```
src/presentation/gui/windows/main_window_actions/navigation.py:79
└── from src.analytics.multi_city_engine import MultiCityEngine
```

---

### 4) ANALYTICS → INFRASTRUCTURE/DATA (2 violations)

```
src/analytics/multi_city_engine_core.py:21,86
├── from src.infrastructure.repositories.city_repository import CityRepository
└── from src.data.weather_client import WeatherClient
```

---

## 🛠️ JAVÍTÁSI STRATÉGIA

### FÁZIS 1: Port Interfészek Létrehozása

#### 1.1) Data Layer Ports (Domain/Analytics rétegbe)
```
src/domain/ports/
├── data_ports.py          # AnalyticsMetric, DataSource, stb. portok
├── repository_ports.py    # CityRepository protocol
├── weather_ports.py       # WeatherClient protocol
└── profile_ports.py       # AnomalyProfileManager protocol
```

#### 1.2) Analytics Layer Ports
```
src/analytics/ports/
├── engine_ports.py        # MultiCityEngine protocol
├── wind_ports.py          # Wind analysis port
└── multi_city_ports.py    # Multi-city operations
```

#### 1.3) Application Layer Ports
```
src/application/ports/
├── analytics_ports.py     # Analytics operations
└── city_ports.py          # City operations
```

### FÁZIS 2: Infrastructure/Data Implementációk

#### 2.1) Data Layer → Port Implementációk
```
src/data/implementations/
├── analytics_metric_impl.py
├── city_repository_impl.py
├── weather_client_impl.py
└── anomaly_profile_impl.py
```

#### 2.2) Analytics Layer → Port Implementációk
```
src/analytics/implementations/
├── multi_city_engine_impl.py
└── wind_analysis_impl.py
```

### FÁZIS 3: Dependency Injection Container

```
src/core/di_container.py
├── register_data_ports()
├── register_analytics_ports()
├── get_port(PortType)
└── inject_dependencies(target)
```

### FÁZIS 4: Rétegek Átírása

#### 4.1) Application Layer javítás
```python
# ELŐTTE (CA violation):
from src.data.enums import AnalyticsMetric

# UTÁNA (CA compliant):
from domain.ports.data_ports import AnalyticsMetricPort
from infrastructure.data.implementations import AnalyticsMetricImpl

class AnalyzeMultiCityUseCase:
    def __init__(self, metric_repo: AnalyticsMetricPort):
        self.metric_repo = metric_repo
```

#### 4.2) API Layer javítás
```python
# ELŐTTE (CA violation):
from src.analytics.multi_city_engine import MultiCityEngine

# UTÁNA (CA compliant):
from application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase

# API csak Application use case-eket hív
```

#### 4.3) Presentation Layer javítás
```python
# ELŐTTE (CA violation):
from src.data.city_manager import CityManager

# UTÁNA (CA compliant):
from core.di_container import get_port
from domain.ports.data_ports import CityManagerPort

class LocationWidget:
    def __init__(self):
        self.city_manager = get_port(CityManagerPort)
```

---

## 📋 FELADAT LISTA

### FÁZIS 1: Port Interfészek (Port -> Impl mapping)

| # | Port fájl | Implementálja | Státusz |
|---|-----------|---------------|---------|
| 1 | `domain/ports/data_ports.py` | `data/enums/*.py` | ⏳ |
| 2 | `domain/ports/repository_ports.py` | `infrastructure/repositories/` | ⏳ |
| 3 | `domain/ports/weather_ports.py` | `data/weather_client.py` | ⏳ |
| 4 | `analytics/ports/engine_ports.py` | `analytics/multi_city_engine*.py` | ⏳ |
| 5 | `analytics/ports/wind_ports.py` | `analytics/wind_analysis.py` | ⏳ |
| 6 | `application/ports/analytics_ports.py` | `application/use_cases/` | ⏳ |

### FÁZIS 2: Infrastructure/Data Implementációk

| # | Implementáció | Függ | Státusz |
|---|---------------|------|---------|
| 1 | `data/implementations/enums_impl.py` | - | ⏳ |
| 2 | `data/implementations/models_impl.py` | - | ⏳ |
| 3 | `analytics/implementations/engine_impl.py` | data, infra | ⏳ |
| 4 | `application/implementations/use_cases_impl.py` | domain, analytics | ⏳ |

### FÁZIS 3: DI Container

| # | Component | Státusz |
|---|-----------|---------|
| 1 | `core/di_container.py` | ⏳ |
| 2 | `core/config.py` | ⏳ |

### FÁZIS 4: API Routes javítás

| # | Fájl | Violations | Státusz |
|---|------|------------|---------|
| 1 | `routes/cities.py` | 2 | ⏳ |
| 2 | `routes/detailed_city.py` | 2 | ⏳ |
| 3 | `routes/single_city.py` | 2 | ⏳ |
| 4 | `routes/anomalies.py` | 2 | ⏳ |
| 5 | `routes/metadata.py` | 2 | ⏳ |
| 6 | `routes/weather.py` | 2 | ⏳ |

### FÁZIS 5: Presentation GUI javítás

| # | Component | Violations | Státusz |
|---|-----------|------------|---------|
| 1 | `hungarian_map_tab/` | 3 | ⏳ |
| 2 | `weather_data_bridge/` | 3 | ⏳ |
| 3 | `universal_location_selector/` | 3 | ⏳ |
| 4 | `control_panel/` | 1 | ⏳ |
| 5 | `workers/analysis_worker/` | 3 | ⏳ |
| 6 | `analytics/analytics_view/` | 1 | ⏳ |
| 7 | `trend_analytics/` | 2 | ⏳ |
| 8 | `results_panel/windy_days_tab/` | 4 | ⏳ |
| 9 | `panel_widgets/location_widget/` | 3 | ⏳ |
| 10 | `panel_widgets/multi_city_widget/` | 1 | ⏳ |
| 11 | `dialogs/anomaly_settings/` | 1 | ⏳ |
| 12 | `hungarian_location_selector/` | 1 | ⏳ |
| 13 | `windows/main_window_actions/` | 1 | ⏳ |

### FÁZIS 6: Analytics Layer javítás

| # | Fájl | Violations | Státusz |
|---|------|------------|---------|
| 1 | `multi_city_engine_core.py` | 2 | ⏳ |

---

## 🧪 VALIDÁCIÓ

### Teszt script (CA validate után)
```bash
# 1. Tesztek futtatása
python -m pytest tests/ -q

# 2. CA analízis újrafuttatása
python scripts/ca_analysis.py --output CA_ANALYSIS_AFTER_FIX.md

# 3. Ellenőrzés
if grep -q "None found" CA_ANALYSIS_AFTER_FIX.md; then
    echo "✅ CA COMPLIANT!"
else
    echo "❌ Még vannak violations"
fi
```

---

## 📁 ÚJ PROJEKT STRUKTÚRA (CÉL ÁLLAPOT)

```
src/
├── domain/                    # BELSŐ - legbelső réteg
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── ports/                 # 🔴 PORTOK (interfészek)
│       ├── data_ports.py
│       ├── repository_ports.py
│       └── weather_ports.py
│
├── application/               # USE CASES
│   ├── use_cases/
│   │   ├── analyze_multi_city.py
│   │   └── detect_anomalies.py
│   └── ports/                 # Application portok
│       └── analytics_ports.py
│
├── analytics/                 # ANALYTICS OPERATIONS
│   ├── models/
│   ├── services/
│   ├── statistics/
│   └── ports/                 # Analytics portok
│       ├── engine_ports.py
│       └── wind_ports.py
│
├── infrastructure/            # KÜLSŐ - Infrastructure
│   └── repositories/
│       └── city_repository.py # Implementálja: repository_ports.py
│
├── data/                      # DATA LAYER
│   ├── enums.py               # Implementálja: data_ports.py
│   ├── models.py              # Implementálja: data_ports.py
│   ├── weather_client.py      # Implementálja: weather_ports.py
│   └── anomaly_profile_manager.py
│
├── api/                       # API LAYER
│   └── routes/                # Csak application use case-eket hív
│       ├── cities.py
│       ├── single_city.py
│       └── ...
│
├── presentation/              # PRESENTATION LAYER
│   └── gui/
│       ├── windows/
│       ├── panels/
│       ├── charts/
│       └── dialogs/
│
└── core/                      # SHARED
    ├── di_container.py        # 🔴 DEPENDENCY INJECTION
    └── config.py
```

---

## 🚀 STARTUP CHECKLIST

```bash
# 1. CA analízis futtatása
python scripts/ca_analysis.py

# 2. Violations számlálása
echo "Domain → outer: $(grep 'Domain depends on outer' report.md -A5 | grep -c 'None')"
echo "Application → outer: $(grep 'Application depends on outer' report.md -A5 | grep -c 'from src\.' | head -1)"
# ... stb

# 3. Tesztek
python -m pytest tests/ -q

# 4. GUI smoke test
python -c "
from src.presentation.gui.windows.main_window import MainWindow
from PySide6.QtWidgets import QApplication
app = QApplication([])
window = MainWindow()
print('GUI ELINDULT')
"
```

---

## 📝 VERSION HISTORY

| Verzió | Dátum | Változás |
|--------|-------|----------|
| 3.33 | 2026-01-28 | ~85% progress - GUI indult, fájlok bontva |
| 4.0 | 2026-01-29 | **TELJES ÚJRAÍRÁS** - CA violations javítása |

---

**Cél: 100% Clean Architecture Compliant Project** 🎯

---

*"A Clean Architecture nem csak elv, hanem karbantarthatóság."*
