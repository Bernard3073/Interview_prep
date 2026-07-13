# Zipline — Autonomy Perception Engineer (CV / 3D Reconstruction)

> Role-specific prep for Zipline's **Droid team**: offboard / cloud-side perception
> that builds 3D + semantic world models of customer delivery zones from satellite
> and aerial survey imagery, predicts deliverability, and ships priors that augment
> the onboard autonomy stack. **Not a research role** — emphasis is on shipping
> robust, production-grade systems at fleet scale in a safety-critical setting.
>
> Builds on: [03 — 3D Geometry & Transforms](03-3d-geometry-transforms.md),
> [05 — Features & Multi-View Geometry](05-features-multiview-geometry.md),
> [07 — SLAM & Odometry](07-slam-odometry.md),
> [08 — Deep Learning Perception](08-deep-learning-perception.md).

---

## How to read this doc

- **Part A** — the question bank, grouped by competency. Use it to find gaps.
- **Part B** — worked deep-dives on the highest-leverage topics (bundle adjustment,
  DSM vs DTM, projecting semantics into 3D, deliverability calibration, coordinate
  frames, eval under no-ground-truth).
- **Part C** — solved coding problems with runnable Python.
- **Part D** — behavioral / system-design framing for the senior–staff signal.

The meta-theme for every answer: *what is the failure mode, and is it a hazard?*
At Zipline a false "yes, deliver here" can drop a package on a person, a pool, or a
power line. Always state the operating point and the asymmetric cost of errors.

---

# Part A — Question Bank

## A1. 3D Reconstruction & Multi-View Geometry

1. Walk through an SfM pipeline end to end. Where does it break on **aerial survey**
   imagery (repetitive texture, large baselines, near-nadir views, GPS/IMU priors)?
2. SfM vs. MVS vs. learned (NeRF / 3D Gaussian Splatting) — for a reusable geometric
   prior of a backyard from drone imagery, which and why?
3. Relate the fundamental matrix, essential matrix, and homography. When is a
   homography sufficient?
4. How do you fuse a known pose prior (GPS/IMU/RTK) into bundle adjustment? Write the
   cost function and explain the weighting of reprojection vs. pose residuals.
5. Satellite imagery (nadir, ~0.3–0.5 m GSD) → metric ground elevation. How? What is
   the **DSM vs. DTM** distinction and why does it matter for "can we land here"?
6. Explain bundle adjustment: what's optimized, why it's sparse, how the Schur
   complement makes it tractable.
7. Register a fresh aerial survey to an existing 3D model of the same site (change
   detection). ICP variants vs. feature-based vs. learned descriptors.
8. Scale ambiguity in monocular reconstruction — every way to resolve it in your
   deployment context.
9. Robust estimation with 50% outliers: RANSAC vs. MAGSAC vs. LMedS. How do you pick
   the inlier threshold in a principled way?
10. Handling moving objects (cars, people, pets) that violate the static-scene
    assumption during reconstruction.

## A2. Semantic Segmentation & Learned Perception

1. Design a segmentation model for deliverable surfaces (grass, concrete, pool, tree
   canopy, deck, vehicle). Which classes matter for **safety**, and how does that
   change loss weighting and eval?
2. Aerial/satellite segmentation: huge scale variation, tiny objects relative to
   frame. Tiling, overlap, context, multi-scale.
3. Fuse 2D semantics with 3D geometry → semantic 3D world model. How do you resolve
   multi-view label disagreement?
4. Lots of unlabeled aerial imagery, little labeled data in a new region. Bootstrap:
   SSL pretraining, foundation models (SAM / DINOv2), weak labels (OSM / cadastral),
   active learning.
5. Domain shift to a new country (vegetation, roofs, building styles). Detect it and
   adapt without full relabeling.
6. Model **learned customer preferences** for drop location — ranking vs.
   classification vs. a learned cost surface over the yard.

## A3. Cloud-side Pipeline / World Models

1. Design the full offboard pipeline: satellite + aerial in → validated 3D semantic
   prior + deliverability map out, to onboard a new customer.
2. Interface to onboard: what's precomputed offboard vs. left to onboard? How do you
   handle **staleness** (a tree grew, a shed was built)?
3. Produce a **deliverability prediction** — a calibrated confidence an address is
   safe to serve. Features and calibration.
