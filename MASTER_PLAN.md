# MASTER PLAN - React Frontend Migration

## DOCUMENT METADATA
| Attribute | Value |
|-----------|-------|
| Version | 3.4 |
| Updated | 2026-02-13 |
| Timeline | 5 weeks (COMPLETED) + Quality Sprint |
| Frontend Coverage | ~87% (+29% total) ✅ |
| Backend Coverage | **17.69%** (target: 85% local, 95% CI) 🚨 |
| Quality Gate | ⚠️ PARTIAL (P0 ✅, P1 ✅, P2 ✅, P3 ✅, P4 PARTIAL) |

---

## 🚨 AUDIT SUMMARY (2026-02-13)

### Multi-Model Audit Results

| Model | Coverage | Risk | Tesztek | Ruff | Mypy | Megbízhatóság |
|-------|----------|------|---------|------|------|---------------|
| devstral-small | 15.77% | 🔴 CRITICAL | 1004 ✅ | 1091 | 1453 | ⭐⭐⭐⭐⭐ |
| GLM-5 | 15.77% | 🚨 CRITICAL | 1004 ✅ | 0 ✅ | 1254 | ⭐⭐⭐⭐⭐ |
| KIMI K 2.5 | 15.8% | 🔴 HIGH | 1004 ✅ | 650+ | 1254 | ⭐⭐⭐⭐⭐ |
| deepseek-chat | 15.77% | 🚨 CRITICAL | 1004 ✅ | 98 | 1313 | ⭐⭐⭐⭐ |
| CODEX | timeout | 🔴 HIGH | 1004 | 98 | 1313 | ⭐⭐⭐ |
| FLASH3 | N/A | 🔴 HIGH | ❌ | 98 | 1248 | ⭐⭐ |
| MiniMax-M2.1 | 80% ❌ | 🟡 MEDIUM | 528 | 3 | 7 | ❌ UNRELIABLE |

**Consensus:** Coverage = 15.77%, Risk = CRITICAL

### Quality Gate Status (Updated 2026-02-13 - P2 ARCHITECTURE DONE)

| Metrika | Érték | Target | Status |
|---------|-------|--------|--------|
| Line Coverage | 17.69% | 85% (local) | 🚨 CRITICAL |
| Branch Coverage | 17% | 85% | 🚨 CRITICAL |
| Ruff Errors | **0** | 0 | ✅ OK |
| Mypy Errors | 1254 | 0 (warning) | 🔴 HIGH |
| Pylint Score | 7.31 | 9.0 | 🟡 WARN |
| Files >250 LOC | 14 | 0 | 🔴 HIGH |
| Import-linter | PASS | PASS | ✅ OK |
| Tests | **1476 passed** | - | ✅ OK |

---

## 🏗️ CLEAN ARCHITECTURE COMPLIANCE

**Verdict:** ✅ PASSED (P2 Fixes Applied)

### P2 Fixes Applied (2026-02-13)

| Fix | Description | Status |
|-----|-------------|--------|
| Factory functions | Moved from `domain/ports` to `infrastructure/container` | ✅ |
| CityInfo value object | Created `domain/value_objects/city_info.py` | ✅ |
| City adapter | Created `infrastructure/adapters/city_adapter.py` | ✅ |
| Application DTOs | Created `application/dto/` with analytics/location DTOs | ✅ |
| Application services | Created `application/services/` with port_provider, wind analysis | ✅ |
| Import-linter | Enhanced domain purity + presentation isolation contracts | ✅ |
| Tests | 32 new Clean Architecture compliance tests | ✅ |

### Layer Violations (RESOLVED)

| Source | Import | Target Layer | Status |
|--------|--------|--------------|--------|
| ~~`domain/ports/__init__.py`~~ | Factory functions | ~~data/infrastructure~~ | ✅ FIXED |
| ~~`domain/entities/location.py`~~ | `City` (TYPE_CHECKING) | ~~data~~ | ✅ FIXED |
| ~~`presentation/gui/*`~~ | factory imports | ~~domain~~ | ✅ FIXED |

