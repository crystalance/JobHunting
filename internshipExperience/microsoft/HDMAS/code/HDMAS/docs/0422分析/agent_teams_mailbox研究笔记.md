# Claude Code Agent Teams: Mailbox 机制研究笔记

> 讨论日期：2026-04-20
> 参考资料：
> - 官方文档：<https://code.claude.com/docs/en/agent-teams>
> - Claude Code 源码（旧版本，已包含 swarm/teammate 实现）：
>   `c:\Users\v-weikailiao\OneDrive - Microsoft\Documents\deep_reasearch_agent\cc_src\src\src`

---

## 1. 文档层视角：Agent Teams 是什么

Claude Code 的 Agent Teams（experimental，需 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）由四个组件构成：

| 组件 | 作用 |
|---|---|
| **Team lead** | 主 session，创建 team、spawn teammates、协调任务 |
| **Teammates** | 独立 Claude Code 实例，每个有自己的 context window |
| **Task list** | 共享待办列表，teammates claim/complete，文件锁防 race |
| **Mailbox** | 消息系统，支持点对点 `message` 与 `broadcast` |

跟 **subagents** 的核心区别：subagent 是函数式调用（spawn → run → return），mailbox 让 teammates 之间可以**对等通信**，因此能做"竞争性假设辩论"、"跨层协调"等需要互相挑战的工作。

---

## 2. Mailbox 类系统的通用实现要素

| 要素 | 说明 | 常见实现 |
|---|---|---|
| Address / Identity | 每个 agent 有唯一名字 | 注册表 / config.json |
| Inbox | 每个 agent 一个有序、可持久化的消息队列 | `asyncio.Queue` / jsonl 文件 / SQLite / Redis stream |
| Send 原语 | `send(to, msg)` 写入对方 inbox | append / socket / `XADD` |
| Receive 原语 | 阻塞或事件触发地从 inbox 读消息 | inotify / signal / `XREAD BLOCK` |
| Broadcast | fan-out 给所有成员 | 遍历 registry / pub/sub topic |
| 并发安全 | 多 writer 同时写不能错乱 | 文件锁、原子 rename、advisory lock |
| Delivery 语义 | at-least-once / 顺序 / 去重 | `read` 标志位 / ack 文件 / offset |
| Notification | 让接收方"立刻知道"有新消息 | watcher / signal / 轮询 |

---

## 3. Claude Code 的具体实现（源码证据）

> 以下文件路径相对 `cc_src/src/src/`。

### 3.1 存储格式

`utils/teammateMailbox.ts`：

```text
~/.claude/teams/<team_name>/inboxes/<agent_name>.json
```

文件内容是一个 JSON 数组，每条消息形如：

```ts
type TeammateMessage = {
  from: string
  text: string
  timestamp: string
  read: boolean      // ← 关键：用 read 标志位实现 at-least-once + 去重
  color?: string
  summary?: string
}
```

**结论**：Claude Code 没有用追加式 jsonl，而是「整文件读 → push → 整文件写回」。这要求严格的写锁。

### 3.2 写消息（sender 侧）

`tools/SendMessageTool/SendMessageTool.ts` → `utils/teammateMailbox.ts::writeToMailbox`：

1. `mkdir -p inboxes/`
2. `writeFile(inboxPath, '[]', { flag: 'wx' })` —— 用 `wx` 原子地"如果不存在则创建"。
3. `lockfile.lock(inboxPath, { lockfilePath: <inbox>.lock, retries: { retries: 10, minTimeout: 5, maxTimeout: 100 } })` —— **proper-lockfile** 包，基于一个 `.lock` 目录/文件。重试 10 次 + 指数退避，避免并发 sender 互相 EBUSY。
4. **拿锁后重读** inbox（防止覆盖别人新写的消息）→ push 新消息 → 整文件写回。
5. 释放锁。

`SendMessage` 工具同步返回 `"Message sent to <name>'s inbox"`，**不阻塞等待对方回复**。

`broadcast` 在 tool 层就是循环调 `writeToMailbox`，不是 pub/sub topic。

### 3.3 通知机制：**纯轮询，没有 fs watcher**

这点跟我之前猜测的"inotify/fs watcher"**不一样**，源码里是定时轮询：

- **进程间（tmux 模式 / 跨进程 teammate）**：`hooks/useInboxPoller.ts`
  - `INBOX_POLL_INTERVAL_MS = 1000` —— 每秒读一次 inbox。
  - 调 `readUnreadMessages(agentName, teamName)` 拿所有 `read === false` 的消息。
  - 按类型分桶：`permissionRequests / permissionResponses / shutdownRequests / planApprovalRequests / regularMessages / ...`，分别处理。

