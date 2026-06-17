# WideSearch 失败原因与 8agent 对比 —— 问答总结

> 日期：2026-04-22
> 数据源：
> - BARE：`COPILOT_FOR_Widesearch/results/test_0416_bare_en50` (200 题)
> - HDMAS_3a：`HDMAS_COPILOT/batch_results/test_0416_copilot_en50_3agents` (200 题)
> - HDMAS_8a：`HDMAS_COPILOT/batch_results/test_0416_copilot_en50_8agents` (50) + `test_0417_copilot_en100_8agents` (74) = 124 题

---

## Q1. BARE 与 HDMAS_3a 这两者"没有答案或者完全 0 分"都是什么原因？

### 概览

| | BARE | HDMAS_3a |
|---|---|---|
| 总题数 | 200 | 200 |
| **SR=0**（没全对） | **177** (88.5%) | **175** (87.5%) |
| **完全无答案 (no_csv)** | **30** (15.0%) | **21** (10.5%) |
| **解析了但 f1=0**（完全错） | 1 (0.5%) | 0 |

> HDMAS 比 BARE 少 9 题 no_csv（主要是 ZH），但 SR=0 总数几乎一样 — 说明 HDMAS 救回的是"低分有答案"，没能把这些转成"完整对"。

### A. 无答案 (no_csv) 的根因

#### BARE 30 题分类

| 类别 | 数 | 平均时长 | 平均字符 | 含义 |
|---|---|---|---|---|
| **timeout_no_table** | 14 | 1805s | 558 | 超时且根本没产出表 — 还在搜的时候被 30 分钟 cap 截断 |
| **completed_with_table**（解析失败） | 10 | 984s | 6430 | 跑完了，输出有表，但 parser 解析失败 |
| timeout_with_table | 4 | 1805s | 4673 | 超时但输出过表（半成品） |
| completed_no_table | 2 | 751s | 3215 | 跑完但根本没输出表（直接说"无法完成"等） |

按语言：EN 7 / **ZH 23**（ZH 占 77%）

#### HDMAS_3a 21 题分类

| 类别 | 数 | 平均时长 | 平均字符 | 含义 |
|---|---|---|---|---|
| **timeout_no_table** | 14 | 1806s | **0** | 超时且 response 是空字符串（最严重） |
| completed_no_table | 5 | 1464s | **0** | **没超时，但仍没产出最终 response** ← 协作流程异常 |
| completed_with_table | 2 | 942s | 5417 | 跑完了，输出有表，但 parser 解析失败 |

按语言：EN 6 / **ZH 15**（ZH 71%）

### B. SR=0 中"接近正确"的占比（这才是 main bucket）

| f1_by_item bucket | BARE | HDMAS_3a |
|---|---|---|
| A. no_csv | 30 (16.9%) | 21 (12.0%) |
| B. csv 但 f1=0（完全错） | 1 (0.6%) | 0 |
| C. 0 < f1 < 0.25 | 6 (3.4%) | 3 (1.7%) |
| D. 0.25 ≤ f1 < 0.5 | 14 (7.9%) | 17 (9.7%) |
| E. 0.5 ≤ f1 < 0.75 | 29 (16.4%) | 25 (14.3%) |
| **F. 0.75 ≤ f1 < 1.0** | **97 (54.8%)** | **109 (62.3%)** |

**SR=0 的题里超过一半 f1 在 0.75–1.0 之间** —— 也就是说 177 题打 0 分的本质是"差一点点没全对"，不是"完全做错"。这正是 early-convergence / "差最后一点完整性" 的典型特征。

### C. 三大改造方向（按 ROI）

