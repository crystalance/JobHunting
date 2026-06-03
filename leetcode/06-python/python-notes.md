# Python Notes

> Section: **Python** — extracted from leetcode_solution.md (lines 4606-5275)

## Python

太好了，这个问题**非常字节 / 非常工程向**。
我给你一张 **「LeetCode 高频 · Python 数据结构速查表」**，不是教材版，是**面试手写友好版**。

------

## ✅ Python 常用数据结构（LeetCode 面试速查表）

> 目标：
> 👉 **看到题目 → 秒想起用什么 → 手不抖写出来**

------

### 一、数组 / 列表（List）

| 用途     | 写法                               | 备注               |
| -------- | ---------------------------------- | ------------------ |
| 初始化   | `arr = []`                         | 动态数组           |
| 固定长度 | `arr = [0] * n`                    | 常用于 DP          |
| 二维数组 | `grid = [[0]*m for _ in range(n)]` | ⚠️ 别用 `[[0]*m]*n` |
| 追加     | `arr.append(x)`                    | O(1)               |
| 弹出末尾 | `arr.pop()`                        | O(1)               |
| 弹出指定 | `arr.pop(i)`                       | O(n)               |
| 切片     | `arr[l:r]`                         | 生成新数组         |
| 遍历     | `for i, v in enumerate(arr):`      | 高频               |

------

### 二、字符串（String）

| 用途   | 写法                     | 备注      |
| ------ | ------------------------ | --------- |
| 转列表 | `list(s)`                |           |
| 拼接   | `"".join(chars)`         | 比 `+` 快 |
| 反转   | `s[::-1]`                |           |
| 子串   | `s[l:r]`                 |           |
| 计数   | `collections.Counter(s)` |           |

------

### 三、哈希表（dict）

| 用途   | 写法                       | 备注     |
| ------ | -------------------------- | -------- |
| 初始化 | `mp = {}`                  |          |
| 计数   | `mp[x] = mp.get(x, 0) + 1` | 高频     |
| 默认值 | `defaultdict(int)`         | 面试最爱 |
| 遍历   | `for k, v in mp.items():`  |          |
| 删除   | `del mp[k]`                |          |

```python
from collections import defaultdict
cnt = defaultdict(int)
```

------

### 四、集合（set）

| 用途   | 写法                         | 备注 |
| ------ | ---------------------------- | ---- |
| 初始化 | `s = set()`                  |      |
| 去重   | `s = set(nums)`              |      |
| 查找   | `x in s`                     | O(1) |
| 添加   | `s.add(x)`                   |      |
| 删除   | `s.remove(x)` / `discard(x)` |      |

------

### 五、栈（Stack，用 list）

| 用途 | 写法              |      |
| ---- | ----------------- | ---- |
| 入栈 | `stack.append(x)` |      |
| 出栈 | `stack.pop()`     |      |
| 栈顶 | `stack[-1]`       |      |

📌 用于：

- 括号匹配
- 单调栈
- DFS

------

### 六、队列 / 双端队列（deque）

| 用途   | 写法            |      |
| ------ | --------------- | ---- |
| 初始化 | `deque()`       |      |
| 入队   | `append(x)`     |      |
| 出队   | `popleft()`     |      |
| 双端   | `appendleft(x)` |      |

```python
from collections import deque
```

📌 BFS / 滑动窗口必备

------

### 七、优先队列（heapq）

| 用途   | 写法                 |      |
| ------ | -------------------- | ---- |
| 建堆   | `heapq.heapify(arr)` | O(n) |
| 入堆   | `heappush(h, x)`     |      |
| 出堆   | `heappop(h)`         |      |
| 最大堆 | `heappush(h, -x)`    |      |

```python
import heapq
```

------

### 八、计数器（Counter）

| 用途     | 写法                 |      |
| -------- | -------------------- | ---- |
| 统计频率 | `Counter(nums)`      |      |
| TopK     | `cnt.most_common(k)` |      |
| 加减     | `cnt[x] += 1`        |      |

```python
from collections import Counter
```

------

### 九、链表（LeetCode 定义）

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

| 操作       | 写法                  |
| ---------- | --------------------- |
| 虚拟头结点 | `dummy = ListNode(0)` |
| 遍历       | `while cur:`          |
| 反转       | 三指针                |

------

### 十、树 / 图

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

| 场景     | 写法                             |
| -------- | -------------------------------- |
| DFS      | 递归                             |
| BFS      | `deque`                          |
| 图邻接表 | `graph = [[] for _ in range(n)]` |

