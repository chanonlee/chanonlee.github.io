---
title: 我如何从混乱里，硬拽出JavaScript的一条学习主线
date: 2026-04-12 10:00:00
permalink: 2026/04/12/20260412-我如何从混乱里，硬拽出JavaScript的一条学习主线/
banner_img: /img/44d47d503b09e7879b9788cdcc98082.jpg
tags:
  - JavaScript
  - 学习笔记
  - 前端
categories: 语言特性
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注：🤖 AI辅助**

</div>

学大模型其实有一个比较通用的思路：先找一本概述性的书入门，暂时忽略 token、tool、MCP、skill、harness 这些看起来“高级”的概念，先把整体结构搭建起来，再逐步把这些术语映射回框架中，这样会清晰很多。

最近在工作中接触到很多前端相关概念，也遇到了类似的问题：术语不断出现，但我对 JavaScript 基本是零基础，导致理解变得碎片化。

所以我决定借鉴这种学习方法，通过一本书先对 JS 建立整体认知框架，理解框架层级，再将各个新鲜词汇标记进这个框架不同层级，理解并列和包含关系，最后在每个部分尝试1-2个非常干净的试手小练习。

```text
- 先建立整体框架（书籍）
    JS 被拆成：语法 / 特性 / 机制 / 工具环境

- 不断接收新术语
    token / tool / MCP / async / closure / event loop …

- 把术语“挂到框架上”
    → 判断属于哪个层级
    → 判断是并列关系还是包含关系

- 每个模块配 1~2 个干净小练习
    → 只验证一个点，不混合复杂逻辑
    → 用来稳定认知锚点
```
# 1. 初始目标：对JS有整体印象

在这个阶段，我们首先要明确目标：不是“学会 JS 的所有细节”，而是先对 JS 形成一个整体印象。

此时我对 JS 的认知仍然非常有限，只知道它是一种前端语言。因此第一步是通过阅读书籍，从目录结构入手，先建立整体的认知框架。

我选择的书是《JavaScript 高级程序设计》。这本书在微信读书上的评分不错。打开目录后可以看到，它与大多数编程语言教材类似：前半部分是基础语法的讲解，中间是进阶特性，后面则是总结与实践项目。

至此，我们已经明确了主线：通过书籍先搭建对 JS 的整体印象，其内容大致可以包含语法基础、项目实操、高级特性，以及工具与运行环境的理解。

在这个框架之下，我们先从基础语法部分开始切入。

# 2. 调整目标：通过书籍搭建JS框架
## 2.1 任务一. 从基础语法入门

在书本里简单看了基础语法，对循环语句、关键词、参数命名、作用域有大概印象。阅读时专注度不高，不求甚解，只是有个大概印象。

## 2.2 任务二. 用真实项目驱动理解

在这一阶段，我首先从 GitHub 上找到了 React core 的源码仓库，一开始误以为这是一个可以直接部署的前端项目。注意到关键字 **React** 后，我意识到它更像是一个“包”或“库”。

此时如果选择直接从源码倒推 React 的设计与实现，学习成本会非常高，远大于先系统阅读官方文档。因此我暂时搁置源码阅读，转而开启一个新的支线任务：**先理解什么是 React**。

### 2.2.1 第一次尝试：从 React 入手

