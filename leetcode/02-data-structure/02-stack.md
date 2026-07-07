# Stack (栈)

> Section: **Data Structure** — extracted from leetcode_solution.md (lines 38-86)

### 栈

1. Stack 类已经和 Vector 一样被遗弃，现在在 Java 中普遍使用双端队列（Deque）来实现栈

2. 在Java中，`Deque`接口及其实现（如`ArrayDeque`和`LinkedList`）可以非常方便地用作栈的数据结构。`Deque`（双端队列）支持在两端插入和移除元素，因此可以轻松地实现栈的LIFO（后进先出）特性。使用`Deque`实现栈主要依靠以下几个方法：

   - `push(E e)`：将元素`e`压入栈顶。
   - `pop()`：移除并返回栈顶元素。
   - `peek()`：查看（但不移除）栈顶元素。

   下面是一个简单的示例，展示如何使用`ArrayDeque`类来实现栈：

   ```java
   import java.util.Deque;
   import java.util.ArrayDeque;
   
   public class StackExample {
       public static void main(String[] args) {
           // 创建一个Deque实例，用作栈
           Deque<Integer> stack = new ArrayDeque<>();
   
           // 使用push方法压入元素
           stack.push(1);
           stack.push(2);
           stack.push(3);
   
           // 查看栈顶元素，但不移除
           System.out.println("栈顶元素（peek）: " + stack.peek()); // 输出：栈顶元素（peek）: 3
   
           // 弹出栈顶元素
           System.out.println("弹出（pop）: " + stack.pop()); // 输出：弹出（pop）: 3
   
           // 继续弹出直到栈为空
           while (!stack.isEmpty()) {
               System.out.println("弹出（pop）: " + stack.pop());
           }
   
           // 此时栈已空，尝试再次弹出将抛出异常
           // System.out.println("弹出（pop）: " + stack.pop()); // 这行将抛出NoSuchElementException
       }
   }
   ```

   这个示例展示了如何使用`ArrayDeque`作为栈来进行基本操作。注意，虽然可以使用`Deque`的`addFirst`和`removeFirst`（或`addLast`和`removeLast`）方法来模拟栈的行为，但是`push`、`pop`和`peek`方法的语义更清晰地表达了栈的意图，因此更推荐使用这些方法。

   **使用`Deque`而不是`Stack`类实现栈的一个主要原因是，`Stack`类是一个遗留的集合类，它扩展自`Vector`，并且它的大部分操作都不是同步的。相比之下，`Deque`接口提供了更丰富和灵活的操作，并且`ArrayDeque`通常比`Stack`具有更好的性能。因此，官方文档也推荐使用`Deque`实现栈功能。**

3.

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #21 — Monotonic stack — when & why

### 21. Monotonic stack

1. what problem does it apply to? how it works?

   1. A monotonic stack is a data structure commonly used to solve problems that require maintaining some order relationship. It is mainly used for the following types of problems:

      1. **Next Greater or Smaller Element**: Finding the next greater or smaller element for each element in an array.
      2. **Maximum or Minimum in a Sliding Window**: Quickly finding the maximum or minimum value in a sliding window.
      3. **Largest Rectangle in Histogram**: Calculating the largest rectangle area in a histogram.

      **Core Idea**:
      
      - A monotonic stack maintains a stack that is either monotonically increasing or decreasing.
      - As you iterate through the array, you decide whether to push the current element onto the stack or pop elements from the stack based on the relationship between the current element and the top of the stack.
      - The monotonic nature allows us to handle operations that require repetitive comparisons in linear time complexity.
      
      **Reason for Reducing Time Complexity**:
      - Each element is pushed and popped from the stack at most once, resulting in an overall complexity of O(n) instead of O(n^2).
      - The stack's monotonicity avoids unnecessary calculations by preventing repeated comparisons during iteration.

2. **Pattern / template (单调栈模板)**

   1. 关键决定：栈里存**下标**（方便算距离），从栈底到栈顶保持单调。想找 **next greater** 就维护一个**单调递减栈**：新元素比栈顶大时，栈顶元素就找到了它右边第一个更大的值，弹出并结算。

   2. 从左到右遍历（存下标，边弹边结算）：

      ```java
      // 对每个 i，求右边第一个「更大」元素的下标 ans[i]（没有则 -1）
      int[] nextGreater(int[] nums) {
          int n = nums.length;
          int[] ans = new int[n];
          Arrays.fill(ans, -1);
          Deque<Integer> st = new ArrayDeque<>(); // 存下标，栈内对应的值单调递减
          for (int i = 0; i < n; i++) {
              // 当前值比栈顶大 => 栈顶找到了它的 next greater
              while (!st.isEmpty() && nums[i] > nums[st.peek()]) {
                  int idx = st.pop();
                  ans[idx] = i;          // 或 nums[i] / 距离 i - idx，视题意而定
              }
              st.push(i);
          }
          return ans; // 循环结束后仍留在栈里的，说明右边没有更大元素
      }
      ```

   3. 从右到左遍历（另一种等价写法，栈顶即候选答案）：

      ```java
      for (int i = n - 1; i >= 0; i--) {
          while (!st.isEmpty() && nums[st.peek()] <= nums[i]) st.pop(); // 弹掉不可能成为答案的
          ans[i] = st.isEmpty() ? -1 : st.peek();
          st.push(i);
      }
      ```

   4. **改栈的单调方向 / 比较符** 即可切换语义：
      1. next **greater** → 递减栈，弹出条件 `nums[i] > nums[st.peek()]`
      2. next **smaller** → 递增栈，弹出条件 `nums[i] < nums[st.peek()]`
      3. previous greater/smaller → 反过来遍历，或结算时机改在 push 之前看栈顶。

3. **Worked examples**

   1. [739. Daily Temperatures](https://leetcode.cn/problems/daily-temperatures/) — 直接套「从左到右 + 存下标」，`ans[idx] = i - idx`（等多少天）。
   2. [496. Next Greater Element I](https://leetcode.cn/problems/next-greater-element-i/) — 先对 nums2 求 next greater 存进 HashMap，再查询。
   3. [84. Largest Rectangle in Histogram](https://leetcode.cn/problems/largest-rectangle-in-histogram/) — 递增栈，弹出时以被弹出的高度为矩形高，宽 = 右边界(当前 i) − 左边界(新栈顶) − 1。常用**哨兵**（首尾各加一个 0 / 极小值）来避免边界特判。
   4. [42. 接雨水](https://leetcode.cn/problems/trapping-rain-water/) — 递减栈，按层结算。

