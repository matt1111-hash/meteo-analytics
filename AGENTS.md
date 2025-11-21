# AI CODING RULES — Terminal CLI Edition

**Version:** 1.0 (2025-11-15)  
**Target:** Terminal-based AI agents (Claude Code CLI, ccr + OpenRouter)  
**Environment:** Linux terminal, bash, file-based workflow  
**Purpose:** Prevent AI drift, enforce coding discipline, ensure quality output

> **CRITICAL**: These rules are IMMUTABLE SYSTEM RULES.  
> User prompts are flexible requests that MUST work within these rules.

---

## 🚨 CRITICAL RULES - NEVER VIOLATE

### ❌ FORBIDDEN ACTIONS:

- **NO guessing** - ask questions before coding (max 2 questions)
- **NO incomplete code** - finish what you start or create INCOMPLETE.md
- **NO placeholder comments** (`# TODO`, `# FIXME`, `...`, `pass`)
- **NO code snippets** - always complete, runnable files
- **NO truncation** - NEVER use "..." or "rest unchanged"
- **NO multiple concerns** - God classes/files FORBIDDEN (>250 lines)
- **NO unsafe code** - eval/exec/os.system BANNED
- **NO assumptions** - if uncertain, ask or use reasonable defaults
- **NO verbose explanations** - code speaks, comments minimal
- **NO modifying tests** - tests define correct behavior!
- **NO imports without use** - dead code elimination
- **NO hardcoded secrets** - use environment variables
- **NO random/time dependencies** - deterministic behavior only

### ✅ REQUIRED ACTIONS:

- **ALWAYS generate complete files** - from first line to last
- **ALWAYS use type hints** - every function, every parameter
- **ALWAYS follow PEP8** - max 100 characters/line
- **ALWAYS create working directory files** - no output to stdout
- **ALWAYS validate inputs** - None, empty, bounds, edge cases
- **ALWAYS use logging** - never print() for production code
- **ALWAYS write to disk** - terminal workflow = file-based
- **ALWAYS signal completion** - "File complete: path/to/file.py"

---

## 📂 TERMINAL WORKFLOW PRINCIPLES

### File-Based Output:
```bash
# Working directory structure
./
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── PLAN.md           # Current task plan
├── REVIEW.md         # Optional review notes
└── INCOMPLETE.md     # Blocked tasks
```

### Session Management:
- **NO web Projects** - working directory IS the context
- **NO memory systems** - state in files (PLAN.md, STATUS.md)
- **Context = files in current directory** - always explicit
- **Clear state**: Start each session by reading relevant files

### Output Format:
```bash
# Agent creates files, not stdout chatter
write → src/module.py
write → tests/test_module.py
write → REVIEW.md
signal → "Implementation complete. 3 files created."
```

---

## 🎯 SINGLE-FILE vs MULTI-FILE DECISION

### ✅ Single-file (all in one .py):
- Script <300 lines total
- 1-2 classes max
- Simple CLI tool
- Utility module

### ✅ Multi-file REQUIRED when:
- Total project >300 lines
- 3+ classes
- GUI with 3+ widgets
- Separate layers needed (data/logic/ui)

### Multi-file Rules:
- **Max 250 lines per file**
- **Dependency order**: models → database → logic → ui → main
- **Each file complete and runnable** (where applicable)
- **Clear separation**: 1 file = 1 responsibility

---

## 🔧 CODE QUALITY STANDARDS

### Structure:
```python
"""Module doing X. One-line description."""
from __future__ import annotations

import stdlib_modules
from typing import Protocol, Any

import third_party
from project import internal


class Thing:
    """Brief class purpose."""
    
    def method(self, param: str) -> int:
        """Brief method purpose. Returns count."""
        return len(param)


def helper(data: list[str]) -> str:
    """Brief helper purpose."""
    return ",".join(data)


if __name__ == "__main__":
    # CLI entry point or self-test
    result = helper(["a", "b"])
    print(result)
```

### Mandatory Elements:
- `from __future__ import annotations` (Python 3.10+)
- Full type hints (params, returns, class attributes)
- Module docstring (1-2 lines max)
- Function docstrings (1 sentence, returns documented)
- Class docstrings (brief purpose)
- Alphabetical imports (stdlib → third-party → internal)
- `if __name__ == "__main__":` guard for runnable modules