官方文档：[https://react.dev/learn/tutorial-tic-tac-toe](https://react.dev/learn/tutorial-tic-tac-toe)

React 官方文档的 Quick Start 部分提供了一个“井字棋”示例教程，从简单到复杂逐步实现一个独立的 React 小工程，整体设计非常清晰，很适合作为入门实践。

过程我就不展开细说了，强烈建议直接跟着代码从零实现一遍，亲自体会项目是如何一步步演进和变复杂的。

Quick Start 的另一部分是《用 React 思考》，核心思路是：将页面拆分为组件，通过函数、组件以及状态（state）的组织方式来思考如何构建应用。

在这个阶段，一个关键问题浮现出来：**React 和 JavaScript 到底是什么关系？**

为了建立直观理解，我让 AI 帮忙整理了一个与 Java 的对比图（一次性生成，主要用于建立整体印象，不必过度纠结精确性）：

AI生成

| 层级   | JS/Node   | Java       | 说明   |
| ---- | --------- | ---------- | ---- |
| 业务代码 | Next.js业务 | Spring业务   | 实际开发 |
| 应用框架 | Next.js框架 | SpringBoot | 开箱能力 |
| 核心库  | React核心库  | Spring核心   | 基础能力 |
| 生态扩展 | React生态   | Spring生态   | 周边能力 |
| 工具库  | 通用工具库     | Java工具库    | 辅助工具 |
| 运行时  | Node.js   | JVM        | 执行环境 |
| 语言   | JS/TS     | Java等      | 编程语言 |
| 操作系统 | OS系统      | OS系统       | 底层支撑 |

支线完成，任务回收，进行下一步。

此时我们已经知道这个项目是一个根仓库，不适合作为玩具练手，于是切换项目。

### 2.2.2 第二次尝试：阅读 hexo 源码

#### Step 1 建立阅读地图

切换回本博客项目，将Hexo作为待阅读源码，进行查看。

让AI写个服务启动文档，帮助我们快速理解代码阅读层级。

| 顺序  | 内容                                          | 说明                       |
| --- | ------------------------------------------- | ------------------------ |
| 1   | 仓库根目录 `[README.md](../README.md)`           | 面向使用者的功能概览与安装方式          |
| 2   | `[lib/hexo/index.ts](../lib/hexo/index.ts)` | `Hexo` 类入口，串联加载配置、插件、主题等 |
| 3   | `[lib/plugins/](../lib/plugins/)`           | 内置控制台命令、生成器、渲染器、过滤器等     |
| 4   | [官方 API 文档](https://hexo.io/api/)           | 与插件、主题开发相关的对外接口说明        |
| 5   | [贡献指南](../.github/CONTRIBUTING.md)          | 提 PR 前的风格、测试要求           |

在此基础上，开始对代码主体进行阅读，第一步从 `index.ts` 入手。

#### Step 2 拆分主函数

整个阅读过程遵循一个原则：**自上而下、大块拆分、再逐层拆解细节**。通过这种方式，可以快速建立树状结构，而不是陷入局部实现细节。在拆分完后，可以跟AI进行一些简单问答，让AI协助验证我们的拆分是否正确。

在 `index.ts` 中，初步可以划分为以下结构：

- 模块导入
- `const` 常量与工具函数
- `interface` 类型定义（Args / Query / Extend / Env 等）
- `declare module` 扩展声明
- `Hexo` 接口定义
- `Hexo` 类实现及初始化逻辑

#### Step 3 记录新语法

在这个过程中，一些更高层级的语法逐渐浮现出来，例如：

- JavaScript / TypeScript 中 `interface` 与 `class` 的关系
- `const` 在模块作用域中的实际行为
- `declare` 语法的用途与边界

这些问题正好补齐了前面“略读书本时跳过的空白部分”。在这个阶段，可以通过关键字向 AI 提问，在对话中不断把新出现的概念（如 `interface`、`class`、代码块外的 `const`、`declare` 等）标记到已经建立的 JavaScript 分层结构中。

这个过程不追求一开始就完全正确，而是先完成“粗粒度映射”，优先把它们放进合适的位置，后续再逐步修正和细化理解。

#### Step 4 筛选并学习特定语法

继续在这些问题中整理术语时可以发现，像 `declare`、`const` 作用域、`module` 等概念距离当前知识体系较远，而 `interface` 和 `class` 相对更接近已有认知。

因此可以优先选择这些“可切入点”作为入口，从更容易理解的概念开始建立连接，再逐步扩展到更抽象的部分。

具体做法是：先在书籍中定位对应知识点，再让 AI 在 `.test` 文件夹下生成使用相同语法的最小测试代码，用于快速验证和理解语法行为。

这里的关键在于“测试代码的纯净性”——不要引入项目相关逻辑，也不要依赖任何未知或复杂的第三方库，只保留最基础的语法结构。

这些约束可以直接交给 AI 生成，效率往往比手动编写更高，也更容易保证实验环境的可控性。

##### 小延伸：JS 中的 class 是什么？跟Java有相似性吗？

在阅读 `index.ts` 的过程中注意到使用了 `class`，于是回到书本中查阅类定义相关章节。

阅读后可以理解为：JavaScript 同样具备“对象”的概念，并可以通过构造函数创建对象实例。在此基础上引入了 `class` 语法作为更结构化的封装方式。

其中有一个在 Java 设计模式中常见、但在 Java 语法层面不太显性的概念：`prototype`。可以将其理解为一种“原型链机制”——实例对象会通过原型链继承共享属性与方法，而不是简单的属性拷贝。

类本身也包含常见的结构能力，例如：

- 公有成员与私有成员
- 静态成员与静态初始化逻辑
- 构造函数（constructor）

整体上，这些概念与 Java 的类模型有一定相似性，属于可以快速建立映射关系的部分。

在这个阶段不需要过度纠结语言细节，尤其是类似生成器函数这类语法糖，可以暂时跳过，不必强行记忆。

此外，JavaScript 的类机制同样支持单继承，也存在类似“抽象能力”的表达方式（通常通过约定或基类实现，而非严格语法层面的抽象类）。

实验代码：
```javascript
const assert = require('node:assert/strict');

/** 迷你版「类骨架」
 * 在本目录执行：npm start
 */
class Counter {
  public label: string;
  public value: number;
  static version = '1.0.0';
  private tickListeners: Array<(n: number) => void> = [];

  constructor(label: string, start = 0) {
    this.label = label;
    this.value = start;
  }

  on(event: 'tick', fn: (n: number) => void): void {
    if (event === 'tick') this.tickListeners.push(fn);
  }

  bump(): number {
    this.value += 1;
    const v = this.value;
    for (const fn of this.tickListeners) fn(v);
    return v;
  }
}

// —— 类 vs 实例 ——
assert.strictEqual(Counter.version, '1.0.0');
const a = new Counter('A', 10);
const b = new Counter('B', 0);

assert.notStrictEqual(a, b);
assert.strictEqual(a.label, 'A');
assert.strictEqual(b.label, 'B');
assert.strictEqual(a.value, 10);
assert.strictEqual(b.value, 0);

a.bump();
assert.strictEqual(a.value, 11);
assert.strictEqual(b.value, 0);

assert.strictEqual('version' in a, false);

// —— 实例监听 ——
{
  const hits: number[] = [];
  const c = new Counter('x', 0);
  c.on('tick', n => hits.push(n));
  c.bump();
  c.bump();
  assert.deepStrictEqual(hits, [1, 2]);
}

console.log('class_vs_instance: 断言全部通过');

```
##### 小延伸：interface中的重载看起来是种很特殊的用法
同名的interface会重载class中的方法，但这个方法是约束给写代码的人和静态编译期的机器看的，更多事解释性说明，跟Java里的约束性用法不同。

```javascript
const assert = require('node:assert/strict');

/** 迷你事件总线：interface + class 合并；用 Map 存监听器 */
interface TinyBus {
  on(event: 'ready', listener: () => void): this;
  on(event: 'ping', listener: (message: string) => void): this;
  on(event: string, listener: (...args: any[]) => any): any;
  emit(event: string, ...args: any[]): boolean;
}

class TinyBus {
  private readonly listeners = new Map<string, Array<(...args: any[]) => any>>();

  on(event: string, listener: (...args: any[]) => any): this {
    const list = this.listeners.get(event) ?? [];
    list.push(listener);
    this.listeners.set(event, list);
    return this;
  }

  emit(event: string, ...args: any[]): boolean {
    const list = this.listeners.get(event);
    if (!list?.length) return false;
    for (const fn of list) fn(...args);
    return true;
  }
}

// —— ready ——
{ const bus = new TinyBus(); let called = false;
  bus.on('ready', () => { called = true; });
  bus.emit('ready');
  assert.strictEqual(called, true);
}

// —— ping ——
{ const bus = new TinyBus(); const received: string[] = [];
  bus.on('ping', msg => received.push(msg));
  bus.emit('ping', 'hello');
  assert.deepStrictEqual(received, ['hello']);
}

// —— 多 listener 顺序 ——
{ const bus = new TinyBus(); const order: number[] = [];
  bus.on('ping', () => order.push(1));
  bus.on('ping', () => order.push(2));
  bus.emit('ping', 'x');
  assert.deepStrictEqual(order, [1, 2]);
}

// —— 未注册事件 ——
{ const bus = new TinyBus();
  assert.strictEqual(bus.emit('nope'), false);
}

console.log('typed_events_minimal: 断言全部通过');
```

## 2.3 必备能力补全：网络请求

在完成前面的试手练习后，回到主线，继续翻阅书本——这也是以书为主线学习的意义所在：为整体认知提供稳定的框架支撑。

这一次翻到了“网络请求”相关章节，可以尝试系统阅读这一部分。不过在快速浏览目录后发现，这一章的内容相对独立，各个模块之间耦合不高。

因此没有选择线性通读，而是基于实际工作经验，优先挑选几个已经接触过、但理解还不够清晰的知识点进行切入学习。

### 2.3.1 Fetch

从本质上看，`fetch()` 提供的是一个统一的网络请求入口，使得前端可以以更标准化的方式与服务器进行通信，并参与到浏览器的请求生命周期管理中。

fetch的代码片段
```javascript
async function runFetch(label, url, init) {
  try {
    const res = await fetch(url, init);
    const ct = res.headers.get('content-type') || '';
    let body;
    if (ct.includes('application/json')) body = await res.json();
    else body = await res.text();
    show({
      label,
      url: res.url,
      status: res.status,
      redirected: res.redirected,
      'x-via-sw': res.headers.get('x-via-sw'),
      body,
    });
  } catch (e) {
    show(`${label} 出错：${e?.message ?? e}`);
  }
}
```

### 2.3.2 跨域资源共享

这一部分本质上与 JavaScript 本身关系不大，更偏向浏览器与服务器之间的通信约定。

跨源资源共享（CORS，Cross-Origin Resource Sharing）定义了浏览器在跨源请求时，如何与服务器进行协商与约束。其核心思想是：通过一组自定义的 HTTP 头部，让浏览器与服务器明确“这个请求是否被允许”。

对于简单请求（例如 GET、POST，且不包含自定义头部、请求体为 `text/plain` 等情况），浏览器会自动在请求中携带一个 `Origin` 头部。该字段表示当前页面的来源信息，包括协议、域名和端口，用于让服务器判断请求是否来自被允许的源。

如果服务器允许该请求，就会在响应中返回 `Access-Control-Allow-Origin` 头部，其值通常为：

- 与 `Origin` 完全一致的源（表示仅允许该来源访问）
- 或 `"*"`（表示允许所有来源访问的公开资源）

如果响应中没有该头部，或者该值与请求的 `Origin` 不匹配，浏览器将认为该跨域请求不被允许，并阻止页面访问响应内容。

### 2.3.3 WebSocket接口

要创建一个 WebSocket 连接，本质上是实例化一个 `WebSocket` 对象，并传入用于建立连接的 URL。在连接建立之后，可以通过监听 WebSocket 的不同状态来处理通信过程中的各个阶段，例如连接建立、消息接收与连接关闭等。

整体来看，这部分内容相对直接，本质是一个基于事件驱动的双向通信接口，理解上没有太大的难度，重点在于理解其“持续连接 + 实时通信”的模型，而不是具体 API 细节。

server代码：
```javascript
/**
 * WebSocket 服务端（`ws` 包）。先在本终端运行：`npm run server`
 *
 * 端口：`WS_PORT` 环境变量，默认 18765。
 */
const { WebSocketServer } = require('ws');

const port = Number(process.env.WS_PORT || 18765);

function rawDataToString(data) {
  if (typeof data === 'string') return data;
  if (Buffer.isBuffer(data)) return data.toString();
  if (data instanceof ArrayBuffer) return Buffer.from(data).toString();
  return Buffer.concat(data).toString();
}

const wss = new WebSocketServer({ host: '127.0.0.1', port });

wss.on('listening', () => {
  console.log(`[server] 监听 ws://127.0.0.1:${port}（Ctrl+C 结束）`);
});

