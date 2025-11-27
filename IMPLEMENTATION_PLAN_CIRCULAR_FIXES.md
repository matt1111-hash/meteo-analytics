# 🔥 CIRCULAR DEPENDENCY FIX - IMPLEMENTATION PLAN

## 📋 FORRÁS ANALYSIS

### A valós circular dependency:

```
src/gui/results_panel/utils.py → from ..utils import AnomalyConstants
ni: src/gui/utils.py is trying to accessed from src/gui/results_panel/utils.py
src/gui/utils.py → from src.gui.theme_manager import get_theme_manager (Line 271)
src/gui/theme_manager.py → from src.gui.color_palette import ColorPalette (Line 35)
```

### 2️⃣ Self-import (NEM circular):
```
src/gui/results_panel/results_panel.py → from .utils import DataFrameExtractor (Line 47)
✅ EZ JÓ (own sub-module import)
```

---

## 🎯 SOLUTION STRATEGY

### 1. Dependency Injection (Interface Segregation)

**Step 1: Create Interface Layer**
```bash
# Create: src/gui/interfaces.py
touch /home/tibor/PythonProjects/Jules/global_weather_analyzer/src/gui/interfaces.py
```

**Content:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI Component Interfaces - Dependency Injection Pattern
🚀 SOLID: Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IAnomalyConstants(ABC):
    """Abstract interface for anomaly constants."""

    @property
    @abstractmethod
    def WIND_HIGH_THRESHOLD(self) -> float:
        """High wind threshold in km/h."""
        pass

    @property
    @abstractmethod
    def WIND_EXTREME_THRESHOLD(self) -> float:
        """Extreme wind threshold in km/h."""
        pass

    @property
    @abstractmethod
    def WIND_HURRICANE_THRESHOLD(self) -> float:
        """Hurricane force wind threshold in km/h."""
        pass


class IConstantsProvider(ABC):
    """Abstract interface for constants provider."""

    @abstractmethod
    def get_wind_threshold(self, threshold_type: str) -> float:
        """Get wind threshold by type."""
        pass

    @abstractmethod
    def get_all_thresholds(self) -> Dict[str, float]:
        """Get all available thresholds."""
        pass


class IWindspeedConstants(ABC):
    """Specific interface for wind constants."""

    @property
    @abstractmethod
    def HIGH(self) -> float:
        """High wind threshold."""
        pass

    @property
    @abstractmethod
    def EXTREME(self) -> float:
        """Extreme wind threshold."""
        pass
```

**Step 2: Create Constants Provider**
```bash
# Create: src/gui/constants_provider.py
touch /home/tibor/PythonProjects/Jules/global_weather_analyzer/src/gui/constants_provider.py
```

**Content:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants Provider - Dependency Injection Implementation
🎯 Single Responsibility Principle
"""

from typing import Dict, Any
from src.gui.interfaces import IConstantsProvider, IAnomalyConstants, IWindspeedConstants

class ConstantsProvider(IConstantsProvider):
    """Concrete implementation of constants provider."""

    def __init__(self):
        # Wind thresholds (moved from utils to here)
        self._wind_thresholds = {
            'high': 70.0,      # WIND_HIGH_THRESHOLD
            'extreme': 100.0,  # WIND_EXTREME_THRESHOLD
            'hurricane': 120.0  # WIND_HURRICANE_THRESHOLD
        }

    def get_wind_threshold(self, threshold_type: str) -> float:
        """Get wind threshold by type."""
        return self._wind_thresholds.get(threshold_type, 70.0)

    def get_all_thresholds(self) -> Dict[str, float]:
        """Get all available thresholds."""
        return self._wind_thresholds.copy()


class WindspeedConstantsAdapter(IWindspeedConstants):
    """Adapter to provide windspeed constants via interface."""

    @property
    def HIGH(self) -> float:
        """High wind threshold."""
        return 70.0

    @property
    def EXTREME(self) -> float:
        """Extreme wind threshold."""
        return 100.0
```

### 2. Refactor WindGustsAnalyzer (Remove Direct Import)

**Modify:** `/home/tibor/PythonProjects/Jules/global_weather_analyzer/src/gui/results_panel/utils.py`

**Changes:**
```python
# LINES TO CHANGE: Remove problematic import
# ❌ REMOVE LINE 305: from ..utils import AnomalyConstants

# ✅ ADD imports at top:
# Interface imports (breaks circular dependency)
from src.gui.interfaces import IConstantsProvider, IWindspeedConstants
from src.gui.constants_provider import ConstantsProvider, WindspeedConstantsAdapter
```

