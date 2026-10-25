#!/usr/bin/env bash
# Kaspi seller kit installer (macOS / Linux / Git Bash).
# Usage: bash install.sh [--home DIR] [--vault DIR] [--force] [--skip-npm]
# Copies skills to <home>/.claude/skills, creates the product vault, installs 1688-cli.
# Nothing is overwritten unless --force is given. No secrets are read or written.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="$HOME"; VAULT=""; FORCE=0; SKIP_NPM=0
while [ $# -gt 0 ]; do
  case "$1" in
    --home) HOME_DIR="$2"; shift 2;;
    --vault) VAULT="$2"; shift 2;;
    --force) FORCE=1; shift;;
    --skip-npm) SKIP_NPM=1; shift;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -n "$VAULT" ] || VAULT="$HOME_DIR/kaspi-agents"
SKILLS_DST="$HOME_DIR/.claude/skills"
mkdir -p "$SKILLS_DST"

echo "== Skills -> $SKILLS_DST"
for src in "$KIT"/skills/*/; do
  name="$(basename "$src")"
  dst="$SKILLS_DST/$name"
  if [ -e "$dst" ] && [ "$FORCE" -eq 0 ]; then
    echo "   skip (exists): $name  (use --force to overwrite)"
    continue
  fi
  rm -rf "$dst"
  cp -r "$src" "$dst"
  echo "   installed: $name"
done

echo "== Vault -> $VAULT"
if [ ! -e "$VAULT" ]; then
  cp -r "$KIT/vault-template" "$VAULT"
  echo "   created from vault-template"
else
  echo "   exists, left untouched"
fi
if [ ! -e "$VAULT/CLAUDE.md" ] || [ "$FORCE" -eq 1 ]; then
  VAULT_ESC="${VAULT//&/\\&}"
  sed "s|__VAULT_PATH__|${VAULT_ESC}|" "$KIT/CLAUDE.md" > "$VAULT/CLAUDE.md"
  echo "   CLAUDE.md written (vault path filled in)"
fi

echo "== 1688-cli"
if [ "$SKIP_NPM" -eq 1 ]; then
  echo "   skipped (--skip-npm)"
elif command -v npm >/dev/null 2>&1; then
  if command -v 1688 >/dev/null 2>&1; then
    echo "   already installed"
  else
    npm install -g 1688-cli || echo "WARNING: npm install -g 1688-cli failed, install Node.js LTS and retry"
  fi
else
  echo "WARNING: npm not found. Install Node.js LTS from https://nodejs.org then run: npm install -g 1688-cli"
fi

echo
echo "DONE. Next (manual): log in to 1688 by QR code ->  1688 --help  (see INSTALL.md step 5)."
echo "Then open Claude Code in: $VAULT"
