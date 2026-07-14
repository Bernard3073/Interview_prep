# Backtracking — common interview questions

## How it works

DFS over a tree of partial solutions: **choose → explore → un-choose**. Prune branches that
can't lead to a valid/better answer. Exponential in the worst case, but pruning and the
choose/undo discipline make it practical and the code uniform.

**Use when:** generate all subsets/permutations/combinations, N-queens, Sudoku, word search,
partitioning.

![Backtracking decision tree for subsets of {1,2,3}](images/lc-backtracking.svg)

**Pseudocode (template):**

```text
function backtrack(partial):
    if partial is a complete solution:
        record(partial); return
    for choice in choices(partial):
        if not promising(choice): continue    # prune dead branches early
        apply(choice)                          # choose
        backtrack(partial + choice)            # explore
        undo(choice)                           # un-choose
```

```python
def subsets(nums):
    res, path = [], []
    def backtrack(start):
        res.append(path[:])              # every node is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])          # choose
            backtrack(i + 1)              # explore (i+1 → no reuse; i → allow reuse)
            path.pop()                    # un-choose
    backtrack(0)
    return res
```

> **In-site drill:** the cleanest choose/explore/un-choose template, **Subsets**, runs in the
> editor → [open it](practice.html?p=subsets). Below are additional classics.

---

## 1. Permutations

All orderings of distinct `nums`. At each depth, choose any unused element, recurse, then undo.
A `used` array (or swapping in place) tracks what's already placed. **O(n · n!)** outputs.

**Example:** `[1,2,3]` → `[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]` — all `3! = 6`
orderings.

:::solution
```python
def permute(nums: list[int]) -> list[list[int]]:
    res, path = [], []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            res.append(path[:])            # a complete permutation
            return
        for i in range(len(nums)):
            if used[i]: continue
            used[i] = True; path.append(nums[i])    # choose
            backtrack()                              # explore
            path.pop(); used[i] = False              # un-choose
    backtrack()
    return res
```
```cpp
#include <vector>

void backtrack(std::vector<int>& nums, std::vector<bool>& used,
               std::vector<int>& path, std::vector<std::vector<int>>& res) {
    if (path.size() == nums.size()) { res.push_back(path); return; }
    for (int i = 0; i < (int)nums.size(); i++) {
        if (used[i]) continue;
        used[i] = true; path.push_back(nums[i]);
        backtrack(nums, used, path, res);
        path.pop_back(); used[i] = false;
    }
}
std::vector<std::vector<int>> permute(std::vector<int>& nums) {
    std::vector<std::vector<int>> res;
    std::vector<int> path;
    std::vector<bool> used(nums.size(), false);
    backtrack(nums, used, path, res);
    return res;
}
```
:::

---

## 2. Combination Sum

All combinations of `candidates` (reuse allowed) that sum to `target`. Pass `start` so
combinations stay non-decreasing (no permuted duplicates); recurse from `i` (not `i+1`) to allow
reuse; prune when the remaining target goes negative.

**Example:** `candidates = [2,3,6,7], target = 7` → `[[2,2,3],[7]]`. `2+2+3 = 7` (reuse of 2) and
the single `7` both reach the target; `[3,2,2]` isn't listed separately because `start` keeps
each combination non-decreasing.

:::solution
```python
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    res, path = [], []
    def backtrack(start, remain):
        if remain == 0:
            res.append(path[:]); return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:     # (sort first to make this a hard prune)
                continue
            path.append(candidates[i])
            backtrack(i, remain - candidates[i])   # i, not i+1 → reuse allowed
            path.pop()
    candidates.sort()
    backtrack(0, target)
    return res
```
```cpp
#include <vector>
#include <algorithm>

void backtrack(std::vector<int>& c, int start, int remain,
               std::vector<int>& path, std::vector<std::vector<int>>& res) {
    if (remain == 0) { res.push_back(path); return; }
    for (int i = start; i < (int)c.size(); i++) {
        if (c[i] > remain) break;          // sorted → all later are too big
        path.push_back(c[i]);
        backtrack(c, i, remain - c[i], path, res);
        path.pop_back();
    }
}
std::vector<std::vector<int>> combinationSum(std::vector<int>& candidates, int target) {
    std::sort(candidates.begin(), candidates.end());
    std::vector<std::vector<int>> res;
    std::vector<int> path;
    backtrack(candidates, 0, target, path, res);
    return res;
}
```
:::

---

## 3. Word Search

Does `word` exist in the grid along 4-directional adjacent cells (no reuse)? DFS from each cell,
marking the current cell visited (mutate then restore) as you match characters. **O(R·C·4^L)**
worst case.

**Example:** `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"`
→ `true`; the path snakes `A→B→C→C→E→D`. `word = "ABCB"` → `false` (the first `B` can't be
reused).

:::solution
```python
def exist(board: list[list[str]], word: str) -> bool:
    R, C = len(board), len(board[0])
    def dfs(r, c, k):
        if k == len(word): return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[k]:
            return False
        tmp, board[r][c] = board[r][c], "#"        # mark visited
        found = (dfs(r+1,c,k+1) or dfs(r-1,c,k+1) or
                 dfs(r,c+1,k+1) or dfs(r,c-1,k+1))
        board[r][c] = tmp                            # restore
        return found
    return any(dfs(r, c, 0) for r in range(R) for c in range(C))
```
```cpp
#include <vector>
#include <string>

bool dfs(std::vector<std::vector<char>>& b, const std::string& w, int r, int c, int k) {
    if (k == (int)w.size()) return true;
    int R = b.size(), C = b[0].size();
    if (r < 0 || r >= R || c < 0 || c >= C || b[r][c] != w[k]) return false;
    char tmp = b[r][c]; b[r][c] = '#';
    bool found = dfs(b,w,r+1,c,k+1) || dfs(b,w,r-1,c,k+1) ||
                 dfs(b,w,r,c+1,k+1) || dfs(b,w,r,c-1,k+1);
    b[r][c] = tmp;
    return found;
}
bool exist(std::vector<std::vector<char>>& board, std::string word) {
    for (int r = 0; r < (int)board.size(); r++)
        for (int c = 0; c < (int)board[0].size(); c++)
            if (dfs(board, word, r, c, 0)) return true;
    return false;
}
```
:::

---

??? What's the core template, and where does the pruning live?
`choose → explore → un-choose`: apply a choice, recurse, then **undo it** so siblings start from
a clean state. Pruning lives at the top of each recursive call (or before recursing): reject
partial states that can't complete (`remain < 0`, character mismatch, constraint violated). Good
pruning is what turns a theoretically exponential search into something that finishes.

??? How do you avoid duplicate combinations vs. duplicate permutations?
For **combinations**, pass a `start` index and only pick elements at or after it, so each set is
generated in one canonical (non-decreasing) order. For **permutations with duplicate values**,
sort first and skip a value at a given depth if it equals the previous value and that previous
copy wasn't used (`i > 0 && nums[i] == nums[i-1] && !used[i-1]`), which cuts mirrored branches.
