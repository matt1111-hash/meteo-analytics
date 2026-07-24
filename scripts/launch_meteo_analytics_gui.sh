#!/usr/bin/env bash
# Project-local launcher for the Meteo Analytics desktop GUI (meteo_gui_starter.py).
#
# Why this exists: the shared ~/PythonProjects/desktop_launchers/common.sh
# requires a ".venv/bin/python" virtualenv, but this project keeps its venv at
# "venv/", so the shared launcher fails with "Hiányzó Python virtuális környezet".
# This launcher uses the correct venv path directly (same convention as
# scripts/launch_meteo_analytics_fullstack.sh).

set -euo pipefail

show_error() {
  local title="$1"
  local message="$2"

  if command -v zenity >/dev/null 2>&1; then
    zenity --error --title="$title" --text="$message" >/dev/null 2>&1 || true
  fi
  printf '%s\n\n%s\n' "$title" "$message" >&2
}

require_file() {
  local path="$1"
  local label="$2"

  if [[ ! -f "$path" ]]; then
    show_error "Indítási hiba" "Hiányzó $label: $path"
    exit 1
  fi
}

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$PROJECT_ROOT/venv/bin/python"

require_file "$PYTHON_BIN" "Python virtuális környezet (venv/)"
require_file "$PROJECT_ROOT/meteo_gui_starter.py" "GUI belépési pont"

if [[ "${1:-run}" == "--check" ]]; then
  printf 'OK %s -> GUI launcher (venv python %s)\n' "$PROJECT_ROOT" "$PYTHON_BIN"
  exit 0
fi

cd "$PROJECT_ROOT"
# Capture output (the desktop icon runs with Terminal=false, so a crash would
# otherwise be invisible). If the window doesn't open, the traceback is here.
exec "$PYTHON_BIN" "$PROJECT_ROOT/meteo_gui_starter.py" >/tmp/meteo_gui.log 2>&1
