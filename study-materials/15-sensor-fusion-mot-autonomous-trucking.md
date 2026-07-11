# Week 15 — Sensor Fusion & Multi-Object Tracking (Autonomous Trucking)

> Prep for **Kodiak — Senior Autonomy Engineer, Perception**. The role is state
> estimation + sensor fusion + multi-object tracking (MOT) across camera, radar,
> lidar, thermal, and IMU, in C++, for highway-speed commercial trucks. Filter
> fundamentals (KF/EKF/UKF/PF) live in **[06-state-estimation](06-state-estimation.md)** —
> this note is the layer above: turning per-sensor detections into stable,
> evaluated tracks of the world.

---

## 1. The one idea to anchor everything: tracking-by-detection

Most production AV stacks are **tracking-by-detection**. Each frame produces
detections; a tracker maintains persistent object *tracks* over time. The loop:

```
detections (per sensor, per frame)
        │
   ┌────▼─────┐  predict every track forward (motion model)
   │  PREDICT │
   └────┬─────┘
   ┌────▼─────┐  gate + associate detections ↔ tracks
   │ ASSOCIATE│
   └────┬─────┘
   ┌────▼─────┐  KF/EKF update matched tracks with their detection
   │  UPDATE  │
   └────┬─────┘
   ┌────▼─────┐  birth new tracks (unmatched dets), kill stale tracks
   │ LIFECYCLE│
   └──────────┘
```

**If you say nothing else in an MOT interview, name these four stages and where
each sensor and each filter plugs in.** Everything below is detail on one stage.

---

## 2. Fusion architecture: where do you combine sensors?

Interviewers want you to place the fusion point and defend the trade-off.

| Level | What is fused | Pros | Cons |
|---|---|---|---|
| **Early / low-level** | raw measurements (points, pixels) | max information, one joint model | brittle to calibration/time-sync; hard to debug; tight coupling |
| **Mid / feature** | learned features (e.g. BEV grid) | rich, learnable cross-modal cues | needs data + training infra; opaque failures |
| **Late / track-level** | per-sensor tracks/detections | modular, debuggable, graceful degradation | throws away joint info; double-counting risk |

- **Detection-level fusion** (associate all sensors' detections to one central
  tracker) is the common pragmatic default — one estimator, still modular.
- **Track-to-track fusion** (each sensor runs its own tracker; fuse the tracks)
  decorrelates nicely but risks **double-counting** shared information → use the
  covariance-intersection trick to stay consistent.
- Safety-critical trucking favors architectures that **degrade gracefully**: if
  the camera blinds on sun glare, radar + lidar must still hold the track.

> Rule of thumb to say out loud: *early fusion maximizes accuracy, late fusion
> maximizes robustness and debuggability.* Name which one the product needs.

---

## 3. Data association (the heart of MOT)

Given N predicted tracks and M detections, which detection updates which track?

**Step 1 — Gating.** Prune impossible pairs before assignment. Use the
**Mahalanobis distance** in innovation space: `d² = νᵀ S⁻¹ ν`, where `ν = z − h(x⁻)`
is the innovation and `S = H P⁻ Hᵀ + R`. Reject pairs where `d²` exceeds a
chi-square threshold for the measurement DoF. (Same math as EKF outlier gating.)

**Step 2 — Assignment.** Build a cost matrix (gated `d²`, or `−log` likelihood, or
IoU for boxes) and solve:

| Method | Idea | When |
|---|---|---|
| **Greedy / NN** | assign each det to nearest track | cheap, fine when sparse & well-separated |
| **GNN (Hungarian)** | one global min-cost assignment per frame | standard default; O(n³) |
| **JPDA** | soft — weight *all* gated dets probabilistically | dense clutter, closely-spaced targets |
| **MHT** | defer decisions, keep multiple hypotheses over time | max accuracy, expensive; ambiguous scenes |

- **Hungarian algorithm** solves the min-cost bipartite assignment optimally in
  O(n³). Know that it's the go-to for GNN and how you fill the cost matrix.
- **JPDA vs. MHT trade-off:** JPDA commits per-frame but shares evidence softly;
  MHT delays commitment across frames (a tree of hypotheses, pruned by score) —
  best accuracy in ambiguity, worst compute.
- Modern learned trackers add an **appearance/embedding** term to the cost (à la
  DeepSORT) so association survives motion-model error and crossing paths.

---

## 4. Track lifecycle: birth, confirm, coast, die

A tracker is only as good as its bookkeeping. This is where IDs are won and lost.

- **Birth:** each unmatched detection spawns a **tentative** track. Initialize
  state from the detection; inflate `P` (large initial position/velocity
  uncertainty) since one detection barely constrains velocity.
