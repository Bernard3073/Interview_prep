# Stack & Monotonic Stack — common interview questions

## How it works

A **stack** is a LIFO ("last in, first out") container: you only ever touch the **top**. `push`,
`pop`, `peek`, `isEmpty`, and `size` are all **O(1)**. In Python a plain list *is* a stack —
`append` to push, `pop()` to pop, `a[-1]` to peek. Reach for it whenever the **most recent**
unresolved thing is the one you need next: matching brackets, undo/redo, DFS's explicit frontier,
expression evaluation, or "what happened just before this."

**Use when:** balanced-brackets / nesting validation, evaluating or parsing expressions (RPN,
calculators), backtracking an explicit call stack, or the **next greater/smaller element** family
(the monotonic-stack special case below).

![Stack LIFO operations and a decreasing monotonic stack resolving next-greater-element](images/lc-stack.svg)

**Pseudocode — balanced brackets (the "match the most recent open" reflex):**

```text
function isBalanced(s):
    stack ← empty
    pairs ← { ')':'(', ']':'[', '}':'{' }
    for ch in s:
        if ch is an opening bracket:
            stack.push(ch)
        else:                                 # closing bracket
            if stack empty or stack.pop() ≠ pairs[ch]:
                return false                  # mismatch or nothing to close
    return stack is empty                     # nothing left dangling
```

**Monotonic stack — the "next greater/smaller element" pattern.** Keep the stack's values in
sorted (increasing *or* decreasing) order by **popping violators before you push**. Each index is
pushed and popped **at most once → O(n)** for a whole class of problems that look `O(n²)`. Store
**indices** (not just values) when you need distances. A **decreasing** stack finds *next
greater*; an **increasing** stack finds *next smaller*.

```text
function nextGreater(a):                       # decreasing monotonic stack of indices
    res ← array of 0s, size len(a)
    stack ← empty
    for i, x in enumerate(a):
        while stack not empty and a[stack.top] < x:
            j ← stack.pop()
            res[j] ← i − j                     # x at i is j's next-greater
        stack.push(i)
    return res                                 # unresolved indices keep their 0
```

Same skeleton powers **Next Greater Element**, **Largest Rectangle in Histogram**, **Trapping
Rain Water**, and stock-span problems — swap the comparison and what you record on each pop.

> **In-site drill:** the monotonic-deque cousin, **Sliding Window Maximum**, runs in the editor →
> [open it](practice.html?p=sliding-window-maximum). Below are additional classics.

---

## 1. Valid Parentheses

Are the brackets balanced and correctly nested? Push openers; on a closer, the top must be its
matching opener — otherwise it's invalid. Valid iff the stack ends empty. **O(n)** time.

:::solution
```python
def is_valid(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch not in pairs:
            stack.append(ch)                # opener → push
        elif not stack or stack.pop() != pairs[ch]:
            return False                     # closer with wrong/absent match
    return not stack                          # nothing left dangling
```
```cpp
#include <string>
#include <stack>
#include <unordered_map>

bool isValid(std::string s) {
    std::unordered_map<char, char> pairs = {{')','('}, {']','['}, {'}','{'}};
    std::stack<char> st;
    for (char ch : s) {
        if (!pairs.count(ch)) st.push(ch);
        else {
            if (st.empty() || st.top() != pairs[ch]) return false;
            st.pop();
        }
    }
    return st.empty();
}
```
:::

---

## 2. Daily Temperatures

For each day, how many days until a warmer one. A **decreasing** monotonic stack of indices:
when today is warmer than the top, pop and record the distance. Unresolved days keep 0.
**O(n)** time.

:::solution
```python
def daily_temperatures(temps: list[int]) -> list[int]:
    res = [0] * len(temps)
    stack = []                              # indices, temps decreasing down the stack
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j                  # i is the first warmer day for day j
        stack.append(i)
    return res
```
```cpp
#include <vector>
#include <stack>

std::vector<int> dailyTemperatures(std::vector<int>& temps) {
    std::vector<int> res(temps.size(), 0);
    std::stack<int> st;                     // indices, decreasing temps
    for (int i = 0; i < (int)temps.size(); i++) {
        while (!st.empty() && temps[st.top()] < temps[i]) {
            int j = st.top(); st.pop();
            res[j] = i - j;
        }
        st.push(i);
    }
    return res;
}
```
:::

---

## 3. Largest Rectangle in Histogram

Largest axis-aligned rectangle under the bar heights. An **increasing** monotonic stack of
indices: when a shorter bar appears, pop taller bars and compute each popped bar's maximal
rectangle (its height × the width between the new boundary and the previous stack entry). A
sentinel `0` at the end flushes the stack. **O(n)** time.

:::solution
```python
def largest_rectangle_area(heights: list[int]) -> int:
    stack = []                              # indices, increasing heights
    best = 0
    for i, h in enumerate(heights + [0]):   # trailing 0 flushes the stack
        while stack and heights[stack[-1]] >= h:
            top = stack.pop()
            height = heights[top]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return best
```
```cpp
#include <vector>
#include <stack>
#include <algorithm>

int largestRectangleArea(std::vector<int>& heights) {
    heights.push_back(0);                   // sentinel flushes the stack
    std::stack<int> st;
    int best = 0;
    for (int i = 0; i < (int)heights.size(); i++) {
        while (!st.empty() && heights[st.top()] >= heights[i]) {
            int h = heights[st.top()]; st.pop();
            int width = st.empty() ? i : i - st.top() - 1;
            best = std::max(best, h * width);
        }
        st.push(i);
    }
    heights.pop_back();
    return best;
}
```
:::

---

## 4. Min Stack

A stack with `push`/`pop`/`top`/`getMin` all `O(1)`. Keep an **auxiliary stack of running
minima** alongside the data stack; each entry records the min of everything at or below it.

:::solution
```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.mins = []                      # mins[i] = min of stack[0..i]

    def push(self, val: int) -> None:
        self.stack.append(val)
        self.mins.append(val if not self.mins else min(val, self.mins[-1]))

    def pop(self) -> None:
        self.stack.pop(); self.mins.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.mins[-1]
```
```cpp
#include <stack>
#include <algorithm>

class MinStack {
    std::stack<int> stk, mins;
public:
    void push(int val) {
        stk.push(val);
        mins.push(mins.empty() ? val : std::min(val, mins.top()));
    }
    void pop() { stk.pop(); mins.pop(); }
    int top() { return stk.top(); }
    int getMin() { return mins.top(); }
};
```
:::

---

??? Why is a monotonic-stack scan O(n) despite the inner while-loop?
Because each index is **pushed exactly once and popped at most once** across the entire scan. The
inner `while` can do many pops in one iteration, but the total number of pops over all iterations
can't exceed the total number of pushes (`n`). So the combined work is `O(n)` — an amortized
argument, not a per-step one.

??? Decreasing vs. increasing monotonic stack — which finds what?
A **decreasing** stack (values shrink toward the top) resolves **next greater element**: a new
larger value pops everything smaller, and it's their next-greater. An **increasing** stack
resolves **next smaller element** and underlies Largest Rectangle in Histogram. Store **indices**
rather than values whenever the answer is a distance or width.
