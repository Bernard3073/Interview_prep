# Week 18 — Perception Coding Drills (KF · IoU/NMS · Association · SORT)

> The coding rounds for a sensor-fusion / MOT role (Kodiak — Senior Autonomy
> Engineer, Perception) are usually *"implement a small piece of the perception
> stack,"* not abstract LeetCode. This note is the drill set: the six problems that
> come up again and again, each with an approach, a clean reference solution, the
> complexity, and the follow-ups interviewers push on. Theory lives in
> [06-state-estimation](06-state-estimation.md) and
> [15-sensor-fusion-mot-autonomous-trucking](15-sensor-fusion-mot-autonomous-trucking.md);
> this is the *write-the-code* companion.

---

## How these rounds actually go

- They start small (a 1D filter, box IoU) and **build up** to a mini-tracker across
  the hour. Expect "now add multiple objects," "now they can be occluded."
- **Say the brute force + complexity out loud first**, name the bottleneck, then
  code. Same reflex as [01-leetcode-patterns](01-leetcode-patterns.md).
- Numerical correctness counts: angle wrapping, symmetric covariance, empty inputs.
  Voicing these edge cases *is* the senior signal.
- Python to move fast; be ready to discuss the **C++** version (allocation in the
  hot loop, `Eigen`, ownership) since the real stack is C++.

---

## Drill 1 — Kalman filter (1D, then constant-velocity)

**Prompt.** Implement a scalar Kalman filter that fuses a noisy position sensor,
then extend it to a constant-velocity model that estimates velocity from position-
only measurements.

**Approach.** Predict pushes the state through the motion model and *grows* `P`;
update blends in the measurement weighted by the Kalman gain. The CV model is the
same equations with `x = [pos, vel]`, `F` advancing position by `v·dt`, and `H`
observing position only — velocity becomes observable *through time*.

:::solution
```python
import numpy as np

class KalmanFilter:
    def __init__(self, x, P, F, H, Q, R):
        self.x, self.P = x, P            # state, covariance
        self.F, self.H = F, H            # motion, measurement models
        self.Q, self.R = Q, R            # process, measurement noise

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x

    def update(self, z):
        y = z - self.H @ self.x                       # innovation
        S = self.H @ self.P @ self.H.T + self.R       # innovation covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)      # Kalman gain
        self.x = self.x + K @ y
        I = np.eye(self.P.shape[0])
        # Joseph form: numerically stable, stays symmetric PSD
        self.P = (I - K @ self.H) @ self.P @ (I - K @ self.H).T + K @ self.R @ K.T
        return self.x

# constant-velocity setup: state [pos, vel], observe pos only
dt = 0.1
kf = KalmanFilter(
    x=np.array([0.0, 0.0]),
    P=np.diag([1.0, 1.0]),
    F=np.array([[1, dt], [0, 1]]),
    H=np.array([[1.0, 0.0]]),
    Q=np.diag([0.01, 0.1]),
    R=np.array([[0.5]]),
)
for z in [1.0, 2.1, 2.9, 4.2]:
    kf.predict()
    kf.update(np.array([z]))
```
```cpp
#include <Eigen/Dense>
using Eigen::MatrixXd;
using Eigen::VectorXd;

class KalmanFilter {
public:
    VectorXd x;                      // state
    MatrixXd P, F, H, Q, R;          // covariance, models, noises

    KalmanFilter(VectorXd x_, MatrixXd P_, MatrixXd F_,
                 MatrixXd H_, MatrixXd Q_, MatrixXd R_)
        : x(std::move(x_)), P(std::move(P_)), F(std::move(F_)),
          H(std::move(H_)), Q(std::move(Q_)), R(std::move(R_)) {}

    void predict() {
        x = F * x;
        P = F * P * F.transpose() + Q;
    }

    void update(const VectorXd& z) {
        const VectorXd y = z - H * x;                     // innovation
        const MatrixXd S = H * P * H.transpose() + R;     // innovation covariance
        const MatrixXd K = P * H.transpose() * S.inverse();  // Kalman gain
        x += K * y;
        const MatrixXd I = MatrixXd::Identity(P.rows(), P.cols());
        const MatrixXd IKH = I - K * H;
        // Joseph form: numerically stable, stays symmetric PSD
        P = IKH * P * IKH.transpose() + K * R * K.transpose();
    }
};

// constant-velocity setup: state [pos, vel], observe pos only
int main() {
    const double dt = 0.1;
    VectorXd x(2); x << 0.0, 0.0;
    MatrixXd P = (MatrixXd(2, 2) << 1, 0, 0, 1).finished();
    MatrixXd F = (MatrixXd(2, 2) << 1, dt, 0, 1).finished();
    MatrixXd H = (MatrixXd(1, 2) << 1, 0).finished();
    MatrixXd Q = (MatrixXd(2, 2) << 0.01, 0, 0, 0.1).finished();
    MatrixXd R = (MatrixXd(1, 1) << 0.5).finished();

    KalmanFilter kf(x, P, F, H, Q, R);
    for (double z : {1.0, 2.1, 2.9, 4.2}) {
        kf.predict();
        kf.update((VectorXd(1) << z).finished());
    }
}
```
:::