### Code Metrics (Target):
- **Lines per function**: ≤50
- **Lines per class**: ≤200
- **Lines per file**: ≤250
- **Cyclomatic complexity**: <8 per function
- **Import count**: <15 per file
- **Nesting depth**: ≤3 levels

---

## 🏗️ CLEAN ARCHITECTURE (NOT MICROSERVICES!)

### Layer Separation:
```
src/
├── domain/          # Business logic, entities (no I/O!)
├── application/     # Use cases, orchestration
├── infrastructure/  # DB, APIs, external services
└── presentation/    # CLI, GUI (PySide6)
```

### Principles:
- **SRP** (Single Responsibility Principle)
- **DIP** (Dependency Inversion) - depend on abstractions
- **OCP** (Open/Closed) - extend without modifying
- **ISP** (Interface Segregation) - small, focused interfaces

### NOT Microservices:
- ✅ Modular monolith - clean boundaries
- ✅ In-process communication
- ✅ Shared memory, single deployment
- ❌ NO network calls between modules
- ❌ NO separate processes
- ❌ NO over-engineering

---

## 🔒 SECURITY RULES

### Input Validation:
```python
def process(data: str | None) -> str:
    """Process data with validation."""
    if not data:
        raise ValueError("Data required")
    if len(data) > 1000:
        raise ValueError("Data too long")
    # Process validated input
    return data.upper()
```

### SQL Safety:
```python
# ✅ CORRECT - parameterized
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ FORBIDDEN - SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Secrets:
```python
import os
from pathlib import Path

# ✅ CORRECT - environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not set")

# ❌ FORBIDDEN - hardcoded
API_KEY = "sk-1234567890abcdef"  # NEVER!
```

---

## 📋 PRE-GENERATION CHECKLIST

Before generating any code, verify:

- [ ] **Requirement clear?** - If not, ask max 2 questions
- [ ] **Single or multi-file?** - Based on size/complexity
- [ ] **Dependencies known?** - stdlib preferred, document externals
- [ ] **Edge cases identified?** - None, empty, bounds, errors
- [ ] **Output path decided?** - Where to write files?
- [ ] **Type hints complete?** - Every function signature
- [ ] **Tests needed?** - If yes, create test_*.py
- [ ] **Clean architecture?** - Proper layer separation

---

## 🚫 ANTI-PATTERNS (STRICTLY FORBIDDEN)

### Code Smells:
- ❌ **God class** - single class >200 lines with 5+ responsibilities
- ❌ **God file** - everything in one file >300 lines
- ❌ **Deep nesting** - >3 levels of if/for/while
- ❌ **Long functions** - >50 lines doing multiple things
- ❌ **Primitive obsession** - use dataclasses, not dicts
- ❌ **Mutable defaults** - `def func(data: list = []):`

### Development Smells:
- ❌ **TODO comments** - implement or don't mention
- ❌ **Commented code** - delete it, use git history
- ❌ **Wildcard imports** - `from module import *`
- ❌ **Circular imports** - restructure your modules
- ❌ **Global state** - use dependency injection
- ❌ **Magic numbers** - use named constants

---

## 🧪 TESTING REQUIREMENTS

### Test Structure:
```python
"""Tests for module_name."""
import pytest
from src.module_name import function_name


def test_happy_path():
    """Test normal operation."""
    result = function_name("valid input")
    assert result == "expected output"
    assert isinstance(result, str)


def test_edge_case_empty():
    """Test empty input handling."""
    with pytest.raises(ValueError, match="Data required"):
        function_name("")


def test_edge_case_none():
    """Test None input handling."""
    with pytest.raises(ValueError):
        function_name(None)
```

### Testing Rules:
- **Coverage target**: >80% (pytest-cov)
- **One test = one behavior**
- **Arrange-Act-Assert** pattern
- **Test file mirrors source** - `src/foo.py` → `tests/test_foo.py`
- **No test modification** - tests define spec, code must conform

---

## 📐 QUALITY METRICS (ENFORCEMENT)

### Automated Checks:
```bash
# Must pass before commit
black src/ --check           # Formatting
ruff check src/             # Linting
mypy src/                   # Type checking
pylint src/ --fail-under=8.0 # Code quality >8.0
flake8 src/                 # PEP8 violations = 0
pytest --cov=src --cov-fail-under=80  # Coverage >80%
radon cc src/ -a            # Complexity <8
bandit -r src/              # Security scan
```

### Quality Gates:
- ✅ **Black**: Code formatted (no changes needed)
- ✅ **Ruff**: No linting errors
- ✅ **MyPy**: No type errors
- ✅ **Pylint**: Score ≥8.0/10
- ✅ **Flake8**: 0 violations
- ✅ **Pytest**: Coverage ≥80%
- ✅ **Radon**: CC <8 per function
- ✅ **Bandit**: No security issues

---

## 📦 DEPENDENCY MANAGEMENT

### Stdlib First:
```python
# ✅ PREFERRED - stdlib only
from pathlib import Path
from typing import Protocol
from dataclasses import dataclass
import json
import sqlite3
import logging