| P | 方向 | 预期 SR 上限提升 | 难度 |
|---|---|---|---|
| **P0** | 修 evaluator 的列严格匹配 + 容错 | +5 pt（救 BARE 10 题、HDMAS 2 题） | 低 |
| **P0** | HDMAS "completed but empty response" 5 题 wiring 修复 | +2.5 pt HDMAS | 低 |
| **P1** | 把 ZH 的 timeout（约 20% 题）从"还在搜"推进到"产出表" | +5–10 pt | 中 |
| **P2** | F bucket（109 题接近全对）防 early-convergence → 推到全对 | 理论 +50 pt 上限，实际 +5–10 pt | 高 |

### 一段话总结

**两个系统 SR=0 的题里 60–70% 是"接近全对" (f1≥0.75)，根本不是"做错" —— 是 early-convergence**。完全无答案的题里：BARE 30 题里 60% 是 ZH 超时（搜不完）、33% 是输出表了但被评测器列严格匹配杀掉；HDMAS 21 题里 67% 是 ZH 超时（且响应字符串为空）、还有 5 题是协作流程 bug 导致没超时但空 response。**最容易拿的提升其实是修评分器列匹配（+5pt）和 HDMAS 的 5 题 wiring bug（+2.5pt）**，比改架构便宜得多。

---

## Q2. `completed_with_table` 解析失败 —— 是答案格式不对还是评测器问题？

### 三类原因

| 类别 | 数 | 谁的锅 | 典型例子 |
|---|---|---|---|
| **A. 模型多了/少了/译错列名**（schema 不严格匹配） | **7** | **模型** | 见下 |
| B. 评测器自身崩溃（traceback） | 3 | 评测器 / 数据中字符无法被 apply 处理 | ws_en_045, ws_zh_006, ws_zh_078 |

### A 类细分（7 题里 3 种 sub-pattern）

#### A1. 模型"多写一列"（小 over-deliver, 答案本质对）— 3 题
- **ws_en_039**：题目要 `[rank, universityname, country, specificaddress]`，模型多写了 `founding year`
- **ws_zh_010**：多了 1 列
- **ws_zh_048**：多了 1 列

→ 这 3 题答案其实正确，只是 schema 严格匹配把它判 0。**容易救**：prompt 里强化"列必须严格等于这几个，不能多不能少"。

#### A2. 模型完全用错列（误解题目）— 3 题
- **ws_en_049**：题目要 9 列汽车规格 `[modelname, price, dimensions, wheelbase, maxtorque, frontsuspension, ...]`，模型输出的是 `[Model, Launched, Status, Decision, Rationale]` —— 完全是另一张表
- **ws_zh_070**：要 4 列，模型给出 5 列且语义不同
- **ws_zh_072**：列名几乎全错位

→ **模型根本没读懂题目要的字段**。Prompt + planner 的锅，不是格式问题。

#### A3. 模型用英文写了中文表头 — 1 题
- **ws_zh_080**：要中文列 `[文件, 日期, ...]`，模型输出 `Document | Date Filed | HKEX URL`

→ 模型没遵守语言一致性。

### B 类（3 题，评测器/数据本身的事）
- **ws_en_045**：`evaluation.py` line 267 在 `df_inner_score[f"{col}_..."] = ...` 时崩了
- **ws_zh_006**：`response.extract_dataframe()` 抛异常 — 可能是 markdown 表里有奇怪字符
- **ws_zh_078**：`evaluation.py` line 184 在 `response_df[col].apply(...)` 时崩了 — 单元格内容评测器不会处理

### 结论

> **`completed_with_table` 解析失败 = 70% 模型 schema 没遵守 + 30% 评测器崩溃**。

- 在"模型锅"里又 50/50：一半是 **小 over-deliver（多 1 列）**——加一句严格 prompt 就能救（≈3pt SR）；另一半是 **真的没读懂题目要哪些字段**——需要 planner / verifier 把"required columns"作为 hard checklist 显式校验。
- 评测器锅 3 题更多是单元格内容（中文符号、特殊字符）让 pandas apply 崩，可以加 try/except 兜底，但那是 WideSearch 仓库的事，不是 agent 这边能修的。

---

## Q3. 为什么 8agent 反而不如 3agent 好？从 score 层面具体说明