**Complexity.** O(n³) in state dim `n` per step (the `S` inverse); `n` is tiny (2–9)
so it's effectively constant.

**Follow-ups they ask.** Why Joseph form? (stays symmetric PSD under finite
precision). What if `R` is huge? (`K→0`, trust the model). How do you get velocity
from position-only measurements? (observability through the motion model over time).
Extend to EKF → linearize `f,h` with Jacobians; see [06](06-state-estimation.md).

---

## Drill 2 — IoU + Non-Max Suppression

**Prompt.** Given boxes `[x1, y1, x2, y2]` with scores, compute IoU and run NMS to
drop duplicate detections.

**Approach.** IoU = intersection area / union area (clamp the overlap to ≥ 0).
NMS: sort by score, greedily keep the top box, discard everything overlapping it
above a threshold, repeat.

:::solution
```python
def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)   # clamp: no negative overlap
    inter = iw * ih
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0

def nms(boxes, scores, thresh=0.5):
    order = sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
    keep = []
    while order:
        i = order.pop(0)          # highest score remaining
        keep.append(i)
        order = [j for j in order if iou(boxes[i], boxes[j]) <= thresh]
    return keep
```
```cpp
#include <algorithm>
#include <array>
#include <numeric>
#include <vector>

using Box = std::array<double, 4>;   // {x1, y1, x2, y2}

double iou(const Box& a, const Box& b) {
    const double ix1 = std::max(a[0], b[0]), iy1 = std::max(a[1], b[1]);
    const double ix2 = std::min(a[2], b[2]), iy2 = std::min(a[3], b[3]);
    const double iw = std::max(0.0, ix2 - ix1);   // clamp: no negative overlap
    const double ih = std::max(0.0, iy2 - iy1);
    const double inter = iw * ih;
    const double area_a = (a[2] - a[0]) * (a[3] - a[1]);
    const double area_b = (b[2] - b[0]) * (b[3] - b[1]);
    const double uni = area_a + area_b - inter;
    return uni > 0.0 ? inter / uni : 0.0;
}

std::vector<int> nms(const std::vector<Box>& boxes,
                     const std::vector<double>& scores, double thresh = 0.5) {
    std::vector<int> order(boxes.size());
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(),
              [&](int i, int j) { return scores[i] > scores[j]; });  // high score first

    std::vector<int> keep;
    std::vector<bool> removed(boxes.size(), false);
    for (int i : order) {
        if (removed[i]) continue;
        keep.push_back(i);
        for (int j : order)
            if (!removed[j] && j != i && iou(boxes[i], boxes[j]) > thresh)
                removed[j] = true;
    }
    return keep;
}
```
:::

**Complexity.** O(n²) worst case (each kept box vs. the rest); fine for detection
counts. Sort is O(n log n).

**Follow-ups.** Edge cases: zero-area boxes, no overlap, identical boxes. Difference
between **hard NMS** and **soft-NMS** (decay scores instead of deleting). Why the
`max(0, ...)` clamp matters (disjoint boxes give negative width). C++: pre-sort
indices, avoid re-allocating the filtered list each pass.

---

## Drill 3 — Data association (greedy, then Hungarian)

