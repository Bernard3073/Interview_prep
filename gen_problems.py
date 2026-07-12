#!/usr/bin/env python3
"""Generate problems.js for the in-site LeetCode practice page.

Each problem is an stdin->stdout task so one judge works for both Python and C++.
Reference solutions here produce the *expected* outputs (run locally so the test
cases are guaranteed correct). C++ starters are compile-checked with g++.

Run:  python3 gen_problems.py
"""
import io, json, subprocess, sys, tempfile, os, contextlib, re, shutil

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

def ref_shortest_path_binary_matrix():
    import sys
    from collections import deque
    lines = sys.stdin.read().split('\n')
    n = int(lines[0].strip())
    g = [lines[1+i].strip() for i in range(n)]
    if g[0][0] != '0' or g[n-1][n-1] != '0':
        print(-1); return
    seen = [[False]*n for _ in range(n)]
    seen[0][0] = True
    q = deque([(0, 0, 1)])
    while q:
        r, c, d = q.popleft()
        if r == n-1 and c == n-1:
            print(d); return
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r+dr, c+dc
                if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc] and g[nr][nc] == '0':
                    seen[nr][nc] = True
                    q.append((nr, nc, d+1))
    print(-1)

def ref_path_minimum_effort():
    import sys, heapq
    data = sys.stdin.read().split()
    rows = int(data[0]); cols = int(data[1])
    vals = list(map(int, data[2:2+rows*cols]))
    h = [vals[i*cols:(i+1)*cols] for i in range(rows)]
    dist = [[float('inf')]*cols for _ in range(rows)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]  # (effort so far, r, c)
    while pq:
        d, r, c = heapq.heappop(pq)
        if r == rows-1 and c == cols-1:
            print(d); return
        if d > dist[r][c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nd = max(d, abs(h[nr][nc] - h[r][c]))
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    heapq.heappush(pq, (nd, nr, nc))
    print(dist[rows-1][cols-1])

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
# Robotics / perception reference solutions (pure Python — no numpy)
# ----------------------------------------------------------------------------
def _gauss_solve(H, c):
    """Solve H x = c (dense, small) via Gauss-Jordan with partial pivoting."""
    n = len(c)
    M = [H[k][:] + [c[k]] for k in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for r in range(n):
            if r != col and abs(M[r][col]) > 1e-18:
                f = M[r][col] / pv
                for cc in range(col, n + 1):
                    M[r][cc] -= f * M[col][cc]
    return [M[k][n] / M[k][k] for k in range(n)]

def _iou(a, b):
    ix1 = max(a[0], b[0]); iy1 = max(a[1], b[1]); ix2 = min(a[2], b[2]); iy2 = min(a[3], b[3])
    iw = max(0.0, ix2 - ix1); ih = max(0.0, iy2 - iy1); inter = iw * ih
    aa = (a[2]-a[0])*(a[3]-a[1]); bb = (b[2]-b[0])*(b[3]-b[1])
    u = aa + bb - inter
    return inter / u if u > 0 else 0.0

def ref_rob_least_squares():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); xs = []; ys = []; idx = 1
    for _ in range(n):
        xs.append(float(d[idx])); ys.append(float(d[idx+1])); idx += 2
    sx = sum(xs); sy = sum(ys); sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
    m = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    b = (sy - m*sx) / n
    print("%.4f %.4f" % (m, b))

def ref_rob_covariance():
    import sys, math
    d = sys.stdin.read().split()
    n = int(d[0]); xs = []; ys = []; idx = 1
    for _ in range(n):
        xs.append(float(d[idx])); ys.append(float(d[idx+1])); idx += 2
    qx = float(d[idx]); qy = float(d[idx+1])
    mx = sum(xs)/n; my = sum(ys)/n
    c00 = sum((x-mx)**2 for x in xs)/(n-1)
    c11 = sum((y-my)**2 for y in ys)/(n-1)
    c01 = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/(n-1)
    det = c00*c11 - c01*c01
    i00 = c11/det; i11 = c00/det; i01 = -c01/det
    dx = qx-mx; dy = qy-my
    d2 = dx*(i00*dx + i01*dy) + dy*(i01*dx + i11*dy)
    print("%.4f %.4f %.4f %.4f" % (c00, c01, c01, c11))
    print("%.4f" % math.sqrt(d2))

def ref_rob_quat_rotate():
    import sys, math
    d = list(map(float, sys.stdin.read().split()))
    w, x, y, z = d[0:4]; vx, vy, vz = d[4:7]
    nrm = math.sqrt(w*w + x*x + y*y + z*z)
    w, x, y, z = w/nrm, x/nrm, y/nrm, z/nrm
    r00 = 1-2*(y*y+z*z); r01 = 2*(x*y-w*z); r02 = 2*(x*z+w*y)
    r10 = 2*(x*y+w*z); r11 = 1-2*(x*x+z*z); r12 = 2*(y*z-w*x)
    r20 = 2*(x*z-w*y); r21 = 2*(y*z+w*x); r22 = 1-2*(x*x+y*y)
    print("%.4f %.4f %.4f" % (r00*vx+r01*vy+r02*vz, r10*vx+r11*vy+r12*vz, r20*vx+r21*vy+r22*vz))

def ref_rob_transform():
    import sys
    d = list(map(float, sys.stdin.read().split()))
    R1 = d[0:9]; t1 = d[9:12]; R2 = d[12:21]; t2 = d[21:24]; p = d[24:27]
    def mv(R, v):
        return [R[0]*v[0]+R[1]*v[1]+R[2]*v[2], R[3]*v[0]+R[4]*v[1]+R[5]*v[2], R[6]*v[0]+R[7]*v[1]+R[8]*v[2]]
    a = mv(R2, p); a = [a[i]+t2[i] for i in range(3)]
    b = mv(R1, a); b = [b[i]+t1[i] for i in range(3)]
    print("%.4f %.4f %.4f" % (b[0], b[1], b[2]))

def ref_rob_convolution():
    import sys
    d = sys.stdin.read().split()
    H = int(d[0]); W = int(d[1]); idx = 2
    img = []
    for _ in range(H):
        img.append([int(d[idx+j]) for j in range(W)]); idx += W
    ker = []
    for _ in range(3):
        ker.append([int(d[idx+j]) for j in range(3)]); idx += 3
    for i in range(H):
        row = []
        for j in range(W):
            s = 0
            for ki in range(3):
                for kj in range(3):
                    ii = i+ki-1; jj = j+kj-1
                    if 0 <= ii < H and 0 <= jj < W:
                        s += ker[ki][kj]*img[ii][jj]
            row.append(s)
        print(*row)

def ref_rob_project():
    import sys
    d = list(map(float, sys.stdin.read().split()))
    fx, fy, cx, cy = d[0:4]; R = d[4:13]; t = d[13:16]; X = d[16:19]
    Xc = [R[0]*X[0]+R[1]*X[1]+R[2]*X[2]+t[0], R[3]*X[0]+R[4]*X[1]+R[5]*X[2]+t[1], R[6]*X[0]+R[7]*X[1]+R[8]*X[2]+t[2]]
    print("%.4f %.4f" % (fx*Xc[0]/Xc[2]+cx, fy*Xc[1]/Xc[2]+cy))

def ref_rob_ransac():
    import sys, math
    d = sys.stdin.read().split()
    n = int(d[0]); pts = []; idx = 1
    for _ in range(n):
        pts.append((float(d[idx]), float(d[idx+1]))); idx += 2
    thresh = float(d[idx])
    best = 0
    for i in range(n):
        for j in range(i+1, n):
            x1, y1 = pts[i]; x2, y2 = pts[j]
            dx = x2-x1; dy = y2-y1; L = math.hypot(dx, dy)
            if L < 1e-12: continue
            a = -dy/L; b = dx/L; c = -(a*x1 + b*y1)
            cnt = sum(1 for (px, py) in pts if abs(a*px + b*py + c) <= thresh + 1e-9)
            best = max(best, cnt)
    print(best)

def _kabsch2d(A, B):
    import math
    n = len(A)
    cax = sum(p[0] for p in A)/n; cay = sum(p[1] for p in A)/n
    cbx = sum(p[0] for p in B)/n; cby = sum(p[1] for p in B)/n
    num = den = 0.0
    for (ax, ay), (bx, by) in zip(A, B):
        ax -= cax; ay -= cay; bx -= cbx; by -= cby
        num += ax*by - ay*bx; den += ax*bx + ay*by
    theta = math.atan2(num, den)
    ct = math.cos(theta); st = math.sin(theta)
    tx = cbx - (ct*cax - st*cay); ty = cby - (st*cax + ct*cay)
    return theta, tx, ty

def ref_rob_rigid_align():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); A = []; B = []; idx = 1
    for _ in range(n):
        A.append((float(d[idx]), float(d[idx+1]))); B.append((float(d[idx+2]), float(d[idx+3]))); idx += 4
    theta, tx, ty = _kabsch2d(A, B)
    print("%.4f %.4f %.4f" % (theta, tx, ty))

def ref_rob_kalman_scalar():
    import sys
    d = sys.stdin.read().split()
    q = float(d[0]); r = float(d[1]); n = int(d[2])
    zs = [float(d[3+i]) for i in range(n)]
    x = 0.0; P = 1.0; out = []
    for z in zs:
        P = P + q
        K = P / (P + r)
        x = x + K*(z - x)
        P = (1 - K)*P
        out.append("%.4f" % x)
    print("\n".join(out))

def ref_rob_fusion():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); idx = 1; si = 0.0; sm = 0.0
    for _ in range(n):
        m = float(d[idx]); v = float(d[idx+1]); idx += 2
        si += 1.0/v; sm += m/v
    print("%.4f %.4f" % (sm/si, 1.0/si))

def ref_rob_icp_step():
    import sys
    d = sys.stdin.read().split()
    ns = int(d[0]); idx = 1; S = []
    for _ in range(ns):
        S.append((float(d[idx]), float(d[idx+1]))); idx += 2
    nt = int(d[idx]); idx += 1; T = []
    for _ in range(nt):
        T.append((float(d[idx]), float(d[idx+1]))); idx += 2
    A = []; B = []
    for (sx, sy) in S:
        bi = -1; bd = 1e18
        for k, (tx, ty) in enumerate(T):
            dd = (sx-tx)**2 + (sy-ty)**2
            if dd < bd - 1e-12: bd = dd; bi = k
        A.append((sx, sy)); B.append(T[bi])
    theta, tx, ty = _kabsch2d(A, B)
    print("%.4f %.4f %.4f" % (theta, tx, ty))

def ref_rob_pose_graph():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); m = int(d[1]); anchor = int(d[2]); idx = 3
    H = [[0.0]*n for _ in range(n)]; c = [0.0]*n
    for _ in range(m):
        i = int(d[idx]); j = int(d[idx+1]); meas = float(d[idx+2]); w = float(d[idx+3]); idx += 4
        H[i][i] += w; H[j][j] += w; H[i][j] -= w; H[j][i] -= w
        c[i] += -w*meas; c[j] += w*meas
    for k in range(n):
        H[anchor][k] = 0.0; H[k][anchor] = 0.0
    H[anchor][anchor] = 1.0; c[anchor] = 0.0
    x = _gauss_solve(H, c)
    print(" ".join("%.4f" % v for v in x))

def ref_rob_iou_nms():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); boxes = []; scores = []; idx = 1
    for _ in range(n):
        boxes.append((float(d[idx]), float(d[idx+1]), float(d[idx+2]), float(d[idx+3])))
        scores.append(float(d[idx+4])); idx += 5
    thr = float(d[idx])
    order = sorted(range(n), key=lambda k: (-scores[k], k))
    keep = []; sup = [False]*n
    for k in order:
        if sup[k]: continue
        keep.append(k)
        for k2 in order:
            if k2 != k and not sup[k2] and _iou(boxes[k], boxes[k2]) > thr:
                sup[k2] = True
    print(*keep)

def ref_rob_avg_precision():
    import sys
    d = sys.stdin.read().split()
    nd = int(d[0]); ng = int(d[1]); idx = 2
    dets = []
    for _ in range(nd):
        dets.append(((float(d[idx]), float(d[idx+1]), float(d[idx+2]), float(d[idx+3])), float(d[idx+4]))); idx += 5
    gts = []
    for _ in range(ng):
        gts.append((float(d[idx]), float(d[idx+1]), float(d[idx+2]), float(d[idx+3]))); idx += 4
    thr = float(d[idx])
    dets.sort(key=lambda x: -x[1])
    matched = [False]*ng; tp = [0]*nd; fp = [0]*nd
    for k, (b, s) in enumerate(dets):
        best = 0.0; bj = -1
        for j, g in enumerate(gts):
            iv = _iou(b, g)
            if iv > best: best = iv; bj = j
        if best >= thr and bj >= 0 and not matched[bj]:
            tp[k] = 1; matched[bj] = True
        else:
            fp[k] = 1
    ctp = cfp = 0; rec = []; prec = []
    for k in range(nd):
        ctp += tp[k]; cfp += fp[k]
        rec.append(ctp/ng if ng else 0.0)
        prec.append(ctp/(ctp+cfp) if (ctp+cfp) else 0.0)
    mrec = [0.0]+rec+[1.0]; mpre = [0.0]+prec+[0.0]
    for i in range(len(mpre)-2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i+1])
    ap = sum((mrec[i]-mrec[i-1])*mpre[i] for i in range(1, len(mrec)) if mrec[i] != mrec[i-1])
    print("%.4f" % ap)

def ref_rob_ring_buffer():
    import sys
    d = sys.stdin.read().split()
    idx = 0; cap = int(d[idx]); idx += 1; q = int(d[idx]); idx += 1
    buf = []; out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "push":
            x = d[idx]; idx += 1
            buf.append(x)
            if len(buf) > cap: buf.pop(0)
        elif cmd == "latest":
            out.append(buf[-1] if buf else "empty")
        elif cmd == "size":
            out.append(str(len(buf)))
    print("\n".join(out))

def ref_rob_time_sync():
    import sys
    d = sys.stdin.read().split()
    idx = 0; na = int(d[idx]); idx += 1
    A = [float(d[idx+i]) for i in range(na)]; idx += na
    nb = int(d[idx]); idx += 1
    B = [float(d[idx+i]) for i in range(nb)]; idx += nb
    mdt = float(d[idx])
    out = []; j = 0
    for i in range(na):
        while j+1 < nb and abs(B[j+1]-A[i]) <= abs(B[j]-A[i]): j += 1
        if nb > 0 and abs(B[j]-A[i]) <= mdt:
            out.append("%d %d" % (i, j))
    print("\n".join(out))

def ref_rob_frame_ingest():
    import sys
    d = sys.stdin.read().split()
    idx = 0; cap = int(d[idx]); idx += 1; q = int(d[idx]); idx += 1
    buf = [0]*cap; head = 0; count = 0; dropped = 0; out = []
    for _ in range(q):
        cmd = d[idx]; idx += 1
        if cmd == "push":
            x = int(d[idx]); idx += 1
            if count == cap:                 # full -> keep-latest: drop oldest
                head = (head + 1) % cap; count -= 1; dropped += 1
            buf[(head + count) % cap] = x; count += 1
        elif cmd == "pop":
            if count == 0:
                out.append("none")
            else:
                out.append(str(buf[head])); head = (head + 1) % cap; count -= 1
        elif cmd == "latest":
            out.append(str(buf[(head + count - 1) % cap]) if count else "none")
        elif cmd == "dropped":
            out.append(str(dropped))
        elif cmd == "size":
            out.append(str(count))
    print("\n".join(out))

