# Union Find (并查集)

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 2112-2158)

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

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #7 — When to use Union-Find

### 7. Union Find set

1. Tutorial: https://programmercarl.com/%E5%9B%BE%E8%AE%BA%E5%B9%B6%E6%9F%A5%E9%9B%86%E7%90%86%E8%AE%BA%E5%9F%BA%E7%A1%80.html#%E8%83%8C%E6%99%AF
2. what kind of problems can it solve?
   1. Connectedness problems
      1. to determine whether a 
3. Examples:
   1. [128. Longest Consecutive Sequence](https://leetcode.cn/problems/longest-consecutive-sequence/)
   2. [684. Redundant Connection](https://leetcode.cn/problems/redundant-connection/)

### Tip #17 — Union-Find — canonical Java template

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

