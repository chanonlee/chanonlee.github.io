---
title: 阅读地图
date: 2026-03-29 12:00:00
layout: page
comments: false
banner_img: /img/44d47d503b09e7879b9788cdcc98082.jpg
---

<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注：🧠 全AI生成 **

</div>

## 语言与运行时（Java / Go / JavaScript）

与语法、标准库、虚拟机行为或「如何学一门语言」相关的笔记。

- [Java中的软引用和它的测试](/2023/09/07/20230907-Java中的软引用和它的测试/)
- [关于equals和hashcode方法](/2024/02/05/%E5%85%B3%E4%BA%8Eequals%E5%92%8Chashcode%E6%96%B9%E6%B3%95/)
- [几个多线程类对AQS的state的变更](/2023/11/28/20231128-%E5%87%A0%E4%B8%AA%E5%A4%9A%E7%BA%BF%E7%A8%8B%E7%B1%BB%E5%AF%B9AQS%E7%9A%84state%E7%9A%84%E5%8F%98%E6%9B%B4/)
- [Collection类源码阅读](/2024/08/10/20240810-Collection%E7%B1%BB%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB/)
- [go的net包中的套接字编程](/2023/12/19/20231219-go%E7%9A%84net%E5%8C%85%E4%B8%AD%E7%9A%84%E5%A5%97%E6%8E%A5%E5%AD%97%E7%BC%96%E7%A8%8B/)
- [我如何从混乱里，硬拽出JavaScript的一条学习主线](/2026/04/12/20260412-%E6%88%91%E5%A6%82%E4%BD%95%E4%BB%8E%E6%B7%B7%E4%B9%B1%E9%87%8C%EF%BC%8C%E7%A1%AC%E6%8B%BD%E5%87%BAJavaScript%E7%9A%84%E4%B8%80%E6%9D%A1%E5%AD%A6%E4%B9%A0%E4%B8%BB%E7%BA%BF/)

## 数据库与中间件

持久化选型、索引与实践，以及 ZK、Kafka 等组件上的手写封装。

- [一些PostgreSQL跟MySQL的细微差别](/2023/10/11/20231011-%E4%B8%80%E4%BA%9BPostgreSQL%E8%B7%9FMySQL%E7%9A%84%E7%BB%86%E5%BE%AE%E5%B7%AE%E5%88%AB/)
- [MongoDB的Index](/2024/08/10/20240810-MongoDB%E7%9A%84Index/)
- [在Springboot项目中使用MongoDB的QuickStart](/2024/08/11/20240811-%E5%9C%A8Springboot%E9%A1%B9%E7%9B%AE%E4%B8%AD%E4%BD%BF%E7%94%A8MongoDB%E7%9A%84QuickStart/)
- [反射+泛型 写一个Zookeeper工具类](/2023/09/01/20230902-%E5%8F%8D%E5%B0%84+%E6%B3%9B%E5%9E%8B-%E5%86%99%E4%B8%80%E4%B8%AAZookeeper%E5%B7%A5%E5%85%B7%E7%B1%BB/)
- [写一个用zk监听变化的 Kafka Consumer](/2023/09/02/20230903-%E5%86%99%E4%B8%80%E4%B8%AA%E7%94%A8zk%E7%9B%91%E5%90%AC%E5%8F%98%E5%8C%96%E7%9A%84kafkaconsumer/)

## 工程实践与设计

设计模式、扩展机制、领域建模、重构权衡，以及工具链或环境差异带来的排障记录（含基于 Java `function` 包的小工具）。