### 核心数字（同一批 124 题，EN+ZH）

| 指标 | 3agent | 8agent | 备注 |
|---|---|---|---|
| **score (SR, 严格全对)** | **0.137** | 0.097 | 3a 高 41% |
| f1_by_item（部分得分） | 0.762 | **0.772** | 8a 反而略高 |
| f1_by_row | 0.559 | 0.561 | 几乎一样 |
| **SR=1 题数** | **17** | 12 | 3a 多 5 题 |
| 3a 拿 SR=1 但 8a 没拿 | **7** | — | |
| 8a 拿 SR=1 但 3a 没拿 | — | 2 | |
| 头对头（f1_item） | 3a 胜 50, 平 24, 8a 胜 50 | | 互有胜负 |

**核心矛盾**：8agent 的"部分得分"略好，但"严格全对"少了 41%。这就是"**细而不全**"。

---

### 三种 8agent 自残的典型 case

#### Case 1 —— 8a "重新设计列名" → 整张表 0 分（最常见，最致命）

**`ws_en_008`** （股票交易所统计）

| | 3agent | 8agent |
|---|---|---|
| f1_item | **0.947** | **0.000** |
| 行数 | 27 | 7 |
| 列头 | `\| Exchange Name \| Statistical Month \| Total Trading Value (USD millions) \| Total Number of Listed Companies \| Domestic Market Capitalization (USD millions) \| ...` | `\| Month \| Trading Value (USD M) \| Listed Companies \| Market Cap (USD M) \| NYSE Composite \|` |
| 评测 msg | （正常打分） | `required_columns ['exchangename','statisticalmonth',...] != response_df Index(['month','tradingvalue',...])` |

**剧情**：3a 老老实实 carry 了题目要的列名（`Exchange Name, Statistical Month, Total Trading Value...`）→ 评测器认。8a 的某个 agent（可能是 "report writer" 角色）"优化"了列名（`Month, Trading Value (USD M), Listed Companies, NYSE Composite`），还把 Exchange Name 这列拿掉了，**8 个 agent 没有一个把它拍回去** → 评测器列严格匹配 fail → 27 行变 7 行 + 0 分。

> **agent 多了之后，每个 agent 都倾向于"加点自己的修改" — 列名越改越远；3 个人吵就妥协回原样，8 个人吵就吵成新方案。**

#### Case 2 —— 8a 协作 dropout，最终 response 直接空字符串

**`ws_zh_003`** 和 **`ws_en_084`**

| | 3agent | 8agent |
|---|---|---|
| `ws_zh_003` f1_item | **0.781** | **0.000** |
| `ws_en_084` f1_item | **0.344** | **0.000** |
| 8a response | （正常表） | **`""` 空字符串** |
| eval msg | （正常） | `response_df is None` |

**剧情**：3a 跑完输出了 64 行表 / 172 行表（前者全部正确率 78%，后者部分对）。8a 跑完了，但 orchestrator → final answer 这一段 wiring 在 8 角色场景下更脆弱（vote 卡住、谁负责写 final 没明确、某个 agent 抢锁失败等），**最后给 evaluator 的是空串**。

> **agent 数量翻倍，"谁来写最终答案"的协议复杂度非线性涨；3a 模式简单，8a 模式经常没人收尾。**

#### Case 3 —— 8a "差最后一两条" 的细水长流（典型"细而不全"）

把 7 道 "3a 拿 SR=1 但 8a 没拿" 的题摆出来看 8a 的 f1_item：

| 题 | 3a SR | 8a f1_item | 差距 |
|---|---|---|---|
| ws_en_069 | 1.000 | **0.992** | 差 **0.8%** |
| ws_zh_017 | 1.000 | **0.994** | 差 **0.6%** |
| ws_zh_012 | 1.000 | **0.991** | 差 **0.9%** |
| ws_zh_004 | 1.000 | 0.981 | 差 1.9% |
| ws_en_081 | 1.000 | 0.972 | 差 2.8% |
| ws_en_037 | 1.000 | 0.929 | 差 7% |
| ws_en_018 | 1.000 | 0.833 | 差 17% |

