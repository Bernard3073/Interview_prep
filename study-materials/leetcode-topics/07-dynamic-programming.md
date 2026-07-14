# Dynamic Programming — common interview questions

## How it works

When subproblems **overlap** and the problem has **optimal substructure** (the optimum is built
from optima of subproblems), cache results. Two equivalent styles:

- **Top-down (memoization):** recursion + a cache. Easiest to derive — write the brute-force
  recurrence, then `@lru_cache` it.
- **Bottom-up (tabulation):** fill a table in dependency order. Lets you shrink memory (often to
  O(1) rows).

**Use when:** "max / min / count the ways / can you reach", with choices that reuse overlapping
sub-answers.

![Coin change DP table and the transition into the last cell](images/lc-dp-table.svg)

**Pseudocode (template, bottom-up):**

```text
define dp[state] = answer to the subproblem `state`
set base cases
for state in dependency order:
    dp[state] ← aggregate over choices:        # min / max / count / OR
        combine( dp[smaller_state], cost(choice) )
return dp[target]
```

```python
# Coin change: fewest coins to make `amount` — classic 1-D DP, O(amount * #coins)
def coin_change(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount         # dp[x] = fewest coins to make x
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                dp[x] = min(dp[x], dp[x - c] + 1)
    return dp[amount] if dp[amount] != INF else -1
```

**How to derive any DP:** (1) define the state (what does `dp[i]` *mean*?), (2) write the
transition (how does it build from smaller states?), (3) set base cases, (4) decide the fill
order. Common families: 1-D sequences (house robber, climbing stairs), **Kadane's** (max subarray
— running best ending here), 2-D grids (edit distance, LCS, **maximal square**), knapsack (subset
sum), and intervals (matrix-chain, burst balloons).

> **In-site drill:** the canonical unbounded-knapsack DP, **Coin Change**, runs in the editor →
> [open it](practice.html?p=coin-change). Below are additional classics spanning 1-D,
> subsequence, grid, and string DP.

---

## 1. House Robber

Max sum of non-adjacent houses. State: `dp[i]` = best loot considering houses `0..i`. Transition:
`dp[i] = max(dp[i-1], dp[i-2] + nums[i])` — skip house `i`, or rob it and add `dp[i-2]`. Only the
last two values matter, so it's `O(1)` space.

**Example:** `[2,7,9,3,1]` → `12`. Robbing houses `2 + 9 + 1` (non-adjacent) beats the
alternative `7 + 3 = 10`.

:::solution
```python
def rob(nums: list[int]) -> int:
    prev2, prev1 = 0, 0                    # best up to i-2 and i-1
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
```
```cpp
#include <vector>
#include <algorithm>

int rob(std::vector<int>& nums) {
    int prev2 = 0, prev1 = 0;
    for (int x : nums) {
        int cur = std::max(prev1, prev2 + x);
        prev2 = prev1; prev1 = cur;
    }
    return prev1;
}
```
:::

---

## 2. Longest Increasing Subsequence

Length of the longest strictly increasing subsequence. The `O(n log n)` method keeps `tails[k]` =
the smallest possible tail of an increasing subsequence of length `k+1`; binary-search where each
value extends or replaces a tail. The array's length is the answer.

**Example:** `[10,9,2,5,3,7,101,18]` → `4`. One longest increasing subsequence is `[2,3,7,101]`
(also `[2,3,7,18]`), of length 4.

:::solution
```python
from bisect import bisect_left

def length_of_lis(nums: list[int]) -> int:
    tails = []
    for x in nums:
        i = bisect_left(tails, x)          # first tail >= x
        if i == len(tails):
            tails.append(x)                # x extends the longest chain
        else:
            tails[i] = x                   # x is a smaller tail for that length
    return len(tails)
```
```cpp
#include <vector>
#include <algorithm>

int lengthOfLIS(std::vector<int>& nums) {
    std::vector<int> tails;
    for (int x : nums) {
        auto it = std::lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);
        else *it = x;
    }
    return tails.size();
}
```
:::

---

## 3. Unique Paths

Number of paths from top-left to bottom-right of an `m × n` grid moving only right/down. Grid DP:
`dp[c] = dp[c] + dp[c-1]` (paths from above + paths from the left), rolled into a single row for
`O(n)` space.

**Example:** `m = 3, n = 7` → `28`. Each cell's path count is the sum of the cell above and the
cell to the left; the bottom-right accumulates to 28.

:::solution
```python
def unique_paths(m: int, n: int) -> int:
    dp = [1] * n                           # first row: one way to each cell
    for _ in range(1, m):
        for c in range(1, n):
            dp[c] += dp[c - 1]             # from above (old dp[c]) + from left
    return dp[-1]
```
```cpp
#include <vector>

int uniquePaths(int m, int n) {
    std::vector<int> dp(n, 1);
    for (int r = 1; r < m; r++)
        for (int c = 1; c < n; c++)
            dp[c] += dp[c - 1];
    return dp[n - 1];
}
```
:::

---

## 4. Word Break

Can `s` be segmented into words from a dictionary? State: `dp[i]` = "is `s[:i]` segmentable?".
Transition: `dp[i]` is true if some `j < i` has `dp[j]` true and `s[j:i]` is a word. **O(n²)**
time (with a set for `O(1)` lookups).

**Example:** `s = "leetcode", wordDict = ["leet","code"]` → `true` (`"leet" + "code"`).
`s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]` → `false` (no split covers
`"…og"`).

:::solution
```python
def word_break(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    dp = [True] + [False] * len(s)         # dp[0]: empty prefix is segmentable
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[len(s)]
```
```cpp
#include <string>
#include <vector>
#include <unordered_set>

bool wordBreak(std::string s, std::vector<std::string>& wordDict) {
    std::unordered_set<std::string> words(wordDict.begin(), wordDict.end());
    int n = s.size();
    std::vector<bool> dp(n + 1, false);
    dp[0] = true;
    for (int i = 1; i <= n; i++)
        for (int j = 0; j < i; j++)
            if (dp[j] && words.count(s.substr(j, i - j))) { dp[i] = true; break; }
    return dp[n];
}
```
:::

---

??? How do you turn a brute-force recursion into a DP?
Write the recursion first (define what the function returns for a given state). Draw the tree; if
the **same arguments** recur, the subproblems overlap, so add a **cache keyed by the state** —
that's top-down memoization and it collapses exponential work to polynomial. If you also want the
constant-factor and space win, rewrite it **bottom-up**: enumerate states in dependency order and
fill a table, then compress dimensions you no longer need (House Robber → two scalars, Unique
Paths → one row).

??? DP vs. greedy — when is greedy *not* safe?
Greedy commits to a locally optimal choice and never reconsiders; it's correct only when an
**exchange argument** proves a greedy-consistent global optimum exists. When a locally worse
choice can enable a better overall outcome (Coin Change with arbitrary denominations, 0/1
knapsack), greedy fails and you need DP, which considers all choices via overlapping subproblems.
