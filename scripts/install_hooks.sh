#!/bin/bash
#
# Git hooks installer script
# Install repository-level git hooks from .githooks directory
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📦 Git hooks telepítése..."
echo ""

# Copy hooks from .githooks to .git/hooks
HOOKS_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Hiba: $HOOKS_DIR nem található"
    exit 1
fi

# Install each hook
for hook in "$HOOKS_DIR"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        target="$GIT_HOOKS_DIR/$hook_name"

        cp "$hook" "$target"
        chmod +x "$target"
        echo "  ✅ $hook_name"
    fi
done

echo ""
echo "✅ Git hooks telepítve!"
echo ""
echo "Aktív hookok:"
ls -1 "$GIT_HOOKS_DIR" | grep -E "commit-msg|pre-commit|pre-push" || echo "  (nincsenek extra hookok)"