**这 7 题里有 4 题 8a 离 100% 不到 2%** —— 可能就是某个 cell 里的数字精度被某个 agent "改写"成了别的写法（"$1.2B" vs "1,200,000,000"）、或者某行被 dedupe 误删了。SR 是 0/1 全对评分，差 1 个 cell = 0 分。

> **3agent 链路短：找到答案 → 整理 → 输出。改动机会少。**
> **8agent 链路长：找答案 → A 校验 → B 翻译 → C 重排 → D 写表 → E 评审。每个环节都可能"轻微改写"原始正确答案，8 个环节累计 → 至少错 1 处。**

---

### 总结：8agent 在这个 benchmark 上反而更差的 3 个机制

| # | 机制 | 后果 | 表现在 case |
|---|---|---|---|
| 1 | **"民主化重设计"**：角色多了，每个 agent 都倾向于"贡献自己的改动"，最常见就是改列名 / 翻译列名 / 简化列名。3 人吵会回到原样，8 人吵会形成"新共识"。 | 整张表被评测器列严格匹配杀掉 → 0 分 | ws_en_008（27 行变 0 分） |
| 2 | **协作 wiring 脆性**：orchestrator → "谁负责写 final response" 的协议在 8 角色下经常掉球，最终 response 是空字符串。 | 直接 0 分 + 浪费 ~25 分钟 | ws_zh_003, ws_en_084 |
| 3 | **细节漂移**：每多一个 agent 经手，原始正确答案就多一次"被轻微改写"的机会。WideSearch 的 SR 评分极苛刻（差 1 cell = 0 分），所以 f1_item 0.99 vs 1.00 的差别 = SR 0 vs SR 1 | f1 看起来只差一点点，SR 直接砍半 | ws_en_069 (0.992), ws_zh_017 (0.994), ws_zh_012 (0.991) |

### 一句话理解

> **WideSearch 是"找全 N 条答案 + 列名/格式分毫不差"的零容错评分。在这种 task 上，agent 数量增加只会放大"信息在传递链路里被改写"的概率 —— 3agent 是最短可用链路，8agent 多出来的 5 个 agent 没在"找回更多答案"上帮忙（f1_item 几乎没涨），却显著放大了"改写已找到的答案"和"丢掉最终输出"的风险，导致 SR 反降 41%。** 这是典型的 **"中间过程方差大于增量价值"** —— 也是为什么 Claude Code 这类系统坚持 **"主 agent 单线程，subagent 只回报压缩结果不直接修主答案"** 的根本原因。

---

## Q4. 时间对比：BARE vs HDMAS_3a —— 为什么"并行架构"反而更慢？

> 我们最初设计 multi-agent 架构的核心动机之一是：**"3 个 agent 并行干活，应该能把任务做得更快，并且可以 scale up"**。
> 实测结果恰好相反。这一节用数据和案例解释为什么。

### A. 总体时间对比（n=198 共同题）

| 指标 | BARE | HDMAS_3a | 比值 |
|---|---|---|---|
| 平均时长 | **767 s** | **1071 s** | 1.40× |
| 中位数时长 | 634 s | 988 s | 1.56× |
| p90 时长 | 1803 s | 1806 s | ≈相同（都打到 30min cap） |
| timeout 题数 | 21 | 30 | HDMAS 多 9 题 |

### B. 排除 timeout，纯粹"两边都正常完成"的 161 题

| 指标 | BARE | HDMAS_3a | 比值 |
|---|---|---|---|
| 平均时长 | **605 s** | **929 s** | **1.53×** |
| 中位数时长 | 499 s | 851 s | **1.71×** |
| 单题 ratio 中位数 | — | — | **1.73×** |
| HDMAS 比 BARE 快的题 | — | — | **仅 21/161 (13%)** |

