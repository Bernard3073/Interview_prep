# Heap / Top-K — common interview questions

## How it works

A **heap (priority queue)** gives `O(log n)` push/pop of the min (or max) and `O(1)` peek. Use it
for **top-k**, **merge k sorted lists**, **running median** (two heaps), and Dijkstra/Prim. In
Python, `heapq` is a **min-heap** — push negatives (or tuples) for max-heap behavior; in C++,
`std::priority_queue` is a **max-heap** by default.

**Use when:** "k largest / smallest", "median of a stream", "k closest", or "always pull the
current best/worst".

![Min-heap as tree and array, plus the top-k trick](images/lc-heap.svg)

**Pseudocode (top-k with a heap):**

```text
function topK(items, k):
    heap ← empty min-heap
    for x in items:
        heap.push(x)
        if heap.size > k:
            heap.pop()            # drop the smallest → heap keeps the k largest
    return heap                   # O(n log k) time, O(k) space
```

> **In-site drill:** **Top K Frequent Elements** runs in the editor →
> [open it](practice.html?p=top-k-frequent). Below are additional classics.

---

## 1. Kth Largest Element in an Array (heap)

Keep a **size-k min-heap**: push each value, pop the smallest whenever the heap exceeds `k`. The
heap's root is then the k-th largest. **O(n log k)** time, **O(k)** space — cheaper than sorting
when `k ≪ n`.

**Example:** `nums = [3,2,1,5,6,4], k = 2` → `5`. The size-2 heap ends holding the two largest,
`{5,6}`, and its root (the smaller of them) `5` is the 2nd largest.

:::solution
```python
import heapq

def find_kth_largest(nums: list[int], k: int) -> int:
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)            # drop the smallest → keep k largest
    return heap[0]                          # root = k-th largest
```
```cpp
#include <vector>
#include <queue>

int findKthLargest(std::vector<int>& nums, int k) {
    std::priority_queue<int, std::vector<int>, std::greater<int>> heap;  // min-heap
    for (int x : nums) {
        heap.push(x);
        if ((int)heap.size() > k) heap.pop();
    }
    return heap.top();
}
```
:::

---

## 2. K Closest Points to Origin

Return the `k` points nearest the origin. Same size-k heap idea, ordered by squared distance
(no `sqrt` needed) — but as a **max-heap** so the farthest of the current best-k sits on top and
gets evicted. **O(n log k)** time.

**Example:** `points = [[1,3],[-2,2]], k = 1` → `[[-2,2]]`. Distances² are `1²+3²=10` and
`(-2)²+2²=8`; `[-2,2]` is closer, so it's the single closest point.

:::solution
```python
import heapq

def k_closest(points: list[list[int]], k: int) -> list[list[int]]:
    heap = []                              # max-heap via negated distance
    for x, y in points:
        d = x * x + y * y
        heapq.heappush(heap, (-d, x, y))
        if len(heap) > k:
            heapq.heappop(heap)            # evict the farthest
    return [[x, y] for _, x, y in heap]
```
```cpp
#include <vector>
#include <queue>

std::vector<std::vector<int>> kClosest(std::vector<std::vector<int>>& points, int k) {
    std::priority_queue<std::pair<int, int>> heap;   // max-heap keyed by distance, value = index
    for (int i = 0; i < (int)points.size(); i++) {
        int d = points[i][0]*points[i][0] + points[i][1]*points[i][1];
        heap.push({d, i});
        if ((int)heap.size() > k) heap.pop();         // evict farthest
    }
    std::vector<std::vector<int>> res;
    while (!heap.empty()) { res.push_back(points[heap.top().second]); heap.pop(); }
    return res;
}
```
:::

---

## 3. Find Median from Data Stream

Maintain **two heaps**: a max-heap `lo` for the smaller half and a min-heap `hi` for the larger
half, kept balanced in size. The median is `lo`'s top (odd total) or the average of both tops
(even). Each `addNum` is `O(log n)`; `findMedian` is `O(1)`.

**Example:** `addNum(1), addNum(2)` then `findMedian()` → `1.5` (average of the two tops);
`addNum(3)` then `findMedian()` → `2` (odd count, `lo`'s top).

:::solution
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []                       # max-heap (negated) for the smaller half
        self.hi = []                       # min-heap for the larger half

    def addNum(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # move largest of lo to hi
        if len(self.hi) > len(self.lo):                     # rebalance so len(lo) >= len(hi)
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```
```cpp
#include <queue>

class MedianFinder {
    std::priority_queue<int> lo;                                   // max-heap, smaller half
    std::priority_queue<int, std::vector<int>, std::greater<int>> hi;  // min-heap, larger half
public:
    void addNum(int num) {
        lo.push(num);
        hi.push(lo.top()); lo.pop();               // shift largest of lo to hi
        if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    double findMedian() {
        if (lo.size() > hi.size()) return lo.top();
        return (lo.top() + hi.top()) / 2.0;
    }
};
```
:::

---

??? Why does a size-k heap beat sorting for "k largest"?
Sorting is `O(n log n)`; a size-k heap is `O(n log k)`. When `k` is small relative to `n`, `log k
≪ log n`, so you do far less work — and you only hold `k` elements in memory, which matters for
**streams** where you can't store all `n`. You keep the k best seen so far and evict the worst of
them as better ones arrive.

??? For the median stream, why two heaps instead of one sorted structure?
Insertion into a sorted array is `O(n)` per element. Two heaps give `O(log n)` insertion while
keeping the boundary between the halves `O(1)` to read: the max-heap's top is the largest of the
low half, the min-heap's top the smallest of the high half. Keep their sizes within one of each
other and the median is always one or two tops away.
