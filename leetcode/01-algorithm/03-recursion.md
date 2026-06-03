# Recursion (递归)

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 1399-1408)

### 递归

#### [124. Binary Tree Maximum Path Sum](https://leetcode.cn/problems/binary-tree-maximum-path-sum/)

1. 主要考虑的是递归的主体，然后再看边界条件，
2. 要求最大，首先看看这个最大的集合如何去寻找，按什么方式找？
3. 这道题中，就是说考虑以每个节点为根节点，然后路径经过这个根节点的值最大的节点。
4. <img src="/Users/lanceliao/Desktop/Screenshot 2024-05-23 at 11.07.44.png" alt="Screenshot 2024-05-23 at 11.07.44" style="zoom: 33%;" /> 
5. 然后再细分，要找到这样的路径，就得找左右子树的最大贡献值，（这里的最大贡献值指的是以这个节点为端点的路径的最大贡献值）

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #2 — Pass info via parameters in DFS recursion

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

### Tip #8 — DFS — deep-copy when capturing results

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

