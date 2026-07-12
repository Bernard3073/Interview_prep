# Trees — the whole family, not just the BST

> A **tree** is a connected, acyclic graph with a single **root**: every node has exactly one
> parent (except the root) and any number of children. It's the shape of hierarchy — file systems,
> the DOM, parse trees, decision trees — and the substrate for a whole family of specialized
> structures (BSTs, heaps, tries, segment trees). This page introduces trees in general, then the
> variants you meet by name.

---

## Vocabulary (learn these once)

![Tree anatomy — root, parent/child, leaf, depth, height, subtree](images/ds-tree-anatomy.svg)

- **Root** — the single node with no parent; every traversal starts here.
- **Parent / child / sibling** — the obvious family relations along edges.
- **Leaf** — a node with no children; **internal node** — one with at least one child.
- **Depth** of a node — edges from the root down to it (root = 0).
- **Height** of the tree — the longest root-to-leaf path (= max depth).
- **Subtree** — a node together with all its descendants.
- **Degree** — number of children; a **binary** tree has degree ≤ 2, an **N-ary** tree any number.

Structural facts worth stating in an interview: a tree with `n` nodes has exactly `n − 1` edges,
no cycles, and one root. **Almost every tree operation costs O(height)** — which is why *balance*
(keeping height ≈ log n) is the recurring theme below.

---

## The binary tree

Each node has up to two children (`left`, `right`). Useful named forms:

| Form | Meaning |
|---|---|
| **Full** | every node has 0 or 2 children |
| **Complete** | all levels full except possibly the last, filled left-to-right (this is a **heap**) |
| **Perfect** | all internal nodes have 2 children and all leaves at the same depth |
| **Balanced** | height is O(log n) — left/right heights differ by a bounded amount |
| **Degenerate** | a chain — height n, no better than a linked list |

```text
class TreeNode:
    val
    left        # child subtree or null
    right
```

A complete tree needs no pointers — it packs into an **array** (child of `i` at `2i+1`, `2i+2`).
That's exactly how a heap is stored; see the Heaps page.

---

## Traversals — the core skill

![Tree traversals: pre-order, in-order, post-order, and level-order on one tree](images/ds-tree-traversals.svg)

**Depth-first (DFS)** dives down before going wide — a **stack** (or recursion). The three orders
differ only in *when you visit the node* relative to its children:

- **Pre-order** (node → L → R): copy/serialize a tree, prefix expressions.
- **In-order** (L → node → R): on a **BST this yields sorted order** — a key fact.
- **Post-order** (L → R → node): delete a tree, evaluate an expression, compute subtree
  aggregates (heights, sums) bottom-up.

**Breadth-first (BFS / level-order)** visits level by level — a **queue**. Use it for shortest
depth, level-by-level output, or "closest to the root" questions.

```text
# DFS (recursive)                    # BFS (iterative, level by level)
def dfs(node):                       q = deque([root])
    if not node: return              while q:
    visit(node)        # pre-order       node = q.popleft()
    dfs(node.left)                        visit(node)
    dfs(node.right)                       if node.left:  q.append(node.left)
                                          if node.right: q.append(node.right)
```

:::solution Level-order traversal (BFS by levels)
```python
from collections import deque

def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):          # exactly this level's nodes
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(level)
    return out
```
```cpp
vector<vector<int>> levelOrder(TreeNode* root) {
    vector<vector<int>> out;
    if (!root) return out;
    queue<TreeNode*> q; q.push(root);
    while (!q.empty()) {
        int sz = q.size();
        vector<int> level;
        for (int i = 0; i < sz; ++i) {       // fix the count = this level
            TreeNode* n = q.front(); q.pop();
            level.push_back(n->val);
            if (n->left)  q.push(n->left);
            if (n->right) q.push(n->right);
        }
        out.push_back(level);
    }
    return out;
}
```
:::

:::solution Max depth (height) — post-order recursion
```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```
```cpp
int maxDepth(TreeNode* root) {
    if (!root) return 0;
    return 1 + max(maxDepth(root->left), maxDepth(root->right));
}
```
:::

