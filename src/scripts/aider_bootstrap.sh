#!/usr/bin/env bash
else
echo "• Meglévő .gitignore érintetlenül hagyva"
fi


# 5) run_health_check.sh – statikus elemzés driver
if [[ ! -f scripts/run_health_check.sh ]]; then
cat > scripts/run_health_check.sh <<'RUN'
#!/usr/bin/env bash
set -euo pipefail


red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }


has() { command -v "$1" >/dev/null 2>&1; }


mkdir -p analysis_out


yellow "▶ Statikus elemzés indul… (analysis_out/)"


if has ruff; then
ruff check . --statistics --output-format=json > analysis_out/ruff_metrics.json || true
green "✔ ruff lefutott (analysis_out/ruff_metrics.json)"
else
red "✖ ruff nincs telepítve (pip install ruff)"
fi


if has mypy; then
mypy . --ignore-missing-imports --pretty > analysis_out/mypy_report.txt || true
green "✔ mypy lefutott (analysis_out/mypy_report.txt)"
else
yellow "⚠ mypy nem elérhető – kihagyva"
fi


if has radon; then
radon cc . -a -nb > analysis_out/radon_cc.txt || true
green "✔ radon lefutott (analysis_out/radon_cc.txt)"
else
yellow "⚠ radon nem elérhető – kihagyva"
fi


if has bandit; then
bandit -q -r . -f json -o analysis_out/bandit_security.json || true
green "✔ bandit lefutott (analysis_out/bandit_security.json)"
else
yellow "⚠ bandit nem elérhető – kihagyva"
fi


green "Kész. Nézd meg az analysis_out/ mappát."
RUN
chmod +x scripts/run_health_check.sh
echo "✔ Létrehozva: scripts/run_health_check.sh"
else
echo "• Meglévő scripts/run_health_check.sh érintetlenül hagyva"
fi


cat <<'DONE'
