# Union-Find — common interview questions

## How it works

**Union-find (disjoint set union)** gives near-`O(1)` `union`/`find` with **path compression** +
**union by rank/size**. It answers "are these two in the same group?" and "how many groups?" under
incremental merges — the go-to for **dynamic connectivity**, counting components, cycle detection
in an **undirected** graph, and Kruskal's MST.

**Use when:** you're repeatedly merging pairs and asking about connectivity or group counts, or a
single extra edge creates a cycle.

![Union-find forests merging two sets](images/lc-union-find.svg)

**Pseudocode (template):**

```text
parent[i] ← i for every i
function find(x):
    while parent[x] ≠ x:
        parent[x] ← parent[parent[x]]    # path compression
        x ← parent[x]
    return x
function union(a, b):
    ra ← find(a);  rb ← find(b)
    if ra == rb: return false            # same set → this edge closes a cycle
    parent[rb] ← ra                      # (attach smaller rank under larger)
    return true
```

> **In-site drill:** **Number of Provinces** runs in the editor →
> [open it](practice.html?p=number-of-provinces). Below are additional classics — each reuses
> this DSU:

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n)); self.r = [0] * n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]     # path compression (halving)
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False             # already connected → this edge closes a cycle
        if self.r[ra] < self.r[rb]: ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]: self.r[ra] += 1
        return True
```

---

## 1. Redundant Connection

A tree had one extra edge added, forming a single cycle; return the edge that can be removed
(the last one in the input that closes a cycle). Union each edge — the first `union` that returns
false is the redundant edge. **O(n · α(n))** time.

**Example:** `edges = [[1,2],[1,3],[2,3]]` → `[2,3]`. Unioning `1-2` and `1-3` connects all three
nodes; the edge `2-3` then finds 2 and 3 already in the same set, so it's the redundant one.

:::solution
```python
def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    dsu = DSU(len(edges) + 1)               # nodes are 1..n
    for a, b in edges:
        if not dsu.union(a, b):             # a and b already connected → cycle edge
            return [a, b]
    return []
```
```cpp
#include <vector>
#include <numeric>

struct DSU {
    std::vector<int> p, r;
    DSU(int n) : p(n), r(n, 0) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    bool unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (r[ra] < r[rb]) std::swap(ra, rb);
        p[rb] = ra;
        if (r[ra] == r[rb]) r[ra]++;
        return true;
    }
};

std::vector<int> findRedundantConnection(std::vector<std::vector<int>>& edges) {
    DSU dsu(edges.size() + 1);
    for (auto& e : edges)
        if (!dsu.unite(e[0], e[1])) return e;
    return {};
}
```
:::

---

## 2. Number of Connected Components in an Undirected Graph

Count groups after unioning all edges. Start with `n` components and decrement each time a
`union` actually merges two different sets. **O(n + E·α(n))** time.

**Example:** `n = 5, edges = [[0,1],[1,2],[3,4]]` → `2`. Starting from 5 singletons, the merges
`0-1`, `1-2`, `3-4` drop the count to 2 components: `{0,1,2}` and `{3,4}`.

:::solution
```python
def count_components(n: int, edges: list[list[int]]) -> int:
    dsu = DSU(n)
    count = n
    for a, b in edges:
        if dsu.union(a, b):                 # a real merge reduces the count
            count -= 1
    return count
```
```cpp
#include <vector>
#include <numeric>

int countComponents(int n, std::vector<std::vector<int>>& edges) {
    DSU dsu(n);
    int count = n;
    for (auto& e : edges)
        if (dsu.unite(e[0], e[1])) count--;
    return count;
}
```
:::

---

## 3. Accounts Merge

Merge accounts that share any email (same person). Map each email to an owner index, union
accounts sharing an email, then group emails by their set's root. Sort each group and prepend the
name. Union-find handles the transitive "A shares with B, B shares with C" merging cleanly.

**Example:** `[["John","a@x.com","b@x.com"], ["John","b@x.com","c@x.com"], ["Mary","m@x.com"]]`
→ `[["John","a@x.com","b@x.com","c@x.com"], ["Mary","m@x.com"]]`. The first two Johns share
`b@x.com`, so they merge into one account; the unrelated Mary stays separate.

:::solution
```python
def accounts_merge(accounts: list[list[str]]) -> list[list[str]]:
    dsu = DSU(len(accounts))
    owner = {}                              # email -> first account index seen
    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in owner:
                dsu.union(i, owner[email])  # same email → same person
            else:
                owner[email] = i
    groups = {}                             # root index -> set of emails
    for email, i in owner.items():
        root = dsu.find(i)
        groups.setdefault(root, set()).add(email)
    return [[accounts[root][0]] + sorted(emails) for root, emails in groups.items()]
```
```cpp
#include <vector>
#include <string>
#include <unordered_map>
#include <map>
#include <set>
#include <numeric>

std::vector<std::vector<std::string>> accountsMerge(std::vector<std::vector<std::string>>& accounts) {
    DSU dsu(accounts.size());
    std::unordered_map<std::string, int> owner;
    for (int i = 0; i < (int)accounts.size(); i++)
        for (int j = 1; j < (int)accounts[i].size(); j++) {
            auto& email = accounts[i][j];
            if (owner.count(email)) dsu.unite(i, owner[email]);
            else owner[email] = i;
        }
    std::map<int, std::set<std::string>> groups;
    for (auto& [email, i] : owner) groups[dsu.find(i)].insert(email);
    std::vector<std::vector<std::string>> res;
    for (auto& [root, emails] : groups) {
        std::vector<std::string> row{accounts[root][0]};
        row.insert(row.end(), emails.begin(), emails.end());
        res.push_back(row);
    }
    return res;
}
```
:::

---

??? Why is union-find preferred over DFS/BFS for connectivity?
When connectivity is queried **incrementally** as edges arrive (or you just need group counts
after many merges), DSU answers each `union`/`find` in near-`O(1)` amortized without rebuilding a
traversal. DFS/BFS recompute components from scratch per query. DSU is also the natural fit for
**Kruskal's MST** (add an edge iff it joins two different components) and undirected cycle
detection.

??? What do path compression and union by rank each buy you?
**Path compression** flattens the tree during `find`, pointing nodes directly (or nearly) at the
root so later `find`s are shallow. **Union by rank/size** always hangs the smaller tree under the
larger root, keeping trees shallow to begin with. Together they give the inverse-Ackermann bound
`O(α(n))` per operation — effectively constant. Either alone is worse.
