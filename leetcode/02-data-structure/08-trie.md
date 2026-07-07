# Trie (字典树 / 前缀树)

> Section: **Data Structure** — new topic. Reference taxonomy: 灵神「如何科学刷题」，常用数据结构章节（枚举技巧/前缀和/差分/栈/队列/堆/**字典树**/并查集/树状数组/线段树）。See https://leetcode.cn/discuss/post/3141566/ru-he-ke-xue-shua-ti-by-endlesscheng-q3yd/

### 1. What is a Trie?

1. A tree where each **edge** represents a character and each **path from root** represents a prefix.
2. 用途：高效存储和检索字符串集合，尤其是**前缀**相关的查询。
   1. `insert(word)` / `search(word)` / `startsWith(prefix)` 都是 O(L)，L 为字符串长度，与集合大小无关。
3. 每个节点存两样东西：
   1. `children`：指向子节点的指针（26 个小写字母用数组，或用 HashMap 支持任意字符）。
   2. `isEnd`：标记从根到此节点的路径是否构成一个完整单词。

### 2. Standard implementation (Java)

1. [208. Implement Trie (Prefix Tree)](https://leetcode.cn/problems/implement-trie-prefix-tree/)

   ```java
   class Trie {
       private final Trie[] children = new Trie[26];
       private boolean isEnd = false;

       public void insert(String word) {
           Trie node = this;
           for (char c : word.toCharArray()) {
               int i = c - 'a';
               if (node.children[i] == null) node.children[i] = new Trie();
               node = node.children[i];
           }
           node.isEnd = true;
       }

       // 找到 word 结尾的节点（找不到返回 null）
       private Trie find(String word) {
           Trie node = this;
           for (char c : word.toCharArray()) {
               int i = c - 'a';
               if (node.children[i] == null) return null;
               node = node.children[i];
           }
           return node;
       }

       public boolean search(String word) {
           Trie node = find(word);
           return node != null && node.isEnd;   // 必须是完整单词
       }

       public boolean startsWith(String prefix) {
           return find(prefix) != null;         // 只要前缀存在即可
       }
   }
   ```

2. 关键区别：`search` 要求 `isEnd == true`，`startsWith` 只要路径存在。

### 3. Python version

```python
class Trie:
    def __init__(self):
        self.children = {}
        self.is_end = False

    def insert(self, word: str) -> None:
        node = self
        for ch in word:
            node = node.children.setdefault(ch, Trie())
        node.is_end = True

    def _find(self, word: str):
        node = self
        for ch in word:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None
```

### 4. Wildcard search (DFS on Trie)

1. [211. Design Add and Search Words Data Structure](https://leetcode.cn/problems/design-add-and-search-words-data-structure/)
   1. 支持 `.` 通配符：遇到 `.` 时对当前节点的**所有非空子节点**递归。

   ```java
   private boolean dfs(String word, int i, Trie node) {
       if (i == word.length()) return node.isEnd;
       char c = word.charAt(i);
       if (c != '.') {
           Trie nxt = node.children[c - 'a'];
           return nxt != null && dfs(word, i + 1, nxt);
       }
       for (Trie child : node.children)          // '.' 匹配任意字符
           if (child != null && dfs(word, i + 1, child)) return true;
       return false;
   }
   ```

### 5. Trie + board DFS

1. [212. Word Search II](https://leetcode.cn/problems/word-search-ii/)
   1. 把所有 words 建成一棵 Trie，然后在网格上 DFS。相比对每个单词单独搜索，Trie 让**多个单词共享前缀**，一次 DFS 就能同时匹配。
   2. 小技巧：找到一个单词后，可把该节点的 `word` 置空（去重），或做剪枝删除叶子节点。

### 6. Bitwise Trie (0/1 Trie) — 处理异或问题

1. 把数字按二进制位（一般从高位到低位）插入 Trie，每个节点最多 2 个子节点（0 和 1）。
2. 求**最大异或**：查询时每一位都贪心地走**相反**的比特，尽量让高位为 1。
   1. [421. Maximum XOR of Two Numbers in an Array](https://leetcode.cn/problems/maximum-xor-of-two-numbers-in-an-array/)

   ```java
   class Solution {
       public int findMaximumXOR(int[] nums) {
           int HIGH = 30;                 // nums[i] < 2^31
           var root = new int[2][];       // 简化：用嵌套数组当 trie
           // 生产写法建议用真正的节点类，这里示意贪心思路：
           // 对每个 num，从高位到低位插入；查询时优先走 1^bit 的那一侧。
           return 0; // 见下方文字说明
       }
   }
   ```

   1. 思路：`ans` 的每一位，如果能在 Trie 中找到与当前位相反的分支，就把该位设为 1 并走过去；否则走相同分支。时间 O(n · 32)。

### 7. When to reach for a Trie

1. 大量字符串的**前缀查询 / 自动补全 / 拼写检查**。
2. 需要同时匹配**多个模式串**（配合 DFS / AC 自动机）。
3. 位运算里的**最大/最小异或**、异或对计数等（0/1 Trie）。
4. 相关题目：
   1. [208. Implement Trie](https://leetcode.cn/problems/implement-trie-prefix-tree/)
   2. [211. Add and Search Word](https://leetcode.cn/problems/design-add-and-search-words-data-structure/)
   3. [212. Word Search II](https://leetcode.cn/problems/word-search-ii/)
   4. [648. Replace Words](https://leetcode.cn/problems/replace-words/)
   5. [677. Map Sum Pairs](https://leetcode.cn/problems/map-sum-pairs/)
   6. [720. Longest Word in Dictionary](https://leetcode.cn/problems/longest-word-in-dictionary/)
   7. [421. Maximum XOR of Two Numbers in an Array](https://leetcode.cn/problems/maximum-xor-of-two-numbers-in-an-array/)
