#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=kafka-common.sh
source "$SCRIPT_DIR/kafka-common.sh"
require_docker

BROKER=${1:?用法: $0 <broker 1-5>}
NAME="kafka${BROKER}"

if [[ ! "$BROKER" =~ ^[1-5]$ ]]; then
  echo "broker 须为 1 到 5。" >&2
  exit 1
fi

require_kafka_container "$NAME"
docker kill "$NAME"
