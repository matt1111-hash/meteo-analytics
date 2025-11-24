# AI CODING RULES — Terminal CLI Edition

**Version:** 2.0 (2025-11-24)  
**Target:** Terminal-based AI agents (Claude Code CLI, ccr + OpenRouter)  
**Environment:** Linux terminal, bash, file-based workflow  
**Purpose:** Prevent AI drift, enforce coding discipline, ensure quality output

> **CRITICAL**: These rules are IMMUTABLE SYSTEM RULES.  
> User prompts are flexible requests that MUST work within these rules.

---

## 🔥 GIT HIGIÉNIA — KÖTELEZŐ MINDEN AGENTNEK

### ❗ SOHA NE FELEJTSD EL:

1. **Új mappa létrehozása után AZONNAL:**
   ```bash
   git status
   ```
   - Ellenőrizd, hogy az új mappa NEM ignorált
   - Ha `??` helyett nincs semmi → `.gitignore` probléma!

2. **Minden "KÉSZ" / "Sprint vége" / "Task done" ELŐTT:**
   ```bash
   git status
   git add -A
   git diff --cached --stat
   ```
   - Csak EZUTÁN írhatsz "✅ KÉSZ" státuszt
   - Ha nincs commit → NEM KÉSZ!

3. **`.gitignore` módosításakor:**
   - **TILOS:** `*/` vagy bármilyen általános wildcard a repo gyökerében
   - Módosítás után KÖTELEZŐ: `git status`
   - Ellenőrizd, hogy nem tűnt el egész mappa

4. **AGENT NEM COMMITOL ÖNÁLLÓAN:**
   - Javasolhatsz commit üzenetet és parancsot
   - A tényleges `git commit`-ot MINDIG az ember futtatja

### ⛔ TILOS PATTERN-EK .gitignore-ban:
```gitignore
# ❌ TILOS - mindent lenyel
*/
**/

# ✅ HELYES - konkrét minták
__pycache__/
*.pyc
node_modules/
dist/
build/
.venv/
.idea/
.vscode/
```

---

## 🚨 CRITICAL RULES - NEVER VIOLATE

### ❌ FORBIDDEN ACTIONS:

- **NO guessing** - ask questions before coding (max 2 questions)
- **NO incomplete code** - finish what you start or create INCOMPLETE.md
- **NO placeholder comments** (`# TODO`, `// FIXME`, `...`, `pass`)
- **NO code snippets** - always complete, runnable files
- **NO truncation** - NEVER use "..." or "rest unchanged"
- **NO multiple concerns** - God classes/files FORBIDDEN (>250 lines)
- **NO unsafe code** - eval/exec/os.system BANNED
- **NO assumptions** - if uncertain, ask or use reasonable defaults
- **NO verbose explanations** - code speaks, comments minimal
- **NO modifying tests** - tests define correct behavior!
- **NO imports without use** - dead code elimination
- **NO hardcoded secrets** - use environment variables
- **NO "KÉSZ" without commit** - verify with `git status` first!

### ✅ REQUIRED ACTIONS:

- **ALWAYS generate complete files** - from first line to last
- **ALWAYS use type hints** - every function, every parameter
- **ALWAYS verify git status** - after creating new folders
- **ALWAYS create working directory files** - no output to stdout
- **ALWAYS validate inputs** - None, empty, bounds, edge cases
- **ALWAYS use logging** - never print() for production code
- **ALWAYS write to disk** - terminal workflow = file-based
- **ALWAYS signal completion** - "File complete: path/to/file"

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
- **Git check**: FIRST thing in session = `git status`

### Output Format:
```bash
# Agent creates files, not stdout chatter
write → src/module.py
write → tests/test_module.py
signal → "Implementation complete. 2 files created."
git status → verify files visible to git
```

---

## 🎯 SINGLE-FILE vs MULTI-FILE DECISION

### ✅ Single-file (all in one):
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

### Mandatory Elements:
- Full type hints (params, returns, class attributes)
- Module docstring (1-2 lines max)
- Function docstrings (1 sentence, returns documented)
- Class docstrings (brief purpose)
- Alphabetical imports (stdlib → third-party → internal)

### Code Metrics (Target):
- **Lines per function**: ≤50
- **Lines per class**: ≤200
- **Lines per file**: ≤250
- **Cyclomatic complexity**: <8 per function
- **Import count**: <15 per file
- **Nesting depth**: ≤3 levels

### ⚠️ NULL/UNDEFINED CHECKS - MINDIG:
```python
# ❌ CRASH
return value.some_method()

# ✅ SAFE
return value.some_method() if value else default
```

```typescript
// ❌ CRASH
return value.toFixed(2)

// ✅ SAFE
return value?.toFixed(2) ?? 'N/A'
```

---

## 🏗️ CLEAN ARCHITECTURE (NOT MICROSERVICES!)

### Layer Separation:
```
src/
├── domain/          # Business logic, entities (no I/O!)
├── application/     # Use cases, orchestration
├── infrastructure/  # DB, APIs, external services
└── presentation/    # CLI, GUI, Web UI
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
- Always validate before processing
- Check for None/null, empty, bounds, edge cases
- Raise/throw explicit errors for invalid input

### SQL Safety:
```python
# ✅ CORRECT - parameterized
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ FORBIDDEN - SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Secrets:
- ✅ Environment variables
- ❌ NEVER hardcode API keys, passwords, tokens

