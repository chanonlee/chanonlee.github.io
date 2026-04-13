if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "勿直接执行本文件。" >&2
  exit 1
fi

KAFKA_LOSS_LAB_SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KAFKA_DOCKER_SH="${KAFKA_LOSS_LAB_SCRIPTS}/kafka-docker.sh"

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "需要 docker。" >&2
    exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "Docker 未运行或无权访问。" >&2
    exit 1
  fi
}

require_kafka_container() {
  local c=$1
  if ! docker inspect "$c" >/dev/null 2>&1; then
    echo "容器 $c 不存在，先执行 ./scripts/up.sh" >&2
    exit 1
  fi
}
