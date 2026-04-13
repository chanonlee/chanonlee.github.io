package com.example.kafkalosslab.command;

import com.example.kafkalosslab.cli.CliConstants;
import com.example.kafkalosslab.cli.CliOptions;
import com.example.kafkalosslab.kafka.KafkaClientProps;
import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * {@code produce}：向指定 topic 发送带序号的测试消息，支持同步/异步与可选固定分区。
 */
public final class ProduceCommand implements CliCommand {

    /** 第一层：从 CLI 解析出的生产参数。 */
    private record Options(
            String bootstrap,
            String topic,
            int count,
            String prefix,
            String acks,
            boolean enableIdempotence,
            boolean sync,
            long lingerMs,
            int batchSize,
            long sleepMs,
            Integer partition
    ) {
        static Options fromCliArgs(String[] args) {
            Map<String, String> o = CliOptions.parse(args);
            return new Options(
                    o.getOrDefault("--bootstrap", CliConstants.DEFAULT_BOOTSTRAP),
                    CliOptions.req(o, "--topic"),
                    Integer.parseInt(o.getOrDefault("--count", "1000")),
                    o.getOrDefault("--prefix", "msg"),
                    o.getOrDefault("--acks", "all"),
                    Boolean.parseBoolean(o.getOrDefault("--enable-idempotence", "true")),
                    Boolean.parseBoolean(o.getOrDefault("--sync", "true")),
                    Long.parseLong(o.getOrDefault("--linger-ms", "0")),
                    Integer.parseInt(o.getOrDefault("--batch-size", "16384")),
                    Long.parseLong(o.getOrDefault("--sleep-ms", "0")),
                    CliOptions.optInt(o, "--partition")
            );
        }
    }

    @Override
    public String name() {
        return "produce";
    }

    @Override
    public void printHelp() {
        System.out.println("""
                Usage: kafka-loss-lab produce --topic <name> [options]

                Options:
                  --bootstrap <servers>           Default: %s
                  --topic <name>                  Required
                  --count <n>                     Default: 1000
                  --prefix <s>                    Default: msg
                  --acks <s>                      Default: all
                  --enable-idempotence <true|false> Default: true
                  --sync <true|false>             sync send or async send, Default: true
                  --linger-ms <n>                 Default: 0
                  --batch-size <n>                Default: 16384
                  --sleep-ms <n>                  Default: 0
                  --partition <n>                 Optional; omit for default partitioning
                """.formatted(CliConstants.DEFAULT_BOOTSTRAP));
    }

    @Override
    public int run(String[] args) throws Exception {
        return execute(Options.fromCliArgs(args));
    }

    /** 第二层：构建 Producer、按 sync/async 策略发送并汇总结果。 */
    private static int execute(Options opts) throws Exception {
        Properties props = producerProperties(opts);
        AtomicInteger success = new AtomicInteger();
        AtomicInteger failed = new AtomicInteger();
        CountDownLatch latch = new CountDownLatch(opts.sync() ? 0 : opts.count());
        Instant start = Instant.now();
        try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {
            sendAll(producer, opts, success, failed, latch);
            producer.flush();
            awaitAsyncCallbacks(opts, latch);
        }
        printProduceSummary(opts, success, failed, start);
        return failed.get() == 0 ? 0 : 2;
    }

    private static Properties producerProperties(Options opts) {
        Properties props = KafkaClientProps.baseProducerProps(opts.bootstrap());
        props.put(ProducerConfig.ACKS_CONFIG, opts.acks());
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, Boolean.toString(opts.enableIdempotence()));
        props.put(ProducerConfig.LINGER_MS_CONFIG, Long.toString(opts.lingerMs()));
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, Integer.toString(opts.batchSize()));
        return props;
    }

    private static void sendAll(
            KafkaProducer<String, String> producer,
            Options opts,
            AtomicInteger success,
            AtomicInteger failed,
            CountDownLatch latch) throws InterruptedException {
        for (int i = 0; i < opts.count(); i++) {
            String key = Integer.toString(i);
            ProducerRecord<String, String> record = buildRecord(opts, i, key);
            if (opts.sync()) {
                sendSync(producer, record, key, success, failed);
            } else {
                producer.send(record, asyncCallback(key, success, failed, latch));
            }
            sleepIfNeeded(opts.sleepMs());
        }
    }

    private static ProducerRecord<String, String> buildRecord(Options opts, int index, String key) {
        String value = opts.prefix() + "-" + index + "|sentAt=" + System.currentTimeMillis()
                + "|run=" + UUID.randomUUID();
        return opts.partition() == null
                ? new ProducerRecord<>(opts.topic(), key, value)
                : new ProducerRecord<>(opts.topic(), opts.partition(), key, value);
    }

    private static void sendSync(
            KafkaProducer<String, String> producer,
            ProducerRecord<String, String> record,
            String key,
            AtomicInteger success,
            AtomicInteger failed) {
        try {
            RecordMetadata md = producer.send(record).get();
            success.incrementAndGet();
            System.out.printf("sent key=%s partition=%d offset=%d%n", key, md.partition(), md.offset());
        } catch (Exception e) {
            failed.incrementAndGet();
            System.err.printf("send failed key=%s error=%s%n", key, e.getMessage());
        }
    }

    private static void sleepIfNeeded(long sleepMs) throws InterruptedException {
        if (sleepMs > 0) {
            Thread.sleep(sleepMs);
        }
    }

    private static void awaitAsyncCallbacks(Options opts, CountDownLatch latch) throws InterruptedException {
        if (!opts.sync()) {
            long waitSec = asyncCallbackWaitSeconds(opts);
            boolean done = latch.await(waitSec, TimeUnit.SECONDS);
            if (!done) {
                long remaining = latch.getCount();
                System.err.printf(
                        "警告: %d 秒内未等齐全部异步回调（剩余 %d 条），success/failed 可能不完整；"
                                + "可减小 --count/--sleep-ms 或确认 broker 与健康网络。%n",
                        waitSec, remaining);
            }
        }
    }

    /**
     * 异步模式下回调完成时间随条数、每条间隔、linger 增长；原先固定 30s 易导致大批量时未等齐回调就退出。
     */
    private static long asyncCallbackWaitSeconds(Options opts) {
        long sleepBudget = (opts.count() * Math.max(0L, opts.sleepMs()) + 999) / 1000;
        long throughputBudget = Math.max(1L, opts.count() / 50L);
        return Math.max(120L, 60L + throughputBudget + sleepBudget);
    }

    private static void printProduceSummary(Options opts, AtomicInteger success, AtomicInteger failed, Instant start) {
        Duration took = Duration.between(start, Instant.now());
        System.out.printf("produce done success=%d failed=%d took=%dms config[acks=%s,idempotence=%s,sync=%s]%n",
                success.get(), failed.get(), took.toMillis(), opts.acks(), opts.enableIdempotence(), opts.sync());
    }

    /** 异步发送时的回调：统计成功/失败并驱动 latch。 */
    private static Callback asyncCallback(String key, AtomicInteger success, AtomicInteger failed, CountDownLatch latch) {
        return (RecordMetadata metadata, Exception exception) -> {
            try {
                if (exception == null) {
                    success.incrementAndGet();
                    System.out.printf("ack key=%s partition=%d offset=%d%n", key, metadata.partition(), metadata.offset());
                } else {
                    failed.incrementAndGet();
                    System.err.printf("send failed key=%s error=%s%n", key, exception.getMessage());
                }
            } finally {
                latch.countDown();
            }
        };
    }
}