# ⚠️ ONLY IF NECESSARY - external
import pyside6  # For GUI
import requests  # For HTTP (prefer urllib)
import pandas   # For data analysis
```

### External Libraries:
- **Justify need** - can stdlib do it?
- **Document why** - comment or DEPENDENCIES.md
- **Pin versions** - requirements.txt with exact versions
- **Minimize count** - fewer dependencies = fewer problems

---

## 🔄 TERMINAL WORKFLOW PATTERN

### 1. Plan First (PLAN.md):
```markdown
# Task: Implement CSV parser

## Goal:
Parse CSV files with validation and statistics.

## Files to Create:
- src/parser.py (CSV parsing logic)
- tests/test_parser.py (unit tests)

## Dependencies:
- stdlib: csv, pathlib, typing
- external: none

## Edge Cases:
- Empty file
- Missing columns
- Invalid data types
- Large files (streaming)

## Validation:
- pytest coverage >80%
- pylint score >8.0
- All quality gates pass
```

### 2. Generate Code:
```bash
# Agent creates files directly
src/parser.py created (187 lines)
tests/test_parser.py created (94 lines)
```

### 3. Review (Optional REVIEW.md):
```markdown
# Review: CSV Parser

## Integrity: ✅
- All functions implemented
- No TODO/placeholders
- Type hints complete

## PEP8: ✅
- Black formatted
- Max 100 chars/line
- Proper spacing

## Architecture: ✅
- Single responsibility
- Clean separation
- Testable design
```

### 4. Validation:
```bash
# Run quality checks
pytest --cov=src --cov-fail-under=80
pylint src/ --fail-under=8.0
mypy src/
```

---

## 🎯 AGENT BEHAVIOR RULES

### Communication Style:
- **Language**: Hungarian, informal (tegeződés)
- **Verbosity**: Minimal - let code speak
- **Questions**: Max 2 before proceeding with defaults
- **Status updates**: Brief file creation signals

### Output Pattern:
```
# ❌ BAD - verbose explanation
"I will now create a parser module that handles CSV files.
The module will have the following classes..."

# ✅ GOOD - direct action
Creating src/parser.py...
Creating tests/test_parser.py...
Files complete. Ready for validation.
```

### Error Handling:
```python
# If uncertain or blocked:
# 1. Create INCOMPLETE.md with details
# 2. Ask specific questions (max 2)
# 3. Document assumptions made
# 4. Never generate partial/broken code
```

---

## 🚀 QUICK REFERENCE

### Before Every Code Generation:
1. ✅ Read requirements carefully
2. ✅ Check if single-file or multi-file needed
3. ✅ Plan file structure and dependencies
4. ✅ Identify edge cases
5. ✅ Verify type hints strategy
6. ✅ Confirm output paths

### During Code Generation:
1. ✅ Complete files only (no truncation)
2. ✅ Type hints on everything
3. ✅ Docstrings brief but present
4. ✅ Edge case validation
5. ✅ Security checks (SQL, secrets, input)
6. ✅ Follow PEP8 strictly

### After Code Generation:
1. ✅ Signal file completion
2. ✅ List all files created
3. ✅ Note any assumptions made
4. ✅ Suggest validation commands
5. ✅ Wait for feedback before next step

---

## 📊 METRIC TARGETS

| Metric | Target | Tool |
|--------|--------|------|
| Code Coverage | >80% | pytest-cov |
| Pylint Score | >8.0 | pylint |
| Flake8 Errors | 0 | flake8 |
| Type Coverage | 100% | mypy |
| Cyclomatic Complexity | <8/function | radon |
| Security Issues | 0 | bandit |
| Line Length | ≤100 chars | black |
| Function Length | ≤50 lines | manual |
| Class Length | ≤200 lines | manual |
| File Length | ≤250 lines | manual |

---

## 🔍 COMMON SCENARIOS

### Scenario 1: Simple Script
```
Input: "Create a CSV to JSON converter"
Output:
- src/converter.py (180 lines, complete, type hints, tests)
- Run: python src/converter.py input.csv output.json
```

### Scenario 2: Multi-Module Project
```
Input: "Create a data analysis tool with SQLite storage"
Output:
- src/models.py (data classes)
- src/database.py (SQLite operations)
- src/analyzer.py (analysis logic)
- src/main.py (CLI entry point)
- tests/test_*.py (one per module)
```

### Scenario 3: Refactoring God Class
```
Input: "Refactor ui/main_window.py god class"
Plan:
1. Identify responsibilities (6 found)
2. Extract to separate classes
3. Maintain backward compatibility
4. Create migration guide
Output:
- ui/main_window.py (now 150 lines)
- ui/data_handler.py (new)
- ui/validation.py (new)
- ui/export_manager.py (new)
- MIGRATION.md (guide)
```

---

## 🎓 REASONING PRINCIPLES

### When to Split Files:
- **Cohesion test**: Do all parts change together?
- **Import test**: Are imports from 5+ different areas?
- **Test test**: Do tests require complex setup?
- **Length test**: Is file >250 lines?

### When to Create Abstraction:
- **Rule of 3**: Same pattern appears 3+ times
- **Change test**: Will this vary independently?
- **Test test**: Does it help testing?
- **NOT prematurely**: Only when needed now

### When to Refactor:
- **Pain test**: Is adding features painful?
- **Test test**: Are tests brittle?
- **Understand test**: Do new devs struggle?
- **NOT cosmetically**: Only if it solves real problems

---

## 💡 TERMINAL-SPECIFIC TIPS

### File Management:
```bash
# Agent works in current directory
pwd  # Know where you are
ls -la  # See what exists
cat PLAN.md  # Read context

