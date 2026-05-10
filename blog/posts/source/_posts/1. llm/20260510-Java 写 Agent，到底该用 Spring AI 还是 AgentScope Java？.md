---
title: Java 写 Agent，到底该用 Spring AI 还是 AgentScope Java？
date: 2026-05-10 17:58:02
permalink: 2026/05/10/20260510-Java 写 Agent，到底该用 Spring AI 还是 AgentScope Java？/
banner_img: /img/44d47d503b09e7879b9788cdcc98082.jpg
tags:
  - Java
  - Agent
  - Spring AI
  - AgentScope
  - LLM
  - ReAct
categories: 工程实践
---

<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🤖 AI辅助**

</div>

最近在看 Java 生态里的 Agent 开发框架时，很容易遇到两个名字：AgentScope 和 Spring AI。

它们看起来都能用来开发 AI 应用，也都能组织模型调用、工具调用和对话流程。但如果只看示例代码，很容易产生一个疑问：这些框架到底是在解决什么问题？它们和我们通常说的 Agent 又是什么关系？

为了把这个问题讲清楚，本文不会一开始就进入 Java 代码，而是先用 Python 写一个最小可运行的 ReAct Agent 示例。

需要提前说明的是，本文是我在 AI 辅助下用大约两小时整理出来的一篇快餐文档，分析并不十分深入，只是从一个简单例子出发，帮助自己建立一个初步判断：Agent 到底由什么组成？框架到底帮我们封装了哪一层？Spring AI 和 Spring IoC 的关系又该如何理解？

## 什么是Agent？

在展开 AgentScope 和 Spring AI 之前，我们先回答一个更基础的问题：什么是 Agent？ 在构建 Agent 之前，我们通常已经有了几个基础能力：大模型 LLM、工具 Tool、多轮对话能力，以及用于约束 Agent 行为的 System Prompt。把这些能力按照一定的流程组织起来，让模型能够根据用户输入进行思考、决定是否调用工具、观察工具结果，并继续生成回答，这就是一个 Agent。

Agent有多种运行模型。一个ReAct Agent如下所示：

