# Graphs — nodes and the edges between them

> A **graph** is a set of **nodes (vertices)** connected by **edges** — the most general relational
> structure (a tree is just a graph with no cycles and one root). This page is about **representing**
> a graph and the two traversals — **BFS** and **DFS** — that everything else is built on.

---

![Graph stored as an adjacency list and as an adjacency matrix](images/ds-graph.svg)

## Flavors

- **Undirected vs directed** — is an edge two-way (`friends`) or one-way (`follows`, `depends-on`)?
- **Weighted vs unweighted** — does each edge carry a cost (distance, time)?
- **Cyclic vs acyclic** — a directed acyclic graph (**DAG**) can be **topologically sorted**
  (schedules, build systems, course prerequisites).
- **Connected / components** — is every node reachable, or are there islands?

## Two representations

| | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | **O(V + E)** | O(V²) |
| "Is u–v an edge?" | O(deg u) | **O(1)** |
| Iterate neighbors of u | O(deg u) | O(V) |
| Best for | **sparse** graphs (the default) | dense graphs / constant-time edge tests |

Almost always use an **adjacency list** — a `dict`/array mapping each node to its neighbors.

```text
# adjacency list
graph = defaultdict(list)
for (u, v) in edges:
    graph[u].append(v)
    graph[v].append(u)        # omit this line for a directed graph
```

| | Python | C++ |
|---|---|---|
| adjacency list | `defaultdict(list)` | `vector<vector<int>>` |
| visited set | `set()` | `vector<bool>` |
| BFS queue | `collections.deque` | `queue<int>` |

---

## BFS — breadth-first (a queue)

Explore in rings of increasing distance from the source. On an **unweighted** graph BFS finds the
**shortest path** (fewest edges), because it reaches every node in non-decreasing hop order. O(V+E).

```text
bfs(start):
    q = deque([start]); visited = {start}
    dist = {start: 0}
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                dist[v] = dist[u] + 1       # first time seen = shortest
                q.append(v)
```

## DFS — depth-first (a stack or recursion)

Dive as deep as possible, then backtrack. The tool for **reachability, connected components, cycle
detection, topological sort, and enumerating paths**. O(V+E).

```text
dfs(u):
    visited.add(u)
    for v in graph[u]:
        if v not in visited:
            dfs(v)
```

> **Pick by the question.** *Shortest path / fewest steps / level-by-level* → BFS. *Reachability /
> components / cycles / all paths / ordering* → DFS. Weighted shortest path → **Dijkstra** (a BFS
> with a min-heap frontier).

:::solution Number of connected components — DFS flood fill
```python
def count_components(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    seen = [False] * n
    def dfs(u):
        seen[u] = True
        for v in graph[u]:
            if not seen[v]:
                dfs(v)

    count = 0
    for i in range(n):
        if not seen[i]:                 # a new island
            count += 1
            dfs(i)
    return count
```
```cpp
int countComponents(int n, vector<vector<int>>& edges) {
    vector<vector<int>> g(n);
    for (auto& e : edges) { g[e[0]].push_back(e[1]); g[e[1]].push_back(e[0]); }
    vector<bool> seen(n, false);
    function<void(int)> dfs = [&](int u) {
        seen[u] = true;
        for (int v : g[u]) if (!seen[v]) dfs(v);
    };
    int count = 0;
    for (int i = 0; i < n; ++i)
        if (!seen[i]) { ++count; dfs(i); }      // new island
    return count;
}
```
:::

:::solution Course Schedule — cycle detection via topological sort (Kahn's BFS)
```python
from collections import deque

def can_finish(num, prereqs):
    graph = [[] for _ in range(num)]
    indeg = [0] * num
    for course, need in prereqs:            # need -> course
        graph[need].append(course)
        indeg[course] += 1

    q = deque(i for i in range(num) if indeg[i] == 0)
    done = 0
    while q:
        u = q.popleft()
        done += 1
        for v in graph[u]:
            indeg[v] -= 1                    # remove edge u->v
            if indeg[v] == 0:
                q.append(v)
    return done == num                      # all placed => no cycle
```
```cpp
bool canFinish(int num, vector<vector<int>>& prereqs) {
    vector<vector<int>> g(num);
    vector<int> indeg(num, 0);
    for (auto& p : prereqs) { g[p[1]].push_back(p[0]); indeg[p[0]]++; }
    queue<int> q;
    for (int i = 0; i < num; ++i) if (indeg[i] == 0) q.push(i);
    int done = 0;
    while (!q.empty()) {
        int u = q.front(); q.pop(); ++done;
        for (int v : g[u]) if (--indeg[v] == 0) q.push(v);
    }
    return done == num;                     // no cycle
}
```
:::

---

## The neighbor functions you'll actually build

Many "graph" problems have an **implicit** graph — a grid, a set of word transformations, a state
space. There's no adjacency list; you generate neighbors on the fly.

```text
# grid: 4-directional neighbors
for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
        ...   # BFS/DFS from here
```

---

## Interview checklist

1. Build an **adjacency list** unless the graph is dense or you need O(1) edge tests.
2. **Shortest path, unweighted** → BFS; **weighted** → Dijkstra (heap); **components/cycles/order**
   → DFS or Kahn's algorithm.
3. **Grid / word ladder / state space** → implicit graph; write a `neighbors()` generator.
4. Always carry a **`visited`** set — cycles cause infinite loops otherwise.
5. State **O(V + E)** for a plain traversal.

??? BFS vs DFS — how do you choose in one sentence?
Use **BFS** when distance/level matters — shortest path on an unweighted graph, "minimum number of
steps," or level-by-level output — because it visits nodes in non-decreasing hop order. Use **DFS**
when structure matters — reachability, connected components, cycle detection, topological ordering,
or enumerating all paths — because it naturally explores and backtracks.

??? Why does plain BFS give the shortest path only on *unweighted* graphs, and what replaces it?
BFS expands nodes in order of hop count, so the first time it reaches a node is via the fewest edges
— optimal only when every edge costs the same. With **weights**, fewest edges ≠ least cost, so you
switch to **Dijkstra** (a priority-queue frontier that always expands the lowest-cost node), or
Bellman-Ford when weights can be negative.

??? How do you detect a cycle — and does directed vs undirected change the method?
**Directed:** either DFS with three colors (white/gray/black) — a back-edge to a *gray* (in-progress)
node is a cycle — or **Kahn's topological sort**: if you can't place all nodes (some keep nonzero
in-degree), there's a cycle. **Undirected:** DFS and treat any visited neighbor that isn't your
parent as a cycle, or use **union-find** — an edge whose endpoints are already in the same set
closes a cycle.