4. Coordinate systems: WGS84 / ECEF / ENU / UTM / camera frames. Transform a
   satellite-derived ground point into the aircraft's local frame; where do
   precision/datum bugs creep in?

## A4. Production MLE / Systems

1. Not research — how do you decide when SOTA (e.g. 3DGS) is worth productionizing
   vs. a robust classical method?
2. Reconstruct/segment hundreds of thousands of zones. Compute design: batch vs.
   streaming, GPU scheduling, cost/site, incremental updates.
3. Version model + training data + generated priors so a bad shipped prior can be
   reproduced and rolled back.

## A5. Evaluation & Validation (safety-critical)

1. No ground-truth 3D for most backyards. Build a validation set and measure quality
   at scale (held-out survey passes, LiDAR spot-checks, geometric consistency, sim).
2. Metrics for "behaves reliably in the field." FN vs. FP tradeoff when the failure
   is delivering into a hazard. Setting the operating point.
3. Catch a regression where average metrics improve but a rare critical class
   (power lines, trampolines, pools) degrades.
4. Power lines / thin structures — hard to reconstruct and segment, critical for
   safety. How do you specifically eval and guarantee them?

## A6. Coding (see Part C for solutions)

- Point-to-plane ICP; make it robust to outliers and partial overlap.
- Homography via DLT + normalization, wrapped in RANSAC.
- Project a point cloud into a pinhole camera with z-buffering.
- Linear (DLT) triangulation from two views.
- Ray–triangle intersection (Möller–Trumbore) for a landing-ray hazard test.
- Largest inscribed empty circle in a deliverability mask (max safe clearance).
- Connected components on a mask (contiguous drop zones).

---

# Part B — Worked Deep-Dives

## B1. Bundle Adjustment, with a pose prior

**What is optimized.** Camera parameters `{Cⱼ}` (6-DoF pose, maybe intrinsics) and
3D points `{Xᵢ}`, minimizing reprojection error over all observations:

```
min_{C, X}  Σ_{i,j}  vᵢⱼ · ρ( ‖ π(Cⱼ, Xᵢ) − xᵢⱼ ‖²_Σ )
```

- `π` projects point `i` into camera `j`; `xᵢⱼ` is the measured pixel.
- `vᵢⱼ ∈ {0,1}` is the visibility indicator (point i seen in camera j).
- `Σ` is the measurement covariance (often σ²·I per keypoint, scaled by detector
  confidence / octave).
- `ρ` is a robust kernel (Huber / Cauchy) so a few bad matches don't dominate.

**Why it's sparse.** Each observation touches exactly **one** camera and **one**
point, so the Jacobian `J` has block structure. The Hessian approximation
`H = JᵀJ` partitions into camera block `U`, point block `V`, and coupling `W`:

```
H = [ U   W  ]      U = block-diag over cameras
    [ Wᵀ  V  ]      V = block-diag over points (and V is easy to invert)
```

**Schur complement.** You don't factor the whole `H`. Eliminate the points first:

```
(U − W V⁻¹ Wᵀ) Δc = (b_c − W V⁻¹ b_p)        ← reduced camera system
Δp = V⁻¹ (b_p − Wᵀ Δc)                       ← back-substitute points
```

`V⁻¹` is cheap (3×3 blocks). The reduced system is `(#cameras·6)` square — tiny
compared to the full problem with millions of points. This is the entire reason BA
scales. (Ceres / g2o / GTSAM do exactly this.)

**Adding the pose prior (your RTK/GPS/IMU).** Add a residual that pulls each camera
toward its measured pose, in the tangent space of SE(3):

```
r_prior(Cⱼ) = Log( C̄ⱼ⁻¹ Cⱼ )  ∈ ℝ⁶,   cost += Σⱼ ‖ r_prior(Cⱼ) ‖²_{Σ_pose}
```

`C̄ⱼ` is the measured pose; `Log` is the SE(3) logarithm (so the error is a proper
6-vector on the manifold, not a naive subtraction of poses). **Weighting is the
whole game:** `Σ_pose` encodes how much you trust the sensor. RTK-fixed → tight
translation prior (centimeters) → it pins absolute scale and georeferencing, killing
the monocular scale ambiguity. Loosely-trusted GPS → soft prior that just
regularizes / seeds the optimization. The relative weighting of `Σ` (pixels) vs.
`Σ_pose` (meters/radians) sets whether geometry or the sensor wins a disagreement —
get the units and covariances right or BA silently biases toward one.