> **HDMAS_3a 在 87% 的题上比 BARE 慢**，中位数慢 1.7 倍。

### C. HDMAS 的"时间地板"现象

BARE 能在 5 分钟内做完的简单题，HDMAS 几乎一律花 6–10 分钟：

| 题 | BARE | HDMAS_3a | ratio |
|---|---|---|---|
| ws_zh_050 | **59 s** | **472 s** | **8.0×** |
| ws_en_088 | 63 s | 390 s | 6.1× |
| ws_zh_004 | 91 s | 507 s | 5.6× |
| ws_zh_015 | 93 s | 670 s | 7.2× |
| ws_en_080 | 113 s | 496 s | 4.4× |
| ws_en_022 | 130 s | 404 s | 3.1× |

→ **HDMAS_3a 有一个 ≈ 6 分钟的 "起步成本地板"**：再简单的题，3 个 agent 也要走完一整套 [并行思考 → 抢锁 → 协商 → 投票 → 收束] 流程。

---

### D. 用 ws_zh_050 解剖：为什么 59s 的事要花 472s

ws_zh_050 是个 ZH 题，BARE 一路顺畅 **59 s** 拿到答案。HDMAS 同题花了 **472 s**（**8 倍慢**）。Event log 拆开看：

| 角色 | 活跃跨度 | 事件数 | 实际"工作"时间 | 利用率 |
|---|---|---|---|---|
| `agent_0` | 0 → 467 s | 39 | 467 s | 100% |
| `agent_1` | 0 → 467 s | 52 | 467 s | 100% |
| `agent_2` | 0 → 467 s | 30 | 467 s | 100% |
| **3 agents 累加 LLM 工作时间** | | | **1401 s** | |
| **wall time（实际用户等待）** | | | **472 s** | |
| **并行因子** | | | **2.97×**（接近完美 3 路并行） | |

**对比 BARE**：单线程 LLM 在 59 s 内完成。

#### 关键观察：**并行其实成功了，但被"额外的 LLM 工作"吃光了**

- HDMAS 在这道题上做了 **1401 s 的 LLM 工作**，是 BARE（59 s）的 **23.7 倍**
- 并行因子 2.97× 把 1401 s 压成 472 s
- 但还是比 BARE 慢 8 倍——因为 **多干的活远多于并行能省的时间**

### E. tool 调用拆开看："并行的 1401 s 都在干什么？"

ws_zh_050 在 events.jsonl 里记录的 33 个 tool_call **没有一个是搜索/网页 tool**：

| Tool | 次数 |
|---|---|
| `lock_file` | **20** |
| `unlock_file` | **13** |
| 真正的 search/web tool | 0（这些走 Copilot 内置 tool，不计入 orchestrator 日志） |

→ HDMAS 的 orchestrator 层只看见 **agents 在反复抢黑板锁**。20 次 lock + 13 次 unlock = 33 次"协调操作"。
→ 同样的模式在 worst-20 case 上扩大到 **lock_file 437 次 + unlock_file 299 次**。

### F. vote_stop 收束机制的尾部代价

| | ws_zh_050 实际 |
|---|---|
| `vote_stop` 事件总数 | 6（3 个 agent 各 2 次重复 vote） |
| 第一票到最后一票时差 | +0s → +17s |
| 整体平均（161 cases）`vote_stop`/case | **4.1 次** |

需要"全员一致 vote 结束" → 即使 agent_2 早 17 s 就投了"该结束"，也要等 agent_1 才真的关停。这就是 Amdahl 律里的 **同步收束尾部**：3 个 agent 要在最慢那个节点收齐。

### G. 跨案例总账（n=161 no-timeout cases）

