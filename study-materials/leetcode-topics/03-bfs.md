# BFS — common interview questions

## How it works

Explore level by level with a **queue**. On an **unweighted** graph/grid, the first time you
reach a node is via a **shortest path** (fewest edges). That's the whole reason BFS exists. Mark
nodes visited **on enqueue**, never on dequeue, so each node enters the queue once.

**Use when:** shortest path / minimum number of steps on an unweighted graph, level-order
traversal, "spread from multiple sources" (multi-source BFS), grid flood fill where you need
distance.

![BFS vs DFS visit order on the same tree](images/lc-bfs-dfs.svg)

**Pseudocode (template):**

```text
function bfs(start):
    queue ← [start];  seen ← {start};  dist ← 0
    while queue not empty:
        for each node in the current level:   # fixed-size sweep
            pop node
            if node is goal: return dist
            for nb in neighbors(node):
                if nb not in seen:
                    seen.add(nb)              # mark on ENQUEUE, not dequeue
                    queue.push(nb)
        dist ← dist + 1
    return -1                                 # unreachable
```

```python
from collections import deque

def bfs_shortest(grid, start, goal):
    R, C = len(grid), len(grid[0])
    q = deque([(start, 0)])             # (cell, distance)
    seen = {start}
    while q:
        (r, c), d = q.popleft()
        if (r, c) == goal: return d
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 0 and (nr,nc) not in seen:
                seen.add((nr, nc))      # mark on ENQUEUE, never on dequeue, to avoid dups
                q.append(((nr, nc), d+1))
    return -1
```

Weighted edges break BFS's shortest-path guarantee → use **Dijkstra** (a heap-ordered BFS).
0/1 weights → **0-1 BFS** with a deque.

> **In-site drill:** multi-source grid BFS, **Rotting Oranges**, runs in the editor →
> [open it](practice.html?p=rotting-oranges). Below are additional classics.

---

## Leveled BFS — when and how

**Leveled** (a.k.a. level-order) BFS processes the queue **one full layer at a time** instead of
node by node. Reach for it whenever the answer depends on *distance/depth*, not just on whether a
node was visited.

**How to spot it** — look for any of these tells:

1. **"Level" / "depth" is in the output shape.** You must return or reason about nodes grouped by
   how far they are from the start — level-order traversal (`List[List[int]]`), right-side view,
   average of levels, zigzag.
2. **"Minimum steps / fewest moves / shortest time"** on an *unweighted* graph or grid. Each sweep
   equals one unit of distance, so the level counter *is* the answer — Word Ladder, Open the Lock,
   01 Matrix.
3. **Simultaneous / multi-source spread.** "Everything spreads one step at a time, how long until
   X" — seed all sources at level 0 and count sweeps: Rotting Oranges, Walls and Gates.

If you only need "is B reachable?" or a plain count with no notion of distance, you don't need
leveling — but it costs nothing extra, so when in doubt, level.

**The one trick:** snapshot `len(q)` *before* the inner loop and pop exactly that many nodes.
Everything left in the queue after the sweep is the next level — the children you pushed during
the sweep won't be touched until the next `while` iteration.

```python
from collections import deque

def leveled_bfs(start):
    q = deque([start]); seen = {start}; level = 0
    while q:
        for _ in range(len(q)):        # freeze size = exactly this level's nodes
            node = q.popleft()
            # ... process node at depth `level` ...
            for nb in neighbors(node):
                if nb not in seen:
                    seen.add(nb)        # mark on ENQUEUE
                    q.append(nb)
        level += 1                      # one full sweep done → advance a level
    return level
```

**Two ways to track distance — pick one, don't mix:**

| Style | How | Best for |
| --- | --- | --- |
| **Level sweep** | `for _ in range(len(q))`, bump counter after each sweep | when you need nodes *grouped* per level (level-order, right-side view, zigzag) |
| **Distance in the tuple** | store `(node, dist)` in the queue, no inner loop | when you just need the number, not the grouping (the `bfs_shortest` template above) |

Both give correct shortest distances. Use the sweep whenever a whole layer must act at once — e.g.
**Rotting Oranges**, where each sweep = one minute and a full ring of oranges rots together:

```python
def oranges_rotting(grid: list[list[int]]) -> int:
    R, C = len(grid), len(grid[0])
    q, fresh = deque(), 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 2: q.append((r, c))    # all sources, level 0
            elif grid[r][c] == 1: fresh += 1
    minutes = 0
    while q and fresh:                              # guard avoids a trailing empty minute
        for _ in range(len(q)):                     # one minute = one sweep
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1                                # advance only after a full ring rots
    return -1 if fresh else minutes
```

---

## 1. Binary Tree Level Order Traversal

Return node values grouped by level. Process the queue one **level at a time**: record the
current queue size, pop exactly that many nodes, and enqueue their children for the next level.
**O(n)** time.

