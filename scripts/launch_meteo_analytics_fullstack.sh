#!/usr/bin/env bash

set -euo pipefail

show_error() {
  local title="$1"
  local message="$2"

  if command -v zenity >/dev/null 2>&1; then
    if zenity --error --title="$title" --text="$message" >/dev/null 2>&1; then
      return 0
    fi
  fi

  printf '%s\n\n%s\n' "$title" "$message" >&2
}

require_dir() {
  local path="$1"
  local label="$2"

  if [[ ! -d "$path" ]]; then
    show_error "Indítási hiba" "Hiányzó $label: $path"
    exit 1
  fi
}

require_file() {
  local path="$1"
  local label="$2"

  if [[ ! -f "$path" ]]; then
    show_error "Indítási hiba" "Hiányzó $label: $path"
    exit 1
  fi
}

PROJECT_ROOT="/home/tibor/PythonProjects/meteo-analytics"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PYTHON_BIN="$PROJECT_ROOT/venv/bin/python"
BACKEND_LOG="/tmp/meteo_analytics_backend.log"
FRONTEND_LOG="/tmp/meteo_analytics_frontend.log"
FRONTEND_URL="http://localhost:3000"
BACKEND_HEALTH_URL="http://127.0.0.1:8003/health"
FRONTEND_HEALTH_URL="http://localhost:3000"
BACKEND_PORT="8003"
FRONTEND_PORT="3000"
BACKEND_RETRY_COUNT="30"
FRONTEND_RETRY_COUNT="120"

backend_started=0
backend_pid=""
frontend_started=0
frontend_pid=""

cleanup() {
  if [[ "$backend_started" == "1" ]] && [[ -n "$backend_pid" ]]; then
    kill "$backend_pid" >/dev/null 2>&1 || true
  fi
  if [[ "$frontend_started" == "1" ]] && [[ -n "$frontend_pid" ]]; then
    kill "$frontend_pid" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

require_dir "$PROJECT_ROOT" "projektkönyvtár"
require_dir "$FRONTEND_DIR" "frontend projektkönyvtár"
require_file "$PYTHON_BIN" "Python virtuális környezet"
require_file "$PROJECT_ROOT/src/api/main.py" "FastAPI belépési pont"
require_file "$FRONTEND_DIR/package.json" "frontend package.json"

if ! command -v npm >/dev/null 2>&1; then
  show_error "Indítási hiba" "Az npm nem található a PATH-ban."
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  show_error "Indítási hiba" "A curl nem található a PATH-ban."
  exit 1
fi

if [[ "${1:-run}" == "--check" ]]; then
  require_dir "$FRONTEND_DIR/node_modules" "frontend node_modules"
  require_file "$PROJECT_ROOT/src/api/main.py" "FastAPI belépési pont"
  printf 'OK %s -> fullstack launcher backend %s frontend %s\n' \
    "$PROJECT_ROOT" \
    "$BACKEND_HEALTH_URL" \
    "$FRONTEND_URL"
  exit 0
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  if command -v zenity >/dev/null 2>&1; then
    zenity --info \
      --title="Meteo Analytics Full Stack" \
      --text="Első indítás: frontend függőségek telepítése indul."
  fi
  (
    cd "$FRONTEND_DIR"
    npm install
  )
fi

if ! curl -fsS "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
  : >"$BACKEND_LOG"
  (
    cd "$PROJECT_ROOT"
    exec "$PYTHON_BIN" -m uvicorn src.api.main:app --host 127.0.0.1 --port "$BACKEND_PORT"
  ) >"$BACKEND_LOG" 2>&1 &
  backend_pid="$!"
  backend_started=1
fi

for _ in $(seq 1 "$BACKEND_RETRY_COUNT"); do
  if curl -fsS "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
    break
  fi
  if [[ "$backend_started" == "1" ]] && [[ -n "$backend_pid" ]] && ! kill -0 "$backend_pid" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "$BACKEND_HEALTH_URL" >/dev/null 2>&1; then
  show_error "Indítási hiba" "A backend nem indult el. Log: $BACKEND_LOG"
  exit 1
fi

if [[ "$backend_started" == "1" ]] && [[ -n "$backend_pid" ]] && ! kill -0 "$backend_pid" >/dev/null 2>&1; then
  backend_started=0
  backend_pid=""
fi

if ! curl -fsS "$FRONTEND_HEALTH_URL" >/dev/null 2>&1; then
  : >"$FRONTEND_LOG"
  (
    cd "$FRONTEND_DIR"
    exec env PORT="$FRONTEND_PORT" npm run dev </dev/null
  ) >"$FRONTEND_LOG" 2>&1 &
  frontend_pid="$!"
  frontend_started=1
fi

for _ in $(seq 1 "$FRONTEND_RETRY_COUNT"); do
  if curl -fsS "$FRONTEND_HEALTH_URL" >/dev/null 2>&1; then
    break
  fi
  if [[ "$frontend_started" == "1" ]] && [[ -n "$frontend_pid" ]] && ! kill -0 "$frontend_pid" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "$FRONTEND_HEALTH_URL" >/dev/null 2>&1; then
  if ! grep -Eq "VITE v|ready in|Local:" "$FRONTEND_LOG" 2>/dev/null; then
    show_error "Indítási hiba" "A frontend nem indult el. Log: $FRONTEND_LOG"
    exit 1
  fi
fi

(
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$FRONTEND_URL" >/dev/null 2>&1 || true
  fi
) &

wait
