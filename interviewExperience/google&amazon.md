<path>/mnt/workspace/7d140057-0015-47b8-b970-c5efbf9d99f7/outputs/小红书_Google_Amazon_SDE_面经汇总_近6个月.md</path>
<type>file</type>
<content>
1: # 小红书 Google / Amazon SDE 面经汇总（近 6 个月）
2: 
3: > 数据来源：小红书 web 搜索结果，关键词 `google sde 面经` / `amazon sde 面经` / `亚麻 sde 面经`
4: > 收录时间窗：2025-12-25 ~ 2026-06-25（按发布日期）
5: > 整理时间：2026-06-25
6: 
7: 每条均附原文出处链接，建议直接收藏对应小红书笔记原贴以备查。
8: 
9: ---
10: 
11: ## 一、Google SDE 面经
12: 
13: ### G1. Google SDE 面试凉经（Phone Screen + Onsite 4 轮）
14: - **作者 / 日期**：青柠布丁 / 2026-04-20
15: - **流程**：Phone Screen (Coding) → Onsite Coding ×3 → Onsite Culture & Behavioural ×1
16: - **LeetCode 题目**：
17:   - Phone Screen：**打家劫舍**（House Robber）变种
18:   - Onsite #1：**课程表**（Course Schedule）变种
19:   - Onsite #2：用**字典树（Trie）实现文件系统**的增删查改
20:   - Onsite #3：**Bulls and Cows** 进阶版
21: - **BQ 方向**：Why Google、Leadership、Teamwork、Problem Solving、Innovation —— 每个维度准备 1 个亲历小故事
22: - **结论 / 经验**：
23:   - 不考原题，题目都经过包装；
24:   - 高度重视 OOP（先算法 → 再设计类封装算法）；
25:   - 每题结束都会被问时空复杂度；
26:   - Coding 难度以 Medium 为主，但 Follow-up 难度较大；
27:   - 凉在 Team Match（HC 通过但没匹配到组）。
28: - **出处**：https://www.xiaohongshu.com/explore/69e6083e00000000220258fe?xsec_token=ABlIUpaznGKXFG1JcNV6YJ3kmGD-Xv08yifxtWkZiKNGQ=
29: 
30: ---
31: 
32: ### G2. Google NG SDE TL + 面经（VO1 + Onsite）
33: - **作者 / 日期**：小红薯69AB57CA / 2026-03-06
34: - **Timeline**：10 月底投递（有内推）→ 11 月中 OA → 12 月中 VO1 → 2 月初 Onsite → 2 周后 HC pass → TM
35: - **题目**：
36:   - **VO1 Tech**：轻 OOD，实现一个 LLM Model：`init(corpus)` + `predict(word)`（返回语料中该 word 后面出现最多的词）。Follow-up：按概率输出。
37:   - **Onsite #1**：实现 song shuffle，要求同一 artist 的歌 shuffle 后不能连续。
38:   - **Onsite #2**：实现 SuperStack（pop / push / sum / `inc(k, index)` 给 0~index 的元素都加 k）。Follow-up：要求所有操作 O(1)。
39: - **BQ**：自我介绍、difficulty、conflict、fail to catch ddl、团队协作的假设场景题。
40: - **总结**：Google 面试官多次强调 efficiency 不重要，沟通和 clarify 才是重点。
41: - **出处**：https://www.xiaohongshu.com/explore/69ab53cc00000000290339b2?xsec_token=ABNdqqMWEA4cKow3pC5YqGGLBwxAO2rcYCSKlC7TYT9Vk=
42: 
43: ---
44: 
45: ### G3. Google SDE 26NG 过经（R1 干货）
46: - **作者 / 日期**：爱喝冰美式 / 2026-02-28
47: - **Timeline**：9/30 开岗当天投递 → 11/16 OA → 1/6 R1 → 1/8 R1 通过 → 1/15 Visa Call → 2/4 R2 Onsite（湾区）→ 2/24 进入 TM
48: - **R1 Coding**：**设计餐厅 waitlist**（高频题）
49: - **R1 BQ（45 分钟，高强度）**：
50:   - tight deadline
51:   - too many work
52:   - a failure
53:   - work with colleagues who usually WFH
54:   - 如何应对项目优先级频繁变化
55:   - good characteristics of a manager
56:   - initiate a project / feature
57:   - a change to your initial proposal
58: - **Tips**：先讲暴力解 + 时空复杂度 → 再讲优化思路 → 写代码加注释；BQ 答案要补足细节，否则会被连环追问。
59: - **出处**：https://www.xiaohongshu.com/explore/69a3a938000000001d0279b8?xsec_token=ABLQM6Z3XZ8J36swcqQrMLGP9FxI6UAJ2LosaiEt9faE4=
60: 
61: ---
62: 
63: ### G4. Google 26NG SDE VO 三轮
64: - **作者 / 日期**：我们不生产代码 / 2026-05-19
65: - **BQ 高频题（同 G3 高度重叠）**：tight deadline、too many work、failure、WFH 同事、优先级变更、好 manager 的特质、initiate 项目、proposal 变更
66: - **经验**：刷题量 500+，重点放沟通；先讲暴力 → 复杂度 → 优化思路 → 确认 → 写代码 + 注释。
67: - **出处**：https://www.xiaohongshu.com/explore/6a0c2bdd0000000038037e3d?xsec_token=ABtyympDgroSscL9YdQftQDK8cN-BUkFbTy4VCPfUgz30=
68: 
69: ---
70: 
71: ### G5. Google 26NG SDE 过经 + Timeline
72: - **作者 / 日期**：Lucas_oi / 2026-03-30
73: - **Timeline**：10/02 投（无内推）→ 11/26 OA → 12/12 R1 → 12/19 通过 → 2/06 R2 Onsite（NYC）→ 3/03 Visa Check → 3/23 TM
74: - **题目**：
75:   - **R1 Coding**：**OO Design + 找超时活动 ID**。Log 文件未排序时 O(n log n)，排序好则 O(n)。
76:   - **R2 Coding #1**：**Rotate Matrix 变体**（n × m），Follow-up 自己提 O(1) Space。
77:   - **R2 Coding #2**：「尔伞散其」（应为某 Greedy 题），O(n) 贪心解，全程 line-by-line 边写边讲，无 follow-up。
78: - **R1 BQ**：地里准备即可。
79: - **出处**：https://www.xiaohongshu.com/explore/69ca4ac20000000023013a2f?xsec_token=ABQ-LEFUctIq2PQR2nYuyUZT4RI6zvTb5NkGSd97j14VM=
80: 
81: ---
82: 
83: ### G6. 2026 Google NG TL + 完整面经
84: - **作者 / 日期**：🤔 / 2026-03-12
85: - **Timeline**：9/30 内推投递 → 11/19 HR Reachout → 12/16 R1 BQ+Coding → 12/30 R1 Pass → 1/28 R2 MTV Onsite → 2/23 TM → 3/12 Verbal Offer
86: - **R1 BQ**：
87:   1. 你给团队带来过什么正面影响
88:   2. 你在 fix 一个项目时另一个项目又出问题，怎么处理
89: - **R1 Coding**：
90:   1. **Number of Different Square Islands**
91:   2. LeetCode **一流其三 / 单调栈**类
92: - **R2 Coding #1**：四 part 的「两幅手牌比大小」设计题（先比最大牌 → 平局比次大 → 引入新数值字符 → 比最大牌频率），重点考察数据结构 trade-off + 自己设计 testcase。
93: - **R2 Coding #2**：一排 heights + sorted index list of fountains，fountain 会淹没低于自身 height 的格子但不能越过 ≥ 自身的，返回淹没 bitmask。
94: - **出处**：https://www.xiaohongshu.com/explore/6998cde6000000002800b5dc?xsec_token=AB1afzoWRG5EFuJG4DR-uf0vsqVn5IUELtIecUPZeHI5k=
95: 
96: ---
97: 
98: ### G7. Google SWE 26NG R2 Onsite 面经
99: - **作者 / 日期**：stella / 2026-02-11
100: - **R2 #1**：给定一棵只知道 parent 的树，设计 `getRandomNode` + `createNode`。Follow-up：`getRandomLeafNode`、`remove`。
101: - **R2 #2**：设计 `SecureLinkedList`，每个 Node 的 hash 由自身 value + 后一个节点 hash 决定（hash function 已给）。要求队首新增 Node + 验证整条 chain hash 合法。
102: - **出处**：https://www.xiaohongshu.com/explore/698d4c87000000001d012d2a?xsec_token=AByej2pvM6NMgEcPwBUYqwb0yOf9w0qifaCrtrfMjNAeQ=
103: 
104: ---
105: 
106: ### G8. Google 26NG R2 挂经 — 文件与指令级联故障
107: - **作者 / 日期**：momo / 2026-02-10
108: - **题目**：「Doc & Query Collapse」——
109:   - 系统中有 Document 和 Query，一对多双向包含。
110:   - 初始一部分 Query 损坏；包含损坏 Query 的 Doc 损坏；Doc 损坏导致其内 Query 全部损坏；级联传播。
111:   - 求最终所有损坏的 Document。
112: - **思路**：构建两个 hashmap（Doc→Queries、Query→Docs），BFS / 并查集。
113: - **出处**：https://www.xiaohongshu.com/explore/698c0bb70000000016008157?xsec_token=ABQOB725kenhOd2LSPPOSsdggrEPP3JN_z9yYp7y94R14=
114: 
115: ---
116: 
117: ### G9. Google 26NG R2 挂经（屋顶修补题）
118: - **作者 / 日期**：zzzzzz / 2026-02-06
119: - **Timeline**：11/10 OA → 12/16 R1 → 12/17 R1 过 → 1/21 R2 → 2/5 挂
120: - **R2 #1**：输入两数组 + k，处理 list2 让它前 k 个元素与 list1 前 k 个无重复，返回 list2。
121: - **R2 #2**：m×n 数组表示屋顶，1 是好的、0 是漏洞，允许 1×m 或 1×n 木板修补，求最少木板数。**答案：二分图匹配 / 最小点覆盖**。
122: - **出处**：https://www.xiaohongshu.com/explore/6986b8390000000028020b32?xsec_token=ABXpFwcNYYQl7lrKYHs_6GknIXAytOKGrfJolnyXawtBs=
123: 
124: ---
125: 
126: ### G10. 12.11 Google SDE VO 面经（BQ + 技术）
127: - **作者 / 日期**：oa vo辅助 / 2025-12-11
128: - **R1 BQ**：
129:   1. Google 技术文化最吸引你的地方？
130:   2. 你 lead 过的 一个对业务有 significant positive impact 的技术决策？
131:   3. 不同背景成员工作风格差异如何协调？
132: - **R2 Coding**：
133:   1. **Easy 热身**：判断二叉树是否平衡（后序递归）。
134:   2. **Medium**：最长公共子序列长度 + Follow-up 输出具体子序列（反向回溯 dp 表）。
135: - **出处**：https://www.xiaohongshu.com/explore/693a7435000000000d034c28?xsec_token=ABg5lBdmqZnHZ-M3xFyRBgQkk324uoabALQBxChQmuvNg=
136: 
137: ---
138: 
139: ### G11. Google 美国 2026 上半年面经
140: - **作者 / 日期**：OooOoo / 2026-06-15
141: - **Coding**：
142:   - **线上**：2D points + 半径 r 的 **clustering** 题，本质 connected components（DFS / BFS / Union-Find）。
143:   - **Onsite #1（数组三连击）**：
144:     1. 数字 n 在数组中最长连续出现长度
145:     2. 给目标数组 `[n,m,k]`，返回每个数字最长连续次数
146:     3. **滑动窗口**：最多改 k 个为 n，n 最长连续多少次
147:   - **Onsite #2（广告轮播 / 调度）**：
148:     1. 设计 `next()`，多广告各有展示次数，尽量轮流
149:     2. 加 cooldown，每个广告展示后需等冷却时间
150: - **BQ（高度发散）**：
151:   - 和工作风格差异极大的人合作
152:   - 你从对方身上学到了什么
153:   - 同事不努力 / WLB 差，作为 IC 怎么改善？
154:   - 推动协作而不只是自己干完的方法
155:   - 作为 IC 会 involve 哪些 stakeholder？
156:   - 假如你是 senior director 会怎么做？
157:   - Review Photos 检测 smiling faces 怎么确保对不同用户都 works well？（metrics / FP / FN / 子人群表现差怎么办）
158:   - manager 没给步骤的项目，怎么 break down 下一步？
159: - **出处**：https://www.xiaohongshu.com/explore/6a3011480000000015025a0c?xsec_token=ABnUfwLvdd2OFROCXcWN9KlfS1wxshmtD0Sn-frKWuTw4=
160: 
161: ---
162: 
163: ### G12. Google 26NG 挂经解析（基础 / 推演踩雷点）
164: - **作者 / 日期**：利维坦 / 2025-11-30
165: - **题目**：贪心算法 O(n log n) 题
166: - **挂的原因（非常值得借鉴）**：
167:   - 基础概念混乱：把单调递减序列说成 Prefix Sum 原理 → 面试官判定为「背题」；
168:   - 逻辑推演弱：代码里有 dead code 但靠试数才发现 → 暴露写代码时逻辑不清；
169: - **建议**：写完 dry run 自己走一遍；不懂别强答；NG 重点考思维与表达。
170: - **出处**：https://www.xiaohongshu.com/explore/692cafba000000000d00f035?xsec_token=ABeB4hJBAW8lmJBqWpQgAYpjjeI-F7axrpr-FiLiE4o3A=
171: 
172: ---
173: 
174: ### G13. Google Round 1 面经
175: - **作者 / 日期**：stella / 2026-01-07
176: - **Coding**：m×n 数组（不同高度），找从 (0,0) → (m-1, n-1) 的路径使路径最大高度最小。
177:   - 解法：**Dijkstra**。Follow-up：能否 DFS？时间复杂度？
178: - **BQ（40 min）**：
179:   - 队友抢功劳怎么办
180:   - 跟难相处的人打交道
181:   - Multitask 经历
182:   - 面对不合理需求
183:   - 在 low culture 公司怎么办
184: - **出处**：https://www.xiaohongshu.com/explore/695ebb6c000000002102a31e?xsec_token=ABGrLvZ2t0vREK7mEGoR56slLnw7o0q_gyemKEylPv_So=
185: 
186: ---
187: 
188: ### G14. 谷歌 26NG R1（这次先 BQ 再 Coding）
189: - **作者 / 日期**：昨日下雨 / 2026-04-26
190: - **BQ**：常规（怎么帮助同事 / 挑战性项目 / 加入 Google 想做什么）+ 非常规（工作外消遣、爱好）
191: - **Coding**：**合并有序数组**（两个已排序数组合并到第一个，从后往前比）。Follow-up：第一个数组空间不够怎么办？→ 建新数组 / 挪位置。
192: - **出处**：https://www.xiaohongshu.com/explore/69cfd001000000001a02c8b9?xsec_token=AB0NmB_3g-KTqYi2Tob-mt3Y_-4iZSLoeNeYGzEVQx5CQ=
193: 
194: ---
195: 
196: ## 二、Amazon SDE 面经
197: 
198: ### A1. Amazon 26 SDE Intern Timeline + 面经（Offer）
199: - **作者 / 日期**：momo / 2026-04-03
200: - **Timeline**：1/18 投 → 3/02 OA → 3/23 VO1 → 3/25 VO2 → 3/27 Offer
201: - **VO1**（30 min BQ + 30 min Coding）：BQ 被连环追问至少 5 题，包含今年新增的 **GenAI 相关问题**；Coding 是常规 **DFS 原题变体**，面试官全程引导改 bug，最后问时空复杂度。
202: - **VO2**（55 min BQ + 5 min Coding）：以 **proudest project + 如何使用 GenAI** 为主线，被打断追问 thesis / 项目 / 大模型八股 / AI 课程；Coding 是 hashmap easy 原题口述 + medium follow-up。
203: - **结论**：组招后题型方差变大，但 BQ + communication + 有眼缘仍是关键。
204: - **出处**：https://www.xiaohongshu.com/explore/69c8534c000000002903e5c0?xsec_token=ABtPtx2BR4OgIhAMTuLUsBw9p4B3S6yXFSQs314b1bJpM=
205: 
206: ---
207: 
208: ### A2. Amazon SDE 26 Summer Intern 面经
209: - **作者 / 日期**：不存在bug / 2026-02-03
210: - **Timeline**：12/13 OA → 1/27 VO（back-to-back 2 轮）→ 周一 Offer
211: - **OA**：HackerRank 两道 medium。
212: - **VO 格式**：每轮 2 BQ + follow-up + 1 Coding，难度 medium-easy。
213: - **Round 1 Coding**：给数组求**幂集**（subsets）。
214: - **BQ**：problem solving、deadline 类。
215: - **Note**：今年部分组把 Coding 换成 **OOD**。
216: - **出处**：https://www.xiaohongshu.com/explore/69821e290000000022023e5f?xsec_token=ABGB9NXIAU014L4etIQ60NfCFE78wvdEAULkhmHv65Zng=
217: 
218: ---
219: 
220: ### A3. 🇺🇸 2026 first Amazon NG SDE1 Offer
221: - **作者 / 日期**：Isisisitch / 2026-01-14
222: - **OA**：
223:   - Q1 **Robotic system**（近期高频）
224:   - Q2 **EC2 machine type**
225: - **VO**：
226:   - **#1 BQ**：get out of comfort zone、made mistake、personal project discussion
227:   - **#2 BQ**：have conflicts with others、bad decision；Coding：**K nearest neighbors**
228:   - **#3 BQ**：dive deep、negative feedback；**OOD（新难题）**：**Amazon product event router**（难度较大，未提前准备很难做出）
229: - **出处**：https://www.xiaohongshu.com/explore/69685efd000000002200b9c8?xsec_token=ABqoSgFheu_9ztS3LI0zRcK5WsdB3kNB3PiW1gNfx2DNY=
230: 
231: ---
232: 
233: ### A4. Amazon SDE Intern (AWS) S26 面经
234: - **作者 / 日期**：Jiming / 2026-02-14
235: - **Timeline**：10 月 OA → 2026/1 月被捞做 FR → 02/11 back-to-back（senior dev + manager）→ 02/12 拒
236: - **Manager 轮**：BQ + 简单 Coding；问 Amazon Principles 经验；**GenAI 题**：不是问用什么工具而是**怎么 verify + risk control**。
237: - **Senior Dev 轮**：Coding 难度低于 LC；重点考 clarify、edge cases、先 working 再 trade-off。
238: - **教训**：
239:   - Syntax 卡壳会扣分；
240:   - BQ 必须对齐 **LP**，准备 **6-8 个 STAR 故事**；
241:   - GenAI 相关讲清楚 verify / 测试 / 人工 review / risk 控制。
242: - **出处**：https://www.xiaohongshu.com/explore/698ee47b00000000150397d7?xsec_token=ABy8GRGQuaJ9N8rgajQ8qveYxAtU7_Alh7ENQrp5wF4RY=
243: 
244: ---
245: 
246: ### A5. Amazon 26 Summer SDE Intern TL（Offer）
247: - **作者 / 日期**：whi s per / 2026-05-04
248: - **Timeline**：开岗当天投 → 12/12 OA 邀请 → 12/19 OA pass → 3/16 VO1 → 3/17 VO2 → 3/24 Offer
249: - **格式**：两轮 online VO，都是印度面试官，**全部是 tag 题**（去地里搜 tag 题命中率高）。
250:   - **VO1**：HM 主持，2 LC medium + 1 BQ with 3 follow-ups
251:   - **VO2**：1 BQ with 3 follow-ups + 1 LC easy + 1 LC medium
252: - **Note**：portal 一直显示 "no longer under consideration" 也可能最终拿 offer，别慌。
253: - **出处**：https://www.xiaohongshu.com/explore/69d5e32b000000002102d5c1?xsec_token=ABq0Fb_v_W5pQ6zjoL_qmsoYUsICfntzJUjvinuVw7UHU=
254: 
255: ---
256: 
257: ### A6. Amazon SDE Intern 过经
258: - **作者 / 日期**：HiBill / 2026-06-02
259: - **BQ**：tight ddl、harsh feedback、dive deep + tight deadline / conflict
260: - **Coding**：**Compare Version Numbers** 变式
261: - **OA Tips**：OA 一般是 2 道 medium，90 分钟，**刷他们家真题极易撞原题**。
262: - **重点**：**Work Simulation / 情景题（LP 决策模拟）** 比纯 Coding 更被强调，BQ 必须 6-8 个 STAR 故事对齐 LP。
263: - **出处**：https://www.xiaohongshu.com/explore/6a1e8d0300000000080024d2?xsec_token=AB2EahATxEz8ookCKHie1ElOxB6VctUX-UPqxLNMnf3XY=
264: 
265: ---
266: 
267: ### A7. Amazon SDE NG 2.5h 大 OA
268: - **作者 / 日期**：心碎版椰 / 2026-04-17
269: - **内容**：NG OA 升级为 2.5 小时，包含 **AI Coding + Work Simulation**（楼主未细说题型，仅求助）。
270: - **出处**：https://www.xiaohongshu.com/explore/69e28d55000000001a02bae9?xsec_token=ABU1mY-tsQagZiAGi_LfUIPZ9dEOpJ5wUu0azvDBoQa4c=
271: 
272: ---
273: 
274: ### A8. AMZ SDE Intern Onsite Timeline
275: - **作者 / 日期**：juju / 2026-03-23
276: - **Timeline**：11 月中 OA → 1 月中 DB 组 Survey（没匹配上）→ 2 月中约面 → 2/27 b2b Onsite（BQ 聊嗨、LC 较简单）→ 3/3 pre-offer survey → 3/5 official offer
277: - **组**：AWS SageMaker
278: - **出处**：https://www.xiaohongshu.com/explore/69a9feee000000001a036acd?xsec_token=ABpUzqe0KDWpofwzbaUODJx8YqcKCJat5aQSFcR9asM-I=
279: 
280: ---
281: 
282: ### A9. Amazon SDE Intern 第一个面试就是 VO
283: - **作者 / 日期**：爷又有号了 / 2026-03-26
284: - **内容**：本人求助贴，没有具体题目；提醒一点：今年部分组 **跳过 OA 直接发 VO**。
285: - **出处**：https://www.xiaohongshu.com/explore/69c5ab42000000001d01ae12?xsec_token=ABxMp3fGN1VRw2nDqWDWWIfGYKs0Xti8XrS38f-HLncG8=
286: 
287: ---
288: 
289: ### A10. Amazon SDE Intern 四次保温挂
290: - **作者 / 日期**：Yvon / 2026-05-07
291: - **Timeline**：11/13 投 → 3/10 OA → 3/15 提交 → 3/17 保温 → 4/6 / 4/15 / 4/22 再三保温 → 5/8 夏季招聘终止
292: - **OA 题（比看到的都简单，核心代码模式）**：
293:   1. **贪心**：服务器配对容量最大化
294:   2. **差分数组**：对任意连续子数组 += x（正整数），使最终数组非递减，最小化所有 x 之和
295: - **出处**：https://www.xiaohongshu.com/explore/69c4ab3f00000000200387c1?xsec_token=AB_Ma5nyujUhnET7DVFwOkBTE-OVaoWshiet55KEEizdI=
296: 
297: ---
298: 
299: ### A11. Amazon SDE Return Offer Timeline
300: - **作者 / 日期**：不明汦 / 2026-02-02
301: - **完整时间线**：2024/12/13 Intern OA → 2025/1/22 Intern VO → 2025/1/30 OC → 5/27 实习开始 → 8/15 实习结束 → 2026/1/17 **Full-time Return Offer**
302: - **备注**：原组无 HC 时会进 org 大池子，建议 day 1 转组。
303: - **出处**：https://www.xiaohongshu.com/explore/6980e009000000000c035358?xsec_token=ABv4rLQiReP8Z-jzYYA0SAdQ1tnUMnUhHx66uFjSGofWc=
304: 
305: ---
306: 
307: ### A12. 亚麻 SDE1 OA（求助贴）
308: - **作者 / 日期**：北极限量白鲟 / 2026-02-05
309: - **内容**：求助贴，无题目细节，仅证明 2026 年 2 月仍有 SDE1 社招 OA 发放。
310: - **出处**：https://www.xiaohongshu.com/explore/6984eb67000000002202ecd4?xsec_token=ABmATMwDodniYT908vrE3fdbqI1g4Nx3rc9RP0e8cnmgM=
311: 
312: ---
313: 
314: ## 三、共性观察 & 通关建议
315: 
316: ### Google
317: - **流程**：OA（NG 才有） → R1（Coding + BQ，BQ 可能在前也可能在后，约 45 min）→ R2 / Onsite（2~3 轮 Coding，部分含 OOD）→ HC → Team Match → Offer。
318: - **题型**：以 LeetCode Medium 包装题为主，**Follow-up 决定分数**；常见模式「先算法 → 再封装成类」，OOP 重要性高。
319: - **沟通**：clarify、think out loud、复杂度分析、dry run；面试官多次明示「efficiency 不是关键」。
320: - **BQ 高频清单**：
321:   - Why Google
322:   - tight deadline / too much work
323:   - a failure / made mistake
324:   - 不同背景 / 工作风格的协作（WFH、跨地区）
325:   - 项目优先级频繁变更
326:   - 你 lead 的有业务影响的技术决策
327:   - good characteristics of a manager
328:   - initiate a project / feature
329:   - 修改 initial proposal 的经历
330:   - 在 low culture / 队友不努力的环境怎么改进
331:   - 假如你是 senior director / 更大权力会怎么做
332: 
333: ### Amazon
334: - **流程**：OA（HackerRank，2 题 medium，**强烈建议刷真题**，原题命中率高；NG 的「大 OA」2.5h 含 AI Coding + Work Simulation）→ VO 2~3 轮 back-to-back。
335: - **每轮格式**：2 BQ + 3 follow-up + 1 Coding（部分组改为 OOD）。
336: - **Coding 难度**：低于 LC，重点在 clarify、edge case、trade-off。常见原题：**幂集 / DFS 变体 / Compare Version Number / KNN / 合并区间**。
337: - **OOD 高频**：**Product Event Router**（新难题）、餐厅/系统设计类。
338: - **BQ 必须对齐 LP（Leadership Principles），准备 6-8 个 STAR 故事**：tight deadline、harsh feedback、dive deep、bad decision、conflict、get out of comfort zone、proudest project、GenAI 使用 + verify + risk control（**2026 新增重点**）。
339: 
340: ### 共同注意事项
341: - 别 syntax 卡壳；
342: - 写代码时多注释 + 边写边讲；
343: - 写完务必 dry run（避免 dead code、逻辑 bug）；
344: - BQ 答案补足细节，否则会被连环追问；
345: - 不会就大白话 clarify，**最忌张冠李戴的「背题感」**。
346: 
347: ---
348: 
349: *本文档由 BrowserCode 自动从小红书搜索结果整理。每条均带原贴 xsec_token 链接，登录后小红书账号可直接打开。建议在小红书 App 内对各原贴执行「收藏」以长期保存。*

(End of file - total 349 lines)
</content>