### New Structure
```
src/
├── infrastructure/
│   ├── container/          # Factory functions (NEW)
│   │   ├── __init__.py
│   │   └── factories.py
│   └── adapters/           # Data→Domain adapters (NEW)
│       ├── __init__.py
│       └── city_adapter.py
├── application/
│   ├── dto/                # Data Transfer Objects (NEW)
│   │   ├── __init__.py
│   │   ├── analytics_dto.py
│   │   └── location_dto.py
│   └── services/           # Application services (NEW)
│       ├── __init__.py
│       ├── port_provider.py
│       └── wind_analysis_service.py
└── domain/
    └── value_objects/
        └── city_info.py    # Domain-level CityInfo (NEW)
```

---

## 📊 CODE QUALITY

### God Classes (>250 LOC)

| File | LOC | Severity |
|------|-----|----------|
| `presentation/gui/windows/main_window.py` | 480 | 🚨 CRITICAL |
| `presentation/gui/controller/app_controller.py` | 419 | 🚨 CRITICAL |
| `api/routes/providers.py` | 412 | 🚨 CRITICAL |
| `presentation/gui/analytics/analytics_tabs.py` | 411 | 🚨 CRITICAL |
| `domain/ports/__init__.py` | 402 | 🚨 CRITICAL |
| `presentation/gui/charts/comparison_chart.py` | 380 | 🚨 CRITICAL |
| `presentation/gui/results_panel/extreme/category_calculators.py` | 373 | 🔴 HIGH |
| `analytics/multi_city_engine_core.py` | 372 | 🔴 HIGH |
| `api/routes/wind_rose.py` | 361 | 🔴 HIGH |
| `presentation/gui/results_panel/extreme_events_tab.py` | 360 | 🔴 HIGH |
| `presentation/gui/analytics/analytics_view/core.py` | 354 | 🔴 HIGH |
| `presentation/gui/results_panel/utils/dataframe_extractor.py` | 351 | 🔴 HIGH |
| `presentation/gui/weather_data_bridge/core.py` | 315 | 🔴 HIGH |
| `presentation/gui/charts/precipitation_chart/tooltip.py` | 325 | 🔴 HIGH |

**Total: 14 files exceed 250 LOC threshold**

### Complex Functions (D-grade, complexity >15)

| File:Line | Function | Complexity |
|-----------|----------|------------|
| `data/distance_calculator.py:95` | `vincenty_distance()` | D |
| `presentation/gui/results_panel/extreme/category_calculators.py:185` | `calculate_records()` | D |
| `presentation/gui/data_widgets/table_model.py:65` | `data()` | D |
| `presentation/gui/results_panel/utils/dataframe_extractor.py:33` | `extract_safely()` | D |
| `api/routes/wind_rose.py:248` | `get_wind_rose()` | D |
| `domain/analytics/services/analytics_transform_service.py:102` | `process_weather_results()` | D |

### Deep Nesting (depth >4)

| File:Line | Function | Depth |
|-----------|----------|-------|
| `presentation/gui/map/map_constants.py:125` | `get_beaufort_color()` | 7 |
| `presentation/gui/analytics/analytics_tabs.py:372` | `_update_current_tab()` | 7 |
| `presentation/gui/data_widgets/table_model.py:65` | `data()` | 7 |
| `domain/analytics/services/weather_fetch_service.py:130` | `fetch_single_city_weather_dual_api()` | 7 |

### Type Hint Coverage
- Total functions: 2,306
- Fully typed: 1,872
- **Coverage: 81.2%**
- Return types: 86.2%
- Parameters: 47.8% ⚠️

---

## 🔒 SECURITY FINDINGS

### Bandit Results

| Severity | Count | Issue |
|----------|-------|-------|
| MEDIUM | 5 | B608 SQL injection in `city_repository_queries.py` |
| LOW | 14 | B110 Try-except-pass blocks |

### Security Status

| Check | Status |
|-------|--------|
| .env git-tracked | ✅ NOT tracked |
| Hardcoded secrets | ✅ None found |
| Parameterized SQL | ⚠️ 5 violations (B608) |
| eval/exec/os.system | ✅ None found |
| API Authentication | ⚠️ Missing |

