# Arrays & Hashing — the O(1)-lookup workhorse

> The two structures you use in almost every problem. An **array** is contiguous memory with
> O(1) random access; a **hash table** trades ordering for O(1)-average lookup by key. Most
> "make it faster than O(n²)" moments are really "add a hash map."

---

## The array

A block of equal-sized slots laid out contiguously in memory. Index `i` lives at
`base + i × elem_size`, so **access by index is O(1)** and iteration is cache-friendly (the
CPU prefetches the next slots). The cost lives at the edges:

| Operation | Cost | Why |
|---|---|---|
| Read/write `a[i]` | O(1) | direct address arithmetic |
| Append (dynamic array) | O(1) amortized | doubles capacity, occasional O(n) copy |
| Insert / delete at middle | O(n) | shift every element after the gap |
| Search (unsorted) | O(n) | must scan |
| Search (sorted) | O(log n) | binary search |

A **dynamic array** (`list`, `std::vector`) hides growth: when full it allocates a bigger block
(usually ×2) and copies. Because doublings are rare, the *amortized* append cost is O(1) even
though a single append can be O(n).

> **C++ tip:** call `vec.reserve(n)` when you know the final size — it skips the reallocation/copy
> churn. **Python tip:** a list comprehension beats repeated `.append()` in a loop.

---

## The hash table

A hash table stores key→value by computing `index = hash(key) % capacity` and dropping the entry
in that bucket. A good hash spreads keys uniformly, so lookup/insert/delete are **O(1) average**.
Two keys can land in the same bucket — a **collision** — resolved by chaining (a list per bucket)
or open addressing (probe for the next free slot). When the **load factor** (entries ÷ buckets)
gets near 1, the table **rehashes** into a larger array.

![Hash map: key hashed to a bucket, with a collision chain](images/ds-hashmap.svg)

- **Average** O(1); **worst case** O(n) if every key collides (adversarial input or a bad hash).
- **No ordering** — iteration order is arbitrary (Python `dict` preserves *insertion* order as an
  implementation detail; `unordered_map` gives no guarantee). Need sorted keys? That's a
  balanced BST (`std::map`), not a hash table.
- Keys must be **hashable / immutable** (a tuple, not a list).

| Need | Python | C++ |
|---|---|---|
| key → value | `dict` | `std::unordered_map` |
| membership / dedup | `set` | `std::unordered_set` |
| counting | `collections.Counter` | `unordered_map<T,int>` |
| group by key | `collections.defaultdict(list)` | `unordered_map<K, vector<V>>` |

---

## The core move: turn O(n²) into O(n)

Whenever you catch a nested loop asking *"is there another element such that…?"*, a hash map
usually collapses it: remember what you've seen, then each element does an O(1) lookup instead of
an O(n) rescan. Two Sum is the archetype.

```text
seen = empty map            # value -> index
for i, x in enumerate(nums):
    need = target - x
    if need in seen:        # O(1)
        return [seen[need], i]
    seen[x] = i
```

:::solution Two Sum — one pass, O(n) time / O(n) space
```python
def two_sum(nums, target):
    seen = {}                       # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:      # complement already stored?
            return [seen[target - x], i]
        seen[x] = i
    return []
```
```cpp
vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int,int> seen;            // value -> index
    for (int i = 0; i < (int)nums.size(); ++i) {
        auto it = seen.find(target - nums[i]);
        if (it != seen.end()) return {it->second, i};
        seen[nums[i]] = i;
    }
    return {};
}
```
:::

:::solution Group Anagrams — hash by a canonical key
```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))      # same letters -> same key
        groups[key].append(w)
    return list(groups.values())
```
```cpp
vector<vector<string>> groupAnagrams(vector<string>& words) {
    unordered_map<string, vector<string>> groups;
    for (auto& w : words) {
        string key = w;
        sort(key.begin(), key.end());   // canonical form
        groups[key].push_back(w);
    }
    vector<vector<string>> out;
    for (auto& [k, v] : groups) out.push_back(move(v));
    return out;
}
```
:::

---

## Prefix sums — the other array superpower

Precompute `pre[i] = a[0] + … + a[i-1]` once (O(n)); then **any** range sum `a[l..r]` is
`pre[r+1] - pre[l]` in O(1). Pairing prefix sums with a hash map counts subarrays with a target
sum in one pass.

```text
pre = 0; count = 0; seen = {0: 1}       # prefix-sum -> how many times seen
for x in nums:
    pre += x
    count += seen.get(pre - k, 0)       # a previous prefix makes a k-sum window
    seen[pre] = seen.get(pre, 0) + 1
```

---

## Interview checklist

1. **"Have I seen…?" / "does a pair/complement exist?"** → hash set/map, one pass.
2. **Repeated range-sum queries on a static array** → prefix sums.
3. **Counting / frequencies / grouping** → `Counter` / `defaultdict`.
4. State the **average vs worst case** — O(1) hashing degrades to O(n) with collisions.
5. Watch mutation-while-iterating and **unhashable keys** (convert lists to tuples).

??? Why is a hash map "O(1) average" but not just "O(1)"?
The average assumes a good hash spreading keys across buckets with a bounded load factor, so each
bucket holds ~O(1) entries. Adversarial keys (or a weak hash) can pile everything into one bucket,
degrading lookups to O(n). Rehashing keeps the load factor low, and a single insert that triggers a
rehash is O(n) — amortized O(1) across many inserts.

??? When would you deliberately avoid a hash map?
When you need **ordering** (sorted iteration, successor/floor queries → balanced BST), when keys
are a **small dense integer range** (a plain array is faster and simpler), when **worst-case
guarantees** matter (a balanced BST is O(log n) worst case vs a hash map's O(n)), or in
**memory-tight / cache-sensitive** hot loops where contiguous arrays win.

??? A `set` and a `dict` both give O(1) lookup — when do you pick which?
A `set` stores keys only (membership, dedup, "seen?"). A `dict` maps keys to values (counts,
indices, adjacency). If you find yourself storing `True` as every value in a dict, you want a set.
