# Sliding Window — common interview questions

## How it works

A two-pointer specialization for **contiguous** subarrays/substrings. Grow the window from the
right; when it violates a constraint, shrink from the left. Each element enters and leaves at
most once → **O(n)**. Keep a little window state (a count, a frequency map, a running sum) so
the validity check is `O(1)`.

**Use when:** "longest/shortest/at-most-k subarray," moving averages over a stream, "smallest
window containing …".

![Sliding window growing right and shrinking left](images/lc-sliding-window.svg)

**Pseudocode (template):**

```text
function slidingWindow(seq):
    left ← 0
    for right in 0 … length(seq) − 1:
        add seq[right] to the window
        while window is invalid:          # constraint broken
            remove seq[left] from window
            left ← left + 1
        update answer with (right − left + 1)
    return answer
```

```python
# Longest substring without repeating characters — O(n)
def longest_unique(s):
    seen = {}            # char -> last index
    left = best = 0
    for right, c in enumerate(s):
        if c in seen and seen[c] >= left:
            left = seen[c] + 1        # jump left past the previous occurrence
        seen[c] = right
        best = max(best, right - left + 1)
    return best
```

For **fixed-size** windows (moving average, sliding-window max), add the entering element and
pop the leaving one — a deque gives O(1) amortized max/min over the window.

> **In-site drill:** the canonical variable window, **Longest Substring Without Repeating
> Characters**, runs in the editor → [open it](practice.html?p=longest-substring-no-repeat).
> Below are additional high-frequency windows.

---

## 1. Minimum Window Substring

Smallest substring of `s` containing every character of `t` (with multiplicity). Expand right to
satisfy the requirement, then contract left while it stays satisfied, recording the best.
`have`/`need` counters track how many distinct chars are fully covered so the check is `O(1)`.
**O(|s| + |t|)** time.

**Example:** `s = "ADOBECODEBANC", t = "ABC"` → `"BANC"`. The window first covers `t` at
`"ADOBEC"`, then keeps shrinking/sliding to smaller covering windows until `"BANC"` (length 4)
proves smallest.

:::solution
```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s: return ""
    need = Counter(t)
    missing = len(t)                 # total chars still to cover (with multiplicity)
    left = start = 0
    best = (float("inf"), 0)         # (length, left)
    for right, c in enumerate(s):
        if need[c] > 0: missing -= 1
        need[c] -= 1
        while missing == 0:          # window covers t → try to shrink
            if right - left + 1 < best[0]:
                best = (right - left + 1, left)
            need[s[left]] += 1
            if need[s[left]] > 0: missing += 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]:best[1] + best[0]]
```
```cpp
#include <string>
#include <unordered_map>
#include <climits>

std::string minWindow(std::string s, std::string t) {
    if (t.empty() || s.empty()) return "";
    std::unordered_map<char, int> need;
    for (char c : t) need[c]++;
    int missing = (int)t.size(), left = 0, bestLen = INT_MAX, bestL = 0;
    for (int right = 0; right < (int)s.size(); right++) {
        if (need[s[right]] > 0) missing--;
        need[s[right]]--;
        while (missing == 0) {
            if (right - left + 1 < bestLen) { bestLen = right - left + 1; bestL = left; }
            need[s[left]]++;
            if (need[s[left]] > 0) missing++;
            left++;
        }
    }
    return bestLen == INT_MAX ? "" : s.substr(bestL, bestLen);
}
```
:::

---

## 2. Longest Repeating Character Replacement

Longest substring you can make all-identical by replacing at most `k` characters. A window is
valid when `(window length − count of its most frequent char) ≤ k`. Track `maxFreq`; when the
window turns invalid, slide left by one. **O(n)** time, **O(26)** space.

**Example:** `s = "AABABBA", k = 1` → `4`. The window `"AABA"` has 3 `A`s and one `B`; replacing
that single `B` (within the budget `k=1`) makes four identical characters.

