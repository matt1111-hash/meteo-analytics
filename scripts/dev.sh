#!/usr/bin/env bash
# Start backend + frontend dev stack for E2E testing.
# Usage: ./scripts/dev.sh
# Environment:
#   BACKEND_PORT  — backend port (default: 8003)
#   FRONTEND_PORT — frontend port (default: 5174)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8003}"
FRONTEND_PORT="${FRONTEND_PORT:-5174}"
BACKEND_HEALTH="http://127.0.0.1:${BACKEND_PORT}/health"
FRONTEND_HEALTH="http://127.0.0.1:${FRONTEND_PORT}"

backend_pid=""
frontend_pid=""
started_backend=0
started_frontend=0

cleanup() {
  if [[ -n "$backend_pid" ]]; then
    kill "$backend_pid" 2>/dev/null || true
  fi
  if [[ -n "$frontend_pid" ]]; then
    kill "$frontend_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

# --- Backend ---
if ! curl -fsS "$BACKEND_HEALTH" >/dev/null 2>&1; then
  (
    cd "$PROJECT_ROOT"
    exec python3 -m uvicorn src.api.main:app \
      --host 127.0.0.1 \
      --port "$BACKEND_PORT"
  ) &
  backend_pid=$!
  started_backend=1
fi

for _ in $(seq 1 60); do
  curl -fsS "$BACKEND_HEALTH" >/dev/null 2>&1 && break
  if [[ -n "$backend_pid" ]] && ! kill -0 "$backend_pid" 2>/dev/null; then
    echo "ERROR: backend process exited prematurely" >&2
    exit 1
  fi
  sleep 2
done

if ! curl -fsS "$BACKEND_HEALTH" >/dev/null 2>&1; then
  echo "ERROR: backend not healthy at $BACKEND_HEALTH" >&2
  exit 1
fi
echo "Backend ready at $BACKEND_HEALTH"

# --- Frontend ---
if ! curl -fsS "$FRONTEND_HEALTH" >/dev/null 2>&1; then
  (
    cd "$PROJECT_ROOT/frontend"
    exec npx vite --host 127.0.0.1 --port "$FRONTEND_PORT" --strictPort
  ) &
  frontend_pid=$!
  started_frontend=1
fi

for _ in $(seq 1 120); do
  if curl -fsS "$FRONTEND_HEALTH" >/dev/null 2>&1; then
    echo "Frontend responded OK"
    break
  fi
  if [[ -n "$frontend_pid" ]] && ! kill -0 "$frontend_pid" 2>/dev/null; then
    echo "ERROR: frontend process exited prematurely" >&2
    exit 1
  fi
  sleep 1
done

if ! curl -fsS "$FRONTEND_HEALTH" >/dev/null 2>&1; then
  echo "ERROR: frontend not healthy at $FRONTEND_HEALTH" >&2
  exit 1
fi
echo "Frontend ready at $FRONTEND_HEALTH"

echo "Dev stack running (backend=$BACKEND_PORT, frontend=$FRONTEND_PORT)"
wait
