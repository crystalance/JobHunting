# Amazon OA

> Section: **Interview** — extracted from leetcode_solution.md (lines 3954-4190)

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