:::solution
```python
from collections import defaultdict

def character_replacement(s: str, k: int) -> int:
    count = defaultdict(int)
    left = max_freq = best = 0
    for right, c in enumerate(s):
        count[c] += 1
        max_freq = max(max_freq, count[c])
        if (right - left + 1) - max_freq > k:   # too many chars to replace
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```
```cpp
#include <string>
#include <algorithm>

int characterReplacement(std::string s, int k) {
    int count[26] = {0};
    int left = 0, maxFreq = 0, best = 0;
    for (int right = 0; right < (int)s.size(); right++) {
        maxFreq = std::max(maxFreq, ++count[s[right] - 'A']);
        if ((right - left + 1) - maxFreq > k)
            count[s[left++] - 'A']--;
        best = std::max(best, right - left + 1);
    }
    return best;
}
```
:::

---

## 3. Permutation in String

Does `s2` contain a permutation of `s1` as a substring? Slide a **fixed-size** window of length
`|s1|` over `s2` and compare frequency vectors. Maintain a `matches` counter over 26 letters so
each step is `O(1)`. **O(|s2|)** time.

**Example:** `s1 = "ab", s2 = "eidbaooo"` → `true`. The length-2 window reaches `"ba"`, whose
letter counts match `"ab"` — a permutation is present. `s1 = "ab", s2 = "eidboaoo"` → `false`.

:::solution
```python
def check_inclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2): return False
    need = [0] * 26
    win = [0] * 26
    for c in s1: need[ord(c) - 97] += 1
    for i, c in enumerate(s2):
        win[ord(c) - 97] += 1
        if i >= len(s1):                       # drop the char leaving the window
            win[ord(s2[i - len(s1)]) - 97] -= 1
        if win == need:
            return True
    return False
```
```cpp
#include <string>
#include <array>

bool checkInclusion(std::string s1, std::string s2) {
    if (s1.size() > s2.size()) return false;
    std::array<int, 26> need{}, win{};
    for (char c : s1) need[c - 'a']++;
    for (int i = 0; i < (int)s2.size(); i++) {
        win[s2[i] - 'a']++;
        if (i >= (int)s1.size()) win[s2[i - s1.size()] - 'a']--;
        if (win == need) return true;
    }
    return false;
}
```
:::

---

## 4. Max Consecutive Ones III

Longest run of 1s after flipping at most `k` zeros. A window is valid while it contains `≤ k`
zeros; grow right, and when the zero count exceeds `k`, move left past one zero. **O(n)** time.

**Example:** `nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2` → `6`. Flipping the two zeros at indices 3
and 4 joins `[1,1,1,0,0,1,1,1,1]`'s middle into a run of six consecutive 1s.

:::solution
```python
def longest_ones(nums: list[int], k: int) -> int:
    left = zeros = best = 0
    for right, x in enumerate(nums):
        if x == 0: zeros += 1
        while zeros > k:                # too many flips used → shrink
            if nums[left] == 0: zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```
```cpp
#include <vector>
#include <algorithm>

int longestOnes(std::vector<int>& nums, int k) {
    int left = 0, zeros = 0, best = 0;
    for (int right = 0; right < (int)nums.size(); right++) {
        if (nums[right] == 0) zeros++;
        while (zeros > k) {
            if (nums[left] == 0) zeros--;
            left++;
        }
        best = std::max(best, right - left + 1);
    }
    return best;
}
```
:::

---

??? Fixed-size vs. variable-size sliding window — how do you tell them apart?
If the problem fixes the window length (e.g. "permutation of s1", "moving average of size k"),
use a **fixed** window: add the entering element and remove the leaving one each step. If the
window length is the thing you're optimizing ("longest/shortest subarray with property P"), use
a **variable** window: grow right unconditionally, and shrink left only while the constraint is
violated (or while it stays satisfied, for "smallest" problems).

??? Why is the total work O(n) even with a nested while-loop?
Because `left` only ever moves **forward**, never resets. Across the whole scan `right` advances
`n` times and `left` advances at most `n` times, so the inner loop runs `O(n)` times *in total*,
not per outer step. It's an amortized argument — each element enters the window once and leaves
at most once.