wss.on('connection', (serverSocket) => {
  console.log('[server] 客户端已连上');
  serverSocket.on('message', (data) => {
    serverSocket.send(`echo: ${rawDataToString(data)}`);
  });
  serverSocket.on('close', () => {
    console.log('[server] 该连接已关闭');
  });
});
```

client代码：
```javascript
/**
 * WebSocket 客户端（Node 22+ 全局 `WebSocket`）。需先另开终端运行服务端：`npm run server`
 *
 * 端口：与 `server.ts` 相同，使用 `WS_PORT`，默认 18765。
 *
 * readyState：CONNECTING(0) / OPEN(1) / CLOSING(2) / CLOSED(3)
 */
function stateLabel(readyState) {
  switch (readyState) {
    case WebSocket.CONNECTING:
      return 'CONNECTING(0) 连接正在建立';
    case WebSocket.OPEN:
      return 'OPEN(1) 连接已建立';
    case WebSocket.CLOSING:
      return 'CLOSING(2) 连接正在关闭';
    case WebSocket.CLOSED:
      return 'CLOSED(3) 连接已关闭';
    default:
      return `未知(${readyState})`;
  }
}

function logClientState(tag, socket) {
  console.log(`[client][${tag}] readyState → ${stateLabel(socket.readyState)}`);
}