**Prompt.** Given a cost matrix of `tracks × detections` (e.g. gated Mahalanobis
or `1 − IoU`), assign detections to tracks. Return matches plus the unmatched on
each side.

**Approach.** Greedy: repeatedly take the globally-cheapest valid pair, remove its
row/column, respect a gating threshold. Optimal one-to-one assignment is the
**Hungarian algorithm** (`scipy.optimize.linear_sum_assignment`) — greedy is the
expected from-scratch answer; naming Hungarian as the optimal upgrade is the senior
signal.

:::solution
```python
import numpy as np

def greedy_match(cost, gate=1e9):
    cost = np.asarray(cost, dtype=float)
    T, D = cost.shape
    matches, used_t, used_d = [], set(), set()
    # candidate pairs cheapest-first, skipping anything above the gate
    pairs = sorted(
        ((cost[t, d], t, d) for t in range(T) for d in range(D) if cost[t, d] <= gate),
        key=lambda p: p[0],
    )
    for c, t, d in pairs:
        if t in used_t or d in used_d:
            continue
        matches.append((t, d)); used_t.add(t); used_d.add(d)
    un_t = [t for t in range(T) if t not in used_t]
    un_d = [d for d in range(D) if d not in used_d]
    return matches, un_t, un_d

def hungarian_match(cost, gate=1e9):
    from scipy.optimize import linear_sum_assignment
    cost = np.asarray(cost, dtype=float)
    rows, cols = linear_sum_assignment(cost)        # minimizes total cost
    matches = [(r, c) for r, c in zip(rows, cols) if cost[r, c] <= gate]
    matched_t = {r for r, _ in matches}
    matched_d = {c for _, c in matches}
    un_t = [t for t in range(cost.shape[0]) if t not in matched_t]
    un_d = [d for d in range(cost.shape[1]) if d not in matched_d]
    return matches, un_t, un_d
```
```cpp
#include <algorithm>
#include <tuple>
#include <vector>

struct Assignment {
    std::vector<std::pair<int, int>> matches;   // (track, detection)
    std::vector<int> unmatched_tracks, unmatched_dets;
};

// Greedy nearest-neighbor. cost[t][d]; pairs above `gate` are excluded.
// The optimal one-to-one upgrade is the Hungarian algorithm (O(n^3)).
Assignment greedy_match(const std::vector<std::vector<double>>& cost,
                        double gate = 1e9) {
    const int T = cost.size();
    const int D = T ? cost[0].size() : 0;

    std::vector<std::tuple<double, int, int>> pairs;    // (cost, track, det)
    for (int t = 0; t < T; ++t)
        for (int d = 0; d < D; ++d)
            if (cost[t][d] <= gate) pairs.emplace_back(cost[t][d], t, d);
    std::sort(pairs.begin(), pairs.end());              // cheapest first

    Assignment out;
    std::vector<bool> used_t(T, false), used_d(D, false);
    for (auto& [c, t, d] : pairs) {
        if (used_t[t] || used_d[d]) continue;
        out.matches.emplace_back(t, d);
        used_t[t] = used_d[d] = true;
    }
    for (int t = 0; t < T; ++t) if (!used_t[t]) out.unmatched_tracks.push_back(t);
    for (int d = 0; d < D; ++d) if (!used_d[d]) out.unmatched_dets.push_back(d);
    return out;
}
```
:::

**Complexity.** Greedy O(TD·log(TD)) from the sort; Hungarian O(n³).

**Follow-ups.** Why greedy can be suboptimal (a cheap early pick blocks two better
pairs). Non-square matrix (more detections than tracks). How the **gate** removes
impossible pairs before assignment (Mahalanobis / chi-square — see
[15](15-sensor-fusion-mot-autonomous-trucking.md)). When to prefer JPDA/MHT (dense
clutter).

---

## Drill 4 — Minimal SORT tracker (the signature question)

**Prompt.** Put drills 1–3 together: a multi-object tracker. Each frame you get
detections (boxes); maintain persistent IDs across frames through birth, matching,
and death.

**Approach.** Tracking-by-detection: predict every track's box forward, associate
detections to tracks by IoU (via drill 3), KF-update matches, birth tracks from
unmatched detections, and delete tracks that miss too many frames. This is the
whole loop from [15](15-sensor-fusion-mot-autonomous-trucking.md) in ~40 lines.

