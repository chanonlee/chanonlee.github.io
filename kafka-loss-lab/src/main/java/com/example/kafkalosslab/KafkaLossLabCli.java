package com.example.kafkalosslab;

import com.example.kafkalosslab.cli.CliConstants;
import com.example.kafkalosslab.command.CliCommand;
import com.example.kafkalosslab.command.ConsumeCommand;
import com.example.kafkalosslab.command.ConsumeUnsafeCommand;
import com.example.kafkalosslab.command.CreateTopicCommand;
import com.example.kafkalosslab.command.ProduceCommand;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 入口：解析全局选项后，将第一个参数作为子命令名分派到 {@link CliCommand} 实现。
 */
public final class KafkaLossLabCli {

    private static final Map<String, CliCommand> COMMANDS;

    static {
        Map<String, CliCommand> m = new LinkedHashMap<>();
        register(m, new CreateTopicCommand());
        register(m, new ProduceCommand());
        register(m, new ConsumeCommand());
        register(m, new ConsumeUnsafeCommand());
        COMMANDS = Collections.unmodifiableMap(m);
    }

    private static void register(Map<String, CliCommand> map, CliCommand cmd) {
        map.put(cmd.name(), cmd);
    }

    private KafkaLossLabCli() {
    }

    public static void main(String[] args) {
        try {
            int code = dispatch(args);
            System.exit(code);
        } catch (IllegalArgumentException e) {
            System.err.println(e.getMessage());
            printUsage();
            System.exit(1);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static int dispatch(String[] args) throws Exception {
        if (args.length == 0) {
            printUsage();
            return 0;
        }
        String first = args[0];
        if ("-h".equals(first) || "--help".equals(first)) {
            printUsage();
            return 0;
        }
        if ("-V".equals(first) || "--version".equals(first)) {
            System.out.println(CliConstants.VERSION_LINE);
            return 0;
        }
        String[] rest = java.util.Arrays.copyOfRange(args, 1, args.length);
        if (rest.length >= 1 && ("-h".equals(rest[0]) || "--help".equals(rest[0]))) {
            printSubcommandHelp(first);
            return 0;
        }
        CliCommand cmd = COMMANDS.get(first);
        if (cmd == null) {
            System.err.println("Unknown command: " + first);
            printUsage();
            return 1;
        }
        return cmd.run(rest);
    }

    private static void printUsage() {
        System.out.println("""
                Usage: kafka-loss-lab [-h|--help] [-V|--version]
                       kafka-loss-lab <command> [--help] [options]

                Commands:
                  create-topic    Create a topic with RF and min ISR
                  produce         Produce numbered messages
                  consume         Consume safely: process first, then commitSync
                  consume-unsafe  Consume unsafely: commit before processing, optionally crash

                Global options:
                  -h, --help      Show this help
                  -V, --version   Show version
                """);
    }

    private static void printSubcommandHelp(String cmdName) {
        CliCommand cmd = COMMANDS.get(cmdName);
        if (cmd != null) {
            cmd.printHelp();
        } else {
            System.out.println("No detailed help for: " + cmdName);
        }
    }
}
