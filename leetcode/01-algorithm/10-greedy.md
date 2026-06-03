# Greedy (贪心)

> Section: **Algorithm** — split from Dynamic Programming. Greedy problems make a locally-optimal choice at each step that proves to lead to the global optimum, without needing to memoize states.

## Problems

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
