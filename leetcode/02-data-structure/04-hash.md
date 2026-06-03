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

