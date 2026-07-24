#!/usr/bin/env bash

set -euo pipefail

show_error() {
  local title="$1"
  local message="$2"

  if command -v zenity >/dev/null 2>&1; then
    zenity --error --title="$title" --text="$message"
  else
    printf '%s\n\n%s\n' "$title" "$message" >&2
  fi
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

PROJECT_DIR="/home/tibor/PythonProjects/meteo-analytics/frontend"
APP_URL="http://localhost:5174"

require_dir "$PROJECT_DIR" "frontend projektkönyvtár"
require_file "$PROJECT_DIR/package.json" "frontend package.json"

if ! command -v npm >/dev/null 2>&1; then
  show_error "Indítási hiba" "Az npm nem található a PATH-ban."
  exit 1
fi

if [[ "${1:-run}" == "--check" ]]; then
  require_dir "$PROJECT_DIR/node_modules" "frontend node_modules"
  printf 'OK %s -> frontend launcher on %s\n' "$PROJECT_DIR" "$APP_URL"
  exit 0
fi

if [[ ! -d "$PROJECT_DIR/node_modules" ]]; then
  if command -v zenity >/dev/null 2>&1; then
    zenity --info \
      --title="Meteo Analytics Frontend" \
      --text="Első indítás: frontend függőségek telepítése indul."
  fi
  (
    cd "$PROJECT_DIR"
    npm install
  )
fi

(
  sleep 8
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$APP_URL" >/dev/null 2>&1 || true
  fi
) &

cd "$PROJECT_DIR"
exec env DANGEROUSLY_DISABLE_HOST_CHECK=true BROWSER=none PORT=5174 npm start