| 指标 | 平均 |
|---|---|
| 单题 LLM 思考 turn 数（assistant_message） | **159 个**（≈ 53 turn/agent × 3 agents） |
| 单题 orchestrator-level tool_call 数 | **35 个**（全是 lock/unlock） |
| 单题 vote_stop 事件 | 4.1 个 |
| **3 个 agent 累加 active 时间** | **2428 s** |
| **wall time** | **939 s** |
| **并行因子** | **2.64×**（mean） / 2.66×（median）|

---

### H. 为什么"理论上的并行收益"没有兑现 —— 真正的根因（重要：修正之前"重复劳动"的猜测）

> **第一版分析里我猜"3 agent 都在做整题、80% 重叠"。翻了 blackboard.json 后这个判断是错的——任务分工实际上是生效的。** 真正的瓶颈在别处。

#### 实证 1：任务分工是真实生效的

抽样 10 个 case 看 `workspace/blackboard.json` 的 `task_log`：

| case | n_subtasks | distinct agents | 分工示例 |
|---|---|---|---|
| `ws_zh_050` | 4 | 3 | agent_0=2015–17, agent_2=2018–20, agent_1=2021–24 |
| `ws_en_088` | 4 | 3 | agent_0=2015–17, agent_1=2018–20, agent_2=2021–24 |
| `ws_zh_004` | 5 | 3 | agent_1=2019–20, agent_0=2021–22, agent_2=2023–24 |
| `ws_en_022` | 3 | 3 | agent_1=Spotify全球, agent_2=Spotify美国, agent_0=合并表 |
| `ws_en_080` | 4 | 3 | agent_0=Paris2024, agent_2=Rio2016, agent_1=Tokyo2020 |
| `ws_en_007` | 5 | 3 | agent_0=Mercury+Gemini, agent_1=Apollo, agent_2=Skylab |

**跨 198 个 case 的统计**：
- **95% (188/198) 的 case 用满了 3 个 agent**
- **0 个 case 把所有任务塞给单一 agent**
- 平均 5.5 子任务/题，平均 2.95 个 distinct agent
- 即使是 2025 年俄超 MVP 评选这种小任务，也被切成了 球员/教练/球队 三块分给 3 个 agent

→ **planner 工作了，分工生效了**。这才是真正的反直觉点：*分工成功的情况下，时间还是膨胀 1.5–8×*。

#### 实证 2：膨胀的不是"重复劳动"，是"每个 turn 的协议成本"

回到 ws_zh_050 的 agent_1 时间线（这是负责 2021–2024 共 4 年的 agent，理论上 4 次网页抓取应该 ≈ 1 分钟）：

```
+  0s  agent_start
+ 11s  assistant_message → tool_call(lock_file)        ← 第 1 turn (LLM 11s)
+ 71s  assistant_message → tool_call(lock_file)        ← 第 2 turn 间隔 60s
+105s  assistant_message → tool_call(lock_file)        ← 第 3 turn 间隔 34s
+136s  assistant_message                                ← 第 4 turn 间隔 31s
+143s  tool_call(unlock_file)
+186s  assistant_message                                ← 又 43s
+251s  assistant_message → tool_call(lock_file)        ← 又 65s
... (持续到 +438s vote_stop)
```

**agent_1 跑了 52 个事件 / ≈ 25 个 LLM turn 才完成 "拉 4 年 Wikipedia 页面 + 写一个 markdown 表" 的任务。** BARE 单线程做整个题（10 年）只用了 59s。

#### 真正的根因 —— **每 turn 的 context-reload 税**

每个 agent 在每个 turn 都要：
1. 重新读取整个 blackboard.json（其他 agent 的进度）
2. 重新读取自己的 personal log
3. 重新看自己上一轮的 tool 输出
4. 决定下一步是 search / 还是 lock blackboard / 还是 vote_stop
5. 写出 assistant message + tool_call

→ 这个 prompt 的输入 context 随时间膨胀（task_log 越长越大），LLM round trip latency 也跟着膨胀（最后几轮 60 s/turn 不奇怪）。

