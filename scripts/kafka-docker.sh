#!/usr/bin/env bash
# 从上一级 monorepo 根目录调用时，转发到 kafka-loss-lab 内的实现。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HERE/../kafka-loss-lab/scripts/kafka-docker.sh"
if [[ ! -f "$TARGET" ]]; then
  echo "找不到 $TARGET。请先 cd 到 kafka-loss-lab 目录后执行: ./scripts/kafka-docker.sh ..." >&2
  exit 1
fi
exec "$TARGET" "$@"