:::solution
```python
class Track:
    _next_id = 0
    def __init__(self, box):
        self.id = Track._next_id; Track._next_id += 1
        self.box = box               # last known box (a real SORT uses a KF here)
        self.hits = 1
        self.misses = 0

class Sort:
    def __init__(self, iou_thresh=0.3, max_misses=3, min_hits=3):
        self.tracks = []
        self.iou_thresh, self.max_misses, self.min_hits = iou_thresh, max_misses, min_hits

    def update(self, detections):
        # 1. PREDICT — (constant-position stub; swap in a KF.predict per track)
        # 2. ASSOCIATE by IoU (cost = 1 - IoU so lower is better)
        cost = [[1 - iou(t.box, d) for d in detections] for t in self.tracks]
        gate = 1 - self.iou_thresh
        matches, un_t, un_d = greedy_match(cost, gate=gate) if self.tracks else ([], [], list(range(len(detections))))

        # 3. UPDATE matched tracks
        for ti, di in matches:
            self.tracks[ti].box = detections[di]      # KF.update(det) in the real thing
            self.tracks[ti].hits += 1
            self.tracks[ti].misses = 0

        # 4. LIFECYCLE — age unmatched tracks, birth new ones, cull the dead
        for ti in un_t:
            self.tracks[ti].misses += 1
        for di in un_d:
            self.tracks.append(Track(detections[di]))
        self.tracks = [t for t in self.tracks if t.misses <= self.max_misses]

        # report confirmed tracks only (M-of-N style)
        return [(t.id, t.box) for t in self.tracks if t.hits >= self.min_hits or t.misses == 0]
```
```cpp
#include <vector>

struct Track {
    int id;
    Box box;              // last known box (a real SORT keeps a KF here)
    int hits = 1;
    int misses = 0;
};

class Sort {
public:
    Sort(double iou_thresh = 0.3, int max_misses = 3, int min_hits = 3)
        : iou_thresh_(iou_thresh), max_misses_(max_misses), min_hits_(min_hits) {}

    std::vector<std::pair<int, Box>> update(const std::vector<Box>& detections) {
        // 1. PREDICT — constant-position stub; swap in KF.predict() per track.
        // 2. ASSOCIATE by IoU (cost = 1 - IoU so lower is better)
        std::vector<std::vector<double>> cost(tracks_.size(),
                                              std::vector<double>(detections.size()));
        for (size_t t = 0; t < tracks_.size(); ++t)
            for (size_t d = 0; d < detections.size(); ++d)
                cost[t][d] = 1.0 - iou(tracks_[t].box, detections[d]);
        Assignment a = greedy_match(cost, 1.0 - iou_thresh_);

        // 3. UPDATE matched tracks
        for (auto& [ti, di] : a.matches) {
            tracks_[ti].box = detections[di];        // KF.update(det) in the real thing
            tracks_[ti].hits++;
            tracks_[ti].misses = 0;
        }

        // 4. LIFECYCLE — age unmatched, birth new, cull the dead
        for (int ti : a.unmatched_tracks) tracks_[ti].misses++;
        for (int di : a.unmatched_dets) tracks_.push_back({next_id_++, detections[di]});
        std::vector<Track> alive;
        for (auto& t : tracks_)
            if (t.misses <= max_misses_) alive.push_back(t);
        tracks_ = std::move(alive);

        // report confirmed tracks only (M-of-N style)
        std::vector<std::pair<int, Box>> out;
        for (auto& t : tracks_)
            if (t.hits >= min_hits_ || t.misses == 0) out.emplace_back(t.id, t.box);
        return out;
    }

private:
    std::vector<Track> tracks_;
    int next_id_ = 0;
    double iou_thresh_;
    int max_misses_, min_hits_;
};
```
:::

**Complexity.** O(T·D) to build the cost matrix + the association cost, per frame.

**Follow-ups.** Where does the KF go? (per-track `predict()`/`update()` on box
state). How do you survive **occlusion**? (coast on prediction, keep the ID, gate
loosely on return — see [15](15-sensor-fusion-mot-autonomous-trucking.md)). Why
`min_hits` before reporting? (suppress flicker/clutter). Add appearance embedding →
DeepSORT. This is where most of the interview time goes — know it cold.

