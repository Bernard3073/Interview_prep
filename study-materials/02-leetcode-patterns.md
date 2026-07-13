# Week 2 — LeetCode Patterns & Core Techniques

> You don't memorize problems — you recognize **patterns**. Almost every coding-round
> question is one of a dozen techniques wearing a costume. This week is the cheat lsheet:
> when to reach for two pointers vs. a hash map, BFS vs. DFS, divide-and-conquer vs.
> dynamic programming — plus a reusable code template and the complexity for each.

---

## How to pick a technique (the decision reflex)

When you read a problem, map its *shape* to a pattern before writing code:

- **Self-similar / tree / nested / "solve a smaller version of the same problem"** → recursion (the engine under DFS, backtracking, divide & conquer, and top-down DP).
- **Sorted array / pair-sum / in-place dedup** → two pointers.
- **Contiguous subarray / substring with a constraint** → sliding window.
- **Shortest path / level-by-level / "minimum steps"** → BFS.
- **Reachability / connected components / all paths / cycles** → DFS.
- **"Sorted" + "find / smallest / search on answer"** → binary search.
- **"Split in half, combine"** (sort, count, merge) → divide and conquer.
- **Overlapping subproblems + optimal substructure** ("max/min/count ways") → DP.
- **"All combinations / permutations / subsets"** → backtracking.
- **"k largest / smallest / running median / merge k"** → heap.
- **Dynamic connectivity / grouping** → union-find.
- **"Next greater/smaller element", matching brackets, expression parsing, undo** → stack (monotonic stack).
- **"Locally optimal = globally optimal" (intervals, scheduling)** → greedy.

> Interview reflex: say the **brute force + its complexity out loud first**, name the
> bottleneck, then pick the pattern that removes it. The pattern is the answer to
> "what is too slow and why."

---

## Topic deep-dives (subpages)

Each pattern below has a **deep-dive subpage** with 3–4 *additional* common interview questions
and full **Python + C++** solutions (toggle the language with a tab on each solution). These are
deliberately *different* problems from the in-site drills and other weeks — extra reps, not
repeats.

| Pattern | Deep-dive subpage | Questions covered |
|---|---|---|
| Recursion | [Open →](topic.html?t=recursion) | Pow(x, n) · Reverse Linked List · Merge Two Sorted Lists · Fibonacci (naive vs. memoized) |
| Two pointers | [Open →](topic.html?t=two-pointers) | Valid Palindrome · Container With Most Water · Two Sum II · Move Zeroes |
| Sliding window | [Open →](topic.html?t=sliding-window) | Minimum Window Substring · Longest Repeating Char Replacement · Permutation in String · Max Consecutive Ones III |
| BFS | [Open →](topic.html?t=bfs) | Level Order Traversal · 01 Matrix · Open the Lock |
| DFS | [Open →](topic.html?t=dfs) | Clone Graph · Max Area of Island · Pacific Atlantic Water Flow |
| Binary search | [Open →](topic.html?t=binary-search) | Koko Eating Bananas · Find Minimum in Rotated Array · First & Last Position · Search a 2D Matrix |
| Divide & conquer | [Open →](topic.html?t=divide-and-conquer) | Sort an Array · Quickselect (Kth Largest) · Count of Smaller Numbers After Self |
| Dynamic programming | [Open →](topic.html?t=dynamic-programming) | House Robber · Longest Increasing Subsequence · Unique Paths · Word Break |
| Backtracking | [Open →](topic.html?t=backtracking) | Permutations · Combination Sum · Word Search |
| Heap / top-k | [Open →](topic.html?t=heap) | Kth Largest (heap) · K Closest Points · Median from Data Stream |
| Union-find | [Open →](topic.html?t=union-find) | Redundant Connection · Connected Components · Accounts Merge |
| Stack / monotonic | [Open →](topic.html?t=stack) | Valid Parentheses · Daily Temperatures · Largest Rectangle · Min Stack |
| Greedy | [Open →](topic.html?t=greedy) | Gas Station · Jump Game II · Merge Intervals · Non-overlapping Intervals |

---

## Complexity cheat sheet

