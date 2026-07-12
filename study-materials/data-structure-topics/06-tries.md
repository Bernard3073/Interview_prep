# Tries — prefix trees for strings

> A **trie** (from re*trie*val, usually said "try") stores a set of strings by **sharing common
> prefixes**. Each node is one character; the path from the root spells a prefix. Insert and
> lookup cost **O(L)** in the key length — independent of how many words are stored — and it
> answers **prefix** queries a hash set simply can't.

---

![Trie storing cat/car/can/dog with shared prefixes and end-of-word markers](images/ds-trie.svg)

## Structure

Each node holds:
- a map/array of **children** keyed by the next character, and
- an **`is_end`** flag marking that a complete word ends here.

Words that share a prefix share the path for that prefix — "cat", "car", "can" all reuse the
`c → a` edges, then branch. That sharing is the whole point: memory scales with *distinct
prefixes*, and any prefix query walks one edge per character.

| Operation | Cost | Note |
|---|---|---|
| insert(word) | O(L) | create missing child nodes down the path |
| search(word) | O(L) | walk the path; check `is_end` at the end |
| startsWith(prefix) | O(L) | walk the path; existence is enough |
| space | O(total chars) | worst case; shared prefixes save memory |

`L` = length of the word/prefix. Note there's **no dependence on N** (the number of stored words) —
that's the trie's edge over scanning a list or even hashing when prefixes matter.

```text
insert(word):
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = new Node()
        node = node.children[ch]
    node.is_end = True

search(word):                       # exact word present?
    node = walk(word)
    return node is not None and node.is_end

startsWith(prefix):                 # any word with this prefix?
    return walk(prefix) is not None
```

---

## Implementation choices

- **Children as a hash map** (`dict[char] → node`): flexible, any alphabet (Unicode, mixed case).
- **Children as a fixed array** (`array<Node*, 26>` for `a–z`): faster and cache-friendlier, but
  wastes slots on sparse alphabets. Pick based on the character set.

| | Python | C++ |
|---|---|---|
| children | `dict` (or `defaultdict`) | `array<Trie*,26>` or `unordered_map<char,Trie*>` |
| end flag | `is_end: bool` | `bool isEnd` |

:::solution Implement Trie — insert / search / startsWith
```python
class Trie:
    def __init__(self):
        self.children = {}          # char -> Trie
        self.is_end = False

    def insert(self, word):
        node = self
        for c in word:
            node = node.children.setdefault(c, Trie())
        node.is_end = True

    def _walk(self, s):
        node = self
        for c in s:
            if c not in node.children:
                return None
            node = node.children[c]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        return self._walk(prefix) is not None
```
```cpp
struct Trie {
    array<Trie*, 26> child{};       // 'a'..'z', all null
    bool isEnd = false;

    void insert(const string& w) {
        Trie* node = this;
        for (char c : w) {
            int i = c - 'a';
            if (!node->child[i]) node->child[i] = new Trie();
            node = node->child[i];
        }
        node->isEnd = true;
    }
    Trie* walk(const string& s) {
        Trie* node = this;
        for (char c : s) {
            int i = c - 'a';
            if (!node->child[i]) return nullptr;
            node = node->child[i];
        }
        return node;
    }
    bool search(const string& w)    { Trie* n = walk(w); return n && n->isEnd; }
    bool startsWith(const string& p){ return walk(p) != nullptr; }
};
```
:::

:::solution Wildcard search — `.` matches any character (branch the walk)
```python
class WordDictionary:
    def __init__(self):
        self.root = {}              # nested dicts; "$" marks end of word

    def add(self, word):
        node = self.root
        for c in word:
            node = node.setdefault(c, {})
        node["$"] = True

    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return "$" in node
            c = word[i]
            if c == ".":                        # try every child
                return any(dfs(child, i + 1)
                           for k, child in node.items() if k != "$")
            return c in node and dfs(node[c], i + 1)
        return dfs(self.root, 0)
```
```cpp
struct WordDictionary {
    struct Node { unordered_map<char, Node*> ch; bool end = false; };
    Node* root = new Node();

    void add(const string& w) {
        Node* n = root;
        for (char c : w) { if (!n->ch.count(c)) n->ch[c] = new Node(); n = n->ch[c]; }
        n->end = true;
    }
    bool dfs(Node* n, const string& w, int i) {
        if (i == (int)w.size()) return n->end;
        char c = w[i];
        if (c == '.') {                         // any child
            for (auto& [k, nxt] : n->ch)
                if (dfs(nxt, w, i + 1)) return true;
            return false;
        }
        return n->ch.count(c) && dfs(n->ch[c], w, i + 1);
    }
    bool search(const string& w) { return dfs(root, w, 0); }
};
```
:::

---

## Where tries shine

- **Autocomplete / typeahead** — walk to the prefix node, then DFS to enumerate completions.
- **Spell-check / dictionary** — membership plus near-miss suggestions.
- **Wildcard / regex-lite matching** — branch on `.` (above).
- **Word-search / Boggle boards** — one trie of the dictionary prunes DFS across the grid.
- **Longest-prefix matching** — IP routing tables, phone prefixes.

---

## Interview checklist

1. **"Prefix", "startsWith", "autocomplete", "dictionary of words"** → trie.
2. **Wildcard `.` matching** → DFS the trie, branching on `.`.
3. **Many words searched on a grid** → build one trie, DFS the grid against it (prune dead paths).
4. State **O(L)**, independent of the number of stored words.
5. Choose **array vs hash-map children** by alphabet size.

??? A hash set already gives O(1) word lookup — why ever use a trie?
A hash set answers "**is this exact word present?**" but cannot answer "**does any word start with
`pre`?**" without scanning every key. A trie answers **prefix** queries in O(L), enumerates all
completions of a prefix, supports wildcard matching, and shares memory across common prefixes. Use a
hash set for exact membership; a trie whenever prefixes matter.

??? How does a trie power autocomplete?
Walk from the root to the node at the end of the typed prefix — O(L). Everything in that node's
subtree is a valid completion, so **DFS the subtree** collecting words that have `is_end` set. Rank
by frequency (store a count per word) or cache the top-k completions at each node for instant
suggestions.

??? What's the memory cost of a trie, and how do you cut it?
Worst case is O(total characters across all words), and a hash-map-per-node has pointer overhead. A
**radix tree (compressed trie)** merges chains of single-child nodes into one edge labeled with a
substring, collapsing long non-branching paths. Using a fixed child **array** instead of a hash map
also trims per-node overhead for a small alphabet.
