# Priority Queue

> Section: **Algorithm** — extracted from leetcode_solution.md (lines 2405-2515)

### priority queue

1. [502. IPO](https://leetcode.com/problems/ipo/)

   1. my solution (out of time limitation)

      1. ```java
         class Solution {
             public int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
         
                 //because k is limited, we need to invest to the most profitable project under the 
                 // limitation of w
                 // so what we do is to find all the project available unber current w, and pick
                 // the most profitable project.
                 int project_num = 0;
                 int n = profits.length;
                 List<Integer> chosen_project = new LinkedList<>();
                 int total=w;
                 while(project_num<k){
                     //bind the capital and profits, and sort it in different ways
                     int max_profit=0;
                     int index =-1;
                     for(int i=0;i<n;i++){
                         if(capital[i]<=w&&!chosen_project.contains(i)){
                             if(profits[i]>max_profit){
                                 index = i;
                                 max_profit = profits[i];
                             }
                         }
                     }
                     chosen_project.add(index);
                     total+=max_profit;
                     w+=max_profit;
                     project_num++;
                 }
                 return total;
             }
         }
         ```


2. [373. Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/)

   1. how to priority queue to sort a structure?

      1. ```java
         PriorityQueue<Triple> pq = new PriorityQueue<>((a, b) -> a.value - b.value);
         ```

         1. based on one piece of infomation of Triple to sort all the Triple in the line 
         2. you don't have to include all the Triples in your queue, instead, adding them dynamically.
            1. which is the main difference with List.sort(), which would only sort when you call the fuction, but if you add the element to the priority queue, it will automatically put the element in the right place.


3. [295. Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)

   1. my solution

      1. ```java
         class MedianFinder {
         
             // implement 2 heaps, one is min-heap for the median and bigger numbers
             // another is max_heap for the median and lower
             
             private PriorityQueue<Integer> pq;
             private int count;
         
             public MedianFinder() {
                 pq = new PriorityQueue<>();
                 count=0;
             }
             
             public void addNum(int num) {
                 pq.add(num);
                 count++;
             }
             
             public double findMedian() {
                 PriorityQueue<Integer> temp = new PriorityQueue<>(pq);
                 if(count%2==0){
                     int low_median = count/2-1;
                     int index=0;
                     int value=0;
                     while(index<=low_median){
                         value = temp.poll();
                         index++;
                     }
                     int high = temp.poll();
                     return (double) (value+high) / (double)2.0;
                 }else{
                     int median_index = (count-1) /2;
                     int index=0;
                     int median=0;
                     while(index<=median_index&&!temp.isEmpty()){
                         median = temp.poll();
                         index++;
                     }
                     return (double) median;
                 }
             }
         }
         
         /**
          * Your MedianFinder object will be instantiated and called as such:
          * MedianFinder obj = new MedianFinder();
          * obj.addNum(num);
          * double param_2 = obj.findMedian();
          */
         ```

---

## Appendix: Tips consolidated from `coding-tricks.md`

### Tip #16 — Java PriorityQueue cheatsheet

### 16. priority queue

1. min heap
   1. ` PriorityQueue<Long> minheap = new PriorityQueue<>();`
2. Max heap
   1. ` PriorityQueue<Long> maxheap = new PriorityQueue<>(Collections.reverseOrder());`
3. Add elements 
   1. Offer

4. get first elements
   1. Poll 
5. 
   1. Use lambda expressions to self-define 
      1. ` PriorityQueue<int[]> pq = new PriorityQueue<>((a,b)->Integer.compare(a[0],b[0]));`
      2. `  PriorityQueue<Pair> maxheap = new PriorityQueue<>((Pair a, Pair b) -> Integer.compare(b.value, a.value));`

