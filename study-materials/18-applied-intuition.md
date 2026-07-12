# Week 18 — Applied Intuition: Company Problem Set

> The coding questions reported for **Applied Intuition** interviews (sourced from
> interviewsolver.com). Every one is solvable in the in-site editor in Python or
> C++ — see **💻 Practice for this week** below. This page is the map: what the set
> tells you, how to group the problems, and the three that are adapted so the
> exact-match judge works.

---

## What this set signals

Applied Intuition builds simulation and autonomy software, and the question mix is
a **generalist software bar**, not a robotics-math gauntlet. You get trees,
backtracking, DP, binary search, greedy/heap, string manipulation, plain math, and
a couple of design problems — standard LeetCode Medium territory with a few Easy
warmers and two Hard design questions. The signal to optimize for:

- **Breadth over depth.** No single pattern dominates, so shore up your weakest
  area rather than grinding one topic. Revisit [01-leetcode-patterns](01-leetcode-patterns.md)
  and the [pattern deep-dives](topic.html?t=binary-search).
- **Clean coding + edge cases.** Easy/Medium problems are judged on crispness:
  off-by-one in binary search, empty inputs, angle/overflow. Say the brute force
  and its complexity first, then optimize.
- **Design fluency.** Snake Game and the O(1) multiset test whether you can pick the
  right data structures under a latency constraint — narrate the invariant.

---

## Group the problems by pattern

| Pattern | Problems | Watch for |
|---|---|---|
| **Trees** | All Nodes Distance K · Diameter of Binary Tree | K-distance needs **parent links** (turn the tree into a graph, then BFS); diameter is DFS returning depth while tracking `max(l+r)`. |
| **Backtracking / DP** | Combination Sum · Unique Paths II | Combination Sum reuses elements (don't advance the index); Unique Paths II zeroes out obstacle cells. |
| **Binary search** | Search Insert Position · Koko Eating Bananas · Kth Smallest in a Sorted Matrix | Koko and Kth-Smallest are **binary search on the answer**, not the array — define the monotonic predicate. |
| **Greedy / heap** | Reorganize String · Construct String With Repeat Limit | Both are max-heap by frequency/char; the trick is placing a **breaker** char between runs. |
| **String / hashing** | One Swap Equal · String Compression · Rank Teams by Votes | Count mismatches / runs / per-position tallies; Rank Teams tie-breaks alphabetically. |
| **Math** | The kth Factor of n · Fraction to Recurring Decimal | Fraction: remember seen **remainders** to detect the repeating cycle. |
| **Design** | Design Snake Game · Insert/Delete/GetRandom · (Merge k Lists) | Snake = deque body + occupancy set; the tail vacates unless you just ate. |
| **Sliding window / matrix / D&C** | Longest Substring · Rotate Image · Merge k Sorted Lists | Already in the bank from weeks 2–4; included here for completeness. |

---

## The three adapted problems (deterministic judging)

The in-site judge is **exact stdin→stdout**, so problems with random or non-unique
answers are reformulated. The core skill is unchanged; only the output differs.
Each problem statement flags this too.

- **Reorganize String** → prints `true`/`false` for **feasibility** (possible iff the
  most frequent char ≤ ⌈n/2⌉). The construction is the natural follow-up.
- **Insert Delete GetRandom O(1) — Duplicates** → the random draw is replaced by a
  `count x` query, so the judge tests the **O(1) multiset bookkeeping** (the actual
  hard part) rather than a random return.
- **Design Snake Game** → already deterministic (food order and moves are given);
  it prints the **score after each move**, ending with `-1` on game over.

> On the real interview these come back in their original form. Solve the adapted
> version here for the algorithm, then rehearse the "in original form I'd…" answer:
> for Reorganize String, build the result with a max-heap placing the two most
> frequent chars each round; for GetRandom, back the multiset with a
> `value → set-of-indices` map plus a flat array for O(1) random.

---

## How to work this set

1. **Untimed first pass** for coverage — hit one problem per pattern row above.
2. **Timed second pass** at ~25 min each on the Mediums; the Easies should be < 10.
3. Any miss → open the matching [pattern deep-dive](01-leetcode-patterns.md) and do
   its extra reps, then re-attempt.

## Resources
- Source list: interviewsolver.com/interview-questions/applied-intuition
- Pattern reference: [01-leetcode-patterns](01-leetcode-patterns.md) and the per-pattern deep-dive subpages.
- Solve them in-site: the **💻 Practice for this week** panel below (Python or C++, no setup).