**Add Dependency Injection to WindGustsAnalyzer:**
```python
class WindGustsAnalyzer:
    """🌪️ Széllökés elemzéséért felelős utility osztály. Dependency injection pattern."""

    def __init__(self, constants_provider: Optional['IConstantsProvider'] = None):
        """Initialize with injected constants provider."""
        self.constants_provider = constants_provider or ConstantsProvider()
        self.windspeed_constants = ("wind_constants_provider or WindspeedConstantsAdapter")

    # REFACTORED METHODS:
    @staticmethod
    def categorize_wind_gust(wind_speed: float, data_source: str = 'wind_gusts_max') -> str:
        """Széllökés kategorizálása élethű értékek alapján."""
        if wind_speed is None or wind_speed < 0:
            return 'moderate'  # Default safe category

        try:
            if data_source in ['wind_gusts_max', 'wind_gusts_10m_max']:
                # Get thresholds via dependency injection
                high_threshold = ("constants_provider.get_wind_threshold('high')")
                extreme_threshold = ("constants_provider.get_wind_threshold('extreme')")
                hurricane_threshold = ("constants_provider.get_wind_threshold('hurricane')")

                # JAVÍTÁS: wind_gusts_max adatforrás élethű küszöbök
                if wind_speed >= hurricane_threshold:
                    return 'hurricane'
                elif wind_speed >= extreme_threshold:
                    return 'extreme'
                elif wind_speed >= high_threshold:
                    return 'strong'
                # ... rest unchanged
            else:
                # Fallback for windspeed_10m_max
                high_threshold = ("windspeed_constants.HIGH")  # Via interface
                extreme_threshold = ("windspeed_constants.EXTREME")  # Via interface

                if wind_speed >= extreme_threshold:
                    return 'strong'  # Hardcoded fallback
                else:
                    return 'moderate'
        except Exception as e:
            # Handle missing constants gracefully
            logger.error(f"Wind gust categorization hiba: {e}")
            return 'moderate'  # Safe fallback
```

### 3. Break Dependency Chain

**Goal:** Ensure gui.utils doesn't depend on gui.theme_manager during import time.

**Modify:** `/home/tibor/PythonProjects/Jules/global_weather_analyzer/src/gui/utils.py`

**The Problem:**
```python
# Line 271 causes circular dependency at import time:
from src.gui.theme_manager import get_theme_manager  # ❌ CIRCULAR - moves dependency to runtime
```

**Solution - Lazy Import Pattern:**
```python
# Move import inside method call (runtime dependency)
@staticmethod
def get_theme_stylesheet(theme_type: ThemeType) -> str:
    """🎨 DINAMIKUS téma stylesheet lekérdezése ThemeManager-rel."""
    try:
        # 🎨 LAZY THEMEMANAGER IMPORT (runtime dependency)
        from .theme_manager import get_theme_manager  # ✅ MOVES TO RUNTIME
        manager = get_theme_manager()
        css = manager.generate_application_css()
        return css
    except ImportError as e:
        logger.warning(f"ThemeManager import failed, using legacy CSS: {e}")
        return StyleSheets._get_legacy_stylesheet(theme_type)
```

---

## 🚀 IMPLEMENTATION TASKS

### Phase 1: Interface Creation (5 minutes)
- [ ] Create `src/gui/interfaces.py`
- [ ] Define IConstantsProvider and IWindspeedConstants interfaces
- [ ] Define IAnomalyConstants interface

### Phase 2: Constants Provider (5 minutes)
- [ ] Create `src/gui/constants_provider.py`
- [ ] Implement ConstantsProvider class
- [ ] Implement WindspeedConstantsAdapter

### Phase 3: Refactor WindGustsAnalyzer (10 minutes)
- [ ] Remove direct import from gui.results_panel.utils
- [ ] Add dependency injection to WindGustsAnalyzer.__init__
- [ ] Update all threshold references to use constants_provider
- [ ] Add proper error handling for missing constants

### Phase 4: Lazy Import Fix (5 minutes)
- [ ] Make theme_manager import lazy in gui/utils.py
- [ ] Move `@staticmethod` decorator to make it runtime-only
- [ ] Test theme loading still works

### Phase 5: Testing & Validation (10 minutes)
- [ ] Run git status to verify no git issues
- [ ] Test WindGustsAnalyzer still works
- [ ] Circular dependency detector validation
- [ ] Ensure thresholds still work correctly

---

## 📊 SUCCESS METRICS

✅ **Import Cycle Broken:** gui.utils no longer circularly imports gui.theme_manager
✅ **Functionality Preserved:** Wind thresholds still work (70.0, 100.0, 120.0 km/h)
✅ **Clean Architecture:** Dependency injection instead of direct imports
✅ **Backward Compatibility:** All existing functionality maintained
✅ **Test Coverage:** Unit tests ensure proper threshold loading

---

## 🔄 ROLLBACK PLAN

If any issues arise:
1. Git revert modification with `git checkout -- src/gui/results_panel/utils.py`
2. Keep interface files as they are unused exports
3. Test WindGustsAnalyzer again with original constants
4. Debug and adjust threshold values if needed

---

## 📞 NEXT STEPS

Once this plan is approved:
1. **Execute in phases** - don't mix phases
2. **Test after each phase** - ensure no regressions
3. **Commit after each phase** - maintain clean git history
4. **Document changes** - update docstrings if needed

**Estimated Time:** 25 minutes total
**Risk Level:** 🔴 LOW - Controlled refactoring with interfaces
**Impact:** 🔴 HIGH - Eliminates circular dependency

Ready for implementation! 🚀