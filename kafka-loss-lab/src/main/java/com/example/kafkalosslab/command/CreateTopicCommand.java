package com.example.kafkalosslab.command;

import com.example.kafkalosslab.cli.CliConstants;
import com.example.kafkalosslab.cli.CliOptions;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.common.errors.TopicExistsException;

import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

/**
 * {@code create-topic}：通过 AdminClient 创建主题并设置 min.insync.replicas。
 */
public final class CreateTopicCommand implements CliCommand {

    /** 第一层：从 CLI 解析出的不可变参数。 */
    private record Options(
            String bootstrap,
            String topic,
            int partitions,
            short replicationFactor,
            String minIsr
    ) {
        static Options fromCliArgs(String[] args) {
            Map<String, String> o = CliOptions.parse(args);
            return new Options(
                    o.getOrDefault("--bootstrap", CliConstants.DEFAULT_BOOTSTRAP),
                    CliOptions.req(o, "--topic"),
                    Integer.parseInt(o.getOrDefault("--partitions", "3")),
                    Short.parseShort(o.getOrDefault("--replication-factor", "3")),
                    o.getOrDefault("--min-isr", "2")
            );
        }
    }

    @Override
    public String name() {
        return "create-topic";
    }

    @Override
    public void printHelp() {
        System.out.println("""
                Usage: kafka-loss-lab create-topic --topic <name> [options]

                Options:
                  --bootstrap <servers>     Default: %s
                  --topic <name>            Required
                  --partitions <n>          Default: 3
                  --replication-factor <n>    Default: 3
                  --min-isr <n>             Default: 2
                """.formatted(CliConstants.DEFAULT_BOOTSTRAP));
    }

    @Override
    public int run(String[] args) throws Exception {
        Options opts = Options.fromCliArgs(args);
        return execute(opts);
    }

    /** 第二层：与 Kafka AdminClient 交互。 */
    private static int execute(Options opts) throws Exception {
        Properties props = new Properties();
        props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, opts.bootstrap());
        try (AdminClient admin = AdminClient.create(props)) {
            NewTopic newTopic = new NewTopic(opts.topic(), opts.partitions(), opts.replicationFactor())
                    .configs(Map.of("min.insync.replicas", opts.minIsr()));
            try {
                admin.createTopics(List.of(newTopic)).all().get(30, TimeUnit.SECONDS);
                System.out.printf("created topic=%s partitions=%d rf=%d minISR=%s%n",
                        opts.topic(), opts.partitions(), opts.replicationFactor(), opts.minIsr());
            } catch (Exception e) {
                Throwable cause = e.getCause();
                if (cause instanceof TopicExistsException) {
                    System.out.printf("topic already exists: %s%n", opts.topic());
                } else {
                    throw e;
                }
            }
        }
        return 0;
    }
}