**实测 per-agent turn latency**（ws_zh_050）：
- agent_0: 平均 13.8 s/turn，最大 60 s
- agent_1: 平均 9.3 s/turn，最大 60 s
- agent_2: 平均 16.4 s/turn，最大 60 s

agent_1 拉 4 年页面 → 需要 ≈ 25 turn → 25 × 10s = 250s + 大量协调 LLM call → ≈ 470 s。

**BARE 单线程拉 10 年页面**：每个页面 ≈ 6 s LLM round trip + 工具 → 10 × 6 = 60 s ≈ 实测 59 s。

#### 为什么单 agent 反而每 turn 更短？

- BARE 的 prompt context 只有 "题目 + 自己的搜索历史"，**约 20 KB**。
- HDMAS agent 的 prompt context = "题目 + 公共 blackboard + 自己 history + 其他 agent 的 message hint"，**约 60–100 KB 且单调增长**。
- LLM 推理时间随 input tokens 近线性增长 → **HDMAS 每 turn 的 LLM 延迟是 BARE 的 2–3×**。

#### 加上协调税

- **lock_file/unlock_file** 都是 LLM tool_call → 每次至少 1 次 LLM round trip
- ws_zh_050 总共 33 次 lock/unlock → 协调本身就吃 ≈ 2–4 分钟
- vote_stop 必须 all-3 投齐才结束，最快 vote 完后还要等 ≈ 17 s（实测）才达成 quorum

**Amdahl 律修正版**：
$$T_{HDMAS} = T_{coord} + \max_i \big(N_i \cdot L_{turn}^{HDMAS}\big)$$
其中 $L_{turn}^{HDMAS} \approx 2 L_{turn}^{BARE}$（因 prompt 膨胀），$N_i$ 是 agent $i$ 的 turn 数。

由于 turn latency 翻倍 + 每个 agent 自己也至少要走 ≈ 20+ turn 的"看-想-动"循环，**即使分工分得再好，单 agent 的最少 wall time 也大幅超过 BARE 整题时间**。

---

### I. 那 "scale up 的潜力" 在哪里 —— 还能救吗？

任务分工已经做对了（这是好事）。剩下 3 个真正在拖慢架构的因素和对应可能的修复方向：

| 问题 | 当前现象 | 可能修复 |
|---|---|---|
| **Context 膨胀** | 每个 agent 的 prompt 包含整个 blackboard + 别人的 message → 每 turn LLM 延迟翻倍 | (a) 给每个 agent 只 inject 自己 sub-task 相关切片；(b) 用 sub-agent 隔离 context（Claude Code 模式：sub-agent 跑完只回压缩摘要）|
| **Lock/Unlock 用 LLM tool_call 实现** | 每次锁操作 = 1 次 LLM round trip（10–60s）；33 次锁 = 5+ 分钟纯协调 | 改成 *system 自动加锁*（agent 写 blackboard 时框架自动获取锁），LLM 不感知 |
| **同步 vote quorum** | 必须 3 个 agent 都投 vote_stop 才结束，最慢的卡住所有人 | 改成 *progress-based 早停*：当 `task_log` 全 done 且 `answer/` 非空 → 立即终止剩余 agent |
| **每 agent 自己也要循环 20+ 次** | 即使只负责 4 年数据，agent 也要走完"读 blackboard → 决定下一步 → 加锁 → 抓 → 解锁 → 写汇报 → 再 check 别人 → ..."20+ 次 | 改成 *worker 模式*：planner 一次下发整个 sub-task spec，worker 单线程执行，不再频繁 check blackboard |

理论上 multi-agent 架构有三种"正确用法"，目前我们部分踩到了（A 已对），但被 B/C 的开销拖累：

| 用法 | 我们的现状 | 状态 |
|---|---|---|
| **A. 子任务划分（embarrassingly parallel）** | ✅ blackboard task_log 显示已生效，95% 题 3 agent 各拿一段 | **正确** |
| **B. Context 隔离（每人只看自己那一块）** | ❌ 所有 agent 共读 blackboard 全文 + 互发 message | **未做** |
| **C. 框架级协调（系统自动加锁、早停）** | ❌ lock/vote 都走 LLM tool，每次 10–60s | **未做** |