- **进程内（in-process teammate，一个 Node 进程托管多个 teammate）**：`utils/swarm/inProcessRunner.ts::waitForNextPromptOrShutdown`
  - `POLL_INTERVAL_MS = 500` —— 每 0.5 秒一次。
  - 每轮先扫"shutdown 请求"（最高优先级），再扫"team-lead 来的消息"（避免被 peer 消息饥饿），再 FIFO 扫其他消息。
  - 如果都没有，再 `tryClaimNextTask(taskListId)` —— **task list 与 mailbox 共用同一个 wait loop**。

为什么用轮询而不是 watcher？最可能的原因：跨平台一致性（Windows fs events 行为差异大）+ 实现简单 + 1s 延迟对人类协作时间尺度可接受。

### 3.4 收件方如何把消息塞进 LLM message list

这是当时讨论里最关键的问题：**mailbox → LLM `messages[]` 的具体路径**。

源码答案分两种部署模式：

#### (a) 进程内 teammate（`inProcessRunner.ts`）

- agent 主循环跑 `runAgent()`；每次 LLM turn 结束后调 `waitForNextPromptOrShutdown(...)`。
- 该函数 loop 轮询 mailbox：
  - 拿到一条 `unread` 消息 → 立即调 `markMessageAsReadByIndex` 标记已读 → return `{ type: 'new_message', message, from, color, summary }`。
- 主循环拿到结果后：

  ```ts
  if (waitResult.from === 'user') {
    currentPrompt = waitResult.message              // 用户消息：原文
  } else {
    currentPrompt = formatAsTeammateMessage(        // 队友消息：包 XML 标签
      waitResult.from, waitResult.message,
      waitResult.color, waitResult.summary,
    )
    appendTeammateMessage(taskId,
      createUserMessage({ content: currentPrompt }),
      setAppState)
  }
  ```

- 然后 `createUserMessage({ content: currentPrompt })` → push 到 `allMessages` → 进入下一次 `runAgent()` 调 LLM。

#### (b) 跨进程 teammate（`useInboxPoller.ts`）

- React hook 每秒轮询。
- 把多条普通消息拼成一段 XML：

  ```ts
  // utils/teammateMailbox.ts
  export function formatTeammateMessages(messages) {
    return messages.map(m =>
      `<teammate-message teammate_id="${m.from}"${colorAttr}${summaryAttr}>\n${m.text}\n</teammate-message>`
    ).join('\n\n')
  }
  ```

  常量定义：`constants/xml.ts` → `TEAMMATE_MESSAGE_TAG = 'teammate-message'`。

- **空闲时**：直接 `onSubmitTeammateMessage(formatted)` 把这段 XML 当作"用户输入"提交，触发新一轮 LLM turn。
- **忙时**（`isLoading || focusedInputDialog`）：写入 `AppState.inbox.messages`（status: `pending`），等当前 turn 结束后另一个 hook 把它合并提交。
- 所有路径都在「成功递交后」才 `markMessagesAsRead` —— 实现"宕机重读"语义。

### 3.5 关键 invariants

- **消息以 `role: "user"` 进入 LLM `messages[]`**（通过 `createUserMessage`），用 `<teammate-message>` XML 标签让模型区分"真人 user"与"队友 user"。
- **单消费者保证**：每个 inbox 文件只被自己 agent 的 poll loop 读 + 标 read，不会有第二个进程消费同一 inbox。
- **send 同步、receive 异步**：sender 写完即返回，受方在自己下一轮 poll 才看到——这是 mailbox 的核心异步语义。
- **优先级**：shutdown > team-lead > peer FIFO > task-list claim。
- **特殊消息走结构化 JSON in `text`**：例如 `permission_request / permission_response / plan_approval_request / shutdown_request`。`useInboxPoller` 用一组 `is*(text)` 解析器分桶，**这些不会进 LLM**，由 runtime 直接处理（弹权限对话框、转 `ToolUseConfirmQueue`、改 PermissionMode 等）。

---

## 4. 时序：A 发消息给 B，B 处理并回复

