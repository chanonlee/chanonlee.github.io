# 本地 Kafka 集群常用命令（无需本机安装 Kafka）

本仓库假定 **仅安装 Docker**，不在宿主机安装 `kafka-topics.sh` 等客户端。所有 Kafka 命令通过 **`./kafka-docker.sh`** 在 broker 容器内执行（等价于 `docker exec … /opt/kafka/bin/…`）。

本文档对应 `docker-compose.yml` 启动的 **5 broker KRaft** 集群。在宿主机上连接 Java CLI 时，任选一个对外端口作为 bootstrap 即可（见下表）。

---

## 若出现 `zsh: command not found: kafka-topics.sh`

说明你在**宿主机**直接敲了 `kafka-topics.sh`。请改用：

```bash
cd /path/to/kafka-loss-lab
./kafka-docker.sh kafka-topics.sh --bootstrap-server kafka1:9092 --list
```

（可选）若坚持本机安装客户端，可自行安装 Kafka 并配置 `PATH`；本仓库文档与脚本均以 Docker 为准。

---

## Bootstrap 地址（宿主机 ↔ Java CLI）

| Broker 容器名 | 宿主机端口（供本机进程连接） |
|---------------|------------------------------|
| kafka1        | localhost:19092              |
| kafka2        | localhost:29092              |
| kafka3        | localhost:39092              |
| kafka4        | localhost:49092              |
| kafka5        | localhost:59092              |

在容器**内部**调用 Kafka 脚本时，对 `kafka1` 容器使用 **`kafka1:9092`**（与宿主机端口无关）。

下文若需从宿主机用 CLI 试连，可先：

```bash
export BS=localhost:19092
```

---

## Topic：创建

**封装脚本（推荐，仅位置参数）：**

```bash
./create-topic.sh my-topic 3 3 2
```

**或手写完整参数：**

```bash
./kafka-docker.sh kafka-topics.sh \
  --bootstrap-server kafka1:9092 \
  --create \
  --if-not-exists \
  --topic my-topic \
  --partitions 3 \
  --replication-factor 3 \
  --config min.insync.replicas=2
```

---

## Topic：列出全部

```bash
./kafka-docker.sh kafka-topics.sh --bootstrap-server kafka1:9092 --list
```

---

## Topic：查看详情（分区、ISR、Leader 等）

```bash
./kafka-docker.sh kafka-topics.sh --bootstrap-server kafka1:9092 --describe --topic my-topic
```

查看所有 topic：

```bash
./kafka-docker.sh kafka-topics.sh --bootstrap-server kafka1:9092 --describe
```

---

## Topic：删除（慎用）

```bash
./kafka-docker.sh kafka-topics.sh --bootstrap-server kafka1:9092 --delete --topic my-topic
```

---

## Topic 里“还有多少消息”

### 用 `GetOffsetShell` 看每个分区的最早 / 最新 offset

**最新 offset**（`-1` 表示 latest）：

```bash
./kafka-docker.sh kafka-run-class.sh kafka.tools.GetOffsetShell \
  --bootstrap-server kafka1:9092 \
  --topic my-topic \
  --time -1
```

**最早 offset**（`-2` 表示 earliest）：

```bash
./kafka-docker.sh kafka-run-class.sh kafka.tools.GetOffsetShell \
  --bootstrap-server kafka1:9092 \
  --topic my-topic \
  --time -2
```

输出格式一般为：`topic:partition:offset`。  
**估算总消息数**：对每个分区计算 `(latest_offset - earliest_offset)`，再**求和**。

若镜像提供 **`kafka-get-offsets.sh`**，可先确认：

```bash
docker exec kafka1 ls /opt/kafka/bin/kafka-get-offsets.sh
```

### 消费组积压（LAG）

先有一个 consumer group（例如用本仓库 JAR 或控制台消费者消费过），再查：

```bash
./kafka-docker.sh kafka-consumer-groups.sh \
  --bootstrap-server kafka1:9092 \
  --describe --group <你的 group id>
```

关注输出中的 **LAG** 列。

---

## 控制台生产 / 消费（快速验证）

**生产者（读标准输入发送）：**

```bash
./kafka-docker.sh kafka-console-producer.sh --bootstrap-server kafka1:9092 --topic my-topic
```

**消费者：**

```bash
./kafka-docker.sh kafka-console-consumer.sh --bootstrap-server kafka1:9092 \
  --topic my-topic --from-beginning
```

---

## 与本仓库 Java CLI 的关系

- 创建 topic、生产、消费也可用项目打好的 JAR，见仓库根目录 [README.md](../README.md)。
- Java CLI 默认 bootstrap 为多个 `localhost:19xxx` 端口，与上表任选其一在单机实验中等价。

---

## 脚本路径说明

官方 `apache/kafka` 镜像内，工具一般在 **`/opt/kafka/bin/`**。若升级镜像后命令报错：

```bash
docker exec kafka1 ls /opt/kafka/bin/
```

确认实际脚本名称后再调整。
