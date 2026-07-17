# Trees

> Section: **Data Structure** — consolidated topic covering Binary Tree, Binary Search Tree, and Red-Black Tree.
>
> 结构：1. DFS 递归建模模板 → 2. 高频 DFS 题对比 → 3. 遍历的迭代实现 → 4. 例题 → 5. BST → 6. 红黑树 → 7. 树的直径

## 1. Binary Tree — DFS 递归建模模板

### 1.1 通用递归三问（一定要背）

```text
1. 递归函数的"定义"是什么？
2. 当前层要做什么？
3. 递归边界是什么？
```

> 所有二叉树递归题，本质都在回答这三件事。面试时先在脑子里回答：
>
> 1. dfs 返回什么？
> 2. root 在哪一步确定？
> 3. 左右子树谁先？
>
> 回答完这三问，代码已经写完 80%。

### 1.2 重建二叉树的抽象模板（核心）

> 问题抽象：**给定遍历序列 + 子区间 → 构造并返回子树根节点**

```python
def dfs(left, right):
    if left > right:
        return None

    # 1. 确定 root
    root_val = ...
    root = TreeNode(root_val)

    # 2. 切分左右子树区间
    mid = index_map[root_val]

    # 3. 构建左右子树（注意顺序）
    root.left = dfs(left, mid - 1)
    root.right = dfs(mid + 1, right)

    return root
```

不同遍历 = 不同 root 获取方式：

| 题目                | root 从哪来      | 递归顺序 |
| ------------------- | ---------------- | -------- |
| preorder + inorder  | preorder[idx++]  | 先左后右 |
| postorder + inorder | postorder[idx--] | 先右后左 |

面试高频陷阱：

1. ❌ 在递归里切 list（应传下标区间）
2. ❌ 每层线性找 root（应预建 HashMap: val → inorder index）
3. ❌ 忘记右子树优先（postorder 从后往前取 root 时，先建右子树）

### 1.3 五大高频 DFS 题横向对比（全都一个模板）

| 题型 | dfs 返回 | 当前层做什么 |
| --- | --- | --- |
| ① 重建二叉树 (Build Tree) | TreeNode | 创建 root，递归构造左右子树 |
| ② 翻转二叉树 (Invert Tree) | TreeNode | 交换左右 |
| ③ 最近公共祖先 (LCA) | 是否包含目标 | 合并左右结果 |
| ④ 路径总和 / 最大路径和 | 单边贡献 | 更新全局最优 |
| ⑤ 克隆二叉树 (Clone Tree) | 新节点 | 复制当前 |

② 翻转二叉树：

```python
def invert(root):
    if not root:
        return None
    root.left, root.right = invert(root.right), invert(root.left)
    return root
```

③ 最近公共祖先（LCA）：

```python
def lca(root, p, q):
    if not root or root == p or root == q:
        return root

    left = lca(root.left, p, q)
    right = lca(root.right, p, q)

    if left and right:
        return root
    return left or right
```

④ 最大路径和（单边贡献 + 全局更新）：

```python
def maxGain(node):
    if not node:
        return 0
    left = max(maxGain(node.left), 0)
    right = max(maxGain(node.right), 0)
    ans = max(ans, node.val + left + right)  # 全局最优：过当前节点的路径
    return node.val + max(left, right)       # 返回给父节点：只能选一边
```

⑤ 克隆二叉树：

```python
def clone(root):
    if not root:
        return None
    new = TreeNode(root.val)
    new.left = clone(root.left)
    new.right = clone(root.right)
    return new
```

### 1.4 统一心智模型

```text
一个节点 = 当前处理 + 左子树结果 + 右子树结果
```

三种返回值模式（超级重要）：

| 返回类型   | 代表题型           |
| ---------- | ------------------ |
| TreeNode   | 构建 / 克隆 / 翻转 |
| bool / int | 是否存在 / 路径和  |
| 自定义对象 | DP / 多信息汇总    |

进阶路线：

1. **二叉树 + 状态压缩**（Tree DP）
2. **二叉树 + 哈希映射**
3. **树 → 图 → 拓扑思维迁移**

## 2. Binary Tree — 遍历的迭代实现

