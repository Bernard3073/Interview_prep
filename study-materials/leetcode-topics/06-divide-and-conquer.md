# Divide & Conquer — common interview questions

## How it works

Split into **independent** subproblems, solve recursively, then **combine** — the merge step
does the real work. Cost follows the Master theorem `T(n) = a·T(n/b) + O(combine)`.

**Use when:** merge sort / quickselect, "count while you merge" (inversions), maximum subarray by
halves, building balanced trees, closest pair of points.

![Merge sort: split down, merge up](images/lc-divide-conquer.svg)

**Pseudocode (template):**

```text
function solve(problem):
    if problem is small: return baseCase(problem)
    parts   ← split(problem)               # divide
    results ← [ solve(p) for p in parts ]  # conquer
    return combine(results)                # the merge step does the real work
```

```python
def merge_sort(a):
    if len(a) <= 1: return a
    mid = len(a) // 2
    L, R = merge_sort(a[:mid]), merge_sort(a[mid:])   # divide + conquer
    out, i, j = [], 0, 0                                # combine: merge two sorted halves
    while i < len(L) and j < len(R):
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else:            out.append(R[j]); j += 1
    out.extend(L[i:]); out.extend(R[j:])
    return out                                          # O(n log n), stable
```

**Quickselect** (kth-smallest in average O(n)) is divide-and-conquer that recurses into *only
one* side. The line between D&C and DP: D&C subproblems **don't overlap**; when they *do*, you
memoize and it becomes DP.

> **In-site drill:** **Merge k Sorted Lists** runs in the editor →
> [open it](practice.html?p=merge-k-sorted-lists). Below are additional classics.

---

## 1. Sort an Array (merge sort)

Sort in guaranteed `O(n log n)` with a stable merge sort: split in half, sort each half, merge.
The merge walks two sorted halves with two pointers.

**Example:** `[5,2,3,1]` → `[1,2,3,5]`. Split into `[5,2]` and `[3,1]`, sort each to `[2,5]` and
`[1,3]`, then merge the two sorted halves into `[1,2,3,5]`.

:::solution
```python
def sort_array(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = sort_array(nums[:mid])
    right = sort_array(nums[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:            # <= keeps it stable
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:]); merged.extend(right[j:])
    return merged
```
```cpp
#include <vector>

std::vector<int> sortArray(std::vector<int>& nums) {
    if (nums.size() <= 1) return nums;
    int mid = nums.size() / 2;
    std::vector<int> left(nums.begin(), nums.begin() + mid);
    std::vector<int> right(nums.begin() + mid, nums.end());
    left = sortArray(left); right = sortArray(right);
    std::vector<int> merged;
    int i = 0, j = 0;
    while (i < (int)left.size() && j < (int)right.size()) {
        if (left[i] <= right[j]) merged.push_back(left[i++]);
        else merged.push_back(right[j++]);
    }
    while (i < (int)left.size()) merged.push_back(left[i++]);
    while (j < (int)right.size()) merged.push_back(right[j++]);
    return merged;
}
```
:::

---

## 2. Kth Largest Element in an Array (quickselect)

The average-`O(n)` cousin of quicksort: partition around a pivot, then recurse into **only the
side** that contains the k-th largest. Worst case `O(n²)`, avoided in practice with a random
pivot.

**Example:** `nums = [3,2,1,5,6,4], k = 2` → `5`. The 2nd largest equals the element that lands
at sorted index `6 − 2 = 4`; quickselect partitions until that slot holds `5`.