**Why this matters for the role.** Aerial surveys come with good pose priors. Using
them turns BA from "recover structure up to an arbitrary similarity transform" into
"recover **metric, georeferenced** structure," which is exactly what a world model
keyed by street address needs.

## B2. DSM vs. DTM — and why landing cares

- **DSM (Digital Surface Model):** elevation of the **top** of everything — tree
  canopy, rooftops, cars, fences.
- **DTM (Digital Terrain Model):** elevation of the **bare ground**, with objects
  removed.
- **nDSM = DSM − DTM:** object height above ground ("normalized DSM" / canopy-height
  model). This is the single most useful layer for delivery: it directly tells you
  *how tall is the stuff in the yard*.

**Pipeline imagery → elevation:** multi-view stereo / SGM across overlapping survey
frames → dense point cloud → rasterize to a DSM grid. To get the DTM you **filter**
out non-ground returns (cloth-simulation filter, progressive morphological filter,
or a learned ground classifier), then interpolate ground under the removed objects.

**Why both matter for "can we land here":**
- You need the **DTM** for the true landing surface and slope.
- You need **nDSM** for clearance — a flat grassy patch (good per DTM) under a tree
  canopy (tall per nDSM) is *not* deliverable.
- Slope from the DTM gradient gates whether a package rolls or the aircraft can
  descend. Thin tall objects in nDSM (poles, lines) are go/no-go hazards.

Common interview trap: quoting only a DSM and forgetting that the canopy hides the
ground — leading to a "flat" call over a spot you can't actually reach.

## B3. Projecting 2D semantics into the 3D model (multi-view label fusion)

You have per-image segmentation masks and a reconstructed mesh / point cloud with
known camera poses. Goal: a single label (+ confidence) per 3D primitive.

**Procedure per 3D point `X`:**
1. For each camera `j` that sees `X`: project `x = π(Cⱼ, X)`.
2. **Occlusion test** — render depth from camera `j`; keep the observation only if
   `X`'s depth ≈ the z-buffer (else another surface occludes it). Skipping this is
   the #1 bug: you paint a roof label onto the ground behind it.
3. Gather the class **probability vectors** `p_j(X)` (use soft logits, not argmax).
4. **Fuse.** Bayesian / log-opinion-pool fusion weighted by per-view reliability:

```
log P(c | X) ∝ Σ_j  w_j(X) · log p_j(c | X)
w_j(X) = f(viewing angle, range, mask confidence, motion blur)
```

   Weight grazing / far / blurry views down; near-nadir, in-focus, close views up.
5. Argmax for the label; keep the entropy as a per-point **uncertainty** layer (feeds
   deliverability and active-learning sampling).

**Disagreement is signal, not noise.** High-entropy regions are exactly where you
request a fresh survey pass or a human label. For thin safety-critical structures
(power lines), use a *recall-biased* fusion: if **any** trusted view says "line,"
flag it — the cost of a missed line dwarfs a false positive.

## B4. Deliverability confidence — building and calibrating it

**Frame:** per address (or per candidate drop point) produce `P(safe-to-deliver)`.

**Features** (geometric + semantic, all from the world model):
- Largest inscribed clearance radius in the drop zone (see Part C5).
- Min 3D clearance to nearest obstacle (from nDSM) along the descent corridor.
- Ground slope and roughness (DTM gradient stats).
- Canopy / overhang coverage fraction over candidate points.
- Semantic hazard presence + distance: pool, vehicle, power line, trampoline, people.
- Prior staleness (age of the imagery) and reconstruction uncertainty (B3 entropy).

**Model:** gradient-boosted trees or a small MLP — interpretable, cheap, easy to
gate. **Do not** ship raw model scores: a classifier's output is not a probability.

**Calibration is the deliverable, not accuracy.** Fit **isotonic regression** (or
Platt scaling) on a held-out set so that among addresses scored 0.9, ~90% are truly
safe. Verify with a **reliability diagram** and report **Expected Calibration Error**.

**Operating point under asymmetric cost.** A missed hazard (deliver into a pool) is
catastrophic; a false hazard (refuse a fine yard) is mere operational friction.
So choose the threshold to bound the **false-accept rate**, not to maximize F1:

```
choose τ such that  P(hazard | predicted-safe, score ≥ τ) ≤ ε_safety
```