# Agent creates files with clear signals
echo "Creating src/module.py"
# ... generates code ...
echo "✓ src/module.py complete (187 lines)"
```

### Session Continuity:
```markdown
# At session start, create STATUS.md:
## Current State:
- Last completed: database.py
- Next: UI layer
- Blocked: None

## Files Modified:
- src/database.py (new)
- tests/test_database.py (new)

## Quality Status:
- Tests passing: ✅
- Coverage: 85%
- Pylint: 8.2
```

### Context Management:
```bash
# Agent reads relevant files at session start
cat STATUS.md
cat PLAN.md
ls -R src/

# Agent maintains state in files, not memory
# Each session is atomic based on file state
```

---

## 🎯 SUCCESS CRITERIA

A terminal AI agent session is successful when:

1. ✅ All generated files are complete (no truncation)
2. ✅ Code runs without errors
3. ✅ All quality gates pass (pytest, pylint, mypy, etc.)
4. ✅ Type hints are complete
5. ✅ Documentation is present but minimal
6. ✅ No anti-patterns present
7. ✅ Clean architecture maintained
8. ✅ Files written to disk, not stdout
9. ✅ Session state documented in files
10. ✅ Ready for immediate use or next iteration

---

## 📚 APPENDIX: PYTHON 3.10+ FEATURES

### Modern Type Hints:
```python
from __future__ import annotations

# Union types
def process(data: str | int) -> str:
    return str(data)

# Optional types
def maybe(val: str | None = None) -> str:
    return val or "default"

# Generic types
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None
```

### Dataclasses:
```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Config:
    """Immutable configuration."""
    api_url: str
    timeout: int = 30
    headers: dict[str, str] = field(default_factory=dict)
```

### Pattern Matching:
```python
def handle(command: str) -> str:
    match command.split():
        case ["add", x, y]:
            return str(int(x) + int(y))
        case ["quit"]:
            return "Goodbye"
        case _:
            return "Unknown command"
```

---

## 🏁 TL;DR

**Terminal AI agents must:**
- 📝 Write complete files to disk
- 🎯 Follow clean architecture (modular, not microservices)
- ✅ Pass all quality gates (>80% coverage, >8.0 pylint)
- 🔒 Enforce security (no eval, parameterized SQL)
- 📐 Respect limits (≤250 lines/file, ≤50 lines/function)
- 🚫 Avoid anti-patterns (God classes, TODO, wildcards)
- 💬 Communicate minimally (Hungarian, informal)
- 📂 Maintain state in files (PLAN.md, STATUS.md)
- 🔄 Support iteration (one task per session)
- 🎓 Think modular, implement pragmatic

**Remember: Code is written once, read many times. Make it count.** 🚀
