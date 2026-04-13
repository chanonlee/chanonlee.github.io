#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=kafka-common.sh
source "$SCRIPT_DIR/kafka-common.sh"
require_docker
require_kafka_container kafka1

if [[ $# -ne 4 ]]; then
  echo "用法: $0 <topic> <partitions> <replication-factor> <min-isr>" >&2
  exit 1
fi

TOPIC=$1
PARTITIONS=$2
REPLICATION=$3
MIN_ISR=$4

if [[ ! "$PARTITIONS" =~ ^[0-9]+$ ]] || [[ ! "$REPLICATION" =~ ^[0-9]+$ ]] || [[ ! "$MIN_ISR" =~ ^[0-9]+$ ]]; then
  echo "分区数、副本因子、min-isr 须为正整数。" >&2
  exit 1
fi

"$KAFKA_DOCKER_SH" kafka-topics.sh \
  --bootstrap-server kafka1:9092 \
  --create \
  --if-not-exists \
  --topic "$TOPIC" \
  --partitions "$PARTITIONS" \
  --replication-factor "$REPLICATION" \
  --config "min.insync.replicas=$MIN_ISR"

"$KAFKA_DOCKER_SH" kafka-topics.sh \
  --bootstrap-server kafka1:9092 \
  --describe \
  --topic "$TOPIC"
