# Backtracking (回溯)

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 1409-1580)

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

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #3 — Copy the partial result before adding to answer

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

### Tip #15 — Combination numbers — watch overflow

### 15.  Combination number

1. be aware of overflow!
2. when doing factorial!

### Tip #18 — Word Search backtracking template

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