Everything below `τ` routes to human review or a survey re-fly rather than auto-deny.
Be explicit in the interview that you'd set `ε_safety` *with the safety team* and
treat it as a product/safety decision, not an ML hyperparameter.

## B5. Coordinate frames — getting a ground point into the aircraft frame

Chain you must be fluent in:

```
WGS84 (lat, lon, h)  →  ECEF (X,Y,Z, geocentric)  →  ENU/UTM (local tangent)  →  body  →  camera
```

1. **WGS84 → ECEF:** closed-form using the ellipsoid (a, e²) and the prime-vertical
   radius `N(φ)`. This is exact; no approximation.
2. **ECEF → ENU:** rotate+translate about a chosen local origin (e.g. the delivery
   site) so you work in metric east/north/up — small numbers, good conditioning.
3. **ENU → body → camera:** apply the aircraft pose `T_world_body` and the calibrated
   extrinsic `T_body_cam`.

**Where bugs live:**
- **Datum / geoid mismatch.** GPS height is **ellipsoidal**; maps/DSMs are often
  **orthometric (above geoid/MSL)**. Mixing them gives a tens-of-meters vertical
  error — fatal for clearance. Always know which height your DSM is in and convert
  via the geoid model.
- **Float32 ECEF.** ECEF magnitudes are ~6.4e6 m; storing them in float32 wastes all
  precision (~0.5 m quantization). Do the subtraction-to-local-origin in **float64**,
  then drop to float32 only in the small ENU frame.
- **UTM zone boundaries / lat-lon axis order** (lon,lat vs lat,lat) — classic
  off-by-a-continent bug.
- **Rotation conventions** — active vs passive, `R` vs `Rᵀ`, quaternion `wxyz` vs
  `xyzw`. State your convention before you write a line of transform code.

## B6. Evaluation when there is no 3D ground truth

You rarely get LiDAR truth for a random backyard. Build confidence from cheaper,
complementary signals:

- **Held-out views / cross-validation of geometry.** Reconstruct from a subset of
  survey frames; measure **reprojection error** and **photometric consistency** on
  the held-out frames. A model that's geometrically wrong won't reproject cleanly.
- **LiDAR / RTK spot-checks.** Truth a small, diverse sample of sites; track
  cloud-to-cloud distance, DTM RMSE, canopy-height error. Use it to *bound* the
  population, not to score every site.
- **Self-consistency across surveys.** Two independent passes should agree where the
  world hasn't changed; disagreement localizes either change or reconstruction error.
- **Synthetic / sim truth.** Render photoreal scenes (you own the geometry) to get
  unlimited labeled 3D for stress-testing edge cases (thin structures, low texture).
- **Task-level proxy:** the real metric is *delivery outcomes* — track field
  success/abort/incident rates against predicted deliverability and close the loop.

**Rare-but-critical classes** need their **own** sliced metrics. Aggregate IoU can
rise while power-line recall falls. Maintain a per-hazard recall dashboard with a
**hard gate**: a model cannot ship if power-line / pool / person recall regresses,
regardless of mean metrics. Mine hard examples continuously into a fixed regression
set.

---

# Part C — Solved Coding Problems

Runnable, dependency-light (numpy). Written to be explained while typing.

## C1. Point-to-plane ICP (robust)

```python
import numpy as np

def icp_point_to_plane(src, dst, dst_normals, iters=30, trim=0.8):
    """Align src -> dst. dst_normals: per-point normals on the target.
    Point-to-plane converges faster than point-to-point on structured scenes.
    `trim` keeps the closest fraction of matches -> robust to partial overlap."""
    from scipy.spatial import cKDTree          # nearest-neighbor correspondences
    T = np.eye(4)
    P = src.copy()
    tree = cKDTree(dst)
    for _ in range(iters):
        d, idx = tree.query(P)                 # match each src pt to nearest dst
        q, n = dst[idx], dst_normals[idx]
        # trimmed ICP: drop the worst (1-trim) matches -> outlier/partial robustness
        keep = d <= np.quantile(d, trim)
        Pk, qk, nk = P[keep], q[keep], n[keep]
        # linearize: minimize Σ ((Pk - qk)·nk + (r x Pk)·nk + t·nk)^2  over (r, t)
        A = np.hstack([np.cross(Pk, nk), nk])  # Nx6 Jacobian
        b = -np.sum((Pk - qk) * nk, axis=1)    # point-to-plane residual
        x, *_ = np.linalg.lstsq(A, b, rcond=None)
        r, t = x[:3], x[3:]
        dT = np.eye(4)
        dT[:3, :3] = _exp_so3(r)               # small-angle rotation update
        dT[:3, 3] = t
        T = dT @ T
        P = (dT[:3, :3] @ P.T).T + dT[:3, 3]
        if np.linalg.norm(x) < 1e-6:           # converged
            break
    return T

def _exp_so3(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
    return np.eye(3) + np.sin(th)*K + (1-np.cos(th))*K@K   # Rodrigues
```