:::solution
```python
import random

def find_kth_largest(nums: list[int], k: int) -> int:
    target = len(nums) - k                 # k-th largest = target-th smallest (0-based)
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        p = partition(nums, lo, hi)
        if   p == target: return nums[p]
        elif p < target:  lo = p + 1       # recurse right only
        else:             hi = p - 1       # recurse left only
    return -1

def partition(a, lo, hi):
    i = random.randint(lo, hi)
    a[i], a[hi] = a[hi], a[i]              # random pivot to the end
    pivot, store = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[store], a[j] = a[j], a[store]; store += 1
    a[store], a[hi] = a[hi], a[store]
    return store
```
```cpp
#include <vector>
#include <cstdlib>
#include <utility>

int partition(std::vector<int>& a, int lo, int hi) {
    int i = lo + rand() % (hi - lo + 1);
    std::swap(a[i], a[hi]);
    int pivot = a[hi], store = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] < pivot) std::swap(a[store++], a[j]);
    std::swap(a[store], a[hi]);
    return store;
}
int findKthLargest(std::vector<int>& nums, int k) {
    int target = (int)nums.size() - k, lo = 0, hi = nums.size() - 1;
    while (lo <= hi) {
        int p = partition(nums, lo, hi);
        if (p == target) return nums[p];
        else if (p < target) lo = p + 1;
        else hi = p - 1;
    }
    return -1;
}
```
:::

---

## 3. Count of Smaller Numbers After Self

For each element, how many elements to its right are smaller. Do it **while merge-sorting**
indices: when the right half contributes an element before a left-half element, every element
already merged from the right is smaller than that left element — accumulate those counts.
**O(n log n)** time.

**Example:** `[5,2,6,1]` → `[2,1,1,0]`. To the right of `5` are `2,1` (2 smaller); right of `2`
is `1` (1 smaller); right of `6` is `1` (1 smaller); right of `1` there is nothing (0).

:::solution
```python
def count_smaller(nums: list[int]) -> list[int]:
    counts = [0] * len(nums)
    idx = list(range(len(nums)))            # sort indices, not values

    def sort(lo, hi):
        if hi - lo <= 1: return
        mid = (lo + hi) // 2
        sort(lo, mid); sort(mid, hi)
        merged, i, j, right_smaller = [], lo, mid, 0
        while i < mid and j < hi:
            if nums[idx[j]] < nums[idx[i]]:
                right_smaller += 1          # this right element is smaller
                merged.append(idx[j]); j += 1
            else:
                counts[idx[i]] += right_smaller
                merged.append(idx[i]); i += 1
        while i < mid:
            counts[idx[i]] += right_smaller
            merged.append(idx[i]); i += 1
        while j < hi:
            merged.append(idx[j]); j += 1
        idx[lo:hi] = merged

    sort(0, len(nums))
    return counts
```
```cpp
#include <vector>

void sortCount(std::vector<int>& nums, std::vector<int>& idx,
               std::vector<int>& counts, int lo, int hi) {
    if (hi - lo <= 1) return;
    int mid = (lo + hi) / 2;
    sortCount(nums, idx, counts, lo, mid);
    sortCount(nums, idx, counts, mid, hi);
    std::vector<int> merged;
    int i = lo, j = mid, rightSmaller = 0;
    while (i < mid && j < hi) {
        if (nums[idx[j]] < nums[idx[i]]) { rightSmaller++; merged.push_back(idx[j++]); }
        else { counts[idx[i]] += rightSmaller; merged.push_back(idx[i++]); }
    }
    while (i < mid) { counts[idx[i]] += rightSmaller; merged.push_back(idx[i++]); }
    while (j < hi) merged.push_back(idx[j++]);
    for (int k = 0; k < (int)merged.size(); k++) idx[lo + k] = merged[k];
}
std::vector<int> countSmaller(std::vector<int>& nums) {
    int n = nums.size();
    std::vector<int> counts(n, 0), idx(n);
    for (int i = 0; i < n; i++) idx[i] = i;
    sortCount(nums, idx, counts, 0, n);
    return counts;
}
```
:::

---

??? Divide-and-conquer vs. dynamic programming — the litmus test?
Draw the recursion tree. If the same subproblem (same arguments) appears in **multiple**
branches, the subproblems **overlap** → memoize/tabulate → it's DP. If each subproblem is solved
**once** and the branches are independent (merge sort's two halves), it's plain divide and
conquer — no cache needed.

??? Why does quickselect average O(n) while quicksort is O(n log n)?
Quicksort recurses into **both** partitions; quickselect recurses into **one**. With a balanced
split the work is `n + n/2 + n/4 + … = O(n)` (a geometric series), versus quicksort's `O(n)` per
level across `log n` levels. A random (or median-of-medians) pivot keeps the split balanced in
expectation, avoiding the `O(n²)` worst case.
