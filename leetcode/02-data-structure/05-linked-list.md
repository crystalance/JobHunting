# Linked List (链表)

> Section: **Data Structure** — extracted from leetcode_solution.md (lines 152-486)

### 链表

#### 1.快慢指针（用于判断链表中是否存在循环）

1. 要修改代码以使用快慢指针来检测链表中是否存在循环，您可以按照以下方式修改 `hasCycle` 方法：

   ```java
   public class Solution {
       public boolean hasCycle(ListNode head) {
           if (head == null || head.next == null) {
               return false;
           }
   
           ListNode slow = head;
           ListNode fast = head.next;
   
           while (slow != fast) {
               if (fast == null || fast.next == null) {
                   return false;
               }
               slow = slow.next;
               fast = fast.next.next;
           }
   
           return true;
       }
   }
   ```

   这样，您就使用了快慢指针来检测链表中是否存在循环。如果存在循环，快慢指针最终会相遇，返回 `true`；否则返回 `false`。

2. the feature of the fast-slow pointer:

   1. leetcode 142
   2. <img src="../images/image-20241027002447299.png" alt="image-20241027002447299" style="zoom:50%;" />


#### 2. 自己构建双向链表实现LRU

1. [LRU 缓存](https://leetcode.cn/problems/lru-cache/)

2. 

   ```java
   class ListNode{
       ListNode prev; 
       ListNode next;
       int key;
       int value;
   
       public ListNode(int key, int value){
           this.key = key;
           this.value = value;
           prev = null;
           next = null;
       }
   
   }
   
   class LRUCache {
       Map<Integer, ListNode> map = new HashMap<>();
       ListNode head = new ListNode(0,0); 
       ListNode tail = new ListNode(0,0); 
       int capacity;
       public LRUCache(int capacity) {
           this.capacity = capacity;
           head.next = tail;
           tail.prev = head;
       }
       
       public int get(int key) {
           if(!map.containsKey(key)) return -1;
           
           ListNode node = map.get(key);
           remove(node);
           add(node);  
           return node.value;  
       }
       
       public void put(int key, int value) {
           if(map.containsKey(key)){
               ListNode old = map.get(key);
               remove(old);
           }
           ListNode node = new ListNode(key, value);
           map.put(key,node);
           add(node);
   
           if(map.size() > capacity){
               ListNode toBeDelete = head.next;
               remove(toBeDelete);
               map.remove(toBeDelete.key);
           }
       }
   
       public void add(ListNode node){
           ListNode prevEnd = tail.prev;
           prevEnd.next = node;
           node.prev = prevEnd;
           node.next = tail;
           tail.prev = node;
       }
   
       public void remove(ListNode node){
           node.prev.next = node.next;
           node.next.prev = node.prev;
       }
   }
   
   /**
    * Your LRUCache object will be instantiated and called as such:
    * LRUCache obj = new LRUCache(capacity);
    * int param_1 = obj.get(key);
    * obj.put(key,value);
    */
   ```


#### 3. Copy List with Random Pointer

1. [138. Copy List with Random Pointer](https://leetcode.cn/problems/copy-list-with-random-pointer/)

2. Solution: to copy nodes separately and in recursion

   1. ```java
      /*
      // Definition for a Node.
      class Node {
          int val;
          Node next;
          Node random;
      
          public Node(int val) {
              this.val = val;
              this.next = null;
              this.random = null;
          }
      }
      */
      
      class Solution {
          Map<Node,Node> cache_copied_nodes = new HashMap<Node,Node>();
         
          public Node copyRandomList(Node head) {
              if(head==null){
                  return null;
              }
              if(!cache_copied_nodes.containsKey(head)){
                  Node copyNode = new Node(head.val);
                  cache_copied_nodes.put(head,copyNode);
                  copyNode.next = copyRandomList(head.next);
                  copyNode.random = copyRandomList(head.random);
              }
              return cache_copied_nodes.get(head);
         
          }
      }
      ```

   2. In this code, why it would be wrong if I put `cache_copied_nodes.put(head,copyNode);` this step after I jump into another recursion?

      1. 在这段代码中，如果将cache_copied_nodes.put(head,copyNode);这一步放在跳入另一个递归之后，会导致在处理相同节点时出现问题。由于递归的特性，程序会在回溯时再次访问相同的节点，如果在跳入另一个递归之后才将节点放入缓存，会导致无法正确地获取到已经复制的节点，从而破坏了复制链表的正确性。因此，正确的做法是在递归之前就将节点放入缓存，以确保在需要时能够正确地获取到已经复制的节点。
      2. What if `head.random = head`?

   3. **Why do we think of using recursion to solve this problem?**

      1. Recursion is **a natural choice** for solving problems involving **linked structures like linked lists or trees because it simplifies the logic by breaking down the problem into smaller subproblems.** In the case of copying a linked list with random pointers, each node can be seen as a smaller linked list in itself, where you need to copy the current node and then recursively copy the next and random nodes.

         Recursion allows you to handle each node and its connections independently, making it easier to manage the complex relationships between nodes in a linked structure. It also helps in reducing the code complexity and making the solution more elegant and concise compared to iterative approaches.

         Overall, recursion is a powerful technique for dealing with problems that exhibit recursive substructure, making it a natural choice for tasks like traversing and manipulating linked structures.

      2. 

#### 4. reverse linked list

1. [92. Reverse Linked List II](https://leetcode.cn/problems/reverse-linked-list-ii/)

2. learning points

3. code

   1. ```java
      /**
       * Definition for singly-linked list.
       * public class ListNode {
       *     int val;
       *     ListNode next;
       *     ListNode() {}
       *     ListNode(int val) { this.val = val; }
       *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
       * }
       */
      class Solution {
          public ListNode reverseBetween(ListNode head, int left, int right) {
              if(left == right) {
                  return head;
              }
              //We use a dummy node to simplify handling cases where the sublist to be reversed includes the head of the original linked list.
              ListNode dummy = new ListNode(0);
              dummy.next = head;
              ListNode neck = dummy; 
            	// We use a neck node to keep track of the node before the sublist to be reversed.
              for (int i = 0; i < left - 1; i++) {
                  neck = neck.next;
              }
      
              ListNode leftNode = neck.next;
              ListNode rightNode = leftNode;
              //We use a neck node to keep track of the node before the sublist to be reversed.
              for (int i = 0; i < right - left; i++) {
                  rightNode = rightNode.next;
              }
      
              ListNode tail = rightNode.next;
      				//reverse
              ListNode previousNode = tail;
              ListNode currentNode = leftNode;
              ListNode nextNode;
      
              while (currentNode != tail) {
                  nextNode = currentNode.next;
                  currentNode.next = previousNode;
                  previousNode = currentNode;
                  currentNode = nextNode;
              }
      
              neck.next = rightNode;
      
              return dummy.next;
      
          }
      }
      ```

#### [19. Remove Nth Node From End of List](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/)

1. **learning point**

   1. we should add a head node of the list to better manipulate the list, processing the edge cases.

2. my version of answer:

   1. ```java
      class Solution {
          Map<Integer,ListNode> node_map = new HashMap<Integer,ListNode>();
          public ListNode removeNthFromEnd(ListNode head, int n) {
              
              if(head.next==null){return null;}
      
              ListNode dummy = new ListNode(0);
              dummy.next = head;
              node_map.put(0,dummy);
              ListNode pointer = head;
              int index = 1;
              while(pointer!=null){
                  node_map.put(index, pointer);
                  index++;
                  pointer = pointer.next;
              }
              ListNode before = node_map.get(index-n-1);
              if(n==1){before.next = null;}else{
                  ListNode after = node_map.get(index-n+1);
                  before.next = after;
              }
              return dummy.next;
      
      
          }
      }
      ```

   2. analyze

      1. To analyze the time complexity of the provided program for removing the nth node from the end of a linked list, let's break down the operations:

         1. Traversing the Linked List to Populate the Map:
            1. In this step, the program traverses the entire linked list of size N to populate the node_map with indices and corresponding nodes.
               1. Time complexity: O(N)
                  Accessing Nodes from the Map:
            2. After populating the map, the program accesses nodes from the map based on the calculated indices.
               1. Time complexity: O(1)
            3. Therefore, the overall time complexity of this program is O(N) due to the traversal of the linked list to populate the map with node indices. The subsequent operations of accessing nodes from the map have a time complexity of O(1) since accessing elements from a HashMap is considered constant time.

         In conclusion, the time complexity of this program is O(N) where N is the number of nodes in the input linked list.

3. The reference solution

   1. ```java
      class Solution {
          public ListNode removeNthFromEnd(ListNode head, int n) {
              ListNode dummy = new ListNode(0, head);
              int length = getLength(head);
              ListNode cur = dummy;
              for (int i = 1; i < length - n + 1; ++i) {
                  cur = cur.next;
              }
              cur.next = cur.next.next;
              ListNode ans = dummy.next;
              return ans;
          }
      
          public int getLength(ListNode head) {
              int length = 0;
              while (head != null) {
                  ++length;
                  head = head.next;
              }
              return length;
          }
      }
      
      
      ```

4. The first solution is faster than the second solution because it directly calculates the position of the node to be removed using a two-pointer technique without the need to store all nodes and their indices in a map.

   In the first solution:

   It uses a dummy node to handle edge cases efficiently.
   It calculates the length of the linked list by traversing it once.
   It then directly moves to the node to be removed by iterating through the list with two pointers (slow and fast pointers).
   Once the correct position is found, it removes the node in constant time without additional lookups.
   In contrast, the second solution:

   It stores all nodes and their indices in a map, which requires additional space and time complexity to build the map.
   It involves traversing the linked list twice - once to populate the map and once to find and remove the node at the calculated index.
   It relies on map lookups to find the nodes, which adds overhead compared to direct pointer manipulation in the first solution.
   Due to these factors, the first solution is more efficient and faster than the second solution in terms of time complexity and space complexity.

#### [25. K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)

1. 思路
   1. 先遍历一遍

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #0.4 — Deque + LRU doubly-circular linked list

4. linkedlist

   1. deque

      1. ` Deque<Integer> deque = new LinkedList<>();`

   2. remove

      1. what's the cost of the remove operation?

         1. its O(n)

         2. so we can't simply use duque in leetcode 146(LRU cache here)

            1. ```java
               class LRUCache {
                   private final int capacity;
                   private final Map<Integer, Integer> map;
                   private final Deque<Integer> deque;
               
                   public LRUCache(int capacity) {
                       this.capacity = capacity;
                       this.map = new HashMap<>();
                       this.deque = new LinkedList<>();
                   }
               
                   public int get(int key) {
                       if (!map.containsKey(key)) {
                           return -1;
                       }
                       // Move the accessed key to the front of the deque
                       deque.remove(key); // the cost of this is O(n)!!
                       deque.addFirst(key);
                       return map.get(key);
                   }
               
                   public void put(int key, int value) {
                       if (map.containsKey(key)) {
                           deque.remove(key);
                       } else if (map.size() == capacity) {
                           // Remove the least recently used element
                           int lruKey = deque.removeLast();
                           map.remove(lruKey);
                       }
                       // Add the new key-value pair
                       map.put(key, value);
                       deque.addFirst(key);
                   }
               }
               
               ```

            2. Instead, we can maintain a doubly circular linked list

               1. ```java
                  class ListNode{
                    //data
                    int key;
                    int value;
                    //pointer
                    ListNode prev;
                    ListNode next;
                    public ListNode(int key, int value){
                      this.key = key;
                      this.value = value;
                    }
                  }
                  class DCLinkedList{
                    ListNode head;
                    ListNode tail;
                    public DCLinkedList(){
                      // dummy;
                      head = new ListNode(-1,-1);
                      tail = new ListNode(-1,-1);
                      // make it circular
                      head.prev = tail;
                      tail.next = head;
                    }
                    //how to make remove operation's cost O(1)?
                    //simply change the pointer
                     public void remove(ListNode node) {
                          node.prev.next = node.next;
                          node.next.prev = node.prev;
                      }
                    
                  }
                  
                  ```

### Tip #5 — Dummy node pattern

### 5. dummy node in linkedList problems

1. why dummy node?
   1. to better tackle first node in the list
   2. in reverse list problems,
   3. we can also remember the head of the list by returning dummy.next

### Tip #23 — Fast/slow pointer — cycle detection

### 23. linkedlist

#### 1. fast slow pointer

1. what's the difference between these two code?

   1. ```java
      public class Solution {
          public boolean hasCycle(ListNode head) {
              ListNode fastIndex = head;
              ListNode slowIndex = head;
              while(fastIndex!=null&&fastIndex.next!=null){
                  fastIndex = fastIndex.next.next;
                  slowIndex = slowIndex.next;
                  if(slowIndex == fastIndex){
                      return true;
                  }
              }
              return false;
          }
      }
      ```

   2. ```java
      public boolean hasCycle(ListNode head) {
              ListNode fastIndex = head;
              ListNode slowIndex = head;
              while(fastIndex!=null&&slowIndex!=null){
                  if(fastIndex.next!=null){
                      fastIndex = fastIndex.next.next;
                  }else{
                    break; // fix bug: added a break, or slowIndex would 
                  }
                  slowIndex = slowIndex.next;
                  if(slowIndex == fastIndex){
                      return true;
                  }
              }
              return false;
          }
      ```

