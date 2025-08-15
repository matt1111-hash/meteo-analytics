# Refactor Plan – God Class Reduction

## Context

The project contains two major "God Classes" with excessive size, complexity, and mixed responsibilities, plus several smaller hotspot files.\
The goal is to split these into smaller, more maintainable modules without breaking existing functionality.

## Top Priority Files

1. ``** – **``

   - 2147 LOC, 89 methods
   - Mixes UI construction, data handling, and signal wiring
   - High number of Qt signal connections

2. ``** – **``

   - 1609 LOC, 58 methods
   - Acts as a central event hub, UI builder, and business logic container
   - High number of imports and dependencies

---

## ControlPanel – Suggested Split

### 1. Signal Wiring Module

- Create `gui/signals/control_panel_signals.py`
- Move all `Signal(...)` definitions and `.connect(...)` calls here
- The `ControlPanel` should only call:
  ```python
  from .signals.control_panel_signals import setup_signals
  setup_signals(self)
  ```

### 2. UI Builder Class

- Create `ControlPanelUIBuilder`
- Responsibility: Create and arrange widgets only (no business logic)

### 3. Data Handler Class

- Create `ControlPanelDataHandler`
- Responsibility: Data loading, API calls, user preferences handling

---

## MainWindow – Suggested Split

### 1. Controller Class

- Create `MainWindowController`
- Responsibility: All `@Slot` methods and complex event handling

### 2. View Builder Class

- Create `MainWindowViewBuilder`
- Responsibility: UI layout and widget instantiation

### 3. Signal Wiring Module

- Create `gui/signals/main_window_signals.py`
- Centralize all Qt signal connections here

---

## Additional Recommendations

### Reduce Fan-in

- `config` module is imported from 11 locations → use dependency injection instead of direct imports where possible

### Reduce Cyclomatic Complexity

- Methods with CC > 30 should be split into smaller helper functions
- Use **guard clauses** for early returns to simplify logic flow

---

## Output Goals

- Each refactored file < 500 LOC
- Each class < 20 methods
- Cyclomatic complexity per method < 15
- Decoupled UI construction, data handling, and signal wiring

