# DFS — common interview questions

## How it works

Go as deep as possible, then backtrack — naturally **recursive** (or an explicit stack). DFS
doesn't find shortest paths, but it's the tool for **reachability, connected components, cycle
detection, topological sort, and enumerating all paths**. On a grid it's the flood-fill
workhorse.

**Use when:** counting/flooding regions, cloning or fully traversing a graph, "can you reach X",
topological ordering, or any "explore everything from here" task where distance doesn't matter.

![BFS vs DFS visit order on the same tree](images/lc-bfs-dfs.svg)

**Pseudocode (template):**

```text
function dfs(node):
    if node is invalid or already visited: return
    mark node visited
    ... pre-order work (e.g. count, record path) ...
    for nb in neighbors(node):
        dfs(nb)
    ... post-order work ...               # topological order = post-order reversed
```

```python
# Count connected components / islands in a grid — O(R*C)
def num_islands(grid):
    R, C = len(grid), len(grid[0])
    seen = set()
    def dfs(r, c):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] != '1' or (r,c) in seen:
            return
        seen.add((r, c))
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            dfs(r+dr, c+dc)
    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == '1' and (r,c) not in seen:
                dfs(r, c); count += 1
    return count
```

**Topological sort** (course scheduling, build/dependency order) is DFS on a DAG, pushing each
node *after* its descendants (post-order) and reversing — or Kahn's algorithm (BFS on
in-degrees). A back-edge during DFS = a **cycle** (so the schedule is impossible).

> **BFS vs. DFS in one line:** need the *shortest* / *fewest steps* → BFS. Need *existence / all
> of them / ordering* → DFS. Both are O(V+E); BFS uses O(width) memory, DFS uses O(depth) — go
> iterative for very deep grids to dodge recursion limits.