- **Confirmation (M-of-N):** promote tentative → **confirmed** only after M hits in
  N frames (or a track score crossing threshold). Filters out flicker/clutter.
- **Coasting through occlusion:** a car hidden behind a truck for 2 s gets no
  detections — keep **predicting** (coasting) and hold the ID. Grow `P` each step;
  re-associate on reappearance via gating + appearance embedding.
- **Death:** delete after K consecutive misses, or when coasted `P` grows so large
  the track is meaningless. Tunable miss budget = ID-stability vs. ghost tracks.
- **Track score / SPRT:** a log-likelihood-ratio score accumulating hits/misses is
  a principled unified birth+death rule (sequential probability ratio test).

> Occlusion + ID stability is the classic senior question. Answer = coast on the
> motion model, gate loosely on return, disambiguate with appearance, cap by a
> covariance/miss budget.

---

## 5. Sensor-by-sensor: strengths, failures, and what each contributes

The JD lists **camera, radar, lidar, thermal, IMU**. Know each one's job.

| Sensor | Gives you | Strong | Weak / fails |
|---|---|---|---|
| **Camera** | dense semantics, class, lateral position | classification, lane/sign, cheap | no direct depth; sun glare, night, fog, rain |
| **Radar** | **range + radial (Doppler) velocity** | direct velocity, long range, all-weather | poor lateral/angular res; clutter, multipath |
| **Lidar** | precise 3D geometry | accurate shape/position, depth | rain/snow/fog scatter; sparse at range; cost |
| **Thermal** | heat signature | night, pedestrians, glare-blind cases | no color/text; low res; poor geometry |
| **IMU** | ego accel + angular rate (high rate) | fills gaps between exteroceptive frames | drifts fast if integrated alone |

Fusion talking points:

- **Radar Doppler is a gift** — it measures radial velocity *directly*, so fold it
  into the measurement model `h(x)` instead of differentiating positions. Huge for
  early, confident velocity on a highway.
- **IMU as the prediction engine:** IMU runs at 100–1000 Hz; lidar/camera at
  10–20 Hz. Predict the state forward with IMU (or a motion model) *between*
  exteroceptive updates so tracks stay fresh at control rate. This is the same
  predict/update split as [06-state-estimation](06-state-estimation.md).
- **Complementary weather:** lidar dies in heavy fog where radar sees; camera dies
  at night where thermal sees. Weight each sensor's `R` by conditions — even an
  online per-sensor reliability estimate.
- **Handling disagreement:** radar says object, camera says empty road. Don't
  average — reason about each sensor's failure mode (radar ghost/multipath vs.
  camera miss at range) and let gating + track score arbitrate over time. For
  safety, an unexplained radar return near the path is treated as real until
  disproven.

### Calibration & synchronization (the boring thing that breaks everything)

- **Extrinsic calibration:** every sensor's pose in the truck frame. A few-cm or
  fraction-of-a-degree error becomes meters of lateral error at 150 m range.
- **Temporal sync:** sensors trigger at different times/rates. Timestamp at capture
  and **motion-compensate** detections to a common time before association;
  mishandled latency looks exactly like a tracking bug.
- **Out-of-sequence measurements:** a slow sensor's data arrives after a newer
  update. Either buffer and reorder, or use an OOSM update that folds the late
  measurement back in without rewinding the whole filter.

---

## 6. Learned + classical (they want both)

The JD says "learned scene estimation" *and* Kalman/particle filtering. The senior
signal is fusing the two cleanly, not picking a side.

- **Learned detector → classical tracker:** the network proposes detections
  (+class, +box, ideally +uncertainty); the KF/EKF maintains temporal state. Best
  of both — data-driven perception, principled temporal fusion.
- **Trusting learned covariance:** a net can output a covariance, but it's usually
  **miscalibrated**. Check calibration (reliability diagrams / NIS on real data)
  and recalibrate (temperature scaling, or learn a variance head with NLL loss)
  before feeding `R` into the filter, or the tracker goes over/underconfident.
- **BEV & transformer fusion:** learned bird's-eye-view features fuse camera+lidar
  in a common top-down frame — a mid-level fusion representation you can still
  track on top of. See [13-bev-transformers](13-bev-transformers.md).
- **End-to-end vs. modular:** end-to-end tracking (e.g. transformer track queries)
  is rising, but modular tracking-by-detection still dominates safety stacks for
  **debuggability and failure isolation** — a point worth making explicitly.
