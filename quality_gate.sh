#!/bin/bash

# =============================================================================
# Universal Python Quality Gate Script
# =============================================================================
# Használat: ./quality_gate.sh [options]
#   --config FILE       Egyedi config file (default: .quality_gate.conf)
#   --coverage NUM      Coverage threshold (default: 95)
#   --pylint NUM        Pylint minimum score (default: 9.0)
#   --max-lines NUM     Max sorok fájlonként (default: 250)
#   --src-dir DIR       Source könyvtár (default: auto-detect)
#   --test-dir DIR      Test könyvtár (default: auto-detect)
#   --skip-git          Git check kihagyása
#   --skip-tests        Tesztek kihagyása (CSAK fejlesztés közben!)
#   --strict            Szigorú mód: 0 warning
#   --help              Súgó
# =============================================================================
# VERZIÓ: 1.5.0 - 2025-12-22
# JAVÍTÁSOK:
#   - PYTHON_BIN változó (python3/python konzisztencia)
#   - bc függőség eltávolítva (Python-alapú score összehasonlítás)
#   - grep -oP (PCRE) eltávolítva (sed/awk kompatibilitás)
#   - Cirkuláris import: Pylint statikus elemzés (nem futtat kódot)
#   - pytest-cov ellenőrzés hozzáadva
#   - FAIL/WARN logika javítva (teszt FAIL = quality gate FAIL)
# =============================================================================

set -o pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Defaults
COVERAGE_THRESHOLD=95
PYLINT_MIN_SCORE=9.0
MAX_FILE_LINES=250
SRC_DIR=""
TEST_DIR=""
SKIP_GIT=false
SKIP_TESTS=false
STRICT_MODE=false
CONFIG_FILE=".quality_gate.conf"
VENV_PATHS=(".venv" "venv" ".env" "env")

# Python binary - will be set by detect_python()
PYTHON_BIN=""

# EXCLUDE patterns
EXCLUDE_DIRS=("venv" ".venv" "env" ".env" "__pycache__" ".git" "node_modules" "htmlcov" ".pytest_cache" ".mypy_cache" ".ruff_cache" "build" "dist" "*.egg-info" "migrations" ".tox" ".idea" ".vscode")

# Result tracking
ALL_PASSED=true
WARNINGS=0
declare -a FAILED_CHECKS=()
declare -a WARNING_CHECKS=()

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}$1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
}

print_status() {
    echo -e "${YELLOW}[CHECK]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ALL_PASSED=false
    FAILED_CHECKS+=("$1")
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
    WARNING_CHECKS+=("$1")
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

show_help() {
    head -20 "$0" | tail -16
    exit 0
}

build_pylint_ignores() {
    local IFS=','
    echo "${EXCLUDE_DIRS[*]}"
}

# =============================================================================
# Python Detection (KRITIKUS - konzisztens python használat)
# =============================================================================

detect_python() {
    # Prioritás: venv python > python3 > python
    if [ -n "$VIRTUAL_ENV" ]; then
        if command -v python &> /dev/null; then
            PYTHON_BIN="python"
            return 0
        fi
    fi
    
    if command -v python3 &> /dev/null; then
        PYTHON_BIN="python3"
        return 0
    fi
    
    if command -v python &> /dev/null; then
        PYTHON_BIN="python"
        return 0
    fi
    
    print_fail "Python nem található!"
    return 1
}

# =============================================================================
# Config & CLI Parsing
# =============================================================================

load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        print_info "Config betöltése: $CONFIG_FILE"
        source "$CONFIG_FILE"
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config)      CONFIG_FILE="$2"; shift 2 ;;
            --coverage)    COVERAGE_THRESHOLD="$2"; shift 2 ;;
            --pylint)      PYLINT_MIN_SCORE="$2"; shift 2 ;;
            --max-lines)   MAX_FILE_LINES="$2"; shift 2 ;;
            --src-dir)     SRC_DIR="$2"; shift 2 ;;
            --test-dir)    TEST_DIR="$2"; shift 2 ;;
            --skip-git)    SKIP_GIT=true; shift ;;
            --skip-tests)  SKIP_TESTS=true; shift ;;
            --strict)      STRICT_MODE=true; shift ;;
            --help|-h)     show_help ;;
            *)             echo "Ismeretlen opció: $1"; show_help ;;
        esac
    done
}

# =============================================================================
# Auto-Detection Functions
# =============================================================================