> **In-site drill:** DFS topological sort, **Course Schedule II**, runs in the editor →
> [open it](practice.html?p=course-schedule-ii). Below are additional classics (Number of Islands
> and Word Ladder are drilled in-site in other weeks, so they're not repeated here).

---

## 1. Clone Graph

Deep-copy a connected undirected graph. DFS from the start node, keeping a `old → new` map so
each node is cloned exactly once; the map also breaks cycles (return the existing clone on a
revisit). **O(V+E)** time.

**Example:** adjacency `[[2,4],[1,3],[2,4],[1,3]]` (a 4-node square, 1–2–3–4–1) → an
independent copy with the same structure. Cloning node 1 recurses into 2, which recurses back to
1 — the map returns 1's existing clone instead of looping forever.

:::solution
```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors or []

def clone_graph(node: "Node") -> "Node":
    if not node: return None
    clones = {}
    def dfs(cur):
        if cur in clones:
            return clones[cur]              # already cloned → reuse (handles cycles)
        copy = Node(cur.val)
        clones[cur] = copy                  # record BEFORE recursing
        for nb in cur.neighbors:
            copy.neighbors.append(dfs(nb))
        return copy
    return dfs(node)
```
```cpp
#include <unordered_map>
#include <vector>
#include <functional>

class Node {
public:
    int val;
    std::vector<Node*> neighbors;
    Node(int v) : val(v) {}
};

Node* cloneGraph(Node* node) {
    if (!node) return nullptr;
    std::unordered_map<Node*, Node*> clones;
    std::function<Node*(Node*)> dfs = [&](Node* cur) -> Node* {
        auto it = clones.find(cur);
        if (it != clones.end()) return it->second;
        Node* copy = new Node(cur->val);
        clones[cur] = copy;                 // record before recursing
        for (Node* nb : cur->neighbors)
            copy->neighbors.push_back(dfs(nb));
        return copy;
    };
    return dfs(node);
}
```
:::

---

## 2. Max Area of Island

Largest connected region of 1s (4-directionally) in a grid. DFS from each unvisited land cell,
sinking cells as you count them so nothing is double-counted. **O(R·C)** time.

**Example:** `[[1,1,0,0],[1,0,0,1],[0,0,1,1]]` → `3`. The top-left island has 3 cells and the
bottom-right island has 3; the largest area is `3`.

:::solution
```python
def max_area_of_island(grid: list[list[int]]) -> int:
    R, C = len(grid), len(grid[0])
    def dfs(r, c):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] == 0:
            return 0
        grid[r][c] = 0                        # sink to avoid revisiting
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)
    best = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 1:
                best = max(best, dfs(r, c))
    return best
```
```cpp
#include <vector>
#include <algorithm>

int dfs(std::vector<std::vector<int>>& g, int r, int c) {
    int R = g.size(), C = g[0].size();
    if (r < 0 || r >= R || c < 0 || c >= C || g[r][c] == 0) return 0;
    g[r][c] = 0;
    return 1 + dfs(g,r+1,c) + dfs(g,r-1,c) + dfs(g,r,c+1) + dfs(g,r,c-1);
}
int maxAreaOfIsland(std::vector<std::vector<int>>& grid) {
    int best = 0;
    for (int r = 0; r < (int)grid.size(); r++)
        for (int c = 0; c < (int)grid[0].size(); c++)
            if (grid[r][c] == 1) best = std::max(best, dfs(grid, r, c));
    return best;
}
```
:::

---

## 3. Pacific Atlantic Water Flow

Cells from which water can reach **both** oceans. Instead of searching from every cell, DFS
**inward from the borders**: mark all cells reachable from the Pacific edge and, separately,
from the Atlantic edge, flowing to **higher-or-equal** neighbors. The answer is the
intersection. **O(R·C)** time.

**Example:** for the classic `heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],
[5,1,1,2,4]]`, the cells reaching both oceans are `[[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]`
— the ridge cells high enough to drain toward both the top/left and bottom/right edges.

:::solution
```python
def pacific_atlantic(heights: list[list[int]]) -> list[list[int]]:
    R, C = len(heights), len(heights[0])
    pac, atl = set(), set()
    def dfs(r, c, seen, prev):
        if (r, c) in seen or not (0 <= r < R and 0 <= c < C) or heights[r][c] < prev:
            return
        seen.add((r, c))
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            dfs(r+dr, c+dc, seen, heights[r][c])
    for r in range(R):
        dfs(r, 0, pac, 0); dfs(r, C-1, atl, 0)
    for c in range(C):
        dfs(0, c, pac, 0); dfs(R-1, c, atl, 0)
    return [[r, c] for r, c in pac & atl]
```
```cpp
#include <vector>

void dfs(std::vector<std::vector<int>>& h, std::vector<std::vector<bool>>& seen,
         int r, int c, int prev) {
    int R = h.size(), C = h[0].size();
    if (r < 0 || r >= R || c < 0 || c >= C || seen[r][c] || h[r][c] < prev) return;
    seen[r][c] = true;
    dfs(h, seen, r+1, c, h[r][c]); dfs(h, seen, r-1, c, h[r][c]);
    dfs(h, seen, r, c+1, h[r][c]); dfs(h, seen, r, c-1, h[r][c]);
}
std::vector<std::vector<int>> pacificAtlantic(std::vector<std::vector<int>>& heights) {
    int R = heights.size(), C = heights[0].size();
    std::vector<std::vector<bool>> pac(R, std::vector<bool>(C)), atl = pac;
    for (int r = 0; r < R; r++) { dfs(heights, pac, r, 0, 0); dfs(heights, atl, r, C-1, 0); }
    for (int c = 0; c < C; c++) { dfs(heights, pac, 0, c, 0); dfs(heights, atl, R-1, c, 0); }
    std::vector<std::vector<int>> res;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++)
            if (pac[r][c] && atl[r][c]) res.push_back({r, c});
    return res;
}
```
:::

---

??? BFS vs. DFS — one line each on when to use which.
Need the **shortest path / fewest steps** on unweighted edges, or level-by-level output → BFS.
Need **existence, all of them, components, cycles, or an ordering** → DFS. Both are `O(V+E)`;
BFS costs `O(width)` memory, DFS `O(depth)` — so on very deep grids/graphs, go **iterative** with
an explicit stack to dodge recursion-limit stack overflows.

??? In Clone Graph, why record the clone in the map *before* recursing into neighbors?
Because the graph has **cycles**. If node A neighbors B and B neighbors A, cloning A recurses
into B, which recurses back into A. If A's clone isn't already in the map at that point, you
recurse forever. Inserting `clones[A] = copyA` before descending means the back-edge finds the
existing clone and returns immediately.
