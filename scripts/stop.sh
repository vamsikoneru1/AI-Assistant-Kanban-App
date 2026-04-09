#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="pm-mvp"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME"
else
  echo "Container not running"
fi
