# Divide and Conquer

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 2159-2404)

### Divide and conquer

#### tricks

1. When you want to divide the problem into small parts, do not copy the context of original problem and start a new one, lets say if you want to Merge lists on a list array, the first thing you need to do is to break it into 2 arrays, and merge them recursively. At this point, do not make 2 new arrays, instead, make a new function, and pass the index of the array to this function.
2. if you want divide and conquer, make sure that there are always multiple functions working at one time.

#### Examples

1. [148. Sort List](https://leetcode.com/problems/sort-list/)

   1. My solution （）

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
             public ListNode sortList(ListNode head) {
         
                 if(head==null){return null;}
                 if(head.next==null){return head;}
                 ListNode curNode = head;
                 ListNode preNode = head;
                 ListNode LeastNode = new ListNode();
                 ListNode preLeastNode = new ListNode();
                 int minVal = Integer.MAX_VALUE;
                 while(curNode!=null){
                     int curVal = curNode.val;
                     if(curVal<minVal){
                         minVal = curVal;
                         LeastNode = curNode;
                         preLeastNode = preNode;
                     }
                     preNode = curNode;
                     curNode = curNode.next;
                 }
         
                 ListNode LastNode = preNode;
                 
                     
                 if(LeastNode == LastNode){
                     LeastNode.next =  head;
                     preLeastNode.next = null;
                 }else{
                     LastNode.next = head;
                     preLeastNode.next = null;
                 }
         
         
                 LeastNode.next = sortList(LeastNode.next);
                 return LeastNode;
         
             }
         }
         ```

      2. fix

         1. ```java
            class Solution {
                public ListNode sortList(ListNode head) {
                    if (head == null || head.next == null) {
                        return head;
                    }
            
                    ListNode leastNode = head;
                    ListNode leastPrev = null;
                    ListNode curNode = head;
                    ListNode prevNode = null;
            
                    // Find the minimum node
                    while (curNode != null) {
                        if (curNode.val < leastNode.val) {
                            leastNode = curNode;
                            leastPrev = prevNode; // Track the previous node of the least node
                        }
                        prevNode = curNode;
                        curNode = curNode.next;
                    }
            
                    // Remove the least node from the list
                    if (leastPrev != null) {
                        leastPrev.next = leastNode.next; // Bypass leastNode
                    } else {
                        head = leastNode.next; // If leastNode is head
                    }
            
                    // Recursively sort the remaining list
                    leastNode.next = sortList(head);
            
                    return leastNode; // Return the sorted list starting with leastNode
                }
            }
            
            ```

         2. Use divide and conquer:

            1. ```java
               
               class Solution {
                   public ListNode findMiddle(ListNode head) {
                       if (head == null) {
                           return null;
                       }
                       ListNode fastPointer = head.next; // we want to split the list evenly, so we need head.next
                       ListNode slowPointer = head;
               
                       // Move fastPointer two steps and slowPointer one step
                       while (fastPointer != null && fastPointer.next != null) {
                           fastPointer = fastPointer.next.next;
                           slowPointer = slowPointer.next;
                       }
                       return slowPointer; // Returns the middle node
                   }
               
                   public ListNode merge(ListNode left, ListNode right) {
                       ListNode temp = new ListNode(-1); // Dummy node
                       ListNode curNode = temp;
               
                       while (left != null && right != null) {
                           if (left.val <= right.val) {
                               curNode.next = left;
                               left = left.next;
                           } else {
                               curNode.next = right;
                               right = right.next;
                           }
                           curNode = curNode.next; // Move the current pointer
                       }
               
                       // Append any remaining nodes
                       if (left != null) {
                           curNode.next = left;
                       }
                       if (right != null) {
                           curNode.next = right;
                       }
                       return temp.next; // Return the merged list, skipping the dummy node
                   }
               
                   public ListNode sortList(ListNode head) {
                       if (head == null || head.next == null) {
                           return head; // Base case: the list is empty or has one node
                       }
                   // Find the middle of the list
                   ListNode middleNode = findMiddle(head);
                   
                   // Split the list into two halves
                   ListNode rightHead = middleNode.next;
                   middleNode.next = null; // Important: split the list
                   
                   // Sort each half
                   ListNode left = sortList(head);
                   ListNode right = sortList(rightHead);
                   
                   // Merge sorted halves
                   return merge(left, right);
                   }
               }
               
               ```

   2. fda

      1. my solution (has bug)

         1. ```java
            class Solution {
                public Node construct(int[][] grid) {
                    int n = grid.length;
                    Node root = new Node(false, false);
            
                if (n == 2) {
                    Node topLeft = new Node(grid[0][0] == 1, true);
                    Node topRight = new Node(grid[0][1] == 1, true);
                    Node bottomLeft = new Node(grid[1][0] == 1, true);
                    Node bottomRight = new Node(grid[1][1] == 1, true);
            
                    if (topLeft.val && topRight.val && bottomLeft.val && bottomRight.val) {
                        root.isLeaf = true;
                        root.val = true;
                    } else if (!topLeft.val && !topRight.val && !bottomLeft.val && !bottomRight.val) {
                        root.isLeaf = true;
                        root.val = false;
                    }else{
                        root.topLeft = topLeft;
                        root.topRight = topRight;
                        root.bottomLeft = bottomLeft;
                        root.bottomRight = bottomRight;
                    }
            
                } else {
                    // Divide
                    int middle = n / 2;
                    int[][] TopLeftGrid = new int[middle][middle];
                    int[][] TopRightGrid = new int[middle][middle];
                    int[][] BottomLeftGrid = new int[middle][middle];
                    int[][] BottomRightGrid = new int[middle][middle];
            
                    for (int i = 0; i < middle; i++) {
                        for (int j = 0; j < middle; j++) {
                            TopLeftGrid[i][j] = grid[i][j];
                            TopRightGrid[i][j] = grid[i][j + middle];
                            BottomLeftGrid[i][j] = grid[i + middle][j];
                            BottomRightGrid[i][j] = grid[i + middle][j + middle];
                        }
                    }
            
                    Node topLeft = construct(TopLeftGrid);
                    Node topRight = construct(TopRightGrid);
                    Node bottomLeft = construct(BottomLeftGrid);
                    Node bottomRight = construct(BottomRightGrid);
            
                    if (topLeft.isLeaf && topRight.isLeaf && bottomLeft.isLeaf && bottomRight.isLeaf) {
                        if (topLeft.val && topRight.val && bottomLeft.val && bottomRight.val) {
                            root.val = true;
                            root.isLeaf = true;
                        } else if(!topLeft.val && !topRight.val && !bottomLeft.val && !bottomRight.val){
                            root.val = false;
                            root.isLeaf = true; // This should remain false if not all are true
                        }
                        return root;
                    } 
                    root.val = false;
                    root.topLeft = topLeft;
                    root.topRight = topRight;
                    root.bottomLeft = bottomLeft;
                    root.bottomRight = bottomRight;
                }
            
                return root;
            }
            }
            ```

      2. 