Talking points: point-to-plane vs point-to-point; trimming for partial overlap;
why we linearize rotation (small-angle); failure when init is far off → use a global
init (FPFH+RANSAC, or your pose prior) first.

## C2. Homography via normalized DLT + RANSAC

```python
import numpy as np

def normalize(pts):                            # Hartley normalization: mean 0, mean dist √2
    c = pts.mean(0)
    s = np.sqrt(2) / np.linalg.norm(pts - c, axis=1).mean()
    T = np.array([[s,0,-s*c[0]],[0,s,-s*c[1]],[0,0,1]])
    ph = (T @ np.c_[pts, np.ones(len(pts))].T).T
    return ph[:, :2], T

def dlt_homography(p1, p2):
    n1, T1 = normalize(p1); n2, T2 = normalize(p2)
    A = []
    for (x,y),(u,v) in zip(n1, n2):            # each correspondence -> 2 rows
        A += [[-x,-y,-1,0,0,0,u*x,u*y,u],
              [0,0,0,-x,-y,-1,v*x,v*y,v]]
    _,_,Vt = np.linalg.svd(np.array(A))
    H = Vt[-1].reshape(3,3)
    return np.linalg.inv(T2) @ H @ T1          # denormalize

def ransac_homography(p1, p2, thresh=3.0, iters=2000):
    best_in, best_H = None, None
    N = len(p1)
    for _ in range(iters):
        s = np.random.choice(N, 4, replace=False)   # minimal sample = 4 points
        try: H = dlt_homography(p1[s], p2[s])
        except np.linalg.LinAlgError: continue
        proj = (H @ np.c_[p1, np.ones(N)].T).T
        proj = proj[:, :2] / proj[:, 2:3]
        err = np.linalg.norm(proj - p2, axis=1)     # symmetric transfer error (1-way shown)
        inl = err < thresh
        if best_in is None or inl.sum() > best_in.sum():
            best_in, best_H = inl, H
    return dlt_homography(p1[best_in], p2[best_in]), best_in   # refit on all inliers
```

Why normalization matters: without it the DLT system is badly conditioned and `H`
is garbage. State the `N`-iterations formula from doc 04.

## C3. Project a point cloud into a pinhole camera (z-buffered)

```python
import numpy as np

def project_pointcloud(X, K, R, t, H, W):
    """X: Nx3 world points. Returns depth image + per-pixel source index."""
    Xc = (R @ X.T).T + t                        # world -> camera
    front = Xc[:, 2] > 1e-6                      # cull points behind camera
    Xc = Xc[front]; src = np.nonzero(front)[0]
    uv = (K @ Xc.T).T
    uv = uv[:, :2] / uv[:, 2:3]                  # perspective divide
    u = np.round(uv[:,0]).astype(int); v = np.round(uv[:,1]).astype(int)
    inb = (u>=0)&(u<W)&(v>=0)&(v<H)              # inside the image
    u,v,z,src = u[inb], v[inb], Xc[inb,2], src[inb]
    depth = np.full((H,W), np.inf)
    index = np.full((H,W), -1, dtype=int)
    order = np.argsort(-z)                       # far -> near, so near overwrites (painter's)
    for uu,vv,zz,ss in zip(u[order],v[order],z[order],src[order]):
        depth[vv,uu] = zz; index[vv,uu] = ss     # z-buffer: nearest wins
    depth[np.isinf(depth)] = 0
    return depth, index
```

For scale, replace the Python loop with `np.minimum.at` on a flattened buffer.

## C4. Linear (DLT) triangulation

```python
import numpy as np

def triangulate(P1, P2, x1, x2):
    """P1,P2: 3x4 projection matrices. x1,x2: pixel (u,v). Returns 3D point."""
    A = np.array([
        x1[0]*P1[2] - P1[0],
        x1[1]*P1[2] - P1[1],
        x2[0]*P2[2] - P2[0],
        x2[1]*P2[2] - P2[1],
    ])                                           # A X = 0, X homogeneous
    _,_,Vt = np.linalg.svd(A)
    X = Vt[-1]
    return X[:3] / X[3]                           # dehomogenize
```