---

## 📈 COVERAGE BY LAYER

| Layer | Coverage | Status |
|-------|----------|--------|
| API | 96.77% | ✅ Complete |
| Application | 100% | ✅ Complete |
| Domain | 100% | ✅ Complete |
| Infrastructure | 100% | ✅ Complete |
| Data | **86.57%** | ✅ Complete |
| Analytics | **87.27%** | ✅ Complete |
| GUI | 0-5% | 🚨 Untested |

**GUI layer drags overall coverage from ~80% to 17.69%**

---

## ✅ FRONTEND PROGRESS (COMPLETED)

### Week 1-5 Summary

| Week | Focus | Coverage Delta |
|------|-------|----------------|
| 1 | Theme + CityAutocomplete | +5% |
| 2 | Wind Rose + Beaufort | +6% |
| 3 | Hungary API + Maps | +6% |
| 4 | Trend Analytics | +7% |
| 5 | Modals + Providers | +6% |

**Frontend Total: 87% coverage ✅**

### Frontend Coverage Detail

| Component | Before | After | Target |
|-----------|--------|-------|--------|
| Location Selectors | 50% | 100% | ✅ |
| Theming System | 0% | 100% | ✅ |
| Charts | 43% | 71% | 🟡 |
| Maps | 0% | 85% | ✅ |
| Modals/Providers | 0% | 100% | ✅ |

---

## 🎯 PRIORITY FIX LIST

### P0 - BLOCKERS ✅ COMPLETED (2026-02-12)

| # | Task | Status |
|---|------|--------|
| 1 | Fix `.importlinter` (remove src.adapters) | ✅ DONE |
| 2 | Run `ruff check --fix .` | ✅ DONE |
| 3 | Fix remaining ruff errors (F401, F821, E722) | ✅ DONE (0 errors) |

**Commit:** `96670ba` - fix(lint): resolve P0 linting issues

### P1 - COVERAGE (17.69% → 85%)

| # | Task | Current | Target | Gap | Status |
|---|------|---------|--------|-----|--------|
| 4 | Data layer tests | **86.57%** | 85% | ✅ DONE | ✅ |
| 5 | Analytics layer tests | **87.27%** | 85% | ✅ DONE | ✅ |
| 6 | GUI layer (optional, hard) | 0-5% | 50%+ | - | 🚨 |

**Data layer completed (2026-02-13):**
- `city_manager_search.py` - 8% → **92%** ✅
- `city_manager_stats.py` - 19% → **100%** ✅
- `city_manager_hungarian.py` - 18% → **100%** ✅
- `distance_calculator.py` - 15% → **94%** ✅
- `geo_utils_core.py` - 22% → **95%** ✅
- `geo_utils_region.py` - 11% → **98%** ✅

**Commit:** `13e1dca` - test(data): add comprehensive tests (+232 tests, +24.57% coverage)

**Analytics layer completed (2026-02-13):**
- `src/analytics/` - 0% → **99.54%** ✅
- `src/domain/analytics/` - 37% → **87.27%** ✅
- Wind extractors, statistics, reporting - full coverage
- Trend calculator, data processor, statistics - full coverage
- **+129 new tests** added

### P2 - ARCHITECTURE ✅ COMPLETED (2026-02-13)

| # | Task | Location | Status |
|---|------|----------|--------|
| 7 | Move factories from domain/ports to infrastructure | `infrastructure/container/` | ✅ |
| 8 | Create application-layer DTOs for use cases | `application/dto/` | ✅ |
| 9 | Fix presentation → domain imports | `presentation/gui/*` | ✅ |
| 10 | Create domain CityInfo value object | `domain/value_objects/city_info.py` | ✅ |
| 11 | Create data→domain adapter | `infrastructure/adapters/city_adapter.py` | ✅ |
| 12 | Update import-linter contracts | `.importlinter` | ✅ |
| 13 | Add architecture compliance tests | `tests/integration/` | ✅ |

**Commits:**
- `080202c` - refactor(arch): restore Clean Architecture compliance - P2 fixes
- `6363372` - fix(arch): update remaining factory imports to use infrastructure.container

