# Hash (哈希)

> Section: **Data Structure** — extracted from leetcode_solution.md (lines 93-151)

### 哈希 hash

1. java中的哈希表是怎么样的，有什么操作方法？

   1. 在Java中，哈希表通常指的是HashMap类，它是一种常用的数据结构，用于存储键值对。HashMap基于哈希表的实现，允许null键和null值，并且不保证元素的顺序。

      以下是HashMap类的一些常见操作方法：

      1. put(key, value)：将指定的键值对存储到哈希表中。
      2. get(key)：根据键获取对应的值。
      3. containsKey(key)：检查哈希表中是否包含指定的键。
      4. containsValue(value)：检查哈希表中是否包含指定的值。
      5. remove(key)：根据键移除对应的键值对。
      6. keySet()：返回哈希表中所有键组成的Set集合。
      7. values()：返回哈希表中所有值组成的Collection集合。
      8. entrySet()：返回哈希表中所有键值对组成的Set集合。

      这些方法使得我们可以方便地操作哈希表，进行插入、查找、删除等操作。HashMap还有许多其他方法，可以根据需要查阅官方文档以获取更多信息。

2. 如何定义一个哈希表？

   1. 在Java中，你可以使用HashMap类来定义一个哈希表。以下是一个简单的示例，展示了如何定义一个HashMap并向其中添加键值对：

      ```java
      import java.util.HashMap;
      
      public class Main {
          public static void main(String[] args) {
              // 定义一个HashMap
              HashMap<String, Integer> hashMap = new HashMap<>();
      
              // 向哈希表中添加键值对
              hashMap.put("A", 1);
              hashMap.put("B", 2);
              hashMap.put("C", 3);
      
              // 输出哈希表中的值
              System.out.println(hashMap); // 输出：{A=1, B=2, C=3}
          }
      }
      ```

      在这个示例中，我们首先导入了HashMap类，然后定义了一个HashMap对象`hashMap`，并向其中添加了几个键值对。你可以根据需要选择不同的数据类型作为键和值。

3. 为什么哈希表可以在 O(1)的时间内完成插入和删除操作？

   1. ```
      哈希表之所以能够在 O(1) 的时间内完成插入和删除操作，是因为它利用了哈希函数将键映射到存储位置。哈希函数能够将键均匀地分布在哈希表的槽位中，使得查找、插入和删除的时间复杂度为常数级别。
      具体来说，当要插入或删除一个元素时，哈希表会根据键通过哈希函数计算出对应的存储位置。在理想情况下，每个槽位中只有一个元素，因此无需遍历整个哈希表即可找到目标位置。这使得插入和删除操作的时间复杂度保持在 O(1)。
      然而，在实际情况下，由于哈希冲突的存在，即不同的键可能映射到同一个槽位，会导致一些额外的操作，例如链表或者红黑树的遍历。但是，通过合理的哈希函数设计和哈希表的动态扩容策略，可以使得哈希冲突的概率较低，从而仍然保持 O(1) 的平均时间复杂度。
      ```

   2. 就是说哈希表，通过给定的索引，仅需经过一次哈希函数计算，就能得到该索引所指向的位置，所以是O(1)

4. 为什么说hash和随机性有关？

5. 为什么软件算法无法产生随机数？

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #0.1 — Java Map traversal & sorting

1. map
   1. traverse
      1. by keys
         1. ` map.keySet()`
      2. By values
      3. by entryset
   2. sort
      1. Directly use tree map

### Tip #9 — HashMap / HashSet operations & complexity

### 9. hashmap & hashes

1. How to get all the keys in a map?
   1. `map.keySet();`
   2. ` HashMap<Integer, List<Integer>> map;`
   3. `List<Integer> sortedKeys = new ArrayList<>(map.keySet());` 
2. how to sort a list?
   1. Lambda expression?
   2. Collections.sort(sortedKeys);

#### time complexity of hash map & hash set

1. we can't use index to find elements in o(1) time(there's no direct method)
2. does hashset provides set.get(index)?
   1. No, a `HashSet` does not provide a method to access elements by index. `HashSet` is an unordered collection and does not maintain any order of elements, so it doesn't support index-based access like a list or array does. If you need index-based access, you would typically use a `List` in conjunction with a `HashSet`.
3. what's the time complexity of hashset remove
   1. The time complexity of removing an element from a `HashSet` is O(1) on average. This is due to the underlying hash table structure, which allows for efficient lookups and deletions. However, in the worst-case scenario (e.g., many hash collisions), the time complexity can degrade to O(n), but this is rare in practice with a well-designed hash function.
4. time complexity of remove and get(index)?
   1. for LinkedList, has O(1) on remove but O(n) on get
   2. for ArrayList, hasO(N) on remove but O(1) on get(index)
      - **LinkedList**: The `get(index)` operation has a time complexity of O(n) because it requires traversing the list from the head (or tail) to reach the specified index.
      - **ArrayList**: The `get(index)` operation has a time complexity of O(1) because it allows direct access to elements based on their index.
   3.

### Tip #20 — Set (placeholder)

### 20. set

1.

### Tip #23 — Count-array imbalance between two sequences (计数数组衡量两序列差异)