---

## 📋 PRE-GENERATION CHECKLIST

Before generating any code, verify:

- [ ] **Requirement clear?** - If not, ask max 2 questions
- [ ] **Single or multi-file?** - Based on size/complexity
- [ ] **Dependencies known?** - stdlib preferred, document externals
- [ ] **Edge cases identified?** - None, empty, bounds, errors
- [ ] **Output path decided?** - Where to write files?
- [ ] **Type hints complete?** - Every function signature
- [ ] **Tests needed?** - If yes, create test files
- [ ] **Clean architecture?** - Proper layer separation
- [ ] **Git status checked?** - New folders visible?

---

## 🚫 ANTI-PATTERNS (STRICTLY FORBIDDEN)

### Code Smells:
- ❌ **God class** - single class >200 lines with 5+ responsibilities
- ❌ **God file** - everything in one file >300 lines
- ❌ **Deep nesting** - >3 levels of if/for/while
- ❌ **Long functions** - >50 lines doing multiple things
- ❌ **Primitive obsession** - use dataclasses/interfaces, not dicts
- ❌ **Mutable defaults** - `def func(data: list = []):`

### Development Smells:
- ❌ **TODO comments** - implement or don't mention
- ❌ **Commented code** - delete it, use git history
- ❌ **Wildcard imports** - `from module import *`
- ❌ **Circular imports** - restructure your modules
- ❌ **Global state** - use dependency injection
- ❌ **Magic numbers** - use named constants
- ❌ **Uncommitted "KÉSZ"** - git status FIRST!

---

## 🧪 TESTING REQUIREMENTS

### Testing Rules:
- **Coverage target**: >80%
- **One test = one behavior**
- **Arrange-Act-Assert** pattern
- **Test file mirrors source** - `src/foo.py` → `tests/test_foo.py`
- **No test modification** - tests define spec, code must conform

---

## 📐 QUALITY METRICS (ENFORCEMENT)

### Quality Gates:
- ✅ **Formatting**: Code formatted (no changes needed)
- ✅ **Linting**: No linting errors
- ✅ **Types**: No type errors
- ✅ **Quality Score**: ≥8.0/10
- ✅ **Coverage**: ≥80%
- ✅ **Complexity**: CC <8 per function
- ✅ **Security**: No security issues
- ✅ **Git**: All changes tracked and visible

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
git status → files visible ✅
Files complete. Ready for validation.
```

### Session Start - KÖTELEZŐ:
```bash
# 1. Hol vagyok?
pwd

# 2. Mi a git állapot?
git status

# 3. Mi van itt?
ls -la

# 4. Context beolvasás
cat PLAN.md 2>/dev/null || echo "No PLAN.md"
cat STATUS.md 2>/dev/null || echo "No STATUS.md"
```

---

## 🚀 QUICK REFERENCE

### Before Every Code Generation:
1. ✅ Read requirements carefully
2. ✅ `git status` - check current state
3. ✅ Check if single-file or multi-file needed
4. ✅ Plan file structure and dependencies
5. ✅ Identify edge cases
6. ✅ Confirm output paths

### During Code Generation:
1. ✅ Complete files only (no truncation)
2. ✅ Type hints on everything
3. ✅ Docstrings brief but present
4. ✅ Null/edge case validation
5. ✅ Security checks (SQL, secrets, input)

### After Code Generation:
1. ✅ Signal file completion
2. ✅ List all files created
3. ✅ `git status` - verify files visible
4. ✅ Suggest validation commands
5. ✅ Wait for feedback before next step
6. ✅ ONLY mark "KÉSZ" if committed or staged

---

## 📊 METRIC TARGETS

| Metric | Target | Notes |
|--------|--------|-------|
| Code Coverage | >80% | pytest-cov / jest |
| Quality Score | >8.0 | pylint / eslint |
| Linting Errors | 0 | flake8 / eslint |
| Type Coverage | 100% | mypy / tsc |
| Cyclomatic Complexity | <8/function | radon / complexity |
| Security Issues | 0 | bandit / npm audit |
| Line Length | ≤100 chars | formatter |
| Function Length | ≤50 lines | manual |
| Class Length | ≤200 lines | manual |
| File Length | ≤250 lines | manual |
| Git Status | Clean or Staged | `git status` |

---

## 🏁 TL;DR

**Terminal AI agents must:**
- 🔥 CHECK `git status` after new folders - FIRST PRIORITY!
- 📝 Write complete files to disk
- 🎯 Follow clean architecture (modular, not microservices)
- ✅ Pass all quality gates (>80% coverage, >8.0 quality)
- 🔒 Enforce security (no eval, parameterized SQL)
- 📐 Respect limits (≤250 lines/file, ≤50 lines/function)
- 🚫 Avoid anti-patterns (God classes, TODO, wildcards)
- 💬 Communicate minimally (Hungarian, informal)
- 📂 Maintain state in files (PLAN.md, STATUS.md)
- 🔄 NEVER say "KÉSZ" without `git status` verification

**Remember: Code is written once, read many times. Git tracks everything - or it doesn't exist.** 🚀