---

## Drill 5 — Mahalanobis gating

**Prompt.** Given a predicted measurement, its innovation covariance `S`, and an
actual measurement, decide whether to accept the association.

**Approach.** Normalized innovation squared `d² = νᵀ S⁻¹ ν`; accept if below a
chi-square threshold for the measurement's degrees of freedom. This is what makes a
cost matrix *gated* before assignment.

:::solution
```python
import numpy as np
from scipy.stats import chi2

def mahalanobis_sq(innov, S):
    innov = np.asarray(innov, dtype=float)
    return float(innov.T @ np.linalg.inv(S) @ innov)

def accept(innov, S, dof, conf=0.99):
    return mahalanobis_sq(innov, S) <= chi2.ppf(conf, dof)   # e.g. dof=2 → ~9.21
```
```cpp
#include <Eigen/Dense>
using Eigen::MatrixXd;
using Eigen::VectorXd;

double mahalanobis_sq(const VectorXd& innov, const MatrixXd& S) {
    return innov.transpose() * S.inverse() * innov;
}

// chi-square 0.99 thresholds by DoF: {1: 6.63, 2: 9.21, 3: 11.34}
bool accept(const VectorXd& innov, const MatrixXd& S, double chi2_thresh) {
    return mahalanobis_sq(innov, S) <= chi2_thresh;   // e.g. dof=2 → 9.21
}
```
:::

**Complexity.** O(m³) in measurement dim `m` (the inverse), `m` tiny.

**Follow-ups.** Why Mahalanobis instead of Euclidean? (normalizes by uncertainty —
a big error along a high-variance axis may be fine). Where does the threshold come
from? (chi-square, `dof` = measurement dimension). Same `S` feeds the Kalman gain,
so you get gating almost for free.

---

## Drill 6 — Time-sync two sensor streams

**Prompt.** Two sensors publish `(timestamp, value)` at different rates. For each
message on stream A, find the nearest-in-time message on stream B within a tolerance
(the "ApproximateTime" problem from [14](14-concurrency-for-robotics.md)).

**Approach.** Both streams are sorted by time → **two pointers**, advancing B while
it gets closer to the current A timestamp. O(n + m), no repeated scans.

:::solution
```python
def time_sync(a, b, tol):
    """a, b: lists of (t, value) sorted by t. Return matched (ta, va, tb, vb)."""
    out, j = [], 0
    for ta, va in a:
        # advance j while the *next* B is closer to ta than the current one
        while j + 1 < len(b) and abs(b[j + 1][0] - ta) <= abs(b[j][0] - ta):
            j += 1
        if b and abs(b[j][0] - ta) <= tol:
            out.append((ta, va, b[j][0], b[j][1]))
    return out
```
```cpp
#include <cmath>
#include <vector>

struct Msg { double t; double value; };
struct Pair { double ta, va, tb, vb; };

// a, b sorted by timestamp. For each a, nearest b within tol. O(n + m).
std::vector<Pair> time_sync(const std::vector<Msg>& a,
                            const std::vector<Msg>& b, double tol) {
    std::vector<Pair> out;
    if (b.empty()) return out;
    size_t j = 0;
    for (const auto& ma : a) {
        // advance j while the next B is closer to ma.t than the current one
        while (j + 1 < b.size() &&
               std::abs(b[j + 1].t - ma.t) <= std::abs(b[j].t - ma.t))
            ++j;
        if (std::abs(b[j].t - ma.t) <= tol)
            out.push_back({ma.t, ma.value, b[j].t, b[j].value});
    }
    return out;
}
```
:::

**Complexity.** O(n + m) with two pointers — the classic upgrade from an O(n·m)
double loop.

**Follow-ups.** Out-of-order timestamps (buffer + sort, or drop late). Why nearest-
neighbor sync isn't enough at speed → **motion-compensate** to a common timestamp
before fusing. Bounded buffer / backpressure if one stream lags
([14](14-concurrency-for-robotics.md)).

---

## Interview-style questions
*Click a question to reveal a model answer.*

