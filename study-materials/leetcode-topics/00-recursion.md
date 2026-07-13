# Recursion — common interview questions

## How it works

Recursion isn't so much a pattern as the **engine** several patterns run on: **DFS**,
**backtracking**, **divide & conquer**, and **top-down DP** are all recursion with one extra
bookkeeping habit bolted on. A function calls itself on a **strictly smaller** input until it
hits a **base case** it can answer directly, then combines the results on the way back up.

**Use when:** the problem is **self-similar** — a tree/linked list, "solve a smaller version of
the same problem," nested structure, or a definition that refers to itself (factorial, `pow`,
Fibonacci).

![Recursion call stack for factorial(4): descend to the base case, then combine back up](images/lc-recursion.svg)

Every correct recursion has exactly two parts:

1. **Base case(s)** — the smallest inputs you answer *without* recursing. Miss one → infinite
   recursion → stack overflow.
2. **Recursive case** — reduce to one or more **strictly smaller** subproblems, call yourself,
   and **combine** the results. "Strictly smaller" is what guarantees you reach a base case.

**Pseudocode (template):**

```text
function solve(problem):
    if is_base_case(problem):          # 1. stop condition — answer directly
        return base_answer(problem)
    subs = reduce(problem)             # 2. one or more strictly smaller subproblems
    results = [solve(s) for s in subs]
    return combine(results)            # 3. build this level's answer from the smaller ones
```

```python
def factorial(n):
    if n <= 1:                 # base case
        return 1
    return n * factorial(n - 1)   # trust that factorial(n-1) is correct, then combine
```

**The leap of faith:** don't trace the whole call tree in your head. Assume the recursive call
*already returns the right answer for the smaller input*, verify your combine step and that the
base case is reachable — induction does the rest.

**Cost:** time = (number of calls) × (work per call), usually captured as a **recurrence**;
space = the **maximum call-stack depth** (each pending call holds a frame), so deep recursion is
O(depth) memory even when each level does little. That depth is why Python caps recursion around
1000 and why very deep recursion is rewritten iteratively.

> **In-site drill:** the cleanest "recurse on children, combine at the parent" problem,
> **Diameter of Binary Tree**, runs in the editor → [open it](practice.html?p=diameter-of-binary-tree).
> Below are additional classics with full Python/C++ solutions.

---

## 1. Pow(x, n)

Compute `x^n`. Naive multiplication is O(n); **halve the exponent** instead — `x^n = (x^{n/2})^2`
(times an extra `x` when `n` is odd) — for **O(log n)**. Handle negative `n` by inverting `x` and
negating `n`. The single recursive call on `n/2` is what makes the recursion tree a *chain* of
depth `log n`.

:::solution
```python
def my_pow(x: float, n: int) -> float:
    if n < 0:
        x, n = 1 / x, -n
    def helper(k):
        if k == 0:                 # base case: x^0 = 1
            return 1.0
        half = helper(k // 2)      # compute x^(k/2) ONCE
        half_sq = half * half
        return half_sq * x if k % 2 else half_sq   # odd k → one extra x
    return helper(n)
```
```cpp
double helper(double x, long long k) {
    if (k == 0) return 1.0;              // base case
    double half = helper(x, k / 2);      // compute x^(k/2) once
    double sq = half * half;
    return (k % 2) ? sq * x : sq;        // odd exponent → one extra x
}
double myPow(double x, int n) {
    long long k = n;
    if (k < 0) { x = 1 / x; k = -k; }
    return helper(x, k);
}
```
:::

---

## 2. Reverse a Linked List (recursively)

Textbook **linear recursion**: recurse to the tail, then rewire pointers on the way back up.
Trust that `reverse(head.next)` hands you the reversed rest; you only have to fix the single link
between `head` and `head.next`. **O(n)** time, **O(n)** stack.

:::solution
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def reverse_list(head: ListNode) -> ListNode:
    if head is None or head.next is None:   # base case: empty or single node
        return head
    new_head = reverse_list(head.next)      # reverse the rest (leap of faith)
    head.next.next = head                   # make the next node point back at us
    head.next = None                        # and cut our old forward link
    return new_head                         # new head bubbles up unchanged
```
```cpp
struct ListNode { int val; ListNode* next; };

