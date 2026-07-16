# Google 26NG SDE 面经 · Coding 题目汇总（按主题分类）

> 从 [面经.md](../面经.md) 中提取的所有 coding/system design 题目，按算法主题归类，并匹配对应的 LeetCode / 系统设计题目，便于针对性刷题。

---

## 目录

- [1. 树 / 二叉树 (Tree)](#1-树--二叉树-tree)
- [2. 滑动窗口 / 单调队列 / 数据流 (Sliding Window)](#2-滑动窗口--单调队列--数据流-sliding-window)
- [3. 回溯 (Backtracking)](#3-回溯-backtracking)
- [4. 数组 (Array)](#4-数组-array)
- [5. 字符串 / 数学 (String / Math)](#5-字符串--数学-string--math)
- [6. 前缀和 + 哈希 (Prefix Sum + Hash)](#6-前缀和--哈希-prefix-sum--hash)
- [7. 图 / 拓扑排序 (Graph / Topological Sort)](#7-图--拓扑排序-graph--topological-sort)
- [8. 贪心 / 堆 (Greedy / Heap)](#8-贪心--堆-greedy--heap)
- [9. 数据结构设计 / OOD (Design)](#9-数据结构设计--ood-design)
- [10. 位运算 / 模拟 (Bit Manipulation / Simulation)](#10-位运算--模拟-bit-manipulation--simulation)

---

## 1. 树 / 二叉树 (Tree)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 二叉树最长连续序列路径长度（父到子连续），follow up 任意方向 | [LC 298 · Binary Tree Longest Consecutive Sequence](https://leetcode.com/problems/binary-tree-longest-consecutive-sequence/) | Medium | Follow up → [LC 549 · Longest Consecutive Sequence II](https://leetcode.com/problems/binary-tree-longest-consecutive-sequence-ii/)（Medium，任意方向） |
| 二叉树叶子节点删除序列 + 拓扑排序模拟递归过程 | [LC 366 · Find Leaves of Binary Tree](https://leetcode.com/problems/find-leaves-of-binary-tree/) | Medium | 按层从叶子往上删；本质是按节点高度分组 |
| 树结构设计：getRandomNode / createNode，follow up getRandomLeafNode / remove | [LC 380 · Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) + 设计 | Medium/Hard | 结合 [LC 528 · Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/) 思路；O(1) 随机需维护数组+索引映射 |

---

## 2. 滑动窗口 / 单调队列 / 数据流 (Sliding Window)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 滑动窗口最大值（单调队列），follow up 实时数据处理 | [LC 239 · Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | Hard | Follow up 用 deque 处理流式数据 |
| 最长无重复子串（滑动窗口） | [LC 3 · Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium | 经典变长滑窗 |
| 流数据处理函数实现（滑动窗口） | [LC 346 · Moving Average from Data Stream](https://leetcode.com/problems/moving-average-from-data-stream/) | Easy | 也可扩展到 [LC 480 · Sliding Window Median](https://leetcode.com/problems/sliding-window-median/)（Hard） |

---

## 3. 回溯 (Backtracking)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 组合总和（回溯 + 剪枝），follow up 去重处理 | [LC 39 · Combination Sum](https://leetcode.com/problems/combination-sum/) | Medium | Follow up（去重）→ [LC 40 · Combination Sum II](https://leetcode.com/problems/combination-sum-ii/)（Medium） |

---

## 4. 数组 (Array)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 找数组第一个"转折点"（peak/波峰） | [LC 162 · Find Peak Element](https://leetcode.com/problems/find-peak-element/) | Medium | 二分可做到 O(log n) |
| 判断数组是否严格单调 | [LC 896 · Monotonic Array](https://leetcode.com/problems/monotonic-array/) | Easy | 注意"严格" vs "非严格"边界 |

---

## 5. 字符串 / 数学 (String / Math)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 两个十六进制字符串相加 | [LC 415 · Add Strings](https://leetcode.com/problems/add-strings/) 变体 | Easy | 进位逻辑改成 base-16 |
| 二进制字符串相加 | [LC 67 · Add Binary](https://leetcode.com/problems/add-binary/) | Easy | 直接对应 |
| 文本排版功能实现（Text Justification） | [LC 68 · Text Justification](https://leetcode.com/problems/text-justification/) | Hard | 细节多：单词分行 + 空格均分 |
| 统计小于等于 n 的素数数量（埃氏筛法），follow up 大数据量优化/近似 | [LC 204 · Count Primes](https://leetcode.com/problems/count-primes/) | Medium | Follow up：线性筛 / 分段筛 / 素数定理近似 n/ln(n) |

---

## 6. 前缀和 + 哈希 (Prefix Sum + Hash)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 和为 K 的子数组（前缀和 + 哈希表） | [LC 560 · Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Medium | 用 `prefixSum - k` 查哈希 |

---

## 7. 图 / 拓扑排序 (Graph / Topological Sort)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 合并多个有序 list 保持原顺序（拓扑排序） | [LC 269 · Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) | Hard | 根据局部顺序建图 + 拓扑排序 |
| Topological sort + heap 分配任务求最小完成时间 | [LC 210 · Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) + 堆 | Medium | 结合 [LC 1834 · Single-Threaded CPU](https://leetcode.com/problems/single-threaded-cpu/)（Medium）调度思路 |

---

## 8. 贪心 / 堆 (Greedy / Heap)

| 面经原题 | 对应 LeetCode | 难度 | 备注 |
| --- | --- | --- | --- |
| 任务调度最大化奖励（贪心） | [LC 630 · Course Schedule III](https://leetcode.com/problems/course-schedule-iii/) | Hard | 贪心 + 大顶堆；类比 [LC 621 · Task Scheduler](https://leetcode.com/problems/task-scheduler/)（Medium） |
| 设计 insert(id, val, ts) 和 popLowest()（配合上面任务分配题） | [LC 295 · Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) 类设计 | Hard | 用最小堆 + 哈希做 lazy deletion；参考 [LC 1046 · Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) 堆用法 |

---

## 9. 数据结构设计 / OOD (Design)

| 面经原题 | 对应 LeetCode / 参考 | 难度 | 备注 |
| --- | --- | --- | --- |
| 设计餐厅 waitlist | [LC 1188 · Design Bounded Blocking Queue](https://leetcode.com/problems/design-bounded-blocking-queue/) + OOD | Medium | 队列 + 优先级；可加预估等待时间 |
| SecureLinkedList 设计及 hash 校验 | 自定义设计题 | Medium | 每个节点存 `hash(prev_hash + data)`，类似区块链 / Merkle 校验 |
| MyHashMap 设计 | [LC 706 · Design HashMap](https://leetcode.com/problems/design-hashmap/) | Easy | 数组 + 链地址法处理冲突 |
| 链表合法性验证（环检测） | [LC 141 · Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | Easy | 快慢指针；可扩展 [LC 142 · Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) |
| 字符串问题 + Trie / OOD 拓展 | [LC 208 · Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) | Medium | 可扩展 [LC 211 · Add and Search Word](https://leetcode.com/problems/design-add-and-search-words-data-structure/)（Medium） |

---

## 10. 位运算 / 模拟 (Bit Manipulation / Simulation)

| 面经原题 | 对应 LeetCode / 参考 | 难度 | 备注 |
| --- | --- | --- | --- |
| 四部分手牌比大小题 | 自定义模拟题 | Medium | 按规则解析牌型 + 比较，重在边界与代码结构清晰 |
| heights 与 fountain 索引的 bitmask 题 | 自定义 bitmask 题 | Medium | 用位掩码表示覆盖/状态，参考 [LC 464 · Can I Win](https://leetcode.com/problems/can-i-win/)（Medium）状态压缩思路 |

---

## 刷题优先级建议

**高频核心（必刷）：**
- LC 239 滑动窗口最大值、LC 3 最长无重复子串、LC 560 和为K的子数组
- LC 39/40 组合总和、LC 68 Text Justification
- LC 298/549 二叉树最长连续序列、LC 366 Find Leaves
- LC 210/269 拓扑排序、LC 630 任务调度贪心

**设计题（Google 偏好）：**
- LC 380 GetRandom、LC 706 HashMap、LC 208 Trie
- 餐厅 waitlist / SecureLinkedList / insert+popLowest 等 OOD + 堆设计

**基础巩固：**
- LC 67 Add Binary、LC 415 Add Strings、LC 162 Find Peak、LC 896 Monotonic Array、LC 204 Count Primes

> 💡 面经反复强调：**沟通 > 纯 AC**。先讲暴力解、边写边讲、多写注释、主动 dry run；BQ 用 STAR 法准备 3-4 个故事。
