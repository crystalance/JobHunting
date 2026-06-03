# Algorithms/Solutions of Leetcode

## data structure

### 数组

1. `int ans[]; `java可以用这样的语句吗，先不定义数组的长度？
   1. 在Java中，可以声明一个数组而不指定其长度，但是在使用这个数组之前，需要为其分配内存空间并指定长度。因此，声明 `int ans[];` 是合法的语句，但在使用 `ans` 数组之前，应该通过 `ans = new int[length];` 来为其分配内存空间并指定长度。在这个语句之后，`ans` 数组才能被正常使用。

#### 双指针

1. 只要数组有序，就应该想到双指针技巧
2. 

#### 最长递增子序列

1. ```java
       public static int minModifications(int[] nums) {
           int n = nums.length;
           List<Integer> lis = new ArrayList<>();
   
           for (int num : nums) {
               int pos = Collections.binarySearch(lis, num);
               if (pos < 0) pos = -(pos + 1); //如果元素不存在，会返回插入位置（-index-1）
               if (pos == lis.size()) {
                   lis.add(num);
               } else {
                   lis.set(pos, num);
               }
           }
   
           return lis.size();
       }
   ```

   

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

### 堆

1. 当前节点的值都大于等于/或者小于等于节点的字节点
2. 堆和栈在操作系统中的使用
   1. 

### 哈希 hash

1. java中的哈希表是怎么样的，有什么操作方法？

   1. 在Java中，哈希表通常指的是HashMap类，它是一种常用的数据结构，用于存储键值对。HashMap基于哈希表的实现，允许null键和null值，并且不保证元素的顺序。

      以下是HashMap类的一些常见操作方法：

      1. put(key, value)：将指定的键值对存储到哈希表中。
      2. get(key)：根据键获取对应的值。
      3. containsKey(key)：检查哈希表中是否包含指定的键。
      4. containsValue(value)：检查哈希表中是否包含指定的值。
      5. remove(key)：根据键移除对应的键值对。
      6. keySet()：返回哈希表中所有键组成的Set集合。
      7. values()：返回哈希表中所有值组成的Collection集合。
      8. entrySet()：返回哈希表中所有键值对组成的Set集合。

      这些方法使得我们可以方便地操作哈希表，进行插入、查找、删除等操作。HashMap还有许多其他方法，可以根据需要查阅官方文档以获取更多信息。

2. 如何定义一个哈希表？

   1. 在Java中，你可以使用HashMap类来定义一个哈希表。以下是一个简单的示例，展示了如何定义一个HashMap并向其中添加键值对：

      ```java
      import java.util.HashMap;
      
      public class Main {
          public static void main(String[] args) {
              // 定义一个HashMap
              HashMap<String, Integer> hashMap = new HashMap<>();
      
              // 向哈希表中添加键值对
              hashMap.put("A", 1);
              hashMap.put("B", 2);
              hashMap.put("C", 3);
      
              // 输出哈希表中的值
              System.out.println(hashMap); // 输出：{A=1, B=2, C=3}
          }
      }
      ```

      在这个示例中，我们首先导入了HashMap类，然后定义了一个HashMap对象`hashMap`，并向其中添加了几个键值对。你可以根据需要选择不同的数据类型作为键和值。

3. 为什么哈希表可以在 O(1)的时间内完成插入和删除操作？

   1. ```
      哈希表之所以能够在 O(1) 的时间内完成插入和删除操作，是因为它利用了哈希函数将键映射到存储位置。哈希函数能够将键均匀地分布在哈希表的槽位中，使得查找、插入和删除的时间复杂度为常数级别。
      具体来说，当要插入或删除一个元素时，哈希表会根据键通过哈希函数计算出对应的存储位置。在理想情况下，每个槽位中只有一个元素，因此无需遍历整个哈希表即可找到目标位置。这使得插入和删除操作的时间复杂度保持在 O(1)。
      然而，在实际情况下，由于哈希冲突的存在，即不同的键可能映射到同一个槽位，会导致一些额外的操作，例如链表或者红黑树的遍历。但是，通过合理的哈希函数设计和哈希表的动态扩容策略，可以使得哈希冲突的概率较低，从而仍然保持 O(1) 的平均时间复杂度。
      ```

   2. 就是说哈希表，通过给定的索引，仅需经过一次哈希函数计算，就能得到该索引所指向的位置，所以是O(1)

4. 为什么说hash和随机性有关？

5. 为什么软件算法无法产生随机数？


### 链表

#### 1.快慢指针（用于判断链表中是否存在循环）

1. 要修改代码以使用快慢指针来检测链表中是否存在循环，您可以按照以下方式修改 `hasCycle` 方法：

   ```java
   public class Solution {
       public boolean hasCycle(ListNode head) {
           if (head == null || head.next == null) {
               return false;
           }
   
           ListNode slow = head;
           ListNode fast = head.next;
   
           while (slow != fast) {
               if (fast == null || fast.next == null) {
                   return false;
               }
               slow = slow.next;
               fast = fast.next.next;
           }
   
           return true;
       }
   }
   ```

   这样，您就使用了快慢指针来检测链表中是否存在循环。如果存在循环，快慢指针最终会相遇，返回 `true`；否则返回 `false`。

2. the feature of the fast-slow pointer:

   1. leetcode 142
   2. <img src="/Users/lanceliao/Library/Application Support/typora-user-images/image-20241027002447299.png" alt="image-20241027002447299" style="zoom:50%;" />


#### 2. 自己构建双向链表实现LRU