const port = Number(process.env.WS_PORT || 18765);
const url = `ws://127.0.0.1:${port}`;

const socket = new WebSocket(url);
logClientState('new WebSocket(url) 之后', socket);
queueMicrotask(() => logClientState('同一事件循环 microtask', socket));

socket.addEventListener('open', () => {
  logClientState('open 回调', socket);
  socket.send('ping');
});

socket.addEventListener('message', (ev) => {
  const raw = ev.data;
  const text = typeof raw === 'string' ? raw : Buffer.from(raw).toString();
  console.log(`[client] 收到消息: ${text}`);
  logClientState('收到消息后', socket);
  socket.close(1000, '示例结束');
});

socket.addEventListener('close', (ev) => {
  logClientState('close 回调', socket);
  console.log(`[client] close code=${ev.code} reason=${ev.reason} wasClean=${ev.wasClean}`);
  process.exit(0);
});

socket.addEventListener('error', (ev) => {
  console.error('[client] error', ev);
  process.exit(1);
});
```
# 3. 总结 

如果用几句话总结这个学习方法，我会概括为三点：

1. 框架优先
2. AI 不参与主线决策
3. 认知降噪

---

在整个学习过程中，我的核心目标始终是**先建立框架体系，再逐步填充细节**。这样可以让学习始终保持结构感与方向性，而不是陷入碎片化的知识堆叠。

在当前的学习过程中，我确实高度依赖与 AI 的交互，但有一个非常重要的原则：**不能把主线思考外包给 AI**。学习路径必须由自己主导，AI 仅作为辅助工具，用于加速局部任务，例如资料查询、示例生成或理解验证，而不能替代整体思考过程。

同时，对于 AI 生成的代码，也不应一味追求“高级写法”或“最优解”，而应优先匹配当前的理解阶段。如果代码中出现过于复杂的语法结构，可以主动要求 AI 进行降级改写，使其转化为更容易理解的表达方式，从而避免被不断出现的新概念和抽象层级不断抬高认知负担。

对于暂时无法理解的新语法或概念，则可以将其拆分为独立的学习任务，在合适的阶段再逐步消化，而不是在主线学习中一次性解决所有问题。
