package com.example.kafkalosslab.command;

import com.example.kafkalosslab.cli.CliConstants;
import com.example.kafkalosslab.cli.CliOptions;
import com.example.kafkalosslab.kafka.KafkaClientProps;
import org.apache.kafka.clients.consumer.CommitFailedException;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Properties;

/**
 * {@code consume-unsafe}：不安全消费——可先提交再处理，或配合自动提交，用于复现“重复消费/丢消息”场景。
 */
public final class ConsumeUnsafeCommand implements CliCommand {

    /** 第一层：从 CLI 解析出的参数。 */
    private record Options(
            String bootstrap,
            String topic,
            String group,
            int maxMessages,
            long processDelayMs,
            int crashAfter,
            boolean useAutoCommit
    ) {
        static Options fromCliArgs(String[] args) {
            Map<String, String> o = CliOptions.parse(args);
            return new Options(
                    o.getOrDefault("--bootstrap", CliConstants.DEFAULT_BOOTSTRAP),
                    CliOptions.req(o, "--topic"),
                    o.getOrDefault("--group", "loss-lab-unsafe"),
                    Integer.parseInt(o.getOrDefault("--max-messages", "100")),
                    Long.parseLong(o.getOrDefault("--process-delay-ms", "500")),
                    Integer.parseInt(o.getOrDefault("--crash-after", "5")),
                    Boolean.parseBoolean(o.getOrDefault("--use-auto-commit", "false"))
            );
        }
    }

    @Override
    public String name() {
        return "consume-unsafe";
    }

    @Override
    public void printHelp() {
        System.out.println("""
                Usage: kafka-loss-lab consume-unsafe --topic <name> [options]

                Options:
                  --bootstrap <servers>        Default: %s
                  --topic <name>               Required
                  --group <id>                 Default: loss-lab-unsafe
                  --max-messages <n>           Default: 100
                  --process-delay-ms <n>       Default: 500
                  --crash-after <n>            Crash after N processed; <=0 disables. Default: 5
                  --use-auto-commit <true|false> Default: false
                """.formatted(CliConstants.DEFAULT_BOOTSTRAP));
    }

    @Override
    public int run(String[] args) throws Exception {
        return execute(Options.fromCliArgs(args));
    }

    /** 第二层：poll →（可选）提前 commit → 逐条处理，可能触发模拟崩溃。 */
    private static int execute(Options opts) throws Exception {
        Properties props = KafkaClientProps.baseConsumerProps(opts.bootstrap(), opts.group(), opts.useAutoCommit());
        int processed = 0;
        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(List.of(opts.topic()));
            while (processed < opts.maxMessages()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(2));
                if (records.isEmpty()) {
                    continue;
                }

                if (!opts.useAutoCommit()) {
                    consumer.commitSync();
                    System.out.printf("UNSAFE commitSync before processing batch count=%d%n", records.count());
                }

                List<ConsumerRecord<String, String>> batch = new ArrayList<>();
                for (ConsumerRecord<String, String> record : records) {
                    batch.add(record);
                }

                processed = processBatchUnsafe(batch, processed, opts.crashAfter(), opts.processDelayMs());
            }
        } catch (CommitFailedException e) {
            System.err.println("commit failed: " + e.getMessage());
            return 2;
        }
        System.out.printf("unsafe consumer done processed=%d%n", processed);
        return 0;
    }

    /** 第三层：单条打印与延迟；达到 crashAfter 时直接退出进程以模拟宕机。 */
    private static int processBatchUnsafe(
            Collection<ConsumerRecord<String, String>> batch,
            int processed,
            int crashAfter,
            long processDelayMs
    ) throws Exception {
        for (ConsumerRecord<String, String> record : batch) {
            System.out.printf("UNSAFE processing key=%s partition=%d offset=%d value=%s%n",
                    record.key(), record.partition(), record.offset(), record.value());
            if (processDelayMs > 0) {
                Thread.sleep(processDelayMs);
            }
            processed++;
            if (crashAfter > 0 && processed >= crashAfter) {
                System.err.printf(
                        "Simulated crash after processed=%d. Offsets may already be committed. "
                                + "Restart with same group to observe skipped records.%n",
                        processed);
                System.exit(99);
            }
        }
        return processed;
    }
}
