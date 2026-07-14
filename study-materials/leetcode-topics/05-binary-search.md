# Binary Search — common interview questions

## How it works

Halve the search space each step → **O(log n)**. Beyond "find x in a sorted array," the real
power is **binary search on the answer**: if you can cheaply test "is a candidate answer
feasible?" and feasibility is **monotonic**, binary-search the smallest/largest feasible value.
Get the `[lo, hi)` invariant and the `<` vs `<=` right and off-by-ones disappear.

**Use when:** anything "sorted" + search, "minimize the max / maximize the min", "smallest value
such that …", or a rotated / 2-D sorted structure.

![Binary search halving the range each step](images/lc-binary-search.svg)

**Pseudocode (template):**

```text
function binarySearch(lo, hi):            # a sorted index range, or an answer range
    while lo < hi:
        mid ← lo + (hi − lo) / 2          # floor; avoids overflow
        if feasible(mid):                 # predicate must be monotonic
            hi ← mid                      # keep mid, search the left half
        else:
            lo ← mid + 1                  # discard mid and everything left
    return lo                             # smallest feasible value
```

```python
# Smallest index where a[i] >= target (lower_bound). Get the half-open invariant right.
def lower_bound(a, target):
    lo, hi = 0, len(a)               # search range [lo, hi)
    while lo < hi:
        mid = (lo + hi) // 2          # // is floor; no overflow worries in Python
        if a[mid] < target: lo = mid + 1
        else:               hi = mid
    return lo                         # in [0, len(a)]
```

**Search-on-answer pattern:** "minimum capacity to ship in D days," "smallest divisor," "split
array largest sum." Write `feasible(x)`, then binary-search x. The monotonicity (`feasible` flips
false→true exactly once) is what licenses it.

> **In-site drill:** **Search in Rotated Sorted Array** runs in the editor →
> [open it](practice.html?p=search-in-rotated-sorted-array). Below are additional classics
> including the search-on-answer pattern.

---

## 1. Koko Eating Bananas

Smallest eating speed `k` so Koko finishes all piles within `h` hours. **Search on the answer:**
`feasible(k)` = `sum(ceil(pile / k)) ≤ h`, which is monotonic in `k`. Binary-search the smallest
feasible `k` in `[1, max(piles)]`. **O(n log max)** time.

**Example:** `piles = [3,6,7,11], h = 8` → `4`. At speed 4 the hours are
`ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4) = 1+2+2+3 = 8 ≤ 8`; speed 3 needs 9 hours, so 4 is the
smallest that fits.

:::solution
```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    def hours(k):                     # hours needed at speed k
        return sum(math.ceil(p / k) for p in piles)
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= h:           # feasible → try slower
            hi = mid
        else:
            lo = mid + 1
    return lo
```
```cpp
#include <vector>
#include <algorithm>

int minEatingSpeed(std::vector<int>& piles, int h) {
    auto hours = [&](long long k) {
        long long t = 0;
        for (int p : piles) t += (p + k - 1) / k;   // ceil(p/k)
        return t;
    };
    int lo = 1, hi = *std::max_element(piles.begin(), piles.end());
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (hours(mid) <= h) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}
```
:::

---

## 2. Find Minimum in Rotated Sorted Array

A sorted array rotated at an unknown pivot; find the minimum in `O(log n)`. Compare `mid` to the
right end: if `nums[mid] > nums[hi]` the minimum lies to the **right** of `mid`; otherwise it's at
`mid` or to its left. Converges on the pivot.

**Example:** `[4,5,6,7,0,1,2]` → `0`. `mid = 7 > nums[hi] = 2`, so the minimum is to the right;
the search narrows onto the pivot value `0`.

:::solution
```python
def find_min(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:      # min must be to the right of mid
            lo = mid + 1
        else:                          # min is mid or to its left
            hi = mid
    return nums[lo]
```
```cpp
#include <vector>

int findMin(std::vector<int>& nums) {
    int lo = 0, hi = (int)nums.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```
:::

---

## 3. Find First and Last Position of Element in Sorted Array

Return the start and end indices of `target`. Two binary searches: `lower_bound` (first index
`≥ target`) and `upper_bound` (first index `> target`). If the target is absent, return
`[-1, -1]`. **O(log n)** time.

**Example:** `nums = [5,7,7,8,8,10], target = 8` → `[3,4]` (the two 8s sit at indices 3 and 4).
`target = 6` → `[-1,-1]` since 6 is absent.

:::solution
```python
from bisect import bisect_left, bisect_right

def search_range(nums: list[int], target: int) -> list[int]:
    lo = bisect_left(nums, target)
    if lo == len(nums) or nums[lo] != target:
        return [-1, -1]
    hi = bisect_right(nums, target) - 1
    return [lo, hi]
```
```cpp
#include <vector>

std::vector<int> searchRange(std::vector<int>& nums, int target) {
    auto lower = [&](int t) {
        int lo = 0, hi = nums.size();
        while (lo < hi) { int m = lo + (hi - lo) / 2; if (nums[m] < t) lo = m + 1; else hi = m; }
        return lo;
    };
    int lo = lower(target);
    if (lo == (int)nums.size() || nums[lo] != target) return {-1, -1};
    int hi = lower(target + 1) - 1;
    return {lo, hi};
}
```
:::

---

## 4. Search a 2D Matrix

Rows sorted, and each row's first element exceeds the previous row's last — so the matrix reads
as one sorted list of length `m·n`. Binary-search that virtual array, mapping index `k` to
`(k / n, k % n)`. **O(log(m·n))** time.

**Example:** `matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3` → `true`. Treated as
the flat sorted list `[1,3,5,7,10,…,60]`, index 1 holds `3`; `target = 13` → `false`.

:::solution
```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // n][mid % n]     # treat as a flat sorted array
        if val == target:  return True
        elif val < target: lo = mid + 1
        else:              hi = mid - 1
    return False
```
```cpp
#include <vector>

bool searchMatrix(std::vector<std::vector<int>>& matrix, int target) {
    int m = matrix.size(), n = matrix[0].size();
    int lo = 0, hi = m * n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        int val = matrix[mid / n][mid % n];
        if (val == target) return true;
        else if (val < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return false;
}
```
:::

---

??? What makes "binary search on the answer" valid?
A **monotonic predicate**. If `feasible(x)` is false for all small `x` and true for all large
`x` (or vice-versa), there's a single false→true boundary, and binary search finds it. You never
touch the input in sorted order — you search the *answer range* and call `feasible` at each
midpoint. The whole trick is proving feasibility flips exactly once; without that, binary search
is unsound.

??? Why prefer the half-open `[lo, hi)` invariant?
It removes the two most common bugs: the `mid + 1` / `mid` update is uniform (`lo = mid + 1` when
rejecting, `hi = mid` when keeping), the loop condition is simply `lo < hi`, and the loop can
return the boundary `lo` in `[0, n]` — including "insert at the end". Mixing `<=` with `hi = mid`
is where infinite loops and off-by-ones creep in.
