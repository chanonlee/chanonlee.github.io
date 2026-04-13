package com.example.kafkalosslab.cli;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 命令行参数解析：仅支持 {@code --name value} 成对形式（与原先 picocli 风格一致）。
 */
public final class CliOptions {

    private CliOptions() {
    }

    /**
     * 将 {@code args} 解析为有序 map；每个以 {@code --} 开头的选项必须紧跟一个非选项值。
     */
    public static Map<String, String> parse(String[] args) {
        Map<String, String> m = new LinkedHashMap<>();
        for (int i = 0; i < args.length; ) {
            String a = args[i];
            if (!a.startsWith("--")) {
                throw new IllegalArgumentException("Expected option starting with --, got: " + a);
            }
            if (i + 1 >= args.length || args[i + 1].startsWith("--")) {
                throw new IllegalArgumentException("Option " + a + " requires a value");
            }
            m.put(a, args[i + 1]);
            i += 2;
        }
        return m;
    }

    public static String req(Map<String, String> o, String name) {
        String v = o.get(name);
        if (v == null) {
            throw new IllegalArgumentException("Missing required option: " + name);
        }
        return v;
    }

    public static Integer optInt(Map<String, String> o, String name) {
        String v = o.get(name);
        if (v == null) {
            return null;
        }
        return Integer.parseInt(v);
    }
}