- [使用 java function 包写一个 RetryUtils](/2024/06/23/20240623-%E4%BD%BF%E7%94%A8java-function%E5%8C%85%E5%86%99%E4%B8%80%E4%B8%AARetryUtils/)
- [策略模式学习笔记](/2024/01/03/20240103-%E7%AD%96%E7%95%A5%E6%A8%A1%E5%BC%8F%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)
- [实现拓展的方式：SPI 拦截调用](/2023/10/16/20231016-%E5%AE%9E%E7%8E%B0%E6%8B%93%E5%B1%95%E7%9A%84%E6%96%B9%E5%BC%8F%EF%BC%9ASPI-%E6%8B%A6%E6%88%AA%E8%B0%83%E7%94%A8/)
- [行政区划下的商店关系：工程实践中的树结构使用](/2025/01/04/20250104-%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E4%B8%8B%E7%9A%84%E5%95%86%E5%BA%97%E5%85%B3%E7%B3%BB%E2%80%94%E2%80%94%E5%B7%A5%E7%A8%8B%E5%AE%9E%E8%B7%B5%E4%B8%AD%E7%9A%84%E6%A0%91%E7%BB%93%E6%9E%84%E4%BD%BF%E7%94%A8-copy/)
- [代码重构中的 Trade Off](/2025/12/02/20251202-%E4%BB%A3%E7%A0%81%E9%87%8D%E6%9E%84%E4%B8%AD%E7%9A%84Trade-Off/)
- [我如何理解交易系统：从状态机到资金流转](/2026/03/29/20260329-%E6%88%91%E5%A6%82%E4%BD%95%E7%90%86%E8%A7%A3%E4%BA%A4%E6%98%93%E7%B3%BB%E7%BB%9F%EF%BC%9A%E4%BB%8E%E7%8A%B6%E6%80%81%E6%9C%BA%E5%88%B0%E8%B5%84%E9%87%91%E6%B5%81%E8%BD%AC/)
- [一个只在测试环境出现的诡异反射报错：我最后查到了 JaCoCo](/2026/04/04/20260404-%E4%B8%80%E4%B8%AA%E5%8F%AA%E5%9C%A8%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%87%BA%E7%8E%B0%E7%9A%84%E8%AF%A1%E5%BC%82%E5%8F%8D%E5%B0%84%E6%8A%A5%E9%94%99JaCoCo/)
- [AI 写得对，但写得不对：关于代码分层、抽象与设计](/2026/04/13/20260413-AI%E5%86%99%E5%BE%97%E5%AF%B9%E4%BD%86%E5%86%99%E5%BE%97%E4%B8%8D%E5%AF%B9%E5%85%B3%E4%BA%8E%E4%BB%A3%E7%A0%81%E5%88%86%E5%B1%82%E6%8A%BD%E8%B1%A1%E4%B8%8E%E8%AE%BE%E8%AE%A1/)

## 脚本与工具链

偏运维或小工具向的一次性记录。

- [处理音频流](/2025/11/19/20251119-%E5%A4%84%E7%90%86%E9%9F%B3%E9%A2%91%E6%B5%81/)

## 阅读与延伸

书本摘要与主题阅读，和上面的工程笔记互为补充。

- [Bitcoin ——《精通区块链编程》读书笔记](/2023/12/25/20231225-Bitcoin%E2%80%94%E2%80%94%E3%80%8A%E7%B2%BE%E9%80%9A%E5%8C%BA%E5%9D%97%E9%93%BE%E7%BC%96%E7%A8%8B%E3%80%8B%E8%AF%BB%E4%B9%A6%E7%AC%94%E8%AE%B0/)
- [分布式服务架构注意点——《可伸缩服务架构：框架与中间件》读书笔记](/2023/12/29/20231229-%E5%88%86%E5%B8%83%E5%BC%8F%E6%9C%8D%E5%8A%A1%E6%9E%B6%E6%9E%84%E6%B3%A8%E6%84%8F%E7%82%B9%E2%80%94%E2%80%94%E3%80%8A%E5%8F%AF%E4%BC%B8%E7%BC%A9%E6%9C%8D%E5%8A%A1%E6%9E%B6%E6%9E%84%EF%BC%9A%E6%A1%86%E6%9E%B6%E4%B8%8E%E4%B8%AD%E9%97%B4%E4%BB%B6%E3%80%8B%E8%AF%BB%E4%B9%A6%E7%AC%94%E8%AE%B0/)