:::solution
```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def level_order(root: TreeNode) -> list[list[int]]:
    if not root: return []
    res, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):        # fixed-size sweep = one level
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        res.append(level)
    return res
```
```cpp
#include <vector>
#include <queue>

struct TreeNode {
    int val; TreeNode *left, *right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

std::vector<std::vector<int>> levelOrder(TreeNode* root) {
    std::vector<std::vector<int>> res;
    if (!root) return res;
    std::queue<TreeNode*> q; q.push(root);
    while (!q.empty()) {
        int n = q.size();
        std::vector<int> level;
        for (int i = 0; i < n; i++) {
            TreeNode* node = q.front(); q.pop();
            level.push_back(node->val);
            if (node->left)  q.push(node->left);
            if (node->right) q.push(node->right);
        }
        res.push_back(level);
    }
    return res;
}
```
:::

---

## 2. 01 Matrix

For each cell, the distance to the nearest 0. **Multi-source BFS**: seed the queue with *all*
zeros at distance 0, then relax outward — the first time a 1-cell is reached is its shortest
distance. **O(R·C)** time.

:::solution
```python
from collections import deque

def update_matrix(mat: list[list[int]]) -> list[list[int]]:
    R, C = len(mat), len(mat[0])
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    for r in range(R):
        for c in range(C):
            if mat[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))               # all sources start together
    while q:
        r, c = q.popleft()
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist
```
```cpp
#include <vector>
#include <queue>

std::vector<std::vector<int>> updateMatrix(std::vector<std::vector<int>>& mat) {
    int R = mat.size(), C = mat[0].size();
    std::vector<std::vector<int>> dist(R, std::vector<int>(C, -1));
    std::queue<std::pair<int,int>> q;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++)
            if (mat[r][c] == 0) { dist[r][c] = 0; q.push({r, c}); }
    int dirs[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};
    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        for (auto& d : dirs) {
            int nr = r + d[0], nc = c + d[1];
            if (nr >= 0 && nr < R && nc >= 0 && nc < C && dist[nr][nc] == -1) {
                dist[nr][nc] = dist[r][c] + 1;
                q.push({nr, nc});
            }
        }
    }
    return dist;
}
```
:::

---

## 3. Open the Lock

Fewest moves to turn a 4-wheel lock from `"0000"` to `target`, avoiding deadends. State = the
4-digit string; each state has 8 neighbors (each wheel ±1). Plain BFS over the state graph gives
the minimum number of moves. **O(10⁴ · 8)** states.

:::solution
```python
from collections import deque

def open_lock(deadends: list[str], target: str) -> int:
    dead = set(deadends)
    if "0000" in dead: return -1
    q = deque([("0000", 0)])
    seen = {"0000"}
    while q:
        state, steps = q.popleft()
        if state == target: return steps
        for i in range(4):
            d = int(state[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                nxt = state[:i] + str(nd) + state[i + 1:]
                if nxt not in seen and nxt not in dead:
                    seen.add(nxt)
                    q.append((nxt, steps + 1))
    return -1
```
```cpp
#include <string>
#include <vector>
#include <queue>
#include <unordered_set>

int openLock(std::vector<std::string>& deadends, std::string target) {
    std::unordered_set<std::string> dead(deadends.begin(), deadends.end());
    if (dead.count("0000")) return -1;
    std::queue<std::pair<std::string,int>> q; q.push({"0000", 0});
    std::unordered_set<std::string> seen{"0000"};
    while (!q.empty()) {
        auto [state, steps] = q.front(); q.pop();
        if (state == target) return steps;
        for (int i = 0; i < 4; i++) {
            for (int delta : {1, 9}) {                 // +1 and -1 (mod 10)
                std::string nxt = state;
                nxt[i] = '0' + (state[i] - '0' + delta) % 10;
                if (!seen.count(nxt) && !dead.count(nxt)) {
                    seen.insert(nxt);
                    q.push({nxt, steps + 1});
                }
            }
        }
    }
    return -1;
}
```
:::

---

??? Why mark visited on enqueue rather than on dequeue?
If you wait until a node is dequeued to mark it, the same node can be pushed by several
neighbors before it's first processed, so it sits in the queue multiple times — that bloats
memory and can break the `O(V+E)` bound. Marking it the instant it's enqueued guarantees each
node is queued at most once. (Mark the start node before the loop, too.)

??? When does BFS stop giving shortest paths, and what replaces it?
The moment edges carry **different positive weights** — BFS counts edges, not cost, so it can
settle a node before a cheaper multi-edge path arrives. Use **Dijkstra** (a heap-ordered BFS)
for non-negative weights, or **0-1 BFS** with a deque when weights are only 0 or 1. For graphs
with negative edges, Bellman-Ford.
