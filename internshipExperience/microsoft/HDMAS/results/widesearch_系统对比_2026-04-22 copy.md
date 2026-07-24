# WideSearch 系统对比：HDMAS vs BARE COPILOT vs Leaderboard

> 对比日期：2026-04-22（v3，HDMAS_COPILOT_8a 的 ZH 已补全 100/100）
> 数据集：WideSearch (200 题，en 100 + zh 100)
> 度量：均为 Avg@1，leaderboard 是 Avg@4，**不严格可比**，仅作量级参考

## 系统与数据可用性

| 系统 | 路径 | eval | parse_ok | EN | ZH | 备注 |
|---|---|---|---|---|---|---|
| **BARE_COPILOT** | `COPILOT_FOR_Widesearch/results/test_0416_bare_en50` | 200 | 170 | 100 | 100 | 单 agent baseline |
| **HDMAS_COPILOT_3a** | `HDMAS_COPILOT/batch_results/test_0416_copilot_en50_3agents` | 200 | 179 | 100 | 100 | 3-agent |
| **HDMAS_COPILOT_8a** | `HDMAS_COPILOT/batch_results/test_0417_copilot_en100_8agents` | 200 | 192 | 100 | 100 | 8-agent（ZH 已补全 100/100） |
| **HDMAS_v4_full** | `HDMAS_v4/batch_results/test_0413_full` | 200 | 195 | 100 | 100 | v4，gpt-5.4 主模型 |

> "parse_ok" = 生成了 `*_eval_result.csv`（输出能解析为表格）。

---

## 一、原始对比（universe = 200，缺失补 0）

| System | n | miss | SR | Row-F1 | **Item-F1** |
|---|---|---|---|---|---|
| **HDMAS_COPILOT_8a** | 200 | 0 | 0.090 | **0.591** | **0.781** |
| **HDMAS_COPILOT_3a** | 200 | 0 | **0.125** | 0.556 | 0.733 |
| HDMAS_v4_full | 200 | 0 | 0.080 | 0.481 | 0.690 |
| BARE_COPILOT | 200 | 0 | 0.115 | 0.499 | 0.679 |

8a 现已跑完全部 200 题：**全集 Row-F1 (0.591) 与 Item-F1 (0.781) 均为四家最高**，但 SR (0.090) 低于 3a/BARE——即“细而不全”在全集口径下同样成立（字段抽取最全，但整表完全正确的比例偏低）。

### EN（n=100，所有系统都已跑完，公平对比）

| System | SR | Row-F1 | **Item-F1** |
|---|---|---|---|
| HDMAS_COPILOT_3a | **0.140** | **0.532** | 0.753 |
| BARE_COPILOT | **0.140** | 0.509 | 0.741 |
| HDMAS_v4_full | 0.130 | 0.510 | 0.736 |
| **HDMAS_COPILOT_8a** | 0.110 | 0.523 | **0.766** |

**反直觉**：8a 的 Item-F1 最高（+1.3 pt vs 3a），但 SR 最低（-3.0 pt vs 3a）——agent 越多越细，但整体完整度反而掉。

### ZH（n=100，四家均已跑完）

| System | SR | Row-F1 | Item-F1 |
|---|---|---|---|
| **HDMAS_COPILOT_3a** | **0.110** | 0.581 | 0.714 |
| BARE_COPILOT | 0.090 | 0.490 | 0.617 |
| **HDMAS_COPILOT_8a** | 0.070 | **0.658** | **0.797** |
| HDMAS_v4_full | 0.030 | 0.452 | 0.645 |

HDMAS_v4 的 ZH SR 仅 0.030，是 3a 的 1/3.7、BARE 的 1/3。8a 的 ZH 与 EN 同样“细而不全”：Row-F1 (0.658) / Item-F1 (0.797) 四家最高，但 SR (0.070) 仍低于 3a/BARE。

---

## 二、排除"无答案"样本

### 视角 A：每个系统排除自己的解析失败样本

