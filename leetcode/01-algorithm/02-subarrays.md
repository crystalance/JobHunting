# Subarrays

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 1391-1398)

### subarrays

#### 1. the sum of subarrays

1. we can maintain a hash map to record the sum of nums[0.....i],
2. once we get the sum, we can find other sum, 
3. Lets say i want to find a subarray with sum k, what i do is, keep the ith sum, find if there exist its_sum - k in map,

