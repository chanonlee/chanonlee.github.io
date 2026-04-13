#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=kafka-common.sh
source "$SCRIPT_DIR/kafka-common.sh"
require_docker

SCRIPT_NAME="${1:?用法: $0 <kafka-bin 脚本名> [参数…]}"
shift
require_kafka_container kafka1

exec docker exec kafka1 "/opt/kafka/bin/$SCRIPT_NAME" "$@"