> **Recursion vs stack:** recursion is cleaner but risks stack overflow on a degenerate tree of
> depth n. Convert to an explicit stack when depth can be large.

---

## Binary search tree (BST)

A binary tree with an **ordering invariant**: for every node, all keys in the left subtree are
smaller and all in the right are larger. This buys **O(h) search/insert/delete** and — via
in-order traversal — **sorted iteration** for free.

![BST ordering invariant with in-order traversal producing sorted output](images/ds-bst.svg)

```text
search(node, key):
    while node and node.val != key:
        node = node.left if key < node.val else node.right
    return node
```

The catch: insert already-sorted keys into a naive BST and it degenerates into a chain
(height n → O(n) ops).

---

## Self-balancing trees — why `std::map` is fast

To guarantee height O(log n) regardless of insertion order, self-balancing BSTs restructure
(via **rotations**) after updates:

- **AVL tree** — strict balance (subtree heights differ by ≤ 1); faster lookups, more rotations.
- **Red-black tree** — looser balance with color rules; fewer rotations on insert/delete. This
  backs **`std::map` / `std::set`** and Java's `TreeMap`.

You won't code a red-black tree in an interview, but you should be able to say **what** balancing
buys (worst-case O(log n)) and **why** you'd pick a balanced BST over a hash map: **ordered**
operations — range queries, floor/ceiling, successor/predecessor, sorted iteration.

> **Python has no built-in balanced BST.** Simulate ordered-structure needs with a **sorted list +
> `bisect`** (O(log n) search, O(n) insert), the `sortedcontainers` library, or a heap when you
> only need the extreme.

---

## Trees in disguise

- **Heap** — a *complete* binary tree kept in an array; parent ≤ children. Pull-min in O(log n).
  See the Heaps page.
- **Trie (prefix tree)** — each node is a character; a root-to-node path spells a prefix. O(L)
  string lookup. See the Tries page.
- **N-ary tree** — arbitrary children (`children[]`); the DOM, file systems, game trees.
- **Segment tree / Fenwick (BIT)** — trees over an array index range for **O(log n) range queries
  + point updates** (range sum/min/max). Advanced, but worth naming when asked "range queries with
  updates."

---

## Interview checklist

1. **Shortest depth / level-by-level / "closest to root"** → BFS with a queue.
2. **Subtree aggregates (height, sum, diameter), delete, serialize** → DFS (post/pre-order).
3. **Sorted output from a BST** → in-order traversal.
4. **Ordered map/set, range/successor queries** → balanced BST (`std::map`); Python: `bisect`.
5. State **O(height)** and whether the tree is **balanced** — it decides O(log n) vs O(n).

??? What do the three DFS orders each give you, concretely?
**Pre-order** (node first) reproduces structure top-down — serialize/clone a tree, or emit a prefix
expression. **In-order** (node between children) yields **sorted keys on a BST**, so k-th smallest =
stop after k in-order visits. **Post-order** (node last) processes children before the parent —
required for deletion, freeing memory, evaluating an expression tree, or any bottom-up aggregate
like height or subtree sum.

??? Why must a BST be balanced, and what does balancing actually do?
All BST operations cost O(height). Random or adversarial (sorted) insertions can make height grow
to n, degrading everything to O(n) — a glorified linked list. **Self-balancing** trees (AVL,
red-black) perform **rotations** after updates to keep height O(log n), guaranteeing worst-case
O(log n) search/insert/delete. That worst-case guarantee is the main reason to choose a balanced
BST over a hash map when you also need ordering.

??? BST vs hash map — when do you pick the tree?
A hash map wins on raw point lookup (O(1) average) but is **unordered**. Choose a balanced BST when
you need **ordered** operations: sorted traversal, range queries (`all keys in [lo, hi]`),
floor/ceiling, successor/predecessor, or **worst-case** O(log n) guarantees rather than a hash
map's O(n) worst case.

??? How would you serialize and deserialize a binary tree?
Do a **pre-order** DFS, emitting each value and a marker (e.g. `#`) for null children — that records
structure. To deserialize, consume the stream in the same pre-order: read a value, then recursively
build the left subtree, then the right. Null markers tell recursion where to stop. Level-order with
null markers works too.
