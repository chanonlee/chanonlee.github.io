# kafka-loss-lab

本实验包含两部分：

1. `docker-compose.yml`：本地启动 5 个 broker 的 Kafka KRaft 集群（**仅需 Docker，无需在本机安装 Kafka**）。
2. `java cli`：创建 topic、发消息、收消息，并演示几种“看起来像丢数据”的场景。

## 目录

- `docker-compose.yml`
- `scripts/up.sh`
- `scripts/down.sh`
- `scripts/create-topic.sh`
- `scripts/kafka-docker.sh`：在 broker 容器内调用 Kafka 官方脚本（本机不必安装 Kafka CLI）。说明与示例见 `scripts/local-kafka-commands.md`。在任意目录均可使用**绝对或相对路径**调用，例如 `path/to/kafka-loss-lab/scripts/kafka-docker.sh …`。
- `scripts/kafka-common.sh`：供其它脚本 `source` 的公共检查（Docker 可用、容器存在等），勿单独执行。
- `scripts/kill-broker.sh`
- `src/main/java/com/example/kafkalosslab/KafkaLossLabCli.java`

## 启动集群

```bash
cd kafka-loss-lab
./scripts/up.sh
```

创建测试 topic：

```bash
./scripts/create-topic.sh loss-lab 3 3 2
```

## 构建 CLI

要求：JDK 17+、Maven 3.9+

```bash
mvn -q -DskipTests package
```

产物：

```bash
target/kafka-loss-lab-1.0.0.jar
```

## CLI 示例

### 创建 topic

```bash
java -jar target/kafka-loss-lab-1.0.0.jar create-topic --topic loss-lab --partitions 3 --replication-factor 3 --min-isr 2
```

### 安全生产

```bash
java -jar target/kafka-loss-lab-1.0.0.jar produce \
  --topic loss-lab \
  --count 100 \
  --acks all \
  --enable-idempotence true \
  --sync true
```

### 风险生产（acks=0）

```bash
java -jar target/kafka-loss-lab-1.0.0.jar produce \
  --topic loss-lab \
  --count 10000 \
  --acks 0 \
  --enable-idempotence false \
  --sync false \
  --linger-ms 200 \
  --sleep-ms 1
```

发送过程中，另开一个终端杀掉 leader 所在 broker，例如：

```bash
./scripts/kill-broker.sh 1
```

然后启动消费者看实际收到多少。

### 安全消费

```bash
java -jar target/kafka-loss-lab-1.0.0.jar consume \
  --topic loss-lab \
  --group loss-lab-safe \
  --max-messages 100
```

### 不安全消费：先提交 offset，再处理，处理中崩溃

```bash
java -jar target/kafka-loss-lab-1.0.0.jar consume-unsafe \
  --topic loss-lab \
  --group loss-lab-unsafe \
  --max-messages 100 \
  --crash-after 5 \
  --use-auto-commit false
```

第一次运行会在处理第 5 条后退出。再次用**同一个 group**重启：

```bash
java -jar target/kafka-loss-lab-1.0.0.jar consume-unsafe \
  --topic loss-lab \
  --group loss-lab-unsafe \
  --max-messages 100 \
  --crash-after 0 \
  --use-auto-commit false
```

你会看到一部分消息被“跳过”，因为 offset 先提交了，业务还没真正处理完。

## 建议你实际演示的三种场景

### 场景 1：`acks=0` 的生产端“表面成功”

- topic 配置：`replication.factor=3, min.insync.replicas=2`
- producer：`acks=0, enable.idempotence=false, sync=false`
- 发送过程中 kill leader broker

预期：CLI 可能打印很多“已发送”，但消费到的消息数会小于发送数。

### 场景 2：`acks=all` + `min.insync.replicas=2`

- producer：`acks=all, enable.idempotence=true`
- kill 1 个 broker 再继续发送

预期：通常不会静默丢；如果 ISR 不足，更可能看到发送失败，而不是“成功但丢”。

### 场景 3：消费者先提交 offset 再处理

- `consume-unsafe`
- 在处理过程中故意退出

预期：重启后部分消息不再被该 consumer group 读取，表现为消费侧丢数。

## 清理

```bash
./scripts/down.sh
```