| Pattern | Typical time | Space | Tell-tale phrasing |
|---|---|---|---|
| Recursion | #calls × work/call | O(depth) stack | "tree", "self-similar", "nested", "smaller subproblem" |
| Two pointers | O(n) | O(1) | "sorted", "pair/triplet", "in place" |
| Sliding window | O(n) | O(k) | "contiguous", "longest/shortest subarray" |
| BFS | O(V+E) | O(width) | "shortest", "fewest steps", "level" |
| DFS | O(V+E) | O(depth) | "reachable", "all paths", "components", "cycle" |
| Binary search | O(log n) | O(1) | "sorted", "minimize the max", "search on answer" |
| Divide & conquer | O(n log n) | O(log n)–O(n) | "sort", "count while merging", "halves" |
| Dynamic programming | states × transition | states | "max/min/count ways", "can you reach" |
| Backtracking | O(branch^depth) | O(depth) | "all combinations/permutations/subsets" |
| Heap / top-k | O(n log k) | O(k) | "k largest", "merge k", "median of stream" |
| Union-find | ~O(α(n)) | O(n) | "connected", "groups", "redundant edge" |
| Stack / monotonic stack | O(n) | O(n) | "matching brackets", "next greater/smaller", "nested" |

---

## Interview-style questions
*Click a question to reveal a model answer.*

??? When do you use BFS vs. DFS, and why does BFS give the shortest path?
Use **BFS** when you need the *shortest path / fewest steps* on an **unweighted** graph, or anything level-by-level; use **DFS** for *reachability, connected components, cycle detection, topological order, or enumerating all paths*. BFS explores in non-decreasing order of distance from the source (a queue processes all distance-`d` nodes before any distance-`d+1` node), so the first time it reaches a node is necessarily via a path with the fewest edges. DFS makes no such guarantee — it dives deep first. Both are O(V+E); BFS uses O(width) memory, DFS O(depth).

??? Two pointers vs. a hash map for the "two-sum" problem — what's the tradeoff?
On a **sorted** array, two pointers solve it in O(n) time and **O(1) space**, but you need (or pay O(n log n) to get) sorted order, and it returns *values/positions in the sorted array*. A **hash map** works on **unsorted** input in O(n) time but O(n) space, and naturally returns the *original indices* in one pass. Pick two pointers when the array is already sorted or space is tight; pick the hash map when input is unsorted and you must report original indices (the classic LeetCode "Two Sum").

??? What's the difference between divide-and-conquer and dynamic programming?
Both split a problem into subproblems. In **divide-and-conquer** the subproblems are **independent / non-overlapping** (e.g. the two halves in merge sort), so you just solve and combine. In **DP** the subproblems **overlap** — the same subproblem is reached many times — so naive recursion is exponential and you **memoize** (top-down) or **tabulate** (bottom-up) to make it polynomial. Litmus test: draw the recursion tree; if the same arguments recur, it's DP. DP also requires **optimal substructure**.

??? How do you recognize a dynamic-programming problem, and how do you design the DP?
Signals: the question asks for a **max/min/count/“is it possible”** over choices, with **overlapping subproblems** and **optimal substructure**. Design in four steps: (1) **define the state** — what `dp[i]` (or `dp[i][j]`) *means*; (2) write the **transition** from smaller states; (3) set **base cases**; (4) choose the **fill order** (and optionally compress memory). I usually first write the brute-force recursion, confirm subproblems repeat, then add memoization — converting to bottom-up only if I need the constant-factor/space win.

??? Explain "binary search on the answer." Give an example.
When the answer is a number and you can cheaply test **`feasible(x)`** — and feasibility is **monotonic** (false for small x, then true for all larger x, or vice-versa) — you binary-search the smallest/largest x instead of searching the input. Example: "minimum ship capacity to deliver all packages in D days." `feasible(cap)` = simulate loading greedily and count days ≤ D; it's monotonic in `cap`, so binary-search the smallest feasible capacity in O(n log(sum)). Same trick: "split array largest sum," "smallest divisor," "Koko eating bananas."

??? Why mark grid/graph nodes as visited on enqueue in BFS, not on dequeue?
If you only mark a node visited when you **dequeue** it, the same node can be **enqueued multiple times** before it's first processed (several neighbors push it), blowing up the queue and possibly the time complexity. Marking it **the moment you enqueue** guarantees each node enters the queue at most once, keeping BFS O(V+E). The same applies to the start node — mark it before the loop.

