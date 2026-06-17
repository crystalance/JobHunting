# Agent Harness 通用方法论：在 Agent Loop 外加协议层

> 整理日期：2026-04-21
> 背景：围绕 HDMAS_v4 在 WideSearch 上容易出现 `f1_by_item = 0`、简单任务也会草草交差的问题，讨论 Claude Code 是否用了某种机制来让 agent 更彻底地做事。结论是：**有，而且本质不是 task-specific hack，而是把一部分控制逻辑从模型内部“感觉”外提成系统级协议。**

---

## 0. 核心结论

这种机制的本质不是“给 agent 多加几句提醒词”，而是：

> **把 agent 的继续条件、完成条件、验证条件，从模型内部的隐式判断，外提为代码可执行的 protocol / state machine / hooks。**

也就是说，agent 不再是：

1. 看上下文
2. 采样一个 response
3. 调 tool
4. 再采样
5. 觉得“差不多了”就结束

而是变成：

1. 模型提出动作
2. 外部 harness 检查当前状态
3. 如果状态不满足协议，就注入 reminder / meta-message / gate
4. 只有协议满足时，才允许 agent 结束

**一句话概括**：

> Claude Code 的很多“更彻底”行为，不是模型自觉，而是 **loop 外面的控制层在约束它**。

---

## 1. 本质是什么

### 1.1 从 prompt engineering 变成 protocol engineering

单靠 prompt，本质上是在说：

- 希望你验证一下
- 希望你别太早停
- 希望你诚实一点

但模型可以忽略这些要求，因为 prompt 是**软约束**。

Harness 的做法是把其中一部分改成：

- 如果还没完成 todo，就**不准退出**
- 如果还没经过 verification，就**不准报完成**
- 如果 budget 还够，就**插一条 meta-message 提醒继续**
- 如果输出 schema 不完整，就**强制继续修**

这就从“希望它这么做”变成“系统要求它这么做”。

### 1.2 从 agent 内部 feeling 变成外部 state

没有 harness 时，`done` 往往等价于：

> “模型当前最可能输出 done。”

有 harness 时，`done` 变成：

> “外部状态机判断现在允许 done。”

这是最关键的变化。

---

## 2. 带来的本质好处

### 2.1 把“完成”变成可审计协议

agent 什么时候结束，不再是黑盒。你可以明确看到：

- 是否 todo 已完成
- 是否 verifier 已跑过
- 是否 schema 已满足
- 是否还有未验证字段
- 是否 budget 还足够继续

### 2.2 降低两种 LLM 常见失败模式

Claude Code 的设计明显是在压两类错误：

1. **Premature closure**：刚找到一个 plausible answer 就停
2. **Verification avoidance**：嘴上说验证了，实际上没验证

Harness 通过 gate / reminder / verifier，直接针对这两类偏差下手。

### 2.3 从“软提示”升级为“半硬约束”

| 机制 | 性质 |
|---|---|
| Prompt | 软约束 |
| Reminder / Meta-message | 半硬约束 |
| Exit gate / verifier gate / schema gate | 硬约束 |

Claude Code 的强点不在于 prompt 写得多漂亮，而在于它把关键节点做成了 protocol。

### 2.4 任务无关，可复用

好的 harness 不应该依赖具体任务语义。它应该只看：

- 是否还有未完成工作
- 是否已经验证
- 是否在重复工具调用
- 是否还有 budget 可以继续
- 是否输出结构满足要求

这类规则是 **task-agnostic** 的。

---

## 3. 触发条件是谁判断的

短答：

> **Claude Code 里关键触发大多是代码硬判断，不是模型自己判断。**

可以分成三类。

### 3.1 代码硬判断

这是最关键的一类。比如 token budget nudge：

- 不是模型自己说“我还可以继续”
- 而是外部代码调用 `checkTokenBudget(...)`
- 然后决定要不要往 message stream 里插一条 meta-message

这种模式可以概括为：

> **Trigger 由代码判，执行由模型完成。**

### 3.2 Prompt 软判断

比如系统提示里写：

- 完成前要验证
- 不要跳过 finish line
- 不要谎报测试通过

这些是“告诉模型应该怎么做”，但不保证执行。

### 3.3 混合判断

例如 verifier gate：

- **代码**判断是否需要 verifier（比如任务 non-trivial）
- verifier 具体怎么找 bug，由**模型**决定

这是最好的一种分工：

- 代码负责 protocol
- 模型负责开放式推理

---

## 4. Claude Code 里真正通用、非 task-specific 的例子

下面这些都不是“搜索任务专属”或“代码任务专属”，而是更基础的 agent control mechanism。

### 4.1 Token Budget Nudge

Claude Code 在 `query.ts` 里有 token budget 检查逻辑。当 budget 还允许继续时，会插入一条 meta-message，而不是等 agent 自己决定停。

这件事的本质是：

> **只要资源还值得继续，就默认 agent 不应该因为“感觉差不多了”而停。**

这个机制完全不依赖任务内容。

### 4.2 TodoWrite 状态机

Claude Code 的 todo 机制要求：

- 复杂任务要维护 todo
- 开始前标 `in_progress`
- 完成后标 `completed`
- 不要攒一堆任务最后一起改状态

这不是任务语义，而是通用 work protocol。

它解决的是：

- silent progress
- fake completion
- 遗忘子任务
- 只做了 80% 就开始总结

### 4.3 Plan Mode

Plan mode 的触发条件是：