> 递归实现直观；迭代（栈）实现可以控制每一步的进行，而递归必须先跑完整个递归过程。例题：[173. Binary Search Tree Iterator](https://leetcode.cn/problems/binary-search-tree-iterator/)

### 2.1 先序遍历（栈）

```java
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

### 2.2 中序遍历（栈）

```java
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

### 2.3 后序遍历（栈 + prev 标记）

```java
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

## 3. Binary Tree — 例题

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

### [310. Minimum Height Trees（最小高度树）](https://leetcode.com/problems/minimum-height-trees/)

1. 要找到最小高度的那个节点，其实就是找树的直径（树中任意两点之间的 **最长简单路径**），然后找这个直径的中心作为顶点，才会有最小高度。

## 4. Binary Search Tree (BST)

1. 一般都是用中序遍历，得到一个递增的序列。

### 4.1 Lowest Common Ancestor（利用 BST 有序性，迭代即可）

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

### 4.2 校验 BST：除了中序遍历，还可以用「上下界」性质

核心：当前节点的值是左子树的**上界**，是右子树的**下界**；DFS 途中逐步缩小界限。

```python
def dfs(node, low, high):
    if not node:
        return True
    if not (low < node.val < high):
        return False
    return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)
```

关键点辨析：**BST 校验用的不是"中序遍历的顺序"，而是 BST 的全局约束。**

1. 这段代码的执行顺序是**先序遍历**（根 → 左 → 右）：先处理当前节点，再递归左、右子树。
2. 但它仍然可以正确判断 BST——因为它用的不是"遍历顺序"，而是 BST 的定义本身：对任意节点 `node`，`low < node.val < high`。
3. `low / high` 从哪里来？
   1. 进入左子树：`high = node.val`
   2. 进入右子树：`low = node.val`
   3. 每一层都带着**祖先节点的约束**往下走。

### 4.3 Tip — 求递增序列相邻差的最小值（边界处理）

1. 将 `pre_val` 初始化为 null，一开始没有 preval，强迫其无法得到差值（跳过第一个节点的比较）。
2. 例题：[530. Minimum Absolute Difference in BST](https://leetcode.cn/problems/minimum-absolute-difference-in-bst/)

## 5. Red-Black Tree (红黑树)

1. 为什么需要红黑树，它比 BST（二叉查找树）好在哪里？
   1. BST 的形状是根据节点插入的顺序决定的，如果按升序或者降序的方式插入，二叉查找树就会退化成一个线性的结构。

### 5.1 红黑树的特性

1. 每个节点或是红色的，或是黑色的。
2. 根节点是黑色的。
3. 所有叶子（NIL节点）都是黑色的。
4. 如果一个节点是红色的，则它的两个子节点都是黑色的。
5. 从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点。

### 5.2 红黑树和平衡二叉查找树（AVL）的区别

1. **平衡条件**：
   - **AVL树**：是一种高度平衡的二叉查找树，对于任何一个节点，其左子树和右子树的高度差（平衡因子）的绝对值不超过1。这意味着AVL树是严格平衡的。
   - **红黑树**：通过确保树中没有两个连续的红节点，并且从任一节点到其每个叶子的所有路径都包含相同数目的黑节点，来近似平衡。红黑树的这些条件确保树大致保持平衡，虽然不像AVL树那样严格。

2. **插入和删除操作**：
   - **AVL树**：由于AVL树维护的是严格的平衡，所以在插入和删除节点时可能需要通过旋转操作来重新平衡树。这些操作可能相对复杂，尤其是在删除操作时。
   - **红黑树**：在插入和删除节点时，也可能需要通过旋转来调整树的平衡。但由于红黑树的平衡条件不像AVL树那样严格，所以通常红黑树的旋转操作会少于AVL树，使得在实际应用中，红黑树在插入和删除操作上可能更高效。

3. **查找性能**：
   - **AVL树**：由于AVL树是高度平衡的，所以在最坏情况下，其查找性能略优于红黑树。
   - **红黑树**：尽管红黑树的平衡条件较为宽松，但它仍然能够保证在最坏情况下查找操作的时间复杂度为O(log n)，其中n是树中节点的数量。

4. **应用场景**：
   - **AVL树**：由于其高度平衡的特性，AVL树更适合那些查找操作远多于插入和删除操作的应用场景。
   - **红黑树**：由于其在插入和删除操作上的高效性，红黑树更适合那些插入和删除操作频繁的应用场景，如在许多语言的标准库中实现的Map和Set等数据结构。

总的来说，AVL树和红黑树各有优势，适用于不同的应用场景。选择哪一种取决于具体的需求，比如对平衡的严格程度、操作的频率和类型等因素的考虑。

## 6. Tree's Diameter（树的直径）

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
