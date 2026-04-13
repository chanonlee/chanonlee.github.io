#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=kafka-common.sh
source "$SCRIPT_DIR/kafka-common.sh"
require_docker

cd "$SCRIPT_DIR/.."
docker compose down -v
