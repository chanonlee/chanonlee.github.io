package com.example.kafkalosslab.command;

import com.example.kafkalosslab.cli.CliConstants;
import com.example.kafkalosslab.cli.CliOptions;
import com.example.kafkalosslab.kafka.KafkaClientProps;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Properties;

/**
 * {@code consume}：安全消费模式——先处理消息再 {@code commitSync}，用于对比“不丢消息”行为。
 */
public final class ConsumeCommand implements CliCommand {

    /** 第一层：从 CLI 解析出的消费参数。 */
    private record Options(
            String bootstrap,
            String topic,
            String group,
            int maxMessages,
            long processDelayMs
    ) {
        static Options fromCliArgs(String[] args) {
            Map<String, String> o = CliOptions.parse(args);
            return new Options(
                    o.getOrDefault("--bootstrap", CliConstants.DEFAULT_BOOTSTRAP),
                    CliOptions.req(o, "--topic"),
                    o.getOrDefault("--group", "loss-lab-safe"),
                    Integer.parseInt(o.getOrDefault("--max-messages", "100")),
                    Long.parseLong(o.getOrDefault("--process-delay-ms", "100"))
            );
        }
    }

    @Override
    public String name() {
        return "consume";
    }

    @Override
    public void printHelp() {
        System.out.println("""
                Usage: kafka-loss-lab consume --topic <name> [options]

                Options:
                  --bootstrap <servers>     Default: %s
                  --topic <name>            Required
                  --group <id>              Default: loss-lab-safe
                  --max-messages <n>        Default: 100
                  --process-delay-ms <n>    Default: 100
                """.formatted(CliConstants.DEFAULT_BOOTSTRAP));
    }

    @Override
    public int run(String[] args) throws Exception {
        return execute(Options.fromCliArgs(args));
    }

    /** 第二层：轮询、处理、同步提交位移。 */
    private static int execute(Options opts) throws Exception {
        Properties props = KafkaClientProps.baseConsumerProps(opts.bootstrap(), opts.group(), false);
        int processed = 0;
        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(List.of(opts.topic()));
            while (processed < opts.maxMessages()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(2));
                if (records.isEmpty()) {
                    continue;
                }
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("processing key=%s partition=%d offset=%d value=%s%n",
                            record.key(), record.partition(), record.offset(), record.value());
                    if (opts.processDelayMs() > 0) {
                        Thread.sleep(opts.processDelayMs());
                    }
                    processed++;
                    if (processed >= opts.maxMessages()) {
                        break;
                    }
                }
                consumer.commitSync();
                System.out.printf("commitSync after processed=%d%n", processed);
            }
        }
        System.out.printf("safe consumer done processed=%d%n", processed);
        return 0;
    }
}
