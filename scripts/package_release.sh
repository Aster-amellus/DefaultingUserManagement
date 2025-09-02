#!/usr/bin/env bash
set -euo pipefail

# Package frontend dist and docs into tarballs for GitHub Release.
# Usage: bash scripts/package_release.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
ARTIFACTS_DIR="$ROOT_DIR/release_artifacts"
FRONTEND_DIR="$ROOT_DIR/frontend"
DOCS_DIR="$ROOT_DIR/docs"

mkdir -p "$ARTIFACTS_DIR"

# 1) Frontend dist
if [ -d "$FRONTEND_DIR/dist" ]; then
  tar -czf "$ARTIFACTS_DIR/frontend-dist.tar.gz" -C "$FRONTEND_DIR" dist
else
  echo "[WARN] frontend/dist not found. Skipping frontend-dist.tar.gz."
fi

# 2) Docs bundle
if [ -d "$DOCS_DIR" ]; then
  tar -czf "$ARTIFACTS_DIR/docs.tar.gz" -C "$DOCS_DIR" .
else
  echo "[WARN] docs/ not found. Skipping docs.tar.gz."
fi

# 3) Deployment helpers
cp -f "$ROOT_DIR/docker-compose.prod.yml" "$ARTIFACTS_DIR/docker-compose.prod.yml" || true
cp -f "$ROOT_DIR/.env.example" "$ARTIFACTS_DIR/.env.example" || true
cp -f "$ROOT_DIR/README.md" "$ARTIFACTS_DIR/README.md" || true

# 4) Manifest
{
  echo "Release Artifacts Manifest"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "Included files:"
  ls -1 "$ARTIFACTS_DIR" || true
} > "$ARTIFACTS_DIR/MANIFEST.txt"

echo "[OK] Release artifacts prepared in: $ARTIFACTS_DIR"