```text
t0  A.LLM 返回 tool_call SendMessage(to=B, text="...")
t1  A.runtime 执行 SendMessage:
      - lockfile.lock(B.json.lock, 重试 10 次)
      - 重读 B.json
      - push 新消息 (read=false)
      - 写回 B.json
      - 释放锁
      - 工具同步返回 "Message sent to B's inbox" 给 A.LLM
t2  A.LLM 拿到 tool_result，继续推进自己的工作（不阻塞）

并行：
t1' B 处于 idle / 上一轮 turn 间隙，poll loop 每 0.5~1s 触发
t2' B.runtime 读 B.json：
      - 扫 shutdown? 无
      - 扫 from=team-lead? 无
      - 取第一条 unread → markRead(idx) 立刻标已读
t3' B.runtime: currentPrompt = formatAsTeammateMessage(A, "...")
                = "<teammate-message teammate_id=\"A\">...</teammate-message>"
t4' B.runtime: createUserMessage({ content: currentPrompt }) → allMessages.push
t5' B 进入下一次 runAgent() → llm.chat(messages=[..., 上面那条 user 消息])
t6' B.LLM 决定 SendMessage(to=A, text="复现了, token 过期")
t7' B.runtime 写到 A.json + 标 read

A 这边：
t8  A 当前 turn 结束 → poll loop 触发 → 读 A.json → 看到 B 的回复
t9  A.runtime 包成 <teammate-message teammate_id="B">...</teammate-message>
t10 当作 user 消息提交 → A.LLM 在新 turn 看到 B 的答复
```

**关键点**：

- A 不被打断，B 也不被打断。"中断"在源码里完全不存在；唯一的"中断"是 abort signal（用户主动终止）。
- 1s/0.5s 的 poll 间隔 = mailbox 端到端延迟下界（idle 时）；忙时延迟 = 当前 LLM turn + 工具执行 + poll 间隔。
- mailbox 不知道 LLM 是什么，它只往 `AppState.inbox.messages` / `pendingUserMessages` 队列塞东西；LLM 那一侧由 agent runtime 在 turn 边界主动 pull。

---

## 5. 跟我之前推测的对比

| 我之前的推测 | 源码实际 |
|---|---|
| 每个 teammate 一个 jsonl 追加文件 | 单个 `<agent>.json` 数组，整文件读改写 |
| fs watcher / inotify / signal 推送 | **纯定时轮询**（in-process 0.5s，跨进程 1s） |
| 文件锁防并发写 | ✅ 一致，用 `proper-lockfile`，重试 10 次指数退避 |
| 消息以 `role: "user"` 加 XML 标签注入 | ✅ 完全一致：`<teammate-message teammate_id="...">` |
| sender 同步返回，receiver 在 turn 边界 pull | ✅ 完全一致 |
| 结构化消息（shutdown / 权限请求）走 mailbox | ✅ 一致；并且**这些不会进 LLM**，由 runtime 拦截处理 |
| broadcast 是 pub/sub topic | ❌ 实际是 **tool 层循环调 send**，逐个写文件 |
| in-process / cross-process 用同一份代码 | ❌ 两条不同代码路径：`useInboxPoller`（hook，跨进程）vs `waitForNextPromptOrShutdown`（runner，进程内） |

---

## 6. 对我们项目的启示（HDMAS_COPILOT）

1. **Mailbox 不需要复杂基础设施**。Claude Code 自己也只用了「文件 + lockfile + 定时轮询」，跨平台、零依赖、易调试。我们如果想加 inter-agent 通信，完全可以照抄这套结构。
2. **send 必须是非阻塞的**。如果改成"等回复"，会出现死锁（A 等 B，B 也卡在等 A）。需要"问答"语义就用 request_id + 后续 turn 自然续上。
3. **轮询间隔决定协作粒度**。0.5~1s 已经足够人 + LLM 协作；要做高频 agent 通信再考虑 watcher。
4. **结构化消息要分桶**。把「真要喂 LLM 的对话」与「runtime 控制信令」（权限、shutdown、计划审批）分开，避免污染上下文窗口、避免出现 LLM"幻想"自己有控制能力的 bug。
5. **优先级 + FIFO 防饥饿**。team-lead 消息优先于 peer 消息，是为了保证用户意图能穿透。我们的 multi-agent 也该有类似的"指挥链优先级"。
6. **at-least-once + 已读标志**比"读后删"更稳健。崩溃重启不会丢消息。

---

## 7. 一句话总结

> A 调 `SendMessage` 工具 → runtime 在文件锁保护下把消息追加进 `~/.claude/teams/<team>/inboxes/B.json`，立刻 return `"sent"` 给 A 的 LLM；B 的 runtime 每 0.5~1s 轮询自己的 inbox，拿到未读消息后包成 `<teammate-message teammate_id="A">...</teammate-message>` 的 XML，**作为 `role:"user"` 消息追加到 B 自己的 `messages[]`**，下一次 `chat/completions` 调用 B 的 LLM 就"看到"了这条消息。整条链路里 LLM 始终是无状态的、被多次重新调用的纯函数；mailbox 不是"推到 LLM 里"，而是"推到 B 进程的下一个 turn 边界上"。
