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

