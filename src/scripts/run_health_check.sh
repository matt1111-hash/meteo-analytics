#!/usr/bin/env bash
set -euo pipefail

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }

has() { command -v "$1" >/dev/null 2>&1; }

mkdir -p analysis_out

yellow "▶ Statikus elemzés indul… (analysis_out/)"

if has ruff; then
  ruff check . --statistics --output-format=json > analysis_out/ruff_metrics.json || true
  green "✔ ruff lefutott (analysis_out/ruff_metrics.json)"
else
  red   "✖ ruff nincs telepítve (pip install ruff)"
fi

green "Kész. Nézd meg az analysis_out/ mappát."