![](https://alidocs.dingtalk.com/core/api/resources/img/5eecdaf48460cde5ed723967596277bfb0c0126238375fa675b8339e1c4c2483da591b68f3619f358d68742cd653602a0524375348f90ffd59702ca8bff5038bc9ab79c36a4fba27b995f2e1733de867f1855e57fa2ccc63b5d202580a5c454f?tmpCode=c31c306a-c988-45aa-bf2b-40e993e25b9c)

## Agent的Python实现

Python写Agent有天然优势，功能简洁，封装干净，即使不运行也能清晰地看出Agent结构。所以这里先用Python作为第一个例子。

在[之前的文章](https://alidocs.dingtalk.com/i/nodes/EpGBa2Lm8azvXdRliEmqwEAeWgN7R35y?utm_scene=team_space&sideCollapsed=true&iframeQuery=utm_source%253Dportal%2526utm_medium%253Dportal_new_tab_open&corpId=ding5f17ba8e3c59f1b435c2f4657eb6378f)里，我已经实现过一个简单的 ReAct Agent，这里继续沿用这个例子：

```python
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# ===================== Agent的状态机 =====================

# 状态：对话历史（也是“记忆”）
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ===================== Tool定义 =====================

# 工具（Act）
@tool
def get_weather(city: str) -> str:
    """根据城市名返回天气信息。"""
    return {
        "beijing": "晴，24℃",
        "shanghai": "多云，26℃",
        "hangzhou": "小雨，22℃",
    }.get(city.lower(), "暂无数据")

# ===================== System Prompt =====================
SYSTEM_PROMPT = "你是一个天气助手。优先调用工具获取天气后再作答，回答简洁。"


# ======================= 图节点（Think / Decide） =======================

tools = [get_weather]

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature= 0,
).bind_tools(tools)

def think(state: State):
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    msg = llm.invoke(messages)
    return {"messages": [msg]}

def should_act(state: State):
    last = state["messages"][-1]
    return "act" if getattr(last, "tool_calls", None) else END


# ============================= LangGraph构建Agent =============================

# 定义一个带环的执行图：Think → Act → Think → ... 直到结束

builder = StateGraph(State)

builder.add_node("think", think)
builder.add_node("act", ToolNode(tools))

builder.add_edge(START, "think")
# Think → Act / END
builder.add_conditional_edges(
    "think",
    should_act,
    {
        "act": "act",
        END: END,
    },
)
# Act → Think（Observe 后进入下一轮）
builder.add_edge("act", "think")


# ============================= 代码运行 =============================

app = builder.compile()

# 用户提问（User Prompt）
result = app.invoke(
    {"messages": [HumanMessage(content="杭州今天天气怎么样？")]}
)
result["messages"][-1].content
```

对照文章开头的题图可以看到，一个 Agent 通常由几个核心要素组成：LLM、System Prompt、Tool，以及一套明确的运行状态机。而所谓ReAct，就是特定的一个运行状态机。把这些部分组织起来之后，我们就可以像调用一个普通程序一样，向这个 Agent 发起对话，并让它按照预设流程完成思考、工具调用和最终回答。

LangChain定义了工具、模型调用、prompt，而Langgraph搞定了运行状态机。

带着这个了解，我们走进接下来的部分。

## 将Python迁移到Java——AgentScope

上面我们已经通过 Python 理解了一个 Agent 的基本结构。接下来，可以把这个结构迁移到 Java 中。

在定义一个 Agent 时，我们通常需要完成几类工作：封装 Tool、配置模型调用、维护对话状态，并定义模型与工具之间的循环流程。如果从零开始实现，这些逻辑都需要自己手写。而 AgentScope 正是对这些通用能力做了一层封装，让我们可以直接使用已有的 Agent 抽象来组织模型、工具和执行流程。

以下是一个使用AgentScope的示例：

```java
import io.agentscope.core.ReActAgent;
import io.agentscope.core.message.Msg;
import io.agentscope.core.model.DashScopeChatModel;
import io.agentscope.core.tool.Toolkit;
import io.agentscope.core.tool.Tool;
import io.agentscope.core.tool.ToolParam;

public class WeatherAgentDemo {

    // ===================== System Prompt =====================

    private static final String SYSTEM_PROMPT =
            "你是一个天气助手。优先调用工具获取天气后再作答，回答简洁。";

    public static void main(String[] args) {

        // ===================== Tool 注册 =====================
        //
        // 对应 Python 里的：
        //
        // tools = [get_weather]
        // ToolNode(tools)

        Toolkit toolkit = new Toolkit();
        toolkit.registerTool(new WeatherTools());

        // ===================== LLM + Agent 构建 =====================
        //
        // 对应 Python 里的：
        //
        // llm = ChatOpenAI(
        //     model="gpt-4.1-mini",
        //     temperature=0,
        // ).bind_tools(tools)
        //
        // 在 AgentScope Java 中：
        // - DashScopeChatModel 对应模型调用层
        // - Toolkit 对应工具集合
        // - ReActAgent 负责 Think -> Act -> Observe -> Think 循环

        ReActAgent weatherAgent = ReActAgent.builder()
                .name("weather-agent")
                .sysPrompt(SYSTEM_PROMPT)
                .model(DashScopeChatModel.builder()
                        .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                        .modelName("qwen-plus")
                        .build())
                .toolkit(toolkit)
                .maxIters(10)
                .build();

        // ===================== 代码运行 =====================
        //
        // 对应 Python 里的：
        //
        // result = app.invoke({
        //     "messages": [HumanMessage(content="杭州今天天气怎么样？")]
        // })
        // result["messages"][-1].content

        Msg userMsg = Msg.builder()
                .textContent("杭州今天天气怎么样？")
                .build();

        Msg response = weatherAgent.call(userMsg).block();

        System.out.println(response.getTextContent());
    }

    // ===================== Tool 定义 =====================
    //
    // 对应 Python 里的：
    //
    // @tool
    // def get_weather(city: str) -> str:
    //     ...

    public static class WeatherTools {

        @Tool(name = "get_weather", description = "根据城市名返回天气信息。")
        public String getWeather(
                @ToolParam(name = "city", description = "城市名，例如 beijing、shanghai、hangzhou")
                String city
        ) {
            if (city == null) {
                return "暂无数据";
            }

            return switch (city.toLowerCase()) {
                case "beijing", "北京" -> "晴，24℃";
                case "shanghai", "上海" -> "多云，26℃";
                case "hangzhou", "杭州" -> "小雨，22℃";
                default -> "暂无数据";
            };
        }
    }
}
```

AgentScope 本质上是一个用于组织和管理 Agent 相关资源的框架。前面的示例中，我们定义的就是一个具体的 Agent。

和 LangGraph 不同，这里没有显式定义一张执行图。原因是在 AgentScope 中，这套流程已经被封装进了 `ReActAgent` 类里。也就是说，模型调用、工具调用以及 Think → Act → Observe → Think 的循环逻辑，都由 AgentScope 帮我们组织好了。

我们对照本文开头的图片来看，我们的代码主要定义了Tool、System Prompt、LLM，但没有定义运行状态机，这份状态机由AgentScope帮我们封装好了。

## 将Python迁移到Java——Spring AI

Spring AI 的能力和 AgentScope 有一定重合，它同样可以用自己的抽象来定义上面这个 Agent。

下面这个示例使用了 Spring AI 的相关包实现了完全一样的功能，但并没有引入 Spring IoC / Spring Boot 框架。也就是说，这里把 Spring AI 当作一个普通 Java SDK 来使用，就像 Jedis、Redisson 之于 Redis 一样：它们可以集成进 Spring 体系，也可以脱离 Spring 容器独立使用。

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class WeatherReActAgentDemo {

    // ===================== ReAct System Prompt =====================

    static final String SYSTEM_PROMPT = """
            你是一个天气助手，必须使用 ReAct 模式解决问题。

            你可以使用的工具：

            1. get_weather
               描述：根据城市名返回天气信息
               参数：city，城市名，例如 beijing、shanghai、hangzhou

            你必须严格按照下面格式输出：

            Thought: 你的思考
            Action: 工具名
            Action Input: 工具参数

            当你已经拿到足够信息后，必须输出：

            Thought: 我已经知道最终答案
            Final Answer: 给用户的简洁中文回答

            规则：
            - 如果问题涉及天气，优先调用 get_weather。
            - Action 只能是 get_weather。
            - Action Input 只输出城市英文名，例如 hangzhou。
            - 不要编造工具结果。
            - 最终回答要简洁。
            """;

    // ===================== Tool 定义 =====================

    static class WeatherTools {

        @Tool(
                name = "get_weather",
                description = "根据城市名返回天气信息。"
        )
        public String getWeather(
                @ToolParam(description = "城市名，例如 beijing、shanghai、hangzhou")
                String city
        ) {
            Map<String, String> weatherMap = Map.of(
                    "beijing", "晴，24℃",
                    "shanghai", "多云，26℃",
                    "hangzhou", "小雨，22℃"
            );

            return weatherMap.getOrDefault(city.toLowerCase(), "暂无数据");
        }
    }

    // ===================== ReAct Agent 主逻辑 =====================

    public static void main(String[] args) {

        String apiKey = System.getenv("OPENAI_API_KEY");

        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("请先设置环境变量 OPENAI_API_KEY");
        }

        OpenAiApi openAiApi = OpenAiApi.builder()
                .apiKey(apiKey)
                .build();

        OpenAiChatModel chatModel = OpenAiChatModel.builder()
                .openAiApi(openAiApi)
                .defaultOptions(OpenAiChatOptions.builder()
                        .model("gpt-4.1-mini")
                        .temperature(0.0)
                        .build())
                .build();

        ChatClient chatClient = ChatClient.builder(chatModel)
                .defaultSystem(SYSTEM_PROMPT)
                .build();

        WeatherTools weatherTools = new WeatherTools();

        String userQuestion = "杭州今天天气怎么样？";

        String answer = runReActAgent(chatClient, weatherTools, userQuestion);

        System.out.println(answer);
    }

    static String runReActAgent(
            ChatClient chatClient,
            WeatherTools weatherTools,
            String userQuestion
    ) {
        StringBuilder scratchpad = new StringBuilder();

        int maxSteps = 5;

        for (int step = 1; step <= maxSteps; step++) {

            String prompt = """
                    用户问题：
                    %s

                    已有推理过程：
                    %s

                    请继续执行下一步。
                    """.formatted(userQuestion, scratchpad);

            String modelOutput = chatClient.prompt()
                    .user(prompt)
                    .call()
                    .content();

            System.out.println("===== Step " + step + " Model Output =====");
            System.out.println(modelOutput);

            scratchpad.append(modelOutput).append("\n");

            if (modelOutput.contains("Final Answer:")) {
                return extractFinalAnswer(modelOutput);
            }

            ReActAction action = parseAction(modelOutput);

            if (action == null) {
                scratchpad.append("Observation: 模型没有按 ReAct 格式输出，请重新按格式输出。\n");
                continue;
            }

            String observation;

            if ("get_weather".equals(action.name())) {
                observation = weatherTools.getWeather(action.input());
            } else {
                observation = "未知工具：" + action.name();
            }

            scratchpad.append("Observation: ")
                    .append(observation)
                    .append("\n");
        }

        return "抱歉，我没有在限定步骤内得到最终答案。";
    }

    // ===================== ReAct 输出解析 =====================

    record ReActAction(String name, String input) {}

    static ReActAction parseAction(String text) {
        Pattern actionPattern = Pattern.compile("Action:\\s*(\\S+)");
        Pattern inputPattern = Pattern.compile("Action Input:\\s*(.+)");

        Matcher actionMatcher = actionPattern.matcher(text);
        Matcher inputMatcher = inputPattern.matcher(text);

        if (!actionMatcher.find() || !inputMatcher.find()) {
            return null;
        }

        String actionName = actionMatcher.group(1).trim();
        String actionInput = inputMatcher.group(1).trim();

        // 去掉可能出现的引号
        actionInput = actionInput
                .replace("\"", "")
                .replace("'", "")
                .trim();

        return new ReActAction(actionName, actionInput);
    }

    static String extractFinalAnswer(String text) {
        int index = text.indexOf("Final Answer:");
        if (index < 0) {
            return text;
        }

        return text.substring(index + "Final Answer:".length()).trim();
    }
}
```

我们继续对照本文开头的图片，我们的代码主要定义了Tool、System Prompt、LLM，但还需要手动写一个ReAct的状态机，Spring AI没有做这层封装，需要我们手动实现。

## Spring集成Agent

然后，我们可能会对 Spring AI 有一些错觉，总觉得它额外提供了某种“集成 Spring”的 Agent 能力。其实未必。  
如果我们的目标只是把 Agent 当作一个 Bean 托管给 IoC 容器，那么这个能力并不绑定 Spring AI。无论 Agent 是用 Spring AI 写的，还是用 AgentScope 写的，本质上都可以在关键类上加一个 `@Component` 注解，然后通过构造器注入依赖。  
Spring AI 在这里更像一个普通 Java SDK，只是它恰好可以很好地被 Spring 容器托管。

## 小结

仅就本文使用到的功能，可以把这几个框架简单对比如下：

| 框架 | 语言生态 | 更像什么 | ReAct 怎么做 |
| --- | --- | --- | --- |
| LangChain | Python | Agent 零部件库 | 提供模型、Prompt、工具等基础能力 |
| LangGraph | Python | Agent 编排层 | 显式搭图，组织状态机 |
| AgentScope Java | Java | 现成 Agent 运行时 | 直接使用 ReActAgent |
| Spring AI | Java | AI 应用基础设施 SDK | 自己写循环，或二次封装 |

回到文章开头的问题：AgentScope 和 Spring AI 到底是什么关系？它们和 Agent 又是什么关系？

通过这个最小示例可以看到，Agent 本身并不是某个框架独有的概念。对于 Java 生态里的几个框架，代码层面的理解其实并不难，可以粗略类比为 Redis 生态里的不同 SDK 或封装：它们都围绕同一类底层能力展开，只是抽象层级和使用方式不同。

粗略类比 Redis 生态，Spring AI 更像 Jedis，AgentScope 更像 Redisson。  
Spring AI 更贴近底层能力，主要提供模型调用、工具调用、Memory、RAG 等 AI 应用基础设施；AgentScope 则在这些能力之上封装了更高层的 Agent 运行时，例如 `ReActAgent` 和多 Agent 协作能力。

理解了这些概念之后，再去看 AgentScope 或 Spring AI，就会更容易判断：框架到底帮我们封装了哪一层，我们又应该在什么场景下使用它。