def ref_rob_bev_splat():
    import sys, math
    data = sys.stdin.read().split()
    x_min = float(data[0]); x_max = float(data[1])
    y_min = float(data[2]); y_max = float(data[3]); cell = float(data[4])
    n = int(data[5]); idx = 6
    W = round((x_max - x_min) / cell)
    H = round((y_max - y_min) / cell)
    grid = [[0.0] * W for _ in range(H)]
    for _ in range(n):
        x = float(data[idx]); y = float(data[idx+1]); f = float(data[idx+2]); idx += 3
        col = int(math.floor((x - x_min) / cell))
        row = int(math.floor((y - y_min) / cell))
        if 0 <= col < W and 0 <= row < H:
            grid[row][col] += f
    print("\n".join(" ".join("%.1f" % v for v in r) for r in grid))

def ref_rob_bev_project():
    import sys
    data = sys.stdin.read().split()
    W = int(data[0]); H = int(data[1]); idx = 2
    P = [float(data[idx + i]) for i in range(12)]; idx += 12
    n = int(data[idx]); idx += 1
    out = []
    for i in range(n):
        X = float(data[idx]); Y = float(data[idx+1]); Z = float(data[idx+2]); idx += 3
        h0 = P[0]*X + P[1]*Y + P[2]*Z + P[3]
        h1 = P[4]*X + P[5]*Y + P[6]*Z + P[7]
        depth = P[8]*X + P[9]*Y + P[10]*Z + P[11]
        if depth > 0:
            u = h0 / depth; v = h1 / depth
            if 0 <= u < W and 0 <= v < H:
                out.append("%d %.2f %.2f" % (i, u, v))
    print("\n".join(out))

# ----------------------------------------------------------------------------
# Problem definitions
# ----------------------------------------------------------------------------
def P(id, title, diff, pattern, week, statement, infmt, outfmt, ref, tests, py, cpp,
      category="leetcode", checker="exact", tol=0.0):
    samples = [{"input": t[0], "expected": run_ref(ref, t[0]), "sample": t[1]} for t in tests]
    add(id=id, title=title, diff=diff, pattern=pattern, week=week, statement=statement,
        inputFormat=infmt, outputFormat=outfmt, tests=samples, category=category,
        checker=checker, tol=tol, starter={"python": py, "cpp": cpp})

PY_HEAD = "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n"
CPP_HEAD = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n"