- **OOD / never-seen objects:** debris, an overturned trailer, lost cargo. A pure
  learned detector may miss them. Geometry-based (lidar occupancy / freespace)
  fallbacks catch "something solid is there" even without a class — defense in
  depth is the safe answer.

---

## 7. Evaluation, metrics & debugging (they call this out twice)

"Understanding of metrics, data analysis, scientific evaluation" is in the JD.

**Tracking metrics — know what each one hides:**

| Metric | Measures | Blind spot |
|---|---|---|
| **MOTA** | 1 − (FN + FP + IDsw)/GT | dominated by detection count; underweights ID switches |
| **MOTP** | localization error of matched tracks | says nothing about association quality |
| **IDF1** | identity-preserving F1 | better for ID consistency; less about per-frame recall |
| **HOTA** | balances detection + association explicitly | newer; the modern default for a reason |

- Report **detection quality** (precision/recall, AP) *and* **association quality**
  (IDsw, IDF1/HOTA) separately — a great detector with a bad associator still fails.
- **Filter consistency** still applies to each track: **NEES/NIS** vs. chi-square to
  catch over/underconfident state — see [06-state-estimation](06-state-estimation.md).
- **Aggregate + curated:** headline metrics on a large log set, *plus* a curated
  hard-case suite (cut-ins, occlusions, night, rain, long-range) so a good average
  can't hide a dangerous tail. Beware **metric gaming** — tune to a proxy and you
  regress the thing you actually care about.
- **Range-stratified metrics** matter for trucks: performance at 150 m ≠ at 30 m,
  and long stopping distance means the far bins are the safety-critical ones.

**Debugging an object dropped from fusion output but present in raw data — trace
the pipeline in order:** detection stage (did any sensor detect it?) → time-sync
(timestamps/motion-compensation) → **gating** (did `d²` wrongly reject it — bad
`R`/`P`?) → **association** (assigned to the wrong track / lost the contest?) →
**lifecycle** (killed too aggressively by the miss budget?). Log per-stage so you
can binary-search where the object disappears.

---

## 8. Autonomous-trucking domain specifics (Kodiak flavor)

Trucks are not big cars. Have these ready — they signal you understand the product.

- **Long stopping distance** (a loaded truck needs a *long* runway) demands
  **long-range** detection & tracking — the far range bins dominate safety, and
  that's exactly where lidar gets sparse and camera depth degrades → radar and
  temporal filtering carry the load.
- **Highway speed + long range** stresses the estimator: small angular error → big
  lateral error far away; closing speeds are high, so early confident velocity
  (radar Doppler) is worth a lot.
- **Trailer articulation & huge blind spots:** the ego "vehicle" is articulated;
  self-occlusion and mounting geometry matter for calibration and coverage.
- **Sensor mounting height** on a cab changes ground-plane assumptions and
  occlusion patterns vs. a sedan.
- **Mostly-highway ODD** is simpler than urban in some ways (fewer classes, more
  structure) but unforgiving on **latency and long-range reliability**.
- **Real-time C++ on-vehicle:** the tracker runs in a hard-deadline loop — no
  allocation in the hot path, deterministic timing, lock-free/bounded queues for
  async sensor streams. See [14-concurrency-for-robotics](14-concurrency-for-robotics.md)
  and [10-cpp-for-robotics](10-cpp-for-robotics.md).

---

## Interview-style questions
*Click a question to reveal a model answer.*

??? Walk me through a multi-object tracking pipeline end to end.
**Tracking-by-detection.** Per frame: (1) **predict** every existing track forward with its motion model (CV/CA/CTRV), growing `P`; (2) **gate** track–detection pairs by Mahalanobis distance and build a cost matrix; (3) **associate** via GNN/Hungarian (or JPDA/MHT in clutter); (4) **update** matched tracks with a KF/EKF; (5) **lifecycle** — birth tentative tracks from unmatched detections, confirm via M-of-N, coast unmatched tracks through occlusion, delete after K misses. Multi-sensor detections feed one central tracker (detection-level fusion). Then you **evaluate** with MOTA/IDF1/HOTA plus per-track NEES/NIS.

??? Compare GNN, JPDA, and MHT for data association.
**GNN** solves one global min-cost assignment per frame (Hungarian, O(n³)) — the standard default; commits hard each frame. **JPDA** is soft: instead of picking one detection per track it weights *all* gated detections by association probability and updates with the combined evidence — better in dense clutter and closely-spaced targets, but it can't create/manage tracks by itself and blurs identities. **MHT** defers the decision: it maintains a tree of association hypotheses across frames, scores them, and prunes — highest accuracy in ambiguity but the most expensive. Pick based on scene density and compute budget.

