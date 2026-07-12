# Stacks & Queues — order-restricted access

> Both are sequences that restrict *where* you add and remove — and that restriction is exactly
> what makes them useful. A **stack** is LIFO (last in, first out); a **queue** is FIFO (first in,
> first out). A **deque** allows both ends. All operations are O(1).

---

![Stack (LIFO) vs queue (FIFO), with the allowed ends highlighted](images/ds-stack-queue.svg)

## Stack (LIFO)

Push and pop happen at the **same end** (the "top"). Think of a stack of plates. It's the natural
model for anything with **nesting or "most recent first"** semantics: the function call stack,
undo history, depth-first search, matching brackets, evaluating expressions.

| Operation | Cost |
|---|---|
| push / pop / peek | O(1) |
| search | O(n) |

```text
push(x):  arr.append(x)
pop():    return arr.pop()          # removes & returns the top
peek():   return arr[-1]            # look without removing
```

**Implementations:** Python — a plain `list` (`append` / `pop`). C++ — `std::stack` (or a
`vector`). You rarely need a linked list for this.

### The monotonic stack

A stack you keep **sorted** (increasing or decreasing) by popping violators before you push. It
answers *"next greater / previous smaller element"* for every position in **O(n) total** — each
element is pushed and popped at most once.

```text
# next greater element to the right, for each index
stack = []                          # holds indices, values decreasing
for i in range(n):
    while stack and nums[stack[-1]] < nums[i]:
        j = stack.pop()
        answer[j] = nums[i]         # nums[i] is j's next-greater
    stack.append(i)
```

:::solution Valid Parentheses — the canonical stack
```python
def is_valid(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for c in s:
        if c in pairs:                          # closing bracket
            if not stack or stack.pop() != pairs[c]:
                return False
        else:
            stack.append(c)                     # opening bracket
    return not stack                            # nothing left unmatched
```
```cpp
bool isValid(const string& s) {
    unordered_map<char,char> pairs{{')','('},{']','['},{'}','{'}};
    stack<char> st;
    for (char c : s) {
        if (pairs.count(c)) {
            if (st.empty() || st.top() != pairs[c]) return false;
            st.pop();
        } else st.push(c);
    }
    return st.empty();
}
```
:::

:::solution Daily Temperatures — monotonic stack, O(n)
```python
def daily_temperatures(temps):
    ans = [0] * len(temps)
    stack = []                      # indices, temps decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j          # days until a warmer temp
        stack.append(i)
    return ans
```
```cpp
vector<int> dailyTemperatures(vector<int>& temps) {
    int n = temps.size();
    vector<int> ans(n, 0);
    stack<int> st;                  // indices, temps decreasing
    for (int i = 0; i < n; ++i) {
        while (!st.empty() && temps[st.top()] < temps[i]) {
            int j = st.top(); st.pop();
            ans[j] = i - j;
        }
        st.push(i);
    }
    return ans;
}
```
:::

---

## Queue (FIFO)

Add at the **back**, remove from the **front**. The model for **fair, in-order processing**: the
BFS frontier, task/print scheduling, buffering a producer→consumer stream.

| Operation | Cost |
|---|---|
| enqueue (push back) | O(1) |
| dequeue (pop front) | O(1) |
| peek front | O(1) |

> **Critical gotcha:** in Python, do **not** use `list.pop(0)` as a dequeue — it shifts every
> remaining element and is **O(n)**. Use `collections.deque` (`append` / `popleft`, both O(1)).
> In C++, `std::queue`.

### Deque — a double-ended queue

Push/pop at **both** ends in O(1). It generalizes both structures and powers the **sliding-window
maximum** (keep a decreasing deque of candidate indices) and fixed-size **ring buffers**.

```text
# sliding-window maximum: deque holds indices, values decreasing
dq = deque()
for i in range(n):
    while dq and nums[dq[-1]] <= nums[i]:   # pop smaller from the back
        dq.pop()
    dq.append(i)
    if dq[0] <= i - k:                      # drop index that left the window
        dq.popleft()
    if i >= k - 1:
        output.append(nums[dq[0]])          # front = window max
```

:::solution Implement a Queue using two Stacks — amortized O(1)
```python
class MyQueue:
    def __init__(self):
        self.inb, self.outb = [], []        # in-box, out-box

    def push(self, x):
        self.inb.append(x)

    def _shift(self):
        if not self.outb:                   # reverse in -> out, once
            while self.inb:
                self.outb.append(self.inb.pop())

    def pop(self):
        self._shift()
        return self.outb.pop()

    def peek(self):
        self._shift()
        return self.outb[-1]

    def empty(self):
        return not self.inb and not self.outb
```
```cpp
class MyQueue {
    stack<int> inb, outb;
    void shift() {
        if (outb.empty())
            while (!inb.empty()) { outb.push(inb.top()); inb.pop(); }
    }
public:
    void push(int x) { inb.push(x); }
    int pop()  { shift(); int v = outb.top(); outb.pop(); return v; }
    int peek() { shift(); return outb.top(); }
    bool empty() { return inb.empty() && outb.empty(); }
};
```
:::

---

## Interview checklist

1. **Nesting / matching / "most recent" / undo / DFS** → stack.
2. **"Next greater / smaller", histogram, span** → monotonic stack, O(n).
3. **In-order / level-by-level / BFS / buffering** → queue.
4. **Window extremes, both-ends access** → deque.
5. Say **"deque, not `list.pop(0)`"** out loud — it's the classic Python complexity trap.

??? Why is each element in a monotonic-stack pass amortized O(1) despite the inner `while`?
Every element is **pushed exactly once and popped at most once** over the whole scan. The inner
`while` can pop several elements in one step, but those pops are "paid for" by earlier pushes — the
total number of push+pop operations is ≤ 2n, so the whole pass is O(n), not O(n²).

??? Implement a stack using queues, or a queue using stacks — what's the trick?
**Queue from two stacks:** push to an in-box; to pop, if the out-box is empty, pour the in-box into
it (reversing order), then pop the out-box — amortized O(1). **Stack from one queue:** after each
push, rotate the queue so the new element sits at the front (O(n) push, O(1) pop). Know which
operation you made expensive.

??? When do you need an actual linked-list-backed queue instead of an array deque?
Almost never in interviews — a `deque` (ring buffer / doubly linked list under the hood) already
gives O(1) both ends. Real systems use a linked or chunked queue mainly for **unbounded growth
without reallocation** or **lock-free concurrent** access.
