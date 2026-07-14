# Week 20 — Aurora: Company Problem Set

> The coding questions reported for **Aurora** interviews (sourced from
> interviewsolver.com). Every one is solvable in the in-site editor in Python or
> C++ — see **💻 Practice for this week** below. This page is the map: what the set
> tells you, how to group the problems, and the four that are adapted so the
> exact-match judge works.

---

## What this set signals

Aurora builds the **Aurora Driver** for self-driving trucks, and the reported set
is a **generalist software bar** rather than a robotics-math gauntlet — the
robotics reasoning shows up in the system-design and behavioral rounds, not here.
The mix is stacks and **monotonic stacks**, heaps, BFS on grids, backtracking, and
DP: standard LeetCode Medium territory with four Easy warmers and a real Hard tier.
The signal to optimize for:

- **Monotonic-stack fluency.** Three of the set (Largest Rectangle, Daily
  Temperatures, Asteroid Collision) are the same reflex: keep a stack that stays
  sorted, and resolve elements the moment the invariant would break. If one of
  these feels slow, that's the highest-leverage thing to drill.
- **Clean coding + edge cases.** Easy/Medium problems are judged on crispness:
  off-by-one in binary search (Kth Missing, Find K Closest), overflow/clamping in
  `atoi`, empty inputs, ties in a heap. Say the brute force and its complexity
  first, then optimize.
- **Design under a constraint.** Max Stack and O(1) Insert/Delete/GetRandom test
  whether you pick the right structures for the required latency — narrate the
  invariant (which op must stay O(1), and what bookkeeping buys it).

---

## Group the problems by pattern

| Pattern | Problems | Watch for |
|---|---|---|
| **Monotonic stack** | Largest Rectangle in Histogram · Daily Temperatures · Asteroid Collision | Keep indices, not values; pop while the new element breaks the order. Histogram width = `i - stack[-1] - 1` after the pop. |
| **Heap / interval sweep** | Find Median from Data Stream · Meeting Rooms II · Kth Smallest in a Sorted Matrix | Median = two balanced heaps; Meeting Rooms = min-heap of end times, its size is rooms in use; Kth-Smallest is **binary search on the value**. |
| **BFS on a grid** | Shortest Path in Binary Matrix · Rotting Oranges | 8-directional vs 4-directional; multi-source BFS (all rotten start in the queue at level 0). |
| **Backtracking** | N-Queens · Subsets II | N-Queens tracks columns + both diagonals (`r-c`, `r+c`); Subsets II sorts first and skips `a[i]==a[i-1]` **at the same depth** to dedupe. |
| **Dynamic programming** | Coin Change II · K Inverse Pairs Array | Coin Change II puts the **coin loop outside** so order doesn't double-count; K Inverse Pairs is a sliding prefix-sum window, mod 1e9+7. |
| **String / parsing** | String to Integer (atoi) · Reverse Words · String Compression · Merge Strings Alternately · Ransom Note | atoi: skip spaces → sign → digits → clamp to 32-bit. Reverse Words: collapse runs of spaces. |
| **Trees** | Check Completeness of a Binary Tree | Level-order BFS **including nulls**; once a gap appears, no real node may follow. |
| **Design / elimination** | Max Stack · Insert/Delete/GetRandom O(1) · Find the Celebrity | Max Stack's `popMax` removes the **top-most** maximum; Celebrity is one elimination pass then one verification pass, O(n). |
| **Greedy / binary search** | Jump Game · Reorganize String · Find K Closest Elements | Already in the bank from weeks 2–8; included here for completeness. |

---

## The four adapted problems (deterministic judging)

The in-site judge is **exact stdin→stdout**, so problems that enumerate solutions
or draw randomly are reformulated. The core skill is unchanged; only the output
differs. Each problem statement flags this too.

- **N-Queens** → prints the **number of distinct solutions** (the N-Queens II
  count) instead of every board. Same backtracking search; you increment a counter
  at a full placement rather than serializing the board.
- **Word Ladder II** → prints the **number of distinct shortest transformation
  sequences** (0 if none) instead of listing them. Same layered BFS; you
  accumulate path counts per word instead of storing predecessor lists.
- **Max Stack** → the ops are given, so it already judges deterministically; it
  prints the return value of each query op (`top` / `pop` / `peekMax` / `popMax`).
- **Insert Delete GetRandom O(1)** → the random draw is replaced by a `count x`
  query, so the judge tests the **O(1) multiset bookkeeping** (the hard part)
  rather than a random return.

> On the real interview these come back in their original form. Solve the adapted
> version here for the algorithm, then rehearse the "in original form I'd…" answer:
> for N-Queens, serialize each valid board (`.` and `Q` rows); for Word Ladder II,
> store a `word → predecessors` map during BFS and DFS backward from `endWord` to
> reconstruct every shortest path.

---

## How to work this set

1. **Untimed first pass** for coverage — hit one problem per pattern row above,
   starting with the monotonic-stack row since it repeats three times.
2. **Timed second pass** at ~25 min each on the Mediums and Hards; the Easies
   (Ransom Note, Merge Strings Alternately, Kth Missing) should be < 10.
3. Any miss → open the matching [pattern deep-dive](02-leetcode-patterns.md) and do
   its extra reps, then re-attempt.

## Resources
- Source list: interviewsolver.com/interview-questions/aurora
- Pattern reference: [02-leetcode-patterns](02-leetcode-patterns.md) and the per-pattern deep-dive subpages.
- Solve them in-site: the **💻 Practice for this week** panel below (Python or C++, no setup).