??? How do you fuse radar, lidar, and camera, and what does each contribute?
**Radar** gives long range and direct **radial (Doppler) velocity**, all-weather, but poor angular resolution → fold Doppler straight into the measurement model for early velocity. **Lidar** gives precise 3D geometry/position but degrades in fog/rain and gets sparse at range. **Camera** gives semantics/classification and lateral position but no direct depth and fails at night/glare. I'd run **detection-level fusion** into one central estimator so it degrades gracefully, weight each sensor's `R` by conditions, and rely on their **complementary failure modes** (radar in fog, thermal at night). Calibration and time-sync (motion-compensate to a common timestamp) are prerequisites or it all looks like a tracking bug.

??? A tracked car is occluded for 2 seconds then reappears. How do you keep its ID?
**Coast** the track on its motion model during the gap — keep predicting, no updates, and let `P` grow. On reappearance, **gate loosely** (the inflated `P` widens the gate) and **disambiguate with an appearance embedding** so it re-associates to the same ID rather than spawning a new track. Cap the coasting with a **miss budget / covariance limit** so genuinely-gone objects die instead of becoming ghosts. The tuning is ID-stability vs. ghost tracks.

??? A learned detector outputs a covariance. Do you feed it straight into your Kalman update?
No — learned uncertainties are usually **miscalibrated**. First verify calibration (reliability diagram, or NIS/consistency checks on real logs); if it's off, **recalibrate** (temperature scaling, or train a variance head with an NLL/regression loss). Only then use it as `R`. Feeding a miscalibrated covariance makes the filter over- or under-confident: too small → gating rejects good detections and the track diverges; too large → sluggish, ignores good measurements.

??? Which tracking metric would you trust, and why not MOTA alone?
**MOTA** is dominated by detection counts (FP/FN) and underweights **ID switches**, so a strong detector with a bad associator scores well while identities scramble. I report **detection quality** (precision/recall/AP) and **association quality** (IDsw, IDF1) separately, and prefer **HOTA**, which explicitly balances detection and association. And I stratify by **range** and by **scenario** (cut-ins, night, rain) plus a curated hard-case set, because a good average can hide a dangerous long-range tail — which is exactly what matters for a truck's stopping distance.

??? An object is in the raw sensor data but missing from the fusion output. How do you debug it?
Trace the pipeline **in order** and binary-search the failure. (1) **Detection** — did any sensor actually detect it, or is it a detector miss? (2) **Time-sync** — right timestamps and motion-compensation? A latency bug drops objects. (3) **Gating** — did `d²` wrongly reject the pair because `R`/`P` is mis-tuned? (4) **Association** — did it lose the assignment contest or get merged into another track? (5) **Lifecycle** — did the miss budget kill it too aggressively? Log per-stage counts so you can see exactly where the object vanishes.

??? What's different about perception for a heavy truck vs. a passenger car?
**Stopping distance** — a loaded truck needs far more room to stop, so **long-range** detection and tracking dominate safety; the 100–200 m bins are the critical ones, and that's where lidar is sparse and camera depth is weak, so radar + temporal filtering carry it. **Highway speed** means small angular errors become large lateral errors far out, and high closing speeds reward early confident velocity (radar Doppler). The ego is **articulated** (trailer), with big blind spots and high sensor-mounting geometry that changes occlusion and ground-plane assumptions. And it's a hard-real-time C++ loop, so latency and determinism are first-class.

??? Early vs. late fusion — which would you pick for a safety-critical truck?
**Early fusion** (raw measurements into one joint model) maximizes information and accuracy but is brittle to calibration/time-sync and hard to debug. **Late/track-level fusion** is modular, debuggable, and **degrades gracefully** — lose the camera to glare and radar+lidar still hold the track. For a safety stack I lean toward **detection-level fusion into one central estimator**: one principled tracker, still modular, graceful degradation. I'd reserve heavier early/mid (BEV) fusion for where the accuracy gain is proven and I can still isolate failures. The honest answer names the trade-off rather than declaring one universally right.

## Resources
- Bar-Shalom, Willett, Tian, *Tracking and Data Association* — the canonical MOT text (GNN/JPDA/MHT).
- Thrun, Burgard, Fox, *Probabilistic Robotics* — filtering foundations (Ch. 3–4).
- HOTA paper (Luiten et al., 2021) — why detection+association need separate accounting.
- SORT / DeepSORT papers — minimal, practical tracking-by-detection baselines.
- Companion notes: [06-state-estimation](06-state-estimation.md), [13-bev-transformers](13-bev-transformers.md), [14-concurrency-for-robotics](14-concurrency-for-robotics.md).
