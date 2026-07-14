# Greedy — common interview questions

## How it works

Make the **locally optimal choice** at each step and never reconsider it. Fast (usually one pass
or one sort) — but correct **only when the greedy choice is provably part of some global
optimum**. If you can't argue that (usually via an **exchange argument**), fall back to DP.

**Use when:** interval scheduling (earliest finish time), "reach the end / minimum jumps," Huffman
coding, assigning/partitioning where an exchange argument holds.

![Greedy reachability in Jump Game](images/lc-greedy.svg)

**Pseudocode (template):**

```text
function greedy(items):
    sort / order items by the greedy key      # e.g. earliest finish, smallest cost
    answer ← initial
    for item in items:
        if item is compatible with the choices so far:
            take item; update answer           # commit, never undo
    return answer
```

> Proving it: assume an optimal solution differs from the greedy one, then **exchange** the first
> differing choice for the greedy choice without making the solution worse — so a greedy-consistent
> optimum exists.

> **In-site drill:** **Jump Game** (farthest-reachable in one pass) runs in the editor →
> [open it](practice.html?p=jump-game). Below are additional classics.

---

## 1. Gas Station

Find the start index from which you can complete the loop, or `-1`. If total gas ≥ total cost a
solution exists and is **unique**; track a running tank, and whenever it goes negative, no start
in the stretch just covered can work — restart from the next station. **O(n)** time, one pass.

**Example:** `gas = [1,2,3,4,5], cost = [3,4,5,1,2]` → `3`. Total gas (15) equals total cost, so a
start exists; the tank only survives the loop when you begin at station 3.

:::solution
```python
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1                           # not enough fuel overall
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                        # can't reach i+1 from `start`
            start = i + 1                   # every station in [start..i] fails too
            tank = 0
    return start
```
```cpp
#include <vector>
#include <numeric>

int canCompleteCircuit(std::vector<int>& gas, std::vector<int>& cost) {
    int total = 0, tank = 0, start = 0;
    for (int i = 0; i < (int)gas.size(); i++) {
        int diff = gas[i] - cost[i];
        total += diff; tank += diff;
        if (tank < 0) { start = i + 1; tank = 0; }
    }
    return total < 0 ? -1 : start;
}
```
:::

---

## 2. Jump Game II

Minimum jumps to reach the last index (a jump is guaranteed possible). Greedily expand the
current reachable "level": within `[left, right]`, compute the farthest reachable; when you pass
the level's end, increment the jump count and start a new level. **O(n)** time — a BFS-in-disguise.

**Example:** `[2,3,1,1,4]` → `2`. Jump from index 0 to index 1 (value 3), then from index 1
straight to the last index — two jumps.

:::solution
```python
def jump(nums: list[int]) -> int:
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):          # no need to jump from the last index
        farthest = max(farthest, i + nums[i])
        if i == cur_end:                    # exhausted the current jump's range
            jumps += 1
            cur_end = farthest
    return jumps
```
```cpp
#include <vector>
#include <algorithm>

int jump(std::vector<int>& nums) {
    int jumps = 0, curEnd = 0, farthest = 0;
    for (int i = 0; i < (int)nums.size() - 1; i++) {
        farthest = std::max(farthest, i + nums[i]);
        if (i == curEnd) { jumps++; curEnd = farthest; }
    }
    return jumps;
}
```
:::

---

## 3. Merge Intervals

Merge all overlapping intervals. **Sort by start**, then sweep: extend the last merged interval's
end when the next one overlaps, otherwise start a new interval. Sorting exposes the greedy sweep.
**O(n log n)** time.

**Example:** `[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]`. `[1,3]` and `[2,6]`
overlap and merge into `[1,6]`; the other two are disjoint and pass through unchanged.

:::solution
```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)   # overlap → extend
        else:
            merged.append([start, end])
    return merged
```
```cpp
#include <vector>
#include <algorithm>

std::vector<std::vector<int>> merge(std::vector<std::vector<int>>& intervals) {
    std::sort(intervals.begin(), intervals.end());
    std::vector<std::vector<int>> merged;
    for (auto& iv : intervals) {
        if (!merged.empty() && iv[0] <= merged.back()[1])
            merged.back()[1] = std::max(merged.back()[1], iv[1]);
        else
            merged.push_back(iv);
    }
    return merged;
}
```
:::

---

## 4. Non-overlapping Intervals

Minimum intervals to remove so the rest don't overlap. **Sort by end time** and greedily keep
each interval whose start is ≥ the last kept end (classic interval scheduling); remove the rest.
Earliest-finish-first is the provably safe greedy. **O(n log n)** time.

**Example:** `[[1,2],[2,3],[3,4],[1,3]]` → `1`. Keeping `[1,2],[2,3],[3,4]` leaves no overlaps;
only `[1,3]` (which overlaps `[2,3]`) must be removed.

:::solution
```python
def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: x[1])      # earliest finish first
    removed, last_end = 0, float("-inf")
    for start, end in intervals:
        if start >= last_end:               # compatible → keep it
            last_end = end
        else:
            removed += 1                     # overlaps → drop it
    return removed
```
```cpp
#include <vector>
#include <algorithm>
#include <climits>

int eraseOverlapIntervals(std::vector<std::vector<int>>& intervals) {
    std::sort(intervals.begin(), intervals.end(),
              [](const auto& a, const auto& b) { return a[1] < b[1]; });
    int removed = 0; long lastEnd = LONG_MIN;
    for (auto& iv : intervals) {
        if (iv[0] >= lastEnd) lastEnd = iv[1];
        else removed++;
    }
    return removed;
}
```
:::

---

??? How do you justify a greedy algorithm in an interview?
With an **exchange argument**: assume an optimal solution differs from the greedy one, then show
you can swap the first differing choice for the greedy choice **without making the solution
worse** — so a greedy-consistent optimum exists. For interval scheduling, picking the earliest
finish time leaves the most room for later intervals, so any optimal schedule can be rewritten to
start with the greedy pick. If you can't build that argument, the problem probably needs DP.

??? Why sort by *end* for interval scheduling but by *start* for merging?
They optimize different things. **Merging** cares about adjacency along the timeline, so sorting
by **start** lets a single left-to-right sweep coalesce overlaps. **Max non-overlapping
scheduling** wants to free up future capacity as early as possible, so sorting by **end** and
always taking the earliest-finishing compatible interval is the safe greedy — it dominates any
alternative first choice.
