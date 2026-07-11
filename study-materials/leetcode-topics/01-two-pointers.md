# Two Pointers — common interview questions

## How it works

Two indices walking an array — **toward each other** (pair problems on **sorted** data) or in
the **same direction** (fast/slow, in-place writes). Turns many `O(n²)` scans into `O(n)` with
`O(1)` extra space.

**Use when:** sorted array, pair/triple sums, palindrome checks, removing duplicates,
partitioning, or merging two sorted sequences.

![Two pointers converging on a sorted array](images/lc-two-pointers.svg)

**Pseudocode (template):**

```text
function twoPointers(a):              # a is sorted
    i ← 0;  j ← length(a) − 1
    while i < j:
        if condition(a[i], a[j]) holds:
            record / return (i, j)
            i ← i + 1;  j ← j − 1      # move both inward
        else if need a larger value:
            i ← i + 1                 # advance the small end
        else:                          # need a smaller value
            j ← j − 1                 # retreat the big end
```

```python
# Pair that sums to target in a SORTED array — O(n) time, O(1) space
def two_sum_sorted(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:   return (i, j)
        elif s < target:  i += 1      # need bigger → move left pointer up
        else:             j -= 1      # need smaller → move right pointer down
    return None
```

The **fast/slow** variant (in-place compaction, cycle detection in a linked list) keeps a
`write` pointer behind a `read` pointer. Cycle detection (Floyd's) advances slow by 1, fast by
2; they meet iff there's a cycle.

> **In-site drill:** the canonical two-pointer problem, **3Sum**, is solvable in the editor →
> [open it](practice.html?p=3sum). The questions below are *additional* high-frequency ones
> with full Python/C++ solutions.

---

## 1. Valid Palindrome

Two pointers from both ends walk inward, skipping non-alphanumeric characters and comparing
case-insensitively. **O(n)** time, **O(1)** space.

**Key idea:** don't build a cleaned copy of the string — filter on the fly so space stays
constant.

:::solution
```python
def is_palindrome(s: str) -> bool:
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and not s[i].isalnum(): i += 1   # skip junk from the left
        while i < j and not s[j].isalnum(): j -= 1   # skip junk from the right
        if s[i].lower() != s[j].lower():
            return False
        i += 1; j -= 1
    return True
```
```cpp
#include <cctype>
#include <string>

bool isPalindrome(const std::string& s) {
    int i = 0, j = (int)s.size() - 1;
    while (i < j) {
        while (i < j && !std::isalnum((unsigned char)s[i])) i++;
        while (i < j && !std::isalnum((unsigned char)s[j])) j--;
        if (std::tolower((unsigned char)s[i]) != std::tolower((unsigned char)s[j]))
            return false;
        i++; j--;
    }
    return true;
}
```
:::

---

## 2. Container With Most Water

Height array; pick two lines forming a container with the most water. Start pointers at both
ends; the area is `min(h[i], h[j]) * (j - i)`. **Always move the shorter wall inward** — the
taller one can only ever be limited by a shorter partner, so moving it can't improve the area.
**O(n)** time, **O(1)** space.

:::solution
```python
def max_area(height: list[int]) -> int:
    i, j, best = 0, len(height) - 1, 0
    while i < j:
        best = max(best, min(height[i], height[j]) * (j - i))
        if height[i] < height[j]:   # move the limiting (shorter) wall
            i += 1
        else:
            j -= 1
    return best
```
```cpp
#include <vector>
#include <algorithm>

int maxArea(std::vector<int>& height) {
    int i = 0, j = (int)height.size() - 1, best = 0;
    while (i < j) {
        best = std::max(best, std::min(height[i], height[j]) * (j - i));
        if (height[i] < height[j]) i++;   // move the shorter wall
        else j--;
    }
    return best;
}
```
:::

---

## 3. Two Sum II — Input Array Is Sorted

Return the 1-indexed pair that sums to `target`. Because the array is **sorted**, converging
pointers give `O(n)`/`O(1)` — no hash map needed. If the sum is too small, advance the left
pointer (need a bigger value); too big, retreat the right.

:::solution
```python
def two_sum(numbers: list[int], target: int) -> list[int]:
    i, j = 0, len(numbers) - 1
    while i < j:
        s = numbers[i] + numbers[j]
        if s == target:   return [i + 1, j + 1]   # problem uses 1-based indices
        elif s < target:  i += 1
        else:             j -= 1
    return []
```
```cpp
#include <vector>

std::vector<int> twoSum(std::vector<int>& numbers, int target) {
    int i = 0, j = (int)numbers.size() - 1;
    while (i < j) {
        int s = numbers[i] + numbers[j];
        if (s == target) return {i + 1, j + 1};
        else if (s < target) i++;
        else j--;
    }
    return {};
}
```
:::

---

## 4. Move Zeroes

Move all zeros to the end in place, keeping the relative order of non-zeros. A **fast/slow**
pair: `write` marks where the next non-zero goes; `read` scans. Swap on each non-zero.
**O(n)** time, **O(1)** space.

:::solution
```python
def move_zeroes(nums: list[int]) -> None:
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
```
```cpp
#include <vector>
#include <utility>

void moveZeroes(std::vector<int>& nums) {
    int write = 0;
    for (int read = 0; read < (int)nums.size(); read++) {
        if (nums[read] != 0)
            std::swap(nums[write++], nums[read]);
    }
}
```
:::

---

??? Why do you move the *shorter* wall in Container With Most Water?
The area is bounded by the **shorter** of the two walls times the width. If you moved the
taller wall inward, the width shrinks and the height is still capped by the (unchanged) shorter
wall — the area can only stay the same or drop. Moving the shorter wall is the only move that
gives a chance at a taller limiting wall, so it's the only move that can improve the answer.
That's why the greedy two-pointer sweep is provably optimal in one pass.

??? When do two pointers beat a hash map?
When the input is **sorted** (or cheap to sort) and you want `O(1)` extra space, or you need
pairs/triples defined by an order relation (closest sum, 3Sum, container area). A hash map wins
when the input is **unsorted**, you must return **original indices**, or membership/counting is
the real question. Rule of thumb: sorted + space-tight → two pointers; unsorted + index-reporting
→ hash map.