| System | n | SR | Row-F1 | Item-F1 |
|---|---|---|---|---|
| **HDMAS_COPILOT_3a** | 179 | **0.140** | **0.621** | **0.820** |
| HDMAS_COPILOT_8a | 192 | 0.094 | 0.616 | 0.814 |
| BARE_COPILOT | 170 | 0.135 | 0.588 | 0.798 |
| HDMAS_v4_full | 195 | 0.082 | 0.493 | 0.708 |

#### EN

| System | n | SR | Row-F1 | Item-F1 |
|---|---|---|---|---|
| BARE_COPILOT | 93 | **0.151** | 0.548 | 0.796 |
| HDMAS_COPILOT_3a | 94 | 0.149 | **0.566** | 0.801 |
| HDMAS_v4_full | 97 | 0.134 | 0.526 | 0.758 |
| HDMAS_COPILOT_8a | 95 | 0.116 | 0.551 | **0.806** |

#### ZH

| System | n | SR | Row-F1 | Item-F1 |
|---|---|---|---|---|
| **HDMAS_COPILOT_3a** | 85 | **0.129** | **0.683** | **0.840** |
| BARE_COPILOT | 77 | 0.117 | 0.636 | 0.801 |
| HDMAS_COPILOT_8a | 97 | 0.072 | 0.679 | 0.821 |
| HDMAS_v4_full | 98 | 0.031 | 0.461 | 0.658 |

> 注：8a 早前 ZH 仅 23 题解析成功时 Row/Item-F1 虚高（**0.749/0.832**，样本太小）；补全到 97 题后回落至 0.679/0.821，3a 重新为 ZH 最高。

### 视角 B：四家全部成功输出的严格交集（n=107，EN 88 + ZH 19）

> ⚠️ 本节交集在 8a 的 ZH 仅 23 题解析成功时计算（ZH 交集被 8a 卡在 n=19）。8a 现已补全（ZH parse_ok=97），**严格交集需重算**，ZH 交集样本量会显著变大；下方数字为旧版，待重跑四家交集后更新。

#### 总体（n=107）

| System | SR | Row-F1 | Item-F1 |
|---|---|---|---|
| **HDMAS_COPILOT_3a** | **0.159** | 0.609 | 0.827 |
| HDMAS_COPILOT_8a | 0.112 | **0.619** | **0.833** |
| BARE_COPILOT | 0.140 | 0.605 | 0.824 |
| HDMAS_v4_full | 0.112 | 0.545 | 0.764 |

#### EN（n=88）

| System | SR | Row-F1 | Item-F1 |
|---|---|---|---|
| **HDMAS_COPILOT_3a** | **0.159** | 0.573 | 0.812 |
| BARE_COPILOT | 0.148 | 0.565 | 0.810 |
| HDMAS_v4_full | 0.136 | 0.542 | 0.767 |
| HDMAS_COPILOT_8a | 0.125 | **0.579** | **0.823** |

#### ZH（n=19，样本太小仅供参考）

| System | SR | Row-F1 | Item-F1 |
|---|---|---|---|
| **HDMAS_COPILOT_3a** | **0.158** | 0.774 | **0.896** |
| BARE_COPILOT | 0.105 | 0.791 | 0.886 |
| HDMAS_COPILOT_8a | 0.053 | **0.805** | 0.879 |
| HDMAS_v4_full | 0.000 | 0.558 | 0.749 |

---

## 三、Leaderboard 对照（量级参考，Avg@4 vs 我们 Avg@1）