1. **Pattern**: use a **single** count array (`int[10]` for digits, `int[26]` for letters, or a HashMap for general keys) where one sequence **increments** and the other **decrements**. The **sign** of each bucket tells you which side currently has a surplus. Lets you compare two multisets in **one pass, O(n) time, O(k) space** instead of two separate maps.

2. **Example: [299. Bulls and Cows](https://leetcode.cn/problems/bulls-and-cows/)** — Topic: **Hash / counting** (+ String).

   1. One `int[10]`. Walk both strings together:
      1. position match (`secret[i] == guess[i]`) → `bulls++`, skip counting.
      2. else `cnt[secret[i]]++` and `cnt[guess[i]]--`. When you `++` a digit that was previously negative, the guess side had a pending surplus → `cows++`; when you `--` a digit that was previously positive, the secret side did → `cows++`.

   ```java
   public String getHint(String secret, String guess) {
       int bulls = 0, cows = 0;
       int[] cnt = new int[10]; // + means secret surplus, - means guess surplus
       for (int i = 0; i < secret.length(); i++) {
           char s = secret.charAt(i), g = guess.charAt(i);
           if (s == g) { bulls++; continue; }
           if (cnt[s - '0']++ < 0) cows++;   // guess had this digit waiting
           if (cnt[g - '0']-- > 0) cows++;   // secret had this digit waiting
       }
       return bulls + "A" + cows + "B";
   }
   ```

   2. **Why cows needs BOTH checks — every pair is counted once, by whichever member arrives second**

      1. A cow pair consists of one `d` from secret and one `d` from guess (at different positions). Scanning left to right, one of them shows up before the other. The rule of this solution is:

         > **A pair is scored at the moment its second member arrives.**

      2. There are only two cases:
         1. **Guess's `d` appeared earlier, secret's `d` arrives now.** The earlier guess `d` made `h[d]` negative ("guess is owed a `d`"). Now the secret side shows `d`: check `h[s] < 0` → cow. This is the natural direction: "secret digit finds an unpaired guess digit."
         2. **Secret's `d` appeared earlier, guess's `d` arrives now.** The earlier secret `d` made `h[d]` positive. Now the guess side shows `d`: check `h[g] > 0` → cow. This is the mirror direction: "guess digit finds an unpaired secret digit."

      3. If you only kept the natural check (`h[s] < 0`), you'd only catch pairs where the guess member came first — and silently miss every pair where the **secret member came first**.
         1. counter-example: `secret = "12"`, `guess = "21"` → should be `0A2B`. At idx 1, `h[2]=-1<0` scores the pair of 2s, and `h[1]=+1>0` scores the pair of 1s. With only one check you'd get `0A1B`.

      4. No double counting: at one index the two checks fire for **different digit values** (`s != g` in the else branch), so they score two different pairs; and the `++`/`--` update afterwards "consumes" the waiting partner, so an earlier digit can never be matched twice.

      5. One-liner to remember: **negative means guess is owed one, positive means secret is owed one; a cow is scored the instant a debt is repaid.**

3. **Why it matters**: the same "one array tracks the imbalance between two sequences" idea appears all over anagram / balancing / matching problems — recognizing it generalizes far beyond 299.

4. **Practice list (same idea)**

   1. Direct anagram / count-matching:
      1. [242. Valid Anagram](https://leetcode.cn/problems/valid-anagram/) — canonical: ++ for s, −− for t, all zero ⇒ anagram.
      2. [383. Ransom Note](https://leetcode.cn/problems/ransom-note/)
      3. [387. First Unique Character in a String](https://leetcode.cn/problems/first-unique-character-in-a-string/)
      4. [350. Intersection of Two Arrays II](https://leetcode.cn/problems/intersection-of-two-arrays-ii/)
      5. [1657. Determine if Two Strings Are Close](https://leetcode.cn/problems/determine-if-two-strings-are-close/)
   2. Sliding window + count-balance:
      1. [438. Find All Anagrams in a String](https://leetcode.cn/problems/find-all-anagrams-in-a-string/)
      2. [567. Permutation in String](https://leetcode.cn/problems/permutation-in-string/)
      3. [76. Minimum Window Substring](https://leetcode.cn/problems/minimum-window-substring/) — track a `need` count + a `missing` counter (the imbalance).
   3. Counting-array to find mismatches:
      1. [645. Set Mismatch](https://leetcode.cn/problems/set-mismatch/)
      2. [2215. Find the Difference of Two Arrays](https://leetcode.cn/problems/find-the-difference-of-two-arrays/)
      3. [389. Find the Difference](https://leetcode.cn/problems/find-the-difference/) — counting or XOR.
   4. XOR "balancing" variant (same imbalance idea, different operator):
      1. [136. Single Number](https://leetcode.cn/problems/single-number/) / [137](https://leetcode.cn/problems/single-number-ii/) / [260](https://leetcode.cn/problems/single-number-iii/) — pairs cancel, leftover is the imbalance.

5. Suggested order: **242 → 383 → 438 → 567 → 76**, then **645 / 389 / 136** for the counting-vs-XOR contrast.

