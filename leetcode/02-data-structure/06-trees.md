# Trees

> Section: **Data Structure** — consolidated topic covering Binary Tree, Binary Search Tree, and Red-Black Tree.

## Binary Tree

### Binary tree & DFS

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

### [105. Construct Binary Tree from Preorder and Inorder Traversal](https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)

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

      

### [117. Populating Next Right Pointers in Each Node II](https://leetcode.cn/problems/populating-next-right-pointers-in-each-node-ii/)

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

### 中序遍历

### 1. 可以递归实现也可以用栈来实现

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


### 非递归实现后序遍历

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

### 先序遍历

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

   

### 最小高度树

1. https://leetcode.com/problems/minimum-height-trees/
2. 要找到最小高度的那个节点，其实就是找树的直径（树中任意两点之间的 **最长简单路径**），那然后找这个直径的中心作为顶点，才会有最小高度，

## Binary Search Tree (BST)

1. 一般都是用中序遍历，得到一个递增的序列

### lowereset common ancestor:

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

### 除了中序遍历，还可以利用的性质：

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

---

### Appendix: Tips consolidated from `coding-tricks.md`

#### Tip #1 — Min adjacent diff & null boundary (BST inorder)

### 1. 求递增数组中相邻两个值的差的最小值， 边界问题

1. 将 pre_val 的值初始化为null，一开始没有preval 强迫其无法得到差值。
2. 例题
   1. [530. Minimum Absolute Difference in BST](https://leetcode.cn/problems/minimum-absolute-difference-in-bst/)

## Red-Black Tree (红黑树)

1. 为什么需要红黑树，他比BST（二叉查找树好在哪里？）
   1. bst的形状是根据节点插入的顺序决定的，如果按升序或者降序的方式插入，二叉查找树就会退化成一个线性的结构

### 1. 红黑树的特性？

1. 每个节点或是红色的，或是黑色的。
   根节点是黑色的。
   所有叶子（NIL节点）都是黑色的。
   如果一个节点是红色的，则它的两个子节点都是黑色的。
   从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点。

### 2. 红黑树和二叉查找平衡树的区别？

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

## tree's diameter

1. Problem list

   1. https://leetcode.com/problems/count-subtrees-with-max-distance-between-cities/description/
   2. https://leetcode.com/problems/diameter-of-binary-tree/

2. how do you get the diameter of a tree?

   1. ```
      BFS from any node
          ↓
      farthest node A
      
      BFS from A
          ↓
      farthest node B
      
      dist(A,B)
      =
      diameter
      ```

3. 利用树型DP求直径，针对图结构而言，不用记录visited数组，直接在参数里维护father节点就行

   1. https://leetcode.cn/problems/difference-between-maximum-and-minimum-price-sum/solutions/2062782/by-endlesscheng-5l70/