detect_project_name() {
    # pyproject.toml parsing Python-nal (megbízhatóbb)
    if [ -f "pyproject.toml" ] && [ -n "$PYTHON_BIN" ]; then
        local name
        name=$($PYTHON_BIN -c "
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

if tomllib:
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    name = data.get('project', {}).get('name', '')
    if not name:
        name = data.get('tool', {}).get('poetry', {}).get('name', '')
    print(name)
" 2>/dev/null)
        if [ -n "$name" ]; then
            echo "$name"
            return
        fi
    fi
    
    # Fallback: basename
    basename "$(pwd)"
}

detect_src_dir() {
    if [ -n "$SRC_DIR" ] && [ -d "$SRC_DIR" ]; then
        echo "$SRC_DIR"
        return
    fi
    
    for dir in "src" "lib" "app" "."; do
        if [ -d "$dir" ] && find "$dir" -maxdepth 2 -name "*.py" -type f \
            -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/__pycache__/*" \
            2>/dev/null | grep -q .; then
            echo "$dir"
            return
        fi
    done
    
    if find . -maxdepth 1 -name "*.py" -type f 2>/dev/null | grep -q .; then
        echo "."
        return
    fi
    
    echo ""
}

detect_test_dir() {
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        echo "$TEST_DIR"
        return
    fi
    
    for dir in "tests" "test" "spec"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return
        fi
    done
    echo ""
}

detect_venv() {
    for venv_path in "${VENV_PATHS[@]}"; do
        if [ -f "$venv_path/bin/activate" ]; then
            echo "$venv_path"
            return
        fi
    done
    echo ""
}

# =============================================================================
# Check Functions
# =============================================================================

check_python_version() {
    print_status "Python verzió ellenőrzése..."
    
    if [ -z "$PYTHON_BIN" ]; then
        print_fail "Python nem található"
        return 1
    fi
    
    local version
    version=$($PYTHON_BIN --version 2>&1 | cut -d' ' -f2)
    print_info "Python verzió: $version (binary: $PYTHON_BIN)"
    
    if $PYTHON_BIN -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_pass "Python >= 3.8"
        return 0
    else
        print_fail "Python >= 3.8 szükséges (jelenlegi: $version)"
        return 1
    fi
}

check_venv() {
    print_status "Virtual environment keresése..."
    
    local venv_path
    venv_path=$(detect_venv)
    
    if [ -n "$venv_path" ]; then
        print_info "Venv aktiválása: $venv_path"
        source "$venv_path/bin/activate"
        # Venv aktiválás után frissítjük a PYTHON_BIN-t
        PYTHON_BIN="python"
        print_pass "Virtual environment aktív"
        return 0
    else
        print_warn "Nincs venv - rendszer Python használata"
        return 0
    fi
}

check_dependencies() {
    print_status "Függőségek ellenőrzése..."
    
    # CLI tool + Python module párok
    local missing=()
    
    # pytest (CLI + module)
    if ! $PYTHON_BIN -c "import pytest" 2>/dev/null; then
        missing+=("pytest")
    fi
    
    # pytest-cov (KRITIKUS - ezt eddig nem ellenőriztük!)
    if ! $PYTHON_BIN -c "import pytest_cov" 2>/dev/null; then
        missing+=("pytest-cov")
    fi
    
    # coverage
    if ! $PYTHON_BIN -c "import coverage" 2>/dev/null; then
        missing+=("coverage")
    fi
    
    # pylint
    if ! $PYTHON_BIN -c "import pylint" 2>/dev/null; then
        missing+=("pylint")
    fi
    
    # mypy
    if ! $PYTHON_BIN -c "import mypy" 2>/dev/null; then
        missing+=("mypy")
    fi
    
    if [ ${#missing[@]} -eq 0 ]; then
        print_pass "Minden quality tool telepítve"
        return 0
    else
        print_fail "Hiányzó csomagok: ${missing[*]}"
        print_info "Telepítés: $PYTHON_BIN -m pip install ${missing[*]}"
        return 1
    fi
}

check_pylint() {
    local src_dir="$1"
    print_status "Pylint ellenőrzés (minimum: $PYLINT_MIN_SCORE)..."
    
    if [ -z "$src_dir" ] || [ ! -d "$src_dir" ]; then
        print_fail "Nincs source könyvtár - pylint FAIL"
        return 1
    fi
    
    local pylint_output
    pylint_output=$(mktemp)
    
    local ignore_list
    ignore_list=$(build_pylint_ignores)
    
    # PYTHONPATH beállítás
    local old_pythonpath="${PYTHONPATH:-}"
    if [ "$src_dir" != "." ]; then
        export PYTHONPATH="${src_dir}:${old_pythonpath}"
    fi
    
    $PYTHON_BIN -m pylint "$src_dir" \
        --ignore="$ignore_list" \
        --ignore-patterns="test_.*\.py" \
        --output-format=text 2>&1 | tee "$pylint_output" || true
    
    export PYTHONPATH="$old_pythonpath"
    
    # Score parsing sed-del (PCRE-mentes, univerzális)
    local score
    score=$(grep "Your code has been rated at" "$pylint_output" | sed -n 's/.*rated at \([0-9]*\.[0-9]*\).*/\1/p' | head -1)
    
    rm -f "$pylint_output"
    
    if [ -z "$score" ]; then
        print_warn "Pylint score nem olvasható"
        return 0
    fi
    
    print_info "Pylint score: $score / 10.0"
    
    # Score összehasonlítás Python-nal (bc nélkül!)
    if $PYTHON_BIN -c "import sys; sys.exit(0 if float('$score') >= float('$PYLINT_MIN_SCORE') else 1)"; then
        print_pass "Pylint score >= $PYLINT_MIN_SCORE"
        return 0
    else
        print_fail "Pylint score $score < $PYLINT_MIN_SCORE"
        return 1
    fi
}

check_mypy() {
    local src_dir="$1"
    print_status "Mypy type checking..."
    
    if [ -z "$src_dir" ] || [ ! -d "$src_dir" ]; then
        print_fail "Nincs source könyvtár - mypy FAIL"
        return 1
    fi
    
    # PYTHONPATH beállítás
    local old_pythonpath="${PYTHONPATH:-}"
    if [ "$src_dir" != "." ]; then
        export PYTHONPATH="${src_dir}:${old_pythonpath}"
    fi
    
    if $PYTHON_BIN -m mypy "$src_dir" \
        --ignore-missing-imports \
        --exclude "venv|\.venv|__pycache__|\.git|build|dist|migrations" \
        --no-error-summary 2>&1; then
        print_pass "Type checking passed"
        export PYTHONPATH="$old_pythonpath"
        return 0
    else
        print_fail "Type checking hibák találhatók"
        export PYTHONPATH="$old_pythonpath"
        return 1
    fi
}

check_tests_and_coverage() {
    local src_dir="$1"
    local test_dir="$2"
    print_status "Tesztek és coverage (minimum: ${COVERAGE_THRESHOLD}%)..."
    
    # --skip-tests flag kezelése
    if [ "$SKIP_TESTS" = true ]; then
        print_warn "Tesztek kihagyva (--skip-tests) - CSAK fejlesztés közben!"
        return 0
    fi
    
    # KRITIKUS: Hiányzó test könyvtár = FAIL
    if [ -z "$test_dir" ] || [ ! -d "$test_dir" ]; then
        print_fail "Test könyvtár KÖTELEZŐ! Hozd létre: tests/"
        print_info "AGENTS.md követelmény: ≥95% coverage, tesztek MANDATORY"
        return 1
    fi
    
    # Ellenőrizzük, hogy van-e teszt fájl
    local test_files
    test_files=$(find "$test_dir" -name "test_*.py" -o -name "*_test.py" 2>/dev/null | head -1)
    if [ -z "$test_files" ]; then
        print_fail "Nincs teszt fájl a $test_dir könyvtárban!"
        return 1
    fi
    
    local cov_output
    cov_output=$(mktemp)
    
    local cov_source="$src_dir"
    [ "$src_dir" = "." ] && cov_source="."
    
    # PYTHONPATH beállítás
    local old_pythonpath="${PYTHONPATH:-}"
    if [ "$src_dir" != "." ] && [ -d "$src_dir" ]; then
        export PYTHONPATH="${src_dir}:${old_pythonpath}"
        print_info "PYTHONPATH beállítva: ${src_dir}"
    fi
    
    $PYTHON_BIN -m pytest "$test_dir" -v --tb=short \
        --cov="$cov_source" \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --cov-fail-under="$COVERAGE_THRESHOLD" 2>&1 | tee "$cov_output"
    
    local pytest_exit=${PIPESTATUS[0]}
    
    export PYTHONPATH="$old_pythonpath"
    
    # Exit code 0 = minden OK
    if [ $pytest_exit -eq 0 ]; then
        print_pass "Minden teszt PASSED, coverage >= ${COVERAGE_THRESHOLD}%"
        rm -f "$cov_output"
        return 0
    fi
    
    # =========================================================================
    # HIBA KEZELÉS - MINDEN HIBA FAIL, NEM WARN!
    # =========================================================================
    
    # Import error vagy collection error?
    if grep -q "ERROR collecting\|ImportError\|ModuleNotFoundError" "$cov_output"; then
        local error_count
        error_count=$(grep -c "ERROR\|ImportError\|ModuleNotFoundError" "$cov_output" 2>/dev/null || echo "?")
        print_fail "Import/collection error - tesztek nem futottak le! ($error_count hiba)"
        rm -f "$cov_output"
        return 1
    fi
    
    # Teszt FAILED?
    if grep -q "FAILED" "$cov_output"; then
        local failed_count
        failed_count=$(grep -c "FAILED" "$cov_output" 2>/dev/null || echo "?")
        print_fail "Tesztek FAILED ($failed_count db) - QUALITY GATE FAIL!"
        rm -f "$cov_output"
        return 1
    fi
    
    # Coverage nem elég?
    if grep -q "TOTAL" "$cov_output"; then
        local coverage_pct
        coverage_pct=$(grep "TOTAL" "$cov_output" | tail -1 | awk '{print $NF}' | sed 's/%//')
        
        if [ -n "$coverage_pct" ]; then
            if $PYTHON_BIN -c "import sys; sys.exit(0 if float('$coverage_pct') >= float('$COVERAGE_THRESHOLD') else 1)" 2>/dev/null; then
                : # OK
            else
                print_fail "Coverage ${coverage_pct}% < ${COVERAGE_THRESHOLD}%"
                rm -f "$cov_output"
                return 1
            fi
        fi
    fi
    
    # Egyéb pytest hiba
    print_fail "Pytest hiba (exit code: $pytest_exit)"
    rm -f "$cov_output"
    return 1
}

check_file_sizes() {
    local src_dir="$1"
    print_status "File méretek ellenőrzése (max: $MAX_FILE_LINES sor)..."
    
    if [ -z "$src_dir" ]; then
        print_fail "Nincs source könyvtár - size check FAIL"
        return 1
    fi
    
    local oversized=()
    local exclude_pattern=""
    
    # Exclude pattern építése
    for dir in "${EXCLUDE_DIRS[@]}"; do
        exclude_pattern="$exclude_pattern -not -path '*/$dir/*'"
    done
    
    while IFS= read -r -d '' file; do
        local lines
        lines=$(wc -l < "$file")
        if [ "$lines" -gt "$MAX_FILE_LINES" ]; then
            oversized+=("$file ($lines sor)")
        fi
    done < <(find "$src_dir" -name "*.py" -type f \
        -not -path "*/venv/*" \
        -not -path "*/.venv/*" \
        -not -path "*/env/*" \
        -not -path "*/.env/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/.git/*" \
        -not -path "*/node_modules/*" \
        -not -path "*/build/*" \
        -not -path "*/dist/*" \
        -not -path "*/.pytest_cache/*" \
        -not -path "*/.mypy_cache/*" \
        -not -path "*/migrations/*" \
        -print0 2>/dev/null)
    
    if [ ${#oversized[@]} -eq 0 ]; then
        print_pass "Minden file <= $MAX_FILE_LINES sor"
        return 0
    else
        for f in "${oversized[@]}"; do
            print_fail "Túl nagy: $f"
        done
        return 1
    fi
}

check_circular_imports() {
    local src_dir="$1"
    print_status "Cirkuláris import ellenőrzés (Pylint statikus elemzés)..."
    
    if [ -z "$src_dir" ]; then
        print_warn "Nincs source könyvtár - circular check kihagyva"
        return 0
    fi
    
    # PYTHONPATH beállítás
    local old_pythonpath="${PYTHONPATH:-}"
    if [ "$src_dir" != "." ]; then
        export PYTHONPATH="${src_dir}:${old_pythonpath}"
    fi
    
    # Pylint statikus elemzés - NEM FUTTAT KÓDOT!
    local circular_output
    circular_output=$($PYTHON_BIN -m pylint "$src_dir" \
        --disable=all \
        --enable=cyclic-import \
        --persistent=n \
        --score=n \
        --ignore-patterns="test_.*\.py" 2>&1 || true)
    
    export PYTHONPATH="$old_pythonpath"
    
    if echo "$circular_output" | grep -q "cyclic-import"; then
        print_warn "Lehetséges cirkuláris importok találhatók:"
        echo "$circular_output" | grep "cyclic-import"
        return 0  # WARNING, nem FAIL (false positive-ok miatt)
    else
        print_pass "Nincs észlelt cirkuláris import"
        return 0
    fi
}

check_git_status() {
    if [ "$SKIP_GIT" = true ]; then
        print_info "Git check kihagyva (--skip-git)"
        return 0
    fi
    
    print_status "Git státusz ellenőrzése..."
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_info "Nem git repository - kihagyva"
        return 0
    fi
    
    local status
    status=$(git status --porcelain 2>/dev/null)
    
    if [ -z "$status" ]; then
        print_pass "Git working directory clean"
        return 0
    else
        print_warn "Uncommitted változások vannak"
        git status --short
        return 0
    fi
}

check_security() {
    print_status "Biztonsági ellenőrzés (bandit)..."
    
    if ! $PYTHON_BIN -c "import bandit" 2>/dev/null; then
        print_info "Bandit nincs telepítve - kihagyva"
        return 0
    fi
    
    local src_dir="$1"
    if [ -z "$src_dir" ]; then
        return 0
    fi
    
    if $PYTHON_BIN -m bandit -r "$src_dir" \
        --exclude "venv,.venv,env,.env,__pycache__,build,dist,tests,test,migrations" \
        -ll -q 2>/dev/null; then
        print_pass "Nincs magas kockázatú biztonsági probléma"
        return 0
    else
        print_warn "Biztonsági figyelmeztetések - nézd meg: bandit -r $src_dir"
        return 0
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    parse_args "$@"
    load_config
    
    # Python detektálás ELŐSZÖR
    if ! detect_python; then
        exit 1
    fi
    
    local project_name
    project_name=$(detect_project_name)
    
    print_header "🚀 Quality Gate: $project_name"
    echo ""
    print_info "Thresholds: coverage=${COVERAGE_THRESHOLD}%, pylint=${PYLINT_MIN_SCORE}, max-lines=${MAX_FILE_LINES}"
    print_info "Excluded: ${EXCLUDE_DIRS[*]}"
    
    local src_dir test_dir
    src_dir=$(detect_src_dir)
    test_dir=$(detect_test_dir)
    
    print_info "Source dir: ${src_dir:-'(nincs)'}"
    print_info "Test dir: ${test_dir:-'(nincs - FAIL!)'}"
    
    echo ""
    
    check_python_version
    check_venv
    check_dependencies
    
    echo ""
    check_pylint "$src_dir"
    
    echo ""
    check_mypy "$src_dir"
    
    echo ""
    check_tests_and_coverage "$src_dir" "$test_dir"
    
    echo ""
    check_file_sizes "$src_dir"
    
    echo ""
    check_circular_imports "$src_dir"
    
    echo ""
    check_git_status
    
    echo ""
    check_security "$src_dir"
    
    # Summary
    print_header "📊 Quality Gate Summary"
    
    if [ "$ALL_PASSED" = true ]; then
        if [ "$WARNINGS" -eq 0 ]; then
            echo -e "${GREEN}✅ ALL CHECKS PASSED - Production ready!${NC}"
        else
            echo -e "${GREEN}✅ ALL CHECKS PASSED${NC} ${YELLOW}($WARNINGS warning(s))${NC}"
            if [ "$STRICT_MODE" = true ]; then
                echo -e "${RED}STRICT MODE: Warningok miatt FAIL${NC}"
                exit 1
            fi
        fi
        exit 0
    else
        echo -e "${RED}❌ FAILED CHECKS:${NC}"
        for check in "${FAILED_CHECKS[@]}"; do
            echo -e "  ${RED}•${NC} $check"
        done
        
        if [ "$WARNINGS" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}⚠️  WARNINGS:${NC}"
            for warn in "${WARNING_CHECKS[@]}"; do
                echo -e "  ${YELLOW}•${NC} $warn"
            done
        fi
        
        echo ""
        echo "Javítási tippek:"
        echo "  $PYTHON_BIN -m pylint $src_dir --output-format=colorized"
        echo "  $PYTHON_BIN -m mypy $src_dir --ignore-missing-imports"
        echo "  $PYTHON_BIN -m pytest $test_dir -v --cov=$src_dir"
        exit 1
    fi
}

main "$@"
