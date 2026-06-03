# Binary Search (二分查找)

> Section: **Algorithm** — extracted from `leetcode_solution.md` (lines 3299-3337), `coding-tricks.md` (Tip #6), and related notes.

### Binary search

#### 1. JAVA binarySearch API

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

#### 2. Write binary search ourselves

1. apart from search a specific value, (like 6 in 2 5 3 3 8 7 6 8 9 0), we can search a value meets some condition 
   1. just add the condition to the 
      1. in problem 162
         1. ![image-20241024162137120](../images/image-20241024162137120.png)
         2. the condition is larger than neighbor nodes or is the egde node
   2. Just to remember: 理解二分，请牢记区间的定义！区间内的数（下标）都是还未确定大小关系的，有的是 <，有的是 ≥；区间外的数（下标）都是确定大小关系的！对于本题（递增数组），区间左侧外面的都是 <，区间右侧外面的都是 ≥。从这个定义可以知道，找到了 ≥ 的数之后，要把这个数（下标）放在区间外面，而不是区间里面！
   3. for example:
      1. ![image-20241212153948374](../images/image-20241212153948374.png)
      2. in this type, ` if nums[mid] < target` means that all the elements with index <= mid are less than target, so you just change the leftbound of the interval to mid+1 (` left = mid + 1`)
   4. ![image-20250126143229789](../images/image-20250126143229789.png)
   5. ![image-20250126143132128](../images/image-20250126143132128.png)
   6. Why left?
      1. look the ternimation condition, when left = [every thing that lower than target]+1
      1. 统一写法：双闭区间，返回left指针（根据if else条件比target小的，都在left指针的左边）
      1. 注意返回的时候left的值可能比区间的最大的index还大1，这个说明target比该区间最大的值还大

#### 3. lowerBound — open interval template (开区间写法)

1. 见 https://www.bilibili.com/video/BV1AP41137w7/

2. **半开区间 `[l, r)` 写法（推荐）**: search range is `[left, right)`, so `left` starts at `0` and `right` starts at `n` (one past the end). The loop ends when `left == right`, and that final `left` is the answer.

   ```java
   // returns the first index i where arr[i] >= target
   private int lowerBound(int[] arr, int target) {
       int left = 0, right = arr.length; // 半开区间 [left, right)
       while (left < right) {            // 区间非空
           // 循环不变量：
           // arr[i] <  target   for all i in [0, left)
           // arr[i] >= target   for all i in [right, n)
           int mid = left + (right - left) / 2;
           if (arr[mid] < target)
               left = mid + 1; // 丢弃 [left, mid]，范围缩到 [mid+1, right)
           else
               right = mid;    // 丢弃 [mid, right)，范围缩到 [left, mid)
       }
       return left; // == right
   }
   ```

3. Key differences vs. the 开区间 `(left, right)` style:
   1. Init: `left = 0, right = n` (not `left = -1, right = n`).
   2. Loop condition: `left < right` (not `left + 1 < right`).
   3. The "less than" branch moves `left = mid + 1` (mid is excluded), while the "else" branch keeps `right = mid`.
   4. Return `left` (which equals `right` at the end).

4. Used in sliding-window problems to locate the left boundary of a valid window, e.g. [2106. 摘水果](https://leetcode.cn/problems/maximum-fruits-harvested-after-at-most-k-steps/).

#### 3.5 upperBound — first position that is strictly `> target`

1. The only change vs. `lowerBound` is the comparison: switch `<` to `<=`. That single character moves the boundary one step to the right.

   1. `lowerBound`: everything left of the answer is `<  target`, so it lands on the first `>= target`.
   2. `upperBound`: everything left of the answer is `<= target`, so it lands on the first `>  target`.

2. **半开区间 `[l, r)` 写法**:

   ```java
   // returns the first index i where arr[i] > target
   private int upperBound(int[] arr, int target) {
       int left = 0, right = arr.length; // 半开区间 [left, right)
       while (left < right) {            // 区间非空
           // 循环不变量：
           // arr[i] <= target   for all i in [0, left)   (注意是 <=，lowerBound 是 <)
           // arr[i] >  target   for all i in [right, n)
           int mid = left + (right - left) / 2;
           if (arr[mid] <= target)
               left = mid + 1; // 范围缩到 [mid+1, right)
           else
               right = mid;    // 范围缩到 [left, mid)
       }
       return left; // == right
   }
   ```

3. **Reuse trick**: you don't even have to write a second function. Since the first index `> target` equals the first index `>= target + 1` (for integers), you can call:

   1. ```java
      upperBound(arr, target) == lowerBound(arr, target + 1);
      ```

4. **The 4 boundary queries from these two helpers** (let `lo = lowerBound`, `hi = upperBound`):

   | want | formula |
   | --- | --- |
   | first `>= target` | `lo(target)` |
   | first `>  target` | `hi(target)` |
   | last  `<  target` | `lo(target) - 1` |
   | last  `<= target` | `hi(target) - 1` |

5. **Why use upperBound instead of lowerBound?**

   1. **Counting occurrences of a value** in a sorted array with duplicates: `count = upperBound(target) - lowerBound(target)`. `upperBound` gives the end of the equal-range, `lowerBound` gives the start. This is exactly how [34. Find First and Last Position](https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/) is solved.
   2. **Finding the last element `<= target`** (e.g. the latest event before a deadline, the largest value not exceeding a budget): use `upperBound(target) - 1`. `lowerBound` cannot express this directly because it would stop at the first equal element, excluding the duplicates you want to keep.
   3. **Insert-after semantics**: when inserting a new equal key and you want it placed *after* existing equal keys (stable / append behavior), insert at `upperBound`. `lowerBound` would insert *before* them.
   4. In short: pick `lowerBound` when "equal counts as found / belongs on the right side", and `upperBound` when "equal counts as already-passed / belongs on the left side".

#### 4. Application: LIS with binary search

1. Longest increasing subsequence — use `Collections.binarySearch` to find insertion position in O(log n) per element:

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

#### 5. Python: bisect module

1. `import bisect` — Python standard library for binary search on sorted lists (`bisect_left`, `bisect_right`, `insort`).
