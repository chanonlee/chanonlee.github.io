package com.example.kafkalosslab.cli;

/**
 * 全局 CLI 常量：默认集群地址、版本号等。
 */
public final class CliConstants {

    public static final String DEFAULT_BOOTSTRAP =
            "localhost:19092,localhost:29092,localhost:39092,localhost:49092,localhost:59092";

    public static final String VERSION_LINE = "kafka-loss-lab 1.0.0";

    private CliConstants() {
    }
}
