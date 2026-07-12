# Union-Find (DSU) — dynamic connectivity in ~O(1)

> **Union-Find**, a.k.a. the **disjoint-set union (DSU)**, tracks a partition of elements into
> groups and answers *"are these two in the same group?"* while groups keep merging. Two
> operations — **find** and **union** — both run in **near-constant** amortized time. It's the
> tidiest tool for **dynamic connectivity** and **cycle detection while adding edges**.

---

![Union-find: parent-pointer trees merged by union and flattened by path compression](images/lc-union-find.svg)

## The idea

Each group is a tree of **parent pointers**; the **root** is the group's representative.

- **find(x)** — follow parents up to the root. Two elements are in the same group iff they share a
  root.
- **union(a, b)** — link one root under the other, merging two trees into one.

Naively these trees can grow tall (O(n) find). Two optimizations flatten them so both operations
become **α(n)** amortized — the inverse Ackermann function, ≤ 4 for any input you'll ever see, i.e.
effectively constant:

- **Path compression** — during `find`, repoint nodes directly at the root, flattening the path.
- **Union by rank/size** — always attach the *shorter/smaller* tree under the taller/larger one,
  so height barely grows.

```text
find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]     # path compression (halving)
        x = parent[x]
    return x

union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb: return False             # already together (a cycle, if an edge)
    if rank[ra] < rank[rb]: swap(ra, rb)  # attach smaller under larger
    parent[rb] = ra
    if rank[ra] == rank[rb]: rank[ra] += 1
    return True
```

| Operation | Cost (amortized) |
|---|---|
| find | ~O(α(n)) ≈ O(1) |
| union | ~O(α(n)) ≈ O(1) |
| build (n singletons) | O(n) |

---

## Reference implementation

:::solution Union-Find with path compression + union by rank
```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))     # each element is its own root
        self.rank = [0] * n
        self.count = n                   # number of disjoint groups

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                 # already connected
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1                  # two groups merged into one
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)
```
```cpp
struct DSU {
    vector<int> parent, rank_;
    int count;
    DSU(int n) : parent(n), rank_(n, 0), count(n) {
        iota(parent.begin(), parent.end(), 0);       // parent[i] = i
    }
    int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;                                     // path compression
    }
    bool unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;                   // already connected
        if (rank_[ra] < rank_[rb]) swap(ra, rb);
        parent[rb] = ra;
        if (rank_[ra] == rank_[rb]) rank_[ra]++;
        --count;
        return true;
    }
    bool connected(int a, int b) { return find(a) == find(b); }
};
```
:::

---

## What it's for

- **Dynamic connectivity** — edges arrive over time; repeatedly ask "are a and b connected yet?"
- **Cycle detection (undirected)** — a `union` whose endpoints already share a root closes a cycle.
- **Kruskal's MST** — add edges cheapest-first, skipping any that would form a cycle.
- **Counting components / accounts merge / friend circles** — merge, then count distinct roots.
- **Grid percolation / islands with a growing set of open cells.**

:::solution Redundant Connection — the edge that creates a cycle
```python
def find_redundant(edges):
    dsu = DSU(len(edges) + 1)           # nodes are 1..n
    for u, v in edges:
        if not dsu.union(u, v):         # u and v already connected
            return [u, v]               # this edge closes the cycle
    return []
```
```cpp
vector<int> findRedundant(vector<vector<int>>& edges) {
    DSU dsu(edges.size() + 1);          // nodes 1..n
    for (auto& e : edges)
        if (!dsu.unite(e[0], e[1]))     // already connected
            return {e[0], e[1]};
    return {};
}
```
:::

---

## Interview checklist

1. **"Dynamic connectivity" / "are these connected?" as edges are added** → union-find.
2. **Undirected cycle detection / MST (Kruskal)** → union whose endpoints already share a root.
3. **Count groups** → track a `count`, decrement on each successful union.
4. Always apply **both** optimizations (path compression + union by rank) to claim ~O(1).
5. Map arbitrary labels (strings, coordinates) to integer indices first.

??? Union-find vs BFS/DFS for connectivity — when does each win?
Use **BFS/DFS** when the graph is fixed and you want to explore it once (list components, find paths,
compute distances). Use **union-find** when connectivity is **incremental** — edges keep arriving and
you repeatedly ask "connected yet?" — because it answers each query in ~O(1) without re-traversing.
It also detects cycles online as edges are added. Union-find gives *connectivity*, not *paths* — it
can't tell you the route between two nodes.

??? What do path compression and union by rank each contribute?
**Union by rank/size** keeps trees shallow by always hanging the smaller tree under the larger, so
height grows logarithmically at worst. **Path compression** flattens the path to the root on every
`find`, so repeated queries get cheaper over time. Individually each gives ~O(log n); **together**
they give the near-constant α(n) amortized bound. Skipping one leaves you with logarithmic finds.

??? Can you undo a union or delete an edge from a DSU?
Not with path compression — it destroys the structure needed to roll back. For "offline" problems
that require deletions, use **union-find with rollback** (union by rank only, no compression, keep a
stack of changes) or process queries in reverse and turn deletions into unions. Plain DSU is
**incremental-merge only**.