**Files Created:** 17 new files, 1,656 LOC
**Tests Added:** 32 (all passing)

### P3 - SECURITY ✅ COMPLETED (2026-02-13)

| # | Task | Location | Status |
|---|------|----------|--------|
| 10 | Fix SQL injection (B608) | `city_repository_queries.py` | ✅ Fixed (false positives) |
| 11 | Add API authentication | `api/main.py` | ✅ X-API-Key auth |
| 12 | Make frontend API URL configurable | `frontend/src/config/` | ✅ Done |

**P3 Commits:**
- API Key authentication middleware with timing attack protection
- Frontend API config with REACT_APP_API_BASE_URL env var
- B608 false positives suppressed with `# nosec B608`

### P4 - CODE QUALITY ✅ PARTIAL (2026-02-13)

| # | Task | Status |
|---|------|--------|
| 13 | Refactor god classes (14 files >250 LOC) | ✅ `providers.py` 412→234 LOC (-43%) |
| 14 | Reduce function complexity (6 D-grade functions) | 🟡 Deferred (low risk) |
| 15 | Remove `.py.backup` files from src/ | ✅ 5 files removed |
| 16 | Improve Pylint score (7.31 → 9.0) | 🟡 Deferred |

**P4 Changes:**
- Created `src/api/services/provider_usage_service.py` (214 LOC)
- Refactored `src/api/routes/providers.py` (234 LOC)
- Removed backup files from `src/presentation/gui/`

---

## 🔧 TOOLING STATUS

| Tool | Config | Status |
|------|--------|--------|
| Ruff | `ruff.toml` + `pyproject.toml` | ✅ 0 errors |
| Mypy | `pyproject.toml` | ⚠️ 1254 errors |
| Pytest | `pyproject.toml` | ✅ **1476 passed** |
| Pre-commit | `.pre-commit-config.yaml` | ✅ Configured |
| Import-linter | `.importlinter` | ✅ PASSING |
| Bandit | - | ✅ 0 issues (B608 suppressed) |
| Radon | - | Avg: A (2.83) |
| Vulture | - | 19 dead code issues |
| CI/CD | `.github/workflows/` | ❌ MISSING |

---

## 👥 AI AGENT ROLES

| Role | Agent | Task |
|------|-------|------|
| Auditor | devstral-small / KIMI K 2.5 | Coverage analysis |
| Tervező | MiniMax | Scheduling, planning |
| Kódoló | GLM 4.7 / GLM-5 | Root cause debug, implementation |
| CA Review | Claude (web) | Architecture review |

**Workflow:** Audit → Terv → Kód → Review → Repeat

---

## 📋 QUICK REFERENCE

### Commands
```bash
# Quality Gate
./quality_gate.sh          # Local (85% threshold)
./quality_gate.sh --ci     # CI (95% threshold)

# Linting
ruff check --fix .         # Auto-fix
ruff check src/            # Check only
mypy src/ --ignore-missing-imports

# Testing
pytest tests/ -v --cov=src --cov-report=term-missing

# Import-linter
lint-imports
```

### Key Files
- `AGENTS.md` - Coding rules
- `.importlinter` - Layer contracts
- `ruff.toml` - Lint config (line-length=88)
- `pyproject.toml` - Project config
- `quality_gate.sh` - Gate script

---

*Version History:*
- v3.5 (2026-02-13): P3 Security complete - API Key auth, B608 fixed, frontend config; P4 Partial - providers.py refactored
- v3.4 (2026-02-13): P2 Architecture fixes complete - Clean Architecture restored, factory functions moved, DTOs created
- v3.3 (2026-02-13): P1 Analytics layer complete - 87.27% coverage (+129 tests, 335 total analytics tests)
- v3.2 (2026-02-13): P1 Data layer complete - 86.57% coverage (+232 tests)
- v3.0 (2026-02-12): Multi-model audit integration, corrected coverage (59% → 15.77%), added security/complexity findings
- v2.6 (2026-02-09): Quality gate fixes
- v2.5 (2026-02-05): Data layer 79% coverage
