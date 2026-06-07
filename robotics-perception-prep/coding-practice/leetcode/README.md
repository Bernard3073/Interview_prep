# LeetCode Practice Guide (robotics-perception flavored)

> 💡 **Solve these in the site.** Open the tracker, click a LeetCode problem, and
> you'll land in the in-site editor (`practice.html`) where you can write Python or
> C++ and run it against test cases — no need to leave for leetcode.com. All 24
> problems below are wired up in-site.


You don't need 500 problems. You need fluency in the **patterns** that show up in
perception/robotics coding rounds. Each week's problems (in the tracker) target a
pattern below. Do them in the language you'll interview in (Python for speed, C++
if the role is C++-heavy).

## The patterns that actually come up

| Pattern | Why it matters for robotics | Representative problems |
|---|---|---|
| **Arrays / hashing / two-pointer** | data wrangling, dedup, windows over streams | Two Sum, Product of Array Except Self |
| **Matrix manipulation** | images, occupancy grids, transforms | Rotate Image, Spiral Matrix, Set Matrix Zeroes |
| **Grid BFS/DFS / connected components** | image segmentation, blob labeling, occupancy maps | Number of Islands, Pacific Atlantic, Maximal Square |
| **Sliding window / streams** | sensor stream processing, moving stats | Moving Average, Sliding Window Maximum |
| **Heaps / top-k** | nearest neighbors, k-closest points | K Closest Points to Origin, Find Median from Stream |
| **Binary search** | timestamp lookup, thresholding | Find K Closest Elements, search-on-answer |
| **Graphs (topo / shortest path / union-find)** | pose graphs, planning, factor graphs, TF trees | Course Schedule, Network Delay, Graph Valid Tree |
| **Geometry** | everything spatial | Max Points on a Line, K Closest Points |
| **Intervals** | time synchronization, sensor windows | Merge Intervals |
| **Design / data structures** | ring buffers, caches, time-keyed stores | LRU Cache, Circular Queue, Time-Based KV Store |
| **DP** | matching, alignment, cost volumes | Maximum Subarray, Maximal Square |

## How to practice (per problem)
1. Brute force out loud first — state it, give its complexity.
2. Find the bottleneck → pick the pattern that removes it.
3. Code it cleanly; handle empty/single/duplicate edge cases.
4. State final time & space complexity.
5. If stuck > 25 min, read the solution, then **re-solve from scratch the next day.**

## Suggested volume for an 8-week plan
- ~3 problems/week from the tracker list (24 total) = the backbone.
- Add 2–3 extra of the *same pattern* each week if you have time.
- Final 2 weeks: timed mixed sets (2 mediums in 45 min) to simulate the round.

## Robotics-specific coding (the other half)
The `../robotics/` folder has the domain coding problems — convolution, RANSAC,
Kalman, ICP, NMS/mAP, etc. These are *just as likely* in a perception interview as
LeetCode. Treat them with the same rigor: implement from scratch, then check
against the reference + tests.

> Tip: many "robotics coding" questions are a LeetCode pattern in disguise —
> time sync = merge intervals/two-pointer, ring buffer = circular queue,
> nearest landmark = k-closest/heap, pose graph = graph + linear solve.