------

### 十一、并查集（字节常考）

```python
parent = [i for i in range(n)]

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    px, py = find(x), find(y)
    if px != py:
        parent[px] = py
```

------

### 十二、常用模块速记

| 模块                  | 用途                          |
| --------------------- | ----------------------------- |
| `collections`         | deque / defaultdict / Counter |
| `heapq`               | 优先队列                      |
| `bisect`              | 二分                          |
| `functools.lru_cache` | 记忆化                        |
| `itertools`           | 组合排列                      |



### 随机数：

1. pivot_index = random.randint(left, right)

### class:

1. 

### List/Array/Queue

1. 对于一个数组，建立value到index的映射

### string：

1. 使用Counter

   1. ```python
      import collections
      dict_t = Counter(s) # s:str
      ```

### 优先队列

1. 

### 二维字符数组变成字符串列表

1. 这个需求在算法题 / 回溯 / N 皇后 里**出现频率极高**，而且写法是否简洁，**一眼就能看出熟不熟 Python** 👀
   直接给你 **结论 + 原理 + 面试推荐写法**。

------

## 一、问题重述

你有一个 **二维字符数组**：

```python
board: list[list[str]] = [
    ['.', 'Q', '.'],
    ['Q', '.', '.'],
    ['.', '.', 'Q']
]
```

你想得到：

```python
[
    ".Q.",
    "Q..",
    "..Q"
]
```

------

## 二、标准答案（最推荐）

### ✅ 列表推导 + `''.join`

```python
result = [''.join(row) for row in board]
```

✔ 简洁
✔ 高效
✔ Pythonic
✔ 面试官最爱

------

## 三、为什么一定要用 `join`（而不是 +）

### ❌ 不推荐：

```python
row_str = ''
for ch in row:
    row_str += ch
```

原因：

- 字符串是不可变的
- 每次 `+=` 都会新建字符串
- 时间复杂度退化

### ✅ 推荐：

```python
''.join(row)
```

👉 一次性分配内存，O(n)

------

## 四、完整例子（N 皇后标准收尾）

```python
def serialize(board: list[list[str]]) -> list[str]:
    return [''.join(row) for row in board]
```

典型用法：

```python
solutions.append(serialize(board))
```

------

## 五、常见变体（你要是想显得“很懂”）

### 1️⃣ 用 map（不推荐但合法）

```python
result = list(map(''.join, board))
```

优点：短
缺点：可读性略差

------

### 2️⃣ 用生成器（省内存，但通常没必要）

```python
result = (''.join(row) for row in board)
```

👉 返回的是 generator，不是 list

------

## 六、面试官可能追问的问题（提前给你答案）

### Q：`join` 的时间复杂度？

> O(n)，一次遍历，提前分配内存

------

### Q：如果 `board` 很大，这一步是瓶颈怎么办？

> 在回溯过程中只在最终解处序列化，而不是每一步都转字符串

------

## 七、面试一句话总结（可直接背）

> 对二维字符数组，通常用 `[''.join(row) for row in board]` 转成字符串列表，`join` 比逐字符拼接更高效。

------

如果你愿意，我可以直接带你**完整走一遍 N 皇后题：从 board 初始化 → 回溯 → 最终 stringify**，顺便把你前面问的 **deep copy / typing / 协程理解** 全部串起来。

### coroutine 协程

1. asyncio.Event()
   1. 一种信号量
   2. 可以 set， wait， clear

#### Python 两个协程交替打印奇偶数，要求顺序打印

1. ```python
   import asyncio
   odd_event = asyncio.Event()
   even_event = asyncio.Event()
   odd_event.set() # 别忘记！！
   
   async def print_odd(n):
     for i in range(1,n+1,2):
     	await odd_event.wait()
       print(i)
       odd_event.clear()
       even_event.set()
   
   async def print_even(n):
     for i in range(2,n+1,2):
       await even_event.wait()
       print(i)
       even_event.clear()
       odd_event.set()
       
   async def main():
     await asyncio.gather(
     	print_odd(10),
       print_even(10),
     )
    
   asyncio.run(main())
     
   ```

   

### 处理ACM模式输入输出

