#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="pm-mvp"
CONTAINER_NAME="pm-mvp"
DATA_DIR="$ROOT_DIR/backend/data"

mkdir -p "$DATA_DIR"

docker build -t "$IMAGE_NAME" "$ROOT_DIR"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

docker run -d \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  --env-file "$ROOT_DIR/backend/.env" \
  -e PM_DB_PATH=/app/backend/data/pm.db \
  -v "$DATA_DIR:/app/backend/data" \
  "$IMAGE_NAME" >/dev/null

echo "Running on http://localhost:8000"
