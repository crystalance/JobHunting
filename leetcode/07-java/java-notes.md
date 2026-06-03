# Java Notes

> Section: **Java** — extracted from leetcode_solution.md (lines 5276-5355)

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

   

