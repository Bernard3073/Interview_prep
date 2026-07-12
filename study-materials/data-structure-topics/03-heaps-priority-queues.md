# Heaps & Priority Queues — always pull the extreme next

> A **priority queue** hands you the smallest (or largest) element next, no matter the insertion
> order. The usual implementation is a **binary heap**: a complete binary tree stored in a plain
> array, with O(log n) insert/remove and O(1) peek.

---

![Min-heap as a tree and its array layout, plus the top-k trick](images/lc-heap.svg)

## The binary heap

A **min-heap** maintains one invariant: every parent is **≤ both children**. That's weaker than a
sorted array — siblings are unordered — which is why it's cheap to maintain, yet it guarantees the
**minimum is always at the root**. The tree is *complete* (filled left to right), so it packs into
an array with no gaps:

```text
node at index i:
    parent(i)      = (i - 1) // 2
    left(i)        = 2*i + 1
    right(i)       = 2*i + 2
```

| Operation | Cost | How |
|---|---|---|
| peek min | O(1) | it's `heap[0]` |
| push | O(log n) | append, then **sift up** while smaller than parent |
| pop min | O(log n) | swap root with last, remove, **sift down** |
| build from n items | **O(n)** | `heapify` — cheaper than n pushes |
| search / arbitrary delete | O(n) | heap is *not* sorted |

```text
push(x):
    heap.append(x)
    i = len(heap) - 1
    while i > 0 and heap[parent(i)] > heap[i]:
        swap(i, parent(i)); i = parent(i)          # sift up

pop():
    swap(0, last); m = heap.pop()                  # remove old root
    i = 0
    while True:                                    # sift down
        s = smallest of (i, left(i), right(i))
        if s == i: break
        swap(i, s); i = s
    return m
```

> **Build is O(n), not O(n log n).** Sifting down from the bottom up, most nodes are shallow, and
> the sum ∑ (height work) telescopes to O(n). Prefer `heapify(list)` over pushing one at a time.

---

## Library types (mind the default direction)

| | Python `heapq` | C++ `std::priority_queue` |
|---|---|---|
| Default | **min**-heap | **max**-heap |
| Push / pop | `heappush`, `heappop` | `push`, `pop` (top = max) |
| Flip direction | push **negated** values, or `(-key, item)` | `priority_queue<int, vector<int>, greater<>>` |
| Build in O(n) | `heapify(list)` | construct from iterators |

Store a **tuple** `(priority, tiebreak, payload)` to sort by a key; make sure the tiebreak is
comparable so Python never tries to compare unorderable payloads.

---

## What heaps are *for*

- **Top-k / k-th largest** — keep a size-k heap: O(n log k) time, O(k) memory (below).
- **Streaming median** — a max-heap of the low half + a min-heap of the high half.
- **Merge k sorted lists / streams** — a heap of the k current heads.
- **Dijkstra / Prim** — always expand the closest frontier node.
- **Scheduling** — run the highest-priority / earliest-deadline task next.

:::solution K-th largest — size-k min-heap, O(n log k)
```python
import heapq

def kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)                 # O(k)
    for x in nums[k:]:
        if x > heap[0]:                 # bigger than the current k-th largest?
            heapq.heapreplace(heap, x)  # pop min, push x — O(log k)
    return heap[0]                      # root = k-th largest
```
```cpp
int kthLargest(vector<int>& nums, int k) {
    priority_queue<int, vector<int>, greater<int>> heap;   // min-heap, size k
    for (int x : nums) {
        heap.push(x);
        if ((int)heap.size() > k) heap.pop();              // drop the smallest
    }
    return heap.top();
}
```
:::

:::solution Streaming median — two heaps
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []    # max-heap (store negatives): smaller half
        self.hi = []    # min-heap: larger half

    def add(self, x):
        heapq.heappush(self.lo, -x)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))    # balance top across
        if len(self.hi) > len(self.lo):                     # keep lo >= hi in size
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```
```cpp
class MedianFinder {
    priority_queue<int> lo;                                  // max-heap: lower half
    priority_queue<int, vector<int>, greater<int>> hi;       // min-heap: upper half
public:
    void add(int x) {
        lo.push(x);
        hi.push(lo.top()); lo.pop();                         // balance across
        if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    double median() {
        if (lo.size() > hi.size()) return lo.top();
        return (lo.top() + hi.top()) / 2.0;
    }
};
```
:::

---

## Interview checklist

1. **"k largest / smallest / closest / most frequent"** → size-k heap, O(n log k).
2. **"Running / streaming median"** → two heaps, balanced by size.
3. **"Merge k sorted …"** → heap of k heads.
4. State the **direction gotcha**: `heapq` is min, `priority_queue` is max — negate to flip.
5. Build from a batch with **`heapify` (O(n))**, not n pushes.

??? Top-k with a heap is O(n log k). When is sorting (O(n log n)) or quickselect (O(n)) better?
Sort when you also need the elements **in order**, or k is close to n. **Quickselect** finds the
k-th element (and partitions around it) in **O(n) average** with O(1) extra space — best when you
want the k-th value or an unordered top-k in one shot and can tolerate O(n²) worst case. The heap
wins for **streaming** (you can't sort data you haven't seen) and small k with bounded memory.

??? Why is `heapify` O(n) when it looks like n sift-downs of O(log n) each?
Sift-down cost is proportional to a node's **height**, and most nodes are near the leaves with tiny
height. Summing height over all nodes, ∑ h · (nodes at height h), telescopes to O(n) — the many
shallow nodes dominate the count, and the few tall ones are rare. Building by repeated **push**
(sift-up) really is O(n log n) because the deep leaves are the majority and sift-up cost grows with
depth.

??? How do you delete or update an arbitrary element in a heap (e.g. Dijkstra's decrease-key)?
A binary heap can't find an arbitrary element in O(log n). Two standard fixes: **lazy deletion** —
push the updated entry and skip stale ones when popped (mark-and-ignore); or keep a **position map**
(value → index) and sift after an in-place change. Interviews almost always accept lazy deletion.
