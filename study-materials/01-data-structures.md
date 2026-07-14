# Week 1 — Core Data Structures

> Before you can recognize a **pattern**, you have to own the **containers** the pattern
> is built from. BFS is a queue. Top-k is a heap. Autocomplete is a trie. "Sorted and
> mutable" is a balanced BST. This week is the toolbox: for each structure — the
> *invariant* it maintains, the *cost* of each operation, the *library type* that
> implements it, and the *tell* that says "reach for this one." Next week these become
> the LeetCode patterns.

---

## How to pick a structure (the decision reflex)

Ask: **which operation must be fast, and how often do I do it?** Then match the shape:

- **Lookup by key / dedup / counting** → hash map / hash set. O(1) average.
- **Order matters, add/remove at one end** → stack (LIFO) or queue (FIFO).
- **"Next greater/smaller", matching brackets, undo, expression parsing** → stack (often *monotonic*).
- **Repeatedly pull the min or max** → heap / priority queue. O(log n) per pop.
- **O(1) insert/delete in the middle *if you hold the node*** → linked list (LRU, free lists).
- **Keep keys sorted *and* mutable (insert/erase/range/successor)** → balanced BST.
- **Prefix queries over strings / autocomplete / word dictionary** → trie.
- **Relationships / reachability / shortest path** → graph (adjacency list).
- **Dynamic connectivity / "are these in the same group?"** → union-find (DSU).

> Interview reflex: name the operation and its frequency *out loud*, state the naive cost,
> then pick the structure whose invariant makes that operation cheap. The structure is the
> answer to "what am I doing repeatedly, and why is it slow?"

---

## Complexity cheat sheet

| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Array / dynamic array | O(1) | O(n) | O(1)* end / O(n) mid | O(n) | *amortized; contiguous, cache-friendly |
| Hash map / set | — | O(1) avg | O(1) avg | O(1) avg | O(n) worst (collisions); unordered |
| Stack / queue / deque | O(1) ends | O(n) | O(1) | O(1) | LIFO / FIFO; deque = both ends |
| Binary heap | O(1) peek | O(n) | O(log n) | O(log n) | build/heapify O(n); not searchable |
| Singly / doubly linked list | O(n) | O(n) | O(1)† | O(1)† | †given the node; no random access |
| Balanced BST | O(log n) | O(log n) | O(log n) | O(log n) | in-order traversal = sorted |
| Trie | O(L) | O(L) | O(L) | O(L) | L = key length; alphabet-sized fan-out |
| Union-find (DSU) | — | ~O(α(n)) | ~O(α(n)) | — | union + find; α = inverse Ackermann |

---

## Language cheat sheet — Python ↔ C++

Interviewers expect you to reach for the *library* type, not hand-roll. Know both columns and
the gotcha in the last one — most bugs live there.

| Structure | Python | C++ (STL) | Watch out |
|---|---|---|---|
| Dynamic array | `list` | `std::vector` | `vector.reserve(n)` to avoid repeated reallocations |
| Hash map / set | `dict` / `set` | `std::unordered_map` / `unordered_set` | unordered; O(n) worst case on collisions |
| Ordered map / set | `bisect` on a sorted `list` | `std::map` / `std::set` | Python has **no** built-in balanced BST |
| Stack (LIFO) | `list` (`append`/`pop`) | `std::stack` | — |
| Queue / deque | `collections.deque` | `std::queue` / `std::deque` | `list.pop(0)` is **O(n)** — use a deque |
| Heap / PQ | `heapq` (**min**-heap) | `std::priority_queue` (**max**-heap) | opposite defaults — negate values to flip |
| Linked list | manual `Node` class | `std::list` (doubly) | rarely beats a `vector`/`list` in practice |
| Trie | `dict` of children | `array<Trie*,26>` or `unordered_map` | fixed array is faster for a lowercase alphabet |
| Union-find | `parent` / `rank` lists | `vector<int>` | path compression + union by rank |

---

## Deep-dive subpages

Each structure below has its own **deep-dive subpage** with more depth than this overview — the
invariant, variants, pseudocode, and full **Python + C++** solutions (toggle the language on each).
Start here for the map; open a subpage to actually learn one structure.

| Structure | Deep-dive subpage | Covers |
|---|---|---|
| Arrays & hashing | [Open →](topic.html?c=ds&t=arrays-hashing) | dynamic arrays · hash map/set · prefix sums · O(n²)→O(n) |
| Stacks & queues | [Open →](topic.html?c=ds&t=stacks-queues) | LIFO/FIFO · monotonic stack · deque · queue-from-stacks |
| Heaps / priority queues | [Open →](topic.html?c=ds&t=heaps-priority-queues) | binary heap · heapify O(n) · top-k · streaming median |
| Linked lists | [Open →](topic.html?c=ds&t=linked-lists) | singly/doubly · dummy head · fast/slow · LRU |
| Trees | [Open →](topic.html?c=ds&t=trees) | terminology · traversals · BST · balancing · heap/trie as trees |
| Tries | [Open →](topic.html?c=ds&t=tries) | prefix tree · O(L) lookup · wildcard search · autocomplete |
| Graphs | [Open →](topic.html?c=ds&t=graphs) | adjacency list/matrix · BFS vs DFS · topological sort |
| Union-Find (DSU) | [Open →](topic.html?c=ds&t=union-find) | path compression · union by rank · dynamic connectivity |

---

## Putting it together — the interview checklist

1. **Name the operation you repeat** (lookup? pull-min? prefix query? merge groups?).
2. **Match it to the structure** whose invariant makes that op cheap (the decision list up top).
3. **State the complexity** of every op you'll use, and the total.
4. **Know the library type** so you don't hand-roll: `dict`/`unordered_map`, `deque`,
   `heapq`/`priority_queue`, `std::map`/`std::set`, and a trie/DSU you can write in ~15 lines.
5. Watch the **gotchas**: `list.pop(0)` is O(n) (use a deque); Python `heapq` is min-only;
   a naive BST degrades on sorted input; hash maps have no order.

> Next week (LeetCode Patterns) these structures *become* the patterns: the BFS queue, the top-k
> heap, the union-find grouping, the monotonic stack. Own the containers now and the patterns
> read as "which structure, applied how."