- 多文件改动
- 架构决策
- 多种可行方案
- 需求不清楚

这不是“某个业务任务”的 trigger，而是**工作形态的 trigger**。

也就是说，Claude Code 在判断的不是“你是不是在做 RAG”，而是在判断“这个工作是否需要先 plan 再 implement”。

### 4.4 Verification Agent

Verifier prompt 的核心不是 task-specific 检查，而是角色目标完全不同：

- 主 agent：优化完成任务
- verifier：优化发现假完成 / 最后 20% 的问题

这种 **role objective decomposition** 是高度通用的。

### 4.5 System-Reminder 标签

Claude Code 允许在 tool result 或 user message 中自动混入 `<system-reminder>` 标签。

这一机制本身与任务内容无关。可注入的信息类型包括：

- 你还有 todo 未完成
- 你还没验证
- 你已经重复调用某类 tool
- 你应该切换模式
- 你还有 budget

本质上，这是一种 **in-loop control middleware**。

---

## 5. 一个更好的抽象名：In-Loop Steering Harness

把上面的做法统一抽象，可以叫：

- **Protocol-Guided Agent Loop**
- **Supervised Agent Harness**
- **In-Loop Steering Harness**

其中最直观的是第三个：

> 在 `tool / response / tool / response` 循环中，适时由系统插入 steering signal。

这和传统纯 LLM loop 的区别如下：

| 维度 | 传统 loop | Harness loop |
|---|---|---|
| 结束条件 | 模型主观判断 | 外部协议判定 |
| 验证 | 靠自觉 | 可被 gate 强制 |
| 提醒 | 靠 prompt 常驻 | 可在 loop 中动态注入 |
| 可观测性 | 黑盒 | 每个 trigger 都可 log |
| 复用性 | 弱 | 强 |

---

## 6. 最合理的职责分工

一个好的 agent harness 不应该把所有事情写死在代码里，也不应该全交给模型。

最合理的分工是：

### 6.1 代码负责判断“是否触发”

代码擅长做的是：

- 还有没有未完成 todo
- 输出 schema 是否完整
- budget 还剩多少
- 是否已经跑过 verifier
- 是否重复调用同类 tool
- 是否尝试 exit 超过 N 次

这些都应该由代码硬判断。

### 6.2 模型负责判断“怎么完成”

模型擅长做的是：

- 用什么搜索词再试一次
- 哪些字段最可疑
- 如何综合多个来源
- verifier 应该怎么设计对抗性 probe

也就是说：

> **代码判断是否继续，模型决定接下来做什么。**

---

## 7. 什么样的 trigger 才是通用的

如果你想在 HDMAS_v4 里做一个 task-agnostic 的 harness，trigger 最好只依赖下面五类通用信号。

### 7.1 Loop State

- 当前是第几轮
- 连续多少轮只 search 不 write
- 连续多少轮没有新信息增量
- 是否已经尝试 exit 若干次

### 7.2 Task State

- todo 是否全部完成
- 是否还存在 `in_progress`
- 是否已经经过 verifier
- 是否已经做过 self-check

### 7.3 Output State

- 输出 schema 是否完整
- 是否为空
- 是否含 placeholder（如 `unknown`, `TBD`, `null`）
- 是否缺 source / evidence

### 7.4 Resource State

- token budget
- tool budget
- time budget

### 7.5 Behavioral State

- 是否重复 search 同一 query
- 是否重复 fetch 同一 URL
- 是否长期 search 却不 synthesis
- 是否频繁切策略但没产生新信息

这些 trigger 都不依赖任务语义，因此是可复用的。

---

## 8. 一个抽象的 harness 结构

可以把 harness 看成一组 hooks：

```python
while not done:
    response = llm(messages)

    # Hook 1: 在 response 之后，tool 调用之前
    pre_tool_injections = harness.on_response(response, state)
    messages.extend(pre_tool_injections)

    if response.tool_calls:
        for call in response.tool_calls:
            result = execute(call)

            # Hook 2: 对 tool result 做增强
            result = harness.on_tool_result(result, state)
            messages.append(result)
    else:
        # Hook 3: 在 agent 想退出时拦截
        block = harness.on_exit_attempt(state)
        if block:
            messages.append(block)
            continue
        done = True

    # Hook 4: 每 N 轮 / 某阈值触发的 periodic hook
    periodic_msgs = harness.on_periodic(state)
    messages.extend(periodic_msgs)
```

这个结构本身就是 task-agnostic 的。

---

## 9. 对 HDMAS_v4 的具体启示

围绕你最关心的现象：

> 简单 query 也可能 `f1_by_item = 0`，说明不是复杂度问题，而是 agent 提前说 done。

那真正该学的不是“换更强模型”，而是：

1. **不要把完成条件交给做事的 agent 自己定义**
2. **把 verify / continue / exit 这些关键节点外提为 protocol**
3. **trigger 用 task-agnostic 的状态信号，不要绑死在具体业务字段上**

换句话说，Claude Code 值得借鉴的不是某个特殊 reminder 文案，而是这一整层：

> **Agent Loop 不是纯采样循环，而是受外部 harness 监督的受控执行过程。**

---

## 10. 最后一句总结

> 这种机制的本质，是把 agent 的“完成条件、继续条件、验证条件”从模型内部感觉，外提为系统级协议；它带来的本质好处，是减少早停、减少假完成、提高可控性和可审计性；在 Claude Code 里，关键触发大多由代码硬判断，而不是模型自己决定。