P("two-sum", "Two Sum", "Easy", "Arrays / Hashing", 3,
  "<p>Given an array of integers and a target, return the <b>indices</b> (0-based) of the two numbers that add up to the target. Exactly one solution exists; return the indices in ascending order.</p>",
  "Line 1: n. Line 2: n integers. Line 3: target.",
  "The two indices, space-separated, ascending.",
  ref_two_sum,
  [("4\n2 7 11 15\n9\n", True), ("3\n3 2 4\n6\n", True), ("2\n3 3\n6\n", False), ("5\n-1 -2 -3 -4 -5\n-8\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    target = int(data[1+n])\n    # TODO: print the two indices\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int target; cin >> target;\n    // TODO: print the two indices\n    return 0;\n}\n"),

P("maximum-subarray", "Maximum Subarray", "Medium", "DP / Kadane", 3,
  "<p>Find the contiguous subarray with the largest sum and return that sum.</p>",
  "Line 1: n. Line 2: n integers.",
  "The maximum subarray sum.",
  ref_max_subarray,
  [("9\n-2 1 -3 4 -1 2 1 -5 4\n", True), ("1\n1\n", True), ("5\n5 4 -1 7 8\n", False), ("4\n-3 -2 -5 -1\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    # TODO: print the maximum subarray sum\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<long long> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print the maximum subarray sum\n    return 0;\n}\n"),

P("product-except-self", "Product of Array Except Self", "Medium", "Arrays / Prefix", 3,
  "<p>Return an array where each element is the product of all the others, <b>without using division</b>. O(n) time.</p>",
  "Line 1: n. Line 2: n integers.",
  "n integers (the answer), space-separated.",
  ref_product_except_self,
  [("4\n1 2 3 4\n", True), ("5\n-1 1 0 -3 3\n", True), ("2\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    arr = list(map(int, data[1:1+n]))\n    # TODO: print the result array\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<long long> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print the result array\n    return 0;\n}\n"),

P("rotate-image", "Rotate Image", "Medium", "Matrix", 4,
  "<p>Rotate an n×n matrix by 90° <b>clockwise</b> and print the result.</p>",
  "Line 1: n. Next n lines: n integers each.",
  "The rotated matrix, n lines of n integers.",
  ref_rotate_image,
  [("3\n1 2 3\n4 5 6\n7 8 9\n", True), ("2\n1 2\n3 4\n", True), ("1\n7\n", False)],
  PY_HEAD + "    n = int(data[0])\n    vals = list(map(int, data[1:1+n*n]))\n    m = [vals[i*n:(i+1)*n] for i in range(n)]\n    # TODO: rotate 90 deg clockwise and print\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<vector<int>> m(n, vector<int>(n));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: rotate 90 deg clockwise and print\n    return 0;\n}\n"),

P("spiral-matrix", "Spiral Matrix", "Medium", "Matrix", 4,
  "<p>Return all elements of the matrix in <b>spiral order</b> (clockwise from top-left).</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "All elements in spiral order, space-separated on one line.",
  ref_spiral,
  [("3 3\n1 2 3\n4 5 6\n7 8 9\n", True), ("3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n", True), ("1 1\n5\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: print spiral order\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: print spiral order\n    return 0;\n}\n"),

P("number-of-islands", "Number of Islands", "Medium", "Grid BFS/DFS", 5,
  "<p>Count the islands in a grid of <code>'1'</code> (land) and <code>'0'</code> (water). Cells connect 4-directionally.</p>",
  "Line 1: rows cols. Next rows lines: a string of cols characters ('0'/'1').",
  "The number of islands.",
  ref_num_islands,
  [("4 5\n11110\n11010\n11000\n00000\n", True), ("3 3\n101\n010\n101\n", True), ("1 1\n0\n", False)],
  PY_HEAD.replace("split()", "split('\\n')") + "    rows, cols = map(int, data[0].split())\n    grid = [list(data[1+i].strip()) for i in range(rows)]\n    # TODO: print the island count\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<string> g(rows);\n    for (auto& s : g) cin >> s;\n    // TODO: print the island count\n    return 0;\n}\n"),

P("path-with-minimum-effort", "Path With Minimum Effort", "Medium", "Grid Dijkstra", 12,
  "<p>Given a <code>rows x cols</code> grid of integer heights, find a path from the top-left to the bottom-right cell moving <b>4-directionally</b>. A path's <b>effort</b> is the maximum absolute height difference between any two consecutive cells on it. Return the minimum possible effort.</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "The minimum effort (an integer).",
  ref_path_minimum_effort,
  [("3 3\n1 2 2\n3 8 2\n5 3 5\n", True), ("3 3\n1 2 3\n3 8 4\n5 3 5\n", True),
   ("5 5\n1 2 1 1 1\n1 2 1 2 1\n1 2 1 2 1\n1 2 1 2 1\n1 1 1 2 1\n", False), ("1 1\n42\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    h = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: print the minimum effort\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> h(rows, vector<int>(cols));\n    for (auto& r : h) for (auto& x : r) cin >> x;\n    // TODO: print the minimum effort\n    return 0;\n}\n"),

P("shortest-path-in-binary-matrix", "Shortest Path in Binary Matrix", "Medium", "Grid BFS/A*", 12,
  "<p>In an <code>n x n</code> grid of <code>'0'</code> (clear) and <code>'1'</code> (blocked), find the length of the shortest <b>clear path</b> from the top-left to the bottom-right cell, moving <b>8-directionally</b> between clear cells. Path length is the number of visited cells. Return <code>-1</code> if no path exists.</p>",
  "Line 1: n. Next n lines: a string of n characters ('0'/'1').",
  "The shortest clear-path length (number of cells), or -1.",
  ref_shortest_path_binary_matrix,
  [("2\n00\n00\n", True), ("3\n000\n110\n110\n", True), ("3\n000\n111\n000\n", False), ("1\n0\n", False)],
  PY_HEAD.replace("split()", "split('\\n')") + "    n = int(data[0].strip())\n    grid = [data[1+i].strip() for i in range(n)]\n    # TODO: print the shortest clear-path length, or -1\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<string> g(n);\n    for (auto& s : g) cin >> s;\n    // TODO: print the shortest clear-path length, or -1\n    return 0;\n}\n"),

P("image-smoother", "Image Smoother", "Easy", "Matrix / Convolution", 5,
  "<p>For each cell output the floor of the average of itself and its (up to 8) neighbors — a 3×3 box filter.</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "The smoothed matrix, rows lines of cols integers.",
  ref_image_smoother,
  [("3 3\n1 1 1\n1 0 1\n1 1 1\n", True), ("2 2\n100 200\n100 200\n", True), ("1 3\n2 4 6\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: print the smoothed matrix\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: print the smoothed matrix\n    return 0;\n}\n"),

P("k-closest-points", "K Closest Points to Origin", "Medium", "Heap / Sorting", 6,
  "<p>Return the k points closest to the origin (Euclidean). Break ties by x then y so the answer is deterministic; print sorted by (distance, x, y).</p>",
  "Line 1: n. Next n lines: x y. Last line: k.",
  "k lines, each 'x y', ordered by distance then x then y.",
  ref_k_closest,
  [("3\n1 3\n-2 2\n5 8\n2\n", True), ("2\n3 3\n5 -1\n1\n", True), ("4\n0 1\n1 0\n2 2\n-1 -1\n3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = []\n    idx = 1\n    for _ in range(n):\n        pts.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    k = int(data[idx])\n    # TODO: print the k closest points\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> p(n);\n    for (auto& q : p) cin >> q.first >> q.second;\n    int k; cin >> k;\n    // TODO: print the k closest points\n    return 0;\n}\n"),

P("max-points-on-a-line", "Max Points on a Line", "Hard", "Geometry", 6,
  "<p>Given n points on a plane, return the maximum number of points that lie on the same straight line.</p>",
  "Line 1: n. Next n lines: x y.",
  "The maximum number of collinear points.",
  ref_max_points,
  [("6\n1 1\n2 2\n3 3\n1 4\n2 5\n3 6\n", True), ("3\n1 1\n3 2\n5 3\n", True), ("1\n0 0\n", False), ("4\n0 0\n1 1\n2 2\n3 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = []\n    idx = 1\n    for _ in range(n):\n        pts.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print max points on a line\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> p(n);\n    for (auto& q : p) cin >> q.first >> q.second;\n    // TODO: print max points on a line\n    return 0;\n}\n"),

P("moving-average", "Moving Average from Data Stream", "Easy", "Stream / Sliding Window", 7,
  "<p>Maintain a moving average over a sliding window of the given size. For each incoming value, print the current average (5 decimals).</p>",
  "Line 1: window size. Line 2: m (count). Line 3: m integers (the stream).",
  "m lines, each the moving average formatted to 5 decimals.",
  ref_moving_average,
  [("3\n5\n1 10 3 5 20\n", True), ("1\n3\n4 0 8\n", True), ("2\n4\n2 2 2 2\n", False)],
  PY_HEAD + "    size = int(data[0]); m = int(data[1])\n    vals = list(map(int, data[2:2+m]))\n    # TODO: print each moving average with '%.5f' % avg\n\nmain()\n",
  CPP_HEAD + "    int size, m; cin >> size >> m;\n    vector<int> v(m);\n    for (auto& x : v) cin >> x;\n    cout << fixed << setprecision(5);\n    // TODO: print each moving average\n    return 0;\n}\n"),

P("sliding-window-maximum", "Sliding Window Maximum", "Hard", "Monotonic Deque", 7,
  "<p>Given an array and window size k, output the maximum of each contiguous window.</p>",
  "Line 1: n. Line 2: n integers. Line 3: k.",
  "The window maxima, space-separated.",
  ref_sliding_window_max,
  [("8\n1 3 -1 -3 5 3 6 7\n3\n", True), ("1\n1\n1\n", True), ("6\n9 8 7 6 5 4\n2\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    k = int(data[1+n])\n    # TODO: print the window maxima\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int k; cin >> k;\n    // TODO: print the window maxima\n    return 0;\n}\n"),

P("course-schedule", "Course Schedule", "Medium", "Graph / Topo Sort", 8,
  "<p>There are numCourses courses. Each edge 'a b' means course a depends on course b. Determine if all courses can be finished (no cycle).</p>",
  "Line 1: numCourses. Line 2: e (edges). Next e lines: a b.",
  "'true' or 'false'.",
  ref_course_schedule,
  [("2\n1\n1 0\n", True), ("2\n2\n1 0\n0 1\n", True), ("4\n3\n1 0\n2 1\n3 2\n", False)],
  PY_HEAD + "    n = int(data[0]); e = int(data[1])\n    edges = []\n    idx = 2\n    for _ in range(e):\n        edges.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print 'true' or 'false'\n\nmain()\n",
  CPP_HEAD + "    int n, e; cin >> n >> e;\n    vector<pair<int,int>> edges(e);\n    for (auto& p : edges) cin >> p.first >> p.second;\n    // TODO: print \"true\" or \"false\"\n    return 0;\n}\n"),

P("network-delay-time", "Network Delay Time", "Medium", "Dijkstra", 8,
  "<p>A signal starts at node k in a network of n nodes (1-indexed). Each directed edge 'u v w' has travel time w. Return the time for all nodes to receive the signal, or -1 if impossible.</p>",
  "Line 1: n m k. Next m lines: u v w.",
  "The delay time, or -1.",
  ref_network_delay,
  [("4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 5\n", True), ("2 1 1\n1 2 1\n", True), ("2 1 2\n1 2 1\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1]); k = int(data[2])\n    edges = []\n    idx = 3\n    for _ in range(m):\n        edges.append((int(data[idx]), int(data[idx+1]), int(data[idx+2]))); idx += 3\n    # TODO: print the delay time or -1\n\nmain()\n",
  CPP_HEAD + "    int n, m, k; cin >> n >> m >> k;\n    vector<array<int,3>> edges(m);\n    for (auto& e : edges) cin >> e[0] >> e[1] >> e[2];\n    // TODO: print the delay time or -1\n    return 0;\n}\n"),

P("maximal-square", "Maximal Square", "Medium", "DP / Grid", 9,
  "<p>In a binary grid, find the largest square containing only 1s and return its <b>area</b>.</p>",
  "Line 1: rows cols. Next rows lines: a string of cols characters ('0'/'1').",
  "The area of the largest all-ones square.",
  ref_maximal_square,
  [("4 5\n10100\n10111\n11111\n10010\n", True), ("2 2\n01\n10\n", True), ("1 1\n0\n", False)],
  PY_HEAD.replace("split()", "split('\\n')") + "    rows, cols = map(int, data[0].split())\n    grid = [data[1+i].strip() for i in range(rows)]\n    # TODO: print the maximal square area\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<string> g(rows);\n    for (auto& s : g) cin >> s;\n    // TODO: print the maximal square area\n    return 0;\n}\n"),

P("word-ladder", "Word Ladder", "Hard", "BFS", 9,
  "<p>Return the number of words in the shortest transformation sequence from beginWord to endWord, changing one letter at a time, where each intermediate word must be in the word list. Return 0 if impossible. (Length counts both endpoints.)</p>",
  "Line 1: beginWord. Line 2: endWord. Line 3: count. Next count lines: the word list.",
  "The length of the shortest sequence, or 0.",
  ref_word_ladder,
  [("hit\ncog\n6\nhot\ndot\ndog\nlot\nlog\ncog\n", True), ("hit\ncog\n5\nhot\ndot\ndog\nlot\nlog\n", True), ("a\nc\n2\nb\nc\n", False)],
  "import sys\n\ndef main():\n    lines = sys.stdin.read().split('\\n')\n    begin = lines[0].strip(); end = lines[1].strip()\n    cnt = int(lines[2])\n    words = [lines[3+i].strip() for i in range(cnt)]\n    # TODO: print shortest ladder length or 0\n\nmain()\n",
  CPP_HEAD + "    string begin, end; cin >> begin >> end;\n    int cnt; cin >> cnt;\n    vector<string> words(cnt);\n    for (auto& w : words) cin >> w;\n    // TODO: print shortest ladder length or 0\n    return 0;\n}\n"),

P("merge-intervals", "Merge Intervals", "Medium", "Intervals", 10,
  "<p>Merge all overlapping intervals and print them sorted by start.</p>",
  "Line 1: n. Next n lines: start end.",
  "The merged intervals, one 'start end' per line, sorted by start.",
  ref_merge_intervals,
  [("4\n1 3\n2 6\n8 10\n15 18\n", True), ("2\n1 4\n4 5\n", True), ("3\n1 4\n0 4\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0])\n    iv = []\n    idx = 1\n    for _ in range(n):\n        iv.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print merged intervals\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<pair<int,int>> iv(n);\n    for (auto& p : iv) cin >> p.first >> p.second;\n    // TODO: print merged intervals\n    return 0;\n}\n"),

P("set-matrix-zeroes", "Set Matrix Zeroes", "Medium", "Matrix", 4,
  "<p>If an element is 0, set its entire row and column to 0 — and print the result. (Classic follow-up: do it in O(1) extra space.)</p>",
  "Line 1: rows cols. Next rows lines: cols integers each.",
  "The modified matrix, rows lines of cols integers.",
  ref_set_matrix_zeroes,
  [("3 3\n1 1 1\n1 0 1\n1 1 1\n", True), ("3 4\n0 1 2 0\n3 4 5 2\n1 3 1 5\n", True), ("1 1\n5\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    m = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: zero out rows/cols and print the matrix\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> m(rows, vector<int>(cols));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    // TODO: zero out rows/cols and print the matrix\n    return 0;\n}\n"),

P("pacific-atlantic", "Pacific Atlantic Water Flow", "Medium", "Grid DFS/BFS", 5,
  "<p>Water flows from a cell to a 4-neighbor with height <b>less than or equal</b> to it. The Pacific touches the top and left edges; the Atlantic touches the bottom and right edges. Print all cells from which water can reach <b>both</b> oceans.</p>",
  "Line 1: m n. Next m lines: n integers (heights).",
  "Each qualifying cell as 'row col' (0-indexed), one per line, sorted by row then col.",
  ref_pacific_atlantic,
  [("5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4\n", True), ("1 1\n1\n", True), ("3 3\n1 2 3\n8 9 4\n7 6 5\n", False)],
  PY_HEAD + "    m = int(data[0]); n = int(data[1])\n    vals = list(map(int, data[2:2+m*n]))\n    h = [vals[i*n:(i+1)*n] for i in range(m)]\n    # TODO: print cells (row col) that reach both oceans, sorted\n\nmain()\n",
  CPP_HEAD + "    int m, n; cin >> m >> n;\n    vector<vector<int>> h(m, vector<int>(n));\n    for (auto& r : h) for (auto& x : r) cin >> x;\n    // TODO: print cells (row col) that reach both oceans, sorted\n    return 0;\n}\n"),

P("find-k-closest-elements", "Find K Closest Elements", "Medium", "Binary Search", 6,
  "<p>Given a <b>sorted</b> array, return the k elements closest to x, in ascending order. Closeness is |a-x|; ties prefer the smaller value.</p>",
  "Line 1: n. Line 2: n integers (ascending). Line 3: k x.",
  "The k closest elements, ascending, space-separated.",
  ref_find_k_closest,
  [("5\n1 2 3 4 5\n4 3\n", True), ("5\n1 2 3 4 5\n4 -1\n", True), ("6\n1 1 1 10 10 10\n1 9\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    k = int(data[1+n]); x = int(data[2+n])\n    # TODO: print the k closest elements (ascending)\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n; vector<int> a(n);\n    for (auto& v : a) cin >> v;\n    int k, x; cin >> k >> x;\n    // TODO: print the k closest elements (ascending)\n    return 0;\n}\n"),

P("find-median-from-data-stream", "Find Median from Data Stream", "Hard", "Two Heaps", 7,
  "<p>Process a stream of operations. <code>add x</code> inserts a number; <code>median</code> queries the current median. For each <code>median</code>, print the median formatted to <b>one decimal</b> (e.g. <code>2.0</code>, <code>2.5</code>).</p>",
  "Line 1: q (operations). Next q lines: 'add x' or 'median'.",
  "One line per 'median' query: the median to 1 decimal.",
  ref_find_median,
  [("5\nadd 1\nadd 2\nmedian\nadd 3\nmedian\n", True), ("4\nadd 5\nmedian\nadd 1\nmedian\n", True), ("3\nadd 2\nadd 2\nmedian\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: maintain a structure (e.g. two heaps)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"add\":\n            x = int(data[idx]); idx += 1\n            pass  # TODO: add x\n        else:\n            pass  # TODO: out.append('%.1f' % median)\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int q; cin >> q;\n    cout << fixed << setprecision(1);\n    string cmd;\n    // TODO: maintain a structure (e.g. two heaps)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"add\") { long long x; cin >> x; /* TODO */ }\n        else { /* TODO: print median */ }\n    }\n    return 0;\n}\n"),

P("graph-valid-tree", "Graph Valid Tree", "Medium", "Union-Find", 8,
  "<p>Given n nodes (0..n-1) and an undirected edge list, decide whether the graph forms a <b>valid tree</b> (fully connected and acyclic).</p>",
  "Line 1: n m. Next m lines: u v.",
  "'true' or 'false'.",
  ref_graph_valid_tree,
  [("5\n4\n0 1\n0 2\n0 3\n1 4\n", True), ("5\n5\n0 1\n1 2\n2 3\n1 3\n1 4\n", True), ("4\n2\n0 1\n2 3\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1])\n    edges = []\n    idx = 2\n    for _ in range(m):\n        edges.append((int(data[idx]), int(data[idx+1]))); idx += 2\n    # TODO: print 'true' if it is a valid tree else 'false'\n\nmain()\n",
  CPP_HEAD + "    int n, m; cin >> n >> m;\n    vector<pair<int,int>> edges(m);\n    for (auto& e : edges) cin >> e.first >> e.second;\n    // TODO: print \"true\" or \"false\"\n    return 0;\n}\n"),

P("lru-cache", "LRU Cache", "Medium", "Design / Hash + List", 9,
  "<p>Implement an LRU cache with the given capacity. <code>put k v</code> inserts/updates; <code>get k</code> returns the value or -1 and marks it most-recently-used. Evict the least-recently-used item when over capacity. Print the result of every <code>get</code>.</p>",
  "Line 1: capacity. Line 2: q. Next q lines: 'put k v' or 'get k'.",
  "One line per 'get': the value, or -1.",
  ref_lru_cache,
  [("2\n6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3\n", True), ("1\n4\nput 1 10\nget 1\nput 2 20\nget 1\n", True), ("2\n3\nget 5\nput 5 5\nget 5\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    cap = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the LRU cache (capacity = cap)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"put\":\n            k = int(data[idx]); v = int(data[idx+1]); idx += 2\n            pass  # TODO: put k, v\n        else:\n            k = int(data[idx]); idx += 1\n            pass  # TODO: out.append(str(get(k)))\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int cap, q; cin >> cap >> q;\n    string cmd;\n    // TODO: build the LRU cache (capacity = cap)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"put\") { int k, v; cin >> k >> v; /* TODO */ }\n        else { int k; cin >> k; /* TODO: print get(k) */ }\n    }\n    return 0;\n}\n"),

P("design-circular-queue", "Design Circular Queue", "Medium", "Design / Ring Buffer", 10,
  "<p>Implement a circular queue of capacity k. Operations: <code>enQueue x</code>, <code>deQueue</code>, <code>Front</code>, <code>Rear</code>, <code>isEmpty</code>, <code>isFull</code>. enQueue/deQueue print <code>true</code>/<code>false</code>; Front/Rear print the value or -1; isEmpty/isFull print <code>true</code>/<code>false</code>. Print the result of every operation.</p>",
  "Line 1: k (capacity). Line 2: q. Next q lines: an operation (with an arg for enQueue).",
  "One line per operation: its return value.",
  ref_circular_queue,
  [("3\n7\nenQueue 1\nenQueue 2\nenQueue 3\nenQueue 4\nRear\nisFull\ndeQueue\n", True), ("2\n4\nisEmpty\nenQueue 5\nFront\ndeQueue\n", True), ("1\n3\nenQueue 9\nRear\ndeQueue\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    k = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the circular queue (capacity = k)\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"enQueue\":\n            x = int(data[idx]); idx += 1\n            pass  # TODO: out.append('true'/'false')\n        else:\n            pass  # TODO: handle deQueue/Front/Rear/isEmpty/isFull\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int k, q; cin >> k >> q;\n    string cmd;\n    // TODO: build the circular queue (capacity = k)\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"enQueue\") { int x; cin >> x; /* TODO */ }\n        else { /* TODO: deQueue/Front/Rear/isEmpty/isFull */ }\n    }\n    return 0;\n}\n"),

P("time-based-key-value-store", "Time-Based Key-Value Store", "Medium", "Design / Binary Search", 10,
  "<p>Implement a store where <code>set key value ts</code> stores a value at timestamp ts (timestamps strictly increase per key), and <code>get key ts</code> returns the value with the largest timestamp ≤ ts, or an empty string if none. Print every <code>get</code> result.</p>",
  "Line 1: q. Next q lines: 'set key value ts' or 'get key ts'. (key/value are single tokens.)",
  "One line per 'get': the value, or an empty line if none.",
  ref_time_map,
  [("5\nset foo bar 1\nget foo 1\nget foo 3\nset foo baz 4\nget foo 4\n", True), ("3\nget x 1\nset x a 5\nget x 10\n", True), ("4\nset k v1 1\nset k v2 2\nget k 1\nget k 2\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: build the time-based store\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"set\":\n            key = data[idx]; val = data[idx+1]; ts = int(data[idx+2]); idx += 3\n            pass  # TODO: set\n        else:\n            key = data[idx]; ts = int(data[idx+1]); idx += 2\n            pass  # TODO: out.append(get(key, ts))\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int q; cin >> q;\n    string cmd;\n    // TODO: build the time-based store\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"set\") { string key, val; int ts; cin >> key >> val >> ts; /* TODO */ }\n        else { string key; int ts; cin >> key >> ts; /* TODO: print get */ }\n    }\n    return 0;\n}\n"),

# ----------------------------------------------------------------------------
# Robotics / perception problems (numpy-free; float-tolerant judging)
# ----------------------------------------------------------------------------
ROB = dict(category="robotics", checker="float", tol=1e-3)
ROB_EXACT = dict(category="robotics", checker="exact")
CPP_F = CPP_HEAD + "    cout << fixed << setprecision(6);\n"

P("rob-least-squares-line", "Least-Squares Line Fit", "Easy", "Linear Algebra", 3,
  "<p>Fit the best line <code>y = m·x + b</code> to noisy points by ordinary least squares (closed-form normal equations). Print the slope and intercept.</p>",
  "Line 1: n. Next n lines: x y (floats).",
  "'m b' (slope, intercept) to ~4 decimals.",
  ref_rob_least_squares,
  [("4\n0 1\n1 3\n2 5\n3 7\n", True), ("5\n0 1.1\n1 0.9\n2 3.2\n3 2.8\n4 5.1\n", True), ("3\n1 2\n2 4\n3 6\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = [(float(data[1+2*i]), float(data[2+2*i])) for i in range(n)]\n    # TODO: print 'm b' via least squares\n\nmain()\n",
  CPP_F + "    int n; cin >> n;\n    vector<double> x(n), y(n);\n    for (int i = 0; i < n; i++) cin >> x[i] >> y[i];\n    // TODO: print 'm b' via least squares\n    return 0;\n}\n", **ROB),

P("rob-covariance-mahalanobis", "Covariance & Mahalanobis Distance", "Medium", "Probability", 3,
  "<p>From a set of 2D points compute the (sample, divided by n-1) covariance matrix, then the Mahalanobis distance of a query point to the mean.</p>",
  "Line 1: n. Next n lines: x y. Last line: qx qy (the query point).",
  "Line 1: covariance 'c00 c01 c10 c11'. Line 2: Mahalanobis distance.",
  ref_rob_covariance,
  [("4\n0 0\n2 0\n0 2\n2 2\n3 3\n", True), ("5\n1 2\n2 1\n3 5\n4 3\n5 6\n3 4\n", True), ("3\n0 0\n2 1\n1 3\n4 4\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = [(float(data[1+2*i]), float(data[2+2*i])) for i in range(n)]\n    qx = float(data[1+2*n]); qy = float(data[2+2*n])\n    # TODO: print covariance (4 nums) then Mahalanobis distance\n\nmain()\n",
  CPP_F + "    int n; cin >> n;\n    vector<double> x(n), y(n);\n    for (int i = 0; i < n; i++) cin >> x[i] >> y[i];\n    double qx, qy; cin >> qx >> qy;\n    // TODO: print covariance then Mahalanobis distance\n    return 0;\n}\n", **ROB),

P("rob-quaternion-rotate", "Rotate a Vector by a Quaternion", "Easy", "3D Geometry", 4,
  "<p>Given a (possibly unnormalized) quaternion [w x y z] and a 3D vector, return the rotated vector. Normalize the quaternion first.</p>",
  "Line 1: w x y z. Line 2: vx vy vz.",
  "The rotated vector 'rx ry rz'.",
  ref_rob_quat_rotate,
  [("0.7071068 0 0 0.7071068\n1 0 0\n", True), ("1 0 0 0\n3 -2 5\n", True), ("0.5 0.5 0.5 0.5\n1 0 0\n", False)],
  "import sys\n\ndef main():\n    d = list(map(float, sys.stdin.read().split()))\n    w, x, y, z = d[0:4]\n    vx, vy, vz = d[4:7]\n    # TODO: normalize q and print the rotated vector\n\nmain()\n",
  CPP_F + "    double w, x, y, z, vx, vy, vz;\n    cin >> w >> x >> y >> z >> vx >> vy >> vz;\n    // TODO: normalize q and print the rotated vector\n    return 0;\n}\n", **ROB),

P("rob-transform-point", "Compose SE(3) and Transform a Point", "Medium", "3D Geometry", 4,
  "<p>Given two rigid transforms T1=(R1,t1) and T2=(R2,t2) (rotations are 3×3 row-major), apply the composition <code>T1 ∘ T2</code> to a point p, i.e. compute <code>R1·(R2·p + t2) + t1</code>.</p>",
  "Line 1: R1 (9 numbers, row-major). Line 2: t1 (3). Line 3: R2 (9). Line 4: t2 (3). Line 5: p (3).",
  "The transformed point 'x y z'.",
  ref_rob_transform,
  [("1 0 0 0 1 0 0 0 1\n5 2 0\n0 -1 0 1 0 0 0 0 1\n0 0 0\n1 0 0\n", True), ("1 0 0 0 1 0 0 0 1\n0 0 0\n1 0 0 0 1 0 0 0 1\n1 2 3\n0 0 0\n", True), ("0 -1 0 1 0 0 0 0 1\n1 1 1\n1 0 0 0 1 0 0 0 1\n0 0 0\n2 0 0\n", False)],
  "import sys\n\ndef main():\n    d = list(map(float, sys.stdin.read().split()))\n    R1 = d[0:9]; t1 = d[9:12]; R2 = d[12:21]; t2 = d[21:24]; p = d[24:27]\n    # TODO: print R1*(R2*p + t2) + t1\n\nmain()\n",
  CPP_F + "    vector<double> d(27);\n    for (auto& v : d) cin >> v;\n    // d[0:9]=R1, d[9:12]=t1, d[12:21]=R2, d[21:24]=t2, d[24:27]=p\n    // TODO: print R1*(R2*p + t2) + t1\n    return 0;\n}\n", **ROB),

P("rob-convolution-2d", "2D Cross-Correlation", "Easy", "Image Processing", 5,
  "<p>Apply a 3×3 kernel to an image by <b>cross-correlation</b> (slide the kernel as-is, no flip) with zero padding. Output the result (same size). Integer arithmetic — e.g. feed a Sobel kernel to get edges.</p>",
  "Line 1: H W. Next H lines: W integers (image). Next 3 lines: 3 integers each (kernel).",
  "The H×W result, integers.",
  ref_rob_convolution,
  [("3 3\n0 0 0\n0 1 0\n0 0 0\n1 2 1\n2 4 2\n1 2 1\n", True), ("3 4\n10 10 10 10\n10 10 10 10\n10 10 10 10\n-1 0 1\n-2 0 2\n-1 0 1\n", True), ("1 3\n1 2 3\n0 0 0\n0 1 0\n0 0 0\n", False)],
  PY_HEAD + "    H = int(data[0]); W = int(data[1]); idx = 2\n    img = [[int(data[idx + i*W + j]) for j in range(W)] for i in range(H)]; idx += H*W\n    ker = [[int(data[idx + i*3 + j]) for j in range(3)] for i in range(3)]\n    # TODO: print the cross-correlated image (zero padding)\n\nmain()\n",
  CPP_HEAD + "    int H, W; cin >> H >> W;\n    vector<vector<int>> img(H, vector<int>(W));\n    for (auto& r : img) for (auto& v : r) cin >> v;\n    vector<vector<int>> ker(3, vector<int>(3));\n    for (auto& r : ker) for (auto& v : r) cin >> v;\n    // TODO: print the cross-correlated image (zero padding)\n    return 0;\n}\n", **ROB_EXACT),

P("rob-project-point", "Project a 3D Point to a Pixel", "Easy", "Camera Model", 5,
  "<p>Project a world point to pixel coordinates with the pinhole model: transform to the camera frame with (R,t), then apply intrinsics. <code>u = fx·X/Z + cx</code>, <code>v = fy·Y/Z + cy</code>.</p>",
  "Line 1: fx fy cx cy. Line 2: R (9, row-major). Line 3: t (3). Line 4: world point (3).",
  "The pixel 'u v'.",
  ref_rob_project,
  [("800 800 320 240\n1 0 0 0 1 0 0 0 1\n0 0 0\n0 0 5\n", True), ("800 800 320 240\n1 0 0 0 1 0 0 0 1\n0 0 0\n1 0.5 5\n", True), ("500 500 100 100\n1 0 0 0 1 0 0 0 1\n0 0 2\n1 -1 3\n", False)],
  "import sys\n\ndef main():\n    d = list(map(float, sys.stdin.read().split()))\n    fx, fy, cx, cy = d[0:4]; R = d[4:13]; t = d[13:16]; X = d[16:19]\n    # TODO: print the pixel 'u v'\n\nmain()\n",
  CPP_F + "    double fx, fy, cx, cy; cin >> fx >> fy >> cx >> cy;\n    vector<double> R(9); for (auto& v : R) cin >> v;\n    vector<double> t(3); for (auto& v : t) cin >> v;\n    vector<double> X(3); for (auto& v : X) cin >> v;\n    // TODO: print the pixel 'u v'\n    return 0;\n}\n", **ROB),

P("rob-ransac-line-inliers", "RANSAC Line — Max Inliers", "Medium", "Robust Fitting", 6,
  "<p>Find the line (through some pair of the given points) that has the most inliers, where a point is an inlier if its perpendicular distance to the line is ≤ threshold. Print the maximum inlier count. (Deterministic version of RANSAC's scoring — try every pair.)</p>",
  "Line 1: n. Next n lines: x y. Last line: threshold (float).",
  "The maximum number of inliers (an integer).",
  ref_rob_ransac,
  [("5\n0 0\n1 1\n2 2\n3 3\n0 5\n0.1\n", True), ("6\n0 0\n1 0\n2 0\n0 1\n1 1\n2 1\n0.1\n", True), ("4\n0 0\n1 1\n2 2\n5 0\n0.5\n", False)],
  PY_HEAD + "    n = int(data[0])\n    pts = [(float(data[1+2*i]), float(data[2+2*i])) for i in range(n)]\n    thresh = float(data[1+2*n])\n    # TODO: print the max inlier count over all candidate lines\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<double> x(n), y(n);\n    for (int i = 0; i < n; i++) cin >> x[i] >> y[i];\n    double thresh; cin >> thresh;\n    // TODO: print the max inlier count over all candidate lines\n    return 0;\n}\n", **ROB_EXACT),

P("rob-rigid-align-2d", "2D Rigid Point-Set Alignment (Kabsch)", "Medium", "Registration", 6,
  "<p>Given corresponding 2D point pairs (a_i ↔ b_i), find the rotation θ and translation (tx,ty) that best maps A onto B in the least-squares sense (closed-form 2D Kabsch). Print θ (radians), tx, ty.</p>",
  "Line 1: n. Next n lines: ax ay bx by.",
  "'theta tx ty' (theta in radians).",
  ref_rob_rigid_align,
  [("3\n0 0 1 1\n1 0 1 2\n0 1 0 2\n", True), ("3\n0 0 0 0\n1 0 0 1\n2 0 0 2\n", True), ("4\n0 0 5 5\n1 0 6 5\n1 1 6 6\n0 1 5 6\n", False)],
  PY_HEAD + "    n = int(data[0])\n    A = [(float(data[1+4*i]), float(data[2+4*i])) for i in range(n)]\n    B = [(float(data[3+4*i]), float(data[4+4*i])) for i in range(n)]\n    # TODO: print 'theta tx ty' (2D Kabsch)\n\nmain()\n",
  CPP_F + "    int n; cin >> n;\n    vector<double> ax(n), ay(n), bx(n), by(n);\n    for (int i = 0; i < n; i++) cin >> ax[i] >> ay[i] >> bx[i] >> by[i];\n    // TODO: print 'theta tx ty' (2D Kabsch)\n    return 0;\n}\n", **ROB),

P("rob-kalman-1d", "1D Kalman Filter (scalar)", "Medium", "State Estimation", 7,
  "<p>Filter a noisy 1D signal with a scalar (random-walk) Kalman filter. Use <b>x₀ = 0, P₀ = 1</b>; per step: predict <code>P += q</code>; update <code>K = P/(P+r)</code>, <code>x += K·(z−x)</code>, <code>P = (1−K)·P</code>. Print the estimate after each measurement.</p>",
  "Line 1: q r (process var, measurement var). Line 2: n. Line 3: n measurements.",
  "n lines: the filtered estimate after each measurement.",
  ref_rob_kalman_scalar,
  [("0.01 1.0\n5\n1 1 1 1 1\n", True), ("0.5 0.5\n4\n0 10 0 10\n", True), ("0.1 2.0\n3\n5 5 5\n", False)],
  PY_HEAD + "    q = float(data[0]); r = float(data[1]); n = int(data[2])\n    z = list(map(float, data[3:3+n]))\n    # TODO: run the scalar Kalman filter; print each estimate\n\nmain()\n",
  CPP_F + "    double q, r; int n; cin >> q >> r >> n;\n    vector<double> z(n); for (auto& v : z) cin >> v;\n    // TODO: run the scalar Kalman filter; print each estimate\n    return 0;\n}\n", **ROB),

P("rob-measurement-fusion", "Inverse-Variance Sensor Fusion", "Easy", "Sensor Fusion", 7,
  "<p>Fuse N independent Gaussian measurements of the same quantity into one estimate by inverse-variance weighting: <code>1/σ² = Σ 1/σᵢ²</code>, <code>μ = (Σ μᵢ/σᵢ²)·σ²</code>. Print the fused mean and variance.</p>",
  "Line 1: n. Next n lines: mean variance.",
  "'mean variance' (fused).",
  ref_rob_fusion,
  [("2\n10 1\n12 1\n", True), ("3\n5 0.5\n5.5 2\n4.8 1\n", True), ("2\n0 4\n10 1\n", False)],
  PY_HEAD + "    n = int(data[0])\n    obs = [(float(data[1+2*i]), float(data[2+2*i])) for i in range(n)]\n    # TODO: print fused 'mean variance'\n\nmain()\n",
  CPP_F + "    int n; cin >> n;\n    vector<double> m(n), v(n);\n    for (int i = 0; i < n; i++) cin >> m[i] >> v[i];\n    // TODO: print fused 'mean variance'\n    return 0;\n}\n", **ROB),

P("rob-icp-2d-step", "ICP — One Iteration (2D)", "Hard", "SLAM / Registration", 8,
  "<p>Perform one ICP iteration: for each source point find its nearest target point (Euclidean; ties → smallest index), then solve the best rigid transform over those correspondences (2D Kabsch). Print θ, tx, ty.</p>",
  "Line 1: ns. Next ns lines: x y (source). Then nt. Next nt lines: x y (target).",
  "'theta tx ty' for the one-step alignment.",
  ref_rob_icp_step,
  [("3\n0 0\n1 0\n0 1\n3\n5 5\n6 5\n5 6\n", True), ("2\n0 0\n2 0\n3\n0 1\n1 1\n2 1\n", True), ("3\n0 0\n1 1\n2 2\n3\n1 0\n2 1\n3 2\n", False)],
  PY_HEAD + "    ns = int(data[0])\n    S = [(float(data[1+2*i]), float(data[2+2*i])) for i in range(ns)]\n    o = 1 + 2*ns\n    nt = int(data[o]); o += 1\n    T = [(float(data[o+2*i]), float(data[o+1+2*i])) for i in range(nt)]\n    # TODO: nearest-neighbor correspondences + Kabsch; print 'theta tx ty'\n\nmain()\n",
  CPP_F + "    int ns; cin >> ns;\n    vector<double> sx(ns), sy(ns);\n    for (int i = 0; i < ns; i++) cin >> sx[i] >> sy[i];\n    int nt; cin >> nt;\n    vector<double> tx(nt), ty(nt);\n    for (int i = 0; i < nt; i++) cin >> tx[i] >> ty[i];\n    // TODO: nearest-neighbor correspondences + Kabsch; print 'theta tx ty'\n    return 0;\n}\n", **ROB),

P("rob-pose-graph-1d", "1D Pose-Graph Optimization", "Hard", "SLAM / Optimization", 8,
  "<p>Optimize 1D poses given relative measurements. Each edge (i, j, d, w) says x_j − x_i ≈ d with weight w. Minimize Σ w·((x_j−x_i)−d)² with the anchor pose fixed to 0. Print the optimized poses x₀…x₍ₙ₋₁₎.</p>",
  "Line 1: n m anchor. Next m lines: i j d w (the edges).",
  "n optimized poses, space-separated.",
  ref_rob_pose_graph,
  [("4 4 0\n0 1 1 1\n1 2 1 1\n2 3 1 1\n0 3 3 5\n", True), ("3 2 0\n0 1 1.1 1\n1 2 0.9 1\n", True), ("5 5 0\n0 1 1 1\n1 2 1 1\n2 3 1 1\n3 4 1 1\n0 4 4 10\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1]); anchor = int(data[2])\n    edges = [(int(data[3+4*i]), int(data[4+4*i]), float(data[5+4*i]), float(data[6+4*i])) for i in range(m)]\n    # TODO: solve the linear system (anchor fixed to 0); print the poses\n\nmain()\n",
  CPP_F + "    int n, m, anchor; cin >> n >> m >> anchor;\n    vector<array<double,4>> e(m);\n    for (auto& a : e) cin >> a[0] >> a[1] >> a[2] >> a[3];\n    // TODO: solve the linear system (anchor fixed to 0); print the poses\n    return 0;\n}\n", **ROB),

P("rob-iou-nms", "IoU + Non-Max Suppression", "Medium", "Detection", 9,
  "<p>Run greedy NMS on detection boxes. Sort by score descending (ties → smaller index); repeatedly keep the top box and suppress any remaining box whose IoU with it exceeds the threshold. Print the kept indices in the order kept.</p>",
  "Line 1: n. Next n lines: x1 y1 x2 y2 score. Last line: iou_threshold.",
  "The kept original indices, space-separated, in NMS order.",
  ref_rob_iou_nms,
  [("5\n10 10 50 50 0.9\n12 11 52 49 0.85\n11 9 48 51 0.8\n100 100 140 140 0.95\n102 98 138 142 0.7\n0.5\n", True), ("3\n0 0 10 10 0.5\n1 1 11 11 0.9\n20 20 30 30 0.8\n0.4\n", True), ("2\n0 0 4 4 0.6\n5 5 9 9 0.7\n0.5\n", False)],
  PY_HEAD + "    n = int(data[0])\n    boxes = [tuple(map(float, data[1+5*i:5+5*i])) for i in range(n)]\n    scores = [float(data[5+5*i]) for i in range(n)]\n    thr = float(data[1+5*n])\n    # TODO: print kept indices after NMS\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<array<double,4>> b(n); vector<double> s(n);\n    for (int i = 0; i < n; i++) { cin >> b[i][0] >> b[i][1] >> b[i][2] >> b[i][3] >> s[i]; }\n    double thr; cin >> thr;\n    // TODO: print kept indices after NMS\n    return 0;\n}\n", **ROB_EXACT),

P("rob-average-precision", "Average Precision (detection)", "Hard", "Detection Metrics", 9,
  "<p>Compute Average Precision for one class. Match detections (high score first) to ground-truth boxes by IoU ≥ threshold (each GT once); build the precision–recall curve and return the all-points AP (area under the monotonic-interpolated curve).</p>",
  "Line 1: nd ng. Next nd lines: x1 y1 x2 y2 score. Next ng lines: x1 y1 x2 y2. Last line: iou_threshold.",
  "The AP value.",
  ref_rob_avg_precision,
  [("3 2\n10 10 50 50 0.9\n100 100 140 140 0.8\n60 60 90 90 0.7\n11 9 49 51\n101 102 139 138\n0.5\n", True), ("2 2\n0 0 10 10 0.9\n0 0 10 10 0.8\n0 0 10 10\n100 100 110 110\n0.5\n", True), ("1 1\n0 0 10 10 0.9\n0 0 10 10\n0.5\n", False)],
  PY_HEAD + "    nd = int(data[0]); ng = int(data[1]); idx = 2\n    dets = []\n    for _ in range(nd):\n        dets.append((tuple(map(float, data[idx:idx+4])), float(data[idx+4]))); idx += 5\n    gts = []\n    for _ in range(ng):\n        gts.append(tuple(map(float, data[idx:idx+4]))); idx += 4\n    thr = float(data[idx])\n    # TODO: print the AP\n\nmain()\n",
  CPP_F + "    int nd, ng; cin >> nd >> ng;\n    vector<array<double,4>> det(nd); vector<double> score(nd);\n    for (int i = 0; i < nd; i++) { cin >> det[i][0] >> det[i][1] >> det[i][2] >> det[i][3] >> score[i]; }\n    vector<array<double,4>> gt(ng);\n    for (auto& g : gt) cin >> g[0] >> g[1] >> g[2] >> g[3];\n    double thr; cin >> thr;\n    // TODO: print the AP\n    return 0;\n}\n", **ROB),

P("rob-ring-buffer", "Sensor Ring Buffer", "Easy", "Systems / Design", 10,
  "<p>Implement a fixed-capacity ring buffer for sensor messages. <code>push x</code> appends (dropping the oldest when full); <code>latest</code> prints the most recent value (or <code>empty</code>); <code>size</code> prints the current count.</p>",
  "Line 1: capacity. Line 2: q. Next q lines: 'push x', 'latest', or 'size'.",
  "One line per 'latest' / 'size' query.",
  ref_rob_ring_buffer,
  [("3\n6\npush 1\npush 2\npush 3\npush 4\nlatest\nsize\n", True), ("2\n4\nlatest\npush 9\nsize\nlatest\n", True), ("1\n3\npush 5\npush 6\nlatest\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    cap = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: maintain a ring buffer of capacity cap\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"push\":\n            x = data[idx]; idx += 1\n            pass  # TODO\n        elif cmd == \"latest\":\n            pass  # TODO: out.append(latest or 'empty')\n        else:\n            pass  # TODO: out.append(str(size))\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int cap, q; cin >> cap >> q;\n    string cmd;\n    // TODO: maintain a ring buffer of capacity cap\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"push\") { long long x; cin >> x; /* TODO */ }\n        else if (cmd == \"latest\") { /* TODO: print latest or 'empty' */ }\n        else { /* TODO: print size */ }\n    }\n    return 0;\n}\n", **ROB_EXACT),

P("rob-time-sync", "Nearest-Timestamp Sensor Sync", "Medium", "Systems / Sync", 10,
  "<p>Two sensors publish timestamps (ascending). For each timestamp in stream A, find the nearest timestamp in stream B; if it's within max_dt, output the matched pair of indices. Use an O(n+m) two-pointer sweep.</p>",
  "Line 1: na. Line 2: na floats (A). Line 3: nb. Line 4: nb floats (B). Line 5: max_dt.",
  "One 'i j' per matched A index (0-based), in A order.",
  ref_rob_time_sync,
  [("7\n0.0 0.033 0.066 0.10 0.133 0.166 0.20\n3\n0.005 0.105 0.205\n0.02\n", True), ("3\n0 1 2\n2\n0.1 5\n0.5\n", True), ("2\n0 10\n2\n0.1 9.9\n0.2\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    na = int(data[idx]); idx += 1\n    A = [float(data[idx+i]) for i in range(na)]; idx += na\n    nb = int(data[idx]); idx += 1\n    B = [float(data[idx+i]) for i in range(nb)]; idx += nb\n    max_dt = float(data[idx])\n    # TODO: print matched 'i j' pairs within max_dt\n\nmain()\n",
  CPP_HEAD + "    int na; cin >> na; vector<double> A(na);\n    for (auto& v : A) cin >> v;\n    int nb; cin >> nb; vector<double> B(nb);\n    for (auto& v : B) cin >> v;\n    double max_dt; cin >> max_dt;\n    // TODO: print matched 'i j' pairs within max_dt\n    return 0;\n}\n", **ROB_EXACT),

P("rob-frame-ingest", "Real-Time Frame Ingest Buffer", "Medium", "Systems / Real-Time", 11,
  "<p>On a drone, a camera callback ingests frames at 30&nbsp;Hz while a slower perception model consumes them asynchronously. Implement the <b>fixed-capacity ring buffer</b> between them: bounded memory (no growth in flight) with a <b>keep-latest</b> policy — when full, a <code>push</code> drops the <i>oldest</i> frame so the freshest data survives and latency stays bounded.</p>"
  "<p>Support: <code>push x</code> (ingest frame id x; if full, drop the oldest and count it), <code>pop</code> (consumer takes the oldest buffered frame — print its id or <code>none</code>), <code>latest</code> (newest buffered id or <code>none</code>), <code>dropped</code> (how many were dropped on overflow), <code>size</code> (current count).</p>",
  "Line 1: capacity. Line 2: q. Next q lines: 'push x', 'pop', 'latest', 'dropped', or 'size'.",
  "One line per pop / latest / dropped / size query.",
  ref_rob_frame_ingest,
  [("3\n8\npush 1\npush 2\npush 3\npush 4\npop\nlatest\ndropped\nsize\n", True),
   ("2\n5\npush 10\npop\npop\nlatest\nsize\n", True),
   ("2\n6\npush 5\npush 6\npush 7\nsize\nlatest\ndropped\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    cap = int(data[idx]); idx += 1\n    q = int(data[idx]); idx += 1\n    out = []\n    # TODO: fixed-capacity ring buffer; keep-latest (drop oldest) when full\n    for _ in range(q):\n        cmd = data[idx]; idx += 1\n        if cmd == \"push\":\n            x = int(data[idx]); idx += 1\n            pass  # TODO\n        elif cmd == \"pop\":\n            pass  # TODO: out.append(oldest id or 'none')\n        elif cmd == \"latest\":\n            pass  # TODO\n        elif cmd == \"dropped\":\n            pass  # TODO\n        else:  # size\n            pass  # TODO\n    print(\"\\n\".join(out))\n\nmain()\n",
  CPP_HEAD + "    int cap, q; cin >> cap >> q;\n    string cmd;\n    // TODO: fixed-capacity ring buffer (no dynamic growth); keep-latest on overflow\n    for (int i = 0; i < q; i++) {\n        cin >> cmd;\n        if (cmd == \"push\") { long long x; cin >> x; /* TODO */ }\n        else if (cmd == \"pop\") { /* TODO: print oldest id or \"none\" */ }\n        else if (cmd == \"latest\") { /* TODO */ }\n        else if (cmd == \"dropped\") { /* TODO */ }\n        else { /* size: TODO */ }\n    }\n    return 0;\n}\n", **ROB_EXACT),

P("rob-bev-splat", "Lift-Splat BEV Pooling", "Medium", "BEV / 3D Perception", 14,
  "<p>The “splat” step of Lift-Splat-Shoot: scatter lifted 3D points into a top-down BEV grid by <strong>sum-pooling</strong> their features. The grid spans <code>[x_min,x_max) x [y_min,y_max)</code> in cells of side <code>cell</code> (so <code>W=(x_max-x_min)/cell</code> columns, <code>H=(y_max-y_min)/cell</code> rows). Point (x,y) lands in column <code>floor((x-x_min)/cell)</code>, row <code>floor((y-y_min)/cell)</code>; add its feature to that cell. Drop points outside the grid.</p>",
  "Line 1: x_min x_max y_min y_max cell. Line 2: n. Next n lines: x y f.",
  "H rows (row 0 = lowest y first), each W summed features formatted to one decimal, space-separated.",
  ref_rob_bev_splat,
  [("0 4 0 4 2\n5\n0.5 0.5 1.0\n3.0 0.5 2.0\n1.0 3.0 3.0\n3.5 3.5 0.5\n5.0 1.0 9.0\n", True),
   ("0 2 0 2 1\n4\n0.1 0.1 1.0\n0.9 0.2 2.0\n1.5 1.5 4.0\n-1.0 0.0 5.0\n", True),
   ("0 2 0 2 2\n1\n1.0 1.0 7.5\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    x_min = float(data[0]); x_max = float(data[1])\n    y_min = float(data[2]); y_max = float(data[3]); cell = float(data[4])\n    n = int(data[5]); idx = 6\n    W = round((x_max - x_min) / cell)\n    H = round((y_max - y_min) / cell)\n    grid = [[0.0] * W for _ in range(H)]\n    for _ in range(n):\n        x = float(data[idx]); y = float(data[idx+1]); f = float(data[idx+2]); idx += 3\n        # TODO: col,row = cell of (x,y); drop if out of [0,W)x[0,H), else grid[row][col] += f\n    # TODO: print H rows (row 0 = lowest y first), each W sums formatted with one decimal\n\nmain()\n",
  "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    double xmin, xmax, ymin, ymax, cell;\n    cin >> xmin >> xmax >> ymin >> ymax >> cell;\n    int n; cin >> n;\n    int W = (int)llround((xmax - xmin) / cell);\n    int H = (int)llround((ymax - ymin) / cell);\n    vector<vector<double>> grid(H, vector<double>(W, 0.0));\n    for (int i = 0; i < n; i++) {\n        double x, y, f; cin >> x >> y >> f;\n        // TODO: col,row = cell of (x,y); drop if out of bounds, else grid[row][col] += f\n    }\n    // TODO: print H rows (row 0 first), each W sums via printf(\"%.1f\")\n    return 0;\n}\n", **ROB_EXACT),

P("rob-bev-project", "Project 3D Points to Camera", "Medium", "BEV / 3D Perception", 14,
  "<p>The backward-projection core of BEVFormer/DETR3D: sample image features by projecting 3D reference points into a camera. Given a 3x4 projection matrix <code>P</code> (row-major), compute <code>h = P*[X,Y,Z,1]</code>. The point is <strong>visible</strong> only if its camera depth <code>h[2] &gt; 0</code> and the pixel <code>(u,v) = (h[0]/h[2], h[1]/h[2])</code> lies inside the image (<code>0 &lt;= u &lt; W</code>, <code>0 &lt;= v &lt; H</code>). Print the visible points in input order.</p>",
  "Line 1: W H. Line 2: 12 floats = P row-major (3 rows of 4). Line 3: n. Next n lines: X Y Z.",
  "For each visible point: '<index> <u> <v>' with u,v to two decimals, one per line.",
  ref_rob_bev_project,
  [("100 100\n100 0 50 0 0 100 50 0 0 0 1 0\n4\n0 0 10\n1 0 10\n0 0 -5\n10 0 10\n", True),
   ("100 100\n100 0 50 0 0 100 50 0 0 0 1 0\n2\n0 0 1\n0 0 0\n", True),
   ("200 200\n100 0 100 0 0 100 100 0 0 0 1 0\n1\n0 0 2\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    W = int(data[0]); H = int(data[1]); idx = 2\n    P = [float(data[idx + i]) for i in range(12)]; idx += 12\n    n = int(data[idx]); idx += 1\n    out = []\n    for i in range(n):\n        X = float(data[idx]); Y = float(data[idx+1]); Z = float(data[idx+2]); idx += 3\n        # h = P @ [X, Y, Z, 1]; depth = h[2]\n        # TODO: if depth > 0 and 0 <= u < W and 0 <= v < H:\n        #           out.append(f\"{i} {u:.2f} {v:.2f}\")\n    print(\"\\n\".join(out))\n\nmain()\n",
  "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    int W, H; cin >> W >> H;\n    double P[12];\n    for (int i = 0; i < 12; i++) cin >> P[i];\n    int n; cin >> n;\n    for (int i = 0; i < n; i++) {\n        double X, Y, Z; cin >> X >> Y >> Z;\n        // h0 = P0*X+P1*Y+P2*Z+P3; h1 = ...; depth = P8*X+P9*Y+P10*Z+P11\n        // TODO: if depth > 0 and pixel inside image, printf(\"%d %.2f %.2f\\n\", i, u, v);\n    }\n    return 0;\n}\n", category="robotics", checker="float", tol=0.01),

# ----------------------------------------------------------------------------
# Week 13 — LeetCode patterns: one canonical, most-asked problem per technique
# ----------------------------------------------------------------------------
def ref_three_sum():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = sorted(map(int, d[1:1+n]))
    res = []
    for i in range(n):
        if i > 0 and a[i] == a[i-1]:
            continue
        l, r = i+1, n-1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append((a[i], a[l], a[r])); l += 1; r -= 1
                while l < r and a[l] == a[l-1]: l += 1
                while l < r and a[r] == a[r+1]: r -= 1
    print("\n".join("%d %d %d" % t for t in res))

def ref_longest_substring():
    import sys
    d = sys.stdin.read().split()
    s = d[0]
    seen = {}; left = best = 0
    for r, c in enumerate(s):
        if c in seen and seen[c] >= left:
            left = seen[c] + 1
        seen[c] = r
        best = max(best, r - left + 1)
    print(best)

def ref_rotting_oranges():
    import sys
    from collections import deque
    d = sys.stdin.read().split()
    rows = int(d[0]); cols = int(d[1]); vals = list(map(int, d[2:2+rows*cols]))
    g = [vals[i*cols:(i+1)*cols] for i in range(rows)]
    q = deque(); fresh = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 2: q.append((r, c, 0))
            elif g[r][c] == 1: fresh += 1
    t = 0
    while q:
        r, c, tt = q.popleft(); t = max(t, tt)
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                g[nr][nc] = 2; fresh -= 1; q.append((nr, nc, tt+1))
    print(-1 if fresh > 0 else t)

def ref_course_schedule_ii():
    import sys, heapq
    d = sys.stdin.read().split()
    n = int(d[0]); m = int(d[1]); idx = 2
    adj = [[] for _ in range(n)]; indeg = [0]*n
    for _ in range(m):
        a = int(d[idx]); b = int(d[idx+1]); idx += 2
        adj[b].append(a); indeg[a] += 1
    h = [i for i in range(n) if indeg[i] == 0]; heapq.heapify(h)
    order = []
    while h:
        u = heapq.heappop(h); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: heapq.heappush(h, v)
    print(" ".join(map(str, order)) if len(order) == n else -1)

def ref_search_rotated():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n])); target = int(d[1+n])
    lo, hi = 0, n-1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            print(mid); return
        if a[lo] <= a[mid]:
            if a[lo] <= target < a[mid]: hi = mid - 1
            else: lo = mid + 1
        else:
            if a[mid] < target <= a[hi]: lo = mid + 1
            else: hi = mid - 1
    print(-1)

def ref_merge_k_lists():
    import sys
    d = sys.stdin.read().split()
    k = int(d[0]); idx = 1; res = []
    for _ in range(k):
        L = int(d[idx]); idx += 1
        res.extend(int(d[idx+j]) for j in range(L)); idx += L
    res.sort()
    print(" ".join(map(str, res)))

def ref_coin_change():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); coins = list(map(int, d[1:1+n])); amount = int(d[1+n])
    INF = amount + 1
    dp = [0] + [INF]*amount
    for x in range(1, amount+1):
        for c in coins:
            if c <= x:
                dp[x] = min(dp[x], dp[x-c] + 1)
    print(dp[amount] if dp[amount] != INF else -1)

def ref_subsets():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n]))
    subs = []
    for mask in range(1 << n):
        subs.append(sorted(a[i] for i in range(n) if mask >> i & 1))
    subs.sort(key=lambda s: (len(s), s))
    print("\n".join(" ".join(map(str, s)) for s in subs))

def ref_top_k_frequent():
    import sys
    from collections import Counter
    d = sys.stdin.read().split()
    n = int(d[0]); k = int(d[1]); a = list(map(int, d[2:2+n]))
    cnt = Counter(a)
    order = sorted(cnt, key=lambda v: (-cnt[v], v))
    print(" ".join(map(str, order[:k])))

def ref_number_of_provinces():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); vals = list(map(int, d[1:1+n*n]))
    M = [vals[i*n:(i+1)*n] for i in range(n)]
    p = list(range(n))
    def find(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for i in range(n):
        for j in range(i+1, n):
            if M[i][j] == 1:
                ri, rj = find(i), find(j)
                if ri != rj: p[ri] = rj
    print(len({find(i) for i in range(n)}))

def ref_jump_game():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1+n]))
    reach = 0
    for i in range(n):
        if i > reach:
            print("false"); return
        reach = max(reach, i + a[i])
    print("true")

P("3sum", "3Sum", "Medium", "Two Pointers", 2,
  "<p>Given an integer array, return <b>all unique triplets</b> <code>(a, b, c)</code> with <code>a + b + c = 0</code>. Print each triplet on its own line with its values in <b>non-decreasing order</b>, and order the triplets in ascending (lexicographic) order. Print nothing if there are none.</p>",
  "Line 1: n. Line 2: n integers.",
  "Each triplet 'a b c' (a<=b<=c) on its own line, triplets sorted ascending.",
  ref_three_sum,
  [("6\n-1 0 1 2 -1 -4\n", True), ("3\n0 0 0\n", True), ("3\n1 2 -1\n", False),
   ("5\n-2 0 1 1 2\n", False), ("4\n1 2 3 4\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    # TODO: print each unique triplet summing to 0 (see statement for ordering)\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print each unique triplet summing to 0 (see statement for ordering)\n    return 0;\n}\n"),

P("longest-substring-no-repeat", "Longest Substring Without Repeating Characters", "Medium", "Sliding Window", 2,
  "<p>Given a string (no spaces), return the <b>length</b> of the longest substring without repeating characters.</p>",
  "Line 1: the string s (no spaces, length >= 1).",
  "The length (an integer).",
  ref_longest_substring,
  [("abcabcbb\n", True), ("bbbbb\n", True), ("pwwkew\n", True), ("dvdf\n", False), ("abba\n", False)],
  PY_HEAD + "    s = data[0]\n    # TODO: print the length of the longest substring without repeats\n\nmain()\n",
  CPP_HEAD + "    string s; cin >> s;\n    // TODO: print the length of the longest substring without repeats\n    return 0;\n}\n"),

P("rotting-oranges", "Rotting Oranges", "Medium", "BFS (multi-source)", 2,
  "<p>In a grid, <code>0</code> = empty, <code>1</code> = fresh orange, <code>2</code> = rotten. Each minute, every fresh orange 4-directionally adjacent to a rotten one becomes rotten. Return the minutes until no fresh orange remains, or <code>-1</code> if some can never rot.</p>",
  "Line 1: rows cols. Next rows lines: cols integers (0/1/2).",
  "The number of minutes, or -1.",
  ref_rotting_oranges,
  [("3 3\n2 1 1\n1 1 0\n0 1 1\n", True), ("3 3\n2 1 1\n0 1 1\n1 0 1\n", True),
   ("1 2\n0 2\n", True), ("1 1\n1\n", False), ("2 2\n2 2\n2 2\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    g = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: multi-source BFS; print minutes or -1\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> g(rows, vector<int>(cols));\n    for (auto& r : g) for (auto& x : r) cin >> x;\n    // TODO: multi-source BFS; print minutes or -1\n    return 0;\n}\n"),

P("course-schedule-ii", "Course Schedule II", "Medium", "DFS / Topological Sort", 2,
  "<p>There are <code>n</code> courses (0..n-1). Each prerequisite pair <code>a b</code> means course <code>b</code> must be taken before course <code>a</code>. Return a valid order to finish all courses; if several exist, return the <b>lexicographically smallest</b> (always take the available course with the smallest index next). Print <code>-1</code> if it is impossible (a cycle).</p>",
  "Line 1: n m (courses, number of prerequisite pairs). Next m lines: 'a b' (take b before a).",
  "The order on one line (space-separated), or -1.",
  ref_course_schedule_ii,
  [("2 1\n1 0\n", True), ("4 4\n1 0\n2 0\n3 1\n3 2\n", True), ("2 2\n1 0\n0 1\n", True),
   ("3 0\n", False), ("1 0\n", False)],
  PY_HEAD + "    n = int(data[0]); m = int(data[1]); idx = 2\n    edges = []\n    for _ in range(m):\n        a = int(data[idx]); b = int(data[idx+1]); idx += 2\n        edges.append((a, b))  # take b before a\n    # TODO: lexicographically smallest topological order, or -1\n\nmain()\n",
  CPP_HEAD + "    int n, m; cin >> n >> m;\n    vector<vector<int>> adj(n);\n    vector<int> indeg(n, 0);\n    for (int i = 0; i < m; i++) {\n        int a, b; cin >> a >> b; // take b before a\n        adj[b].push_back(a); indeg[a]++;\n    }\n    // TODO: lexicographically smallest topological order, or -1\n    return 0;\n}\n"),

P("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", "Medium", "Binary Search", 2,
  "<p>An ascending array of <b>distinct</b> integers was rotated at an unknown pivot. Given a target, return its <b>index</b>, or <code>-1</code> if absent. Aim for O(log n).</p>",
  "Line 1: n. Line 2: n integers (rotated sorted). Line 3: target.",
  "The index of target, or -1.",
  ref_search_rotated,
  [("7\n4 5 6 7 0 1 2\n0\n", True), ("7\n4 5 6 7 0 1 2\n3\n", True), ("5\n3 4 5 1 2\n1\n", True),
   ("1\n5\n5\n", False), ("1\n5\n6\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    target = int(data[1+n])\n    # TODO: binary search the rotated array; print index or -1\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int target; cin >> target;\n    // TODO: binary search the rotated array; print index or -1\n    return 0;\n}\n"),

P("merge-k-sorted-lists", "Merge k Sorted Lists", "Hard", "Divide & Conquer / Heap", 2,
  "<p>Merge <code>k</code> ascending-sorted lists into one ascending-sorted sequence. Print the merged values on one line; print nothing if every list is empty.</p>",
  "Line 1: k. Next k lines: 'L v1 v2 ... vL' (length then L sorted integers).",
  "The merged sorted values, space-separated on one line.",
  ref_merge_k_lists,
  [("3\n3 1 4 5\n3 1 3 4\n2 2 6\n", True), ("1\n3 -5 0 7\n", True), ("0\n", True),
   ("2\n0\n0\n", False), ("2\n2 1 2\n3 1 3 5\n", False)],
  PY_HEAD + "    k = int(data[0]); idx = 1; lists = []\n    for _ in range(k):\n        L = int(data[idx]); idx += 1\n        lists.append(list(map(int, data[idx:idx+L]))); idx += L\n    # TODO: merge all lists in sorted order; print on one line\n\nmain()\n",
  CPP_HEAD + "    int k; cin >> k;\n    vector<int> all;\n    for (int i = 0; i < k; i++) {\n        int L; cin >> L;\n        for (int j = 0; j < L; j++) { int v; cin >> v; all.push_back(v); }\n    }\n    // TODO: output all values in sorted (merged) order on one line\n    return 0;\n}\n"),

P("coin-change", "Coin Change", "Medium", "Dynamic Programming", 2,
  "<p>Given coin denominations and a target <code>amount</code>, return the <b>fewest coins</b> that sum to it (each coin usable unlimited times), or <code>-1</code> if it cannot be made.</p>",
  "Line 1: n. Line 2: n coin values. Line 3: amount.",
  "The minimum number of coins, or -1.",
  ref_coin_change,
  [("3\n1 2 5\n11\n", True), ("1\n2\n3\n", True), ("1\n1\n0\n", True),
   ("4\n2 5 10 1\n27\n", False), ("2\n3 7\n5\n", False)],
  PY_HEAD + "    n = int(data[0])\n    coins = list(map(int, data[1:1+n]))\n    amount = int(data[1+n])\n    # TODO: DP for fewest coins; print count or -1\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> coins(n);\n    for (auto& x : coins) cin >> x;\n    int amount; cin >> amount;\n    // TODO: DP for fewest coins; print count or -1\n    return 0;\n}\n"),

P("subsets", "Subsets", "Medium", "Backtracking", 2,
  "<p>Given an array of <b>distinct</b> integers, print <b>all</b> subsets (the power set). Print each subset's values in ascending order, space-separated, on its own line; print the empty subset as an empty line. Order the lines by subset <b>size ascending</b>, breaking ties by ascending values (so the empty subset comes first).</p>",
  "Line 1: n. Line 2: n distinct integers.",
  "All 2^n subsets, one per line (see statement for ordering).",
  ref_subsets,
  [("3\n1 2 3\n", True), ("1\n5\n", True), ("2\n3 1\n", True), ("0\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    # TODO: print every subset (see statement for ordering)\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print every subset (see statement for ordering)\n    return 0;\n}\n"),

P("top-k-frequent", "Top K Frequent Elements", "Medium", "Heap / Top-K", 2,
  "<p>Given an integer array and <code>k</code>, return the <code>k</code> most frequent values. Break frequency ties by the <b>smaller value</b> first, and print the result in order of <b>decreasing frequency</b>, then increasing value.</p>",
  "Line 1: n k. Line 2: n integers.",
  "The k values, space-separated on one line.",
  ref_top_k_frequent,
  [("6 2\n1 1 1 2 2 3\n", True), ("1 1\n1\n", True), ("6 2\n4 4 5 5 6 6\n", True),
   ("7 3\n5 3 1 1 1 3 3\n", False)],
  PY_HEAD + "    n = int(data[0]); k = int(data[1])\n    a = list(map(int, data[2:2+n]))\n    # TODO: print the k most frequent values (see statement for tie-breaking/order)\n\nmain()\n",
  CPP_HEAD + "    int n, k; cin >> n >> k;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: print the k most frequent values (see statement for tie-breaking/order)\n    return 0;\n}\n"),

P("number-of-provinces", "Number of Provinces", "Medium", "Union-Find", 2,
  "<p>An <code>n x n</code> matrix <code>M</code> has <code>M[i][j] = 1</code> if cities <code>i</code> and <code>j</code> are directly connected. A <b>province</b> is a connected group of cities. Return the number of provinces.</p>",
  "Line 1: n. Next n lines: n integers (0/1), the isConnected matrix.",
  "The number of provinces.",
  ref_number_of_provinces,
  [("3\n1 1 0\n1 1 0\n0 0 1\n", True), ("3\n1 0 0\n0 1 0\n0 0 1\n", True), ("1\n1\n", True),
   ("4\n1 1 0 0\n1 1 0 0\n0 0 1 1\n0 0 1 1\n", False)],
  PY_HEAD + "    n = int(data[0])\n    vals = list(map(int, data[1:1+n*n]))\n    M = [vals[i*n:(i+1)*n] for i in range(n)]\n    # TODO: count connected components (union-find or DFS)\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<vector<int>> M(n, vector<int>(n));\n    for (auto& r : M) for (auto& x : r) cin >> x;\n    // TODO: count connected components (union-find or DFS)\n    return 0;\n}\n"),

P("jump-game", "Jump Game", "Medium", "Greedy", 2,
  "<p>Each element is the maximum jump length from that index. Starting at index 0, return <code>true</code> if you can reach the last index, else <code>false</code>.</p>",
  "Line 1: n. Line 2: n non-negative integers.",
  "'true' or 'false'.",
  ref_jump_game,
  [("5\n2 3 1 1 4\n", True), ("5\n3 2 1 0 4\n", True), ("1\n0\n", True),
   ("3\n0 1 2\n", False), ("2\n1 0\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    # TODO: greedily track the farthest reachable index; print 'true'/'false'\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: greedily track the farthest reachable index; print true/false\n    return 0;\n}\n"),

# ----------------------------------------------------------------------------
# Applied Intuition company set (week 18). Sourced from interviewsolver.com.
# stdin->stdout, exact-judge friendly. A few LeetCode originals are adapted to a
# deterministic variant (noted in the statement) so a single exact judge works.
# ----------------------------------------------------------------------------
class _TN:
    __slots__ = ("v", "l", "r")
    def __init__(self, v): self.v = v; self.l = None; self.r = None

def _build_tree(tokens):
    """LeetCode level-order serialization with 'null' for missing children."""
    from collections import deque
    if not tokens or tokens[0] == "null":
        return None
    root = _TN(int(tokens[0])); q = deque([root]); i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens):
            t = tokens[i]; i += 1
            if t != "null": node.l = _TN(int(t)); q.append(node.l)
        if i < len(tokens):
            t = tokens[i]; i += 1
            if t != "null": node.r = _TN(int(t)); q.append(node.r)
    return root

def ref_all_nodes_distance_k():
    import sys
    from collections import deque, defaultdict
    lines = sys.stdin.read().split("\n")
    root = _build_tree(lines[0].split())
    target = int(lines[1]); k = int(lines[2])
    graph = defaultdict(list)
    def dfs(node, par):
        if not node: return
        if par is not None:
            graph[node.v].append(par.v); graph[par.v].append(node.v)
        dfs(node.l, node); dfs(node.r, node)
    dfs(root, None)
    seen = {target}; q = deque([(target, 0)]); res = []
    while q:
        v, d = q.popleft()
        if d == k: res.append(v); continue
        for nb in graph[v]:
            if nb not in seen: seen.add(nb); q.append((nb, d + 1))
    print(" ".join(map(str, sorted(res))))

P("all-nodes-distance-k", "All Nodes Distance K in Binary Tree", "Medium", "Tree / BFS", 18,
  "<p>Given the root of a binary tree (values are unique), a <code>target</code> value, and an integer <code>k</code>, return all node values that are distance <code>k</code> from the target node, in <b>ascending order</b>.</p>",
  "Line 1: level-order tree, space-separated, 'null' for missing. Line 2: target value. Line 3: k.",
  "The values at distance k, ascending and space-separated (blank line if none).",
  ref_all_nodes_distance_k,
  [("3 5 1 6 2 0 8 null null 7 4\n5\n2\n", True), ("3 5 1 6 2 0 8 null null 7 4\n5\n0\n", True),
   ("1\n1\n1\n", False), ("0 1 null 3 2\n2\n1\n", False)],
  "import sys\n\ndef main():\n    lines = sys.stdin.read().split('\\n')\n    tokens = lines[0].split()\n    target = int(lines[1]); k = int(lines[2])\n    # TODO: build tree, add parent links, BFS k steps; print values ascending\n\nmain()\n",
  CPP_HEAD + "    string line; getline(cin, line);\n    long long target, k; cin >> target >> k;\n    // TODO: parse the level-order tokens in `line`, BFS k steps; print ascending\n    return 0;\n}\n"),

def ref_diameter():
    import sys
    root = _build_tree(sys.stdin.read().split("\n")[0].split())
    best = [0]
    def depth(node):
        if not node: return 0
        l = depth(node.l); r = depth(node.r)
        best[0] = max(best[0], l + r)
        return 1 + max(l, r)
    depth(root)
    print(best[0])

P("diameter-of-binary-tree", "Diameter of Binary Tree", "Easy", "Tree / DFS", 18,
  "<p>Return the length of the <b>diameter</b> of a binary tree: the number of edges on the longest path between any two nodes (it need not pass through the root).</p>",
  "Line 1: level-order tree, space-separated, 'null' for missing.",
  "The diameter (edge count).",
  ref_diameter,
  [("1 2 3 4 5\n", True), ("1 2\n", True), ("1\n", False), ("1 2 3 4 null null 5 6 null null 7\n", False)],
  "import sys\n\ndef main():\n    tokens = sys.stdin.read().split('\\n')[0].split()\n    # TODO: build tree; DFS returning depth while tracking max(l+r)\n\nmain()\n",
  CPP_HEAD + "    string line; getline(cin, line);\n    // TODO: parse the level-order tokens; DFS depth while tracking max(l+r)\n    return 0;\n}\n"),

def ref_combination_sum():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); cand = sorted(map(int, d[1:1 + n])); target = int(d[1 + n])
    res = []
    def bt(start, remain, path):
        if remain == 0: res.append(list(path)); return
        for i in range(start, len(cand)):
            if cand[i] > remain: break
            path.append(cand[i]); bt(i, remain - cand[i], path); path.pop()
    bt(0, target, [])
    res.sort()
    print("\n".join(" ".join(map(str, c)) for c in res))

P("combination-sum", "Combination Sum", "Medium", "Backtracking", 18,
  "<p>Given distinct positive integers and a target, return every combination (each number may be reused unlimited times) that sums to the target. Print each combination in non-decreasing order, one per line, with combinations sorted lexicographically.</p>",
  "Line 1: n. Line 2: n distinct integers. Line 3: target.",
  "Each combination on its own line, numbers ascending, combinations sorted (blank if none).",
  ref_combination_sum,
  [("4\n2 3 6 7\n7\n", True), ("3\n2 3 5\n8\n", True), ("1\n2\n1\n", False), ("2\n3 5\n8\n", False)],
  PY_HEAD + "    n = int(data[0])\n    cand = list(map(int, data[1:1+n]))\n    target = int(data[1+n])\n    # TODO: backtrack (reuse allowed); print each combination sorted, combos sorted\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> cand(n);\n    for (auto& x : cand) cin >> x;\n    int target; cin >> target;\n    // TODO: backtrack (reuse allowed); print combinations\n    return 0;\n}\n"),

def ref_randomized_collection():
    import sys
    from collections import Counter
    data = sys.stdin.read().split("\n")
    q = int(data[0].strip()); cnt = Counter(); out = []
    for i in range(1, q + 1):
        parts = data[i].split(); op = parts[0]; x = int(parts[1])
        if op == "insert":
            out.append("1" if cnt[x] == 0 else "0"); cnt[x] += 1
        elif op == "remove":
            if cnt[x] > 0: cnt[x] -= 1; out.append("1")
            else: out.append("0")
        else:  # count
            out.append(str(cnt[x]))
    print("\n".join(out))

P("insert-delete-getrandom-duplicates", "Insert Delete GetRandom O(1) - Duplicates Allowed", "Hard", "Hash Table / Design", 18,
  "<p>Design a multiset supporting O(1) <code>insert</code>, <code>remove</code>, and membership counts. <i>Adapted for deterministic judging:</i> the random draw is replaced by a <code>count</code> query, so only the O(1) bookkeeping is tested.</p><p>Process each op: <code>insert x</code> prints 1 if x was newly added (absent before) else 0, and always inserts one copy; <code>remove x</code> prints 1 if a copy was present (and removes one) else 0; <code>count x</code> prints x's current multiplicity.</p>",
  "Line 1: q. Next q lines: 'insert x', 'remove x', or 'count x'.",
  "One line per op (the value described above).",
  ref_randomized_collection,
  [("7\ninsert 1\ninsert 1\ninsert 2\ncount 1\nremove 1\ncount 1\nremove 3\n", True),
   ("4\ninsert 5\nremove 5\nremove 5\ncount 5\n", True),
   ("3\ninsert 9\ninsert 9\ncount 9\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    q = int(data[0])\n    # TODO: keep a multiset; print per-op results\n\nmain()\n",
  CPP_HEAD + "    int q; cin >> q;\n    // TODO: keep a multiset (unordered_map<int,int>); print per-op results\n    return 0;\n}\n"),

def ref_check_swap():
    import sys
    lines = sys.stdin.read().split("\n")
    s1 = lines[0].strip(); s2 = lines[1].strip()
    if len(s1) != len(s2): print("false"); return
    diff = [(a, b) for a, b in zip(s1, s2) if a != b]
    if len(diff) == 0: print("true")
    elif len(diff) == 2 and diff[0] == diff[1][::-1]: print("true")
    else: print("false")

P("check-string-swap", "Check if One String Swap Can Make Strings Equal", "Easy", "Hash Table / String", 18,
  "<p>Two equal-length strings. Return <code>true</code> if you can make them equal with <b>at most one</b> swap of two characters within a single string, else <code>false</code>.</p>",
  "Line 1: s1. Line 2: s2.",
  "'true' or 'false'.",
  ref_check_swap,
  [("bank\nkanb\n", True), ("attack\ndefend\n", True), ("kelb\nkelb\n", False), ("abcd\nabdc\n", False)],
  "import sys\n\ndef main():\n    lines = sys.stdin.read().split('\\n')\n    s1 = lines[0].strip(); s2 = lines[1].strip()\n    # TODO: count mismatched positions; print 'true'/'false'\n\nmain()\n",
  CPP_HEAD + "    string s1, s2; cin >> s1 >> s2;\n    // TODO: count mismatched positions; print true/false\n    return 0;\n}\n"),

def ref_unique_paths_ii():
    import sys
    d = sys.stdin.read().split()
    rows = int(d[0]); cols = int(d[1]); vals = list(map(int, d[2:2 + rows * cols]))
    g = [vals[i * cols:(i + 1) * cols] for i in range(rows)]
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 1: dp[r][c] = 0
            elif r == 0 and c == 0: dp[r][c] = 1
            else: dp[r][c] = (dp[r - 1][c] if r > 0 else 0) + (dp[r][c - 1] if c > 0 else 0)
    print(dp[rows - 1][cols - 1])

P("unique-paths-ii", "Unique Paths II", "Medium", "Dynamic Programming", 18,
  "<p>Count paths from the top-left to the bottom-right of a grid, moving only <b>right</b> or <b>down</b>. Cells marked <code>1</code> are obstacles and cannot be entered.</p>",
  "Line 1: rows cols. Next rows lines: cols integers (0 = open, 1 = obstacle).",
  "The number of unique paths.",
  ref_unique_paths_ii,
  [("3 3\n0 0 0\n0 1 0\n0 0 0\n", True), ("2 2\n0 1\n0 0\n", True), ("1 1\n0\n", False), ("2 2\n1 0\n0 0\n", False)],
  PY_HEAD + "    rows = int(data[0]); cols = int(data[1])\n    vals = list(map(int, data[2:2+rows*cols]))\n    g = [vals[i*cols:(i+1)*cols] for i in range(rows)]\n    # TODO: DP over the grid, obstacles contribute 0; print paths\n\nmain()\n",
  CPP_HEAD + "    int rows, cols; cin >> rows >> cols;\n    vector<vector<int>> g(rows, vector<int>(cols));\n    for (auto& r : g) for (auto& x : r) cin >> x;\n    // TODO: DP over the grid; print number of paths\n    return 0;\n}\n"),

def ref_nested_weight_ii():
    import sys, json
    data = json.loads(sys.stdin.read().strip())
    def maxdepth(x):
        best = 1
        for e in x:
            if isinstance(e, list): best = max(best, 1 + maxdepth(e))
        return best
    md = maxdepth(data); total = 0
    def dfs(x, depth):
        nonlocal total
        for e in x:
            if isinstance(e, int): total += e * (md - depth + 1)
            else: dfs(e, depth + 1)
    dfs(data, 1)
    print(total)

P("nested-list-weight-sum-ii", "Nested List Weight Sum II", "Medium", "DFS / Stack", 18,
  "<p>Each integer in a nested list has a weight based on its depth, but <b>reversed</b>: leaf-level integers weigh the least. Weight = <code>maxDepth - depth + 1</code>. Return the sum of each integer times its weight.</p>",
  "Line 1: a nested list in JSON bracket notation, e.g. [1,[4,[6]]].",
  "The weighted sum.",
  ref_nested_weight_ii,
  [("[1,[4,[6]]]\n", True), ("[[1,1],2,[1,1]]\n", True), ("[5]\n", False), ("[[3,[2,[1]]]]\n", False)],
  "import sys, json\n\ndef main():\n    data = json.loads(sys.stdin.read().strip())\n    # TODO: find max depth, then sum value*(maxDepth-depth+1)\n\nmain()\n",
  CPP_HEAD + "    string s; getline(cin, s);\n    // TODO: parse the bracket string; weight = maxDepth - depth + 1\n    return 0;\n}\n"),

def ref_string_compression():
    import sys
    s = sys.stdin.read().split("\n")[0]
    out = []; i = 0; n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]: j += 1
        cnt = j - i
        out.append(s[i] + (str(cnt) if cnt > 1 else "")); i = j
    print("".join(out))

P("string-compression", "String Compression", "Medium", "Two Pointers / String", 18,
  "<p>Run-length compress a string: each maximal run of a repeated character becomes the character followed by the run length (length omitted when it is 1). Print the compressed string. E.g. <code>aabbbcccc</code> &rarr; <code>a2b3c4</code>.</p>",
  "Line 1: the string (no spaces).",
  "The compressed string.",
  ref_string_compression,
  [("aabbbcccc\n", True), ("abc\n", True), ("aaaaaa\n", False), ("aabbccdd\n", False)],
  "import sys\n\ndef main():\n    s = sys.stdin.read().split('\\n')[0]\n    # TODO: walk runs with two pointers; append char + count(if>1)\n\nmain()\n",
  CPP_HEAD + "    string s; getline(cin, s);\n    // TODO: walk runs; append char + count(if>1)\n    return 0;\n}\n"),

def ref_min_abs_diff():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = sorted(map(int, d[1:1 + n]))
    best = min(a[i + 1] - a[i] for i in range(n - 1))
    res = [(a[i], a[i + 1]) for i in range(n - 1) if a[i + 1] - a[i] == best]
    print("\n".join(f"{x} {y}" for x, y in res))

P("minimum-absolute-difference", "Minimum Absolute Difference", "Easy", "Array / Sorting", 18,
  "<p>Given an array of distinct integers, find every pair (a, b) with a &lt; b whose absolute difference equals the <b>minimum</b> absolute difference of any pair. Print pairs in ascending order of the smaller element.</p>",
  "Line 1: n. Line 2: n distinct integers.",
  "Each qualifying pair 'a b' on its own line, ascending.",
  ref_min_abs_diff,
  [("4\n4 2 1 3\n", True), ("3\n1 3 6\n", True), ("5\n3 8 -10 23 19\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = sorted(map(int, data[1:1+n]))\n    # TODO: min adjacent gap after sort; print all pairs with that gap\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    // TODO: sort, find min adjacent gap, print all such pairs\n    return 0;\n}\n"),

def ref_search_insert():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); a = list(map(int, d[1:1 + n])); target = int(d[1 + n])
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target: lo = mid + 1
        else: hi = mid
    print(lo)

P("search-insert-position", "Search Insert Position", "Easy", "Binary Search", 18,
  "<p>Given a sorted array of distinct integers and a target, return the index where it is found, or the index where it would be inserted to keep the array sorted. O(log n).</p>",
  "Line 1: n. Line 2: n sorted distinct integers. Line 3: target.",
  "The index (0-based).",
  ref_search_insert,
  [("4\n1 3 5 6\n5\n", True), ("4\n1 3 5 6\n2\n", True), ("4\n1 3 5 6\n7\n", False), ("1\n1\n0\n", False)],
  PY_HEAD + "    n = int(data[0])\n    a = list(map(int, data[1:1+n]))\n    target = int(data[1+n])\n    # TODO: lower-bound binary search; print the index\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<int> a(n);\n    for (auto& x : a) cin >> x;\n    int target; cin >> target;\n    // TODO: lower-bound binary search; print index\n    return 0;\n}\n"),

def ref_snake_game():
    import sys
    from collections import deque
    data = sys.stdin.read().split("\n")
    w, h = map(int, data[0].split())
    F = int(data[1].strip()); idx = 2; food = []
    for _ in range(F):
        r, c = map(int, data[idx].split()); idx += 1; food.append((r, c))
    M = int(data[idx].strip()); idx += 1
    moves = [data[idx + i].strip() for i in range(M)]
    body = deque([(0, 0)]); occ = {(0, 0)}
    score = 0; fi = 0; out = []
    dirs = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    for mv in moves:
        dr, dc = dirs[mv]; hr, hc = body[-1]; nr, nc = hr + dr, hc + dc
        if nr < 0 or nr >= h or nc < 0 or nc >= w:
            out.append(-1); break
        eat = fi < len(food) and (nr, nc) == food[fi]
        if not eat:
            tail = body.popleft(); occ.discard(tail)
        if (nr, nc) in occ:
            out.append(-1); break
        body.append((nr, nc)); occ.add((nr, nc))
        if eat: score += 1; fi += 1
        out.append(score)
    print(" ".join(map(str, out)))

P("design-snake-game", "Design Snake Game", "Medium", "Array / Queue / Design", 18,
  "<p>Simulate the Snake game on a <code>width x height</code> board. The snake starts length 1 at cell (0,0). Food appears at given cells <b>in order</b>; eating one grows the snake and scores a point. Moving into a wall or into the snake's own body ends the game. Print the score after each move; on game over print <code>-1</code> and stop.</p>",
  "Line 1: width height. Line 2: F. Next F lines: 'r c' food cells (in order). Next line: M. Next M lines: a move (U/D/L/R).",
  "Score after each move, space-separated; ends with -1 if the game is lost.",
  ref_snake_game,
  [("3 2\n2\n1 2\n0 1\n5\nR\nD\nR\nU\nL\n", True), ("3 3\n1\n0 1\n2\nR\nR\n", True),
   ("2 2\n0\n2\nR\nD\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    w, h = map(int, data[0].split())\n    # TODO: simulate the snake with a deque body + occupancy set\n\nmain()\n",
  CPP_HEAD + "    int w, h; cin >> w >> h;\n    int F; cin >> F;\n    // TODO: read food, moves; simulate with a deque body + occupancy set\n    return 0;\n}\n"),

def ref_reorganize_feasible():
    import sys
    from collections import Counter
    s = sys.stdin.read().split("\n")[0].strip()
    n = len(s); c = Counter(s)
    print("true" if n > 0 and max(c.values()) <= (n + 1) // 2 else ("true" if n == 0 else "false"))

P("reorganize-string", "Reorganize String", "Medium", "Greedy / Heap", 18,
  "<p><i>Adapted for deterministic judging:</i> report whether the string <b>can</b> be rearranged so that no two adjacent characters are the same. (The construction is the natural follow-up; feasibility is the key insight: it is possible iff the most frequent character appears at most &lceil;n/2&rceil; times.)</p>",
  "Line 1: the string.",
  "'true' if a valid rearrangement exists, else 'false'.",
  ref_reorganize_feasible,
  [("aab\n", True), ("aaab\n", True), ("aaabc\n", False), ("aaaabbc\n", False)],
  "import sys\nfrom collections import Counter\n\ndef main():\n    s = sys.stdin.read().split('\\n')[0].strip()\n    # TODO: print 'true' iff max frequency <= (n+1)//2\n\nmain()\n",
  CPP_HEAD + "    string s; getline(cin, s);\n    // TODO: print true iff max frequency <= (n+1)/2\n    return 0;\n}\n"),

def ref_repeat_limit():
    import sys, heapq
    from collections import Counter
    lines = sys.stdin.read().split("\n")
    s = lines[0].strip(); limit = int(lines[1].strip())
    cnt = Counter(s)
    heap = [(-ord(ch), ch) for ch in cnt]
    heapq.heapify(heap); res = []
    while heap:
        negord, ch = heapq.heappop(heap)
        use = min(cnt[ch], limit)
        res.append(ch * use); cnt[ch] -= use
        if cnt[ch] > 0:
            if not heap: break
            no2, ch2 = heapq.heappop(heap)
            res.append(ch2); cnt[ch2] -= 1
            if cnt[ch2] > 0: heapq.heappush(heap, (no2, ch2))
            heapq.heappush(heap, (negord, ch))
    print("".join(res))

P("construct-string-repeat-limit", "Construct String With Repeat Limit", "Medium", "Greedy / Heap", 18,
  "<p>Using all the characters of <code>s</code>, build the <b>lexicographically largest</b> string in which no character is used more than <code>repeatLimit</code> times in a row.</p>",
  "Line 1: s. Line 2: repeatLimit.",
  "The lexicographically largest valid string.",
  ref_repeat_limit,
  [("cczazcc\n3\n", True), ("aababab\n2\n", True), ("zzzzz\n2\n", False), ("aaabbbccc\n1\n", False)],
  "import sys\nfrom collections import Counter\n\ndef main():\n    lines = sys.stdin.read().split('\\n')\n    s = lines[0].strip(); limit = int(lines[1].strip())\n    # TODO: greedily take the largest char up to `limit`, break runs with next char\n\nmain()\n",
  CPP_HEAD + "    string s; getline(cin, s);\n    int limit; cin >> limit;\n    // TODO: greedily build the largest string with runs capped at limit\n    return 0;\n}\n"),

def ref_koko():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); piles = list(map(int, d[1:1 + n])); H = int(d[1 + n])
    lo, hi = 1, max(piles)
    def hours(k): return sum((p + k - 1) // k for p in piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= H: hi = mid
        else: lo = mid + 1
    print(lo)

P("koko-eating-bananas", "Koko Eating Bananas", "Medium", "Binary Search", 18,
  "<p>Koko eats at <code>k</code> bananas/hour, finishing at most one pile per hour. Given the piles and <code>h</code> total hours, return the <b>minimum</b> integer speed <code>k</code> that finishes every pile within h hours.</p>",
  "Line 1: n. Line 2: n integers (pile sizes). Line 3: h.",
  "The minimum eating speed k.",
  ref_koko,
  [("4\n3 6 7 11\n8\n", True), ("5\n30 11 23 4 20\n5\n", True), ("5\n30 11 23 4 20\n6\n", False), ("1\n1000000000\n2\n", False)],
  PY_HEAD + "    n = int(data[0])\n    piles = list(map(int, data[1:1+n]))\n    h = int(data[1+n])\n    # TODO: binary search k in [1, max(piles)]; hours(k) = sum(ceil(p/k))\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<long long> piles(n);\n    for (auto& x : piles) cin >> x;\n    long long h; cin >> h;\n    // TODO: binary search minimal k with total hours <= h\n    return 0;\n}\n"),

def ref_kth_factor():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); k = int(d[1]); cnt = 0
    for i in range(1, n + 1):
        if n % i == 0:
            cnt += 1
            if cnt == k: print(i); return
    print(-1)

P("kth-factor-of-n", "The kth Factor of n", "Medium", "Math / Number Theory", 18,
  "<p>Return the <code>k</code>-th smallest positive integer that divides <code>n</code>, or <code>-1</code> if n has fewer than k divisors.</p>",
  "Line 1: n k.",
  "The kth factor of n, or -1.",
  ref_kth_factor,
  [("12 3\n", True), ("7 2\n", True), ("4 4\n", False), ("1000 3\n", False)],
  PY_HEAD + "    n = int(data[0]); k = int(data[1])\n    # TODO: enumerate divisors 1..n; print the kth or -1\n\nmain()\n",
  CPP_HEAD + "    long long n, k; cin >> n >> k;\n    // TODO: enumerate divisors; print the kth or -1\n    return 0;\n}\n"),

def ref_fraction():
    import sys
    d = sys.stdin.read().split()
    num = int(d[0]); den = int(d[1])
    if num == 0: print("0"); return
    res = []
    if (num < 0) != (den < 0): res.append("-")
    num = abs(num); den = abs(den)
    res.append(str(num // den)); rem = num % den
    if rem == 0: print("".join(res)); return
    res.append("."); seen = {}; frac = []
    while rem != 0:
        if rem in seen:
            frac.insert(seen[rem], "("); frac.append(")"); break
        seen[rem] = len(frac); rem *= 10
        frac.append(str(rem // den)); rem %= den
    res.append("".join(frac)); print("".join(res))

P("fraction-to-recurring-decimal", "Fraction to Recurring Decimal", "Medium", "Hash Table / Math", 18,
  "<p>Given the numerator and denominator of a fraction, return the value as a string. If the fractional part repeats, enclose the repeating block in parentheses. E.g. <code>4/333</code> &rarr; <code>0.(012)</code>.</p>",
  "Line 1: numerator denominator.",
  "The decimal string.",
  ref_fraction,
  [("1 2\n", True), ("4 333\n", True), ("2 1\n", False), ("-50 8\n", False)],
  PY_HEAD + "    num = int(data[0]); den = int(data[1])\n    # TODO: long division; remember remainders to detect the repeating cycle\n\nmain()\n",
  CPP_HEAD + "    long long num, den; cin >> num >> den;\n    // TODO: long division; track remainders to find the repeating cycle\n    return 0;\n}\n"),

def ref_kth_smallest_matrix():
    import sys
    d = sys.stdin.read().split()
    n = int(d[0]); vals = list(map(int, d[1:1 + n * n])); k = int(d[1 + n * n])
    m = [vals[i * n:(i + 1) * n] for i in range(n)]
    lo, hi = m[0][0], m[n - 1][n - 1]
    def count_le(x):
        cnt = 0; r = n - 1; c = 0
        while r >= 0 and c < n:
            if m[r][c] <= x: cnt += r + 1; c += 1
            else: r -= 1
        return cnt
    while lo < hi:
        mid = (lo + hi) // 2
        if count_le(mid) < k: lo = mid + 1
        else: hi = mid
    print(lo)

P("kth-smallest-in-sorted-matrix", "Kth Smallest Element in a Sorted Matrix", "Medium", "Binary Search / Heap", 18,
  "<p>Given an <code>n x n</code> matrix whose rows and columns are each sorted ascending, return the <code>k</code>-th smallest element (in overall sorted order, counting duplicates).</p>",
  "Line 1: n. Next n lines: n integers each. Last line: k.",
  "The kth smallest element.",
  ref_kth_smallest_matrix,
  [("3\n1 5 9\n10 11 13\n12 13 15\n8\n", True), ("2\n-5 -4\n-5 -4\n2\n", True), ("1\n7\n1\n", False), ("3\n1 2 3\n4 5 6\n7 8 9\n5\n", False)],
  PY_HEAD + "    n = int(data[0])\n    vals = list(map(int, data[1:1+n*n]))\n    m = [vals[i*n:(i+1)*n] for i in range(n)]\n    k = int(data[1+n*n])\n    # TODO: binary search on value; count elements <= mid by walking bottom-left\n\nmain()\n",
  CPP_HEAD + "    int n; cin >> n;\n    vector<vector<int>> m(n, vector<int>(n));\n    for (auto& r : m) for (auto& x : r) cin >> x;\n    int k; cin >> k;\n    // TODO: binary search on value; count <= mid via bottom-left walk\n    return 0;\n}\n"),

def ref_rank_teams():
    import sys
    data = sys.stdin.read().split("\n")
    V = int(data[0].strip())
    votes = [data[1 + i].strip() for i in range(V)]
    teams = votes[0]; m = len(teams)
    score = {t: [0] * m for t in teams}
    for v in votes:
        for pos, t in enumerate(v):
            score[t][pos] += 1
    ranked = sorted(teams, key=lambda t: ([-x for x in score[t]], t))
    print("".join(ranked))

P("rank-teams-by-votes", "Rank Teams by Votes", "Medium", "Array / Hash Table / Sorting", 18,
  "<p>Each voter ranks all teams (letters) in order of preference. Rank the teams by number of first-place votes, breaking ties by second-place votes, and so on; if still tied, order alphabetically. Return the final ranking.</p>",
  "Line 1: V (number of votes). Next V lines: a ranking string (a permutation of the team letters).",
  "The final team ranking as a string.",
  ref_rank_teams,
  [("5\nABC\nACB\nABC\nACB\nACB\n", True), ("2\nWXYZ\nXYZW\n", True), ("1\nZMK\n", False), ("3\nBCA\nCAB\nABC\n", False)],
  "import sys\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    V = int(data[0])\n    votes = [data[1+i].strip() for i in range(V)]\n    # TODO: per-team position counts; sort by counts desc, then alphabetically\n\nmain()\n",
  CPP_HEAD + "    int V; cin >> V;\n    vector<string> votes(V);\n    for (auto& s : votes) cin >> s;\n    // TODO: per-team position counts; sort desc, tie-break alphabetically\n    return 0;\n}\n"),

# ----------------------------------------------------------------------------
# Compile-check every C++ starter so users never hit a template compile error
# ----------------------------------------------------------------------------
def _find_cxx():
    """Pick a compiler that ships <bits/stdc++.h> (a GNU libstdc++ header).

    On Linux CI plain `g++` is real GCC and works. On macOS `g++` is an Apple
    Clang shim over libc++, which lacks that header, so prefer any Homebrew
    versioned `g++-NN` (highest version wins) and fall back to `g++`.
    """
    versioned = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        try:
            for name in os.listdir(d):
                m = re.fullmatch(r"g\+\+-(\d+)", name)
                if m and os.access(os.path.join(d, name), os.X_OK):
                    versioned.append((int(m.group(1)), name))
        except OSError:
            continue
    if versioned:
        return max(versioned)[1]
    return "g++"

def compile_check():
    cxx = _find_cxx()
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in PROBLEMS:
            src = os.path.join(tmp, "s.cpp")
            with open(src, "w") as f:
                f.write(p["starter"]["cpp"])
            r = subprocess.run([cxx, "-std=c++17", "-O2", "-o", os.path.join(tmp, "a.out"), src],
                               capture_output=True, text=True)
            if r.returncode != 0:
                failures.append((p["id"], r.stderr.strip().split("\n")[0]))
    return failures

HERE = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_JS = os.path.join(HERE, "problems.js")
CURRICULUM_JS = os.path.join(HERE, "curriculum.js")

def ids_in_problems_js(path):
    """Problem ids currently committed in problems.js (empty if absent)."""
    if not os.path.exists(path):
        return set()
    return set(re.findall(r'"id":\s*"([^"]+)"', open(path).read()))

def pids_in_curriculum(path):
    """Problem ids the in-site plan links to (curriculum.js `pid:` fields)."""
    if not os.path.exists(path):
        return set()
    return set(re.findall(r'\bpid:\s*"([^"]+)"', open(path).read()))

def validate(force):
    """Guard the generator<->problems.js<->curriculum.js contract.

    problems.js is fully regenerated from this file, so anything not defined
    here is lost on the next run, and any curriculum link to a missing id
    silently falls back to the first problem in the UI. Catch both here.
    """
    errors, warnings = [], []

    ids = [p["id"] for p in PROBLEMS]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errors.append("duplicate problem id(s) defined in this file: " + ", ".join(dupes))
    new_ids = set(ids)

    # Problems present in the committed problems.js that this run would drop.
    dropped = sorted(ids_in_problems_js(PROBLEMS_JS) - new_ids)
    if dropped:
        msg = ("problems.js currently contains id(s) this generator does NOT define, "
               "so regenerating would delete them: " + ", ".join(dropped) +
               "\n  -> port them into gen_problems.py, or rerun with --force to drop them.")
        (warnings if force else errors).append(msg)

    # Curriculum links that would 404 to the practice page's fallback problem.
    missing = sorted(pids_in_curriculum(CURRICULUM_JS) - new_ids)
    if missing:
        errors.append("curriculum.js links to pid(s) with no problem defined here "
                      "(in-site links silently fall back to the first problem): " + ", ".join(missing))

    return errors, warnings

if __name__ == "__main__":
    force = "--force" in sys.argv
    check_only = "--check" in sys.argv

    errors, warnings = validate(force)
    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    fails = compile_check()
    if fails:
        print("C++ starter compile failures:")
        for i, e in fails:
            print(f"  {i}: {e}")
        sys.exit(1)
    print(f"All {len(PROBLEMS)} C++ starters compile.")

    banner = "/* AUTO-GENERATED by gen_problems.py. Expected outputs verified by running\n   reference solutions locally. Edit gen_problems.py and rerun to change.\n   Do NOT hand-edit this file: it is overwritten on every run. */\n"
    out = banner + "const PROBLEMS = " + json.dumps(PROBLEMS, indent=2) + ";\n"

    if check_only:
        current = open(PROBLEMS_JS).read() if os.path.exists(PROBLEMS_JS) else ""
        if current != out:
            print("Validation failed:")
            print("  - problems.js is stale: it does not match gen_problems.py output.")
            print("    -> run `python3 gen_problems.py` and commit the regenerated problems.js.")
            sys.exit(1)
        print(f"--check OK: {len(PROBLEMS)} problems; problems.js up to date and consistent with curriculum.js.")
        sys.exit(0)

    with open(PROBLEMS_JS, "w") as f:
        f.write(out)
    total_tests = sum(len(p["tests"]) for p in PROBLEMS)
    print(f"Wrote problems.js: {len(PROBLEMS)} problems, {total_tests} test cases.")
