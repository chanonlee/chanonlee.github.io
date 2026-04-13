#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=kafka-common.sh
source "$SCRIPT_DIR/kafka-common.sh"
require_docker

cd "$SCRIPT_DIR/.."
docker compose up -d

until docker inspect --format='{{json .State.Health.Status}}' kafka1 2>/dev/null | grep -q healthy; do
  sleep 3
done

echo "localhost:19092,localhost:29092,localhost:39092,localhost:49092,localhost:59092"