→ **要让分工带来真正的并行加速，关键不是再分得更细，而是切掉每个 agent 的"协议开销"——上下文隔离 + 系统级锁 + 早停**。

### J. 一段话总结时间维度

> **HDMAS_3a 的 1.5–8× 慢于 BARE 不是因为"3 agent 干同样的活"——blackboard 数据显示 95% 的题任务分工实际生效**。**真正的瓶颈是每个 agent 在每个 turn 都要重读完整 blackboard 上下文 + 走 LLM tool_call 加锁/解锁/投票，导致单 agent 的 per-turn latency 比 BARE 翻倍，而每个 agent 还要经历 20+ 次这样的 turn 才能完成自己那 1/3 的子任务**。3 路并行因子 2.64× 是真实的，但被"每 agent 自己的 wall time 仍长于 BARE 整题"完全吃掉。**简单题延迟膨胀 6–8×（每 agent 的 ≈ 6 分钟最少 turn 循环 vs BARE 1 分钟整题），难题延迟膨胀 1.3–1.5×（任务被切小后单 agent 的 turn 数减少，膨胀比缩小）**。要兑现并行收益，必须把"协调走 LLM"换成"协调走系统"，把"每 agent 共享全 context"换成"context 隔离"。

---

## 四个问题串起来的整体结论

1. **WideSearch 评分机制极不容错**：列名严格匹配 + 0/1 SR，导致"答对内容但写错列名"= 0 分，"漏 1 行"= 0 分。
2. **BARE 与 HDMAS_3a 的 SR=0 题里 60%+ 是 "差一点点"**（f1 ≥ 0.75），不是不会做。瓶颈是 *最后一公里完整性*，不是检索能力。
3. **8agent 在零容错 benchmark 上反而比 3agent 差** —— 多出来的 agent 没增加"找全答案"的能力，只增加了"在传递中改写已正确答案"的方差。
4. **HDMAS_3a 的并行架构在时间上反而比单线程 BARE 慢 1.5–8×**：**任务分工实际生效了**（95% 题 3 agent 各拿一段子任务），并行因子 2.64× 也接近完美。**真正瓶颈是 "每 turn 的协议开销"**：每个 agent 在每个 turn 都要重读完整 blackboard context（让 LLM round trip 比 BARE 慢 2–3×）+ 走 LLM tool_call 加锁/解锁/投票（每次 10–60s）+ 经历 20+ 次这样的 turn 才能完成自己那 1/3 子任务，最终单 agent 的 wall time 仍长于 BARE 整题时间。简单题尤其严重（地板效应 6–8×）。
5. **最便宜的得分提升路径**：
   - 修评测器列严格匹配 / 加 schema 容错 → +5 pt（涉及 WideSearch 仓库）
   - 修 HDMAS "完成但 response 空" 的 5 题 wiring → +2.5 pt
   - prompt 里加"列名必须严格等于 X，不能多不能少不能翻译" → +3 pt
6. **架构方向性建议**：
   - **得分维度**：保持 3agent 主链路（已证明最佳），把多出来的角色用作 **"只回报、不修改最终答案"** 的 read-only verifier/searcher（Claude Code 模式），而不是写权限 agent。
   - **时间维度**：分工本身没问题（已生效），瓶颈是协议开销。三个修复方向：(a) **Context 隔离**——每个 agent 只看自己 sub-task 切片，不共读全 blackboard；(b) **系统级加锁**——agent 写 blackboard 时框架自动 lock，LLM 不感知（消掉 33 次 LLM round trip）；(c) **progress-based 早停**——`task_log` 全 done + `answer/` 非空就立即终止剩余 agent，不等 vote quorum。如果三个都做不了，**直接降到 1 agent（即 BARE）反而最快**。
