# Monotonic Queue (单调队列)

> Section: **Data Structure** — new topic. Sibling of the monotonic **stack** (see `02-stack.md`). Reference taxonomy: 灵神「常用数据结构」→ 队列 / 滑动窗口最值。

### 1. A general pattern for recognizing monotonic queue problems

When you see a problem that can be rewritten as:

- process indices from left to right,
- for each current index `j`, you need to choose a previous index `i`,
- some previous candidates become permanently worse than a newer one (**dominated**),
- and once a candidate has produced its optimal answer, it will never improve in the future,

a **monotonic queue** is often the right data structure.

1. The queue stores **candidate indices** in a useful order (increasing or decreasing by value).
2. Two kinds of eviction:
   1. **From the back** — a new candidate `j` *dominates* older ones (e.g. `nums[j]` is better and also more recent), so pop those older candidates before pushing `j`. This keeps monotonicity.
   2. **From the front** — a candidate has fallen out of the valid window / range, so it can never be used again; pop it.
3. Because each index is pushed and popped **at most once**, the whole scan is **O(n)**.

### 2. Template (deque of indices)

```java
// sliding window maximum, window size k -> decreasing deque (front = max)
int[] maxSlidingWindow(int[] nums, int k) {
    int n = nums.length;
    int[] ans = new int[n - k + 1];
    Deque<Integer> dq = new ArrayDeque<>(); // stores indices, nums[dq] decreasing
    for (int j = 0; j < n; j++) {
        // 1. back eviction: new value dominates smaller/older values
        while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[j]) dq.pollLast();
        dq.offerLast(j);
        // 2. front eviction: index out of the window [j-k+1, j]
        if (dq.peekFirst() <= j - k) dq.pollFirst();
        // 3. record answer once the window is full
        if (j >= k - 1) ans[j - k + 1] = nums[dq.peekFirst()];
    }
    return ans;
}
```

1. Want the **minimum** instead? Keep the deque **increasing** (`nums[dq.peekLast()] >= nums[j]` as the pop condition); front is then the min.

### 3. Why it works (the two invariants)

1. **Monotonicity ⇒ front is the answer.** If the deque is decreasing, the front is always the current window's max. Any element smaller than a newer one to its right is useless (dominated), so we drop it — it can never be the max while that newer, larger element is still in the window.
2. **Front expiry ⇒ correctness of the window.** The only reason we ever remove the front (other than domination) is that its index left the valid range. This matches the "once a candidate is out of range it never comes back" property.

### 4. Example problems

1. [239. Sliding Window Maximum](https://leetcode.cn/problems/sliding-window-maximum/) — the canonical template above.
2. [1425. Constrained Subsequence Sum](https://leetcode.cn/problems/constrained-subsequence-sum/) — DP `f[j] = nums[j] + max(0, max f[i] for j-k <= i < j)`. The `max f[i]` over a sliding window of size `k` is exactly a monotonic-queue query → O(n) instead of O(nk).
3. [862. Shortest Subarray with Sum at Least K](https://leetcode.cn/problems/shortest-subarray-with-sum-at-least-k/) — on prefix sums `P`; keep an **increasing** deque of prefix indices. Front eviction: if `P[j] - P[dq.front] >= K`, record length and pop front (that start can't give a shorter answer later). Back eviction: pop `dq.back` while `P[dq.back] >= P[j]` (a larger-or-equal earlier prefix is dominated by the newer, smaller one).
4. [1438. Longest Continuous Subarray With Absolute Diff ≤ Limit](https://leetcode.cn/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/) — maintain **two** deques (one max, one min) over the window; shrink from the left when `max - min > limit`.

### 5. Monotonic queue vs. monotonic stack

1. **Stack** answers "nearest smaller/greater element" (previous/next), evicting only from one end.
2. **Queue** answers "extreme value within a moving range/window", evicting from **both** ends (back for domination, front for expiry).
3. Both rely on the same domination idea and both are O(n) because each index is touched a constant number of times.


---
review:
1499:
Yes, exactly! What you're describing is called **"mental set"** or **"mental fixation"** in English.

Some natural ways to say it are:

* **I had a mental set.** (closest to 思维定势)
* **I got stuck in a certain way of thinking.** ⭐ (very natural)
* **I was trapped by my usual pattern of thinking.**
* **I was thinking about it like a standard sliding window problem.**
* **I fell into the sliding window mindset.** (casual)

For example:

> I got stuck in the sliding window mindset, so I instinctively inserted the current element before updating the answer.

---

Now, about **why this problem is different**—this is a really good question. The answer is that **this isn't actually a sliding window problem**, even though it uses a deque.

## Regular sliding window

Take Leetcode 3 (Longest Substring Without Repeating Characters):

```java
for (right = 0; right < n; right++) {

    // add nums[right]

    while (window invalid)
        remove left

    update answer
}
```

The key idea is:

> **The window itself is the answer.**

After adding `right`, the window becomes

```text
[left ... right]
```

and you're asking:

> "Is this window valid?"

If yes,

```text
answer = f(window)
```

So of course you must **include `right` first**, because the current window ends at `right`.

---

## But 1499 is different

For every `j`, you're asking

```text
Among all previous i,

which one maximizes

yi - xi ?
```

Notice the word:

> **previous**

`j` is **not** one of the candidates.

The deque stores

```text
candidate i's
```

not

```text
current window
```

When processing `j`, the deque should conceptually be

```text
i1
i2
i3
```

Then you choose the best one:

```text
best i + current j
```

Only **after finishing** with `j` does `j` become a candidate for future points.

So the timeline is

```text
process j

↓

use previous points

↓

finish processing j

↓

j becomes previous
```

That's why insertion happens last.

---

## Think of it as a DP transition

A better mental model is dynamic programming.

Suppose

```text
dp[j] = best answer ending at j
```

Then

```text
dp[j]
```

depends on

```text
dp[0...j-1]
```

never on

```text
dp[j]
```

itself.

The deque is just accelerating this transition.

The order naturally becomes

```text
1. Remove expired previous states

2. Query best previous state

3. Insert current state
```

Exactly like DP.

---

## Compare the two mindsets

### Sliding window

```text
Window = answer

add current

↓

fix window

↓

answer = current window
```

The current element **belongs to the answer**.

---

### Monotonic deque optimization

```text
Current element asks a question.

↓

Previous candidates answer it.

↓

Current element joins the candidates.
```

The current element is a **query**, not a candidate.

---

I actually use this rule of thumb when solving deque problems:

> **Ask yourself: "Is the current element part of the answer, or is it asking a question about previous elements?"**

* If it's **part of the answer** (sliding window, longest/shortest window, etc.), then:

  > **Insert → Maintain → Update Answer**

* If it's **asking about previous elements** (1499, 862, DP optimizations, Convex Hull Trick, etc.), then:

  > **Maintain Previous Candidates → Query → Insert Current**

Once you start classifying monotonic deque problems into these two categories, the correct order of operations becomes almost automatic. In my experience, this distinction is one of the biggest "aha!" moments for understanding deque-based algorithms.




----
## problems
1. 1696. Jump Game VI
    1. greedy is not OK here
    2. DP + monotonic Queue
        