??? They ask you to code a Kalman filter. What do you say before writing anything?
State the model out loud: "state, covariance `P`, motion `F`, measurement `H`, noises `Q`, `R`." Then the two-phase loop — **predict** (`x = Fx`, `P = FPFᵀ + Q`, uncertainty grows) and **update** (innovation `y = z − Hx`, gain `K = PHᵀS⁻¹`, blend). Call out the edge cases you'll handle: symmetric-PSD covariance (Joseph form), and — if there's an angle in the state — wrapping the innovation to `[−π, π]`. Naming these before coding is the senior signal.

??? Why does a constant-velocity KF estimate velocity from position-only measurements?
Velocity is **observable through the motion model over time**, not from any single measurement. The predict step couples position and velocity (`pos += v·dt`), so when successive position measurements are consistent with a velocity, the update flows that information into the velocity component via the off-diagonal covariance terms. `H = [1, 0]` never observes velocity directly, but the filter infers it from the *sequence*.

??? Walk through NMS and its complexity. Where do people get IoU wrong?
Sort detections by score; repeatedly keep the highest and discard everything overlapping it above the IoU threshold; repeat on the rest. O(n²) worst case, O(n log n) sort. The classic IoU bug is forgetting to **clamp the intersection to zero** — disjoint boxes produce negative width/height, and multiplying two negatives gives a spurious positive "overlap." Always `max(0, x2 − x1)`. Also handle zero-area/union-zero boxes.

??? Greedy vs. Hungarian for data association — when does greedy fail?
Greedy takes the globally-cheapest pair each step; it's simple and O(n²log n) but **can be suboptimal**: one cheap early assignment can block two pairs that were jointly cheaper. **Hungarian** (`linear_sum_assignment`) finds the optimal one-to-one assignment minimizing total cost in O(n³). In practice greedy is fine when detections are well-separated; you reach for Hungarian when costs are close, and for JPDA/MHT under dense clutter. Both should run on a **gated** cost matrix so impossible pairs are excluded first.

??? Build a minimal multi-object tracker. What are the four things it must do?
**Predict** each existing track forward (motion model, grow `P`); **associate** detections to tracks via a gated IoU/Mahalanobis cost matrix (greedy/Hungarian); **update** matched tracks with a KF; and manage **lifecycle** — birth tentative tracks from unmatched detections, confirm via M-of-N, coast unmatched tracks through occlusion, delete after K misses. The subtle parts are keeping stable IDs through occlusion (coast + loose re-gating + appearance) and suppressing flicker (`min_hits` before reporting).

??? Why Mahalanobis distance for gating instead of Euclidean?
Euclidean distance treats all directions equally; Mahalanobis **normalizes by the innovation covariance `S`**, so an error along a high-uncertainty axis is penalized less than the same error along a confident axis. It's `d² = νᵀS⁻¹ν`, compared against a **chi-square** threshold for the measurement's degrees of freedom. It reuses the same `S` you already compute for the Kalman gain, so gating is nearly free and statistically principled.

??? Sync two sensor streams at different rates — brute force vs. the good answer?
Brute force is an O(n·m) double loop (for each A, scan all of B). Since both streams are **timestamp-sorted**, use **two pointers**: advance the B pointer while the next B message is closer to the current A timestamp, then accept if within tolerance — O(n + m). For a moving vehicle, nearest-timestamp isn't enough at speed: **motion-compensate** detections to a common time before fusing, and buffer/reorder out-of-sequence messages.

## Resources
- SORT (Bewley et al., 2016) and DeepSORT — the reference minimal trackers to emulate.
- `scipy.optimize.linear_sum_assignment` — Hungarian assignment in one call.
- Roger Labbe, *Kalman and Bayesian Filters in Python* — interactive KF drills.
- Companion notes: [06-state-estimation](06-state-estimation.md),
  [15-sensor-fusion-mot-autonomous-trucking](15-sensor-fusion-mot-autonomous-trucking.md),
  [14-concurrency-for-robotics](14-concurrency-for-robotics.md),
  [10-cpp-for-robotics](10-cpp-for-robotics.md).
- Existing numpy references: `coding-practice/robotics/w5_kalman_1d.py`,
  `w7_nms_iou.py`, `w8_time_sync.py`, `w8_ring_buffer.py`.