> 数据源：[WideSearch 官方 leaderboard](https://widesearch-seed.github.io/#leaderboard)
> 官方报告 Avg@4 / Pass@4，**我们只跑了 Avg@1**，下面对比仅作量级参考。

### 3.1 与 Multi-Agent 赛道 Avg@4 对比

| Rank | System | SR | Row-F1 | **Item-F1** |
|---|---|---|---|---|
| 🥇 ours | **HDMAS_COPILOT_3a** *(Avg@1)* | **12.5** | **55.6** | **73.3** |
| 🥈 ours | BARE_COPILOT *(Avg@1)* | 11.5 | 49.9 | 67.9 |
| 🥉 ours | HDMAS_v4_full *(Avg@1)* | 8.0 | 48.1 | 69.0 |
| 1 | OpenAI o3 MA | 5.1 | 37.8 | 57.3 |
| 2 | Claude Sonnet 4 (Thinking) MA | 3.6 | 38.5 | 62.2 |
| 3 | Kimi K2 MA | 3.0 | 36.2 | 61.2 |
| 4 | Gemini 2.5 Pro MA | 2.0 | 33.5 | 57.4 |
| 5 | Doubao-1.6 MA | 2.5 | 34.0 | 54.6 |
| 6 | DeepSeek-R1 MA | 0.8 | 22.9 | 44.3 |

### 3.2 与 Single-Agent 赛道 Avg@4 对比

| System | SR | Row-F1 | Item-F1 |
|---|---|---|---|
| **BARE_COPILOT (ours, Avg@1)** | **11.5** | **49.9** | **67.9** |
| OpenAI o3 SA | 4.5 | 34.0 | 52.6 |
| Claude Sonnet 4 (Thinking) SA | 2.3 | 31.7 | 57.9 |
| Kimi K2 SA | 1.1 | 29.7 | 54.4 |
| Gemini 2.5 Pro SA | 1.5 | 30.0 | 51.0 |

### 3.3 与 Pass@4（peak capability，4 次最好那次）对比

Pass@4 是顶级模型 4 次中最好的一次表现，比 Avg@4 高得多。即使把它当我们 Avg@1 的对照：

| System | SR Pass@4 | Row-F1 Pass@4 | Item-F1 Pass@4 |
|---|---|---|---|
| **HDMAS_COPILOT_3a (ours, Avg@1)** | **12.5** | **55.6** | **73.3** |
| OpenAI o3 MA Pass@4 | 9.5 | 50.5 | 68.9 |
| Claude Sonnet 4 (Thinking) MA Pass@4 | 6.5 | 52.2 | 73.1 |
| Kimi K2 MA Pass@4 | 6.5 | 49.6 | 70.7 |

我们的 Avg@1 在 SR / Row-F1 上仍超过所有顶级模型的 Pass@4，Item-F1 与 Claude Pass@4 持平。

### 3.4 倍数对比（HDMAS_3a 相对 leaderboard 最高 MA Avg@4）

| 指标 | HDMAS_3a | 顶级 MA Avg@4 | 倍数 |
|---|---|---|---|
| SR | 12.5 | 5.1 (o3) | **2.45×** |
| Row-F1 | 55.6 | 38.5 (Claude) | **1.44×** |
| Item-F1 | 73.3 | 62.2 (Claude) | **1.18×** |

### 3.5 ⚠️ 解读警告

差距过大，**不能直接宣称"打榜"**，必须先排除以下系统性差异：

1. **评估 pipeline 一致性**
   - LLM judge 用的是什么模型？官方用 GPT-4o-mini judge？
   - 列名匹配规则、字符串归一化、数字容忍度是否一致？
   - 我们用的 eval 脚本是否就是 [ByteDance-Seed/WideSearch](https://github.com/ByteDance-Seed/WideSearch) 官方那一份？

2. **Avg@1 vs Avg@4 方差**
   - 官方 Avg@4 是 4 次平均，我们只跑 1 次
   - 单跑可能正好命中较容易的轨迹（low-hanging）；4 次平均会被难轨迹拉低
   - 结论可信前应至少跑 Avg@4

3. **底层模型差异**
   - 我们用的是 GitHub Copilot Chat 的底层模型（GPT-5.4 / 高版本 GPT-4 系），可能新于 leaderboard 中所列模型
   - leaderboard 上 OpenAI o3、Claude Sonnet 4 是 2025 中后期发布，我们的 Copilot 后端可能更强
   - 这部分差距是"模型代差"而非"架构优势"

4. **题目集是否一致**
   - 我们 200 题与官方 200 题是否完全一致？需要确认 instance_id 集合相同

### 3.6 下一步验证清单

要把"超过 leaderboard"做实，必须：

- [ ] 核对 eval 脚本与官方 commit 一致
- [ ] 至少跑 Avg@4，给出标准差
- [ ] 公开模型版本 / Copilot 后端 build
- [ ] 用同一份 eval 跑一个开源 baseline（如 Claude API + 简单 ReAct）确认评分尺度匹配

---

## 四、关键结论

### 1. HDMAS_COPILOT_3a 在 SR 上综合最强

所有口径、EN/ZH 子集、严格交集，3a 的 SR 都不弱于其它三家。（补全后 8a 在 Row-F1 / Item-F1 上全集最高，但 SR 仍以 3a 领先——见结论 2。）

### 2. **8a 出现"细而不全"现象**：agent 越多 → Item-F1 升 / SR 反降

| EN 公平对比 (n=100) | 3a | 8a | Δ |
|---|---|---|---|
| Item-F1 | 0.753 | **0.766** | **+1.3 pt** |
| Row-F1 | 0.532 | 0.523 | -0.9 pt |
| SR | **0.140** | 0.110 | **-3.0 pt** |

| 严格交集 EN (n=88) | 3a | 8a | Δ |
|---|---|---|---|
| Item-F1 | 0.812 | **0.823** | +1.1 pt |
| SR | **0.159** | 0.125 | -3.4 pt |

| ZH 公平对比 (n=100) | 3a | 8a | Δ |
|---|---|---|---|
| Item-F1 | 0.714 | **0.797** | **+8.3 pt** |
| Row-F1 | 0.581 | **0.658** | **+7.7 pt** |
| SR | **0.110** | 0.070 | -4.0 pt |

ZH 补全后，“细而不全”在 ZH **更明显**：8a 的 Item-F1 领先 3a 达 +8.3 pt，但 SR 反落 4.0 pt。

**解读**：8 个 agent 分工后字段抽取确实更精细，但**整合阶段损失了完整性**——可能的原因：
- 分工切碎后每个 agent 只看到局部，最终合并时 row 拼不齐
- 协作 overhead 消耗了步数预算，没空回头补漏
- 8 agent 并发引入更多 race condition / 重复 / 冲突

**结论：若以 SR（整表全对率）为主度量，3a 更优、可停在 3a；但若目标是字段级召回（Item-F1 / Row-F1），8a 在 EN 与 ZH 全集均为四家最高——是否加到 8a 取决于优化的度量。**

### 3. HDMAS_v4 的 EN 持平、ZH 崩盘

EN 接近其他系统，ZH SR 仅 0.030（3a 的 1/3.7）。优先修 ZH。

### 4. Multi-agent 协作的真实增量集中在 ZH

- 严格交集 EN：3a vs BARE，SR 仅 +1.1 pt
- 严格交集 ZH（n=19）：3a vs BARE，SR +5.3 pt
- 视角 A ZH：3a vs BARE，Item-F1 +3.9 pt
- **EN 上多 agent 收益微薄；ZH 上才回收成本**

### 5. 全行共同瓶颈：early-convergence

所有系统 Item-F1 ≈ 0.7-0.83 但 SR 仅 0.10-0.15——抓得到字段，凑不齐表。
对应修复方向：TodoWrite + system-reminder + verifier 那一套防早收敛机制。

### 6. ZH 解析失败率（含失败口径）

| | parse 失败 | 占比 |
|---|---|---|
| BARE | 23/100 | 23% |
| HDMAS_3a | 15/100 | 15% |
| **HDMAS_v4** | **2/100** | **2%** |

**v4 的格式可靠性其实是最好的**——但成功解析后内容质量明显不如其他系统。它的 ZH 问题不在"输出格式"，而在"内容本身"。

---

## 五、一段话总览

**HDMAS_COPILOT_3a 是当前四个系统里综合最强**，但它对 BARE 的优势在 EN 上几乎为零、在 ZH 上 +3-5 pt——多 agent 协作的成本只在中文场景被回收。**8 agent 出现明显的"细而不全"反例**：Item-F1 比 3a 还高 1-2 pt，但 SR 反而低 3 pt，agent 越多越破坏整体完整性，**3a → 8a 不值得**。**HDMAS_v4 EN 持平、ZH SR 仅 0.030**，且其 ZH 问题不在格式（格式可靠性反而最高）而在内容本身。**所有系统 Item-F1 ≈ 0.7-0.83 但 SR ≈ 0.10-0.15**——共同的天花板是 early-convergence，下一步该聚焦 TodoWrite + system-reminder + verifier 那一套防早收敛机制，而不是再扩 agent 规模。
