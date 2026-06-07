#!/usr/bin/env python3
"""Generate problems.js for the in-site LeetCode practice page.

Each problem is an stdin->stdout task so one judge works for both Python and C++.
Reference solutions here produce the *expected* outputs (run locally so the test
cases are guaranteed correct). C++ starters are compile-checked with g++.

Run:  python3 gen_problems.py
"""
import io, json, subprocess, sys, tempfile, os, contextlib

PROBLEMS = []

def add(**kw):
    PROBLEMS.append(kw)

def run_ref(fn, inp):
    """Run a reference fn that reads stdin and writes stdout; return output text."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        old = sys.stdin
        sys.stdin = io.StringIO(inp)
        try:
            fn()
        finally:
            sys.stdin = old
    return out.getvalue()

# ----------------------------------------------------------------------------
# Reference solutions (read stdin, print stdout)
# ----------------------------------------------------------------------------
def ref_two_sum():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); arr = list(map(int, d[1:1+n])); target = int(d[1+n])
    seen = {}
    for i, x in enumerate(arr):
        if target - x in seen:
            print(seen[target-x], i); return
        seen[x] = i

def ref_max_subarray():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); arr = list(map(int, d[1:1+n]))
    best = cur = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x); best = max(best, cur)
    print(best)

def ref_product_except_self():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n]))
    res = [1]*n
    p = 1
    for i in range(n):
        res[i] = p; p *= a[i]
    p = 1
    for i in range(n-1, -1, -1):
        res[i] *= p; p *= a[i]
    print(*res)

def ref_rotate_image():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); vals = list(map(int, d[1:1+n*n]))
    m = [vals[i*n:(i+1)*n] for i in range(n)]
    r = [[m[n-1-j][i] for j in range(n)] for i in range(n)]
    for row in r: print(*row)

def ref_spiral():
    import sys
    d = sys.stdin.read().split()
    rows = int(d[0]); cols = int(d[1]); vals = list(map(int, d[2:2+rows*cols]))
    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]
    res = []
    top, bot, left, right = 0, rows-1, 0, cols-1
    while top <= bot and left <= right:
        for c in range(left, right+1): res.append(m[top][c])
        top += 1
        for r in range(top, bot+1): res.append(m[r][right])
        right -= 1
        if top <= bot:
            for c in range(right, left-1, -1): res.append(m[bot][c])
            bot -= 1
        if left <= right:
            for r in range(bot, top-1, -1): res.append(m[r][left])
            left += 1
    print(*res)

def ref_num_islands():
    import sys
    lines = sys.stdin.read().split('\n')
    rows, cols = map(int, lines[0].split())
    g = [list(lines[1+i].strip()) for i in range(rows)]
    cnt = 0
    def dfs(r, c):
        stack = [(r, c)]
        while stack:
            x, y = stack.pop()
            if 0 <= x < rows and 0 <= y < cols and g[x][y] == '1':
                g[x][y] = '0'
                stack += [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    for i in range(rows):
        for j in range(cols):
            if g[i][j] == '1':
                cnt += 1; dfs(i, j)
    print(cnt)

def ref_image_smoother():
    import sys
    d = sys.stdin.read().split()
    rows = int(d[0]); cols = int(d[1]); vals = list(map(int, d[2:2+rows*cols]))
    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]
    out = []
    for i in range(rows):
        row = []
        for j in range(cols):
            s = c = 0
            for x in (i-1, i, i+1):
                for y in (j-1, j, j+1):
                    if 0 <= x < rows and 0 <= y < cols:
                        s += m[x][y]; c += 1
            row.append(s // c)
        out.append(row)
    for row in out: print(*row)

def ref_k_closest():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); pts = []
    idx = 1
    for _ in range(n):
        x = int(d[idx]); y = int(d[idx+1]); idx += 2; pts.append((x, y))
    k = int(d[idx])
    pts.sort(key=lambda p: (p[0]**2 + p[1]**2, p[0], p[1]))
    for x, y in pts[:k]: print(x, y)

def ref_max_points():
    import sys
    from math import gcd
    d = sys.stdin.read().split()
    n = int(d[0]); pts = []
    idx = 1
    for _ in range(n):
        pts.append((int(d[idx]), int(d[idx+1]))); idx += 2
    if n <= 2:
        print(n); return
    best = 1
    for i in range(n):
        slopes = {}
        for j in range(n):
            if i == j: continue
            dx = pts[j][0]-pts[i][0]; dy = pts[j][1]-pts[i][1]
            g = gcd(dx, dy) or 1
            dx //= g; dy //= g
            if dx < 0 or (dx == 0 and dy < 0): dx, dy = -dx, -dy
            slopes[(dx, dy)] = slopes.get((dx, dy), 1) + 1
            best = max(best, slopes[(dx, dy)])
    print(best)

def ref_moving_average():
    import sys
    from collections import deque
    d = sys.stdin.read().split()
    size = int(d[0]); m = int(d[1]); vals = list(map(int, d[2:2+m]))
    q = deque(); s = 0
    for v in vals:
        q.append(v); s += v
        if len(q) > size: s -= q.popleft()
        print("%.5f" % (s/len(q)))

def ref_sliding_window_max():
    import sys
    from collections import deque
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n])); k = int(d[1+n])
    dq = deque(); res = []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x: dq.pop()
        dq.append(i)
        if dq[0] <= i-k: dq.popleft()
        if i >= k-1: res.append(a[dq[0]])
    print(*res)

def ref_course_schedule():
    import sys
    from collections import deque
    d = sys.stdin.read().split()
    n = int(d[0]); e = int(d[1])
    adj = [[] for _ in range(n)]; indeg = [0]*n
    idx = 2
    for _ in range(e):
        a = int(d[idx]); b = int(d[idx+1]); idx += 2
        adj[b].append(a); indeg[a] += 1
    q = deque([i for i in range(n) if indeg[i] == 0]); seen = 0
    while q:
        u = q.popleft(); seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    print("true" if seen == n else "false")

def ref_network_delay():
    import sys, heapq
    d = sys.stdin.read().split()
    n = int(d[0]); m = int(d[1]); k = int(d[2])
    adj = [[] for _ in range(n+1)]
    idx = 3
    for _ in range(m):
        u = int(d[idx]); v = int(d[idx+1]); w = int(d[idx+2]); idx += 3
        adj[u].append((v, w))
    dist = [float('inf')]*(n+1); dist[k] = 0
    pq = [(0, k)]
    while pq:
        dd, u = heapq.heappop(pq)
        if dd > dist[u]: continue
        for v, w in adj[u]:
            if dd + w < dist[v]:
                dist[v] = dd + w; heapq.heappush(pq, (dist[v], v))
    ans = max(dist[1:n+1])
    print(ans if ans != float('inf') else -1)

def ref_maximal_square():
    import sys
    lines = sys.stdin.read().split('\n')
    rows, cols = map(int, lines[0].split())
    g = [lines[1+i].strip() for i in range(rows)]
    dp = [[0]*(cols+1) for _ in range(rows+1)]
    best = 0
    for i in range(1, rows+1):
        for j in range(1, cols+1):
            if g[i-1][j-1] == '1':
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
                best = max(best, dp[i][j])
    print(best*best)

def ref_word_ladder():
    import sys
    from collections import deque, defaultdict
    lines = [l for l in sys.stdin.read().split('\n')]
    begin = lines[0].strip(); end = lines[1].strip()
    cnt = int(lines[2]); words = set(lines[3+i].strip() for i in range(cnt))
    if end not in words:
        print(0); return
    q = deque([(begin, 1)]); words.discard(begin)
    while q:
        w, steps = q.popleft()
        if w == end:
            print(steps); return
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + c + w[i+1:]
                if nw in words:
                    words.discard(nw); q.append((nw, steps+1))
    print(0)

def ref_merge_intervals():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); iv = []
    idx = 1
    for _ in range(n):
        iv.append((int(d[idx]), int(d[idx+1]))); idx += 2
    iv.sort()
    res = []
    for s, e in iv:
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    for s, e in res: print(s, e)

def ref_set_matrix_zeroes():
    import sys
    d = sys.stdin.read().split()
    rows = int(d[0]); cols = int(d[1]); vals = list(map(int, d[2:2+rows*cols]))
    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]
    zr, zc = set(), set()
    for i in range(rows):
        for j in range(cols):
            if m[i][j] == 0: zr.add(i); zc.add(j)
    for i in range(rows):
        for j in range(cols):
            if i in zr or j in zc: m[i][j] = 0
    for row in m: print(*row)

def ref_pacific_atlantic():
    import sys
    from collections import deque
    d = sys.stdin.read().split()
    m = int(d[0]); n = int(d[1]); vals = list(map(int, d[2:2+m*n]))
    h = [vals[i*n:(i+1)*n] for i in range(m)]
    def bfs(starts):
        seen = set(starts); dq = deque(starts)
        while dq:
            r, c = dq.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < m and 0 <= nc < n and (nr,nc) not in seen and h[nr][nc] >= h[r][c]:
                    seen.add((nr,nc)); dq.append((nr,nc))
        return seen
    pac = [(r,0) for r in range(m)] + [(0,c) for c in range(n)]
    atl = [(r,n-1) for r in range(m)] + [(m-1,c) for c in range(n)]
    for r, c in sorted(bfs(pac) & bfs(atl)):
        print(r, c)

def ref_find_k_closest():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n])); k = int(d[1+n]); x = int(d[2+n])
    lo, hi = 0, n - k
    while lo < hi:
        mid = (lo + hi) // 2
        if x - a[mid] > a[mid+k] - x:
            lo = mid + 1
        else:
            hi = mid
    print(*a[lo:lo+k])

def ref_find_median():
    import sys, heapq
    d = sys.stdin.read().split()
    idx = 0; q = int(d[idx]); idx += 1
    lo, hi = [], []   # lo: max-heap (negated), hi: min-heap
    out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "add":
            x = int(d[idx]); idx += 1
            heapq.heappush(lo, -x)
            heapq.heappush(hi, -heapq.heappop(lo))
            if len(hi) > len(lo):
                heapq.heappush(lo, -heapq.heappop(hi))
        else:
            med = -lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2
            out.append("%.1f" % med)
    print("\n".join(out))

def ref_graph_valid_tree():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); m = int(d[1])
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    idx = 2; ok = True; edges = 0
    for _ in range(m):
        u = int(d[idx]); v = int(d[idx+1]); idx += 2
        ru, rv = find(u), find(v)
        if ru == rv: ok = False
        else: parent[ru] = rv
        edges += 1
    roots = len({find(i) for i in range(n)})
    print("true" if (ok and edges == n-1 and roots == 1) else "false")

def ref_lru_cache():
    import sys
    from collections import OrderedDict
    d = sys.stdin.read().split()
    idx = 0; cap = int(d[idx]); idx += 1; q = int(d[idx]); idx += 1
    cache = OrderedDict(); out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "put":
            kk = int(d[idx]); vv = int(d[idx+1]); idx += 2
            if kk in cache: cache.move_to_end(kk)
            cache[kk] = vv
            if len(cache) > cap: cache.popitem(last=False)
        else:
            kk = int(d[idx]); idx += 1
            if kk in cache:
                cache.move_to_end(kk); out.append(str(cache[kk]))
            else:
                out.append("-1")
    print("\n".join(out))

def ref_circular_queue():
    import sys
    d = sys.stdin.read().split()
    idx = 0; k = int(d[idx]); idx += 1; q = int(d[idx]); idx += 1
    buf = [0]*k; head = 0; count = 0; out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "enQueue":
            x = int(d[idx]); idx += 1
            if count == k: out.append("false")
            else: buf[(head+count) % k] = x; count += 1; out.append("true")
        elif cmd == "deQueue":
            if count == 0: out.append("false")
            else: head = (head+1) % k; count -= 1; out.append("true")
        elif cmd == "Front":
            out.append(str(buf[head]) if count else "-1")
        elif cmd == "Rear":
            out.append(str(buf[(head+count-1) % k]) if count else "-1")
        elif cmd == "isEmpty":
            out.append("true" if count == 0 else "false")
        elif cmd == "isFull":
            out.append("true" if count == k else "false")
    print("\n".join(out))

def ref_time_map():
    import sys, bisect
    d = sys.stdin.read().split()
    idx = 0; q = int(d[idx]); idx += 1
    store = {}; out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "set":
            key = d[idx]; val = d[idx+1]; ts = int(d[idx+2]); idx += 3
            store.setdefault(key, ([], []))
            store[key][0].append(ts); store[key][1].append(val)
        else:
            key = d[idx]; ts = int(d[idx+1]); idx += 2
            if key in store:
                pos = bisect.bisect_right(store[key][0], ts) - 1
                out.append(store[key][1][pos] if pos >= 0 else "")
            else:
                out.append("")
    print("\n".join(out))

# ----------------------------------------------------------------------------
# Problem definitions
# ----------------------------------------------------------------------------
def P(id, title, diff, pattern, week, statement, infmt, outfmt, ref, tests, py, cpp):
    samples = [{"input": t[0], "expected": run_ref(ref, t[0]), "sample": t[1]} for t in tests]
    add(id=id, title=title, diff=diff, pattern=pattern, week=week, statement=statement,
        inputFormat=infmt, outputFormat=outfmt, tests=samples,
        starter={"python": py, "cpp": cpp})

PY_HEAD = "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n"
CPP_HEAD = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n"

P("two-sum", "Two Sum", "Easy", "Arrays / Hashing", 1,
  "<p>Given an array of integers and a target, return the <b>indices</b> (0-based) of the two numbers that add up to the target. Exactly one solution exists; return the indices in ascending order.</p>",
  "Line 1: n. Line 2: n integers. Line 3: target.",
  "The two indices, space-separated, ascending.",
  ref_two_sum,
  [("4\n2 7 11 15\n9\n", True), ("3\n3 2 4\n6\n", True), ("2\n3 3\n6\n", False), ("5\n-1 -2 -3 -4 -5\n-8\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    target = int(data[1+n])\n    # TODO: print the two indices\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int target; cin >> target;\n    // TODO: print the two indices\n    return 0;\n}\n"),

P("maximum-subarray", "Maximum Subarray", "Medium", "DP / Kadane", 1,
  "<p>Find the contiguous subarray with the largest sum and return that sum.</p>",
  "Line 1: n. Line 2: n integers.",
  "The maximum subarray sum.",
  ref_max_subarray,
  [("9\n-2 1 -3 4 -1 2 1 -5 4\n", True), ("1\n1\n", True), ("5\n5 4 -1 7 8\n", False), ("4\n-3 -2 -5 -1\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    # TODO: print the maximum subarray sum\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<long long> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print the maximum subarray sum\n    return 0;\n}\n"),

P("product-except-self", "Product of Array Except Self", "Medium", "Arrays / Prefix", 1,
  "<p>Return an array where each element is the product of all the others, <b>without using division</b>. O(n) time.</p>",
  "Line 1: n. Line 2: n integers.",
  "n integers (the answer), space-separated.",
  ref_product_except_self,
  [("4\n1 2 3 4\n", True), ("5\n-1 1 0 -3 3\n", True), ("2\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    # TODO: print the result array\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<long long> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print the result array\n    return 0;\n}\n"),

P("rotate-image", "Rotate Image", "Medium", "Matrix", 2,
  "<p>Rotate an n×n matrix by 90° <b>clockwise</b> and print the result.</p>",
  "Line 1: n. Next n lines: n integers each.",
  "The rotated matrix, n lines of n integers.",
  ref_rotate_image,
  [("3\n1 2 3\n4 5 6\n7 8 9\n", True), ("2\n1 2\n3 4\n", True), ("1\n7\n", False)],
  PY_HEAD + "    n = int(data[0])\n    vals = list(map(int, data[1:1+n*n]))\n    m = [vals[i*n:(i+1)*n] for i in range(n)]\n    # TODO: rotate 90 deg clockwise and print\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<vector<int>> m(n, vector<int>(n));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: rotate 90 deg clockwise and print\n    return 0;\n}\n"),

P("spiral-matrix", "Spiral Matrix", "Medium", "Matrix", 2,
  "<p>Return all elements of the matrix in <b>spiral order</b> (clockwise from top-left).</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "All elements in spiral order, space-separated on one line.",
  ref_spiral,
  [("3 3\n1 2 3\n4 5 6\n7 8 9\n", True), ("3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n", True), ("1 1\n5\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: print spiral order\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: print spiral order\n    return 0;\n}\n"),

P("number-of-islands", "Number of Islands", "Medium", "Grid BFS/DFS", 3,
  "<p>Count the islands in a grid of <code>'1'</code> (land) and <code>'0'</code> (water). Cells connect 4-directionally.</p>",
  "Line 1: rows cols. Next rows lines: a string of cols characters ('0'/'1').",
  "The number of islands.",
  ref_num_islands,
  [("4 5\n11110\n11010\n11000\n00000\n", True), ("3 3\n101\n010\n101\n", True), ("1 1\n0\n", False)],
  PY_HEAD.replace("split()", "split('\\n')") + "    rows, cols = map(int, data[0].split())\n    grid = [list(data[1+i].strip()) for i in range(rows)]\n    # TODO: print the island count\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<string> g(rows);\n    for (auto& s : g) cin >> s;\n    // TODO: print the island count\n    return 0;\n}\n"),

P("image-smoother", "Image Smoother", "Easy", "Matrix / Convolution", 3,
  "<p>For each cell output the floor of the average of itself and its (up to 8) neighbors — a 3×3 box filter.</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "The smoothed matrix, rows lines of cols integers.",
  ref_image_smoother,
  [("3 3\n1 1 1\n1 0 1\n1 1 1\n", True), ("2 2\n100 200\n100 200\n", True), ("1 3\n2 4 6\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: print the smoothed matrix\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: print the smoothed matrix\n    return 0;\n}\n"),

P("k-closest-points", "K Closest Points to Origin", "Medium", "Heap / Sorting", 4,
  "<p>Return the k points closest to the origin (Euclidean). Break ties by x then y so the answer is deterministic; print sorted by (distance, x, y).</p>",
  "Line 1: n. Next n lines: x y. Last line: k.",
  "k lines, each 'x y', ordered by distance then x then y.",
  ref_k_closest,
  [("3\n1 3\n-2 2\n5 8\n2\n", True), ("2\n3 3\n5 -1\n1\n", True), ("4\n0 1\n1 0\n2 2\n-1 -1\n3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = []\n    idx = 1\n    for _ in range(n):\n        pts.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    k = int(data[idx])\n    # TODO: print the k closest points\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> p(n);\n    for (auto& q : p) cin >> q.first >> q.second;\n    int k; cin >> k;\n    // TODO: print the k closest points\n    return 0;\n}\n"),

P("max-points-on-a-line", "Max Points on a Line", "Hard", "Geometry", 4,
  "<p>Given n points on a plane, return the maximum number of points that lie on the same straight line.</p>",
  "Line 1: n. Next n lines: x y.",
  "The maximum number of collinear points.",
  ref_max_points,
  [("6\n1 1\n2 2\n3 3\n1 4\n2 5\n3 6\n", True), ("3\n1 1\n3 2\n5 3\n", True), ("1\n0 0\n", False), ("4\n0 0\n1 1\n2 2\n3 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = []\n    idx = 1\n    for _ in range(n):\n        pts.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print max points on a line\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> p(n);\n    for (auto& q : p) cin >> q.first >> q.second;\n    // TODO: print max points on a line\n    return 0;\n}\n"),

P("moving-average", "Moving Average from Data Stream", "Easy", "Stream / Sliding Window", 5,
  "<p>Maintain a moving average over a sliding window of the given size. For each incoming value, print the current average (5 decimals).</p>",
  "Line 1: window size. Line 2: m (count). Line 3: m integers (the stream).",
  "m lines, each the moving average formatted to 5 decimals.",
  ref_moving_average,
  [("3\n5\n1 10 3 5 20\n", True), ("1\n3\n4 0 8\n", True), ("2\n4\n2 2 2 2\n", False)],
  PY_HEAD + "    size = int(data[0]); m = int(data[1])\n    vals = list(map(int, data[2:2+m]))\n    # TODO: print each moving average with '%.5f' % avg\n\nmain()\n",
  CPP_HEAD + "    int size, m; cin >> size >> m;\n    vector<int> v(m);\n    for (auto& x : v) cin >> x;\n    cout << fixed << setprecision(5);\n    // TODO: print each moving average\n    return 0;\n}\n"),

P("sliding-window-maximum", "Sliding Window Maximum", "Hard", "Monotonic Deque", 5,
  "<p>Given an array and window size k, output the maximum of each contiguous window.</p>",
  "Line 1: n. Line 2: n integers. Line 3: k.",
  "The window maxima, space-separated.",
  ref_sliding_window_max,
  [("8\n1 3 -1 -3 5 3 6 7\n3\n", True), ("1\n1\n1\n", True), ("6\n9 8 7 6 5 4\n2\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    k = int(data[1+n])\n    # TODO: print the window maxima\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int k; cin >> k;\n    // TODO: print the window maxima\n    return 0;\n}\n"),

P("course-schedule", "Course Schedule", "Medium", "Graph / Topo Sort", 6,
  "<p>There are numCourses courses. Each edge 'a b' means course a depends on course b. Determine if all courses can be finished (no cycle).</p>",
  "Line 1: numCourses. Line 2: e (edges). Next e lines: a b.",
  "'true' or 'false'.",
  ref_course_schedule,
  [("2\n1\n1 0\n", True), ("2\n2\n1 0\n0 1\n", True), ("4\n3\n1 0\n2 1\n3 2\n", False)],
  PY_HEAD + "    n = int(data[0]); e = int(data[1])\n    edges = []\n    idx = 2\n    for _ in range(e):\n        edges.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print 'true' or 'false'\n\nmain()\n",
  CPP_HEAD + "    int n, e; cin >> n >> e;\n    vector<pair<int,int>> edges(e);\n    for (auto& p : edges) cin >> p.first >> p.second;\n    // TODO: print \"true\" or \"false\"\n    return 0;\n}\n"),

P("network-delay-time", "Network Delay Time", "Medium", "Dijkstra", 6,
  "<p>A signal starts at node k in a network of n nodes (1-indexed). Each directed edge 'u v w' has travel time w. Return the time for all nodes to receive the signal, or -1 if impossible.</p>",
  "Line 1: n m k. Next m lines: u v w.",
  "The delay time, or -1.",
  ref_network_delay,
  [("4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 5\n", True), ("2 1 1\n1 2 1\n", True), ("2 1 2\n1 2 1\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1]); k = int(data[2])\n    edges = []\n    idx = 3\n    for _ in range(m):\n        edges.append((int(data[idx]), int(data[idx+1]), int(data[idx+2]))); idx += 3\n    # TODO: print the delay time or -1\n\nmain()\n",
  CPP_HEAD + "    int n, m, k; cin >> n >> m >> k;\n    vector<array<int,3>> edges(m);\n    for (auto& e : edges) cin >> e[0] >> e[1] >> e[2];\n    // TODO: print the delay time or -1\n    return 0;\n}\n"),

P("maximal-square", "Maximal Square", "Medium", "DP / Grid", 7,
  "<p>In a binary grid, find the largest square containing only 1s and return its <b>area</b>.</p>",
  "Line 1: rows cols. Next rows lines: a string of cols characters ('0'/'1').",
  "The area of the largest all-ones square.",
  ref_maximal_square,
  [("4 5\n10100\n10111\n11111\n10010\n", True), ("2 2\n01\n10\n", True), ("1 1\n0\n", False)],
  PY_HEAD.replace("split()", "split('\\n')") + "    rows, cols = map(int, data[0].split())\n    grid = [data[1+i].strip() for i in range(rows)]\n    # TODO: print the maximal square area\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<string> g(rows);\n    for (auto& s : g) cin >> s;\n    // TODO: print the maximal square area\n    return 0;\n}\n"),

P("word-ladder", "Word Ladder", "Hard", "BFS", 7,
  "<p>Return the number of words in the shortest transformation sequence from beginWord to endWord, changing one letter at a time, where each intermediate word must be in the word list. Return 0 if impossible. (Length counts both endpoints.)</p>",
  "Line 1: beginWord. Line 2: endWord. Line 3: count. Next count lines: the word list.",
  "The length of the shortest sequence, or 0.",
  ref_word_ladder,
  [("hit\ncog\n6\nhot\ndot\ndog\nlot\nlog\ncog\n", True), ("hit\ncog\n5\nhot\ndot\ndog\nlot\nlog\n", True), ("a\nc\n2\nb\nc\n", False)],
  "import sys\n\ndef main():\n    lines = sys.stdin.read().split('\\n')\n    begin = lines[0].strip(); end = lines[1].strip()\n    cnt = int(lines[2])\n    words = [lines[3+i].strip() for i in range(cnt)]\n    # TODO: print shortest ladder length or 0\n\nmain()\n",
  CPP_HEAD + "    string begin, end; cin >> begin >> end;\n    int cnt; cin >> cnt;\n    vector<string> words(cnt);\n    for (auto& w : words) cin >> w;\n    // TODO: print shortest ladder length or 0\n    return 0;\n}\n"),

P("merge-intervals", "Merge Intervals", "Medium", "Intervals", 8,
  "<p>Merge all overlapping intervals and print them sorted by start.</p>",
  "Line 1: n. Next n lines: start end.",
  "The merged intervals, one 'start end' per line, sorted by start.",
  ref_merge_intervals,
  [("4\n1 3\n2 6\n8 10\n15 18\n", True), ("2\n1 4\n4 5\n", True), ("3\n1 4\n0 4\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    iv = []\n    idx = 1\n    for _ in range(n):\n        iv.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print merged intervals\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> iv(n);\n    for (auto& p : iv) cin >> p.first >> p.second;\n    // TODO: print merged intervals\n    return 0;\n}\n"),

P("set-matrix-zeroes", "Set Matrix Zeroes", "Medium", "Matrix", 2,
  "<p>If an element is 0, set its entire row and column to 0 — and print the result. (Classic follow-up: do it in O(1) extra space.)</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "The modified matrix, rows lines of cols integers.",
  ref_set_matrix_zeroes,
  [("3 3\n1 1 1\n1 0 1\n1 1 1\n", True), ("3 4\n0 1 2 0\n3 4 5 2\n1 3 1 5\n", True), ("1 1\n5\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: zero out rows/cols and print the matrix\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: zero out rows/cols and print the matrix\n    return 0;\n}\n"),

P("pacific-atlantic", "Pacific Atlantic Water Flow", "Medium", "Grid DFS/BFS", 3,
  "<p>Water flows from a cell to a 4-neighbor with height <b>less than or equal</b> to it. The Pacific touches the top and left edges; the Atlantic touches the bottom and right edges. Print all cells from which water can reach <b>both</b> oceans.</p>",
  "Line 1: m n. Next m lines: n integers (heights).",
  "Each qualifying cell as 'row col' (0-indexed), one per line, sorted by row then col.",
  ref_pacific_atlantic,
  [("5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4\n", True), ("1 1\n1\n", True), ("3 3\n1 2 3\n8 9 4\n7 6 5\n", False)],
  PY_HEAD + "    m = int(data[0]); n = int(data[1])\n    vals = list(map(int, data[2:2+m*n]))\n    h = [vals[i*n:(i+1)*n] for i in range(m)]\n    # TODO: print cells (row col) that reach both oceans, sorted\n\nmain()\n",
  CPP_HEAD + "    int m, n; cin >> m >> n;\n    vector<vector<int>> h(m, vector<int>(n));\n    for (auto& r : h) for (auto& x : r) cin >> x;\n    // TODO: print cells (row col) that reach both oceans, sorted\n    return 0;\n}\n"),

P("find-k-closest-elements", "Find K Closest Elements", "Medium", "Binary Search", 4,
  "<p>Given a <b>sorted</b> array, return the k elements closest to x, in ascending order. Closeness is |a-x|; ties prefer the smaller value.</p>",
  "Line 1: n. Line 2: n integers (ascending). Line 3: k x.",
  "The k closest elements, ascending, space-separated.",
  ref_find_k_closest,
  [("5\n1 2 3 4 5\n4 3\n", True), ("5\n1 2 3 4 5\n4 -1\n", True), ("6\n1 1 1 10 10 10\n1 9\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    k = int(data[1+n]); x = int(data[2+n])\n    # TODO: print the k closest elements (ascending)\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n; vector<int> a(n);\n    for (auto& v : a) cin >> v;\n    int k, x; cin >> k >> x;\n    // TODO: print the k closest elements (ascending)\n    return 0;\n}\n"),

P("find-median-from-data-stream", "Find Median from Data Stream", "Hard", "Two Heaps", 5,
  "<p>Process a stream of operations. <code>add x</code> inserts a number; <code>median</code> queries the current median. For each <code>median</code>, print the median formatted to <b>one decimal</b> (e.g. <code>2.0</code>, <code>2.5</code>).</p>",
  "Line 1: q (operations). Next q lines: 'add x' or 'median'.",
  "One line per 'median' query: the median to 1 decimal.",
  ref_find_median,
  [("5\nadd 1\nadd 2\nmedian\nadd 3\nmedian\n", True), ("4\nadd 5\nmedian\nadd 1\nmedian\n", True), ("3\nadd 2\nadd 2\nmedian\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: maintain a structure (e.g. two heaps)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"add\":\n            x = int(data[idx]); idx += 1\n            pass  # TODO: add x\n        else:\n            pass  # TODO: out.append('%.1f' % median)\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int q; cin >> q;\n    cout << fixed << setprecision(1);\n    string cmd;\n    // TODO: maintain a structure (e.g. two heaps)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"add\") { long long x; cin >> x; /* TODO */ }\n        else { /* TODO: print median */ }\n    }\n    return 0;\n}\n"),

P("graph-valid-tree", "Graph Valid Tree", "Medium", "Union-Find", 6,
  "<p>Given n nodes (0..n-1) and an undirected edge list, decide whether the graph forms a <b>valid tree</b> (fully connected and acyclic).</p>",
  "Line 1: n m. Next m lines: u v.",
  "'true' or 'false'.",
  ref_graph_valid_tree,
  [("5\n4\n0 1\n0 2\n0 3\n1 4\n", True), ("5\n5\n0 1\n1 2\n2 3\n1 3\n1 4\n", True), ("4\n2\n0 1\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1])\n    edges = []\n    idx = 2\n    for _ in range(m):\n        edges.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print 'true' if it is a valid tree else 'false'\n\nmain()\n",
  CPP_HEAD + "    int n, m; cin >> n >> m;\n    vector<pair<int,int>> edges(m);\n    for (auto& e : edges) cin >> e.first >> e.second;\n    // TODO: print \"true\" or \"false\"\n    return 0;\n}\n"),

P("lru-cache", "LRU Cache", "Medium", "Design / Hash + List", 7,
  "<p>Implement an LRU cache with the given capacity. <code>put k v</code> inserts/updates; <code>get k</code> returns the value or -1 and marks it most-recently-used. Evict the least-recently-used item when over capacity. Print the result of every <code>get</code>.</p>",
  "Line 1: capacity. Line 2: q. Next q lines: 'put k v' or 'get k'.",
  "One line per 'get': the value, or -1.",
  ref_lru_cache,
  [("2\n6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3\n", True), ("1\n4\nput 1 10\nget 1\nput 2 20\nget 1\n", True), ("2\n3\nget 5\nput 5 5\nget 5\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    cap = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the LRU cache (capacity = cap)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"put\":\n            k = int(data[idx]); v = int(data[idx+1]); idx += 2\n            pass  # TODO: put k, v\n        else:\n            k = int(data[idx]); idx += 1\n            pass  # TODO: out.append(str(get(k)))\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int cap, q; cin >> cap >> q;\n    string cmd;\n    // TODO: build the LRU cache (capacity = cap)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"put\") { int k, v; cin >> k >> v; /* TODO */ }\n        else { int k; cin >> k; /* TODO: print get(k) */ }\n    }\n    return 0;\n}\n"),

P("design-circular-queue", "Design Circular Queue", "Medium", "Design / Ring Buffer", 8,
  "<p>Implement a circular queue of capacity k. Operations: <code>enQueue x</code>, <code>deQueue</code>, <code>Front</code>, <code>Rear</code>, <code>isEmpty</code>, <code>isFull</code>. enQueue/deQueue print <code>true</code>/<code>false</code>; Front/Rear print the value or -1; isEmpty/isFull print <code>true</code>/<code>false</code>. Print the result of every operation.</p>",
  "Line 1: k (capacity). Line 2: q. Next q lines: an operation (with an arg for enQueue).",
  "One line per operation: its return value.",
  ref_circular_queue,
  [("3\n7\nenQueue 1\nenQueue 2\nenQueue 3\nenQueue 4\nRear\nisFull\ndeQueue\n", True), ("2\n4\nisEmpty\nenQueue 5\nFront\ndeQueue\n", True), ("1\n3\nenQueue 9\nRear\ndeQueue\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    k = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the circular queue (capacity = k)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"enQueue\":\n            x = int(data[idx]); idx += 1\n            pass  # TODO: out.append('true'/'false')\n        else:\n            pass  # TODO: handle deQueue/Front/Rear/isEmpty/isFull\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int k, q; cin >> k >> q;\n    string cmd;\n    // TODO: build the circular queue (capacity = k)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"enQueue\") { int x; cin >> x; /* TODO */ }\n        else { /* TODO: deQueue/Front/Rear/isEmpty/isFull */ }\n    }\n    return 0;\n}\n"),

P("time-based-key-value-store", "Time-Based Key-Value Store", "Medium", "Design / Binary Search", 8,
  "<p>Implement a store where <code>set key value ts</code> stores a value at timestamp ts (timestamps strictly increase per key), and <code>get key ts</code> returns the value with the largest timestamp ≤ ts, or an empty string if none. Print every <code>get</code> result.</p>",
  "Line 1: q. Next q lines: 'set key value ts' or 'get key ts'. (key/value are single tokens.)",
  "One line per 'get': the value, or an empty line if none.",
  ref_time_map,
  [("5\nset foo bar 1\nget foo 1\nget foo 3\nset foo baz 4\nget foo 4\n", True), ("3\nget x 1\nset x a 5\nget x 10\n", True), ("4\nset k v1 1\nset k v2 2\nget k 1\nget k 2\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the time-based store\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"set\":\n            key = data[idx]; val = data[idx+1]; ts = int(data[idx+2]); idx += 3\n            pass  # TODO: set\n        else:\n            key = data[idx]; ts = int(data[idx+1]); idx += 2\n            pass  # TODO: out.append(get(key, ts))\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int q; cin >> q;\n    string cmd;\n    // TODO: build the time-based store\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"set\") { string key, val; int ts; cin >> key >> val >> ts; /* TODO */ }\n        else { string key; int ts; cin >> key >> ts; /* TODO: print get */ }\n    }\n    return 0;\n}\n"),

# ----------------------------------------------------------------------------
# Compile-check every C++ starter so users never hit a template compile error
# ----------------------------------------------------------------------------
def compile_check():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in PROBLEMS:
            src = os.path.join(tmp, "s.cpp")
            with open(src, "w") as f:
                f.write(p["starter"]["cpp"])
            r = subprocess.run(["g++", "-std=c++17", "-O2", "-o", os.path.join(tmp, "a.out"), src],
                               capture_output=True, text=True)
            if r.returncode != 0:
                failures.append((p["id"], r.stderr.strip().split("\n")[0]))
    return failures

if __name__ == "__main__":
    fails = compile_check()
    if fails:
        print("C++ starter compile failures:")
        for i, e in fails:
            print(f"  {i}: {e}")
        sys.exit(1)
    print(f"All {len(PROBLEMS)} C++ starters compile.")

    banner = "/* AUTO-GENERATED by gen_problems.py. Expected outputs verified by running\n   reference solutions locally. Edit gen_problems.py and rerun to change. */\n"
    out = banner + "const PROBLEMS = " + json.dumps(PROBLEMS, indent=2) + ";\n"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems.js")
    with open(path, "w") as f:
        f.write(out)
    total_tests = sum(len(p["tests"]) for p in PROBLEMS)
    print(f"Wrote problems.js: {len(PROBLEMS)} problems, {total_tests} test cases.")