Follow-up: this minimizes algebraic error; refine with nonlinear reprojection-error
minimization (Levenberg–Marquardt). Degenerate when the baseline is ~0 (small
parallax) → large depth uncertainty, the same issue that plagues near-nadar aerial
pairs with short baselines.

## C5. Largest inscribed empty circle = max safe clearance

```python
import numpy as np
from scipy.ndimage import distance_transform_edt

def max_clearance(deliverable_mask):
    """deliverable_mask: HxW bool, True = safe ground.
    Returns (center_rc, radius_px): biggest circle that fits in the safe region."""
    dt = distance_transform_edt(deliverable_mask)   # dist from each safe px to nearest unsafe
    r, c = np.unravel_index(np.argmax(dt), dt.shape)
    return (r, c), dt[r, c]                          # peak of the distance transform
```

This is the cleanest "geometry-flavored" question they can ask: the **distance
transform** turns "largest inscribed empty circle" into one line, its peak is the
safest drop point, and its value (× GSD) is the metric clearance radius — a direct
deliverability feature (B4).

## C6. Connected components (contiguous drop zones)

```python
from scipy.ndimage import label

def drop_zones(mask, min_area):
    """Label contiguous safe regions; drop ones too small to land in."""
    lab, n = label(mask)                          # 4-connectivity by default
    zones = []
    for i in range(1, n+1):
        ys, xs = (lab == i).nonzero()
        if len(ys) >= min_area:                   # filter specks
            zones.append({"id": i, "area": len(ys),
                          "centroid": (ys.mean(), xs.mean())})
    return zones
```

If they want it from scratch, write the BFS/union-find version — that's the actual
"number of islands" LeetCode they may ask live.

---

# Part D — Behavioral & System-Design Framing

**Recurring system-design prompt:** *"Design the cloud pipeline that onboards a new
delivery address."* A strong answer hits:

1. **Ingest** — pull satellite + scheduled aerial survey; store raw + metadata
   (pose, GSD, timestamp) immutably.
2. **Reconstruct** — SfM/MVS (pose-prior-seeded BA) → DSM/DTM/nDSM; cache the dense
   product.
3. **Segment** — tiled semantic seg; multi-view fusion into the 3D model (B3).
4. **Score** — deliverability features → calibrated confidence (B4) → drop-point
   recommendation (C5).
5. **Validate** — automated gates (B6) + human review queue for low-confidence /
   high-entropy sites.
6. **Ship** — versioned prior to the fleet; **staleness** tracking triggers re-fly.
7. **Close the loop** — field outcomes feed back as labels.

Cross-cutting: versioning (model + data + prior), incremental updates when new
imagery lands, cost-per-site budget, and observability/regression dashboards.

**Senior–staff signal** — show you reason about: the offboard/onboard **trust &
override** contract; the asymmetric safety cost in every threshold; *buy-vs-build*
and *classical-vs-SOTA* tradeoffs justified by reliability not novelty; and making
the system **debuggable and rollback-able** because it's safety-critical.

**Questions to ask them** (signals seniority and fit):
- How are offboard priors consumed onboard today — what's the trust/override model
  when the prior and live perception disagree?
- Biggest current scaling bottleneck: compute, labeling, or imagery freshness?
- How is "deliverability" defined, who owns the safety case, and how is the operating
  point chosen?
- What does the loop from field incidents back into model training look like today?

---

## One-line summaries to memorize

- BA is sparse because each observation links one camera + one point; the Schur
  complement eliminates points to a tiny camera system. Pose priors make it metric.
- **DTM** = bare ground (landing surface + slope); **nDSM** = object height
  (clearance). You need both.
- Project semantics into 3D *with an occlusion test*; fuse soft probabilities,
  weight by view quality, keep entropy as uncertainty.
- Don't ship raw scores — **calibrate** (isotonic) and set the threshold by a bounded
  **false-accept** rate, not F1.
- Heights: ellipsoidal (GPS) vs orthometric (maps) — convert via the geoid or you're
  tens of meters off. Localize in float64 before float32.
- Rare hazards (power lines, pools) get their own recall gate; mean IoU can lie.
