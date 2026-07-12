# Linked Lists — pointers instead of contiguity

> A chain of nodes, each holding a value and a pointer to the next. No contiguous block, so **no
> O(1) random access** — but **O(1) insert/delete once you hold the node**, with no shifting. The
> interview value is less the structure itself and more the **pointer-manipulation reflexes** it
> drills.

---

![Singly and doubly linked lists; O(1) middle removal by relinking](images/ds-linkedlist.svg)

## Shapes

- **Singly linked:** each node has `next`. Traverse forward only.
- **Doubly linked:** each node has `next` **and** `prev`. Traverse both ways; remove a node in
  O(1) given only that node (relink its neighbors). Backs the **LRU cache** and `std::list`.
- **Circular:** the tail's `next` points back to the head — round-robin schedulers, ring buffers.

| Operation | Array | Linked list |
|---|---|---|
| Access index i | O(1) | O(n) (walk from head) |
| Insert/delete at a **held** node | O(n) (shift) | **O(1)** (relink) |
| Insert/delete at head | O(n) | O(1) |
| Search by value | O(n) | O(n) |
| Memory / cache | contiguous, friendly | scattered, pointer-chasing |

```text
class Node:
    val
    next        # and prev, for a doubly linked list
```

> **Reality check:** arrays usually beat linked lists in practice because contiguous memory is
> cache-friendly while pointer-chasing thrashes the cache. Reach for a linked list when you need
> **O(1) splice/erase at a node you already hold** (LRU eviction, free lists) — not for generic
> sequences.

---

## The two reflexes: dummy head & fast/slow pointers

**Dummy (sentinel) head** — allocate a throwaway node before the real head so insertion/deletion at
the front needs no special case; return `dummy.next` at the end.

**Fast/slow pointers (Floyd)** — advance one pointer by 1 and another by 2. When fast reaches the
end, slow is at the **middle**; if there's a **cycle**, they eventually meet.

```text
# detect a cycle
slow = head; fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow is fast:
        return True          # pointers met -> cycle
return False
```

:::solution Reverse a singly linked list — iterative, O(n) / O(1)
```python
def reverse_list(head):
    prev = None
    while head:
        nxt = head.next     # save next
        head.next = prev    # flip the pointer
        prev = head         # advance prev
        head = nxt          # advance head
    return prev             # new head
```
```cpp
ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    while (head) {
        ListNode* nxt = head->next;   // save
        head->next = prev;            // flip
        prev = head;                  // advance
        head = nxt;
    }
    return prev;
}
```
:::

:::solution Merge two sorted lists — dummy head
```python
def merge(a, b):
    dummy = tail = ListNode()           # sentinel avoids head special-case
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b                  # attach the remainder
    return dummy.next
```
```cpp
ListNode* merge(ListNode* a, ListNode* b) {
    ListNode dummy, *tail = &dummy;
    while (a && b) {
        if (a->val <= b->val) { tail->next = a; a = a->next; }
        else                  { tail->next = b; b = b->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}
```
:::

---

## Why the LRU cache pairs a hash map with a doubly linked list

An LRU cache needs two O(1) operations: **find a key** and **move it to "most recently used."** A
hash map gives O(1) find (key → node); a doubly linked list gives O(1) move/evict (unlink a node,
splice it to the front, drop the tail). Neither alone suffices — together they hit O(1) for both
`get` and `put`.

```text
get(key):   node = map[key]; move node to front; return node.val
put(key,v): if key in map: update, move to front
            else: insert at front; map[key]=node
                  if size > capacity: evict tail; delete map[tail.key]
```

---

## Interview checklist

1. **Reversal / reordering / merging** → track `prev`/`next` carefully; draw the pointers.
2. **Middle, cycle, k-th from end** → fast/slow pointers.
3. **Head might change** → dummy sentinel node.
4. **O(1) get + O(1) recency update** → hash map + doubly linked list (LRU).
5. In C++ mind **ownership** — who frees the nodes (raw pointers vs `unique_ptr`).

??? What's the single most useful trick for linked-list problems, and why?
The **dummy head**. Front insertions/deletions and "the head itself might be removed" are the
bug-prone cases; a sentinel node before the head makes every position uniform, so you write one
code path and return `dummy.next`. It eliminates most null-pointer edge cases.

??? Find the middle, detect a cycle, and find the cycle's start — all with two pointers?
**Middle:** slow +1, fast +2; when fast ends, slow is the middle. **Cycle detection:** same walk —
if they ever meet, there's a cycle (Floyd). **Cycle start:** after they meet, reset one pointer to
the head and advance both by 1; they meet at the entry node (a distance argument shows why).

??? Doubly vs singly linked — what does the extra `prev` pointer buy, and what does it cost?
`prev` lets you **delete a node in O(1) given only that node** (relink both neighbors) and traverse
backward — essential for LRU and `std::list`. The cost is an extra pointer per node (more memory)
and two links to maintain on every insert/delete, so it's easier to introduce bugs.