1. ACM 模式本质是：**你只写 `main`，所有输入从 `stdin` 来，所有输出到 `stdout`**。
   Python 里**80% 的 WA / TLE 都是 I/O 写错或读慢**。

   下面我给你一套 **ACM 模式 I/O 心智模型 + 常见题型模板**，直接可套。

   ------

   # 一、ACM 模式通用原则（先记住）

   ### ✅ 1️⃣ 一律用 `sys.stdin`

   ```python
   import sys
   data = sys.stdin.read()
   ```

   ### ✅ 2️⃣ 一次性读完，自己解析（最快、最稳）

   - 不用 `input()`（慢）
   - 不依赖交互

   ### ✅ 3️⃣ 输出统一 `print()` 或 `sys.stdout.write()`

   ------

   # 二、最基础输入（单行）

   ### 示例 1：输入一个整数

   **输入**

   ```
   5
   ```

   **代码**

   ```python
   import sys
   
   n = int(sys.stdin.readline())
   print(n)
   ```

   ------

   # 三、多整数一行（最常见）

   ### 示例 2：一行 n 个整数

   **输入**

   ```
   1 2 3 4 5
   ```

   **代码**

   ```python
   import sys
   
   arr = list(map(int, sys.stdin.readline().split()))
   print(sum(arr))
   ```

   ------

   # 四、多行多整数（二维数组）

   ### 示例 3：n 行，每行 m 个整数

   **输入**

   ```
   3 4
   1 2 3 4
   5 6 7 8
   9 10 11 12
   ```

   **代码**

   ```python
   import sys
   
   n, m = map(int, sys.stdin.readline().split())
   grid = [list(map(int, sys.stdin.readline().split())) for _ in range(n)]
   
   print(grid)
   ```

   ------

   # 五、不定行输入（直到 EOF）

   ### 示例 4：读到文件结束（非常重要）

   **输入**

   ```
   1 2
   3 4
   5 6
   ```

   **代码**

   ```python
   import sys
   
   for line in sys.stdin:
       a, b = map(int, line.split())
       print(a + b)
   ```

   ------

   # 六、所有数据一次性读（高性能）

   ### 示例 5：超大输入（推荐）

   **输入**

   ```
   10
   1 2 3 4 5 6 7 8 9 10
   ```

   **代码**

   ```python
   import sys
   
   data = list(map(int, sys.stdin.read().split()))
   n = data[0]
   arr = data[1:]
   
   print(sum(arr))
   ```

   ------

   # 七、多测试用例（T）

   ### 示例 6：多个 test case

   **输入**

   ```
   3
   4
   1 2 3 4
   3
   5 6 7
   2
   8 9
   ```

   **代码**

   ```python
   import sys
   
   data = list(map(int, sys.stdin.read().split()))
   idx = 0
   
   t = data[idx]; idx += 1
   for _ in range(t):
       n = data[idx]; idx += 1
       arr = data[idx:idx+n]
       idx += n
       print(sum(arr))
   ```

   ------

   # 八、字符串类输入

   ### 示例 7：读字符串（可能有空格）

   ```python
   import sys
   
   s = sys.stdin.readline().rstrip('\n')
   print(s)
   ```

   ------

   # 九、混合输入（整数 + 字符串）

   ### 示例 8：典型 ACM 混合

   **输入**

   ```
   3
   abc
   4
   defg
   2
   hi
   ```

   **代码**

   ```python
   import sys
   
   lines = sys.stdin.read().splitlines()
   idx = 0
   
   t = int(lines[idx]); idx += 1
   for _ in range(t):
       s = lines[idx]; idx += 1
       k = int(lines[idx]); idx += 1
       print(s[:k])
   ```

   ------

   # 十、输出格式控制（很重要）

   ### 示例 9：空格分隔输出

   ```python
   print(*arr)
   ```

   ### 示例 🔟：多行拼接输出（快）

   ```python
   out = []
   for i in range(5):
       out.append(str(i))
   print('\n'.join(out))
   ```

   ------

   # 十一、ACM 模式下常见坑（一定要避）

   ### ❌ 1️⃣ 用 `input()` 读大数据 → TLE

   ### ❌ 2️⃣ 每次 print 一行 → 慢

   ### ❌ 3️⃣ 没处理 EOF → WA

   ### ❌ 4️⃣ 多测试没清空状态 → WA

   ------

   # 十二、万能 ACM Python 模板（建议直接背）

   ```python
   import sys
   
   def main():
       data = sys.stdin.read().split()
       idx = 0
   
       # example
       n = int(data[idx]); idx += 1
       arr = list(map(int, data[idx:idx+n]))
       idx += n
   
       print(sum(arr))
   
   if __name__ == "__main__":
       main()
   ```

   

