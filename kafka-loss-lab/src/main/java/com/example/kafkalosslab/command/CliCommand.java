package com.example.kafkalosslab.command;

/**
 * 单个子命令的契约：由 {@link com.example.kafkalosslab.KafkaLossLabCli} 根据首参数分派。
 */
public interface CliCommand {

    /** 与命令行第一个参数一致，例如 {@code create-topic}。 */
    String name();

    /** 执行子命令逻辑，返回进程退出码。 */
    int run(String[] args) throws Exception;

    /** 打印该子命令的详细用法（供 {@code kafka-loss-lab <command> --help} 使用）。 */
    void printHelp();
}