ListNode* reverseList(ListNode* head) {
    if (!head || !head->next) return head;      // base case
    ListNode* newHead = reverseList(head->next); // reverse the rest
    head->next->next = head;                     // point next node back at us
    head->next = nullptr;                        // cut old forward link
    return newHead;                              // new head is unchanged going up
}
```
:::

---

## 3. Merge Two Sorted Lists (recursively)

Recursion that **builds structure**: the smaller head is the answer's head; its `next` is "the
merge of the rest," which is the same problem on shorter input. Base case is when either list is
empty. **O(n + m)** time, O(n + m) stack.

:::solution
```python
def merge_two_lists(a: ListNode, b: ListNode) -> ListNode:
    if a is None: return b        # base cases: one list exhausted
    if b is None: return a
    if a.val <= b.val:
        a.next = merge_two_lists(a.next, b)   # a leads; merge the rest behind it
        return a
    else:
        b.next = merge_two_lists(a, b.next)
        return b
```
```cpp
ListNode* mergeTwoLists(ListNode* a, ListNode* b) {
    if (!a) return b;                       // base cases
    if (!b) return a;
    if (a->val <= b->val) {
        a->next = mergeTwoLists(a->next, b);
        return a;
    } else {
        b->next = mergeTwoLists(a, b->next);
        return b;
    }
}
```
:::

---

## 4. Fibonacci — naive recursion vs. memoized

The canonical lesson in *why recursion can be slow and how to fix it without changing the logic*.
Naive `fib(n) = fib(n-1) + fib(n-2)` is **branching** recursion: the same arguments recur, so the
tree has O(φⁿ) nodes — exponential. Because subproblems **overlap**, caching each result
(**memoization**) collapses it to **O(n)**. That one step *is* top-down DP.

:::solution
```python
# Naive: O(φ^n) time — every fib(k) is recomputed many times
def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

# Memoized: O(n) time, O(n) space — each fib(k) computed once
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```
```cpp
#include <vector>

// Memoized: each fib(k) computed once → O(n)
int fibHelper(int n, std::vector<int>& memo) {
    if (n < 2) return n;                 // base cases
    if (memo[n] != -1) return memo[n];   // already solved this subproblem
    return memo[n] = fibHelper(n - 1, memo) + fibHelper(n - 2, memo);
}
int fib(int n) {
    std::vector<int> memo(n + 1, -1);
    return fibHelper(n, memo);
}
```
:::

---

??? What two parts must every recursion have, and what breaks if either is wrong?
A **base case** (smallest input answered without recursing) and a **recursive case** that reduces
to a **strictly smaller** subproblem and combines the results. A missing/wrong base case, or a
recursive case that doesn't actually shrink the input, means the calls never stop → **stack
overflow**. So state the base case *first*, then show each recursive call strictly moves toward
it. For correctness, use the **recursive leap of faith**: assume the recursive call is right for
the smaller input, then just check the combine step and termination.

??? How do you analyze the time and space complexity of a recursion?
**Time** = (number of calls) × (work per call), usually written as a **recurrence** and solved:
`T(n)=T(n-1)+O(1)` → O(n) (factorial); `T(n)=2T(n/2)+O(n)` → O(n log n) by the **Master Theorem**
(merge sort); `T(n)=T(n-1)+T(n-2)` → O(φⁿ) (naive Fibonacci). **Space** is the **maximum call
stack depth** — O(n) for linear recursion, O(log n) for balanced divide & conquer, O(height) for
a tree walk. Note time and space can differ sharply: naive Fibonacci is exponential time but only
O(n) stack.

??? How would you convert a recursive solution to iterative, and why?
It depends on the shape. **Tail / linear** recursion → a plain **loop** with an accumulator.
**Branching** recursion (tree/graph walks) → a loop with an **explicit stack** you push/pop
yourself (that *is* iterative DFS). **Overlapping-subproblem** recursion → **memoization** or a
**bottom-up table** (that *is* DP). Reasons to bother: avoid **stack overflow** on deep inputs,
cut the constant-factor overhead of call frames, and sometimes reduce space. The logic is
identical — you're just managing the stack explicitly instead of letting the language do it.

??? Recursion sits inside several patterns — how do they differ?
Same engine, one extra habit each: **DFS** = recurse over neighbors, mark visited so you don't
loop. **Backtracking** = recurse over choices but **undo** each after the call (choose → explore
→ un-choose). **Divide & conquer** = split into **independent** halves, recurse, and **combine**
(merge sort, quickselect). **Top-down DP** = recursion whose subproblems **overlap**, so you
**memoize**. Litmus test on the recursion tree: independent branches → divide & conquer; repeated
arguments → DP; try/undo each option → backtracking; explore everything reachable → DFS.