1. [LRU 缓存](https://leetcode.cn/problems/lru-cache/)

2. 

   ```java
   class ListNode{
       ListNode prev; 
       ListNode next;
       int key;
       int value;
   
       public ListNode(int key, int value){
           this.key = key;
           this.value = value;
           prev = null;
           next = null;
       }
   
   }
   
   class LRUCache {
       Map<Integer, ListNode> map = new HashMap<>();
       ListNode head = new ListNode(0,0); 
       ListNode tail = new ListNode(0,0); 
       int capacity;
       public LRUCache(int capacity) {
           this.capacity = capacity;
           head.next = tail;
           tail.prev = head;
       }
       
       public int get(int key) {
           if(!map.containsKey(key)) return -1;
           
           ListNode node = map.get(key);
           remove(node);
           add(node);  
           return node.value;  
       }
       
       public void put(int key, int value) {
           if(map.containsKey(key)){
               ListNode old = map.get(key);
               remove(old);
           }
           ListNode node = new ListNode(key, value);
           map.put(key,node);
           add(node);
   
           if(map.size() > capacity){
               ListNode toBeDelete = head.next;
               remove(toBeDelete);
               map.remove(toBeDelete.key);
           }
       }
   
       public void add(ListNode node){
           ListNode prevEnd = tail.prev;
           prevEnd.next = node;
           node.prev = prevEnd;
           node.next = tail;
           tail.prev = node;
       }
   
       public void remove(ListNode node){
           node.prev.next = node.next;
           node.next.prev = node.prev;
       }
   }
   
   /**
    * Your LRUCache object will be instantiated and called as such:
    * LRUCache obj = new LRUCache(capacity);
    * int param_1 = obj.get(key);
    * obj.put(key,value);
    */
   ```


#### 3. Copy List with Random Pointer

1. [138. Copy List with Random Pointer](https://leetcode.cn/problems/copy-list-with-random-pointer/)

2. Solution: to copy nodes separately and in recursion

   1. ```java
      /*
      // Definition for a Node.
      class Node {
          int val;
          Node next;
          Node random;
      
          public Node(int val) {
              this.val = val;
              this.next = null;
              this.random = null;
          }
      }
      */
      
      class Solution {
          Map<Node,Node> cache_copied_nodes = new HashMap<Node,Node>();
         
          public Node copyRandomList(Node head) {
              if(head==null){
                  return null;
              }
              if(!cache_copied_nodes.containsKey(head)){
                  Node copyNode = new Node(head.val);
                  cache_copied_nodes.put(head,copyNode);
                  copyNode.next = copyRandomList(head.next);
                  copyNode.random = copyRandomList(head.random);
              }
              return cache_copied_nodes.get(head);
         
          }
      }
      ```

   2. In this code, why it would be wrong if I put `cache_copied_nodes.put(head,copyNode);` this step after I jump into another recursion?

      1. 在这段代码中，如果将cache_copied_nodes.put(head,copyNode);这一步放在跳入另一个递归之后，会导致在处理相同节点时出现问题。由于递归的特性，程序会在回溯时再次访问相同的节点，如果在跳入另一个递归之后才将节点放入缓存，会导致无法正确地获取到已经复制的节点，从而破坏了复制链表的正确性。因此，正确的做法是在递归之前就将节点放入缓存，以确保在需要时能够正确地获取到已经复制的节点。
      2. What if `head.random = head`?

   3. **Why do we think of using recursion to solve this problem?**

      1. Recursion is **a natural choice** for solving problems involving **linked structures like linked lists or trees because it simplifies the logic by breaking down the problem into smaller subproblems.** In the case of copying a linked list with random pointers, each node can be seen as a smaller linked list in itself, where you need to copy the current node and then recursively copy the next and random nodes.

         Recursion allows you to handle each node and its connections independently, making it easier to manage the complex relationships between nodes in a linked structure. It also helps in reducing the code complexity and making the solution more elegant and concise compared to iterative approaches.

         Overall, recursion is a powerful technique for dealing with problems that exhibit recursive substructure, making it a natural choice for tasks like traversing and manipulating linked structures.

      2. 

#### 4. reverse linked list

1. [92. Reverse Linked List II](https://leetcode.cn/problems/reverse-linked-list-ii/)

2. learning points

3. code

   1. ```java
      /**
       * Definition for singly-linked list.
       * public class ListNode {
       *     int val;
       *     ListNode next;
       *     ListNode() {}
       *     ListNode(int val) { this.val = val; }
       *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
       * }
       */
      class Solution {
          public ListNode reverseBetween(ListNode head, int left, int right) {
              if(left == right) {
                  return head;
              }
              //We use a dummy node to simplify handling cases where the sublist to be reversed includes the head of the original linked list.
              ListNode dummy = new ListNode(0);
              dummy.next = head;
              ListNode neck = dummy; 
            	// We use a neck node to keep track of the node before the sublist to be reversed.
              for (int i = 0; i < left - 1; i++) {
                  neck = neck.next;
              }
      
              ListNode leftNode = neck.next;
              ListNode rightNode = leftNode;
              //We use a neck node to keep track of the node before the sublist to be reversed.
              for (int i = 0; i < right - left; i++) {
                  rightNode = rightNode.next;
              }
      
              ListNode tail = rightNode.next;
      				//reverse
              ListNode previousNode = tail;
              ListNode currentNode = leftNode;
              ListNode nextNode;
      
              while (currentNode != tail) {
                  nextNode = currentNode.next;
                  currentNode.next = previousNode;
                  previousNode = currentNode;
                  currentNode = nextNode;
              }
      
              neck.next = rightNode;
      
              return dummy.next;
      
          }
      }
      ```

#### [19. Remove Nth Node From End of List](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/)

1. **learning point**

   1. we should add a head node of the list to better manipulate the list, processing the edge cases.

2. my version of answer:

   1. ```java
      class Solution {
          Map<Integer,ListNode> node_map = new HashMap<Integer,ListNode>();
          public ListNode removeNthFromEnd(ListNode head, int n) {
              
              if(head.next==null){return null;}
      
              ListNode dummy = new ListNode(0);
              dummy.next = head;
              node_map.put(0,dummy);
              ListNode pointer = head;
              int index = 1;
              while(pointer!=null){
                  node_map.put(index, pointer);
                  index++;
                  pointer = pointer.next;
              }
              ListNode before = node_map.get(index-n-1);
              if(n==1){before.next = null;}else{
                  ListNode after = node_map.get(index-n+1);
                  before.next = after;
              }
              return dummy.next;
      
      
          }
      }
      ```

   2. analyze

      1. To analyze the time complexity of the provided program for removing the nth node from the end of a linked list, let's break down the operations:

         1. Traversing the Linked List to Populate the Map:
            1. In this step, the program traverses the entire linked list of size N to populate the node_map with indices and corresponding nodes.
               1. Time complexity: O(N)
                  Accessing Nodes from the Map:
            2. After populating the map, the program accesses nodes from the map based on the calculated indices.
               1. Time complexity: O(1)
            3. Therefore, the overall time complexity of this program is O(N) due to the traversal of the linked list to populate the map with node indices. The subsequent operations of accessing nodes from the map have a time complexity of O(1) since accessing elements from a HashMap is considered constant time.

         In conclusion, the time complexity of this program is O(N) where N is the number of nodes in the input linked list.

3. The reference solution

   1. ```java
      class Solution {
          public ListNode removeNthFromEnd(ListNode head, int n) {
              ListNode dummy = new ListNode(0, head);
              int length = getLength(head);
              ListNode cur = dummy;
              for (int i = 1; i < length - n + 1; ++i) {
                  cur = cur.next;
              }
              cur.next = cur.next.next;
              ListNode ans = dummy.next;
              return ans;
          }
      
          public int getLength(ListNode head) {
              int length = 0;
              while (head != null) {
                  ++length;
                  head = head.next;
              }
              return length;
          }
      }
      
      
      ```

4. The first solution is faster than the second solution because it directly calculates the position of the node to be removed using a two-pointer technique without the need to store all nodes and their indices in a map.

   In the first solution:

   It uses a dummy node to handle edge cases efficiently.
   It calculates the length of the linked list by traversing it once.
   It then directly moves to the node to be removed by iterating through the list with two pointers (slow and fast pointers).
   Once the correct position is found, it removes the node in constant time without additional lookups.
   In contrast, the second solution:

   It stores all nodes and their indices in a map, which requires additional space and time complexity to build the map.
   It involves traversing the linked list twice - once to populate the map and once to find and remove the node at the calculated index.
   It relies on map lookups to find the nodes, which adds overhead compared to direct pointer manipulation in the first solution.
   Due to these factors, the first solution is more efficient and faster than the second solution in terms of time complexity and space complexity.

#### [25. K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)

1. 思路
   1. 先遍历一遍

### Binary Tree

#### Binary tree & DFS

1. 太好了，这一步你已经**站在“会写 → 会建模 → 会迁移”的门口了** 👍
   我直接 **两个都给你**，而且是**一套能长期复用的体系**。

   ------

   # 一、统一的「二叉树 DFS + 递归建模模板」🧠

   > 所有二叉树递归题，本质都在回答 **三件事**。

   ------

   ## 🌳 通用递归三问（一定要背）

   ```text
   1. 递归函数的“定义”是什么？
   2. 当前层要做什么？
   3. 递归边界是什么？
   ```

   ------

   ## 🧩 重建二叉树的抽象模板（核心）

   ### 问题抽象

   > **给定遍历序列 + 子区间 → 构造并返回子树根节点**

   ------

   ### 模板代码（通用）

   ```python
   def dfs(left, right):
       if left > right:
           return None
   
       # 1️⃣ 确定 root
       root_val = ...
       root = TreeNode(root_val)
   
       # 2️⃣ 切分左右子树区间
       mid = index_map[root_val]
   
       # 3️⃣ 构建左右子树（注意顺序）
       root.left = dfs(left, mid - 1)
       root.right = dfs(mid + 1, right)
   
       return root
   ```

   ------

   ## 🧠 不同遍历 = 不同 root 获取方式

   | 题目                | root 从哪来      | 递归顺序 |
   | ------------------- | ---------------- | -------- |
   | preorder + inorder  | preorder[idx++]  | 先左后右 |
   | postorder + inorder | postorder[idx--] | 先右后左 |

   ------

   ## 🚨 面试高频陷阱

   ❌ 在递归里切 list
   ❌ 每层线性找 root
   ❌ 忘记右子树优先（postorder）

   ------

   # 二、二叉树「5 大高频 DFS 题」横向对比 🧩

   > 你会发现：**全都一个模板**

   ------

   ## ① 重建二叉树（Build Tree）

   ```text
   dfs 返回：TreeNode
   当前层：创建 root
   递归：构造左右子树
   ```

   ------

   ## ② 翻转二叉树（Invert Tree）

   ```python
   def invert(root):
       if not root:
           return None
       root.left, root.right = invert(root.right), invert(root.left)
       return root
   dfs 返回：TreeNode
   当前层：交换左右
   ```

   ------

   ## ③ 最近公共祖先（LCA）

   ```python
   def lca(root, p, q):
       if not root or root == p or root == q:
           return root
   
       left = lca(root.left, p, q)
       right = lca(root.right, p, q)
   
       if left and right:
           return root
       return left or right
   dfs 返回：是否包含目标
   当前层：合并左右结果
   ```

   ------

   ## ④ 路径总和 / 最大路径和

   ```python
   def maxGain(node):
       if not node:
           return 0
       left = max(maxGain(node.left), 0)
       right = max(maxGain(node.right), 0)
       ans = max(ans, node.val + left + right)
       return node.val + max(left, right)
   dfs 返回：单边贡献
   当前层：更新全局最优
   ```

   ------

   ## ⑤ 克隆二叉树（Clone Tree）

   ```python
   def clone(root):
       if not root:
           return None
       new = TreeNode(root.val)
       new.left = clone(root.left)
       new.right = clone(root.right)
       return new
   dfs 返回：新节点
   当前层：复制当前
   ```

   ------

   # 三、你应该形成的「统一心智模型」🔥

   ### 所有二叉树 DFS，本质都是：

   ```text
   一个节点 = 当前处理 + 左子树结果 + 右子树结果
   ```

   ------

   ## 🧠 三种返回值模式（超级重要）

   | 返回类型   | 代表题型           |
   | ---------- | ------------------ |
   | TreeNode   | 构建 / 克隆 / 翻转 |
   | bool / int | 是否存在 / 路径和  |
   | 自定义对象 | DP / 多信息汇总    |

   ------

   # 四、怎么在面试中“看一眼就知道怎么写”

   ### 面试官给题，你先在脑子里问：

   1. dfs 返回什么？
   2. root 在哪一步确定？
   3. 左右子树谁先？

   你一旦回答完这三问，**代码已经写完 80% 了**。

   ------

   # 五、你的进阶路线（非常适合你现在）

   你现在已经具备：

   - ✅ DFS 熟练
   - ✅ 递归建模能力
   - ✅ 能发现 O(n²) 并优化到 O(n)

   下一步建议你冲这三类：

   1. **二叉树 + 状态压缩**（Tree DP）
   2. **二叉树 + 哈希映射**
   3. **树 → 图 → 拓扑思维迁移**

   ------

   如果你愿意，我可以下一步直接给你：

   - 📌 一张「二叉树 DFS 模板速查表」
   - 📌 5 题「同模板变体」实战训练
   - 📌 或把这些整理成 **面试 5 分钟复盘稿**

   你选一个，我继续陪你打通这一关 💪

#### [105. Construct Binary Tree from Preorder and Inorder Traversal](https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)

1. to constrcut a tree is to 

   1. find its root node 

   2. find its child_node

   3. based on its child_node, contruct child tree recursively
      1. so the root node of a tree can be determined by the first element of preorder array
      2. then what's its left child(if exists)?
      3. --- the first element of sub-preorder array?
      4. then how to determine the preorder array of both child tree?
      5. --- should look for its inorder array

     the total number of nodes of each child tree is divided by root node at inorder array

     preoder array:  [root] [left preorder nodes] [right ---]

     inorder array:  [left inorder nodes] [root] [right inoder nodes]

2. solution

   1. ```java
      /**
       * Definition for a binary tree node.
       * public class TreeNode {
       *     int val;
       *     TreeNode left;
       *     TreeNode right;
       *     TreeNode() {}
       *     TreeNode(int val) { this.val = val; }
       *     TreeNode(int val, TreeNode left, TreeNode right) {
       *         this.val = val;
       *         this.left = left;
       *         this.right = right;
       *     }
       * }
       */
      
      class Solution {
          int preorderIndex = 0;
          int[] self_preorder;
          HashMap<Integer,Integer> Val_index_inorder = new HashMap<>();
          public TreeNode buildTree(int[] preorder, int[] inorder) {
              self_preorder = preorder;
              for(int i=0;i<inorder.length;i++){
                  Val_index_inorder.put(inorder[i],i);
              }
              return constructTree(0,inorder.length-1);
          }
      
          private TreeNode constructTree(int left_border, int right_border){// border of inorder array
              if (left_border > right_border) {
                  return null;
              }
              int root_val = self_preorder[preorderIndex];
              preorderIndex++;
              int rootIndex = Val_index_inorder.get(root_val);
              TreeNode root = new TreeNode(root_val);
              root.left = constructTree(left_border, rootIndex - 1);
              root.right = constructTree(rootIndex + 1, right_border); //change position?
              return root;
          }
      }
      ```

      

#### [117. Populating Next Right Pointers in Each Node II](https://leetcode.cn/problems/populating-next-right-pointers-in-each-node-ii/)

1. 对于二叉树的每层，用next指针将每层的节点连起来？

   1. 可以立马想到用层序遍历
   2. 如何判断当前节点是属于哪一层？
      1. 用当前队列中剩余元素的个数来判断
         1. 用queue.size()先拿到当前有多少元素，再用for循环来处理，连接每一个元素，
         2. 连接的时候只要用queue.peek()就好了
         3. 这样就一次性处理一层的元素，不用担心下一层的影响

   ```java
   /*
   // Definition for a Node.
   class Node {
       public int val;
       public Node left;
       public Node right;
       public Node next;
   
       public Node() {}
       
       public Node(int _val) {
           val = _val;
       }
   
       public Node(int _val, Node _left, Node _right, Node _next) {
           val = _val;
           left = _left;
           right = _right;
           next = _next;
       }
   };
   */
   
   class Solution {
       public Node connect(Node root) {
           if(root==null){return null;}
           Queue<Node>  NodeQueue = new LinkedList<>();
           NodeQueue.offer(root);
           while(!NodeQueue.isEmpty()){
               int level_size = NodeQueue.size();
               for(int i=0;i<level_size;i++){
                   Node currentNode = NodeQueue.poll();
                   if(i<level_size-1){
                       currentNode.next = NodeQueue.peek();
                   }
                   if(currentNode.left != null){NodeQueue.offer(currentNode.left);}
                   if(currentNode.right!=null){NodeQueue.offer(currentNode.right);}
               }
           }
           return root;
       }   
   }
   ```

#### 中序遍历

##### 1. 可以递归实现也可以用栈来实现

1. 例题：[173. Binary Search Tree Iterator](https://leetcode.cn/problems/binary-search-tree-iterator/)
   1. 区别在于栈来实现可以做到控制每一步的进行，而递归实现必须先跑完整个递归过程不带停，然后根据递归得到的一个序列进行操作
2. 栈实现中序遍历

   1. ```java
      public void inordertraverse(TreeNode root){
        TreeNode curNode = root;
        List<TreeNode> result = new ArrayList<TreeNode>();
        Deque<TreeNode> stk = new ArrayDeque<TreeNode>();
        while(curNode!=null||!stk.isEmpty()){
          while(curNode!=null){
            stk.push(curNode);
            curNode = curNode.left;
          }
          
          TreeNode left = stk.pop();
          result.add(left);
          curNode = left.right;
        }
        return result
      }
      ```


#### 非递归实现后序遍历

1. ```java
   public List<Integer> postorderTraversal(TreeNode root) {
       List<Integer> result = new ArrayList<>();
       Deque<TreeNode> stack = new ArrayDeque<>();
       TreeNode curr = root, prev = null;
   
       while (curr != null || !stack.isEmpty()) {
           while (curr != null) {
               stack.push(curr);
               curr = curr.left; // 先走左边
           }
   
           TreeNode peek = stack.peek(); // 栈顶
           // 如果右子树为空，或右子树刚刚访问过了 ⇒ 可以访问根了
           if (peek.right == null || peek.right == prev) {
               result.add(peek.val);
               stack.pop();
               prev = peek; // 标记这个节点已经访问
           } else {
               curr = peek.right; // 否则先访问右子树
           }
       }
   
       return result;
   }
   ```

#### 先序遍历

1. ```java
   public List<Integer> preorderTraversal(TreeNode root) {
       List<Integer> result = new ArrayList<>();
       if (root == null) return result;
   
       Deque<TreeNode> stack = new ArrayDeque<>();
       stack.push(root);
   
       while (!stack.isEmpty()) {
           TreeNode node = stack.pop();
           result.add(node.val); // 访问当前节点
   
           // 先压右再压左（保证左子树先访问）
           if (node.right != null) stack.push(node.right);
           if (node.left != null) stack.push(node.left);
       }
   
       return result;
   }
   
   ```

   

#### 最小高度树

1. https://leetcode.com/problems/minimum-height-trees/
2. 要找到最小高度的那个节点，其实就是找树的直径（树中任意两点之间的 **最长简单路径**），那然后找这个直径的中心作为顶点，才会有最小高度，

### Binary Search Tree 二叉搜索树

1. 一般都是用中序遍历，得到一个递增的序列

#### lowereset common ancestor:

```python
class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        cur = root
        while cur:
            if p.val < cur.val and q.val < cur.val:
                cur = cur.left
            elif p.val > cur.val and q.val > cur.val:
                cur = cur.right
            else:
                return cur
```

#### 除了中序遍历，还可以利用的性质：

当前的值是左子树的值的上界，是右子树的下届，在dfs的途中可以逐步缩小界限。

1. 但关键点在于：

   > **BST 校验用的不是“中序遍历的顺序”，而是“中序遍历的性质”。**

   我们把这两件事彻底分开，你就不会混了。

   ------

   ## 一、先给结论（先稳住）

   - ✅ **这段代码的执行顺序是先序遍历（根 → 左 → 右）**
   - ✅ **它仍然可以正确判断 BST**
   - ❌ **它不是在“做中序遍历”**
   - 💡 **它是在用 BST 的「全局约束」来验证，而不是用中序序列**

   ------

   ## 二、为什么它看起来像先序？（你没看错）

   代码是：

   ```python
   def dfs(node, low, high):
       if not node:
           return True
       if not (low < node.val < high):
           return False
       return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)
   ```

   执行顺序是：

   1. **先处理当前节点（root）**
   2. 再递归左子树
   3. 再递归右子树

   👉 这就是标准的 **先序遍历（Preorder）**

   ------

   ## 三、那为什么它还能判断 BST？（关键）

   因为你用的**不是“遍历顺序”**，而是 **BST 的定义本身**：

   > 对任意节点 `node`
   >  `low < node.val < high`

   ### `low / high` 从哪里来？

   - 左子树：`high = node.val`
   - 右子树：`low = node.val`

   📌 **每一层都带着“祖先节点的约束”往下走**。


### 红黑树

1. 为什么需要红黑树，他比BST（二叉查找树好在哪里？）
   1. bst的形状是根据节点插入的顺序决定的，如果按升序或者降序的方式插入，二叉查找树就会退化成一个线性的结构

#### 1. 红黑树的特性？

1. 每个节点或是红色的，或是黑色的。
   根节点是黑色的。
   所有叶子（NIL节点）都是黑色的。
   如果一个节点是红色的，则它的两个子节点都是黑色的。
   从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点。

#### 2. 红黑树和二叉查找平衡树的区别？

1. 红黑树和平衡二叉查找树（AVL树）都是自平衡的二叉查找树，它们都可以在对数时间内完成查找、插入和删除操作，但它们在平衡条件和具体操作上有所不同。下面是它们之间的一些主要区别：

   1. **平衡条件**：
      - **AVL树**：是一种高度平衡的二叉查找树，对于任何一个节点，其左子树和右子树的高度差（平衡因子）的绝对值不超过1。这意味着AVL树是严格平衡的。
      - **红黑树**：通过确保树中没有两个连续的红节点，并且从任一节点到其每个叶子的所有路径都包含相同数目的黑节点，来近似平衡。红黑树的这些条件确保树大致保持平衡，虽然不像AVL树那样严格。

   2. **插入和删除操作**：
      - **AVL树**：由于AVL树维护的是严格的平衡，所以在插入和删除节点时可能需要通过旋转操作来重新平ƒ衡树。这些操作可能相对复杂，尤其是在删除操作时。
      - **红黑树**：在插入和删除节点时，也可能需要通过旋转来调整树的平衡。但由于红黑树的平衡条件不像AVL树那样严格，所以通常红黑树的旋转操作会少于AVL树，使得在实际应用中，红黑树在插入和删除操作上可能更高效。

   3. **查找性能**：
      - **AVL树**：由于AVL树是高度平衡的，所以在最坏情况下，其查找性能略优于红黑树。
      - **红黑树**：尽管红黑树的平衡条件较为宽松，但它仍然能够保证在最坏情况下查找操作的时间复杂度为O(log n)，其中n是树中节点的数量。

   4. **应用场景**：
      - **AVL树**：由于其高度平衡的特性，AVL树更适合那些查找操作远多于插入和删除操作的应用场景。
      - **红黑树**：由于其在插入和删除操作上的高效性，红黑树更适合那些插入和删除操作频繁的应用场景，如在许多语言的标准库中实现的Map和Set等数据结构。

   总的来说，AVL树和红黑树各有优势，适用于不同的应用场景。选择哪一种取决于具体的需求，比如对平衡的严格程度、操作的频率和类型等因素的考虑。

### 图

#### 图的遍历算法

1. 用队列实现BFS，用栈实现DFS，递归其实也是一种DFS

##### BFS(breath first search)

1. usually to solve shortest route question





##### dfs

1. 可以用栈实现，也可以用函数递归调用来实现

   1. 本质上，用栈实现是一个显示栈，而函数递归调用是一个隐式栈

2. 比较一下两者的优劣？

   1. 使用栈实现深度优先搜索（DFS）而非递归调用的好处主要取决于具体的应用场景和环境。在某些情况下，使用栈的方法可能会有性能上的优势，但这并不总是绝对的。下面是一些考虑因素：

      ### 1. 栈溢出的避免

      - **递归方法**：在深度很大的搜索树上使用递归可能会导致调用栈溢出，因为每一次函数调用都会消耗一定的栈空间，而系统为每个线程分配的栈空间是有限的。
      - **栈方法**：使用显式的栈来控制搜索过程可以帮助避免这个问题，因为它使用的是堆空间，而堆空间一般远大于栈空间。

      ### 2. 性能开销的比较

      - **递归方法**：递归调用本身有一定的开销，每次递归调用都会增加额外的调用栈帧，包括参数传递、局部变量存储等。
      - **栈方法**：使用显式栈虽然可以避免调用栈的消耗，但管理栈的操作（如入栈、出栈）也会引入开销，并且代码可能更加复杂，增加了维护的难度。

      ### 3. 可读性和易用性

      - **递归方法**：递归方法通常更容易理解和实现，特别是对于树或图的深度优先搜索，递归的代码往往更直观、更简洁。
      - **栈方法**：虽然使用栈可以提供更细粒度的控制，但代码通常会更复杂，逻辑不那么直观。

      ### 结论

      选择使用递归还是栈实现DFS，主要取决于具体问题的需求和环境限制。如果搜索树的深度非常大，且存在栈溢出的风险，那么使用栈可能是更好的选择。如果搜索树的深度适中，且代码的可读性和易用性更为重要，递归方法可能更优。

      在性能方面，是否有明显的优势并不总是一致的，需要根据具体情况分析。在某些情况下，递归的性能可能完全可以接受，而且由于其简洁性，更易于实现和维护。在其他情况下，显式栈的方法可能由于可以避免栈溢出而更受青睐，尤其是在深度搜索或资源受限的环境中。

   2. the relationship between dfs and recursion?

      1. 递归和深度优先搜索（DFS）有很强的联系，因为递归本质上是一种天然的深度优先搜索方式。以下是它们之间的联系和区别：

         ### 递归和DFS的联系

         1. **递归实现DFS**：
            - 递归是一种编程技术，允许函数调用自身。
            - DFS是一种遍历或搜索树或图的算法，优先深入到树或图的最深处。
            - 递归可以非常自然地实现DFS，因为每次递归调用都会深入到更深的层次，直到到达叶子节点或终止条件。
            - 在递归实现的DFS中，系统调用栈隐式地充当了栈数据结构，管理函数调用和返回。

         2. **递归的特性**：
            - 每次递归调用都会将当前状态（如当前节点、路径和等）压入系统调用栈中。
            - 当递归调用返回时，系统调用栈会弹出这些状态，回溯到上一个状态。
            - 这种“压栈”和“弹栈”的机制与DFS使用显式栈的机制相同。

         ### 递归实现DFS的示例

         以二叉树的遍历为例，以下是递归实现的DFS：

         ```java
         public class Solution {
             public int sumNumbers(TreeNode root) {
                 return dfs(root, 0);
             }
         
             private int dfs(TreeNode node, int currentSum) {
                 if (node == null) {
                     return 0;
                 }
                 currentSum = currentSum * 10 + node.val;
                 // 如果是叶子节点，返回当前路径的和
                 if (node.left == null && node.right == null) {
                     return currentSum;
                 }
                 // 递归计算左子树和右子树的路径和
                 int leftSum = dfs(node.left, currentSum);
                 int rightSum = dfs(node.right, currentSum);
                 return leftSum + rightSum;
             }
         
             public static class TreeNode {
                 int val;
                 TreeNode left;
                 TreeNode right;
                 TreeNode(int x) { val = x; }
             }
         
             public static void main(String[] args) {
                 TreeNode root = new TreeNode(1);
                 root.left = new TreeNode(2);
                 root.right = new TreeNode(3);
         
                 Solution solution = new Solution();
                 System.out.println(solution.sumNumbers(root));  // 输出 25
             }
         }
         ```

         ### 递归和显式栈实现DFS的区别

         虽然递归和显式栈都可以实现DFS，但它们在实现细节上有所不同：

         1. **递归实现**：
            - 使用系统调用栈来管理递归调用。
            - 代码简洁，易于理解和实现。
            - 受限于系统调用栈的深度限制，可能导致栈溢出（stack overflow）。

         2. **显式栈实现**：
            - 使用显式的栈数据结构来模拟递归调用。
            - 代码相对复杂，需要手动管理栈的压入和弹出。
            - 不受系统调用栈深度限制，更适合处理深度较大的树或图。

         ### 显式栈实现DFS的示例

         ```java
         import java.util.Stack;
         
         public class Solution {
             public int sumNumbers(TreeNode root) {
                 if (root == null) {
                     return 0;
                 }
         
                 int totalSum = 0;
                 Stack<Pair> stack = new Stack<>();
                 stack.push(new Pair(root, 0));
         
                 while (!stack.isEmpty()) {
                     Pair current = stack.pop();
                     TreeNode node = current.node;
                     int currentSum = current.currentSum * 10 + node.val;
         
                     // 如果是叶子节点，累加当前路径的和
                     if (node.left == null && node.right == null) {
                         totalSum += currentSum;
                     }
         
                     // 如果有右子节点，压入栈中
                     if (node.right != null) {
                         stack.push(new Pair(node.right, currentSum));
                     }
         
                     // 如果有左子节点，压入栈中
                     if (node.left != null) {
                         stack.push(new Pair(node.left, currentSum));
                     }
                 }
         
                 return totalSum;
             }
         
             private static class Pair {
                 TreeNode node;
                 int currentSum;
         
                 Pair(TreeNode node, int currentSum) {
                     this.node = node;
                     this.currentSum = currentSum;
                 }
             }
         
             public static class TreeNode {
                 int val;
                 TreeNode left;
                 TreeNode right;
                 TreeNode(int x) { val = x; }
             }
         
             public static void main(String[] args) {
                 TreeNode root = new TreeNode(1);
                 root.left = new TreeNode(2);
                 root.right = new TreeNode(3);
         
                 Solution solution = new Solution();
                 System.out.println(solution.sumNumbers(root));  // 输出 25
             }
         }
         ```

         ### 总结

         - **递归**：自然实现DFS，代码简洁，但受系统调用栈限制。
         - **显式栈**：手动管理栈，实现DFS，不受系统调用栈限制。

         希望这些解释能帮助你理解递归和DFS之间的联系。如果有其他问题，欢迎继续提问！

###### 岛屿问题

1. https://leetcode.cn/problems/number-of-islands/solutions/211211/dao-yu-lei-wen-ti-de-tong-yong-jie-fa-dfs-bian-li-
2. 主要思路就是dfs走一遍，base condition是当前的坐标不在图的范围内，或者当前的值为0
   1. 为了避免走重复的路，需要对走过的路进行标记，直接标记为2就行
   2. 

###### 例题

1. 有些题目需要求根节点到叶子结点的所有路径，因为要找到一个叶子结点才算结束一个查找，所以需要dfs来最先找到一个符合条件的项

   [129. Sum Root to Leaf Numbers](https://leetcode.cn/problems/sum-root-to-leaf-numbers/)

#### 图的克隆

1. 优先考虑用递归的方式做，用显示栈的话会显的很麻烦，从编码角度来讲。
   1. 需要用哈希表记录一下已访问过的节点

#### 有向图，加权边（权>=0），求距离最小： Dijkstra 算法

1. 核心： 其实就是遍历每条边，但是是根据与当前已经访问的图相连的权值最小的边开始，依次访问，并在访问途中更新最小值 --》那为什么不从权值最大的边开始？是否最终也能得到一样的结果？

2. 理解有误，其实是 每次pop出来一个点，就已经确定了src到该点的最小距离

   1. 如果有其他路径，比当前最小路径还小，那么那条路径上的点肯定在其他点之前就被入队处理了-->所以不可能漏下
   2. 状态从邻接接点开始传播

3. 把 Dijkstra 想成 **水波扩散** 🌊：

   - 水从源点出发
   - 以“单位时间 = 边权”向外扩散
   - **最先被水淹到的点，一定是最短路径到达的**
   - 所以，为了找到接下来被水淹到的那个点，一定要从当前已知距离最近的点开始（最小堆）

4. ```python
   import heapq
   
   def dijkstra(graph, start):
       dist = {node: float('inf') for node in graph}
       dist[start] = 0
       pq = [(0, start)]
   
       while pq:
           cur_dist, u = heapq.heappop(pq)
   
           # 关键：跳过过期状态
           if cur_dist > dist[u]:
               continue
   
           for v, w in graph[u]:
               if dist[v] > cur_dist + w:
                   dist[v] = cur_dist + w
                   heapq.heappush(pq, (dist[v], v))
   
       return dist
   ```

   

#### How to determine if a graph has a cycle?

##### Topological Sorting

1. how to get topological sorting?

   1. ![image-20240716150702323](/Users/lanceliao/Library/Application Support/typora-user-images/image-20240716150702323.png)

   2. STEPs

      1. Build the in-degree array: to determine if a vertex can be reached

      2. Initialize the queue: we shall be begin visiting the vertex with 0 in-degree. so we need 0-indegree queue

      3. Togological sorting process:

         1. ```java
            while (!queue.isEmpty()) {
                        int vertex = queue.poll();
                        visitedCount++;
                        
                        for (int j = 0; j < numVertices; j++) {
                            if (adjMatrix[vertex][j] == 1) {
                                inDegree[j]--;
                                if (inDegree[j] == 0) {
                                    queue.add(j);
                                }
                            }
                        }
                    }
            ```

##### Example Problem

1. [207. Course Schedule](https://leetcode.cn/problems/course-schedule/)
2. 

## Algorithm 

### sliding window / two pointers

#### 1. What kind of problem can/cannot be solved by two pointers

1. https://leetcode.com/problems/subarray-sum-equals-k/solutions/301242/general-summary-of-what-kind-of-problem-can-cannot-solved-by-two-pointers/
   1. If a wider scope of the sliding window is valid, the narrower scope of that wider scope is valid
   2. If a narrower scope of the sliding window is invalid, the wider scope of that narrower scope is invalid
2. so in problem ([560. Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/)), since the element in nums can be negative, wider scope and narrow scope has no direct relation, so it can't be solved by two pointers.
3. 

#### example problems

1. https://leetcode.com/problems/binary-subarrays-with-sum/description/

#### kmp算法（一种字符串匹配算法）

##### 介绍

1. https://zhuanlan.zhihu.com/p/83334559
2. **KMP 算法永不回退 `txt` 的指针 `i`，不走回头路（不会重复扫描 `txt`），而是借助 `dp` 数组中储存的信息把 `pat` 移到正确的位置继续匹配**，时间复杂度只需 O(N)，用空间换时间，所以我认为它是一种动态规划算法。
3. 影子状态：

   1. 因为我们想尽可能少的回退状态，所以

   2. 相当于再来一个指针来匹配，转移，这样，只有当原来的指针再一次遇到了pat的前缀，影子状态才会更新。

   3. ```java
      class kmp{
        private int[][] dp;
        private char[] pat;
        
        
        
        
      }
      ```

      


##### 相关题目

1. [28. 找出字符串中第一个匹配项的下标](https://leetcode.cn/problems/find-the-index-of-the-first-occurrence-in-a-string/)

   1. ```java
      class Solution {
          public int strStr(String ss, String pp) {
              int n = ss.length(), m = pp.length();
              char[] s = ss.toCharArray(), p = pp.toCharArray();
              // 枚举原串的「发起点」
              for (int i = 0; i <= n - m; i++) {
                  // 从原串的「发起点」和匹配串的「首位」开始，尝试匹配
                  int a = i, b = 0;
                  while (b < m && s[a] == p[b]) {
                      a++;
                      b++;
                  }
                  // 如果能够完全匹配，返回原串的「发起点」下标
                  if (b == m) return i;
              }
              return -1;
          }
      }
      ```

   2. 把原串的每一个元素作为起点

   3. 该解法是一种暴力揭发，时间复杂度O(MN),

   

#### 滑动窗口+单调队列

![image-20250710001646252](/Users/lanceliao/Library/Application Support/typora-user-images/image-20250710001646252.png)

1. 

### subarrays

#### 1. the sum of subarrays

1. we can maintain a hash map to record the sum of nums[0.....i],
2. once we get the sum, we can find other sum, 
3. Lets say i want to find a subarray with sum k, what i do is, keep the ith sum, find if there exist its_sum - k in map,

### 递归

#### [124. Binary Tree Maximum Path Sum](https://leetcode.cn/problems/binary-tree-maximum-path-sum/)

1. 主要考虑的是递归的主体，然后再看边界条件，
2. 要求最大，首先看看这个最大的集合如何去寻找，按什么方式找？
3. 这道题中，就是说考虑以每个节点为根节点，然后路径经过这个根节点的值最大的节点。
4. <img src="/Users/lanceliao/Desktop/Screenshot 2024-05-23 at 11.07.44.png" alt="Screenshot 2024-05-23 at 11.07.44" style="zoom: 33%;" /> 
5. 然后再细分，要找到这样的路径，就得找左右子树的最大贡献值，（这里的最大贡献值指的是以这个节点为端点的路径的最大贡献值）

### 回溯 算法

#### 一般解题步骤

- 针对所给问题，定义问题的解空间，它至少包含问题的一个（最优）解。
- 确定易于搜索的解空间结构,使得能用回溯法方便地搜索整个解空间 。
- 以**深度优先的方式**搜索解空间，并且在搜索过程中用剪枝函数避免无效搜索。
  - 之所以要用深度优先，本质上是因为我们首先要走完一遍找出一个完整的符合要求的解，才能从继续
  - dfs可以用

#### 递归的终止？

1. 引子：[236. Lowest Common Ancestor of a Binary Tree](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/)

   1. 这道题中，我想要在一个二叉树中找到符合条件的节点，并返回根节点到该节点的路径（`List<TreeNode>`）,我原来的解法是：

      1. ```java
         public void dfs_p(TreeNode root, TreeNode p){
             if (root == null) { return; }
             path_p.add(root);
             if (root.val == p.val) {
                 return;
             }
             dfs_p(root.left, p);
             dfs_p(root.right, p);
             path_p.remove(path_p.size() - 1);
         }
         ```

      2. 想着是利用回溯的思路来做，先压入当前节点，先序遍历，如果找到则直接返回，如果没找到，找左子树和右子树，如果这两者都没有，把当前节点弹出。

      3. 然而，由于没有返回值，我不知道左右子树是否找到，这导致了不论左子树` dfs_p(root.left, p);`这个步骤中有没有找到，都不影响我继续寻找右子树,`dfs_p(root.right, p);`所以，如果返回值是void，我们很难通过直接的方式去控制递归的终止。

      4. 所以，应当用返回值boolean来控制。

         1. ```java
            private boolean findPath(TreeNode root, TreeNode target, List<TreeNode> path) {
                if (root == null) {
                    return false;
                }
                path.add(root);
                if (root.val == target.val) {
                    return true;
                }
                if (findPath(root.left, target, path) || findPath(root.right, target, path)) {
                    return true;
                }
                path.remove(path.size() - 1);
                return false;
            }
            ```

         2. 

#### 例题

##### [131. 分割回文串](https://leetcode.cn/problems/palindrome-partitioning/)

1. 代码

   1. ```java
      class Solution {
          private List<List<String>> ans = new ArrayList<>();
          private List<String> path = new ArrayList();
          private String s;
      
          public List<List<String>> partition(String s) {
              this.s = s;
              dfs(0);
              return ans;
      
          }
      
          private void dfs(int i){
              if(i==s.length()){
                  ans.add(new ArrayList<>(path));
                  return;
              }
              for(int j=i;j<s.length();j++){
                  if(isPalidrome(i,j)){
                      path.add(s.substring(i,j+1));
                      dfs(j+1);
                      path.remove(path.size()-1); //恢复现场
                  }
              }
          }
        // 判断是否为回味串
          public boolean isPalidrome(int left, int right){
              while(left<right){
                  if(s.charAt(left)!=s.charAt(right)){
                      return false;
                  }
                  left++;
                  right--;
              }
              return true;
          }
      }
      ```

   2. 恢复现场那一步，是递归地去除path的最后一个元素，直至状态返回到 `path.add(s.substring(i,j+1));`的前一步

   3. 这一步是回溯的精髓，即回退状态。

2. 既然是深度优先搜索，那我可不可以使用栈来做这道题呢，而不是用递归？ 会不会麻烦很多？

   1. 是的，您完全可以使用栈来实现深度优先搜索（DFS），而不是使用递归。使用栈的方法本质上是将递归调用的过程转换为迭代的形式。这种方法有时被称为"显式栈"DFS，因为它显式地使用一个栈来模拟递归过程中隐式的调用栈。

      使用栈来解决问题确实可能会稍微复杂一些，因为您需要手动管理栈，包括何时添加元素到栈中、何时从栈中移除元素，以及如何追踪每一步的状态。但是，这种方法为理解DFS提供了更深层次的视角，对于某些情况下优化性能或解决栈溢出问题也很有帮助。

      以下是使用栈来解决字符串分割为所有可能回文串的一个基本思路：

      1. 创建一个栈来保存当前的路径（已经找到的回文串）。
      2. 使用另一个栈来保存每一步的索引位置。
      3. 迭代地探索字符串，每次尝试一个新的可能的回文串分割，并将其加入路径栈。
      4. 如果找到一种分割方案，记录当前路径，然后回退到上一步，尝试其他可能的分割。
      5. 每次回退时，从栈中移除最后一个元素（上一次尝试的回文串）。

      这里是一个使用栈模拟递归过程的简化代码示例，注意这个示例主要是为了展示思路，可能需要根据实际问题调整：

      ```java
      import java.util.*;
      
      public class Solution {
          public List<List<String>> partition(String s) {
              List<List<String>> ans = new ArrayList<>();
              Stack<String> path = new Stack<>();
              Stack<Integer> indexStack = new Stack<>();
              indexStack.push(0); // 初始索引
      
              while (!indexStack.isEmpty()) {
                  int start = indexStack.peek(); // 当前探索起点
                  if (start == s.length()) {
                      ans.add(new ArrayList<>(path));
                      indexStack.pop();    // 回溯
                      if (!path.isEmpty()) {
                          path.pop();      // 恢复现场
                      }
                      continue;
                  }
                  boolean found = false;
                  for (int end = start; end < s.length(); end++) {
                      if (isPalindrome(s, start, end)) {
                          path.push(s.substring(start, end + 1));
                          indexStack.push(end + 1); // 探索下一个位置
                          found = true;
                          break;
                      }
                  }
                  if (!found) {
                      indexStack.pop(); // 回溯
                      if (!path.isEmpty()) {
                          path.pop(); // 恢复现场
                      }
                  }
              }
              return ans;
          }
      
          private boolean isPalindrome(String s, int left, int right) {
              while (left < right) {
                  if (s.charAt(left++) != s.charAt(right--)) {
                      return false;
                  }
              }
              return true;
          }
      }
      ```

      请注意，这个代码示例主要是为了演示如何使用栈来模拟递归过程，实际实现时可能需要根据具体问题进行调整。使用栈的方法相比递归，需要更多地手动管理状态，这可能会让代码看起来更加复杂。但对于某些情况，尤其是需要避免递归调用栈溢出的场景，使用栈来实现DFS是一个很好的选择。

### 排序

1. java 有没有办法对一个二维数组，根据它的每个数组的第一个元素的大小，对这个二维数组排序？

   1. 在 Java 中，你可以使用 `Arrays.sort()` 方法来对二维数组进行排序，但是需要自定义比较器（Comparator）来指定排序规则。对于二维数组，你可以创建一个自定义的比较器，根据每个数组的第一个元素的大小来进行排序。

      以下是一个示例代码，演示如何对一个二维数组根据每个数组的第一个元素的大小进行排序：

      ```java
      import java.util.Arrays;
      import java.util.Comparator;
      
      public class Main {
          public static void main(String[] args) {
              int[][] array = {{3, 2}, {1, 4}, {2, 1}};
      
              // 使用自定义比较器按每个数组的第一个元素进行排序
              Arrays.sort(array, Comparator.comparingInt(a -> a[0]));
      
              // 打印排序后的二维数组
              for (int[] row : array) {
                  System.out.println(Arrays.toString(row));
              }
          }
      }
      ```

      在上面的示例中，我们首先定义了一个二维数组 `array`，然后使用 `Arrays.sort()` 方法和自定义的比较器 `Comparator.comparingInt(a -> a[0])` 对二维数组进行排序，该比较器按每个数组的第一个元素进行比较。最后，我们打印出排序后的二维数组。

2. 请你解释一下Arrays.sort(array, Comparator.comparingInt(a -> a[0]));这行代码的语法，并举其它例子说明自定义比较器是怎么用的

   1. 这行代码 `Arrays.sort(array, Comparator.comparingInt(a -> a[0]));` 的语法解释如下：

      - `Arrays.sort(array, ...)`：这部分调用了 `Arrays` 类中的 `sort` 方法，用于对数组进行排序。
      - `Comparator.comparingInt(a -> a[0])`：这部分是一个比较器，使用了 `Comparator` 类的 `comparingInt` 静态方法。在这里，`a -> a[0]` 是一个 Lambda 表达式，表示比较器会根据每个数组的第一个元素进行比较。

      另外，下面是一个例子说明如何使用自定义比较器来对对象列表进行排序：

      ```java
      import java.util.ArrayList;
      import java.util.Comparator;
      import java.util.List;
      
      class Person {
          String name;
          int age;
      
          public Person(String name, int age) {
              this.name = name;
              this.age = age;
          }
      
          @Override
          public String toString() {
              return "Person{name='" + name + "', age=" + age + "}";
          }
      }
      
      public class Main {
          public static void main(String[] args) {
              List<Person> personList = new ArrayList<>();
              personList.add(new Person("Alice", 25));
              personList.add(new Person("Bob", 30));
              personList.add(new Person("Charlie", 20));
      
              // 使用自定义比较器按年龄进行排序
              personList.sort(Comparator.comparingInt(Person::getAge));
      
              // 打印排序后的对象列表
              for (Person person : personList) {
                  System.out.println(person);
              }
          }
      }
      ```

      在上面的例子中，我们定义了一个 `Person` 类表示人员，然后创建了一个包含 `Person` 对象的列表 `personList`。我们使用 `Comparator.comparingInt(Person::getAge)` 来创建一个比较器，根据每个对象的年龄进行排序。最后，我们调用 `sort()` 方法对对象列表进行排序，并打印排序后的列表。

       1. Person::getName ::是什么意思?

          1. 在 Java 中，`Person::getName` 是一种方法引用（Method Reference）的写法。方法引用是用来简化 Lambda 表达式的一种方式，可以直接引用现有方法（静态方法、实例方法或构造方法），而不用重新编写一个Lambda表达式来调用该方法。

             在这种情况下，`Person::getName` 表示引用 `Person` 类中的 `getName` 方法。这种写法等价于使用 Lambda 表达式来调用 `getName` 方法，例如 `(person) -> person.getName()`。

             具体来说：

             - `Person::` 表示引用 `Person` 类中的方法。
             - `getName` 表示要引用的方法名称。

             因此，`Person::getName` 表示引用 `Person` 类中的 `getName` 方法，而不是直接调用该方法。这种写法在需要传递方法作为参数的情况下非常有用，可以使代码更加简洁和易读。

#### 1. 快速排序 QuickSort

1. 核心思想

   1. 冒泡排序+分治
      1. 每次都挑一个最左边的元素作为基准值，然后遍历数组，将比基准值小的元素都交换到基准值的左边
      2. 然后基准值就确定了它的位置，但是它左右两边的数组还是乱序的，于是对这两边递归地使用快速排序。
      3. 这有点像利用前序遍历+中序遍历 或者 后续遍历+中序遍历 构造二叉树，
         1. 

2. 代码示例

   1. ```Java
      public class QuickSort {
      
          // 快速排序主方法
          public static void quickSort(int[] arr, int left, int right) {
              if (left < right) {
                  // 分区操作：返回基准值的最终位置
                  int pivotIndex = partition(arr, left, right);
      
                  // 对左右子数组递归排序
                  quickSort(arr, left, pivotIndex - 1);
                  quickSort(arr, pivotIndex + 1, right);
              }
          }
      
          // 分区函数，返回 pivot 的最终位置
          private static int partition(int[] arr, int left, int right) {
              int pivot = arr[right];  // 选择最后一个元素作为基准
              int i = left - 1;        // 小于 pivot 的区域的尾部指针
      
              for (int j = left; j < right; j++) {
                  if (arr[j] <= pivot) {
                      i++;
                      swap(arr, i, j);
                  }
              }
      
              // 把 pivot 放到正确的位置
              swap(arr, i + 1, right);
              return i + 1;
          }
      
          // 交换数组元素
          private static void swap(int[] arr, int i, int j) {
              int temp = arr[i];
              arr[i] = arr[j];
              arr[j] = temp;
          }
      
          // 测试入口
          public static void main(String[] args) {
              int[] nums = {5, 2, 9, 1, 5, 6};
              quickSort(nums, 0, nums.length - 1);
      
              for (int num : nums) {
                  System.out.print(num + " ");
              }
              // 输出：1 2 5 5 6 9
          }
      }
      ```

3.  随机选一个pivot的值，这样的话可以避免1234567这样子的极端情况

   ```python
           
           def partition(nums:List[int], left:int, right:int) -> int:
               if left==right:
                   return left
               pivot_index = random.randint(left, right)
               nums[pivot_index], nums[right] = nums[right], nums[pivot_index]
               pivot = nums[right]
               index = left
               # 从左至右扫描。把所有小于
               for j in range(left,right):
                   if nums[j] < pivot
                       nums[j], nums[index] = nums[index], nums[j]
                       index+=1
               
               nums[right],nums[index] = nums[index], nums[right]
               return index
                   
   
           def quicksort(nums: List[int], left:int, right:int):
   
               if left>=right:
                   return
               partion = partition(nums,left,right)
               quicksort(nums,left,partion-1)
               quicksort(nums,partion+1,right)
   
           quicksort(nums,0,len(nums)-1)
           return nums
   ```

4. 进一步优化：处理 2，2，2，2，2，2，2，2这类的情况

   1. 三路排序

   2. ```python
      import random
      
      class Solution:
          def sortArray(self, nums):
      
              def quicksort(left, right):
                  if left >= right:
                      return
      
                  pivot = nums[random.randint(left, right)]
      
                  lt = left      # nums[left .. lt-1] < pivot
                  i = left       # nums[lt .. i-1] == pivot
                  gt = right     # nums[gt+1 .. right] > pivot
      
                  while i <= gt:
                      if nums[i] < pivot:
                          nums[lt], nums[i] = nums[i], nums[lt]
                          lt += 1
                          i += 1
                      elif nums[i] > pivot:
                          nums[i], nums[gt] = nums[gt], nums[i]
                          gt -= 1
                      else:
                          i += 1
      
                  quicksort(left, lt - 1)
                  quicksort(gt + 1, right)
      
              quicksort(0, len(nums) - 1)
              return nums
      
      ```

      

##### 多指针判断循环条件：定义好指针的语义，明确区间的两个端点

为什么循环判断条件为什么是<= 而不是 <? 

1. 这是**三路快排里最容易被问、但也最容易被“机械记忆”的一个点**。
   你这个问题问得非常好，说明你已经在**真正理解算法不变量（invariant）**了。

   我按 **「区间语义 → 不变量 → 反例」** 三步给你讲清楚。

   ------

   ## 一、先给每个指针一个**明确的语义**

   在这段代码里（我用你原变量名）：

   ```python
   lt = left
   i  = left
   bt = right
   pivot = ...
   ```

   我们**始终维护下面 4 个区间不变量**：

   ```
   [left      ... lt-1]  < pivot
   [lt        ... i-1 ]  == pivot
   [i         ... bt  ]  未处理
   [bt+1      ... right] > pivot
   ```

   👉 **关键点**：
   `i ... bt` 是「**尚未检查**」的区域

   ------

   ## 二、为什么循环条件必须是 `i <= bt`

   ### 1️⃣ 因为 `bt` 位置 **还没被处理**

   只要满足：

   ```text
   i <= bt
   ```

   就说明：

   > 至少还有 **一个未知元素** 需要分类

   ------

   ### 2️⃣ 当 `i == bt` 时会发生什么？

   此时区间变成：

   ```
   [i == bt]  ← 只剩一个元素没检查
   ```

   这个元素：

   - 可能 `< pivot`
   - 可能 `== pivot`
   - 可能 `> pivot`

   👉 **必须处理它一次**

   如果你用的是：

   ```python
   while i < bt:
   ```

   那么：

   - 当 `i == bt` 时
   - 循环直接退出
   - **这个元素永远没被分类**

   ❌ 不变量被破坏

   ------

   ## 三、用一个最小反例直接说明 `<` 会错

   ### 示例

   ```python
   nums = [2, 1]
   pivot = 2
   ```

   初始状态：

   ```
   lt = 0, i = 0, bt = 1
   ```

   ### 如果用 `while i < bt`

   #### 第 1 轮

   - i = 0 < 1 ✔
   - nums[0] == pivot → i += 1

   #### 第 2 轮

   - i = 1
   - i < bt ❌（1 < 1 为假）
   - 循环结束

   👉 **nums[1] = 1 从未被处理**

   最终数组仍是：

   ```python
   [2, 1]  # 错的
   ```

   ------

   ### 而 `while i <= bt`：

   #### 第 2 轮

   - i = 1 <= 1 ✔
   - nums[1] < pivot
   - swap 到左边
   - 排序正确完成

   ------

   ## 四、为什么在 `nums[i] > pivot` 时 **i 不动**

   这是同一层逻辑，顺带一起理解会很通。

   ```python
   elif nums[i] > pivot:
       nums[i], nums[bt] = nums[bt], nums[i]
       bt -= 1
   ```

   原因一句话：

   > 从 `bt` 换过来的元素是「未知的」，必须重新检查

   所以：

   - 不能 `i += 1`
   - 仍然停在 `i`
   - 这也是为什么需要 `i <= bt`

   ------

   ## 五、循环终止时，发生了什么？

   当循环结束：

   ```python
   i > bt
   ```

   说明：

   ```
   未处理区间 [i ... bt] 为空
   ```

   此时不变量自然收敛为：

   ```
   [left ... lt-1] < pivot
   [lt   ... bt ] == pivot
   [bt+1 ... right] > pivot
   ```

   👉 中间整段 `== pivot`
   👉 不再递归
   👉 性能直接起飞 🚀

   ------

   ## 六、一句话总结（非常像面试答案）

   > 因为 `i` 到 `bt` 表示尚未处理的区间，当 `i == bt` 时仍然有一个元素需要分类；只有使用 `i <= bt` 才能保证所有元素都被处理一次，维护三路快排的不变量。

   ------

   你现在问的已经是 **算法 invariant 层面的问题**，不是「模板怎么背」。
   如果你愿意，我可以下一步带你：

   - 用 **形式化不变量证明**这段循环的正确性
   - 或帮你把这段话压缩成 **15 秒白板解释版**（非常适合面试）

   你选一个。



#### 2. 归并排序

1. 主要思想就是

   1. 对一个数组切成一半

   2. 递归地对这两半进行归并排序

   3. 最后合并这两个已经拍过序的数组

      1. 怎么合并？

      2. 对于一个数组的两部分，用两个临时数组来存储，然后用两个指针分别比较临时数组的元素，哪个小就放到前面，最后复制剩余元素。

         ```java
         public class MergeSort {
             // 主方法，用于调用归并排序
             public static void main(String[] args) {
                 int[] arr = {12, 11, 13, 5, 6, 7};
                 System.out.println("给定的数组");
                 printArray(arr);    
         		MergeSort ob = new MergeSort();
             ob.sort(arr, 0, arr.length - 1);
         
             System.out.println("\n排序后的数组");
             printArray(arr);
         }
         
         // 归并排序的主要方法
         void sort(int arr[], int l, int r) {
             if (l < r) {
                 // 找到中间点
                 int m = (l + r) / 2;
         
                 // 分别对左右半边进行排序
                 sort(arr, l, m);
                 sort(arr, m + 1, r);
         
                 // 合并两个有序部分
                 merge(arr, l, m, r);
             }
         }
         
         // 合并方法，用于合并两个有序部分
         void merge(int arr[], int l, int m, int r) {
             // 计算两个部分的大小
             int n1 = m - l + 1;
             int n2 = r - m;
         
             // 创建临时数组
             int L[] = new int[n1];
             int R[] = new int[n2];
         
             // 复制数据到临时数组
             for (int i = 0; i < n1; ++i)
                 L[i] = arr[l + i];
             for (int j = 0; j < n2; ++j)
                 R[j] = arr[m + 1 + j];
         
             // 合并临时数组
         
             // 初始化索引
             int i = 0, j = 0;
         
             // 初始合并数组的索引
             int k = l;
             while (i < n1 && j < n2) {
                 if (L[i] <= R[j]) {
                     arr[k] = L[i];
                     i++;
                 } else {
                     arr[k] = R[j];
                     j++;
                 }
                 k++;
             }
         
             // 复制剩余的L[]元素
             while (i < n1) {
                 arr[k] = L[i];
                 i++;
                 k++;
             }
         
             // 复制剩余的R[]元素
             while (j < n2) {
                 arr[k] = R[j];
                 j++;
                 k++;
             }
         }
         
         // 用于打印数组的方法
         static void printArray(int arr[]) {
             int n = arr.length;
             for (int i = 0; i < n; ++i)
                 System.out.print(arr[i] + " ");
             System.out.println();
         }
         }
         
         ```

### UnionFind 并查集

1. 参考
   1. https://iyukiyama.github.io/union-find/
2. quick review
   1. parent array
   2. union
      1. first use find ==> find root
      2. Union two roots
   3. find

3. ```python
   class Solution:
       def countComponents(self, n: int, edges: List[List[int]]) -> int:
           parent = list(range(n))
           rank = [0] * n
   
           def find(x):
               if parent[x] != x:
                   parent[x] = find(parent[x])
               return parent[x]
   
           def union(x, y):
               rx, ry = find(x), find(y)
               if rx == ry:
                   return
               if rank[rx] < rank[ry]:
                   parent[rx] = ry
               elif rank[rx] > rank[ry]:
                   parent[ry] = rx
               else:
                   parent[ry] = rx
                   rank[rx] += 1
   
           for u, v in edges:
               union(u, v)
   
           return len({find(i) for i in range(n)})
   ```

   

#### Example Problem

1. https://leetcode.cn/problems/longest-consecutive-sequence/
2. 

### Divide and conquer

#### tricks

1. When you want to divide the problem into small parts, do not copy the context of original problem and start a new one, lets say if you want to Merge lists on a list array, the first thing you need to do is to break it into 2 arrays, and merge them recursively. At this point, do not make 2 new arrays, instead, make a new function, and pass the index of the array to this function.
2. if you want divide and conquer, make sure that there are always multiple functions working at one time.

#### Examples

1. [148. Sort List](https://leetcode.com/problems/sort-list/)

   1. My solution （）

      1. ```java
         /**
          * Definition for singly-linked list.
          * public class ListNode {
          *     int val;
          *     ListNode next;
          *     ListNode() {}
          *     ListNode(int val) { this.val = val; }
          *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
          * }
          */
         class Solution {
             public ListNode sortList(ListNode head) {
         
                 if(head==null){return null;}
                 if(head.next==null){return head;}
                 ListNode curNode = head;
                 ListNode preNode = head;
                 ListNode LeastNode = new ListNode();
                 ListNode preLeastNode = new ListNode();
                 int minVal = Integer.MAX_VALUE;
                 while(curNode!=null){
                     int curVal = curNode.val;
                     if(curVal<minVal){
                         minVal = curVal;
                         LeastNode = curNode;
                         preLeastNode = preNode;
                     }
                     preNode = curNode;
                     curNode = curNode.next;
                 }
         
                 ListNode LastNode = preNode;
                 
                     
                 if(LeastNode == LastNode){
                     LeastNode.next =  head;
                     preLeastNode.next = null;
                 }else{
                     LastNode.next = head;
                     preLeastNode.next = null;
                 }
         
         
                 LeastNode.next = sortList(LeastNode.next);
                 return LeastNode;
         
             }
         }
         ```

      2. fix

         1. ```java
            class Solution {
                public ListNode sortList(ListNode head) {
                    if (head == null || head.next == null) {
                        return head;
                    }
            
                    ListNode leastNode = head;
                    ListNode leastPrev = null;
                    ListNode curNode = head;
                    ListNode prevNode = null;
            
                    // Find the minimum node
                    while (curNode != null) {
                        if (curNode.val < leastNode.val) {
                            leastNode = curNode;
                            leastPrev = prevNode; // Track the previous node of the least node
                        }
                        prevNode = curNode;
                        curNode = curNode.next;
                    }
            
                    // Remove the least node from the list
                    if (leastPrev != null) {
                        leastPrev.next = leastNode.next; // Bypass leastNode
                    } else {
                        head = leastNode.next; // If leastNode is head
                    }
            
                    // Recursively sort the remaining list
                    leastNode.next = sortList(head);
            
                    return leastNode; // Return the sorted list starting with leastNode
                }
            }
            
            ```

         2. Use divide and conquer:

            1. ```java
               
               class Solution {
                   public ListNode findMiddle(ListNode head) {
                       if (head == null) {
                           return null;
                       }
                       ListNode fastPointer = head.next; // we want to split the list evenly, so we need head.next
                       ListNode slowPointer = head;
               
                       // Move fastPointer two steps and slowPointer one step
                       while (fastPointer != null && fastPointer.next != null) {
                           fastPointer = fastPointer.next.next;
                           slowPointer = slowPointer.next;
                       }
                       return slowPointer; // Returns the middle node
                   }
               
                   public ListNode merge(ListNode left, ListNode right) {
                       ListNode temp = new ListNode(-1); // Dummy node
                       ListNode curNode = temp;
               
                       while (left != null && right != null) {
                           if (left.val <= right.val) {
                               curNode.next = left;
                               left = left.next;
                           } else {
                               curNode.next = right;
                               right = right.next;
                           }
                           curNode = curNode.next; // Move the current pointer
                       }
               
                       // Append any remaining nodes
                       if (left != null) {
                           curNode.next = left;
                       }
                       if (right != null) {
                           curNode.next = right;
                       }
                       return temp.next; // Return the merged list, skipping the dummy node
                   }
               
                   public ListNode sortList(ListNode head) {
                       if (head == null || head.next == null) {
                           return head; // Base case: the list is empty or has one node
                       }
                   // Find the middle of the list
                   ListNode middleNode = findMiddle(head);
                   
                   // Split the list into two halves
                   ListNode rightHead = middleNode.next;
                   middleNode.next = null; // Important: split the list
                   
                   // Sort each half
                   ListNode left = sortList(head);
                   ListNode right = sortList(rightHead);
                   
                   // Merge sorted halves
                   return merge(left, right);
                   }
               }
               
               ```

   2. fda

      1. my solution (has bug)

         1. ```java
            class Solution {
                public Node construct(int[][] grid) {
                    int n = grid.length;
                    Node root = new Node(false, false);
            
                if (n == 2) {
                    Node topLeft = new Node(grid[0][0] == 1, true);
                    Node topRight = new Node(grid[0][1] == 1, true);
                    Node bottomLeft = new Node(grid[1][0] == 1, true);
                    Node bottomRight = new Node(grid[1][1] == 1, true);
            
                    if (topLeft.val && topRight.val && bottomLeft.val && bottomRight.val) {
                        root.isLeaf = true;
                        root.val = true;
                    } else if (!topLeft.val && !topRight.val && !bottomLeft.val && !bottomRight.val) {
                        root.isLeaf = true;
                        root.val = false;
                    }else{
                        root.topLeft = topLeft;
                        root.topRight = topRight;
                        root.bottomLeft = bottomLeft;
                        root.bottomRight = bottomRight;
                    }
            
                } else {
                    // Divide
                    int middle = n / 2;
                    int[][] TopLeftGrid = new int[middle][middle];
                    int[][] TopRightGrid = new int[middle][middle];
                    int[][] BottomLeftGrid = new int[middle][middle];
                    int[][] BottomRightGrid = new int[middle][middle];
            
                    for (int i = 0; i < middle; i++) {
                        for (int j = 0; j < middle; j++) {
                            TopLeftGrid[i][j] = grid[i][j];
                            TopRightGrid[i][j] = grid[i][j + middle];
                            BottomLeftGrid[i][j] = grid[i + middle][j];
                            BottomRightGrid[i][j] = grid[i + middle][j + middle];
                        }
                    }
            
                    Node topLeft = construct(TopLeftGrid);
                    Node topRight = construct(TopRightGrid);
                    Node bottomLeft = construct(BottomLeftGrid);
                    Node bottomRight = construct(BottomRightGrid);
            
                    if (topLeft.isLeaf && topRight.isLeaf && bottomLeft.isLeaf && bottomRight.isLeaf) {
                        if (topLeft.val && topRight.val && bottomLeft.val && bottomRight.val) {
                            root.val = true;
                            root.isLeaf = true;
                        } else if(!topLeft.val && !topRight.val && !bottomLeft.val && !bottomRight.val){
                            root.val = false;
                            root.isLeaf = true; // This should remain false if not all are true
                        }
                        return root;
                    } 
                    root.val = false;
                    root.topLeft = topLeft;
                    root.topRight = topRight;
                    root.bottomLeft = bottomLeft;
                    root.bottomRight = bottomRight;
                }
            
                return root;
            }
            }
            ```

      2. 

### priority queue

1. [502. IPO](https://leetcode.com/problems/ipo/)

   1. my solution (out of time limitation)

      1. ```java
         class Solution {
             public int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
         
                 //because k is limited, we need to invest to the most profitable project under the 
                 // limitation of w
                 // so what we do is to find all the project available unber current w, and pick
                 // the most profitable project.
                 int project_num = 0;
                 int n = profits.length;
                 List<Integer> chosen_project = new LinkedList<>();
                 int total=w;
                 while(project_num<k){
                     //bind the capital and profits, and sort it in different ways
                     int max_profit=0;
                     int index =-1;
                     for(int i=0;i<n;i++){
                         if(capital[i]<=w&&!chosen_project.contains(i)){
                             if(profits[i]>max_profit){
                                 index = i;
                                 max_profit = profits[i];
                             }
                         }
                     }
                     chosen_project.add(index);
                     total+=max_profit;
                     w+=max_profit;
                     project_num++;
                 }
                 return total;
             }
         }
         ```


2. [373. Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/)

   1. how to priority queue to sort a structure?

      1. ```java
         PriorityQueue<Triple> pq = new PriorityQueue<>((a, b) -> a.value - b.value);
         ```

         1. based on one piece of infomation of Triple to sort all the Triple in the line 
         2. you don't have to include all the Triples in your queue, instead, adding them dynamically.
            1. which is the main difference with List.sort(), which would only sort when you call the fuction, but if you add the element to the priority queue, it will automatically put the element in the right place.


3. [295. Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)

   1. my solution

      1. ```java
         class MedianFinder {
         
             // implement 2 heaps, one is min-heap for the median and bigger numbers
             // another is max_heap for the median and lower
             
             private PriorityQueue<Integer> pq;
             private int count;
         
             public MedianFinder() {
                 pq = new PriorityQueue<>();
                 count=0;
             }
             
             public void addNum(int num) {
                 pq.add(num);
                 count++;
             }
             
             public double findMedian() {
                 PriorityQueue<Integer> temp = new PriorityQueue<>(pq);
                 if(count%2==0){
                     int low_median = count/2-1;
                     int index=0;
                     int value=0;
                     while(index<=low_median){
                         value = temp.poll();
                         index++;
                     }
                     int high = temp.poll();
                     return (double) (value+high) / (double)2.0;
                 }else{
                     int median_index = (count-1) /2;
                     int index=0;
                     int median=0;
                     while(index<=median_index&&!temp.isEmpty()){
                         median = temp.poll();
                         index++;
                     }
                     return (double) median;
                 }
             }
         }
         
         /**
          * Your MedianFinder object will be instantiated and called as such:
          * MedianFinder obj = new MedianFinder();
          * obj.addNum(num);
          * double param_2 = obj.findMedian();
          */
         ```


### Dynamic programming

1. [123. Best Time to Buy and Sell Stock III](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)

   1. My solution(out of time limitation)

      1. ```java
         class Solution {
             public int maxProfit(int[] prices) {
                 //dp[i][j] means sell on i, j day to get the max profit, i<=j, if i==j means, only has 1 ransactions
         
                 int n = prices.length;
                 int[] dp = new int[n];
                 int maxProfit =0;
                 dp[0] = 0;
         
                 int minPrice= prices[0];
                 for(int k=1;k<n;k++){
                     minPrice = Math.min(minPrice, prices[k]);
                     dp[k] = prices[k] - minPrice;
                     maxProfit = Math.max(maxProfit, dp[k]);
                     
                 }
                 
                 for(int i=1;i<n;i++){
                     int min_2 = prices[i];
                     for(int j=i+1;j<n;j++){
                         min_2 = Math.min(min_2,prices[j]);
                         int i_j = dp[i] + prices[j]-min_2;
                         maxProfit = Math.max(maxProfit,i_j);
                     }
                 }
         
                 return maxProfit;
         
             }
         }
         ```

      2. 

## 杂题

### [26. 删除有序数组中的重复项](https://leetcode.cn/problems/remove-duplicates-from-sorted-array/)

1. 这段程序可以怎么优化？

   ```c++
     int removeDuplicates(vector<int>& nums) {
           int j= INT_MAX ;
           for(int i=0;i<nums.size();i++){
               if(nums[i]==j){
                   nums.erase(nums.begin()+i);
                   i--;
               }
               j = nums[i];
           }
           return nums.size();
       } 
   ```

   1. 这段程序可以通过使用**双指针**来优化，从而将时间复杂度降至 O(n)。以下是优化后的代码：

      ```c++
      int removeDuplicates(vector<int>& nums) {
          if (nums.empty()) {
              return 0;
          }
          
          int i = 0;
          for (int j = 1; j < nums.size(); j++) {
              if (nums[j] != nums[i]) {
                  i++;
                  nums[i] = nums[j];
              }
          }
          
          return i + 1;
      }
      
      ```

      1. 在上面的代码中，我们使用了两个指针 i 和 j，其中 i 指向当前没有重复元素的位置，而 j 则用于遍历整个数组。当发现 nums[j] 与 nums[i] 不同时，将 nums[j] 赋值给 nums[i+1]，并将 i 向前移动一位。这样，我们可以保证 nums[0, i] 中的元素都是不重复的。最后返回值为 i+1，即不重复元素的数量。


         这种方法的时间复杂度为 O(n)，因为我们只需要遍历一次数组就可以完成任务，而不需要像原始代码中那样每次删除重复元素。
    
      2. 分析下上面我写的代码的时间复杂度？
    
         1. `erase` 函数的时间复杂度是 O(n)，因为它需要将要删除位置之后的所有元素向前移动，以填补删除后的空缺。这意味着，如果要删除的元素位于数组的开头，那么所有元素都需要向前移动一位；如果要删除的元素位于数组的中间，那么要删除元素之后的所有元素都需要向前移动一位。这个过程需要遍历所有要移动的元素，因此时间复杂度为 O(n)。
    
            需要注意的是，如果您只需要删除 vector 中的最后一个元素，可以使用 `pop_back` 函数来完成，其时间复杂度为常数级别 O(1)。
    
         2. 上面的代码中使用了一个 for 循环来遍历整个数组，时间复杂度为 O(n)。在循环中，我们还使用了一个 if 语句来判断当前元素是否与前一个元素相同，这需要常数时间。在 if 语句的条件为真时，我们还需要调用 `erase` 函数来删除当前元素，这需要 O(n) 的时间复杂度。因此，如果数组中有大量重复元素，那么 `erase` 函数的调用次数也会很多，导致时间复杂度变高。
    
            综上所述，上面的代码的时间复杂度为 O(n^2)。如果数组中有大量重复元素，则该算法的性能会变得很差。

### [189. 轮转数组](https://leetcode.cn/problems/rotate-array/)

1. 我写的代码（有错误）

   1. ```c++
          void rotate(vector<int>& nums, int k) {
              int pos = 0;
              vector<int>* num_second  = new vector<int>();
              int total = nums.size();
              for(int j=0;j<total;j++){
                  pos = (j+k)%total;
                  num_second[pos] = nums[j];
              }
              nums = num_second;
              delete num_second;
              num_second = nullptr;
              return null;
          }
      ```

   2. 错误：

      1. 这段代码存在几个错误：

         1. `num_second` 是一个指向 `vector<int>` 的指针，但没有初始化为一个有效的对象。在使用指针之前，需要通过 `new` 运算符来分配内存并创建一个新的 `vector<int>` 对象。

         2. 在循环中，将 `nums[j]` 赋值给 `num_second[pos]`，但是 `num_second` 是一个指针，不能像数组那样直接通过索引进行赋值。应该使用 `push_back()` 函数将元素添加到 `num_second` 中。

         3. 在最后的返回语句中，使用了 `null`，但正确的写法应该是 `nullptr`。

         下面是修改后的代码示例：

         ```cpp
         int pos = 0;
         vector<int>* num_second = new vector<int>();  // 创建一个新的 vector<int> 对象
         
         int total = nums.size();
         for (int j = 0; j < total; j++) {
             pos = (j + k) % total;
             num_second->push_back(nums[j]);  // 将元素添加到 num_second 中
         }
         
         nums = *num_second;  // 将 num_second 的内容赋值给 nums
         
         delete num_second;
         num_second = nullptr;
         
         return nullptr;  // 使用 nullptr 表示空指针
         ```

         通过这些修改，代码中的错误得到了修正，并且可以正常运行。

   3. **这里的nums 是由**` vector<int>& nums`定义的**引用**，就是一个对象，可以直接拿来用。

      1. 所以` nums = *num_second;` 这里的赋值应该是` num_second`指向的对象。

2. 正确答案

   1. 这是需要额外分配空间的做法	

   2. ```c++
          void rotate(vector<int>& nums, int k) {
              int pos = 0;
              vector<int>* num_second  = new vector<int>(nums.size());
              int total = nums.size();
              for(int j=0;j<total;j++){
                  pos = (j+k)%total;
                  (*num_second)[pos] = nums[j];
              }
              nums = *num_second;
              delete num_second;
              num_second = nullptr;
      }
      ```

3. 解法二：环状替换 （不需要额外空间，仅需要一个变量用来保存要替换的值）

   1. ```c++
      	void rotate(vector<int>& nums, int k){
          int n = nums.size();
          k = k%n;
          int count = gcd(k,n);
          for(int start = 0; start<count;start++){
            int current = start;
            int prev = nums[start];
            do{
              int next = (start+k)%n;
              swap(nums[next],prev);
              current = next;
            }while(start != current);
          }
          
          
        }
      ```

      1. 核心想法是从1开始然后替换，比如说 ` 1,2,3,4,5,6,7`, k =2 , 那么仅需要一次就可以全部遍历完，顺序是` 1,3,5,7,2,4,6,1` 但是如果` 1,2,3,4,5,6,` 则需要两次遍历` 1,3,5,1` 和 ` 2,4,6,2`,
      2. 那么，如何确定遍历的次数？
         1. 已知 元素总数是n, 每跳一步是k，那么因为最后还是会回到最初的起点，所以是走过了整数数量的圈，不妨设遍历了a圈，然后这一圈遍历了b个元素，那么有 an = bk，又要a最小，所以 an就是n, k 的最小公倍数lcm。 又 所以 b = lcm/k， 遍历次数就是 n / （b） = lcm/k 就是n, k的最大公约数。

### [121. 买卖股票的最佳时机](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)

1. 解法一，暴力 （超时）

   1. ```c++
      class Solution {
      public:
          int maxProfit(vector<int>& prices) {
              int n = prices.size();
              if(n == 0){return 0;}
              int maxP = 0;
              for(int i=0;i<n;i++){
                  for(int j=i+1;j<n;j++){
                      if(prices[j]-prices[i]>maxP){
                          maxP = prices[j]-prices[i];
                      }
                  }
              }
              return maxP;
      
          }
      };
      ```

2. 解法二

   1. ```c++
      class Solution {
      public:
          int maxProfit(vector<int>& prices) {
              int inf = 1e9;
              int minprice = inf;
              int maxprofit = 0;
              for(int price : prices){
                  maxprofit = max ( maxprofit, price - minprice);
                  minprice = min(price, minprice);
              }
              return maxprofit;
          }
      };
      ```

   2. 第二种解析其实是一种动态的变化，在遍历向前推进时，找到一个最小买入价格minprice，然后，在没有找到下一个更小的买入价格时，计算接下来每一天的利润，记录其中最大利润。如果找到下一个最小买入价格minprice，继续计算接下来未找到下一个更小买入价格时的利润最大值，直到遍历完prices数组，maxProfit就是历史最大差值！

### [55. 跳跃游戏](https://leetcode.cn/problems/jump-game/)

1. **贪心算法**

   1. ```c++
      class Solution {
      public:
          bool canJump(vector<int>& nums) {
              int k = 0;
              for(int i=0;i<nums.size();i++){
                  if(i>k){return false;}
                  k = max(k,i+nums[i]);
              }
              return true;
          }
      };
      ```

### [45. 跳跃游戏 II](https://leetcode.cn/problems/jump-game-ii/)

1. ```c++
   class Solution {
   public:
       int jump(vector<int>& nums) {
           int minstep = 0; //最少步数
           int futherest = 0; //在当前范围内能跳最远的地方，也就是下一步后的边界。
           int border = 0;//记录在当前位置最远能跳到哪（设为b），然后根据当前位置i和b的范围里，选择最远的那个，更新futherset.
           // 整体思路就是每一步都选择能跳最远的那一步，这样就是最少的。
           for(int i=0;i<nums.size()-1;i++){
               futherest = max(futherest, nums[i]+i);
               if(i==border){
                   border = futherest;
                   minstep++;
               }
           }
           return minstep;
   
       }
   };
   ```

### [134. 加油站](https://leetcode.cn/problems/gas-station/)

1. 总的想法是遍历每个点作为起点，看看是否能遍历

   1. 肯定超时了

   2. ```java
      class Solution {
          public int canCompleteCircuit(int[] gas, int[] cost) {
              int n = gas.length;
              int gas_total=0; int cost_total = 0;
              int ans = 0;
              int plus = 0;
              for(int i=0;i<n;i++){
                  gas_total += gas[i];
                  cost_total += cost[i];
              }
              if(gas_total<cost_total){
                  return -1;
              }
              for(int j=0;j<n;j++){
                  if(gas[j]<cost[j]){
                      continue;
                  }
                  ans = j;
                  int num = 0;
                  int flag = 0;
                  for(int i=0;i<n;i++){
                      num += gas[(j+i)%n] - cost[(j+i)%n];
                      if(num<0){
                          flag = 1;
                      }
                  }
                  if(flag == 0){
                      break;
                  }
              }
              return ans;
      
          }
      }
      ```

2. 有没有什么可以降低时间复杂度的？

   1. 一次遍历
      1. 设点x为起点，最远能到y，那么一定到不了y的下一个点
      2. 设x，y路上的一点z，那么以z为起点，一定到不了y的下一个点（很显然，若以x为起点，能到z，那么还是有油的，以z为起点，一开始是没有油的）
      3. 所以，若以x为起点，开始跑，设能跑到y（还没遍历一圈），那么xy上任何一点都到不了y的下一个点，更别提遍历一圈了，所以直接跳过xy上的所有加油站，从y的下一个点开始遍历

### [42. 接雨水](https://leetcode.cn/problems/trapping-rain-water/)

1. 暴力解法（超时）

   1. ```java
      class Solution {
          public int trap(int[] height) {
              int ans = 0;
              int flag = 0;
              int n =height.length;
              while(flag != 1){
                //一层层算
                  int leftB=0;
                  int rightB=0;
                  for(int i=0;i<n;i++){
                      if(height[i]!=0){
                          leftB = i;
                          break;
                      } 
                  }
                  for(int j=n-1;j>=0;j--){
                      if(height[j]!=0){
                          rightB = j;
                          break;
                      }
                  }
                  if(leftB == rightB){
                      flag = 1;
                      break;
                  }
                  // count
                  for(int k=leftB;k<rightB;k++){
                      if(height[k]==0){
                          ans++;
                      }
                  }
                  for(int j=0;j<n;j++){
                      if(height[j]>=1){
                          height[j]--;
                      }
                  }
              }
              return ans;
      
          }
      }
      ```


## lil TRICK

### 0. java data structure manipulation 

1. map
   1. traverse
      1. by keys
         1. ` map.keySet()`
      2. By values
      3. by entryset
   2. sort
      1. Directly use tree map
   
2. string
   1. how to tackle strings like path?
      1. ` /home/user/Documents/../Pictures` ?
      2. we use split() method to get the put the words apart
         1. ` String[] names = path.split("/");`

   2. multiple manipulation 

      1. ```java
         // The indexOf(char) method in Java returns the index (position) of the first occurrence of the specified character in a string. If the character is not found, it returns -1.       
         int star = p.indexOf('*');
         //index of a substring && substring from a to b(exclude)
         int i = s.indexOf(p.substring(0, star));
         //substring from x to end
         return i >= 0 && s.substring(i + star).contains(p.substring(star + 1));
         ```

   3. concatenate and decompose
      1. ` String sequence = list.get(i).web + " " + list.get(j).web + " " + list.get(k).web;`
      2. ` String[] r= res.split(" ");` (decomposition )
   4. Compare strings in a lexicographically smallest way
      1. ` if(str1.compareTo(str2)<0){// str1 is lexicographically smaller}`
   
   5. ` trim()`
   
      1. `String[] strArray = s.trim().split("\\s+");`
      2. Regular expression:` \\s+`, ` \\s`means any blankspace
   
3. math
   1. mod
   2. Abs 
      1. ` Math.abs()`

4. linkedlist

   1. deque

      1. ` Deque<Integer> deque = new LinkedList<>();`

   2. remove

      1. what's the cost of the remove operation?

         1. its O(n)

         2. so we can't simply use duque in leetcode 146(LRU cache here)

            1. ```java
               class LRUCache {
                   private final int capacity;
                   private final Map<Integer, Integer> map;
                   private final Deque<Integer> deque;
               
                   public LRUCache(int capacity) {
                       this.capacity = capacity;
                       this.map = new HashMap<>();
                       this.deque = new LinkedList<>();
                   }
               
                   public int get(int key) {
                       if (!map.containsKey(key)) {
                           return -1;
                       }
                       // Move the accessed key to the front of the deque
                       deque.remove(key); // the cost of this is O(n)!!
                       deque.addFirst(key);
                       return map.get(key);
                   }
               
                   public void put(int key, int value) {
                       if (map.containsKey(key)) {
                           deque.remove(key);
                       } else if (map.size() == capacity) {
                           // Remove the least recently used element
                           int lruKey = deque.removeLast();
                           map.remove(lruKey);
                       }
                       // Add the new key-value pair
                       map.put(key, value);
                       deque.addFirst(key);
                   }
               }
               
               ```

            2. Instead, we can maintain a doubly circular linked list

               1. ```java
                  class ListNode{
                    //data
                    int key;
                    int value;
                    //pointer
                    ListNode prev;
                    ListNode next;
                    public ListNode(int key, int value){
                      this.key = key;
                      this.value = value;
                    }
                  }
                  class DCLinkedList{
                    ListNode head;
                    ListNode tail;
                    public DCLinkedList(){
                      // dummy;
                      head = new ListNode(-1,-1);
                      tail = new ListNode(-1,-1);
                      // make it circular
                      head.prev = tail;
                      tail.next = head;
                    }
                    //how to make remove operation's cost O(1)?
                    //simply change the pointer
                     public void remove(ListNode node) {
                          node.prev.next = node.next;
                          node.next.prev = node.prev;
                      }
                    
                  }
                  
                  ```

5. array

   1. sort
      1. ` char[] s = str.toCharArray()`
      2. ` Arrays.sort(s)`;
      3. Sort by self-definition(lambda)
         1. ` Arrays.sort(intervals,(a,b)->a[0]-b[0]);`
            1. Intervals is a 2-dimensional array, we just compare each element by its first element 

      4. list to array
         1. `list.toArray(new int[ans.size()][])`;



### 1. 求递增数组中相邻两个值的差的最小值， 边界问题

1. 将 pre_val 的值初始化为null，一开始没有preval 强迫其无法得到差值。
2. 例题
   1. [530. Minimum Absolute Difference in BST](https://leetcode.cn/problems/minimum-absolute-difference-in-bst/)

### 2. 用函数递归来实现dfs时，可以新建一个函数，将信息用函数的参数传递。

1. 例题

   1. [211. Design Add and Search Words Data Structure](https://leetcode.cn/problems/design-add-and-search-words-data-structure/)

   2. [212. Word Search II](https://leetcode.cn/problems/word-search-ii/)\

      1. Solution:

         1. ```java
            import java.util.LinkedList;
            import java.util.List;
            
            class Solution {
                private char[][] board;
            
                public List<String> findWords(char[][] board, String[] words) {
                    this.board = board;
                    List<String> ans = new LinkedList<>();
                    for (String word : words) {
                        int[] numChar = new int[26];
                        for (int i = 0; i < word.length(); i++) {
                            int index = word.charAt(i) - 'a';
                            numChar[index]++;
                        }
                        for (int i = 0; i < board.length; i++) {
                            for (int j = 0; j < board[0].length; j++) {
                                boolean[][] visited = new boolean[board.length][board[0].length];
                                if (search(i, j, numChar, word, visited)) {
                                    if(!ans.contains(word)){
                                        ans.add(word);
                                    }
                                    break;
                                }
                            }
                        }
                    }
                    return ans;
                }
            
                public boolean search(int r, int c, int[] charLeft, String word, boolean[][] visited) {
                    // Check boundaries
                    if (r < 0 || r >= board.length || c < 0 || c >= board[0].length) {
                        return false;
                    }
                    if (visited[r][c]) {
                        return false;
                    }
            
                    char cur_char = board[r][c];
                    int index = cur_char - 'a';
                    if (charLeft[index] <= 0) {
                        return false; // No more characters left to match
                    }
            
                    // Mark the cell as visited
                    visited[r][c] = true;
                    charLeft[index]--;
            
                    // Check if all characters are matched
                    boolean allMatched = true;
                    for (int count : charLeft) {
                        if (count > 0) {
                            allMatched = false;
                            break;
                        }
                    }
                    if (allMatched) {
                        return true;
                    }
            
                    // Explore neighbors
                    boolean found = search(r, c + 1, charLeft, word, visited) ||
                                    search(r, c - 1, charLeft, word, visited) ||
                                    search(r + 1, c, charLeft, word, visited) ||
                                    search(r - 1, c, charLeft, word, visited);
            
                    // Backtrack
                    visited[r][c] = false;
                    charLeft[index]++;
                    
                    return found;
                }
            }
            
            ```

         2. my solution: (out of time limit)

            1. ```java
               class Solution {
                   private char[][] board;
                   public List<String> findWords(char[][] board, String[] words) {
                       this.board = board;
                       List<String> ans = new LinkedList<>();
                       for(String word : words){
               
                           for(int i=0;i<board.length;i++){
                               for(int j=0;j<board[0].length;j++){
                                   boolean[][] visisted = new boolean[board.length][board[0].length];
                                   if(search(i,j,0,word,visisted)){
                                      if(!ans.contains(word)){
                                       ans.add(word);
                                      }
                                      break;            
                                   }
                               }
                           }
                       }
                       return ans;
                   }
               
                   public boolean search(int r, int c, int index,String word, boolean[][] visisted){
                       if(r<0||r>=board.length||c<0||c>=board[0].length){
                           return false;
                       }
                       if(visisted[r][c]){return false;}
                       
                     // check before visit
                       char cur_char = board[r][c];
                       if(cur_char!=word.charAt(index)){
                           return false;
                       }
                       if(index+1==word.length()){return true;}
               
                       // if only the character matches the word that it would be visited
                       visisted[r][c] = true;
               
                       // Explore neighbors
                       boolean found = search(r, c + 1, index+1, word, visisted) ||
                                       search(r, c - 1, index+1, word, visisted) ||
                                       search(r + 1, c, index+1, word, visisted) ||
                                       search(r - 1, c, index+1, word, visisted);
               
                       // Backtrack
                       // because this array is shared across all recursive calls of the search method
                       visisted[r][c] = false;
                       
                       return found;
                   }
               }
               ```

### 3. Remember to make a copy when adding results to answer, specifically doing bactrack quesitons

1. Example

   1. [77. Combinations](https://leetcode.cn/problems/combinations/)

      1. ```java
            public void dfs(int start,List<Integer> curList){
                 if(curList.size()==k){
                     // make a copy
                   	// if we didn't make a copy, ans will store multiple same elements curList,any change to curList later will influence the result
                     ans.add(new LinkedList<>(curList));
                     return;
                 }
                 for(int i=start;i<=n;i++){
                     curList.add(i);
                     dfs(i+1,curList);
                     if(!curList.isEmpty()){
                         curList.remove(curList.size()-1);
                     }
                 }
            
             }
         ```


### 4. lambda expression in List

1. used to sort a list in a spectial way

   1. so the parameters in the lambda expression must be the element in list?

   2. Yes, in a lambda expression used with `list.sort()`, the parameters represent the elements being compared in the list. The lambda expression defines how two elements should be compared to determine their order.

      Here's a breakdown:

      1. **Parameters**: The two parameters (e.g., `s1` and `s2` in the string sorting example) represent two elements from the list. These are the elements you are comparing to decide their order.

      2. **Return Value**: The lambda expression should return an integer:
         - A negative integer if the first argument is less than the second (meaning the first should come before the second).
         - Zero if they are equal (no change in order).
         - A positive integer if the first argument is greater than the second (meaning the first should come after the second).

      ### Example Recap

      For example, consider this lambda expression used in sorting a list of integers:

      ```java
      numbers.sort((n1, n2) -> n2.compareTo(n1));
      ```

      Here:
      - `n1` and `n2` are parameters representing two integers from the list.
      - `n2.compareTo(n1)` is used to sort the numbers in descending order.

      ### Summary

      So, yes, the parameters in the lambda expression must correspond to the elements in the list being sorted. You can define how to compare these elements based on the desired sorting criteria.

   3. examples

      1. ```java
         import java.util.ArrayList;
         import java.util.List;
         
         class Person {
             String name;
             int age;
         
             Person(String name, int age) {
                 this.name = name;
                 this.age = age;
             }
         
             @Override
             public String toString() {
                 return name + " (" + age + ")";
             }
         }
         
         public class SortPersons {
             public static void main(String[] args) {
                 List<Person> people = new ArrayList<>();
                 people.add(new Person("John", 25));
                 people.add(new Person("Alice", 30));
                 people.add(new Person("Bob", 20));
         
                 // Sort by age using lambda expression
                 people.sort((p1, p2) -> Integer.compare(p1.age, p2.age));
         
                 System.out.println(people); // Output: [Bob (20), John (25), Alice (30)]
             }
         }
         
         ```

### 5. dummy node in linkedList problems

1. why dummy node?
   1. to better tackle first node in the list
   2. in reverse list problems,
   3. we can also remember the head of the list by returning dummy.next

### 6. Binary search

#### 6.1 JAVA binarysearch API

1. ```java
   lis = [2,5,7,18]
   num = 6
   Collections.binarySearch(lis,6) // return -pos-1(6 doesnt exist in lis)
   
   // so if we need to find a position where pos>= number,
   // we should normalize it first, 
     
     int pos = Collections.binarySearch(lis, num);
     if(pos<0){pos = -(pos+1);}
   // however, if lis has duplicate number, we should write binarySearch ourselves.
   
   
   ```

   

#### 6.2 write binary search ourself.

1. apart from search a specific value, (like 6 in 2 5 3 3 8 7 6 8 9 0), we can search a value meets some condition 
   1. just add the condition to the 
      1. in problem 162
         1. ![image-20241024162137120](/Users/lanceliao/Library/Application Support/typora-user-images/image-20241024162137120.png)
         2. the condition is larger than neighbor nodes or is the egde node
   2. Just to remember: 理解二分，请牢记区间的定义！区间内的数（下标）都是还未确定大小关系的，有的是 <，有的是 ≥；区间外的数（下标）都是确定大小关系的！对于本题（递增数组），区间左侧外面的都是 <，区间右侧外面的都是 ≥。从这个定义可以知道，找到了 ≥ 的数之后，要把这个数（下标）放在区间外面，而不是区间里面！
   3. for example:
      1. ![image-20241212153948374](/Users/lanceliao/Library/Application Support/typora-user-images/image-20241212153948374.png)
      2. in this type, ` if nums[mid] < target` means that all the elements with index <= mid are less than target, so you just change the leftbound of the interval to mid+1 (` left = mid + 1`)
   4. ![image-20250126143229789](/Users/lanceliao/Library/Application Support/typora-user-images/image-20250126143229789.png)
   5. ![image-20250126143132128](/Users/lanceliao/Library/Application Support/typora-user-images/image-20250126143132128.png)
   6. Why left?
      1. look the ternimation condition, when left = [every thing that lower than target]+1
      1. 统一写法：双闭区间，返回left指针（根据if else条件比target小的，都在left指针的左边）
      1. 注意返回的时候left的值可能比区间的最大的index还大1，这个说明target比该区间最大的值还大

### 7. Union Find set

1. Tutorial: https://programmercarl.com/%E5%9B%BE%E8%AE%BA%E5%B9%B6%E6%9F%A5%E9%9B%86%E7%90%86%E8%AE%BA%E5%9F%BA%E7%A1%80.html#%E8%83%8C%E6%99%AF
2. what kind of problems can it solve?
   1. Connectedness problems
      1. to determine whether a 
3. Examples:
   1. [128. Longest Consecutive Sequence](https://leetcode.cn/problems/longest-consecutive-sequence/)
   2. [684. Redundant Connection](https://leetcode.cn/problems/redundant-connection/)

### 8. dfs

1. when you found sth you wanted in dfs or recursion process, remember to **DEEP COPY**!

   1. example(leetcode 2096)

      1. ```java
         class Solution {
         
                 StringBuilder s_string;
                 StringBuilder d_string;
             public String getDirections(TreeNode root, int startValue, int destValue) {
         
                 //find
                 s_string = new StringBuilder();
                 d_string = new StringBuilder();
                 dfs(root,startValue,s_string,1);
                 dfs(root,destValue,d_string,0);
         
                 int count=0;
                 StringBuilder ans_string = new StringBuilder();
                 while(count<s_string.length()&&count<d_string.length()){
                     if(s_string.charAt(count)!=d_string.charAt(count)){   
                         break;
                     }
                     count++;
                 }
                 for(int i=0;i<s_string.length()-count;i++){
                     ans_string.append("U");
                 }
         
         
                 while(count<d_string.length()){
                     ans_string.append(d_string.charAt(count));
                     count++;
                 }
                 String ans = ans_string.toString();
                 return ans;        
             }
         
             void dfs(TreeNode root, int target_value, StringBuilder str,int choose){
                 if(root==null){
                     return;
                 }
                 if(root.val==target_value){
                     if(choose==1){
                         s_string = new StringBuilder(str);
                     }else{
                         d_string = new StringBuilder(str);
                     }
                     return;
                 }
         
                 if(root.left!=null){
                     str.append("L");
                     dfs(root.left,target_value,str,choose);
                     str.deleteCharAt(str.length()-1);
                 }
         
                 if(root.right!=null){
                     str.append("R");
                     dfs(root.right,target_value,str,choose);
                     str.deleteCharAt(str.length()-1);
                 }
         
             }
         }
         ```

      2. in code 

         1. ```java
                        if(choose==1){
                            s_string = new StringBuilder(str);
                        }else{
                            d_string = new StringBuilder(str);
                        }
            ```

         2. save it to public variable

         3. otherwise, it will change if any code modified 

### 9. hashmap & hashes

1. How to get all the keys in a map?
   1. `map.keySet();`
   2. ` HashMap<Integer, List<Integer>> map;`
   3. `List<Integer> sortedKeys = new ArrayList<>(map.keySet());` 
2. how to sort a list?
   1. Lambda expression?
   2. Collections.sort(sortedKeys);

#### time complexity of hash map & hash set

1. we can't use index to find elements in o(1) time(there's no direct method)
2. does hashset provides set.get(index)?
   1. No, a `HashSet` does not provide a method to access elements by index. `HashSet` is an unordered collection and does not maintain any order of elements, so it doesn't support index-based access like a list or array does. If you need index-based access, you would typically use a `List` in conjunction with a `HashSet`.
3. what's the time complexity of hashset remove
   1. The time complexity of removing an element from a `HashSet` is O(1) on average. This is due to the underlying hash table structure, which allows for efficient lookups and deletions. However, in the worst-case scenario (e.g., many hash collisions), the time complexity can degrade to O(n), but this is rare in practice with a well-designed hash function.
4. time complexity of remove and get(index)?
   1. for LinkedList, has O(1) on remove but O(n) on get
   2. for ArrayList, hasO(N) on remove but O(1) on get(index)
      - **LinkedList**: The `get(index)` operation has a time complexity of O(n) because it requires traversing the list from the head (or tail) to reach the specified index.
      - **ArrayList**: The `get(index)` operation has a time complexity of O(1) because it allows direct access to elements based on their index.
   3. 

### 10. Dynamic programming

1. 解决动态规划问题的核心：找出子问题及其子问题与原问题的关系
   1. 动态规划要解决的都是一些问题的最优解，即从很多解决问题的方案中找到最优的一个。当我们在求一个问题最优解的时候，如果可以把这个问题分解成多个子问题，然后递归地找到每个子问题的最优解，最后通过一定的数学方法对各个子问题的最优解进行组合得出最终的结果。总结来说就是一个问题的最优解是由它的各个子问题的最优解决定的。
   2. 将子问题的解进行组合可以得到原问题的解是动态规划可行性的关键。
2. 问题分类
   1. https://leetcode.cn/circle/discuss/u9jlGz/
   2. 区间dp
      1. [5. Longest Palindromic Substring](https://leetcode.cn/problems/longest-palindromic-substring/)
         1. 更新dp数组的顺序
            1. 是往右上角递增的，所以应该斜着一层层更新
   3. 背包问题
      1. 01背包
         1. 每种物品至多用一次
         2. 先遍历物品，再从大到小遍历背包容量
            1. 之所以从大到小遍历是因为确保对于每个重量，每个物品至多用一次
            2. ![Screenshot 2024-11-29 at 18.50.30](/Users/lanceliao/Library/Application Support/typora-user-images/Screenshot 2024-11-29 at 18.50.30.png)
         3. 例题
            1. [416. Partition Equal Subset Sum](https://leetcode.cn/problems/partition-equal-subset-sum/)
            2. 
      2. 完全背包
         1. 每种物品可以用无限次
         2. 先遍历物品，再从小到大遍历背包容量


### 11. String

1. since its a string, if we want to decide if two string has the same characters but different arrangements, instead of using hashmap to record, we can sort them first, and directly compare it using `HashMap<String, List<String>>`:

   1. ```java
                char[] arr=str.toCharArray();
                Arrays.sort(arr);
                String key=new String(arr);
      ```


### 12. Prefix sum

1. decide before add, 

   1. ```java
      
              for(int i=0;i<nums.length;i++){
                  sum += nums[i];
                  prefix[i] = sum;
                // decide first!!
                  if(map.containsKey(prefix[i]-k)){
                      ans+=map.get(prefix[i]-k).size();
                  }
                // add
                  if(map.containsKey(prefix[i])){
                     List<Integer> list = map.get(prefix[i]);
                     list.add(i);
                     map.put(prefix[i],list);
                  }else{
                      List<Integer> newList = new ArrayList<>();
                      newList.add(i);
                      map.put(prefix[i],newList);
                  }
               
              }
      ```

2. https://leetcode.cn/problems/maximum-subarray-sum-with-length-divisible-by-k/description/

   1. apart from dynamic programming, we can maintain a array that get the minimum value of the prefix at the index that modules k by i (i can be 0 to k-1)


### 13. difference array

1. how it works?
   1. https://leetcode.cn/circle/discuss/FfMCgb/
   2. when to use?
      1. when counting frequency, but given an array of interval
         1. Normally we traverse the interval and add the frequency of the element in that interval with 1
         2. but we just add the first element, and subtract last element 
   3. main idea
      1. instead of updating a whole bunch of subarray, just update one value in difference array to make that happen
      2. since they are equivalent
      3. ![Screenshot 2024-11-14 at 22.55.39](/Users/lanceliao/Library/Application Support/typora-user-images/Screenshot 2024-11-14 at 22.55.39.png)
   4. For example, in
      1. https://leetcode.cn/problems/count-positions-on-street-with-required-brightness/
      2. instead of adding brightness to every position in the range of a light, in stead, just record what's added and what deleted between moving from  previous position to current position
      3. and add up all the  previous difference to get the current value (prefix sum)
      4. using this technique, we can shrink the complexity from O(N*M) to O(N+M)
   5. other problems
      1. 

### 14. Sliding window/two pointers

1. 题单

   1. https://leetcode.cn/circle/discuss/0viNMK/

2. 定长滑窗

   1. https://leetcode.cn/problems/maximum-number-of-vowels-in-a-substring-of-given-length/solutions/2809359/tao-lu-jiao-ni-jie-jue-ding-chang-hua-ch-fzfo/

3. 不定长滑窗

   1. 先确定左边界，再枚举右边界

      1. for(right++)
         1. 加入右边界的值
         2. while() 减去左边届的值，更新左边届直至满足条件
         3. 更新统计值

   2. example

      1. ```java
         class Solution {
             public int maxTotalFruits(int[][] fruits, int startPos, int k) {
                 int left = lowerBound(fruits, startPos - k); // 向左最远能到 fruits[left][0]
                 int ans = 0, s = 0, n = fruits.length;
                 for (int right = left; right < n && fruits[right][0] <= startPos + k; right++) {
                     s += fruits[right][1]; // 枚举最右位置为 fruits[right][0]
                     while (fruits[right][0] * 2 - fruits[left][0] - startPos > k &&
                             fruits[right][0] - fruits[left][0] * 2 + startPos > k)
                         s -= fruits[left++][1]; // fruits[left][0] 无法到达
                     ans = Math.max(ans, s); // 更新答案最大值
                 }
                 return ans;
             }
         
             // 见 https://www.bilibili.com/video/BV1AP41137w7/
             private int lowerBound(int[][] fruits, int target) {
                 int left = -1, right = fruits.length; // 开区间 (left, right)
                 while (left + 1 < right) { // 开区间不为空
                     // 循环不变量：
                     // fruits[left][0] < target
                     // fruits[right][0] >= target
                     int mid = (left + right) >>> 1;
                     if (fruits[mid][0] < target)
                         left = mid; // 范围缩小到 (mid, right)
                     else
                         right = mid; // 范围缩小到 (left, mid)
                 }
                 return right;
             }
         }
         ```

### 15.  Combination number

1. be aware of overflow!
2. when doing factorial!

### 16. priority queue

1. min heap
   1. ` PriorityQueue<Long> minheap = new PriorityQueue<>();`
2. Max heap
   1. ` PriorityQueue<Long> maxheap = new PriorityQueue<>(Collections.reverseOrder());`
3. Add elements 
   1. Offer

4. get first elements
   1. Poll 
5. 
   1. Use lambda expressions to self-define 
      1. ` PriorityQueue<int[]> pq = new PriorityQueue<>((a,b)->Integer.compare(a[0],b[0]));`
      2. `  PriorityQueue<Pair> maxheap = new PriorityQueue<>((Pair a, Pair b) -> Integer.compare(b.value, a.value));`

### 17. union find

1. example problem

   1. leetcode 200 number of islands(https://leetcode.com/problems/number-of-islands/description/?envType=company&envId=amazon&favoriteSlug=amazon-thirty-days)

2. basic form

   1. ```java
      class UnionFind{
      
      	int[] parent;
        int[] rank; // start with 0;
        
        //initialize
        //make parent[i] = i
        // rank[i] = 0
        //find root 
        public int find(int i){
          if(parent[i]!=i){
            parent[i] = find(parent[i]);
          }
          return parent[i];
        }
       public void union(int x, int y){
         int rootx= find(x);
         int rooty = find(y);
         // make low rank root join high rank root, if same, plus rank with 1;
         if(rootx!=rooty){
           if(rank[rootx]>rank[rooty]){
             parent[rooty] = rootx;
           }else if(rank[rootx]==rank[rooty]){
             parent[rooty] = root[x];
             rank[rootx]++;
           }else{
             parent[rootx] = rooty;
           }
         }
         
       }
      
      
      }
      
      ```

### 18. backtrack

1. example

   1. https://leetcode.com/problems/word-search/description/?envType=company&envId=amazon&favoriteSlug=amazon-thirty-days

      1. ```java
         class Solution {
             char[][] board;
             boolean[][] visited;
             String word;
         
             public boolean exist(char[][] board, String word) {
                 this.board = board;
                 visited = new boolean[board.length][board[0].length];
                 this.word = word;
                 for (int i = 0; i < board.length; i++) {
                     for (int j = 0; j < board[0].length; j++) {
                         if (dfs(i, j, 0)) {
                             return true;
                         }
                     }
                 }
                 return false;
             }
         
             public boolean dfs(int row, int col, int i){
               // decide
                 if(row<0||row>=board.length||col<0||col>=board[0].length||visited[row][col]==true||i>=word.length()){
                     return false;
                 }        
                 if(board[row][col]!=word.charAt(i)){
                     return false;
                 }else{
                     if(i==word.length()-1){
                         return true;
                     }
                 }
                 visited[row][col] = true;
               // recursion, explore neighbors  
               boolean results = dfs(row+1,col,i+1)||dfs(row-1,col,i+1)||dfs(row,col+1,i+1)||dfs(row,col-1,i+1);
               // restore state  
               visited[row][col] = false;
                 
             
                 return results;
             }
         }
         
         public class ListNode{
           int val;
           ListNode next = null;
           public ListNode(int val){
             this.val = val;
           }
         }
         ```

### 19. graph

#### 1. decide whether there exists a circle in graph(khan algorithm)

1. bfs

   1. found all the vertices which have 0 indegree, visit them, delete them from graph
   2. Continue found 0-indegree vertice, visited them
   3. if all the vertices can be visited, then there's no circle in the graph

2. ```java
       int[] indegree = new int[numCourses];
       List<List<Integer>> adj = new ArrayList<>(numCourses);
       for(int i=0;i<numCourses;i++){
           adj.add(new ArrayList<>());
       }
        
       for(int[] prereq : prerequisites){
           adj.get(prereq[1]).add(prereq[0]);
           indegree[prereq[0]]++;
       }
       Queue<Integer> queue = new LinkedList<>();
       for(int j=0;j<numCourses;j++){
           if(indegree[j]==0){
               queue.offer(j);
           }
       }
       int visitedNum=0;
       while(!queue.isEmpty()){
           int curr = queue.poll();
           visitedNum++;
           List<Integer> neighbors = adj.get(curr);
           //delete
           for(int k=0;k<neighbors.size();k++){
               indegree[neighbors.get(k)]--;
               if(indegree[neighbors.get(k)]==0){
                   queue.offer(neighbors.get(k));
               }
           }
       }
       return visitedNum == numCourses;
   ```

3. leetcode 207(real problem)



### 20. set

1. 

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

### 22. Math

#### 1. xor

1. property
   1. if a xor b = c, then b = c xor a

#### 2. random

1. in java: 

### 23. linkedlist

#### 1. fast slow pointer

1. what's the difference between these two code?

   1. ```java
      public class Solution {
          public boolean hasCycle(ListNode head) {
              ListNode fastIndex = head;
              ListNode slowIndex = head;
              while(fastIndex!=null&&fastIndex.next!=null){
                  fastIndex = fastIndex.next.next;
                  slowIndex = slowIndex.next;
                  if(slowIndex == fastIndex){
                      return true;
                  }
              }
              return false;
          }
      }
      ```

   2. ```java
      public boolean hasCycle(ListNode head) {
              ListNode fastIndex = head;
              ListNode slowIndex = head;
              while(fastIndex!=null&&slowIndex!=null){
                  if(fastIndex.next!=null){
                      fastIndex = fastIndex.next.next;
                  }else{
                    break; // fix bug: added a break, or slowIndex would 
                  }
                  slowIndex = slowIndex.next;
                  if(slowIndex == fastIndex){
                      return true;
                  }
              }
              return false;
          }
      ```

      

### 24.dp

1. 非单调dp

   1. 是的，这道题可以用 **动态规划（DP）** 来解决。它是一个变种的路径规划问题，只不过不是求和最大值，而是求路径上所有点的 **按位与（AND）值的最大值**。

      ------

      ## ✅ 题目解析

      - **输入**：一个 `n * m` 的矩阵 `grid`，每个格子是一个非负整数。
      - **起点**：`(0, 0)`。
      - **终点**：`(n-1, m-1)`。
      - **移动规则**：只能向右或向下。
      - **目标**：找一条路径，使得路径上所有数的按位与的结果最大。

      ------

      ## ✅ 解法思路：动态规划 + 状态集合

      ### 为什么不能简单地 dp[i][j] = max(dp[i-1][j], dp[i][j-1]) & grid[i][j]？

      因为按位与（&）**不是单调的**，不能保证一步一步往下或往右取最大值就能得到最优解。例如：

      ```text
      路径1：111 & 110 = 110
      路径2：111 & 100 = 100
      虽然 111 > 100，但 111 & 100 = 100
      ```

      ### 所以，我们需要在每个点维护**多个状态**：从起点 `(0,0)` 到 `(i,j)` 的路径可能会有多个不同的 & 值。

      ------

      ## ✅ 代码实现（Java）

      ```java
      import java.util.*;
      
      public class MaxAndPath {
          public static int maxAndPath(int[][] grid) {
              int n = grid.length, m = grid[0].length;
      
              // dp[i][j] 存储所有到 (i,j) 的路径的 & 结果集合
              Set<Integer>[][] dp = new HashSet[n][m];
      
              for (int i = 0; i < n; i++)
                  for (int j = 0; j < m; j++)
                      dp[i][j] = new HashSet<>();
      
              dp[0][0].add(grid[0][0]);
      
              for (int i = 0; i < n; i++) {
                  for (int j = 0; j < m; j++) {
                      // 当前格子的值
                      int val = grid[i][j];
                      if (i > 0) {
                          for (int prev : dp[i - 1][j]) {
                              dp[i][j].add(prev & val);
                          }
                      }
                      if (j > 0) {
                          for (int prev : dp[i][j - 1]) {
                              dp[i][j].add(prev & val);
                          }
                      }
                      // 起点已经初始化过
                  }
              }
      
              // 找到终点的所有可能路径中的最大值
              int res = 0;
              for (int x : dp[n - 1][m - 1]) {
                  res = Math.max(res, x);
              }
              return res;
          }
      
          public static void main(String[] args) {
              int[][] grid = {
                  {5, 2, 3},
                  {1, 7, 8},
                  {4, 6, 0}
              };
              System.out.println(maxAndPath(grid)); // 输出最大路径&值
          }
      }
      ```

      ------

      ## ✅ 时间复杂度分析

      - 每个格子最多有若干个不同的 & 值集合（不超过 32 个，因整数最多 32 位）。
      - 总时间复杂度近似为 `O(n * m * k)`，其中 `k` 是最多可能的 & 值个数（通常较小，最多 32~64 个）。

      ------

      如果你希望进一步优化（比如空间复杂度、用 `BitSet` 来剪枝等），我也可以帮你优化。需要吗？

### 25. string

#### python

1. 

## Amazon OA

### reference

1. https://wdxtub.com/interview/14520850399861.html
2. 

### leadership

1. **顾客至上**（Customer Obsession）：以顾客为中心，努力满足和超越顾客的期望。
2. **拥有与承担**（Ownership）：对工作负责，关注长期成功，而非短期利益。
3. **发明与简化**（Invent and Simplify）：鼓励创新，寻找更简单的方法来解决问题。
4. **正确的人**（Are Right, A Lot）：依赖数据和直觉，做出明智的决策。
5. **学习与好奇**（Learn and Be Curious）：持续学习，不断寻求知识和技能的提升。
6. **招募和培养优秀人才**（Hire and Develop the Best）：吸引、培养和提升优秀人才。
7. **追求卓越**（Insist on the Highest Standards）：对工作质量和结果有高标准。
8. **思考大局**（Think Big）：鼓励大胆的想法，追求具有重大影响的目标。
9. **节俭**（Frugality）：用有限的资源创造更多的价值。
10. **获得信任**（Earn Trust）：通过诚实、透明和尊重来建立信任。
11. **深入细节**（Dive Deep）：关注细节，深入分析问题。
12. **有 Backbone**（Have Backbone; Disagree and Commit）：勇于表达不同意见，但一旦达成一致，积极支持决策。
13. **交付结果**（Deliver Results）：专注于实现目标并推动结果。
14. **倾向于行动**（Bias for Action）：重视快速行动，减少不必要的延迟。
15. **追求多样性**（Strive to be Earth’s Best Employer）：致力于创造多元和包容的工作环境。
16. **小心使用资源**（Success and Scale Bring Broad Responsibility）：认识到成功和规模带来的责任，关注社会和环境影响。

#### Work style 

1. 排序优先级不选neutral, 一般选more/most
2. 客户相关选客户
3. 优先deliver result
4. 提前做计划？

### coding problems

#### 1, outlier

1. https://www.fastprep.io/problems/amazon-get-outlier-value

   1. We are given the constraint that 1 <= arr[i] <= 10^9... meaning all array elements must be positive.

      Why is that important? -> it means that the maximum element in arr is either the SUM or the OUTLIER.

      There are three cases for an arbitary element in arr:

      Case 1) Part of the sum
      Case 2) The actual value of the sum of other elements
      Case 3) An outlier

      The maximum element cannot be part of the sum (cannot be case 1), as max(arr) + other positive elements would be greater than max(arr), which doesn't exist in our array, by the definition of what a maximum is.

      So, since max(arr) can only be either Cases 2) or 3), we just need to check if it is 3). If it isn't 3) we know max(arr) falls in case 2), and it is easy to find the outlier.

      Take our example arr = [4, 1, 3, 16, 2, 10]:

      Step 1) Identify max value and index: 16 (index 3)
      Step 2) Check if max value is the outlier by taking max(arr excluding max_index) and seeing if it equals the sum of arr. In our example, max([4, 1, 3, 16, 2, 10] - [16]) = 10, and 4 + 1 + 3 + 2 = 10, so we know max(arr) is the largest outlier, and can just return 16.
      Step 3) Suppose our max wasn't the outlier, (even though it was in this example, but for sake of tackling the case we will continue with the explanation). Find sum of non-max elements (sum all elements except max_index 3): 4 + 1 + 3 + 2 + 10 = 20
      Step 4) Subtract our max.. if it truly is case (2), there must exist an outlier (in 4 + 1 + 3 + 2 + 10) while the rest add up to 16. So because sum + outlier = Step2sum, we can just do Step2sum - sum to find our potential outlier. 20 - 16 = 4.
      Step 5) We are guaranteed by the problem at least one outlier, so we can just return the one we found from step 4. (In our example we already returned 16 from step(2) because max(arr) was the outlier, but in case max(arr) isn't the outlier, this case would return the true outlier.

      The time complexity is O(N), as we only ever do linear scans of our array without nesting any of these operations.

2. solution:

   1. ```java
      public class Solution {
          public int getOutlierValue(int[] arr) {
              // Step 1
              int maxVal = Integer.MIN_VALUE;
              int maxIndex = -1;
              
              for (int i = 0; i < arr.length; i++) {
                  if (arr[i] > maxVal) {
                      maxVal = arr[i];
                      maxIndex = i;
                  }
              }
              // Step 2, check if max(arr) is the outlier
              int secondMax = Integer.MIN_VALUE;
              int sumOthers = 0;
      
              for (int i = 0; i < arr.length; i++) {
                  if (i != maxIndex) {
                      int val = arr[i];
                      sumOthers += val;
                      if (val > secondMax) {
                          secondMax = val;
                      }
                  }
              }
              if (sumOthers - secondMax == secondMax) {
                  // Max is the largest outlier
                  return maxVal;
              }
              // Step 4: outlier = sum_others - max
              int outlier = sumOthers - maxVal;
              // Step 5: Because it is guaranteed by the problem an outlier exists, just return it
              return outlier;
          }
      }
      
      ```

#### 2. get data dependence sum(floor())

1. solution

   1. ```java
      public class Solution {
          public long getDataDependenceSum(long n) {
              long ans = 0;
              int temp = -1;
              
              for (long k = n; k >= 1; k--) {
                  if (n / k != temp) {
                      temp = (int)(n / k);
                      ans += temp;
                  }
              }
              
              return ans;
          }
      
          public static void main(String[] args) {
              Solution solution = new Solution();
              long n = 10;
              System.out.println(solution.getDataDependenceSum(n)); // Output: calculated sum
          }
      }
      
      ```

#### 3. getSuccessValue

1. ![image-20241225074608522](https://oss.1p3a.com/forum/202412/28/31947yu8eowug6y4a9trn.jpg)

1. solution

   1. ```java
      public int[] getSuccessValue(int[] queries, int[] num_viewers) {
        // write your code here
        
        PriorityQueue<Integer> maxheap = new PriorityQueue<>(Collections.reverseOrder());
        int[] successValue = new int[num_viewers.length];
        for(int i=0;i<num_viewers.length;i++){
          //System.out.println(num_viewers[i]);
          maxheap.offer(num_viewers[i]);
        }
        successValue[0] = maxheap.poll();
        for(int j=1;j<num_viewers.length;j++){
          successValue[j] = successValue[j-1]+maxheap.poll();
        }
        int[] ans = new int[queries.length];
        for(int k=0;k<queries.length;k++){
         ans[k] = successValue[queries[k]-1];
        }
        return ans;
      
        
      }
      ```

#### 4. find k nearest point

1. Solution 

   1. ```java
      import java.util.PriorityQueue;
      import java.util.Comparator;
      
      public class kNearestPoint {
          public Point[] Solution(Point[] array, Point origin, int k) {
              Point[] rvalue = new Point[k];
              int index = 0;
              PriorityQueue<Point> pq = new PriorityQueue<Point> (k, new Comparator<Point> () {
                  @Override
                  public int compare(Point a, Point b) {
                      return (int) (getDistance(a, origin) - getDistance(b, origin));
                  }
              });
              
              for (int i = 0; i < array.length; i++) {
                  pq.offer(array[i]);
                  if (pq.size() > k)
                      pq.poll();
              }
              while (!pq.isEmpty())
                  rvalue[index++] = pq.poll();
              return rvalue;
          }
          private double getDistance(Point a, Point b) {
              return Math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
          }
      }
      ```

#### 5. Relative rating

1. solution

   1. ```java
      public long[] getRelativeRatings(int[] skill, int[] rating, int k) {
        // write your code here
        int N = skill.length;
              int[][] arr = new int[N][3];
              for(int i = 0; i < N; i++){
                  arr[i][0] = skill[i];
                  arr[i][1] = rating[i];
                  arr[i][2] = i;
              }
      
              Arrays.sort(arr, (o1, o2) -> o1[0]-o2[0]);
              PriorityQueue<Integer> pq = new PriorityQueue<Integer>((a, b)->b-a);
              int curSum = 0;
              long[] ans = new long[N];
              for(int i = 0; i < k; i++){
                  ans[i] = curSum;
                  pq.add(arr[i][1]);
                  curSum+=arr[i][1];
              }
      
              for(int i = k; i < N; i++){
                  ans[i] = curSum;
                  pq.add(arr[i][1]);
                  curSum = curSum + arr[i][1] - pq.poll();
              }
      
              long[] result = new long[N];
              for(int i = 0; i < N; i++) {
                  result[arr[i][2]] = ans[i];
              }
      
              return result;
      }
      ```

## Amazon VO preparation (let's f**king get it!)



### lru

```java
class LRU{
  class Node{
    int key;
    int val;
    Node prev;
    Node next;
    public Node(int key, int val){
      this.key 
      this.val = val;
    }
  }
  int capacity;
  Node head;
  Node tail;
  Map<Integer, Node> map;
  
  public LRU(int capacity){
    this.capacity=capacity;
    head=new Node(-1,-1);
    tail = new Node(-1,-1);
    map = new HashMap<>();
    
    head.next = tail;
    tail.prev = head;
  }
  
  
  
  
  //helper
  
  public void put(){
    //if already contains, remove old one
    if()
      
      // new a Node, 
      // update map
      // update linkedlist
      
      
      // if size > capacity
      // remove end 
    
  }
  
  
  
  
  
  
  
  
  
}
```



### OOD

1. 









### 0. Self-introduction

1. Hello, my name is Weikai Liao, and I'm currently a Master student studying software engineering at Duke University. I have a strong passion for software development and have gained practical experience through projects and internships.
2. During my internship at BoulderAI Technologies from April to June 2024, I engineered a Large Language Model bot using FastGPT to transform natural language into BPMN diagrams, developed automation tools for data management, and implemented workflows using a low-code platform. These projects enhanced efficiency and automation, reducing manual effort. 
3. During my internship, I focused on collaboration and quickly integrating into a complex system. I utilized GitLab for multi-version control and configured projects using Nacos. I developed APIs within a microservices architecture and learned to test them locally using a shared development environment. I also learned the importance of quickly integrating into an existing, complex system and efficiently reading and understanding others' code. Working closely with my mentor and team leader, I effectively navigated challenges and contributed to successful project outcomes
4. Thank you for considering my application.I'm excited about the opportunity at Amazon

### 1. BQ questions 

1. method

   1. TASK
   2. https://docs.google.com/document/d/112HBiMNvu6TYbDUOfVRe_MS4A-fKaWYrpMlmnsiMNiA/edit?tab=t.0
   3. 

2. questions

   1. most impactful project

3. Leadership principles 

   1. Bias for action

      1. key words: speed, **calculated risk** 
      2. 
      3. **tight deadline** (Bias for action)(customer obsession)

         1. first edition 

            1. During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify workflow creation, enabling project managers to effectively design workflows.

               Facing a tight deadline, I had to choose between two LLM models: one was faster and cheaper but less accurate, while the other was more accurate but slower and costlier. Given our objective to empower project managers with a user-friendly tool, I prioritized accuracy to ensure reliable workflows.

               Before making a decision, I took action to collect essential data. I gathered insights from our development team and analyzed feedback from previous projects highlighting the importance of accuracy. I discovered that high-quality outputs significantly reduced user frustration and errors in workflow creation.

               After deciding on the more accurate model, I quickly iterated several versions to optimize performance despite the slower processing time. This resulted in a 30% decrease in user revisions and increased confidence in constructing accurate workflows independently.

               By prioritizing data-driven decisions and fast iterations, we enhanced the user experience, aligning with our mission to simplify workflow creation. This taught me the importance of balancing immediate challenges with long-term benefits, ultimately leading to greater efficiency and user satisfaction.
         
         2. Second edition
         
            1. **Tight Deadline Story (Bias for Action, Customer Obsession)**
         
               During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify workflow creation, enabling project managers to effectively design workflows.
         
               **Facing a tight deadline**, I had to quickly choose between two LLM models: one was faster and cheaper but less accurate, while the other was more accurate but slower and costlier. Given our objective to empower project managers with a user-friendly tool, I prioritized accuracy to ensure reliable workflows.
         
               To make an informed decision swiftly, I coordinated closely with cross-functional teams. I organized rapid feedback sessions with the development team and engaged in quick discussions with customer support to gather insights from previous projects. This highlighted the critical importance of accuracy in reducing user frustration and errors.
         
               After selecting the more accurate model, I communicated regularly with the team to iterate several versions rapidly, optimizing performance despite the slower processing time. We held daily stand-ups to keep everyone aligned and used collaborative tools to track progress and share updates in real-time.
         
               This approach resulted in a 30% decrease in user revisions and increased confidence in constructing accurate workflows independently. By prioritizing data-driven decisions and fast iterations, we enhanced the user experience, aligning with our mission to simplify workflow creation. This experience taught me the value of effective communication and collaboration under pressure, balancing immediate challenges with long-term benefits to achieve greater efficiency and user satisfaction.
         
      4. Limited info

         1. During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify the workflow creation process, enabling project managers—rather than just professional programmers—to effectively design workflows.

            While engineering the bot, I faced a critical decision between two LLM models. One model was faster and less expensive but sometimes produced less accurate results. The other model was more accurate but slower and costlier to implement. Given our objective to empower project managers with a user-friendly tool, I recognized that accuracy was paramount to ensure that the generated workflows were reliable and effective.

            To make an informed decision, I gathered insights from our development team and analyzed feedback from previous projects that emphasized the importance of content accuracy for end users. Although I had limited information on how the slower processing times might impact user experience, I discovered that high-quality outputs significantly reduced user frustration and errors in workflow creation.

            Ultimately, I chose the more accurate model, despite its higher cost. This decision resulted in a 30% decrease in the number of revisions required by users when creating workflows. Users reported increased confidence in their ability to construct accurate workflows independently, significantly enhancing their overall experience with the tool.

            By prioritizing accuracy over speed and cost, we not only aligned with our mission to simplify workflow creation for project managers but also demonstrated a commitment to **Customer Obsession**. This experience taught me the importance of making data-driven decisions, especially when aiming to empower users with innovative solutions, even if it meant investing more upfront. Ultimately, the long-term benefits of accuracy outweighed the initial costs, leading to greater efficiency and satisfaction among our users.

   2. Ownership

      1. above and beyond （**Outside responsibility**）

         1. 初始版本：下面是我这个故事的细节（要求用star原则）：老板要求我们team为公司的平台开发一个new feature的原型：开发一个利用ai自动生成的工作流程图的功能，我的职责是写prompt开发那个ai bot，它可以将自然语言转化为json格式的流程图数据。然后开发完成后和mentor对接，也成功将api对接进了系统，并能在前端成功显示流程图，但我是一个喜欢从客户角度出发测试产品品质的人， 我详细测试了产品，发现每当我提出很详细的要求时，前端无法正常显示流程图，但是我查看ai bot的日志时他是能正常生成数据的。然后我又经过细致的排查，利用浏览器f12发现是后端api超时了，超过2分钟的全都超时，我没有权限改这个config,然后就找我mentor一起修改，问题最终解决，大大提高了这个功能按要求生成复杂流程图的能力。

         2. Version1:
            1. **Situation:** Our team was tasked with developing a new feature for our company's platform: an AI-driven workflow diagram generator. My role was to create prompts for the AI bot to convert natural language into JSON format for the diagrams.
            2. **Task:** After successfully integrating the API and displaying the diagrams on the front end, I decided to test the product further from a customer perspective. I noticed that when I input detailed requests,  the diagrams failed to display properly, though the AI bot's logs showed correct data generation.
            3. **Action:** I conducted a thorough analysis and discovered, using the browser's developer tools, that the backend API was timing out after two minutes, causing the display issue. The configuration to change this was beyond my permissions. With the owner on vacation, I took the initiative to address this issue immediately, considering the potential negative impact on our users.\
            4. I collaborated with my mentor to adjust the API timeout settings, ensuring the feature could handle complex requests. I also documented the problem and solution, then emailed the owner upon their return, suggesting further improvements.
            5. **Result:** This proactive approach significantly enhanced the feature's capability to generate complex workflow diagrams, improving user satisfaction and retention. By stepping outside my assigned role, I ensured a seamless user experience and demonstrated long-term thinking and ownership.

      2. Pushback & conflicting

         1. sacrifice short term gains for long term goals

            1. main point:

               1.  Short-term vs long term 

               2. During my internship at BoulderAI Technologies, I was tasked with enhancing BPMN diagrams by linking them to existing workflows. I faced a decision between a short-term solution of manually linking processes to meet an upcoming deadline and a long-term solution using RAG technology to automate integration with our knowledge base.

                  I discussed both options with my supervisor, advocating for the long-term approach. I explained how RAG technology would provide sustainable benefits and reduce future workload. To mitigate the risk of missing the deadline, I broke down tasks and identified reusable components from our systems that could return task template names and IDs. I imported this data into the LLM’s knowledge base, allowing the system to automatically generate accurate and integrated workflows.

                  By optimizing the development process and re-prioritizing tasks, we implemented the RAG-based solution before the deadline. This not only improved functionality and reliability but also enhanced user satisfaction by streamlining operations and aligning with our long-term goals.

   3. are right, a lot 

      1. Mistake/failure 类问题

         1. Miss ddl. one time you failed/biggest mistake

            1. project in undergraduates

               1. idea

                  1. 
                  2. underestimate & (**most important: **)
                     1. 可以错的点：
                        1. Misjudged the 
                        2. focus on too much on detail
                        3. (写自己的错)
                  
                  3. teachers's requriement is vague, just let us use a java framework called spring and other frontend language  to create a full-stack web application making a . As a team leader of my team i was responsible for backend development and let my teammates to learn frontend. as we are both new to the web development at that time, we knows little about how to coordinate frontend and backend. and unfortunately my teammates was not positive and responsive. when i ask him about progress, he always says there's some bug and his working on it. But he was my friend and I'm not pushing him for the sake of friendship. at last i he didn't make his part and i have to help him to do it. eventually we missed ddl and asked extension from professor for one week to re implement frontend and coordinate with ,backend  worked as hard i as can and finally make up.  
                  
                  This experience **taught me the importance of ensuring clear and continuous communication between teams**. I learned to establish more thorough documentation and regular synchronization meetings to verify that all teams are aligned on technical specifications.
   
         2. interpersonal conflict 类问题
   
            1. How you resolve conflict with your teammates
   
            2. Whether or not to implement  segmented file upload feature under limited time
   
               1. **Situation:** In our undergraduate project team, we were tasked with enhancing a centralized family file management solution for our classmates and professor. One proposal was to implement a segmented file upload feature to increase transfer speed and allow resumption of interrupted uploads.
   
                  **Task:** Our team was divided. I supported the feature, believing it would enhance user experience for students and faculty. However, a teammate was worried about the complexity it would add, given our limited timeline.
   
                  **Action:** I communicated my perspective, highlighting the long-term benefits and improved user satisfaction from faster uploads and reliable resumption. I acknowledged my teammate's concerns about time constraints and proposed a small-scale proof of concept to assess feasibility within our deadline.
   
                  While breaking down the project into smaller tasks, I discovered an API we could reuse, significantly reducing development time since we didn't have to build it from scratch. To mitigate risks, we agreed on a plan to allocate resources efficiently and set clear milestones for progress evaluation.
   
                  **Result:** The proof of concept showed significant improvements in upload speed, and feedback from our classmates and professor was overwhelmingly positive. We successfully implemented the feature, resulting in a 30% increase in user engagement. My teammate later appreciated the collaborative approach and recognized the positive impact on our project.
   
      2. Customer obsession
   
      3. Think Big
   
         1. Most challenge in previous job?
   
         2. 
   
      4. Invent & Simplify
   
      5. Learn, and Be Curious
   
      6. Dive Deep
   
      7. Insist On The Highest Standards
   
      8. Earn Trust
   
      9. Deliver Results
   
   4. 

### 2. potential coding problems

1. Leetcode 545 

2. Leetcode 45

   1. While(boundary){

      1. While(){}

      }


3. lc 200

### 3. 面筋

1. VO：20分钟bq，问了out of duty和w/o enough info to make decision，每个故事会问两个follow up问题。20分钟算法题考了用最小堆解决问题，问了优化follow up。
2. VO的前20-30分钟bq 只问了一个out of responsibility 的问题，其余时间都是技术问题细节，eg. design patterns，API design，scalability etc.
   1. （个人猜测可能是挂在这里了，他问的好多tech细节内容都忘记了， 瞎回答的，design pattern这块是真的不知道）coding 参考LC 溜耳伊。 
   2. （coding应该没问题，给面试官讲完思路后他赞同然后开始写，vo 结束后自己又跑了一遍）
   3. 经验总结： 还是要对自己做过的project非常熟悉。之前花太多精力在coding上面了，忽略了八股这方面。
   4. 

### 4. Good problem worth reviewing

1. leetcode 2055

   1. sometimes we can reach o(n) time complexity by recording addtional information using additional array or sth
   2. more examples 
      1. leetcode 155
         1. use a hashmap to recorde the minimum value of each state;

2. backtrack

   1. when remove, make sure you remove the right element, it should be the last element you added into data structure 
   2. ![Screenshot 2025-01-26 at 23.51.09](/Users/lanceliao/Desktop/Screenshot 2025-01-26 at 23.51.09.png)

3. leetcode 138

4. 1642

   1. Greedy 
      1. 用无穷长的ladder 替换bricks


### 5. what should i do at the coding part?

1. asking clarification  question
   1. about input data
   2. Write a solution at first and optimized it later
   3. take some time write a case that's not a happy case to test your code
   4. Don't forget to include time complexity
   5. time your self taking those exercises
2. 

### 6.  finnal bq answer



#### 1. Tight ddl

-------

During my internship at BoulderAI Technologies, I was tasked with developing an AI assistant to convert natural language into business process workflows. Initially, we had a month to create a prototype for a customer demonstration. However, my manager unexpectedly cut the deadline to two weeks to align with an important client meeting.

Faced with this tight deadline, I realized I couldn't include all the features we initially discussed. After consulting with my manager, we agreed to focus on delivering a functional prototype by cutting non-essential features and optimizing critical performance aspects. For example, I initially planned to connect the database to the AI knowledge platform for automatic data retrieval using RAG technology to enhance performance. But I had no time for that. Instead, I manually imported data to ensure the demonstration's effectiveness.

I sought assistance from my mentor, who quickly helped me familiarize myself with the AI platform to avoid process delays due to potential bugs.

By collaborating closely with cross-functional teams from both the backend and frontend, we successfully launched the product feature on schedule, surpassing user adoption targets. Feedback from my supervisors highlighted the effectiveness of my approach, and I learned the importance of strategic prioritization and teamwork in meeting tight deadlines.

#### 2. out of responsibility

------

1. **Situation:** Our team was tasked with developing a new feature for the company's platform: an AI-driven workflow diagram generator. My responsibility was to develop the AI application using the AI knowledge platform called FastGPT, ensuring it correctly returned desired results from prompts.
2. **Task:** After developing the AI application and testing the generated data,  my part is over. but I wanted to test the feature from a user perspective to see if it works. I found that simple requests worked well, but complex requests failed to display correctly on the front end. The AI logs showed correct data generation, which means my part is fine, indicating an issue elsewhere.
3. **Action:** Facing this problem, I felt an urge to solve it or at least report the problem to ensure a seamless experience for customers.  I conducted a thorough analysis and discovered that the backend API was timing out after two minutes, which caused the display issue. Since I was responsible only for developing the AI application and not integrating the API with the backend, I didn't have the authority to change the timeout settings. Recognizing the importance of resolving this, I scheduled a brief meeting with my supervisor, presenting the data and clearly explaining the timeout problem and its impact on user experience. explaining that while the AI application worked locally, it faced integration issues. He helped me to find who's reponsible for this. And I then coordinated with the responsible colleague to adjust the timeout settings.
4. **Result:** This proactive approach improved the feature's ability to handle complex requests, significantly enhancing user satisfaction.

##### 2.1 possible follow ups

1. Certainly!

   1. **Communication:** How did you approach your supervisor and colleague to discuss the timeout issue?
      - I scheduled a brief meeting with my supervisor, presenting the data and clearly explaining the timeout problem and its impact on user experience. I focused on collaboration to find a solution.

   2. **Collaboration:** How did you coordinate with the colleague responsible for the backend to implement the necessary changes?
      - I reached out to the colleague via a quick chat, shared my findings, and we reviewed the API settings together. We then worked as a team to adjust the timeout settings and ensured thorough testing.

   3. **Initiative:** What motivated you to go beyond your initial responsibilities and test the feature from a user perspective?
      - I wanted to ensure a seamless user experience and believe that understanding the end-user perspective is crucial for delivering high-quality products.

   4. **Challenge Handling:** Did you face any resistance or challenges when proposing the changes to the backend settings?
      - Initially, there was some hesitation about changing the timeout settings. I addressed this by presenting evidence of the issue and demonstrating the benefits for the project’s goals, gaining support through data and user impact.

   5. **Outcome Measurement:** How did you measure the improvement in user satisfaction and retention after resolving the issue?
      - We analyzed user feedback and tracked metrics such as request completion rates and user engagement before and after the change. Positive feedback and increased retention rates confirmed our solution's success.

   6. **Learning:** What key lessons did you take away from this experience, and how have they influenced your approach to subsequent projects?
      - I learned the importance of looking beyond immediate responsibilities for project success and the value of effective communication and collaboration. These lessons have made me more proactive and solution-oriented in future projects.

#### 3.  help peers, 

-------------------

During a university project, we were tasked with creating a full-stack web application to implement a mini Uber using Django  for the backend and React for the frontend. As the team leader, I was responsible for the backend, while a teammate handled the frontend. However, my teammate was new to web development and unsure about effectively coordinating the two aspects. 

The project's success relied on seamless integration between the frontend and backend, and his struggle with the frontend was critical to our completion. 

Recognizing the issue, I stepped in to assist. I showcased a demo featuring user registration and login to help him understand RESTful APIs, wrote a clear API document detailing the expected data, and explained it to him. Once he grasped the overall framework, he began to learn quickly and took charge of the frontend development. I also initiated regular check-ins to ensure he wasn't blocked for long periods. 

As a result, our project was completed on time and received high marks for its functionality and integration. This experience not only boosted my teammate's confidence but also strengthened our collaborative skills.



#### most challenging project, 

--------------------------------

1. One of my most challenging projects was developing a family-oriented cloud storage system during my undergraduate studies.
2. The challenge stemmed from high demanding performance requirements from my instructors, he wish us to lower the reponding time below 300 ms for file searching feature
3. Initially, we planned to use MySQL's `LIKE` statement for implementing the fuzzy search for the file search feature. However, testing revealed that as the number of stored files increased to over 50,000, response times slowed significantly, from an average of 600ms to over 2 seconds, degrading user experience. 
4. To address this, I leveraged online resources, including technical articles and forums, to understand the limitations of using MySQL for searching, which results in a time complexity of O(n). I learned about inverted index technology, which can achieve O(log(n)) search time, and discovered that Elasticsearch, a non-relational database, utilizes this technique.
5. I quickly learned how to implement Elasticsearch for fuzzy searching by studying documentation and tutorials. This reduced the average response time to under 100ms, significantly enhancing the application's performance. This experience required prioritizing tasks, breaking them into manageable parts, and rapidly acquiring new skills through self-directed learning.
6. Despite the complexity, we successfully delivered a robust application on schedule, enhancing user satisfaction and productivity.

#### calculated risk | limited info

-----------------------------------------------------

During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify the workflow creation process, enabling project managers—rather than just professional programmers—to effectively design workflows.

While engineering the bot, I faced a critical decision between two LLM models. We tested both models using 100 test cases to evaluate the accuracy of their results with the same input and output. We found that Model A had a 20% higher cost and a 25% longer response time, but it delivered results that were 15% more accurate than Model B. Given the time and resource limitations of only having 100 test cases, I questioned whether this sample was representative enough to draw definitive conclusions about overall performance.

At that moment, I recognized the need for a trade-off. Our product was designed for project managers, who would find it challenging to modify the generated process diagrams. Therefore, ensuring successful generation on the first attempt was crucial, even if it meant sacrificing some speed and cost for that additional 15% accuracy.

With this analysis, I presented my findings to my manager, who agreed with my perspective. Ultimately, we opted to use the more accurate model, which improved the precision and effectiveness of the generated results. Enventually the user expressed high satisfaction and indicated they were willing to accept a modest increase in cost and response time, as they valued the enhanced accuracy and reliability of the tool.

This experience taught me the importance of making data-driven decisions, especially when aiming to empower users with innovative solutions, even if it meant investing more upfront. Ultimately, the long-term benefits of accuracy outweighed the initial costs, leading to greater efficiency and satisfaction among our users.

#### biggest mistake ｜ miss ddl

-----------------

Mistake? Waste too much time on choosing things? 

1. 没有做好priority, 在一个不太重要的地方被block住了很长时间（分清主次）
2. （never underestimate task） 如果要重来一遍的话 要把任务划分成几个点，把具体的任务细节化，然后给每个任务进行评估
3. 事情不对劲，应该提早地transparent到上级（team），不应该在最后一刻才告知.

----

**Situation:**Smart Home system While working on the user management system and designing a WebSocket communication protocol, I faced challenges that ultimately led to missing the project deadline.

**Task:** My responsibilities included developing user management features and establishing a robust WebSocket protocol. However, I became overly focused on optimizing performance with Redis caching, which took up a significant amount of my time.

**Action:** By dedicating too much effort to the caching implementation, I neglected the design of the WebSocket protocol, leaving insufficient time to create a solid and effective solution. Additionally, I did not communicate my challenges to the team early enough, which hindered our collective progress.

**Result:** As a result, I missed the deadline, causing delays not only in my work but also for the entire team, as the WebSocket protocol was essential for real-time communication.

**Learning:** This experience taught me the importance of prioritization, effective task management, and open communication. I learned to balance performance optimizations with foundational tasks, ensuring that I allocate time appropriately. I also recognized the need to be transparent with my team about challenges, allowing for collaborative problem-solving. Moving forward, I actively applied these lessons to improve project outcomes and foster a supportive team environment. The miss ddl situation never happened again 

As an engineer, facing choices is constant. It's often hard to determine the right path, but it's crucial to keep moving forward and make incremental progress. Even if some attempts fail, they help rule out possibilities, contributing to overall progress.

#### conflict with others

------

**Situation:** In our undergraduate project team, we were tasked with developing a centralized family file management solution. Our team was divided about whether or not we should implement a segmented file upload feature to increase transfer speed and allow resumption of interrupted uploads.

**Task:** . I supported the feature, believing it would enhance user experience for students and faculty. However, a teammate was worried about the complexity it would add, given our limited timeline.

**Action:** I communicated my perspective, highlighting the long-term benefits and improved user satisfaction from faster uploads and reliable resumption. I acknowledged my teammate's concerns about time constraints and proposed a small-scale proof of concept to assess feasibility within our deadline.

While breaking down the project into smaller tasks, I discovered two existing API(for backend, a ) we could reuse, significantly reducing the  development time since we didn't have to build it from scratch. And it also mitigate my teammate's concern for , we agreed on a plan to allocate resources efficiently and set clear milestones for progress evaluation.

**Result:** The proof of concept showed significant improvements in upload speed, and feedback from our classmates and professor was overwhelmingly positive. We successfully implemented the feature, resulting in a 30% increase in user engagement. My teammate later appreciated the collaborative approach and recognized the positive impact on our project.

#### A time u sacrificed short term interest for long term gain

----

1. (use conflict with others)
   1. my team mates think we should develop new features instead of enhancing the performance of existing feature. 

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

   

## java

### Acm 模式，从输入构造

1. ```java
   import java.io.*;
   import java.util.*;
   
   public class Main {
   
       // ===== 二叉树节点必须是 static =====
       static class TreeNode {
           int val;
           TreeNode left;
           TreeNode right;
           TreeNode(int v) {
               val = v;
           }
       }
   
       // ===== 全局变量必须是 static =====
       static int ans = Integer.MIN_VALUE;
   
       public static void main(String[] args) throws Exception {
           BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
           String line = br.readLine();
           if (line == null || line.length() == 0) return;
   
           // 示例输入：1 2 3 null 4
           String[] arr = line.split(" ");
           TreeNode root = buildTree(arr);
   
           maxGain(root);
           System.out.println(ans);
       }
   
       // ===== LeetCode 105/107 风格的层序建树 =====
       static TreeNode buildTree(String[] arr) {
           if (arr[0].equals("null")) return null;
   
           TreeNode root = new TreeNode(Integer.parseInt(arr[0]));
           Queue<TreeNode> queue = new LinkedList<>();
           queue.offer(root);
   
           int i = 1;
           while (!queue.isEmpty() && i < arr.length) {
               TreeNode cur = queue.poll();
   
               if (i < arr.length && !arr[i].equals("null")) {
                   cur.left = new TreeNode(Integer.parseInt(arr[i]));
                   queue.offer(cur.left);
               }
               i++;
   
               if (i < arr.length && !arr[i].equals("null")) {
                   cur.right = new TreeNode(Integer.parseInt(arr[i]));
                   queue.offer(cur.right);
               }
               i++;
           }
           return root;
       }
   
       // ===== 二叉树最大路径和核心逻辑 =====
       static int maxGain(TreeNode root) {
           if (root == null) return 0;
   
           int left = Math.max(0, maxGain(root.left));
           int right = Math.max(0, maxGain(root.right));
   
           ans = Math.max(ans, root.val + left + right);
   
           return root.val + Math.max(left, right);
       }
   }
   
   ```

   