??? What is a monotonic stack, and how does it turn an O(n²) scan into O(n)?
A **monotonic stack** keeps its contents sorted (all-increasing or all-decreasing) by **popping every element that would break the order before pushing the new one**. It solves the "**next/previous greater or smaller element**" family: as you scan left to right, each element that finally gets a "next greater" is the one being popped when a larger value arrives. The cost argument is amortized — **every index is pushed once and popped at most once**, so the total work across the whole scan is O(n) even though there's a nested `while` loop. A *decreasing* stack (top is smallest) resolves *next greater*; an *increasing* stack resolves *next smaller*. Store **indices** rather than values when the answer is a distance (e.g. Daily Temperatures) or a width (Largest Rectangle in Histogram). It's the same core loop behind Next Greater Element, Trapping Rain Water, and stock-span.

??? When is greedy correct, and how would you justify it in an interview?
Greedy is correct only when a **locally optimal choice is provably part of some global optimum** (the "greedy-choice property") and the problem has optimal substructure. Justify it with an **exchange argument**: assume an optimal solution differs from the greedy one, then show you can swap in the greedy choice without making the solution worse — so a greedy-consistent optimum exists. Classic safe greedies: interval scheduling (earliest finish time), Huffman coding, Dijkstra. If you can't make that argument, fall back to DP, which considers all choices.

## Resources
- *Grokking the Coding Interview* — patterns-first framing (the basis of this list).
- *Elements of Programming Interviews* / *Cracking the Coding Interview* — drills per pattern.
- LeetCode "Explore" cards: Binary Search, Graph, Dynamic Programming.
- NeetCode's pattern roadmap (free) for a curated problem-per-pattern path.

---

## The one question to drill per pattern

If you do nothing else, do **one canonical question per pattern** until it's automatic.
These are the highest-frequency interview questions for each technique (and deliberately
*don't* repeat any problem from other weeks). **Every "most-asked" question below is
solvable right here in the in-site editor** (Python or C++) — use the links, or the
"💻 Practice for this week" panel. The "good second" links go out to leetcode.com.

| Pattern | Most-asked question (solve in-site) | Difficulty | Good second (leetcode.com) |
|---|---|---|---|
| Two pointers | [3Sum](practice.html?p=3sum) | Medium | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) |
| Sliding window | [Longest Substring Without Repeating Characters](practice.html?p=longest-substring-no-repeat) | Medium | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) |
| BFS | [Rotting Oranges](practice.html?p=rotting-oranges) | Medium | [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) |
| DFS / topo sort | [Course Schedule II](practice.html?p=course-schedule-ii) | Medium | [Clone Graph](https://leetcode.com/problems/clone-graph/) |
| Binary search | [Search in Rotated Sorted Array](practice.html?p=search-in-rotated-sorted-array) | Medium | [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) (search-on-answer) |
| Divide & conquer | [Merge k Sorted Lists](practice.html?p=merge-k-sorted-lists) | Hard | [Sort an Array](https://leetcode.com/problems/sort-an-array/) (merge sort) |
| Dynamic programming | [Coin Change](practice.html?p=coin-change) | Medium | [House Robber](https://leetcode.com/problems/house-robber/) · [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) |
| Backtracking | [Subsets](practice.html?p=subsets) | Medium | [Combination Sum](https://leetcode.com/problems/combination-sum/) · [Word Search](https://leetcode.com/problems/word-search/) |
| Heap / top-k | [Top K Frequent Elements](practice.html?p=top-k-frequent) | Medium | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) |
| Union-find | [Number of Provinces](practice.html?p=number-of-provinces) | Medium | [Redundant Connection](https://leetcode.com/problems/redundant-connection/) |
| Stack / monotonic | [Sliding Window Maximum](practice.html?p=sliding-window-maximum) (monotonic deque) | Hard | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) · [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) |
| Greedy | [Jump Game](practice.html?p=jump-game) | Medium | [Gas Station](https://leetcode.com/problems/gas-station/) |

> Note: [Clone Graph](https://leetcode.com/problems/clone-graph/) is the other classic DFS
> question, but "did you actually deep-copy the graph?" can't be checked through
> stdin/stdout, so the in-site DFS drill is **Course Schedule II** (topological sort)
> instead — study Clone Graph on leetcode.com.

> 💡 Every in-site drill above runs on real CPython / g++ in the editor with verified test cases —
> write the brute force, name the bottleneck, then code the pattern. For more reps on the
> same patterns, other weeks also have Two Sum, Number of Islands, Word Ladder, Course
> Schedule, Maximum Subarray, and Maximal Square in-site.
